#!/usr/bin/env python3
import contextlib
import importlib.util
import io
import os
import re
import tempfile
import time
import unittest
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlparse


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "export_pptx.py"
SPEC = importlib.util.spec_from_file_location("export_pptx", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class ExportPptxTests(unittest.TestCase):
    def test_parse_agent_browser_version(self):
        self.assertEqual(MODULE.parse_version("agent-browser 0.33.2"), (0, 33, 2))
        self.assertEqual(MODULE.parse_version("v1.4.0-beta.1"), (1, 4, 0))

    @patch.object(MODULE, "run_command")
    @patch.object(MODULE.shutil, "which")
    def test_old_agent_browser_is_upgraded(self, which, run_command):
        which.side_effect = [
            "/bin/node",
            "/bin/npm",
            "/bin/agent-browser",
            "/bin/npm",
            "/bin/agent-browser",
        ]
        run_command.side_effect = [
            MODULE.subprocess.CompletedProcess([], 0, "v22.11.0\n"),
            MODULE.subprocess.CompletedProcess([], 0, "agent-browser 0.17.1\n"),
            MODULE.subprocess.CompletedProcess([], 0, "changed 1 package\n"),
            MODULE.subprocess.CompletedProcess([], 0, "agent-browser 0.33.2\n"),
        ]
        self.assertEqual(MODULE.ensure_agent_browser(), "/bin/agent-browser")
        self.assertEqual(run_command.call_args_list[2].args[0], [
            "/bin/npm", "install", "-g", "agent-browser@latest"
        ])

    @patch.object(MODULE, "run_command")
    @patch.object(MODULE.shutil, "which")
    def test_missing_nodejs_raises_clear_error(self, which, run_command):
        which.return_value = None
        with self.assertRaisesRegex(MODULE.ExportError, "Node.js is not installed"):
            MODULE.ensure_nodejs()
        run_command.assert_not_called()

    @patch.object(MODULE, "run_command")
    @patch.object(MODULE.shutil, "which")
    def test_old_nodejs_raises_clear_error(self, which, run_command):
        which.return_value = "/bin/node"
        run_command.return_value = MODULE.subprocess.CompletedProcess([], 0, "v16.20.2\n")
        with self.assertRaisesRegex(MODULE.ExportError, "Node.js 18\\+ is required"):
            MODULE.ensure_nodejs()

    @patch.object(MODULE, "run_command")
    @patch.object(MODULE.shutil, "which")
    def test_missing_npm_raises_clear_error(self, which, run_command):
        which.side_effect = ["/bin/node", None]
        run_command.return_value = MODULE.subprocess.CompletedProcess([], 0, "v22.11.0\n")
        with self.assertRaisesRegex(MODULE.ExportError, "npm is not installed"):
            MODULE.ensure_nodejs()

    def test_parse_node_version(self):
        self.assertEqual(MODULE.parse_node_version("v22.11.0"), (22, 11, 0))
        self.assertEqual(MODULE.parse_node_version("18.20.4"), (18, 20, 4))

    def test_fade_is_inserted_before_timing(self):
        source = (
            b'<?xml version="1.0" encoding="UTF-8"?>'
            b'<p:sld xmlns:p="urn:test"><p:cSld><p:spTree><p:extLst/>'
            b'</p:spTree></p:cSld><p:clrMapOvr/><p:timing/><p:extLst/></p:sld>'
        )
        result_bytes = MODULE.replace_transition(source, "fade")
        result = result_bytes.decode("utf-8")
        self.assertIn("<p:transition", result)
        self.assertIn("<p:fade/>", result)
        self.assertGreater(result.index("<p:transition"), result.index("<p:clrMapOvr"))
        self.assertLess(result.index("<p:transition"), result.index("<p:timing"))
        MODULE.validate_transition_order(result_bytes, "fade")

    def test_existing_transition_is_replaced_or_removed(self):
        source = (
            b'<p:sld xmlns:p="urn:test"><p:cSld/>'
            b'<p:transition><p:wipe/></p:transition><p:extLst/></p:sld>'
        )
        faded = MODULE.replace_transition(source, "fade").decode("utf-8")
        self.assertNotIn("p:wipe", faded)
        self.assertEqual(faded.count("<p:transition"), 1)
        MODULE.validate_transition_order(faded.encode("utf-8"), "fade")
        cleared = MODULE.replace_transition(source, "none").decode("utf-8")
        self.assertNotIn("p:transition", cleared)
        MODULE.validate_transition_order(cleared.encode("utf-8"), "none")

    def test_nested_transition_is_relocated_to_slide_root(self):
        source = (
            b'<p:sld xmlns:p="urn:test"><p:cSld><p:spTree>'
            b'<p:transition><p:fade/></p:transition><p:extLst/>'
            b'</p:spTree></p:cSld><p:clrMapOvr/><p:extLst/></p:sld>'
        )
        result = MODULE.replace_transition(source, "fade")
        MODULE.validate_transition_order(result, "fade")
        self.assertEqual(MODULE.root_child_names(result), [
            "cSld", "clrMapOvr", "transition", "extLst"
        ])

    def test_patch_transitions_preserves_a_valid_zip(self):
        with tempfile.TemporaryDirectory() as name:
            deck = Path(name) / "test.pptx"
            with zipfile.ZipFile(deck, "w", zipfile.ZIP_DEFLATED) as archive:
                archive.writestr(
                    "[Content_Types].xml",
                    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                    '<Override PartName="/ppt/presentation.xml" '
                    f'ContentType="{MODULE.PPTX_CONTENT_TYPE}"/></Types>',
                )
                archive.writestr("ppt/presentation.xml", "<p:presentation xmlns:p=\"urn:test\"/>")
                archive.writestr(
                    "ppt/slides/slide1.xml",
                    '<p:sld xmlns:p="urn:test"><p:cSld/></p:sld>',
                )
            self.assertEqual(MODULE.patch_transitions(deck, "fade"), 1)
            with zipfile.ZipFile(deck) as archive:
                self.assertIsNone(archive.testzip())
                slide = archive.read("ppt/slides/slide1.xml")
                self.assertIn(b"<p:fade/>", slide)

    @patch.object(MODULE.subprocess, "call", return_value=0)
    def test_run_command_captures_utf8_via_temp_file(self, call):
        def write_sink(*_args, **kwargs):
            kwargs["stdout"].write("agent-browser 0.33.2\n")
            return 0

        call.side_effect = write_sink
        process = MODULE.run_command(["agent-browser", "--version"], timeout=5)
        self.assertEqual(process.returncode, 0)
        self.assertIn("0.33.2", process.stdout)
        self.assertEqual(call.call_args.kwargs["stderr"], MODULE.subprocess.STDOUT)

    def test_find_download_ignores_files_older_than_since(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            old = root / "old.pptx"
            new = root / "new.pptx"
            for path in (old, new):
                with zipfile.ZipFile(path, "w") as archive:
                    archive.writestr(
                        "[Content_Types].xml",
                        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                        '<Override PartName="/ppt/presentation.xml" '
                        f'ContentType="{MODULE.PPTX_CONTENT_TYPE}"/></Types>',
                    )
                    archive.writestr("ppt/presentation.xml", "<p:presentation/>")

            older = time.time() - 60
            os.utime(old, (older, older))
            since = time.time() - 5
            found = MODULE.find_download([root], timeout=2.0, since=since)
            self.assertEqual(found.resolve(), new.resolve())

    def test_find_download_survives_files_vanishing_mid_scan(self):
        # Chrome renames "*.crdownload" files away between directory listing
        # and stat(); a vanished file must be skipped, not crash the export.
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            deck = root / "deck.pptx"
            with zipfile.ZipFile(deck, "w") as archive:
                archive.writestr(
                    "[Content_Types].xml",
                    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                    '<Override PartName="/ppt/presentation.xml" '
                    f'ContentType="{MODULE.PPTX_CONTENT_TYPE}"/></Types>',
                )
                archive.writestr("ppt/presentation.xml", "<p:presentation/>")
            ghost = root / "ghost.crdownload"
            ghost.write_bytes(b"partial download")

            real_stat = Path.stat
            seen = {"count": 0}

            def racy_stat(self, **kwargs):
                if self.name == "ghost.crdownload":
                    seen["count"] += 1
                    if seen["count"] > 1:
                        raise FileNotFoundError(2, "vanished mid-scan", str(self))
                return real_stat(self, **kwargs)

            with patch.object(Path, "stat", racy_stat):
                found = MODULE.find_download([root], timeout=2.0)
            self.assertEqual(found.resolve(), deck.resolve())

    def test_browser_open_does_not_pass_download_path(self):
        session = MODULE.BrowserSession(
            "/bin/agent-browser",
            "test-session",
            Path("."),
            Path("/tmp/downloads"),
        )
        with patch.object(session, "run") as run:
            session.open("http://127.0.0.1:9/?ndExport=1")
        run.assert_called_once_with(
            ["open", "http://127.0.0.1:9/?ndExport=1"],
            timeout=90,
        )

    def test_ensure_debug_chrome_is_windows_only(self):
        with patch.object(MODULE.sys, "platform", "linux"):
            self.assertIsNone(MODULE.ensure_debug_chrome())

    @patch.object(MODULE, "cdp_alive", return_value=True)
    def test_ensure_debug_chrome_prefers_working_explicit_port(self, cdp_alive):
        with patch.object(MODULE.sys, "platform", "win32"), \
                patch.dict(MODULE.os.environ, {"AGENT_BROWSER_CDP": "9444"}):
            self.assertEqual(MODULE.ensure_debug_chrome(), 9444)
        cdp_alive.assert_called_once_with(9444)

    def test_browser_session_exports_cdp_port_to_env(self):
        with patch.dict(MODULE.os.environ, {}, clear=False):
            MODULE.os.environ.pop("AGENT_BROWSER_CDP", None)
            with_port = MODULE.BrowserSession(
                "/bin/agent-browser", "s", Path("."), Path("/tmp/d"), cdp_port=9337
            )
            self.assertEqual(with_port.env["AGENT_BROWSER_CDP"], "9337")
            without_port = MODULE.BrowserSession(
                "/bin/agent-browser", "s", Path("."), Path("/tmp/d")
            )
            self.assertNotIn("AGENT_BROWSER_CDP", without_port.env)


# --------------------------------------------------------------------------
# Page narration audio (TD-007) test helper scaffolding
# --------------------------------------------------------------------------
AUDIO_FIXTURE = Path(__file__).resolve().parent / "fixtures" / "audio" / "beep.mp3"
P_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


def xml_slide(timing: str = "") -> bytes:
    """A minimal well-formed slide XML using real OOXML namespaces.

    Optional ``timing`` text is inserted after the fade transition so the
    fixture models a WASM-exported slide in valid CT_Slide order.
    """
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<p:sld xmlns:p="{P_NS}" xmlns:a="{A_NS}" xmlns:r="{R_NS}">'
        "<p:cSld><p:spTree>"
        '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
        '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/>'
        '<a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
        '<p:sp><p:nvSpPr><p:cNvPr id="2" name="Title 1"/><p:cNvSpPr txBox="1"/>'
        '<p:nvPr/></p:nvSpPr><p:spPr/><p:txBody><a:bodyPr/><a:lstStyle/><a:p/>'
        "</p:txBody></p:sp></p:spTree></p:cSld>"
        "<p:clrMapOvr><a:overrideClrMapping/></p:clrMapOvr>"
        '<p:transition spd="fast" advClick="1"><p:fade/></p:transition>'
        f"{timing}"
        "</p:sld>"
    ).encode("utf-8")


def base_content_types(slide_count: int = 1) -> bytes:
    overrides = "".join(
        f'<Override PartName="/ppt/slides/slide{i}.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
        for i in range(1, slide_count + 1)
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        f'<Override PartName="/ppt/presentation.xml" ContentType="{MODULE.PPTX_CONTENT_TYPE}"/>'
        f"{overrides}"
        "</Types>"
    ).encode("utf-8")


def rels_bytes(relations) -> bytes:
    inner = "".join(
        f'<Relationship Id="{rid}" Type="{rtype}" Target="{target}"/>'
        for rid, rtype, target in relations
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">{inner}'
        "</Relationships>"
    ).encode("utf-8")


def make_pptx(path: Path, slides, rels=None) -> None:
    """Write a minimal PPTX ZIP: content types + presentation + slide(s)."""
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("[Content_Types].xml", base_content_types(len(slides)))
        archive.writestr("ppt/presentation.xml", "<p:presentation xmlns:p=\"urn:x\"/>")
        for number, slide_xml in slides.items():
            archive.writestr(f"ppt/slides/slide{number}.xml", slide_xml)
            if rels and number in rels:
                archive.writestr(
                    f"ppt/slides/_rels/slide{number}.xml.rels", rels[number]
                )


def make_deck(root: Path, spec, missing_media=frozenset()) -> Path:
    """Create a self-contained PPTD deck from ``spec`` (list of per-page dicts).

    Each dict may set ``audio`` (value string) and ``animations`` (bool). Local
    audio files referenced by the pages are materialized with fixture bytes
    unless listed in ``missing_media``.
    """
    media = root / "media"
    media.mkdir(parents=True, exist_ok=True)
    (media / "beep.mp3").write_bytes(AUDIO_FIXTURE.read_bytes())
    page_files = []
    for index, config in enumerate(spec, start=1):
        audio = config.get("audio")
        if audio and audio not in missing_media:
            if urlparse(audio).scheme or audio.startswith("data:"):
                pass  # URL / data URI values are never materialized locally
            elif ".." in audio.replace("\\", "/").split("/"):
                pass  # path-escaping values are never materialized
            else:
                target = root / audio
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(AUDIO_FIXTURE.read_bytes())
        page_path = root / "pages" / (f"{index:02d}.page")
        page_path.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            "pageType: content",
            "elements:",
            f"  - elementId: page{index}-t1",
            "    elementType: text",
            "    bounds: [10, 10, 100, 40]",
            "    content:",
            "      fontSize: 18",
            f"      text: Page {index}",
        ]
        if audio:
            lines.append(f"audio: {audio!r}")
        if config.get("animations"):
            lines += [
                "animations:",
                f"  - elementId: page{index}-t1",
                "    effect: fade-in",
                "    trigger: onClick",
            ]
        page_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        page_files.append(f"pages/{index:02d}.page")
    manifest = (
        "version: v2\n"
        "title: Audio Test Deck\n"
        "size: [960, 540]\n"
        "pages:\n" + "\n".join(f"  - {page}" for page in page_files) + "\n"
    )
    manifest_path = root / "deck.pptd"
    manifest_path.write_text(manifest, encoding="utf-8")
    return manifest_path


