#!/usr/bin/env python3
"""文档规范总表（DOCUMENTATION_STANDARDS.md）机械检查（挂 pre-commit，失败即拒绝提交）。

只读、无副作用——遵循仓库「gate first, side effects after」惯例，本脚本只报告违规与
处置指引，绝不自动修改文档（登记/删除由人按指引执行，git 历史可溯）。

职责：CODE_WIKI 有 doc_sync（标记 + .py 引用双向覆盖）、TO-TICKETS/TECH_DEBT 有
pool_cleanup_check（清出机制），DOCUMENTATION_STANDARDS.md 作为「文档家族登记表」
由本脚本站岗，检查四项：

1. **总表内部格式**：文档清单表列数与表头一致（防列错位漏读）、无重复文档行、
   登记行首格必须为反引号包裹的根级 .md 文件名（`AGENTS.md`）——新增文档须按该
   格式登记，正文引用不参与登记集合。
2. **文档 ↔ 仓库根目录 .md 双向覆盖**：登记集合（无斜杠 .md 名）每个必须存在于
   仓库根目录；仓库根目录全部 *.md（含未来新增）必须在登记集合——新建核心文档
   漏登记 / 登记文档被删都会被拦截。含路径的 .md 引用（如 `docs/adr/xxx.md`）单独
   校验存在性，不入登记集合（根级登记语义）。
3. **门禁脚本存在性**：「四、机械门禁」节引用的 `scripts/*.py` 必须存在于仓库——
   门禁表引用失效（删除/改名）被拦截。档位自适应：标准档项目（仓库无 `CODE_WIKI.md`）
   不分发 `doc_sync.py`，门禁表引用它时豁免脚本存在性——与 pre-commit.sh 的
   `[ -f CODE_WIKI.md ]` 跳过逻辑同构，模板门禁表可原样复制、无需按档位删行。
4. **pre-commit 挂载**：`scripts/pre-commit.sh` 必须调用三道门禁脚本
   （pool_cleanup_check / doc_sync / doc_standards_check）——新增门禁忘挂钩被拦截
   （与检查 3 互补：表里写了但钩子没挂）。

表格解析契约：单元格不得含未转义 `|`（Markdown 表格列分隔符）；含则列数错位，
由检查 1 报格式异常并在提交前修复，而非误读文档名列。
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

__all__ = ["REQUIRED_HOOKS", "check_standards", "main"]

STANDARDS_FILE = "DOCUMENTATION_STANDARDS.md"
PRE_COMMIT = "scripts/pre-commit.sh"
# 应挂载的门禁脚本文件名（防新增门禁忘挂钩；与 pre-commit.sh 实际调用强校验）
REQUIRED_HOOKS = ("pool_cleanup_check.py", "doc_sync.py", "doc_standards_check.py")
# 文档清单表（一、）与门禁表（四、）节标题
TABLE_SECTION = "## 一、文档清单与单一事实来源分配"
GATE_SECTION = "## 四、机械门禁"
_TOP_HEADING = "## "
# 反引号引用的 .md / scripts/*.py；md 名分「根级裸名」与「含路径」两形态。
# 脚本引用匹配反引号内 `scripts/xxx.py` 前缀——表格行惯写 `scripts/x.py --check`，
# `--check` 等旗标同在反引号内，后缀匹配在 .py 处截断。
_MD_REF_RE = re.compile(r"`([A-Za-z0-9_./\\-]+\.md)`")
_SCRIPT_REF_RE = re.compile(r"`(scripts/[A-Za-z0-9_./\\-]+\.py)")
# 必要节存在性：整行精确匹配（防「## 四、机械门禁（变体）」被子串判断误认存在）
_SECTION_LINE_RE = lambda s: re.compile(rf"^{re.escape(s)}$", re.MULTILINE)
# 表头首格标签（防把表头行当数据行）
_HEADER_FIRST_CELLS = {"文档"}
# 已知跨仓库外部参考文档（总表头部引用参考项目范式等合法引用；误录防误报，手动维护）。
# 示例条目：docs/documentation-standards.md——外部仓库的范式文档，无需在本仓库存在。
# 目标项目无此类外部引用时保持空集。
_KNOWN_EXTERNAL = frozenset({"docs/documentation-standards.md"})


def _cells(line: str) -> list[str]:
    """表格行去壳取格（去头尾竖线、去空白）。

    契约：单元格内含未转义 `|` 属格式缺陷——由 _table_rows 的列数校验报格式异常，
    而非在本层猜测列位（与 pool_cleanup_check 同契约）。
    """
    core = line.strip()
    if core.startswith("|"):
        core = core[1:]
    if core.endswith("|"):
        core = core[:-1]
    return [c.strip() for c in core.split("|")]


def _section_table(
    text: str, start: str, end_prefix: str | None
) -> tuple[list[list[str]], list[str]]:
    """取节内表格行：返回 (数据行, 格式异常行原文)。

    限界 = 下一个顶级节（## ）；表头行（首格属 _HEADER_FIRST_CELLS）的列数即表格
    契约列数。空态占位行（_（无）_）跳过；列数不符的行列为格式异常（绝不静默跳过）。
    """
    lines = text.splitlines()
    rows: list[list[str]] = []
    malformed: list[str] = []
    expect_cells: int | None = None
    on = False
    for line in lines:
        if line.startswith(start):
            on = True
            continue
        if on and end_prefix is not None and line.startswith(end_prefix):
            break
        if not on:
            continue
        stripped = line.strip()
        if not stripped or not stripped.startswith("|"):
            continue
        if set(stripped) <= {"|", "-", " ", ":"}:
            continue  # 表头分隔行
        cells = _cells(line)
        if not cells:
            continue
        if cells[0] in _HEADER_FIRST_CELLS:
            expect_cells = len(cells)
            continue
        if len(cells) == 1 and cells[0] in {"_（无）_", "（无）", "暂无", "—"}:
            continue  # 单格空态占位行
        if expect_cells is not None and len(cells) != expect_cells:
            malformed.append(stripped[:80])
            continue
        rows.append(cells)
    return rows, malformed


def _registered_md_names(rows: list[list[str]]) -> list[str]:
    """从文档清单数据行首格提取根级 .md 名（`AGENTS.md` → AGENTS.md）。

    每行首个无斜杠 .md 引用为登记名；含路径（docs/x.md）不入登记集合。首格
    无反引号 .md 引用 = 未按格式登记（交由 _check_registration_format 报错）。
    """
    names: list[str] = []
    for cells in rows:
        m = _MD_REF_RE.search(cells[0])
        if m and "/" not in m.group(1):
            names.append(m.group(1).replace("\\", "/"))
    return names


def _check_table_format(rows: list[list[str]], malformed: list[str]) -> list[str]:
    violations: list[str] = []
    for r in malformed:
        violations.append(f"文档清单表 表格格式异常（应 3 列：文档/角色/唯一来源）：{r}")
    seen: dict[str, int] = {}
    for cells in rows:
        m = _MD_REF_RE.search(cells[0])
        if not m:
            violations.append(
                f"文档清单表 登记行首格未按格式写根级 .md 文件名（`Xxx.md`）：{cells[0][:60]!r}"
            )
            continue
        name = m.group(1)
        seen[name] = seen.get(name, 0) + 1
    dups = [n for n, c in seen.items() if c > 1]
    for n in dups:
        violations.append(f"文档清单表 重复登记文档「{n}」×{seen[n]}")
    return violations


def _check_md_coverage(
    text: str, rows: list[list[str]], root: Path
) -> list[str]:
    violations: list[str] = []
    registered = set(_registered_md_names(rows))

    # 正向：登记集合每个必须存在于根目录
    for name in sorted(registered):
        if not (root / name).is_file():
            violations.append(f"文档清单表 登记文档不存在于仓库根目录: {name}")

    # 反向：根目录全部 *.md 必须已登记（新增核心文档漏登记被拦截）
    root_mds = {p.name for p in root.glob("*.md")}
    for name in sorted(root_mds - registered):
        violations.append(f"仓库根目录 .md 未登记进文档清单表（新增文档须登记角色与单一事实来源）: {name}")

    # 含路径的 .md 引用（登记集合之外）：引用存在性校验（如 `docs/adr/xxx.md`）
    for m in _MD_REF_RE.finditer(text):
        ref = m.group(1).replace("\\", "/")
        if "/" in ref and ref not in _KNOWN_EXTERNAL and not (root / ref).is_file():
            violations.append(f"总表引用不存在的文档: {ref}")
    return violations


def _check_gate_scripts(text: str, root: Path) -> list[str]:
    violations: list[str] = []
    in_gate = False
    seen: set[str] = set()
    for line in text.splitlines():
        if line.startswith(GATE_SECTION):
            in_gate = True
            continue
        if in_gate and line.startswith(_TOP_HEADING):
            break
        if in_gate:
            for m in _SCRIPT_REF_RE.finditer(line):
                seen.add(m.group(1))
    # 档位自适应：标准档（无 CODE_WIKI.md）不分发 doc_sync.py，门禁表若引用它
    # 则不要求脚本存在——与 pre-commit.sh 的 `[ -f CODE_WIKI.md ]` 跳过逻辑同构，
    # 使模板门禁表可原样复制、无需按档位删行。
    tier_optional = (
        {"scripts/doc_sync.py"} if not (root / "CODE_WIKI.md").is_file() else set()
    )
    for ref in sorted(seen):
        if ref in tier_optional:
            continue
        if not (root / ref).is_file():
            violations.append(f"机械门禁表 引用不存在的脚本: {ref}")
    return violations


def _check_precommit_hooks(text: str, root: Path) -> list[str]:
    violations: list[str] = []
    hook = root / PRE_COMMIT
    if not hook.is_file():
        return [f"缺少 {PRE_COMMIT}（pre-commit 钩子安装源，门禁挂载载体）"]
    content = hook.read_text(encoding="utf-8")
    for name in REQUIRED_HOOKS:
        if name not in content:
            violations.append(
                f"pre-commit.sh 未调用门禁脚本 {name}——新增门禁须挂钩（scripts/install-hooks.bat 重装到 .git/hooks/pre-commit）"
            )
    return violations


def check_standards(root: Path) -> list[str]:
    """对文档规范总表执行全部检查，返回违规列表（空 = 合规）。返回前已做存在性兜底。"""
    standards = root / STANDARDS_FILE
    if not standards.is_file():
        return [f"缺少 {STANDARDS_FILE}（文档规范总表）"]
    text = standards.read_text(encoding="utf-8")
    if not text.strip():
        return [f"{STANDARDS_FILE} 为空（应含一~六节，文档清单表登记全部核心文档）"]

    violations: list[str] = []
    # 必要节存在性：一（登记表）与 四（门禁表）是机械检查的锚点节
    for section in (TABLE_SECTION, GATE_SECTION):
        if not _SECTION_LINE_RE(section).search(text):
            label = section.lstrip("# ")
            violations.append(f"{STANDARDS_FILE} 缺少「{label}」节")

    rows, malformed = _section_table(text, TABLE_SECTION, _TOP_HEADING)
    violations += _check_table_format(rows, malformed)
    violations += _check_md_coverage(text, rows, root)
    violations += _check_gate_scripts(text, root)
    violations += _check_precommit_hooks(text, root)
    return violations


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="文档规范总表机械检查（pre-commit 挂载，失败 exit 1；检查仓库根 DOCUMENTATION_STANDARDS.md）"
    )
    # --check 为兼容既有 hook 引用而保留：恒执行检查，不改变行为
    ap.add_argument("--check", action="store_true", help="执行检查（默认即执行，兼容显式调用）")
    args = ap.parse_args(argv)
    root = Path(__file__).resolve().parent.parent
    violations = check_standards(root)
    if violations:
        print(f"[doc-standards] {len(violations)} 项不通过：")
        for v in violations:
            print(f"  - {v}")
        print("处置指引：文档清单表按 `Xxx.md` 格式登记全部根级核心文档（含角色/单一事实来源）；")
        print("          门禁表引用真实存在的 scripts/*.py；pre-commit.sh 调用三道门禁后重装钩子；")
        print("          可 git commit --no-verify 临时绕过，但请随后补上。")
        return 1
    print("[doc-standards] OK：文档清单登记 / 双向覆盖 / 门禁脚本 / pre-commit 挂载全部合规")
    return 0


if __name__ == "__main__":
    sys.exit(main())