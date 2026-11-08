#!/usr/bin/env python3
"""fetchflow 回归 smoke：examples 中 E3 路径的可重放确定性检查。

默认只跑离线路径（make_case 建 case、check_target 本地判定）；
--net 追加探测失败路径与 run_crawl 实采（crawl4ai 未安装则 SKIP，不算 FAIL）。
exit 0 = 无 FAIL；FAIL/SKIP 明细逐行打印，结果可粘进统一报告的「已验证事实」。

用法：
    python scripts/smoke_examples.py            # 离线 smoke
    python scripts/smoke_examples.py --net      # 含网络探测与 crawl4ai 实采
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from typing import List, Optional, Tuple

__all__ = ["run_smoke", "main"]

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
UNREACHABLE = "http://nonexistent-domain-fetchflow-smoke.invalid/"


def _run(cmd: List[str], timeout: int = 120) -> Tuple[int, str]:
    """运行子进程，返回 (exit code, 合并输出)。"""
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


class _Smoke:
    """结果收集器：PASS/FAIL/SKIP 逐行打印，汇总决定 exit code。"""

    def __init__(self) -> None:
        self.failures: List[str] = []

    def ok(self, name: str, passed: bool, detail: str = "") -> None:
        if passed:
            print(f"[PASS] {name}")
        else:
            print(f"[FAIL] {name} — {detail}")
            self.failures.append(name)

    def skip(self, name: str, reason: str) -> None:
        print(f"[SKIP] {name} — {reason}")


def _check_make_case(s: _Smoke, tmp: str) -> None:
    """对应 examples/crawl-route.md 步骤 2：case 工作区结构与 manifest。"""
    out = os.path.join(tmp, "work")
    code, out_text = _run([PY, os.path.join(SCRIPTS, "make_case.py"),
                           "--case", "smk", "--goal", "smoke", "--out", out])
    manifest = os.path.join(out, "smk", "manifest.json")
    ok = code == 0 and os.path.isfile(manifest)
    if ok:
        with open(manifest, encoding="utf-8") as f:
            data = json.load(f)
        ok = all(k in data for k in ("case", "goal", "created_at")) and \
            all(os.path.isdir(os.path.join(out, "smk", d))
                for d in ("artifacts", "triage", "reports", "raw"))
    s.ok("make_case: case 结构 + manifest 字段", ok, out_text.strip()[-200:])


def _check_target_local(s: _Smoke, tmp: str) -> None:
    """对应 authorization-check.md 逆向侧信号：缺文件 CHECKPOINT / 存在 ALLOW。"""
    script = os.path.join(SCRIPTS, "check_target.py")
    missing = os.path.join(tmp, "no-such-sample.bin")
    code, out_text = _run([PY, script, missing])
    s.ok("check_target: 本地缺文件 → CHECKPOINT",
         code == 0 and "CHECKPOINT" in out_text, out_text.strip()[-200:])

    probe = os.path.join(SCRIPTS, "check_target.py")
    code, out_text = _run([PY, script, probe])
    s.ok("check_target: 本地存在 → ALLOW",
         code == 0 and "ALLOW" in out_text, out_text.strip()[-200:])


def _check_target_probe_failure(s: _Smoke) -> None:
    """P1-1 回归锚点：不可达目标必须 CHECKPOINT，不静默放行。"""
    code, out_text = _run([PY, os.path.join(SCRIPTS, "check_target.py"), UNREACHABLE],
                          timeout=60)
    s.ok("check_target: 探测失败 → CHECKPOINT（不静默放行）",
         code == 0 and "CHECKPOINT" in out_text, out_text.strip()[-200:])


def _check_run_crawl(s: _Smoke) -> None:
    """对应 README 验证节 crawl E3：example.com markdown 实采。"""
    code, _ = _run([PY, "-c", "import crawl4ai"])
    if code != 0:
        s.skip("run_crawl: crawl4ai 实采", "crawl4ai 未安装（pip install -U crawl4ai）")
        return
    code, out_text = _run([PY, os.path.join(SCRIPTS, "run_crawl.py"),
                           "https://example.com/", "--extraction", "markdown"], timeout=180)
    ok = code == 0
    if ok:
        try:
            data = json.loads(out_text[out_text.index("{"):out_text.rindex("}") + 1])
            ok = bool(data.get("success")) and (data.get("markdown_len") or 0) > 0
        except (ValueError, IndexError):
            ok = False
    s.ok("run_crawl: example.com markdown 实采 success=True", ok, out_text.strip()[-200:])


def run_smoke(with_net: bool) -> int:
    """执行全部 smoke 检查，返回 exit code（0 = 无 FAIL）。"""
    s = _Smoke()
    with tempfile.TemporaryDirectory(prefix="fetchflow-smoke-") as tmp:
        _check_make_case(s, tmp)
        _check_target_local(s, tmp)
        if with_net:
            _check_target_probe_failure(s)
            _check_run_crawl(s)
        else:
            s.skip("check_target: 探测失败路径（--net）", "离线模式")
            s.skip("run_crawl: crawl4ai 实采（--net）", "离线模式")
    print(f"\nsummary: {len(s.failures)} FAIL"
          + (f" → {', '.join(s.failures)}" if s.failures else "，smoke 通过"))
    return 1 if s.failures else 0


def main() -> None:
    p = argparse.ArgumentParser(description="fetchflow 回归 smoke")
    p.add_argument("--net", action="store_true", help="追加网络探测与 crawl4ai 实采")
    args: Optional[argparse.Namespace] = p.parse_args()
    sys.exit(run_smoke(args.net))


if __name__ == "__main__":
    main()