class _FakeResponse:
    """A minimal urllib response for download tests (chunked read)."""

    def __init__(self, data=b"", headers=None):
        self._data = data
        self._pos = 0
        self.headers = headers or {}

    def read(self, size=-1):
        if size is None or size < 0:
            size = len(self._data) - self._pos
        chunk = self._data[self._pos : self._pos + size]
        self._pos += len(chunk)
        return chunk

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False


def _audio_shapes(root: ET.Element):
    """Yield (sp, nvSpPr, cNvPr, audioFile) for every audioFile shape in a slide."""
    for sp in (element for element in root.iter() if MODULE.local_name(element.tag) == "sp"):
        nv_sp_pr = next(
            (child for child in sp if MODULE.local_name(child.tag) == "nvSpPr"), None
        )
        if nv_sp_pr is None:
            continue
        nv_pr = next(
            (child for child in nv_sp_pr if MODULE.local_name(child.tag) == "nvPr"), None
        )
        if nv_pr is None:
            continue
        audio_file = next(
            (child for child in nv_pr if MODULE.local_name(child.tag) == "audioFile"), None
        )
        if audio_file is None:
            continue
        c_nv_pr = next(
            (child for child in nv_sp_pr if MODULE.local_name(child.tag) == "cNvPr"), None
        )
        yield sp, nv_sp_pr, c_nv_pr, audio_file


