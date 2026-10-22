#!/usr/bin/env python3
"""Export a PPTD project to PPTX.

Default path (preferred): local patched official WASM writer
  scripts/local-export/export-pptd.mjs --no-sign
  → offline, no cookie, no signature API, no browser UI.

Optional --browser path: local neo-ppt mirror via agent-browser
  (same UI as `npx open-kimi-ppt-skill serve`, no www.kimi.com).

Image QA (`export_images.py`) uses the same local editor host.
"""

from __future__ import annotations

import argparse
import base64
import http.client
import json
import mimetypes
import os
import posixpath
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request
import uuid
import zipfile
import xml.etree.ElementTree as ET
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple
from urllib.parse import urlparse

SKILL_DIR = Path(__file__).resolve().parent.parent
IMAGE_MIME = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".svg": "image/svg+xml",
}
MAX_IMAGE_BYTES = 20 * 1024 * 1024
MAX_EMBEDDED_MEDIA_BYTES = 200 * 1024 * 1024
PPTX_CONTENT_TYPE = (
    "application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"
)
FADE_TRANSITION_XML = (
    '<p:transition spd="fast" advClick="1"><p:fade/></p:transition>'
)

# --- page narration audio (TD-007) -----------------------------------------
AUDIO_EXTENSION_MIME = {
    ".mp3": "audio/mpeg",
    ".wav": "audio/wav",
    ".m4a": "audio/mp4",
    ".aac": "audio/aac",
    ".ogg": "audio/ogg",
}
AUDIO_EXTENSIONS = frozenset(AUDIO_EXTENSION_MIME)
# Per-file cap for a single page narration audio; reuses the existing embedded
# media budget constant (200 MiB) as the per-file limit.
MAX_AUDIO_FILE_BYTES = MAX_EMBEDDED_MEDIA_BYTES
AUDIO_DOWNLOAD_CHUNK_BYTES = 64 * 1024
AUDIO_DOWNLOAD_TIMEOUT_SECONDS = 120
AUDIO_MEDIA_PART_RE = re.compile(r"ppt/media/audio(\d+)\.(\w+)$")

P_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
RELS_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
AUDIO_REL_TYPE = f"{R_NS}/audio"
ET.register_namespace("p", P_NS)
ET.register_namespace("a", A_NS)
ET.register_namespace("r", R_NS)
MIN_AGENT_BROWSER_VERSION = (0, 33, 2)
MIN_NODE_MAJOR = 18
NODE_INSTALL_HINT = "Install Node.js 18+ from https://nodejs.org, then retry."
EDITOR_MISSING_HINT = (
    "local neo-ppt editor not found. Re-run "
    "`npx open-kimi-ppt-skill install` (copies editor into the skill) "
    "or set OPEN_KIMI_PPT_EDITOR to the editor directory."
)


class ExportError(RuntimeError):
    pass


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, _format: str, *_args: Any) -> None:
        return


def log(message: str) -> None:
    print(f"[open-kimi-ppt] {message}", file=sys.stderr, flush=True)


def run_command(
    command: Sequence[str],
    *,
    cwd: Optional[Path] = None,
    env: Optional[Dict[str, str]] = None,
    timeout: int = 90,
) -> subprocess.CompletedProcess[str]:
    """Capture merged stdout/stderr via a temp file.

    On Windows, agent-browser's detached daemon can inherit a PIPE handle and
    prevent EOF, deadlocking ``subprocess.run(stdout=PIPE)``. Decoding with the
    system locale (GBK on zh-CN Windows) can also raise UnicodeDecodeError.
    Writing to a UTF-8 file avoids both failures.
    """
    handle, sink_path = tempfile.mkstemp(prefix="open-kimi-ppt-", suffix=".log")
    os.close(handle)
    sink = Path(sink_path)
    output = ""
    try:
        with sink.open("w", encoding="utf-8", errors="replace") as out:
            returncode = subprocess.call(
                list(command),
                cwd=str(cwd) if cwd is not None else None,
                env=env,
                stdout=out,
                stderr=subprocess.STDOUT,
                timeout=timeout,
            )
        output = sink.read_text(encoding="utf-8", errors="replace")
    except subprocess.TimeoutExpired as exc:
        try:
            output = sink.read_text(encoding="utf-8", errors="replace")
        except OSError:
            output = ""
        raise subprocess.TimeoutExpired(
            cmd=list(command),
            timeout=timeout,
            output=output,
        ) from exc
    finally:
        try:
            sink.unlink(missing_ok=True)
        except OSError:
            # WinError 32: daemon may still hold the log file handle.
            pass
    return subprocess.CompletedProcess(list(command), returncode, output, None)


def temporary_directory(prefix: str) -> Any:
    # ignore_cleanup_errors avoids masking the real export error when a Windows
    # browser daemon still holds files under the temp tree (Python 3.10+).
    try:
        return tempfile.TemporaryDirectory(prefix=prefix, ignore_cleanup_errors=True)
    except TypeError:
        return tempfile.TemporaryDirectory(prefix=prefix)


def default_downloads_dir() -> Path:
    home = Path.home()
    candidates: List[Path] = []
    user_profile = os.environ.get("USERPROFILE")
    if user_profile:
        candidates.append(Path(user_profile) / "Downloads")
    candidates.extend((home / "Downloads", home / "下载"))
    for path in candidates:
        if path.is_dir():
            return path
    return home / "Downloads"


def ensure_pyyaml() -> Any:
    try:
        import yaml
    except ImportError:
        log("PyYAML is required; installing pyyaml with pip --user")
        process = run_command(
            [sys.executable, "-m", "pip", "install", "--user", "pyyaml"],
            timeout=300,
        )
        if process.returncode != 0:
            raise ExportError(
                "failed to install PyYAML with pip --user:\n"
                f"{process.stdout[-2000:]}\n"
                "Install it manually with: python3 -m pip install --user pyyaml"
            )
        import yaml
    return yaml


yaml = ensure_pyyaml()


def parse_version(output: str) -> Tuple[int, int, int]:
    match = re.search(r"(\d+)\.(\d+)\.(\d+)\b", output)
    if not match:
        raise ExportError(f"could not parse agent-browser version from: {output.strip()}")
    return tuple(int(part) for part in match.groups())


def parse_node_version(output: str) -> Tuple[int, int, int]:
    match = re.search(r"v?(\d+)\.(\d+)\.(\d+)\b", output)
    if not match:
        raise ExportError(f"could not parse Node.js version from: {output.strip()}")
    return tuple(int(part) for part in match.groups())


def read_agent_browser_version(executable: str) -> Tuple[int, int, int]:
    process = run_command([executable, "--version"], timeout=30)
    if process.returncode != 0:
        raise ExportError(f"agent-browser --version failed:\n{process.stdout[-2000:]}")
    return parse_version(process.stdout)


def ensure_nodejs() -> str:
    executable = shutil.which("node")
    if not executable:
        raise ExportError(f"Node.js is not installed or not on PATH. {NODE_INSTALL_HINT}")

    process = run_command([executable, "--version"], timeout=30)
    if process.returncode != 0:
        raise ExportError(f"node --version failed:\n{process.stdout[-2000:]}")

    version = parse_node_version(process.stdout)
    if version[0] < MIN_NODE_MAJOR:
        raise ExportError(
            f"Node.js {MIN_NODE_MAJOR}+ is required; found "
            f"{'.'.join(map(str, version))} ({process.stdout.strip()}). {NODE_INSTALL_HINT}"
        )

    npm = shutil.which("npm")
    if not npm:
        raise ExportError(
            "npm is not installed or not on PATH. "
            f"npm ships with Node.js. {NODE_INSTALL_HINT}"
        )

    log(f"Node.js version: {'.'.join(map(str, version))}")
    return executable


def ensure_agent_browser() -> str:
    ensure_nodejs()

    executable = shutil.which("agent-browser")
    version = read_agent_browser_version(executable) if executable else None
    if version is not None and version >= MIN_AGENT_BROWSER_VERSION:
        log(f"agent-browser version: {'.'.join(map(str, version))}")
        return executable

    npm = shutil.which("npm")
    if not npm:
        reason = "not installed" if version is None else ".".join(map(str, version))
        raise ExportError(
            f"agent-browser {reason}; npm is required to install agent-browser@latest. "
            f"npm ships with Node.js. {NODE_INSTALL_HINT}"
        )

    current = "not installed" if version is None else ".".join(map(str, version))
    minimum = ".".join(map(str, MIN_AGENT_BROWSER_VERSION))
    log(f"agent-browser {current} is below {minimum}; installing agent-browser@latest")
    process = run_command(
        [npm, "install", "-g", "agent-browser@latest"],
        timeout=300,
    )
    if process.returncode != 0:
        raise ExportError(f"failed to install agent-browser@latest:\n{process.stdout[-4000:]}")

    executable = shutil.which("agent-browser")
    if not executable:
        raise ExportError("agent-browser@latest installed, but executable is not on PATH")
    version = read_agent_browser_version(executable)
    if version < MIN_AGENT_BROWSER_VERSION:
        raise ExportError(
            "agent-browser@latest is still below the required version "
            f"{minimum}: {'.'.join(map(str, version))}"
        )
    log(f"agent-browser upgraded to {'.'.join(map(str, version))}")
    return executable


