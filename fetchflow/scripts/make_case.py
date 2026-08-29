#!/usr/bin/env python3
"""fetchflow 建 case 工作区：为一次采集/逆向/组合任务建立统一目录与清单。

借鉴 reverse-flow 的 create_case.py 思路（保持最小），产出可被
shared-evidence-protocol 消费的结构：
    <out>/<case-name>/
        artifacts/      # 原始产物（逆向样本副本等）
        triage/         # 分诊 JSON（逆向时由 reverse-flow 的 triage_artifact.py 填充）
        reports/        # 报告
        raw/            # 采集原始输出
        manifest.json   # 清单

用法：
    python make_case.py --case my-target --goal "爬取 + 逆向该目标" --out ./work
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone


def build_case(case_name: str, goal: str, out: str) -> str:
    root = os.path.join(out, case_name)
    for sub in ("artifacts", "triage", "reports", "raw"):
        os.makedirs(os.path.join(root, sub), exist_ok=True)
    manifest = {
        "case": case_name,
        "goal": goal,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "modules": ["crawl", "reverse"],  # 按任务实际使用裁剪
    }
    manifest_path = os.path.join(root, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    return root


def main() -> None:
    p = argparse.ArgumentParser(description="fetchflow 建 case 工作区")
    p.add_argument("--case", required=True, help="case 名")
    p.add_argument("--goal", default="", help="目标描述")
    p.add_argument("--out", default=".", help="父目录")
    args = p.parse_args()
    root = build_case(args.case, args.goal, args.out)
    print(f"case 已创建: {root}")


if __name__ == "__main__":
    main()