class AudioPackagingTests(unittest.TestCase):
    """AC7-1 media 打包 / AC7-2 Content_Types / AC7-3 slide rels."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.deck_root = self.root / "deck"
        make_deck(self.deck_root, [{"audio": "media/beep.mp3"}])
        self.pptx = self.root / "out.pptx"
        make_pptx(self.pptx, {1: xml_slide()})

    def tearDown(self):
        self._tmp.cleanup()

    def test_audio_media_part_bytes_match_fixture(self):
        MODULE.patch_audio(self.pptx, self.deck_root)
        with zipfile.ZipFile(self.pptx) as archive:
            self.assertIsNone(archive.testzip())
            self.assertIn("ppt/media/audio1.mp3", archive.namelist())
            self.assertEqual(
                archive.read("ppt/media/audio1.mp3"), AUDIO_FIXTURE.read_bytes()
            )

    def test_audio_content_types_override_mp3_in_schema_order(self):
        MODULE.patch_audio(self.pptx, self.deck_root)
        with zipfile.ZipFile(self.pptx) as archive:
            content_types = archive.read("[Content_Types].xml").decode("utf-8")
        self.assertIn('PartName="/ppt/media/audio1.mp3"', content_types)
        self.assertIn('ContentType="audio/mpeg"', content_types)
        # Defaults precede Overrides; the new Override comes before </Types>
        self.assertGreater(
            content_types.index('PartName="/ppt/media/audio1.mp3"'),
            content_types.rindex("<Default "),
        )
        self.assertLess(
            content_types.index('PartName="/ppt/media/audio1.mp3"'),
            content_types.rindex("</Types>"),
        )

    def test_audio_extension_mime_mapping(self):
        self.assertEqual(MODULE.AUDIO_EXTENSION_MIME[".mp3"], "audio/mpeg")
        self.assertEqual(MODULE.AUDIO_EXTENSION_MIME[".wav"], "audio/wav")
        self.assertEqual(MODULE.AUDIO_EXTENSION_MIME[".m4a"], "audio/mp4")
        self.assertEqual(MODULE.AUDIO_EXTENSION_MIME[".aac"], "audio/aac")
        self.assertEqual(MODULE.AUDIO_EXTENSION_MIME[".ogg"], "audio/ogg")
        self.assertNotIn(".flac", MODULE.AUDIO_EXTENSION_MIME)

    def test_audio_unknown_extension_skipped_with_warning(self):
        unknown_root = self.root / "deck-unknown"
        make_deck(unknown_root, [{"audio": "media/beep.xyz"}])
        out = self.root / "out-unknown.pptx"
        make_pptx(out, {1: xml_slide()})
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            result = MODULE.patch_audio(out, unknown_root)
        self.assertEqual(result["audioSkippedUnknownExtensions"], 1)
        self.assertEqual(result["audioParts"], 0)
        self.assertEqual(result["audioSlides"], 0)
        with zipfile.ZipFile(out) as archive:
            self.assertNotIn("ppt/media/audio1.xyz", archive.namelist())
            self.assertNotIn(b"playFrom(0)", archive.read("ppt/slides/slide1.xml"))
        self.assertIn("unsupported extension", err.getvalue())

    def test_audio_rels_rId_is_max_existing_plus_one(self):
        existing_rels = rels_bytes([
            (
                "rId3",
                "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout",
                "../slideLayouts/slideLayout1.xml",
            ),
        ])
        make_pptx(self.pptx, {1: xml_slide()}, rels={1: existing_rels})
        MODULE.patch_audio(self.pptx, self.deck_root)
        with zipfile.ZipFile(self.pptx) as archive:
            rels_text = archive.read("ppt/slides/_rels/slide1.xml.rels").decode("utf-8")
        self.assertIn('Id="rId4"', rels_text)
        self.assertIn(
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/audio"',
            rels_text,
        )
        self.assertIn('Target="../../media/audio1.mp3"', rels_text)

    def test_audio_rels_created_when_missing(self):
        MODULE.patch_audio(self.pptx, self.deck_root)
        with zipfile.ZipFile(self.pptx) as archive:
            self.assertIn("ppt/slides/_rels/slide1.xml.rels", archive.namelist())
            rels_text = archive.read("ppt/slides/_rels/slide1.xml.rels").decode("utf-8")
        self.assertIn('Id="rId1"', rels_text)
        self.assertIn(
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/audio"',
            rels_text,
        )
        self.assertIn('Target="../../media/audio1.mp3"', rels_text)

    def test_audio_multiple_pages_get_sequential_parts(self):
        deck_root = self.root / "deck-multi"
        make_deck(deck_root, [
            {"audio": "media/beep.mp3"},
            {"audio": "media/beep.wav"},
            {},
        ])
        out = self.root / "out-multi.pptx"
        make_pptx(out, {1: xml_slide(), 2: xml_slide(), 3: xml_slide()})
        MODULE.patch_audio(out, deck_root)
        with zipfile.ZipFile(out) as archive:
            names = archive.namelist()
            self.assertIn("ppt/media/audio1.mp3", names)
            self.assertIn("ppt/media/audio2.wav", names)
            self.assertFalse(any(name.startswith("ppt/media/audio3") for name in names))
            ct = archive.read("[Content_Types].xml").decode("utf-8")
            self.assertIn('PartName="/ppt/media/audio2.wav"', ct)
            self.assertIn('ContentType="audio/wav"', ct)
        summary = MODULE.verify_output(out, "fade", False, deck=deck_root)
        self.assertEqual(summary["audioSlides"], 2)
        self.assertEqual(summary["audioParts"], 2)

    def test_audio_page_without_slide_part_is_skipped(self):
        # G2: page 3 declares audio but the exported zip only contains slides
        # 1 and 2 → skip with a warning; no dangling rels/media/Override for
        # the missing slide, no raw KeyError.
        deck_root = self.root / "deck-3p"
        make_deck(deck_root, [
            {"audio": "media/beep.mp3"},
            {"audio": "media/beep.mp3"},
            {"audio": "media/beep.wav"},
        ])
        out = self.root / "out-3p.pptx"
        make_pptx(out, {1: xml_slide(), 2: xml_slide()})
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            result = MODULE.patch_audio(out, deck_root)
        self.assertEqual(result["audioSlides"], 2)
        self.assertEqual(result["audioParts"], 2)
        with zipfile.ZipFile(out) as archive:
            names = archive.namelist()
            self.assertIn("ppt/media/audio1.mp3", names)
            self.assertIn("ppt/media/audio2.mp3", names)
            self.assertFalse(any(name.startswith("ppt/media/audio3") for name in names))
            self.assertNotIn("ppt/slides/_rels/slide3.xml.rels", names)
            ct = archive.read("[Content_Types].xml").decode("utf-8")
            self.assertNotIn("/ppt/media/audio3", ct)
        self.assertIn("no slide part", err.getvalue())

    def test_audio_all_pages_without_slide_parts_return_zero(self):
        # G2 degenerate case: every declared audio page lacks a slide part →
        # nothing written, zero summary, warning for each skipped page.
        deck_root = self.root / "deck-allmissing"
        make_deck(deck_root, [{"audio": "media/beep.mp3"}])
        out = self.root / "out-allmissing.pptx"
        make_pptx(out, {2: xml_slide()})  # zip has slide2 only; page 1 has no slide part
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            result = MODULE.patch_audio(out, deck_root)
        self.assertEqual(result["audioSlides"], 0)
        self.assertEqual(result["audioParts"], 0)
        with zipfile.ZipFile(out) as archive:
            names = archive.namelist()
            self.assertFalse(any(name.startswith("ppt/media/audio") for name in names))
            self.assertNotIn("ppt/slides/_rels/slide1.xml.rels", names)
        self.assertIn("no slide part", err.getvalue())


class AudioTimingTests(unittest.TestCase):
    """AC7-4 隐藏 shape / AC7-5 timing 结构与顺序."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.deck_root = self.root / "deck"
        make_deck(self.deck_root, [{"audio": "media/beep.mp3"}])
        self.pptx = self.root / "out.pptx"
        make_pptx(self.pptx, {1: xml_slide()})

    def tearDown(self):
        self._tmp.cleanup()

    def _patched_slide_root(self) -> ET.Element:
        MODULE.patch_audio(self.pptx, self.deck_root)
        with zipfile.ZipFile(self.pptx) as archive:
            return ET.fromstring(archive.read("ppt/slides/slide1.xml"))

    def test_audio_hidden_shape_1px_nofill_with_audiofile(self):
        root = self._patched_slide_root()
        shapes = list(_audio_shapes(root))
        self.assertEqual(len(shapes), 1)
        _sp, _nv_sp_pr, c_nv_pr, audio_file = shapes[0]
        embed = audio_file.get(f"{{{R_NS}}}embed")
        self.assertTrue(embed and embed.startswith("rId"))
        self.assertTrue(c_nv_pr.get("id"))
        # 1px geometry + no fill + rect preset
        sp_pr = next(child for child in _sp if MODULE.local_name(child.tag) == "spPr")
        xfrm = sp_pr.find(f"{{{A_NS}}}xfrm")
        self.assertIsNotNone(xfrm)
        off = xfrm.find(f"{{{A_NS}}}off")
        ext = xfrm.find(f"{{{A_NS}}}ext")
        self.assertEqual((off.get("x"), off.get("y")), ("1", "1"))
        self.assertEqual((ext.get("cx"), ext.get("cy")), ("1", "1"))
        self.assertIsNotNone(sp_pr.find(f"{{{A_NS}}}noFill"))
        self.assertEqual(sp_pr.find(f"{{{A_NS}}}prstGeom").get("prst"), "rect")

    def test_audio_timing_single_cmd_and_order(self):
        MODULE.patch_audio(self.pptx, self.deck_root)
        with zipfile.ZipFile(self.pptx) as archive:
            slide = archive.read("ppt/slides/slide1.xml")
        names = MODULE.root_child_names(slide)
        self.assertEqual(names.count("timing"), 1)
        self.assertGreater(names.index("timing"), names.index("transition"))
        MODULE.validate_transition_order(slide, "fade")
        root = ET.fromstring(slide)
        commands = [
            element
            for element in root.iter()
            if MODULE.local_name(element.tag) == "cmd"
        ]
        self.assertEqual(len(commands), 1)
        self.assertEqual(commands[0].get("type"), "call")
        self.assertEqual(commands[0].get("cmd"), "playFrom(0)")
        sp_tgt = commands[0].find(f".//{{{P_NS}}}spTgt")
        self.assertIsNotNone(sp_tgt)
        shapes = list(_audio_shapes(root))
        self.assertEqual(len(shapes), 1)
        _sp, _nv_sp_pr, c_nv_pr, _audio_file = shapes[0]
        self.assertEqual(sp_tgt.get("spid"), c_nv_pr.get("id"))


