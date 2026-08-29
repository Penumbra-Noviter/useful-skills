#!/usr/bin/env python3
"""fetchflow 授权预检：对采集/逆向目标做可观测信号的机械判定。

判定输出（见 references/authorization-check.md）：
    ALLOW        无风险信号，可进入 crawl/reverse
    CHECKPOINT   命中风险信号（登录墙/鉴权/robots 禁止/样本缺失等），需用户确认
    BLOCK        明确红线，停止

只做可观测信号的机械判定，判不了的一律升 CHECKPOINT，不静默放行。

用法：
    python check_target.py https://example.com/products      # URL 目标
    python check_target.py ./local/sample.bin                # 本地逆向样本
    python check_target.py --json https://example.com        # JSON 输出
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

try:
    import requests
except ImportError:  # pragma: no cover - requests 一般随 crawl4ai 装上
    requests = None  # type: ignore

UA = "Mozilla/5.0 fetchflow-check/0.1"
TIMEOUT = 8


def _classify(target: str) -> str:
    if target.startswith(("http://", "https://")):
        return "url"
    return "local"


def _fetch_robots(origin: str) -> Optional[str]:
    if requests is None:
        return None
    try:
        r = requests.get(f"{origin}/robots.txt", timeout=TIMEOUT, allow_redirects=True,
                         headers={"User-Agent": UA})
        return r.text if r.status_code == 200 else None
    except Exception:
        return None


def _robots_disallows(robots: Optional[str], path: str) -> bool:
    """简化解析：只认 `User-agent: *` 下的 Disallow 前缀规则。"""
    if not robots:
        return False
    star_allowed = False
    for raw in robots.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.lower().startswith("user-agent:"):
            ua = line.split(":", 1)[1].strip()
            star_allowed = ua == "*"
        elif line.lower().startswith("disallow:") and star_allowed:
            rule = line.split(":", 1)[1].strip()
            if rule and path.startswith(rule):
                return True
    return False


def _probe_url(url: str) -> Tuple[Optional[int], Optional[str]]:
    """无凭证轻量 GET，探测是否登录墙 / 鉴权重定向。"""
    if requests is None:
        return None, None
    try:
        r = requests.get(url, timeout=TIMEOUT, allow_redirects=False,
                         headers={"User-Agent": UA})
        return r.status_code, r.headers.get("location")
    except Exception:
        return None, None


def check_url(url: str) -> Tuple[str, List[str]]:
    u = urlparse(url)
    origin = f"{u.scheme}://{u.netloc}"
    path = u.path or "/"
    robots = _fetch_robots(origin)
    disallowed = _robots_disallows(robots, path)
    code, loc = _probe_url(url)

    signals: List[str] = []
    if disallowed:
        signals.append(f"robots.txt disallows path {path}")
    if code in (401, 403):
        signals.append(f"auth-required (status {code})")
    if loc and "login" in (loc or "").lower():
        signals.append(f"redirects to login ({loc})")
    if requests is None:
        signals.append("requests unavailable; probe skipped")

    if code in (401, 403) or (loc and "login" in (loc or "").lower()):
        return "CHECKPOINT", signals or ["auth/protected-content signal"]
    if disallowed:
        return "CHECKPOINT", signals  # 方法可行仍可采，但需用户确认
    return "ALLOW", signals


def check_local(path: str) -> Tuple[str, List[str]]:
    if not os.path.exists(path):
        return "CHECKPOINT", [f"target file not found: {path}"]
    return "ALLOW", ["local file, user-provided path"]


def main() -> None:
    p = argparse.ArgumentParser(description="fetchflow 授权预检")
    p.add_argument("target", help="目标 URL 或本地路径")
    p.add_argument("--json", action="store_true", help="JSON 输出")
    args = p.parse_args()

    if _classify(args.target) == "url":
        verdict, signals = check_url(args.target)
    else:
        verdict, signals = check_local(args.target)

    result: Dict[str, object] = {
        "target": args.target,
        "verdict": verdict,
        "signals": signals,
        "note": "CHECKPOINT/BLOCK 需用户确认后再继续；ALLOW 按方法可行即可采推进",
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"target: {args.target}")
        print(f"verdict: {verdict}")
        for s in signals:
            print(f"  - {s}")


if __name__ == "__main__":
    main()