DEBUG_CHROME_PORT = 9337
CHROME_CANDIDATES = (
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    str(Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "Application" / "chrome.exe"),
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
)


def cdp_alive(port: int) -> bool:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/json/version", timeout=2):
            return True
    except OSError:
        return False


def ensure_debug_chrome() -> Optional[int]:
    """Return a CDP port for agent-browser to connect to (Windows only).

    On Windows agent-browser cannot launch Chrome itself: the Chrome launcher
    process hands off to a child and exits, which agent-browser mistakes for a
    crash ("Chrome exited early without writing DevToolsActivePort"). The
    export therefore always drives an externally started browser. An
    already-working AGENT_BROWSER_CDP wins; otherwise a dedicated debug
    instance is started (or reused) on port 9337. The instance is left running
    on purpose: relaunching with the same profile joins the existing browser,
    so repeated exports reuse one instance instead of piling up processes.
    """
    if sys.platform != "win32":
        return None

    explicit = os.environ.get("AGENT_BROWSER_CDP")
    if explicit:
        try:
            if cdp_alive(int(explicit)):
                return int(explicit)
        except ValueError:
            pass
        log(f"AGENT_BROWSER_CDP={explicit} is not answering; starting a debug browser instead")

    port = DEBUG_CHROME_PORT
    if cdp_alive(port):
        return port
    with socket.socket() as probe:
        if probe.connect_ex(("127.0.0.1", port)) == 0:
            # Port taken by something that is not a CDP endpoint.
            with socket.socket() as spare:
                spare.bind(("127.0.0.1", 0))
                port = spare.getsockname()[1]

    executable = next((c for c in CHROME_CANDIDATES if Path(c).is_file()), None)
    if executable is None:
        raise ExportError(
            "no Chrome or Edge found to drive the export; install Google Chrome, "
            "or start a browser with --remote-debugging-port yourself and set "
            "AGENT_BROWSER_CDP to that port"
        )
    profile = Path(tempfile.gettempdir()) / "okp-cdp-profile"
    log(f"starting debug browser on port {port}: {executable}")
    subprocess.Popen(
        [
            executable,
            f"--user-data-dir={profile}",
            f"--remote-debugging-port={port}",
            "--no-first-run",
            "--no-default-browser-check",
            "--window-position=-2400,0",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
    )
    deadline = time.monotonic() + 20
    while time.monotonic() < deadline:
        if cdp_alive(port):
            return port
        time.sleep(0.5)
    raise ExportError(f"debug browser did not open CDP port {port} within 20s")


def kill_debug_chrome() -> None:
    """Kill leftover agent-browser debug Chrome instances (Windows only).

    agent-browser launches Chrome with a dedicated --user-data-dir under the
    temp dir (okp-cdp-profile). Leftover instances can be reused as a stale
    session and make exports fail with "export dialog did not become ready".
    Killing only processes whose command line matches that profile never
    touches the user's own Chrome/Edge. Non-Windows platforms do nothing
    (agent-browser manages its own browser lifecycle there).
    """
    if sys.platform != "win32":
        return
    profile_marker = "okp-cdp-profile"
    powershell = (
        "Get-CimInstance Win32_Process -Filter \"Name='chrome.exe'\" | "
        f"Where-Object {{ $_.CommandLine -match '{profile_marker}' }} | "
        "ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"
    )
    try:
        subprocess.run(
            ["powershell", "-NoProfile", "-Command", powershell],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        pass  # cleanup is best-effort; the export retry path still applies


def find_manifest(source: Path) -> Path:
    source = source.expanduser().resolve()
    if source.is_file():
        if source.suffix.lower() != ".pptd":
            raise ExportError(f"input must be a .pptd file or project directory: {source}")
        return source
    if not source.is_dir():
        raise ExportError(f"input does not exist: {source}")
    manifests = sorted(source.rglob("*.pptd"))
    if not manifests:
        raise ExportError(f"no .pptd manifest found under: {source}")
    if len(manifests) > 1:
        choices = "\n  ".join(str(path) for path in manifests[:20])
        raise ExportError(
            "multiple .pptd manifests found; pass one manifest explicitly:\n  " + choices
        )
    return manifests[0]


def read_yaml_mapping(path: Path) -> Tuple[str, Dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    try:
        value = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ExportError(
            "invalid YAML in {path}: {exc}\n"
            "常见原因与修法：\n"
            "  1) 文本值里出现「词: 」形式的冒号（如 text: xxx concern: yyy）会被 YAML 当成映射语法 → "
            "整行 text 值用双引号包裹，例如 text: \"... concern: ...\"；\n"
            "  2) 值以特殊字符开头（*、&、!、|、> 等）或以行首空格缩进 → 同样用引号包裹；\n"
            "  3) 缩进层级与上下文不符 → 检查该行对齐到所属元素的同一列。".format(path=path, exc=exc)
        ) from exc
    if not isinstance(value, dict):
        raise ExportError(f"expected a YAML mapping in {path}")
    return text, value


def safe_project_path(root: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative.strip():
        raise ExportError("page path must be a non-empty string")
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ExportError(f"project path escapes the PPTD directory: {relative}") from exc
    return candidate


def build_image_map(root: Path) -> Dict[str, str]:
    image_map: Dict[str, str] = {}
    total = 0
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in IMAGE_MIME:
            continue
        size = path.stat().st_size
        if size > MAX_IMAGE_BYTES:
            log(f"skip local image over 20 MiB: {path.relative_to(root)}")
            continue
        if total + size > MAX_EMBEDDED_MEDIA_BYTES:
            raise ExportError(
                "local image payload exceeds 200 MiB; reduce media size or use remote URLs"
            )
        data = base64.b64encode(path.read_bytes()).decode("ascii")
        rel = path.relative_to(root).as_posix()
        image_map[rel] = f"data:{IMAGE_MIME[path.suffix.lower()]};base64,{data}"
        total += size
    if image_map:
        log(f"prepared {len(image_map)} local image resource(s), {total} bytes")
    return image_map


def build_payload(manifest: Path) -> Dict[str, Any]:
    manifest_text, manifest_data = read_yaml_mapping(manifest)
    if manifest_data.get("version") != "v2":
        raise ExportError("local PPTX export currently requires PPTD version: v2")
    page_paths = manifest_data.get("pages")
    if not isinstance(page_paths, list) or not page_paths:
        raise ExportError("PPTD manifest must contain a non-empty pages list")

    root = manifest.parent.resolve()
    pages: List[Dict[str, str]] = []
    for entry in page_paths:
        page_path = safe_project_path(root, entry)
        if not page_path.is_file():
            raise ExportError(f"missing page file: {entry}")
        page_text, page_data = read_yaml_mapping(page_path)
        if not isinstance(page_data.get("elements"), list):
            raise ExportError(f"page elements must be an array: {entry}")
        pages.append({"path": str(entry), "content": page_text})

    title = str(manifest_data.get("title") or manifest.stem)
    return {
        "id": f"local-export-{uuid.uuid4().hex}",
        "title": title,
        "manifestPath": manifest.name,
        "manifestContent": manifest_text,
        "pages": pages,
        "imageMap": build_image_map(root),
    }


def json_result(output: str) -> Dict[str, Any]:
    for line in reversed(output.splitlines()):
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            return value
    raise ExportError(f"agent-browser returned no JSON object:\n{output[-2000:]}")


class BrowserSession:
    def __init__(
        self,
        executable: str,
        session: str,
        cwd: Path,
        download_dir: Path,
        cdp_port: Optional[int] = None,
    ):
        self.executable = executable
        self.session = session
        self.cwd = cwd
        # Kept as a search root fallback; not passed to agent-browser. On Windows,
        # --download-path can be rewritten to a \\?\ path that cancels Chrome downloads.
        self.download_dir = download_dir
        self.env = os.environ.copy()
        self.env.setdefault("AGENT_BROWSER_DEFAULT_TIMEOUT", "60000")
        self.env.setdefault("AGENT_BROWSER_IDLE_TIMEOUT_MS", "180000")
        # Local editor host is 127.0.0.1; corporate HTTP(S)_PROXY would otherwise
        # intercept and 403 the offline export page.
        for key in (
            "http_proxy",
            "https_proxy",
            "HTTP_PROXY",
            "HTTPS_PROXY",
            "ALL_PROXY",
            "all_proxy",
            "socks5_proxy",
            "SOCKS5_PROXY",
        ):
            self.env.pop(key, None)
        no_proxy = self.env.get("NO_PROXY") or self.env.get("no_proxy") or ""
        parts = {p.strip() for p in no_proxy.split(",") if p.strip()}
        parts.update({"127.0.0.1", "localhost", "::1"})
        joined = ",".join(sorted(parts))
        self.env["NO_PROXY"] = joined
        self.env["no_proxy"] = joined
        if cdp_port is not None:
            self.env["AGENT_BROWSER_CDP"] = str(cdp_port)

    def run(
        self,
        args: Sequence[str],
        *,
        timeout: int = 90,
        check: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        command = [self.executable, "--session", self.session, *args]
        process = run_command(command, cwd=self.cwd, env=self.env, timeout=timeout)
        if check and process.returncode != 0:
            raise ExportError(
                f"agent-browser command failed ({process.returncode}): "
                f"{' '.join(args)}\n{process.stdout[-4000:]}"
            )
        return process

    def open(self, url: str) -> None:
        # Avoid --download-path: agent-browser ≤0.33.2 + Chrome may cancel downloads
        # when given a verbatim Windows path. Files land in the default Downloads folder.
        self.run(["open", url], timeout=90)

    def snapshot(self) -> Dict[str, Any]:
        process = self.run(["snapshot", "-i", "-C", "--json"])
        return json_result(process.stdout)

    def close(self) -> None:
        self.run(["close"], timeout=20, check=False)


def snapshot_data(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    data = snapshot.get("data")
    if not isinstance(data, dict):
        raise ExportError(f"invalid agent-browser snapshot: {snapshot}")
    return data


def ref_by_name(snapshot: Dict[str, Any], name: str, role: Optional[str] = None) -> str:
    refs = snapshot_data(snapshot).get("refs")
    if not isinstance(refs, dict):
        raise ExportError("snapshot contains no interactive refs")
    matches = []
    for ref, metadata in refs.items():
        if not isinstance(metadata, dict) or metadata.get("name") != name:
            continue
        if role is not None and str(metadata.get("role", "")).lower() != role.lower():
            continue
        matches.append(ref)
    if not matches:
        raise ExportError(f"could not find {role or 'element'} named {name!r}")
    return matches[-1]


def switch_state(snapshot: Dict[str, Any]) -> Optional[Tuple[str, bool, bool]]:
    text = str(snapshot_data(snapshot).get("snapshot") or "")
    match = re.search(r"switch \[(?P<attrs>[^\]]*?)ref=(?P<ref>e\d+)\]", text)
    if not match:
        return None
    attrs = match.group("attrs")
    return match.group("ref"), "checked=true" in attrs, "disabled" in attrs


def wait_for_export_dialog(browser: BrowserSession, timeout: float = 20.0) -> Dict[str, Any]:
    deadline = time.monotonic() + timeout
    last: Optional[Dict[str, Any]] = None
    while time.monotonic() < deadline:
        last = browser.snapshot()
        try:
            ref_by_name(last, "下载", "button")
            return last
        except ExportError:
            time.sleep(0.35)
    raise export_dialog_timeout(last)


def _open_export_dialog(browser: BrowserSession, url: str) -> Dict[str, Any]:
    """Open the local editor, wait until the deck is ready, and click 导出
    to bring up the export dialog. Shared by the normal path and the
    kill-and-retry path.
    """
    log("opening the local neo-ppt editor")
    browser.open(url)
    browser.run(
        [
            "wait",
            "--fn",
            'document.documentElement.dataset.deckStatus === "ready"',
        ],
        timeout=120,
    )
    browser.run(["set", "viewport", "1280", "720"])
    snapshot = browser.snapshot()
    export_ref = ref_by_name(snapshot, "导出", "button")
    browser.run(["click", f"@{export_ref}"])
    return wait_for_export_dialog(browser)


def export_dialog_timeout(last: Optional[Dict[str, Any]]) -> ExportError:
    """Build an actionable error for the "export dialog did not become ready" case.

    Root causes seen in the wild: a leftover agent-browser debug Chrome
    instance on port 9337 being reused as a stale session. The message names
    the automatic cleanup performed by the caller (kill_debug_chrome) plus a
    manual one-liner, instead of dumping an undigestible CDP snapshot.
    """
    hint = (
        "export dialog did not become ready: the local editor did not open the export dialog.\n"
        "常见原因：残留的 agent-browser 调试 Chrome（--user-data-dir 含 okp-cdp-profile）"
        "被复用成失效会话。\n已自动按 okp-cdp-profile 特征清理该 Chrome 簇；请重试导出。\n"
        "若仍失败，手动清理后重试：\n"
        "  powershell -NoProfile -Command \"Get-CimInstance Win32_Process -Filter \\\"Name='chrome.exe'\\\" "
        "| ? { $_.CommandLine -match 'okp-cdp-profile' } | Stop-Process -Force\"\n"
        "（该命令只杀调试实例，不影响你自己的 Chrome/Edge）"
    )
    return ExportError(hint)


def is_pptx(path: Path) -> bool:
    if not path.is_file() or path.name.endswith(".crdownload"):
        return False
    try:
        with zipfile.ZipFile(path) as archive:
            if "ppt/presentation.xml" not in archive.namelist():
                return False
            content_types = archive.read("[Content_Types].xml")
            return PPTX_CONTENT_TYPE.encode("utf-8") in content_types
    except (OSError, KeyError, zipfile.BadZipFile):
        return False


def find_download(
    search_roots: Iterable[Path],
    timeout: float = 150.0,
    accept: Callable[[Path], bool] = is_pptx,
    *,
    since: Optional[float] = None,
) -> Path:
    deadline = time.monotonic() + timeout
    last_sizes: Dict[Path, int] = {}
    stable: Dict[Path, int] = {}
    while time.monotonic() < deadline:
        # Snapshot stats while collecting and tolerate races everywhere: the
        # search roots include the live Downloads folder, where Chrome renames
        # .crdownload files away between directory listing and stat().
        entries: List[Tuple[Path, float, int]] = []
        for root in search_roots:
            if not root.exists():
                continue
            for path in root.rglob("*"):
                if not path.is_file():
                    continue
                try:
                    info = path.stat()
                except OSError:
                    continue
                entries.append((path, info.st_mtime, info.st_size))
        for path, mtime, size in sorted(entries, key=lambda entry: entry[1], reverse=True):
            if since is not None and mtime < since:
                continue
            if size == last_sizes.get(path) and size > 0:
                stable[path] = stable.get(path, 0) + 1
            else:
                stable[path] = 0
            last_sizes[path] = size
            if stable[path] >= 1 and accept(path):
                return path
        time.sleep(0.5)
    visible = "\n  ".join(str(path) for path in last_sizes) or "(none)"
    raise ExportError(f"timed out waiting for download; observed files:\n  {visible}")


def replace_transition(slide_xml: bytes, transition: str) -> bytes:
    text = slide_xml.decode("utf-8")
    pattern = re.compile(
        r"<p:transition\b[^>]*(?:/>|>.*?</p:transition>)", re.DOTALL
    )
    text = pattern.sub("", text)
    if transition == "none":
        return text.encode("utf-8")

    # CT_Slide requires transition as a direct child after cSld/clrMapOvr and
    # before timing/extLst. Searching for the first p:extLst is incorrect:
    # shapes may contain their own nested extLst inside cSld, causing Office to
    # ignore a transition inserted there.
    color_map = re.search(
        r"<p:clrMapOvr\b[^>]*(?:/>|>.*?</p:clrMapOvr>)", text, re.DOTALL
    )
    common_slide = re.search(
        r"<p:cSld\b[^>]*(?:/>|>.*?</p:cSld>)", text, re.DOTALL
    )
    anchor = color_map or common_slide
    if anchor is None:
        raise ExportError("slide XML has no cSld/clrMapOvr insertion anchor")
    position = anchor.end()
    return (text[:position] + FADE_TRANSITION_XML + text[position:]).encode("utf-8")


def root_child_names(slide_xml: bytes) -> List[str]:
    try:
        root = ET.fromstring(slide_xml)
    except ET.ParseError as exc:
        raise ExportError(f"invalid slide XML: {exc}") from exc
    return [child.tag.rsplit("}", 1)[-1] for child in root]


def has_direct_fade_transition(slide_xml: bytes) -> bool:
    try:
        root = ET.fromstring(slide_xml)
    except ET.ParseError as exc:
        raise ExportError(f"invalid slide XML: {exc}") from exc
    transition = next(
        (child for child in root if child.tag.rsplit("}", 1)[-1] == "transition"),
        None,
    )
    if transition is None:
        return False
    return any(child.tag.rsplit("}", 1)[-1] == "fade" for child in transition)


def validate_transition_order(slide_xml: bytes, transition: str) -> None:
    names = root_child_names(slide_xml)
    transition_indexes = [index for index, name in enumerate(names) if name == "transition"]
    if transition == "none":
        if transition_indexes:
            raise ExportError("transition=none left a root-level transition")
        return
    if len(transition_indexes) != 1 or not has_direct_fade_transition(slide_xml):
        raise ExportError("slide does not contain exactly one root-level fade transition")
    transition_index = transition_indexes[0]
    for required_before in ("cSld", "clrMapOvr"):
        if required_before in names and names.index(required_before) > transition_index:
            raise ExportError(f"{required_before} appears after transition")
    for required_after in ("timing", "extLst"):
        if required_after in names and names.index(required_after) < transition_index:
            raise ExportError(f"{required_after} appears before transition")


def local_name(tag: Any) -> str:
    """Return the local (namespace-stripped) part of an XML tag name."""
    return str(tag).rsplit("}", 1)[-1]


def _sub(parent: ET.Element, tag: str, ns: str, attrib: Optional[Dict[str, str]] = None) -> ET.Element:
    """Append a namespaced child element to ``parent`` and return it."""
    child = ET.Element(f"{{{ns}}}{tag}", attrib or {})
    parent.append(child)
    return child


def _root_child(element: Optional[ET.Element], name: str) -> Optional[ET.Element]:
    """Return the first direct child of ``element`` whose local name is ``name``."""
    if element is None:
        return None
    return next((child for child in element if local_name(child.tag) == name), None)


def collect_page_audio(deck: Path) -> List[Dict[str, Any]]:
    """Return per-page narration-audio declarations in slide order.

    Parses the PPTD manifest and each page; maps the 1-based page index (which
    matches ``slide{n}.xml`` numbering) to the raw ``audio`` value. Pages
    without an ``audio`` string are skipped; a non-string ``audio`` value is a
    deck contract violation and raises ``ExportError``.
    """
    manifest = find_manifest(deck)
    root = manifest.parent
    _, data = read_yaml_mapping(manifest)
    page_entries = data.get("pages")
    if not isinstance(page_entries, list):
        return []
    declared: List[Dict[str, Any]] = []
    for index, entry in enumerate(page_entries, start=1):
        page_path = safe_project_path(root, entry)
        if not page_path.is_file():
            continue
        _, page_data = read_yaml_mapping(page_path)
        value = page_data.get("audio")
        if value is None or (isinstance(value, str) and not value.strip()):
            continue
        if not isinstance(value, str):
            raise ExportError(f"page audio must be a string: {page_path}")
        declared.append({"slide": index, "value": value.strip()})
    return declared


def audio_extension_mime(value: str) -> Optional[Tuple[str, str]]:
    """Return ``(extension, mime)`` for a supported audio value, else ``None``.

    The extension is taken from the path part of the value so http(s) URLs with
    query strings still resolve (e.g. ``https://host/a.mp3?t=1`` → ``.mp3``).
    """
    parsed = urlparse(value)
    path = parsed.path if parsed.scheme else value
    extension = Path(path).suffix.lower()
    if extension not in AUDIO_EXTENSION_MIME:
        return None
    return extension, AUDIO_EXTENSION_MIME[extension]


def download_audio(url: str) -> bytes:
    """Download remote narration audio, enforcing the 200 MiB per-file limit.

    Raises ``ExportError`` when the request fails (DNS / connect / timeout /
    truncated body, including ``http.client.IncompleteRead`` / non-2xx) or when
    the payload exceeds ``MAX_AUDIO_FILE_BYTES``. On a mid-stream failure the
    error carries the number of bytes received before it broke off.
    """
    chunks: List[bytes] = []
    total = 0
    try:
        with urllib.request.urlopen(url, timeout=AUDIO_DOWNLOAD_TIMEOUT_SECONDS) as response:
            length = response.headers.get("Content-Length")
            if length:
                try:
                    if int(length) > MAX_AUDIO_FILE_BYTES:
                        raise ExportError(
                            f"audio exceeds the 200 MiB per-file limit: {url} "
                            f"(Content-Length={length})"
                        )
                except (TypeError, ValueError):
                    pass
            while True:
                chunk = response.read(AUDIO_DOWNLOAD_CHUNK_BYTES)
                if not chunk:
                    break
                total += len(chunk)
                if total > MAX_AUDIO_FILE_BYTES:
                    raise ExportError(
                        f"audio download exceeds the 200 MiB per-file limit: {url}"
                    )
                chunks.append(chunk)
    except ExportError:
        raise
    except (OSError, http.client.HTTPException) as exc:
        progress = f" (received {total} bytes before failure)" if total else ""
        raise ExportError(f"failed to download audio {url}: {exc}{progress}") from exc
    return b"".join(chunks)


def resolve_audio_source(deck_root: Path, value: str) -> Optional[Tuple[bytes, str, str]]:
    """Resolve a ``Page.audio`` value to ``(payload, extension, mime)``.

    Contract (spec Implementation Decisions, TD-007):

    - relative path → resolved against the deck root (the ``.pptd`` directory);
    - http(s) URL → downloaded at export time;
    - base64 ``data:`` URIs, non-http(s) schemes, missing local files, failed
      downloads, and payloads over the 200 MiB per-file limit raise
      ``ExportError``;
    - unsupported / unknown extensions return ``None`` (the caller warns and
      skips that page's audio).
    """
    if value.startswith("data:"):
        raise ExportError(
            "base64 audio data URIs are not supported; use a relative path or "
            f"an http(s) URL: {value[:80]}"
        )
    extension_mime = audio_extension_mime(value)
    if extension_mime is None:
        return None
    extension, mime = extension_mime
    parsed = urlparse(value)
    if parsed.scheme in ("http", "https"):
        payload = download_audio(value)
    elif parsed.scheme:
        raise ExportError(f"audio must be a relative path or an http(s) URL: {value}")
    else:
        path = safe_project_path(deck_root, value)
        if not path.is_file():
            raise ExportError(f"audio file not found: {value}")
        payload = path.read_bytes()
    if len(payload) > MAX_AUDIO_FILE_BYTES:
        raise ExportError(f"audio exceeds the 200 MiB per-file limit: {value}")
    return payload, extension, mime


def build_audio_shape(spid: int, r_id: str) -> ET.Element:
    """Build the hidden 1px audio shape (``p:sp``) that references ``r_id``.

    The shape is 1x1px, fill-free, and carries ``p:audioFile`` with an
    ``r:embed`` relation inside ``p:nvPr`` — the structure PowerPoint uses for
    narration audio placeholders; it stays out of the visual layer.
    """
    sp = ET.Element(f"{{{P_NS}}}sp")
    nv_sp_pr = _sub(sp, "nvSpPr", P_NS)
    c_nv_pr = _sub(nv_sp_pr, "cNvPr", P_NS, {"id": str(spid), "name": f"Audio Placeholder {spid}"})
    _sub(c_nv_pr, "hlinkClick", A_NS, {f"{{{R_NS}}}id": r_id, "action": "ppaction://media"})
    _sub(nv_sp_pr, "cNvSpPr", P_NS)
    nv_pr = _sub(nv_sp_pr, "nvPr", P_NS)
    _sub(nv_pr, "audioFile", P_NS, {f"{{{R_NS}}}embed": r_id})
    sp_pr = _sub(sp, "spPr", P_NS)
    xfrm = _sub(sp_pr, "xfrm", A_NS)
    _sub(xfrm, "off", A_NS, {"x": "1", "y": "1"})
    _sub(xfrm, "ext", A_NS, {"cx": "1", "cy": "1"})
    prst_geom = _sub(sp_pr, "prstGeom", A_NS, {"prst": "rect"})
    _sub(prst_geom, "avLst", A_NS)
    _sub(sp_pr, "noFill", A_NS)
    tx_body = _sub(sp, "txBody", P_NS)
    _sub(tx_body, "bodyPr", A_NS)
    _sub(tx_body, "lstStyle", A_NS)
    _sub(tx_body, "p", A_NS)
    return sp


def build_narration_par(spid: int, first_id: int) -> ET.Element:
    """Build the narration ``p:par`` block (``playFrom(0)`` auto-play).

    Mirrors Microsoft's embed_audio.py golden reference: the ``p:cmd`` call is
    wrapped in ``p:cBhvr`` with a ``p:spTgt`` whose ``spid`` targets the hidden
    audio shape. Ids are ``first_id .. first_id+2`` so callers can renumber
    when merging into an existing timing tree.
    """
    par = ET.Element(f"{{{P_NS}}}par")
    c_tn = _sub(par, "cTn", P_NS, {"id": str(first_id), "fill": "hold"})
    st_cond = _sub(c_tn, "stCondLst", P_NS)
    _sub(st_cond, "cond", P_NS, {"delay": "0"})
    child_lst = _sub(c_tn, "childTnLst", P_NS)
    inner_par = _sub(child_lst, "par", P_NS)
    inner_ct = _sub(inner_par, "cTn", P_NS, {"id": str(first_id + 1), "fill": "hold"})
    st_cond_2 = _sub(inner_ct, "stCondLst", P_NS)
    _sub(st_cond_2, "cond", P_NS, {"delay": "0"})
    inner_child = _sub(inner_ct, "childTnLst", P_NS)
    cmd = _sub(inner_child, "cmd", P_NS, {"type": "call", "cmd": "playFrom(0)"})
    c_bhvr = _sub(cmd, "cBhvr", P_NS)
    _sub(c_bhvr, "cTn", P_NS, {"id": str(first_id + 2), "dur": "0", "fill": "hold"})
    tgt_el = _sub(c_bhvr, "tgtEl", P_NS)
    _sub(tgt_el, "spTgt", P_NS, {"spid": str(spid)})
    return par


def _slide_cond(evt: str) -> ET.Element:
    """Build a ``p:cond`` targeting the whole slide (prev/next navigation)."""
    cond = ET.Element(f"{{{P_NS}}}cond", {"evt": evt, "delay": "0"})
    tgt_el = _sub(cond, "tgtEl", P_NS)
    _sub(tgt_el, "sldTgt", P_NS)
    return cond


def build_narration_timing(spid: int) -> ET.Element:
    """Build a root-level ``p:timing`` narration template for ``spid``.

    Follows the Microsoft embed_audio.py golden reference: a single
    ``mainSeq`` whose first parallel par is the ``playFrom(0)`` call, so the
    narration auto-plays when the slide is shown.
    """
    timing = ET.Element(f"{{{P_NS}}}timing")
    tn_lst = _sub(timing, "tnLst", P_NS)
    root_par = _sub(tn_lst, "par", P_NS)
    root_ct = _sub(
        root_par, "cTn", P_NS,
        {"id": "1", "dur": "indefinite", "restart": "never", "nodeType": "tmRoot"},
    )
    root_child = _sub(root_ct, "childTnLst", P_NS)
    seq = _sub(root_child, "seq", P_NS, {"concurrent": "1", "nextAc": "seek"})
    seq_ct = _sub(seq, "cTn", P_NS, {"id": "2", "dur": "indefinite", "nodeType": "mainSeq"})
    seq_child = _sub(seq_ct, "childTnLst", P_NS)
    seq_child.append(build_narration_par(spid, 3))
    prev_cond = _sub(seq, "prevCondLst", P_NS)
    prev_cond.append(_slide_cond("onPrev"))
    next_cond = _sub(seq, "nextCondLst", P_NS)
    next_cond.append(_slide_cond("onNext"))
    return timing


def _max_timing_id(timing: ET.Element) -> int:
    """Return the largest numeric ``p:cTn`` id in a timing tree (0 if none)."""
    ids = []
    for element in timing.iter():
        if local_name(element.tag) == "cTn":
            try:
                ids.append(int(element.get("id")))
            except (TypeError, ValueError):
                pass
    return max(ids, default=0)


def merge_narration_timing(timing: ET.Element, spid: int) -> Optional[ET.Element]:
    """Merge the narration ``playFrom(0)`` par into an existing ``p:timing``.

    The narration is inserted as the first parallel ``p:par`` of the first
    ``p:seq``'s main sequence, so authored element animations stay intact and
    the slide keeps exactly one root-level ``p:timing``. Returns the (mutated)
    timing element, or ``None`` when the expected ``tmRoot → seq → childTnLst``
    structure is absent — the caller then degrades to replace + warning.
    """
    tn_lst = _root_child(timing, "tnLst")
    root_par = _root_child(tn_lst, "par") if tn_lst is not None else None
    root_ct = _root_child(root_par, "cTn") if root_par is not None else None
    if root_ct is None or root_ct.get("nodeType") != "tmRoot":
        return None
    root_child = _root_child(root_ct, "childTnLst")
    if root_child is None:
        return None
    seq = next((child for child in root_child if local_name(child.tag) == "seq"), None)
    if seq is None:
        return None
    seq_ct = _root_child(seq, "cTn")
    seq_child = _root_child(seq_ct, "childTnLst") if seq_ct is not None else None
    if seq_child is None:
        return None
    narration = build_narration_par(spid, _max_timing_id(timing) + 1)
    seq_child.insert(0, narration)
    return timing


def _max_shape_id(root: ET.Element) -> int:
    """Return the largest numeric ``p:cNvPr`` shape id in a slide (0 if none)."""
    ids = []
    for element in root.iter():
        if local_name(element.tag) == "cNvPr":
            try:
                ids.append(int(element.get("id")))
            except (TypeError, ValueError):
                pass
    return max(ids, default=0)


def place_timing(root: ET.Element, timing: ET.Element) -> None:
    """Insert a root-level ``p:timing`` in CT_Slide order.

    ``p:timing`` belongs after ``cSld → clrMapOvr? → transition`` and before the
    optional ``p:extLst``, per the CT_Slide sequence enforced elsewhere by
    ``validate_transition_order``.
    """
    names = [local_name(child.tag) for child in root]
    anchor_index = names.index("transition") if "transition" in names else -1
    if anchor_index < 0:
        anchor_index = names.index("clrMapOvr") if "clrMapOvr" in names else -1
    if anchor_index < 0:
        anchor_index = names.index("cSld") if "cSld" in names else -1
    if anchor_index < 0:
        raise ExportError("slide XML has no timing insertion anchor")
    root.insert(anchor_index + 1, timing)


def patch_slide_audio(slide_xml: bytes, r_id: str) -> Tuple[bytes, int]:
    """Inject the hidden audio shape and narration timing into one slide.

    Returns the patched slide XML and the hidden shape's ``spid``. An existing
    root-level ``p:timing`` (element animations) is merged first; on merge
    failure it is replaced by the narration template and a warning is logged.
    """
    try:
        root = ET.fromstring(slide_xml)
    except ET.ParseError as exc:
        raise ExportError(f"invalid slide XML: {exc}") from exc
    c_sld = _root_child(root, "cSld")
    sp_tree = _root_child(c_sld, "spTree") if c_sld is not None else None
    if sp_tree is None:
        raise ExportError("slide XML has no spTree")
    spid = _max_shape_id(root) + 1
    sp_tree.append(build_audio_shape(spid, r_id))

    existing = _root_child(root, "timing")
    if existing is not None and merge_narration_timing(existing, spid) is None:
        log("warning: failed to merge narration timing into the existing animation "
            "timing; replacing the slide timing")
        root.remove(existing)
        existing = None
    if existing is None:
        place_timing(root, build_narration_timing(spid))

    # Keep the final timing (merged or fresh) in valid CT_Slide order.
    names = [local_name(child.tag) for child in root]
    timing_index = names.index("timing") if "timing" in names else -1
    anchor_names = {"cSld", "clrMapOvr", "transition"}
    out_of_order = any(
        name in anchor_names and names.index(name) > timing_index
        for name in anchor_names
        if name in names and timing_index >= 0
    )
    if out_of_order:
        timing = root[timing_index]
        root.remove(timing)
        place_timing(root, timing)
    return ET.tostring(root, encoding="utf-8", xml_declaration=True), spid


def _ct_part_name(media_name: str) -> str:
    """Normalize a media part name to ``[Content_Types].xml`` form (leading slash)."""
    return "/" + media_name.lstrip("/")


def add_audio_content_type_overrides(content_types_xml: bytes, overrides: Dict[str, str]) -> bytes:
    """Append ``<Override>`` entries to ``[Content_Types].xml``.

    New Overrides are inserted before the closing ``</Types>`` so the required
    Defaults-then-Overrides sequence is preserved; an existing Override for the
    same part name is never duplicated.
    """
    text = content_types_xml.decode("utf-8")
    close_index = text.rfind("</Types>")
    if close_index == -1:
        raise ExportError("[Content_Types].xml has no closing </Types>")
    existing_names = set(re.findall(r'PartName="([^"]+)"', text))
    additions = "".join(
        f'<Override PartName="{_ct_part_name(name)}" ContentType="{mime}"/>'
        for name, mime in overrides.items()
        if _ct_part_name(name) not in existing_names
    )
    text = text[:close_index] + additions + text[close_index:]
    return text.encode("utf-8")


def add_audio_relationship(rels_xml: Optional[bytes], media_name: str) -> Tuple[bytes, str]:
    """Append an audio Relationship to a slide rels part.

    The new ``rId`` is the max numeric relationship id in the file plus one
    (``rId1`` for a freshly created rels part). Returns the rels bytes and the
    new id.
    """
    target = f"../../media/{Path(media_name).name}"
    if rels_xml is None:
        text = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            f'<Relationships xmlns="{RELS_NS}"></Relationships>'
        )
        max_id = 0
    else:
        text = rels_xml.decode("utf-8")
        numeric_ids = [int(match) for match in re.findall(r'Id="rId(\d+)"', text)]
        if numeric_ids:
            max_id = max(numeric_ids)
        else:
            max_id = len(re.findall(r"<Relationship\b", text))
    r_id = f"rId{max_id + 1}"
    close_index = text.rfind("</Relationships>")
    if close_index == -1:
        raise ExportError("slide rels has no closing </Relationships>")
    entry = f'<Relationship Id="{r_id}" Type="{AUDIO_REL_TYPE}" Target="{target}"/>'
    text = text[:close_index] + entry + text[close_index:]
    return text.encode("utf-8"), r_id


def patch_audio(pptx: Path, deck: Path) -> Dict[str, Any]:
    """Add page narration audio to an exported PPTX via pure-ZIP post-processing.

    Parses the PPTD deck, resolves each page's ``audio`` value to bytes, then
    rewrites the PPTX ZIP in place: a media part under ``ppt/media/audio{n}.``,
    a ``[Content_Types].xml`` Override, a slide-rels audio Relationship, a
    hidden 1px audio shape, and a root-level ``p:timing`` narration template
    (``playFrom(0)`` auto-play). Slides that already carry an animation
    ``p:timing`` get the narration merged in; on merge failure the timing is
    replaced and a warning is logged.

    Returns ``{"audioSlides", "audioParts", "audioSkippedUnknownExtensions"}``.
    """
    sources = collect_page_audio(deck)
    if not sources:
        return {"audioSlides": 0, "audioParts": 0, "audioSkippedUnknownExtensions": 0}
    deck_root = find_manifest(deck).parent

    packs: List[Dict[str, Any]] = []
    skipped = 0
    for source in sources:
        resolved = resolve_audio_source(deck_root, source["value"])
        if resolved is None:
            skipped += 1
            log(
                f"warning: page {source['slide']} audio has an unsupported "
                f"extension; skipping: {source['value']}"
            )
            continue
        data, extension, mime = resolved
        packs.append({
            "slide": source["slide"],
            "value": source["value"],
            "data": data,
            "ext": extension,
            "mime": mime,
        })
    if not packs:
        return {"audioSlides": 0, "audioParts": 0, "audioSkippedUnknownExtensions": skipped}

    # TD-010 G2: a declared audio page must have a matching slide part in the
    # exported package. Skip missing slides with a warning instead of writing
    # dangling rels / media parts / Content-Types Overrides.
    with zipfile.ZipFile(pptx) as probe:
        present_slides = {
            int(match.group(1))
            for name in probe.namelist()
            for match in [re.fullmatch(r"ppt/slides/slide(\d+)\.xml", name)]
            if match
        }
    absent_packs = [pack for pack in packs if pack["slide"] not in present_slides]
    for pack in absent_packs:
        log(
            f"warning: page {pack['slide']} declares audio but has no slide "
            f"part in the exported PPTX; skipping: {pack['value']}"
        )
    if absent_packs:
        packs = [pack for pack in packs if pack["slide"] in present_slides]
        if not packs:
            return {
                "audioSlides": 0,
                "audioParts": 0,
                "audioSkippedUnknownExtensions": skipped,
            }

    temporary = pptx.with_name(f".{pptx.name}.{uuid.uuid4().hex}.tmp")
    try:
        with zipfile.ZipFile(pptx, "r") as source_zip, zipfile.ZipFile(temporary, "w") as target_zip:
            target_zip.comment = source_zip.comment
            existing_names = set(source_zip.namelist())
            if "[Content_Types].xml" not in existing_names:
                raise ExportError("exported PPTX has no [Content_Types].xml")
            existing_numbers = [
                int(match.group(1))
                for name in existing_names
                for match in [AUDIO_MEDIA_PART_RE.match(name)]
                if match
            ]
            next_audio_number = max(existing_numbers, default=0) + 1
            for pack in packs:
                pack["media_name"] = f"ppt/media/audio{next_audio_number}{pack['ext']}"
                next_audio_number += 1

            rels_cache: Dict[int, bytes] = {}
            for pack in packs:
                rels_name = f"ppt/slides/_rels/slide{pack['slide']}.xml.rels"
                existing_rels = source_zip.read(rels_name) if rels_name in existing_names else None
                new_rels, r_id = add_audio_relationship(existing_rels, pack["media_name"])
                pack["r_id"] = r_id
                rels_cache[pack["slide"]] = new_rels

            content_types = source_zip.read("[Content_Types].xml")
            patched_content_types = add_audio_content_type_overrides(
                content_types,
                {pack["media_name"]: pack["mime"] for pack in packs},
            )
            rels_names_to_write = {
                f"ppt/slides/_rels/slide{pack['slide']}.xml.rels": pack["slide"]
                for pack in packs
            }
            slide_numbers = {pack["slide"] for pack in packs}

            for info in source_zip.infolist():
                data = source_zip.read(info.filename)
                if info.filename == "[Content_Types].xml":
                    data = patched_content_types
                elif info.filename in rels_names_to_write:
                    data = rels_cache[rels_names_to_write[info.filename]]
                elif re.fullmatch(r"ppt/slides/slide\d+\.xml", info.filename):
                    match = re.fullmatch(r"ppt/slides/slide(\d+)\.xml", info.filename)
                    slide_number = int(match.group(1))
                    if slide_number in slide_numbers:
                        pack = next(p for p in packs if p["slide"] == slide_number)
                        data, _spid = patch_slide_audio(data, pack["r_id"])
                target_zip.writestr(info, data, compress_type=info.compress_type)

            for pack in packs:
                target_zip.writestr(
                    pack["media_name"], pack["data"], compress_type=zipfile.ZIP_STORED
                )
            for rels_name, slide_number in rels_names_to_write.items():
                if rels_name not in existing_names:
                    target_zip.writestr(rels_name, rels_cache[slide_number])
        temporary.replace(pptx)
    finally:
        temporary.unlink(missing_ok=True)

    return {
        "audioSlides": len(packs),
        "audioParts": len(packs),
        "audioSkippedUnknownExtensions": skipped,
    }


def _resolve_rel_target(rels_name: str, target: str) -> str:
    """Resolve a rels ``Target`` (relative to the rels part's folder) to a part name."""
    return posixpath.normpath(posixpath.join(posixpath.dirname(rels_name), target))


def verify_audio_slide(archive: zipfile.ZipFile, slide_number: int) -> Dict[str, Any]:
    """Assert a declared-audio slide's packaging is complete.

    Verifies exactly one root-level ``p:timing`` with a ``playFrom(0)``
    narration command whose ``spTgt`` spid matches the hidden audio shape, that
    shape's ``r:embed`` resolves through the slide rels to an audio
    Relationship, and that the media part + ``[Content_Types].xml`` Override
    exist. Returns the part name / rId / spid; raises ``ExportError`` on any
    violation.
    """
    rels_name = f"ppt/slides/_rels/slide{slide_number}.xml.rels"
    if rels_name not in archive.namelist():
        raise ExportError(f"audio slide {slide_number} has no rels part")
    try:
        slide_xml = archive.read(f"ppt/slides/slide{slide_number}.xml")
    except KeyError as exc:
        raise ExportError(f"audio slide {slide_number} has no slide XML part") from exc
    rels_xml = archive.read(rels_name)
    try:
        root = ET.fromstring(slide_xml)
    except ET.ParseError as exc:
        raise ExportError(f"invalid slide XML: {exc}") from exc

    names = [local_name(child.tag) for child in root]
    if names.count("timing") != 1:
        raise ExportError(f"audio slide {slide_number} must have exactly one root-level timing")
    commands = [
        element
        for element in root.iter()
        if local_name(element.tag) == "cmd" and element.get("cmd") == "playFrom(0)"
    ]
    if not commands:
        raise ExportError(f"audio slide {slide_number} has no playFrom(0) narration command")
    sp_tgt = next(
        (element for element in commands[0].iter() if local_name(element.tag) == "spTgt"),
        None,
    )
    if sp_tgt is None or not sp_tgt.get("spid"):
        raise ExportError(f"audio slide {slide_number} narration command has no spTgt spid")
    spid = sp_tgt.get("spid")

    audio_file = None
    for sp in (element for element in root.iter() if local_name(element.tag) == "sp"):
        nv_sp_pr = _root_child(sp, "nvSpPr")
        nv_pr = _root_child(nv_sp_pr, "nvPr") if nv_sp_pr is not None else None
        candidate = _root_child(nv_pr, "audioFile") if nv_pr is not None else None
        if candidate is None:
            continue
        c_nv_pr = _root_child(nv_sp_pr, "cNvPr")
        if c_nv_pr is None or c_nv_pr.get("id") != spid:
            continue
        audio_file = candidate
        break
    if audio_file is None:
        raise ExportError(
            f"audio slide {slide_number} has no hidden audio shape matching spid {spid}"
        )
    r_id = audio_file.get(f"{{{R_NS}}}embed")
    if not r_id:
        raise ExportError(f"audio slide {slide_number} audio shape has no r:embed")

    try:
        rels_root = ET.fromstring(rels_xml)
    except ET.ParseError as exc:
        raise ExportError(f"invalid slide rels XML: {exc}") from exc
    relationship = None
    for element in rels_root:
        if local_name(element.tag) != "Relationship":
            continue
        if element.get("Id") == r_id:
            relationship = element
            break
    if relationship is None:
        raise ExportError(f"audio slide {slide_number} relationship {r_id} is missing")
    if not str(relationship.get("Type", "")).endswith("/audio"):
        raise ExportError(f"audio slide {slide_number} relationship {r_id} has the wrong Type")
    target = relationship.get("Target")
    if not target:
        raise ExportError(f"audio slide {slide_number} relationship {r_id} has no Target")
    part_name = _resolve_rel_target(rels_name, target)
    if part_name not in archive.namelist():
        raise ExportError(f"audio slide {slide_number} media part missing: {part_name}")

    extension = Path(part_name).suffix.lower()
    expected_mime = AUDIO_EXTENSION_MIME.get(extension)
    if expected_mime is None:
        raise ExportError(f"audio part has an unknown extension: {part_name}")
    content_types = archive.read("[Content_Types].xml").decode("utf-8")
    ct_part = _ct_part_name(part_name)
    if f'PartName="{ct_part}"' not in content_types or f'ContentType="{expected_mime}"' not in content_types:
        raise ExportError(f"audio part has no [Content_Types].xml Override: {part_name}")
    return {"part": part_name, "rId": r_id, "spid": spid}


def patch_transitions(pptx: Path, transition: str) -> int:
    temporary = pptx.with_name(f".{pptx.name}.{uuid.uuid4().hex}.tmp")
    slide_count = 0
    try:
        with zipfile.ZipFile(pptx, "r") as source, zipfile.ZipFile(temporary, "w") as target:
            target.comment = source.comment
            for info in source.infolist():
                data = source.read(info.filename)
                if re.fullmatch(r"ppt/slides/slide\d+\.xml", info.filename):
                    data = replace_transition(data, transition)
                    slide_count += 1
                target.writestr(info, data, compress_type=info.compress_type)
        if slide_count == 0:
            raise ExportError("exported PPTX contains no slide XML")
        temporary.replace(pptx)
    finally:
        temporary.unlink(missing_ok=True)
    return slide_count


def verify_output(
    pptx: Path,
    transition: str,
    expect_fonts: bool,
    deck: Optional[Path] = None,
) -> Dict[str, Any]:
    if not is_pptx(pptx):
        raise ExportError(f"output is not a valid PPTX ZIP: {pptx}")
    with zipfile.ZipFile(pptx) as archive:
        broken = archive.testzip()
        if broken:
            raise ExportError(f"PPTX CRC check failed at: {broken}")
        slide_names = [
            name
            for name in archive.namelist()
            if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)
        ]
        slide_xml = {name: archive.read(name) for name in slide_names}
        for data in slide_xml.values():
            validate_transition_order(data, transition)
        transition_hits = sum(has_direct_fade_transition(data) for data in slide_xml.values())
        if transition == "fade" and transition_hits != len(slide_names):
            raise ExportError("fade transition was not written to every slide")
        fonts = [
            name
            for name in archive.namelist()
            if name.startswith("ppt/fonts/") and not name.endswith("/")
        ]
        if expect_fonts and not fonts:
            log(
                "warning: embed-fonts was enabled, but the official writer produced no font part"
            )
        audio_parts = sorted(
            name for name in archive.namelist() if AUDIO_MEDIA_PART_RE.match(name)
        )
        audio_slides = 0
        for slide_name in slide_names:
            rels_name = (
                f"ppt/slides/_rels/{Path(slide_name).name}.rels"
            )
            if rels_name not in archive.namelist():
                continue
            rels_root = ET.fromstring(archive.read(rels_name))
            if any(
                local_name(element.tag) == "Relationship"
                and str(element.get("Type", "")).endswith("/audio")
                for element in rels_root
            ):
                audio_slides += 1
        if deck is not None:
            for source in collect_page_audio(deck):
                if audio_extension_mime(source["value"]) is None:
                    # Unknown-extension pages are deliberately skipped at patch
                    # time with a warning; do not fail verification for them.
                    continue
                verify_audio_slide(archive, source["slide"])
        return {
            "slides": len(slide_names),
            "fadeTransitions": transition_hits,
            "fontParts": len(fonts),
            "audioSlides": audio_slides,
            "audioParts": len(audio_parts),
            "bytes": pptx.stat().st_size,
        }


def postprocess_pptx(
    output: Path,
    project_dir: Path,
    transition: str,
    expect_fonts: bool,
) -> Dict[str, Any]:
    """Shared post-export pipeline used by both export paths.

    Fixed order: ``patch_transitions`` → ``patch_audio`` → ``verify_output``.
    ``project_dir`` is the deck root used to resolve ``Page.audio`` values and
    against which ``verify_output`` cross-checks the packaged audio.
    """
    slide_count = patch_transitions(output, transition)
    patch_audio(output, project_dir)
    summary = verify_output(output, transition, expect_fonts, deck=project_dir)
    summary["transitionPatchedSlides"] = slide_count
    return summary


def resolve_editor_root() -> Path:
    """Locate the offline neo-ppt mirror (package editor/ or skill-installed copy)."""
    env = os.environ.get("OPEN_KIMI_PPT_EDITOR")
    candidates: List[Path] = []
    if env:
        candidates.append(Path(env).expanduser().resolve())
    candidates.append(SKILL_DIR / "editor")
    # monorepo / npm package: skills/open-kimi-ppt → package root
    candidates.append(SKILL_DIR.parent.parent / "editor")
    for candidate in candidates:
        if (candidate / "index.html").is_file():
            return candidate
    raise ExportError(EDITOR_MISSING_HINT)


def serve(
    directory: Path,
    *,
    entry: str = "index.html",
) -> Tuple[ThreadingHTTPServer, threading.Thread, str]:
    """Legacy static serve (tests / callers). Prefer serve_local_editor for exports."""
    handler = lambda *args, **kwargs: QuietHandler(  # noqa: E731
        *args, directory=str(directory), **kwargs
    )
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address
    return server, thread, f"http://{host}:{port}/{entry.lstrip('/')}"


def serve_local_editor(
    payload: Dict[str, Any],
) -> Tuple[ThreadingHTTPServer, threading.Thread, str]:
    """Serve the offline editor and inject payload.json for headless export."""
    editor_root = resolve_editor_root()
    payload_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    class LocalEditorHandler(QuietHandler):
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__(*args, directory=str(editor_root), **kwargs)

        def _is_payload(self) -> bool:
            path = urlparse(self.path).path
            return path in ("/payload.json", "payload.json")

        def do_GET(self) -> None:  # noqa: N802
            if self._is_payload():
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(payload_bytes)))
                self.send_header("Cache-Control", "no-store")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(payload_bytes)
                return
            return SimpleHTTPRequestHandler.do_GET(self)

        def do_HEAD(self) -> None:  # noqa: N802
            if self._is_payload():
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(payload_bytes)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                return
            return SimpleHTTPRequestHandler.do_HEAD(self)

    server = ThreadingHTTPServer(("127.0.0.1", 0), LocalEditorHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address
    url = f"http://{host}:{port}/?ndExport=1"
    log(f"local editor host: {url} (root={editor_root})")
    return server, thread, url


LOCAL_EXPORT_DIR = Path(__file__).resolve().parent / "local-export"
LOCAL_EXPORT_MJS = LOCAL_EXPORT_DIR / "export-pptd.mjs"
# Canonical patched WASM: editor/neo-ppt/assets/ (repo/npm). Skill install copies it
# into local-export/pptd_wasm_bg.wasm for ~/.agents|~/.claude skills trees.
CANONICAL_WASM_NAME = "pptd_wasm_bg-DPPWdROu.wasm"


def resolve_local_wasm() -> Path:
    package_root = Path(__file__).resolve().parents[3]
    candidates = [
        LOCAL_EXPORT_DIR / "pptd_wasm_bg.wasm",
        LOCAL_EXPORT_DIR / CANONICAL_WASM_NAME,
        SKILL_DIR / "editor" / "neo-ppt" / "assets" / CANONICAL_WASM_NAME,
        package_root / "editor" / "neo-ppt" / "assets" / CANONICAL_WASM_NAME,
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise ExportError(
        "patched WASM not found. Expected "
        f"editor/neo-ppt/assets/{CANONICAL_WASM_NAME} (repo/npm package) or "
        f"{LOCAL_EXPORT_DIR / 'pptd_wasm_bg.wasm'} (after skill install)."
    )


def export_pptx_local(
    source: Path,
    output: Path,
    transition: str,
    force: bool = False,
) -> Dict[str, Any]:
    """Export via local patched official WASM (no cookie / no browser UI)."""
    if not LOCAL_EXPORT_MJS.is_file():
        raise ExportError(f"local exporter missing: {LOCAL_EXPORT_MJS}")
    wasm_path = resolve_local_wasm()
    node = shutil.which("node")
    if not node:
        raise ExportError("node is required for local WASM export")

    manifest = find_manifest(source)
    output = output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists() and not force:
        raise ExportError(f"output already exists (pass --force to replace it): {output}")

    log(f"local WASM export: {manifest} → {output}")
    log(f"defaults: transition={transition} (no-sign / signature bypassed)")

    # Pass project directory so media paths resolve relative to the deck root.
    project_dir = manifest.parent if manifest.is_file() else source
    cmd = [
        node,
        str(LOCAL_EXPORT_MJS),
        str(project_dir),
        "-o",
        str(output),
        "--no-sign",
        "--transition",
        transition if transition in ("fade", "none") else "fade",
        "--wasm",
        str(wasm_path),
    ]

    process = subprocess.run(
        cmd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=300,
    )
    if process.returncode != 0:
        raise ExportError(
            f"local WASM export failed ({process.returncode}):\n{process.stdout[-4000:]}"
        )

    summary = postprocess_pptx(output, manifest.parent, transition, expect_fonts=False)
    summary["output"] = str(output)
    summary["exporter"] = "local-wasm-patched"
    log(f"local export ok: {output} ({output.stat().st_size} bytes)")
    return summary


def export_pptx(
    source: Path,
    output: Path,
    transition: str,
    embed_fonts: bool,
    keep_download: bool = False,
    force: bool = False,
    prefer_local: bool = True,
) -> Dict[str, Any]:
    """Prefer local patched WASM; fall back to local neo-ppt browser UI."""
    if prefer_local:
        try:
            return export_pptx_local(source, output, transition, force=force)
        except ExportError as exc:
            log(f"local WASM export unavailable ({exc}); falling back to local browser editor")

    manifest = find_manifest(source)
    payload = build_payload(manifest)
    output = output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists() and not force:
        raise ExportError(f"output already exists (pass --force to replace it): {output}")
    agent_browser = ensure_agent_browser()
    cdp_port = ensure_debug_chrome()

    log(f"manifest: {manifest}")
    log(
        f"defaults: transition={transition}, embed_fonts={'on' if embed_fonts else 'off'}"
    )

    with temporary_directory(prefix="open-kimi-ppt-export-") as temp_name:
        temp_dir = Path(temp_name)
        download_dir = temp_dir / "downloads"
        download_dir.mkdir()
        server, thread, url = serve_local_editor(payload)
        session = f"open-kimi-ppt-export-{os.getpid()}-{uuid.uuid4().hex[:8]}"
        browser = BrowserSession(agent_browser, session, temp_dir, download_dir, cdp_port)
        downloads = default_downloads_dir()
        try:
            try:
                dialog = _open_export_dialog(browser, url)
            except ExportError as first_error:
                # Dialog timeout is usually a stale reused debug-Chrome session.
                # Kill the leftover cluster and retry once against a fresh browser.
                log(
                    f"export dialog did not become ready ({first_error}); "
                    "killing leftover debug Chrome and retrying once"
                )
                browser.close()
                kill_debug_chrome()
                cdp_port = ensure_debug_chrome()
                browser = BrowserSession(agent_browser, session, temp_dir, download_dir, cdp_port)
                dialog = _open_export_dialog(browser, url)

            state = switch_state(dialog)
            if state is not None:
                switch_ref, checked, disabled = state
                if disabled and checked != embed_fonts:
                    log("warning: the font switch is disabled for this deck")
                elif checked != embed_fonts:
                    browser.run(["click", f"@{switch_ref}"])
                    dialog = wait_for_export_dialog(browser)
            elif embed_fonts:
                log("warning: the export dialog exposed no font switch")

            # Plain click (not agent-browser `download`) so Chrome saves to the
            # default Downloads folder; --download-path is broken on some Windows setups.
            started_at = time.time() - 1.0
            download_ref = ref_by_name(dialog, "下载", "button")
            log("generating PPTX in the local editor")
            browser.run(["click", f"@{download_ref}"], timeout=180)
            downloaded = find_download(
                (downloads, download_dir, temp_dir),
                timeout=90,
                since=started_at,
            )
            shutil.copy2(downloaded, output)
            if keep_download:
                debug_copy = output.with_name(f"{output.stem}.browser-raw.pptx")
                if debug_copy.exists() and not force:
                    raise ExportError(
                        f"raw debug output already exists (pass --force): {debug_copy}"
                    )
                shutil.copy2(downloaded, debug_copy)
            try:
                if downloaded.resolve().parent == downloads.resolve():
                    downloaded.unlink(missing_ok=True)
            except OSError:
                pass
        finally:
            browser.close()
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)
            # 复盘教训: agent-browser 的调试 Chrome 若留着复用，下次导出会
            # 复用失效会话而卡 "export dialog did not become ready"。导出结束
            # 即清理（成功/失败都执行），代价是下次冷启动一次 Chrome。
            kill_debug_chrome()

    summary = postprocess_pptx(output, manifest.parent, transition, embed_fonts)
    summary["output"] = str(output)
    summary["exporter"] = "browser-local-editor"
    return summary


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Export a PPTD project to PPTX. "
            "Default: local patched official WASM (offline). "
            "Optional --browser uses the local neo-ppt mirror (also offline)."
        )
    )
    parser.add_argument("input", type=Path, help=".pptd manifest or project directory")
    parser.add_argument("--output", "-o", type=Path, help="output .pptx path")
    parser.add_argument(
        "--transition",
        choices=("fade", "none"),
        default="fade",
        help="slide transition written to every slide (default: fade)",
    )
    font_group = parser.add_mutually_exclusive_group()
    font_group.add_argument(
        "--embed-fonts",
        dest="embed_fonts",
        action="store_true",
        default=True,
        help="embed fonts when available (browser path; default)",
    )
    font_group.add_argument(
        "--no-embed-fonts",
        dest="embed_fonts",
        action="store_false",
        help="disable font embedding (browser path)",
    )
    parser.add_argument(
        "--browser",
        action="store_true",
        help="force local neo-ppt browser UI path instead of Node WASM",
    )
    parser.add_argument(
        "--keep-browser-raw",
        action="store_true",
        help="also keep the unpatched browser download beside the output",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="replace an existing output file",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    try:
        manifest = find_manifest(args.input)
        output = args.output or manifest.with_suffix(".pptx")
        summary = export_pptx(
            args.input,
            output,
            args.transition,
            args.embed_fonts,
            args.keep_browser_raw,
            args.force,
            prefer_local=not args.browser,
        )
    except (ExportError, OSError, subprocess.SubprocessError) as exc:
        print(f"open-kimi-ppt export failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if summary.get("fontParts", 0) == 0:
        print(
            "open-kimi-ppt 提示: 本版 .pptx 未嵌入字体 (fontParts=0)。"
            "若本机未安装 deck 使用的字体（默认 MiSans），PPT 会回退到系统字体且粗体失真。"
            "本机已装对应字体则可忽略；若需分发到未装字体的机器，请用 --browser 路径重导出"
            "（该路径嵌入字体，fontParts=1）。",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