ANIMATION_TIMING = (
    '<p:timing><p:tnLst><p:par>'
    '<p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot">'
    '<p:childTnLst><p:seq concurrent="1" nextAc="seek">'
    '<p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst><p:par>'
    '<p:cTn id="10" dur="500" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst>'
    '<p:childTnLst><p:effect effectId="1" presetClass="entr" presetSubtype="0" grpId="0">'
    '<p:cBhvr><p:cTn id="11" dur="500" fill="hold"/><p:tgtEl><p:spTgt spid="2"/></p:tgtEl></p:cBhvr>'
    "</p:effect></p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn>"
    '<p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
    '<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst>'
    "</p:seq></p:childTnLst></p:cTn></p:par></p:tnLst></p:timing>"
)


class AudioMergeTests(unittest.TestCase):
    """AC7-6 动画 + audio 共存合并 (恰一个 timing；失败降级替换 + 警告)."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.deck_root = self.root / "deck"
        make_deck(self.deck_root, [{"audio": "media/beep.mp3", "animations": True}])
        self.pptx = self.root / "out.pptx"

    def tearDown(self):
        self._tmp.cleanup()

    def test_audio_merges_into_existing_animation_timing(self):
        make_pptx(self.pptx, {1: xml_slide(timing=ANIMATION_TIMING)})
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            MODULE.patch_audio(self.pptx, self.deck_root)
        with zipfile.ZipFile(self.pptx) as archive:
            slide = archive.read("ppt/slides/slide1.xml")
        names = MODULE.root_child_names(slide)
        self.assertEqual(names.count("timing"), 1)
        MODULE.validate_transition_order(slide, "fade")
        root = ET.fromstring(slide)
        commands = [
            element
            for element in root.iter()
            if MODULE.local_name(element.tag) == "cmd"
            and element.get("cmd") == "playFrom(0)"
        ]
        self.assertEqual(len(commands), 1)
        effects = [
            element
            for element in root.iter()
            if MODULE.local_name(element.tag) == "effect"
        ]
        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].get("effectId"), "1")
        # narration cTn ids renumbered beyond the existing max (11)
        ids = [
            int(element.get("id"))
            for element in root.iter()
            if MODULE.local_name(element.tag) == "cTn"
        ]
        self.assertTrue(any(cid >= 12 for cid in ids), f"not renumbered: {ids}")
        # no merge warning expected on the success path
        self.assertNotIn("merge", err.getvalue())

    def test_audio_merge_failure_degrades_to_replace_with_warning(self):
        bad_timing = (
            "<p:timing><p:tnLst><p:par>"
            '<p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot"/>'
            "</p:par></p:tnLst></p:timing>"
        )
        make_pptx(self.pptx, {1: xml_slide(timing=bad_timing)})
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            MODULE.patch_audio(self.pptx, self.deck_root)
        with zipfile.ZipFile(self.pptx) as archive:
            slide = archive.read("ppt/slides/slide1.xml")
        names = MODULE.root_child_names(slide)
        self.assertEqual(names.count("timing"), 1)
        root = ET.fromstring(slide)
        commands = [
            element
            for element in root.iter()
            if MODULE.local_name(element.tag) == "cmd"
            and element.get("cmd") == "playFrom(0)"
        ]
        self.assertEqual(len(commands), 1)
        self.assertIn("merge", err.getvalue())


class AudioBadInputTests(unittest.TestCase):
    """AC7-7 坏输入契约: base64 / 缺失文件 / URL 失败 / 超限 / 未知 scheme."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def _run_patch(self, audio_value, missing_media=frozenset()):
        deck_root = self.root / "deck"
        make_deck(deck_root, [{"audio": audio_value}], missing_media=missing_media)
        out = self.root / "out.pptx"
        make_pptx(out, {1: xml_slide()})
        return MODULE.patch_audio(out, deck_root), out

    def test_audio_base64_data_uri_raises(self):
        with self.assertRaisesRegex(MODULE.ExportError, "base64"):
            self._run_patch("data:audio/mpeg;base64,SUQzAw==")

    def test_audio_missing_local_file_raises(self):
        with self.assertRaisesRegex(MODULE.ExportError, "not found"):
            self._run_patch("media/missing.mp3", missing_media={"media/missing.mp3"})

    def test_audio_relative_path_escaping_deck_raises(self):
        with self.assertRaisesRegex(MODULE.ExportError, "escapes"):
            self._run_patch("../outside.mp3", missing_media={"../outside.mp3"})

    def test_audio_unknown_scheme_raises(self):
        with self.assertRaisesRegex(MODULE.ExportError, "http"):
            self._run_patch("ftp://host.example.com/a.mp3")

    @patch.object(MODULE.urllib.request, "urlopen", side_effect=OSError("connection refused"))
    def test_audio_url_download_failure_raises(self, _urlopen):
        with self.assertRaisesRegex(MODULE.ExportError, "failed to download audio"):
            self._run_patch("https://media.example.com/narration.mp3")

    @patch.object(MODULE, "MAX_AUDIO_FILE_BYTES", 10)
    def test_audio_oversized_local_file_raises(self):
        with self.assertRaisesRegex(MODULE.ExportError, "200 MiB"):
            self._run_patch("media/beep.mp3")

    @patch.object(
        MODULE.urllib.request,
        "urlopen",
        return_value=_FakeResponse(b"GOLDEN-URL-MP3-BYTES", {"Content-Length": "19"}),
    )
    def test_audio_url_download_success_embeds(self, _urlopen):
        result, out = self._run_patch("https://media.example.com/narration.mp3?t=1")
        self.assertEqual(result["audioParts"], 1)
        self.assertEqual(result["audioSlides"], 1)
        with zipfile.ZipFile(out) as archive:
            self.assertEqual(
                archive.read("ppt/media/audio1.mp3"), b"GOLDEN-URL-MP3-BYTES"
            )

    @patch.object(
        MODULE.urllib.request,
        "urlopen",
        return_value=_FakeResponse(b"", {"Content-Length": str(MODULE.MAX_AUDIO_FILE_BYTES + 1)}),
    )
    def test_audio_url_content_length_over_limit_raises(self, _urlopen):
        with self.assertRaisesRegex(MODULE.ExportError, "200 MiB"):
            self._run_patch("https://media.example.com/big.mp3")

    @patch.object(MODULE, "MAX_AUDIO_FILE_BYTES", 4)
    @patch.object(
        MODULE.urllib.request, "urlopen", return_value=_FakeResponse(b"0123456789", {})
    )
    def test_audio_url_chunked_download_over_limit_raises(self, _urlopen):
        with self.assertRaisesRegex(MODULE.ExportError, "200 MiB"):
            self._run_patch("https://media.example.com/chunky.mp3")

    @patch.object(
        MODULE.urllib.request,
        "urlopen",
        return_value=_FakeResponse(b"X", {"Content-Length": "not-a-number"}),
    )
    def test_audio_url_invalid_content_length_header_ignored(self, _urlopen):
        result, out = self._run_patch("https://media.example.com/a.mp3")
        self.assertEqual(result["audioParts"], 1)

    @patch.object(MODULE.urllib.request, "urlopen")
    def test_audio_url_incomplete_read_is_wrapped(self, urlopen):
        # A truncated body raises http.client.IncompleteRead (HTTPException),
        # which must be wrapped into ExportError with the bytes-received context
        # instead of escaping raw to the CLI handler.
        import http.client

        class BrokenResponse(_FakeResponse):
            def read(self, size=-1):
                if self._pos > 0:
                    raise http.client.IncompleteRead(b"partial", 100)
                self._pos = 4
                return b"PART"

        urlopen.return_value = BrokenResponse(b"PARTIAL-DATA")
        with self.assertRaisesRegex(
                MODULE.ExportError, "failed to download audio.*received 4 bytes"
        ):
            self._run_patch("https://media.example.com/truncated.mp3")


class AudioVerifyTests(unittest.TestCase):
    """AC7-8 verify_output 音频断言与 summary 字段."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_verify_output_reports_audio_summary(self):
        deck_root = self.root / "deck"
        make_deck(deck_root, [{"audio": "media/beep.mp3"}])
        out = self.root / "out.pptx"
        make_pptx(out, {1: xml_slide()})
        MODULE.patch_audio(out, deck_root)
        summary = MODULE.verify_output(out, "fade", False, deck=deck_root)
        self.assertEqual(summary["slides"], 1)
        self.assertEqual(summary["audioSlides"], 1)
        self.assertEqual(summary["audioParts"], 1)
        self.assertEqual(summary["fadeTransitions"], 1)

    def test_verify_output_raises_when_declared_audio_missing(self):
        deck_root = self.root / "deck"
        make_deck(deck_root, [{"audio": "media/beep.mp3"}])
        out = self.root / "out.pptx"
        make_pptx(out, {1: xml_slide()})
        with self.assertRaisesRegex(MODULE.ExportError, "audio"):
            MODULE.verify_output(out, "fade", False, deck=deck_root)

    def test_verify_summary_without_deck(self):
        deck_root = self.root / "deck"
        make_deck(deck_root, [{"audio": "media/beep.mp3"}])
        out = self.root / "out.pptx"
        make_pptx(out, {1: xml_slide()})
        MODULE.patch_audio(out, deck_root)
        summary = MODULE.verify_output(out, "fade", False)
        self.assertEqual(summary["audioSlides"], 1)
        self.assertEqual(summary["audioParts"], 1)

    def test_verify_ignores_unknown_extension_page(self):
        deck_root = self.root / "deck-unknown"
        make_deck(deck_root, [{"audio": "media/beep.xyz"}])
        out = self.root / "out.pptx"
        make_pptx(out, {1: xml_slide()})
        MODULE.patch_audio(out, deck_root)
        summary = MODULE.verify_output(out, "fade", False, deck=deck_root)
        self.assertEqual(summary["audioSlides"], 0)
        self.assertEqual(summary["audioParts"], 0)


class AudioExporterHookupTests(unittest.TestCase):
    """AC7-8 导出路径挂接: postprocess (transition → audio → verify)."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_postprocess_runs_pipeline_in_order(self):
        deck_root = self.root / "deck"
        make_deck(deck_root, [{"audio": "media/beep.mp3"}])
        out = self.root / "out.pptx"
        make_pptx(out, {1: xml_slide()})
        calls = []

        def recorder(name):
            def record(*args, **kwargs):
                calls.append((name, args, kwargs))
                return 1 if name == "patch_transitions" else {}
            return record

        with patch.object(MODULE, "patch_transitions", recorder("patch_transitions")), \
                patch.object(MODULE, "patch_audio", recorder("patch_audio")), \
                patch.object(MODULE, "verify_output", recorder("verify_output")):
            MODULE.postprocess_pptx(out, deck_root, "fade", False)
        self.assertEqual(
            [name for name, _args, _kwargs in calls],
            ["patch_transitions", "patch_audio", "verify_output"],
        )
        self.assertEqual(calls[-1][1], (out, "fade", False))
        self.assertEqual(calls[-1][2], {"deck": deck_root})

    def test_export_pptx_local_hooks_postprocess(self):
        manifest = make_deck(self.root / "deck-local", [{"audio": "media/beep.mp3"}])
        out = self.root / "out-local.pptx"
        make_pptx(out, {1: xml_slide()})
        with patch.object(
                MODULE.subprocess, "run",
                return_value=MODULE.subprocess.CompletedProcess([], 0, ""),
        ), patch.object(MODULE.shutil, "which", return_value="/bin/node"), \
                patch.object(MODULE, "postprocess_pptx", return_value={"slides": 1}) as post:
            summary = MODULE.export_pptx_local(manifest, out, "fade", force=True)
        self.assertEqual(summary["exporter"], "local-wasm-patched")
        post.assert_called_once_with(out, manifest.parent, "fade", expect_fonts=False)

    def test_export_pptx_browser_hooks_postprocess(self):
        manifest = make_deck(self.root / "deck-browser", [{"audio": "media/beep.mp3"}])
        out = self.root / "out-browser.pptx"
        downloaded = self.root / "Downloads" / "raw.pptx"
        downloaded.parent.mkdir(parents=True, exist_ok=True)
        make_pptx(downloaded, {1: xml_slide()})

        class FakeServer:
            def shutdown(self):
                return None

            def server_close(self):
                return None

        class FakeThread:
            def join(self, timeout=None):
                return None

        with patch.object(MODULE, "postprocess_pptx", return_value={}) as post, \
                patch.object(MODULE, "ensure_agent_browser", return_value="/bin/agent-browser"), \
                patch.object(MODULE, "ensure_debug_chrome", return_value=None), \
                patch.object(MODULE, "default_downloads_dir", return_value=self.root / "Downloads"), \
                patch.object(
                    MODULE, "serve_local_editor",
                    return_value=(FakeServer(), FakeThread(), "http://127.0.0.1:9/?ndExport=1"),
                ), \
                patch.object(
                    MODULE, "_open_export_dialog",
                    return_value={"snapshot": {}, "data": {"refs": {}}},
                ), \
                patch.object(MODULE, "switch_state", return_value=None), \
                patch.object(MODULE, "ref_by_name", return_value="e0"), \
                patch.object(MODULE, "find_download", return_value=downloaded), \
                patch.object(MODULE, "BrowserSession") as browser_class, \
                patch.object(MODULE.shutil, "copy2"), \
                patch.object(MODULE, "kill_debug_chrome"):
            summary = MODULE.export_pptx(
                manifest, out, "fade", True, force=True, prefer_local=False
            )
        self.assertEqual(summary["exporter"], "browser-local-editor")
        post.assert_called_once_with(out, manifest.parent, "fade", True)


def rewrite_zip(src: Path, dst: Path, replacements=None, additions=None, drops=frozenset()) -> None:
    """Copy a ZIP while replacing/adding/dropping specific members (for tampering)."""
    with zipfile.ZipFile(src) as source_zip, zipfile.ZipFile(dst, "w") as target_zip:
        for info in source_zip.infolist():
            if info.filename in drops:
                continue
            data = (replacements or {}).get(info.filename)
            if data is None:
                data = source_zip.read(info.filename)
            target_zip.writestr(info, data, compress_type=info.compress_type)
        for name, data in (additions or {}).items():
            target_zip.writestr(name, data)


class AudioSourceCollectionTests(unittest.TestCase):
    """collect_page_audio / patch_audio 快速路径与错误分支."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_collect_non_list_pages_returns_empty(self):
        root = self.root / "d1"
        root.mkdir()
        (root / "d.pptd").write_text("version: v2\npages: 0\n", encoding="utf-8")
        self.assertEqual(MODULE.collect_page_audio(root), [])

    def test_collect_skips_missing_page_file(self):
        root = self.root / "d2"
        root.mkdir()
        (root / "d.pptd").write_text(
            "version: v2\npages:\n  - pages/nope.page\n", encoding="utf-8"
        )
        self.assertEqual(MODULE.collect_page_audio(root), [])

    def test_collect_rejects_non_string_audio(self):
        root = self.root / "d3"
        (root / "pages").mkdir(parents=True)
        (root / "pages" / "01.page").write_text(
            "elements:\n  - elementId: t1\n    elementType: text\n    bounds: [0, 0, 1, 1]\n"
            "audio: [1, 2]\n",
            encoding="utf-8",
        )
        (root / "d.pptd").write_text(
            "version: v2\npages:\n  - pages/01.page\n", encoding="utf-8"
        )
        with self.assertRaisesRegex(MODULE.ExportError, "audio must be a string"):
            MODULE.collect_page_audio(root)

    def test_patch_audio_fast_path_when_no_sources(self):
        deck_root = self.root / "deck"
        make_deck(deck_root, [{}])
        out = self.root / "out.pptx"
        make_pptx(out, {1: xml_slide()})
        result = MODULE.patch_audio(out, deck_root)
        self.assertEqual(
            result,
            {"audioSlides": 0, "audioParts": 0, "audioSkippedUnknownExtensions": 0},
        )

    def test_patch_audio_missing_content_types_raises(self):
        deck_root = self.root / "deck"
        make_deck(deck_root, [{"audio": "media/beep.mp3"}])
        out = self.root / "noct.pptx"
        with zipfile.ZipFile(out, "w") as archive:
            archive.writestr("ppt/presentation.xml", "<p:presentation/>")
            archive.writestr("ppt/slides/slide1.xml", xml_slide())
        with self.assertRaisesRegex(MODULE.ExportError, "Content_Types"):
            MODULE.patch_audio(out, deck_root)


class AudioMergeStructureFailureTests(unittest.TestCase):
    """merge 各结构缺失路径 → 降级替换 + 警告."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.deck_root = self.root / "deck"
        make_deck(self.deck_root, [{"audio": "media/beep.mp3"}])

    def tearDown(self):
        self._tmp.cleanup()

    def _assert_degrades(self, timing_xml: str):
        out = self.root / "out.pptx"
        make_pptx(out, {1: xml_slide(timing=timing_xml)})
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            MODULE.patch_audio(out, self.deck_root)
        with zipfile.ZipFile(out) as archive:
            slide = archive.read("ppt/slides/slide1.xml")
        names = MODULE.root_child_names(slide)
        self.assertEqual(names.count("timing"), 1)
        self.assertIn(b"playFrom(0)", slide)
        self.assertIn("merge", err.getvalue())

    def test_merge_degrades_when_root_not_tmroot(self):
        self._assert_degrades(
            "<p:timing><p:tnLst><p:par>"
            '<p:cTn id="1" dur="indefinite" restart="never" nodeType="otherSeq"/>'
            "</p:par></p:tnLst></p:timing>"
        )

    def test_merge_degrades_when_no_seq(self):
        self._assert_degrades(
            "<p:timing><p:tnLst><p:par>"
            '<p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot">'
            '<p:childTnLst><p:par><p:cTn id="2" fill="hold"/>'
            "</p:par></p:childTnLst></p:cTn></p:par></p:tnLst></p:timing>"
        )

    def test_merge_degrades_when_seq_has_no_child_timing(self):
        self._assert_degrades(
            "<p:timing><p:tnLst><p:par>"
            '<p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot">'
            '<p:childTnLst><p:seq concurrent="1" nextAc="seek"/>'
            "</p:childTnLst></p:cTn></p:par></p:tnLst></p:timing>"
        )

    def test_merge_tolerates_non_numeric_ctn_ids(self):
        # _max_timing_id must skip non-numeric ids and renumber beyond the max
        weird = ANIMATION_TIMING.replace('<p:cTn id="10"', '<p:cTn id="abc"')
        out = self.root / "out.pptx"
        make_pptx(out, {1: xml_slide(timing=weird)})
        MODULE.patch_audio(out, self.deck_root)
        with zipfile.ZipFile(out) as archive:
            slide = archive.read("ppt/slides/slide1.xml")
        self.assertEqual(MODULE.root_child_names(slide).count("timing"), 1)
        root = ET.fromstring(slide)
        ids = [
            int(element.get("id"))
            for element in root.iter()
            if MODULE.local_name(element.tag) == "cTn"
            and str(element.get("id")).isdigit()
        ]
        self.assertTrue(any(cid >= 12 for cid in ids))


class AudioDirectHelperTests(unittest.TestCase):
    """直接单元测试: place_timing / add_audio_relationship / patch_slide_audio."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_patch_slide_audio_rejects_malformed_xml(self):
        with self.assertRaisesRegex(MODULE.ExportError, "invalid slide XML"):
            MODULE.patch_slide_audio(b"<broken", "rId1")

    def test_patch_slide_audio_rejects_missing_sp_tree(self):
        slide = f'<p:sld xmlns:p="{P_NS}"><p:foo/></p:sld>'.encode("utf-8")
        with self.assertRaisesRegex(MODULE.ExportError, "no spTree"):
            MODULE.patch_slide_audio(slide, "rId1")

    def test_patch_slide_audio_repositions_misplaced_merged_timing(self):
        # a mergeable timing placed before the fade transition violates CT_Slide
        # order; the merged timing must be repositioned after the transition.
        slide = (
            f'<p:sld xmlns:p="{P_NS}" xmlns:a="{A_NS}" xmlns:r="{R_NS}">'
            "<p:cSld><p:spTree><p:sp><p:nvSpPr><p:cNvPr id=\"2\" name=\"s\"/>"
            "<p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr/><p:txBody><a:bodyPr/>"
            '<a:lstStyle/><a:p/></p:txBody></p:sp></p:spTree></p:cSld>'
            f"<p:clrMapOvr/>{ANIMATION_TIMING}"
            '<p:transition spd="fast" advClick="1"><p:fade/></p:transition>'
            "</p:sld>"
        ).encode("utf-8")
        patched, _spid = MODULE.patch_slide_audio(slide, "rId9")
        self.assertEqual(
            MODULE.root_child_names(patched),
            ["cSld", "clrMapOvr", "transition", "timing"],
        )
        MODULE.validate_transition_order(patched, "fade")

    def test_patch_slide_audio_tolerates_non_numeric_shape_id(self):
        slide = xml_slide().decode("utf-8").replace(
            '<p:cNvPr id="2" name="Title 1"/>',
            '<p:cNvPr id="OLE1" name="OLE Object"/>',
        ).encode("utf-8")
        _patched, spid = MODULE.patch_slide_audio(slide, "rId1")
        self.assertEqual(spid, 2)

    def test_place_timing_after_clrmapovr_without_transition(self):
        root = ET.fromstring(
            f'<p:sld xmlns:p="{P_NS}"><p:cSld/><p:clrMapOvr/><p:extLst/></p:sld>'
        )
        MODULE.place_timing(root, ET.Element(f"{{{P_NS}}}timing"))
        self.assertEqual(
            [MODULE.local_name(child.tag) for child in root],
            ["cSld", "clrMapOvr", "timing", "extLst"],
        )

    def test_place_timing_after_csld_when_no_other_anchor(self):
        root = ET.fromstring(f'<p:sld xmlns:p="{P_NS}"><p:cSld/><p:extLst/></p:sld>')
        MODULE.place_timing(root, ET.Element(f"{{{P_NS}}}timing"))
        self.assertEqual(
            [MODULE.local_name(child.tag) for child in root],
            ["cSld", "timing", "extLst"],
        )

    def test_place_timing_raises_without_anchor(self):
        root = ET.fromstring(f'<p:sld xmlns:p="{P_NS}"><p:foo/></p:sld>')
        with self.assertRaisesRegex(MODULE.ExportError, "no timing insertion anchor"):
            MODULE.place_timing(root, ET.Element(f"{{{P_NS}}}timing"))

    def test_audio_content_types_without_closing_types_raises(self):
        with self.assertRaisesRegex(MODULE.ExportError, "</Types>"):
            MODULE.add_audio_content_type_overrides(
                b"<Types xmlns='urn:x'><Override/></TypesX>",
                {"ppt/media/audio1.mp3": "audio/mpeg"},
            )

    def test_add_audio_relationship_falls_back_to_count_for_non_numeric_ids(self):
        rels = rels_bytes([
            ("abc1", "http://schemas.example/x", "t1"),
            ("x7", "http://schemas.example/y", "t2"),
        ])
        out, r_id = MODULE.add_audio_relationship(rels, "ppt/media/audio1.mp3")
        self.assertEqual(r_id, "rId3")
        self.assertIn('Id="rId3"', out.decode("utf-8"))

    def test_add_audio_relationship_without_closing_raises(self):
        with self.assertRaisesRegex(MODULE.ExportError, "</Relationships>"):
            MODULE.add_audio_relationship(
                b"<Relationships xmlns='urn:x'><foo/></RelationshipsX>",
                "ppt/media/audio1.mp3",
            )


class VerifyAudioSlideFailureTests(unittest.TestCase):
    """verify_audio_slide 的逐条失败断言 (AC7-8 防回归)."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.deck_root = self.root / "deck"
        make_deck(self.deck_root, [{"audio": "media/beep.mp3"}])
        self.base = self.root / "base.pptx"
        make_pptx(self.base, {1: xml_slide()})
        MODULE.patch_audio(self.base, self.deck_root)

    def tearDown(self):
        self._tmp.cleanup()

    def _tampered(self, replacements=None, additions=None, drops=frozenset()):
        out = self.root / "tampered.pptx"
        rewrite_zip(
            self.base,
            out,
            replacements=replacements,
            additions=additions,
            drops=drops,
        )
        return out

    def _verify(self, path):
        with zipfile.ZipFile(path) as archive:
            return MODULE.verify_audio_slide(archive, 1)

    def _slide(self):
        with zipfile.ZipFile(self.base) as archive:
            return archive.read("ppt/slides/slide1.xml").decode("utf-8")

    def _rels(self):
        with zipfile.ZipFile(self.base) as archive:
            return archive.read("ppt/slides/_rels/slide1.xml.rels").decode("utf-8")

    def _content_types(self):
        with zipfile.ZipFile(self.base) as archive:
            return archive.read("[Content_Types].xml").decode("utf-8")

    def test_verify_missing_rels_part(self):
        with self.assertRaisesRegex(MODULE.ExportError, "no rels part"):
            self._verify(self._tampered(drops={"ppt/slides/_rels/slide1.xml.rels"}))

    def test_verify_missing_slide_xml_raises_export_error(self):
        # G3: archive.read() KeyError for a missing slide part must surface as
        # ExportError, not leak a bare KeyError.
        with self.assertRaisesRegex(MODULE.ExportError, "no slide XML part"):
            self._verify(self._tampered(drops={"ppt/slides/slide1.xml"}))

    def test_verify_invalid_slide_xml(self):
        with self.assertRaisesRegex(MODULE.ExportError, "invalid slide XML"):
            self._verify(self._tampered(
                replacements={"ppt/slides/slide1.xml": b"<broken"},
            ))

    def test_verify_two_timings(self):
        slide = self._slide().replace("</p:sld>", "<p:timing/></p:sld>")
        with self.assertRaisesRegex(MODULE.ExportError, "exactly one root-level timing"):
            self._verify(self._tampered(replacements={"ppt/slides/slide1.xml": slide.encode()}))

    def test_verify_no_timing(self):
        slide = re.sub(r"<p:timing>.*?</p:timing>", "", self._slide(), flags=re.DOTALL)
        with self.assertRaisesRegex(MODULE.ExportError, "exactly one root-level timing"):
            self._verify(self._tampered(replacements={"ppt/slides/slide1.xml": slide.encode()}))

    def test_verify_no_narration_command(self):
        slide = re.sub(r"<p:cmd[^>]*>.*?</p:cmd>", "", self._slide(), flags=re.DOTALL)
        with self.assertRaisesRegex(MODULE.ExportError, "no playFrom"):
            self._verify(self._tampered(replacements={"ppt/slides/slide1.xml": slide.encode()}))

    def test_verify_cmd_without_spid(self):
        slide = self._slide().replace('spid="3"', 'spid=""')
        with self.assertRaisesRegex(MODULE.ExportError, "no spTgt spid"):
            self._verify(self._tampered(replacements={"ppt/slides/slide1.xml": slide.encode()}))

    def test_verify_audio_shape_id_mismatch(self):
        slide = self._slide().replace(
            '<p:cNvPr id="3" name="Audio Placeholder 3"',
            '<p:cNvPr id="9" name="Audio Placeholder 3"',
        )
        with self.assertRaisesRegex(MODULE.ExportError, "no hidden audio shape"):
            self._verify(self._tampered(replacements={"ppt/slides/slide1.xml": slide.encode()}))

    def test_verify_audio_shape_without_embed(self):
        slide = re.sub(r'p:audioFile r:embed="rId\d+"', "p:audioFile", self._slide())
        with self.assertRaisesRegex(MODULE.ExportError, "no r:embed"):
            self._verify(self._tampered(replacements={"ppt/slides/slide1.xml": slide.encode()}))

    def test_verify_invalid_rels_xml(self):
        with self.assertRaisesRegex(MODULE.ExportError, "invalid slide rels XML"):
            self._verify(self._tampered(
                replacements={"ppt/slides/_rels/slide1.xml.rels": b"<Relationships"},
            ))

    def test_verify_relationship_missing(self):
        rels = re.sub(r'<Relationship Id="rId\d+"[^>]*/>', "", self._rels())
        with self.assertRaisesRegex(MODULE.ExportError, "is missing"):
            self._verify(self._tampered(
                replacements={"ppt/slides/_rels/slide1.xml.rels": rels.encode()},
            ))

    def test_verify_relationship_wrong_type(self):
        rels = self._rels().replace('/relationships/audio"', '/relationships/slide"')
        with self.assertRaisesRegex(MODULE.ExportError, "wrong Type"):
            self._verify(self._tampered(
                replacements={"ppt/slides/_rels/slide1.xml.rels": rels.encode()},
            ))

    def test_verify_relationship_without_target(self):
        rels = re.sub(r' Target="[^"]*"', "", self._rels())
        with self.assertRaisesRegex(MODULE.ExportError, "no Target"):
            self._verify(self._tampered(
                replacements={"ppt/slides/_rels/slide1.xml.rels": rels.encode()},
            ))

    def test_verify_media_part_missing(self):
        rels = self._rels().replace("audio1.mp3", "audio99.mp3")
        with self.assertRaisesRegex(MODULE.ExportError, "media part missing"):
            self._verify(self._tampered(
                replacements={"ppt/slides/_rels/slide1.xml.rels": rels.encode()},
            ))

    def test_verify_unknown_extension(self):
        rels = self._rels().replace("audio1.mp3", "audio1.flac")
        with self.assertRaisesRegex(MODULE.ExportError, "unknown extension"):
            self._verify(self._tampered(
                replacements={"ppt/slides/_rels/slide1.xml.rels": rels.encode()},
                additions={"ppt/media/audio1.flac": b"X"},
            ))

    def test_verify_missing_content_type_override(self):
        ct = re.sub(
            r'<Override PartName="/ppt/media/audio1\.mp3"[^>]*/>', "", self._content_types()
        )
        with self.assertRaisesRegex(MODULE.ExportError, "no \\[Content_Types\\].xml Override"):
            self._verify(self._tampered(
                replacements={"[Content_Types].xml": ct.encode()},
            ))

    def test_verify_skips_non_relationship_children(self):
        # a non-Relationship child before the audio Relationship must be
        # skipped (continue) without breaking the look-up
        rels = self._rels().replace("<Relationship ", "<foo/><Relationship ", 1)
        self._verify(self._tampered(
            replacements={"ppt/slides/_rels/slide1.xml.rels": rels.encode()},
        ))


if __name__ == "__main__":
    unittest.main()
