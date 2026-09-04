---
name: doc-scaffold
description: 为任意项目按参考范式建立完整的文档结构与机械门禁（pre-commit 检查）。Use when the user asks to 建立/补全文档体系、按某目录的文档范式建项目文档、安装文档机制检查、生成 DOCUMENTATION_STANDARDS 总表、给项目挂 pre-commit 文档门禁，或说「参考 X 的文档范式给 Y 建文档结构」「这个项目要按规范建核心文档」。目标：把「标准档四件套（AGENTS/PROJECT_REFERENCE/TO-TICKETS/DEV_LOG）+ 可选完整档 CODE_WIKI + 文档规范总表 + 三道机械检查（pool_cleanup/doc_sync/doc_standards）」装进指定项目目录，全部经机械验证。
---

# Doc Scaffold — 文档体系脚手架

## Overview

把本次 Model Fingerprint 文档体系审计沉淀为可复用流程：给定**目标项目目录**，参考**范式目录**（或 skill 内置模板），判定档位（标准档/完整档），补建核心文档（含 `DOCUMENTATION_STANDARDS.md` 文档规范总表），分发三道 pre-commit 机械检查脚本并挂载安装，最终全部检查跑绿。只建文档与机制，不碰业务代码。

## Resource Guide

- `references/standards-template.md` — `DOCUMENTATION_STANDARDS.md` 总表模板（六节结构 + 各文档角色/单一事实来源），复制后按目标项目实际文档改写登记表与门禁表。
- `references/audit-reference.md` — 档位判定规则、文档角色速查表、范式提取步骤（读范式目录时应看哪些文件、提哪些要素）。
- `scripts/pool_cleanup_check.py` — TO-TICKETS/TECH_DEBT 清出机制检查（标准档就分发）。
- `scripts/doc_sync.py` — CODE_WIKI 机械标记防漂移（仅完整档分发）。
- `scripts/doc_standards_check.py` — 文档规范总表检查（总表一经建立就必须分发，总表与检查成对存在）。
- `scripts/pre-commit.sh.template` / `scripts/install-hooks.bat.template` — 钩子源与安装器，复制到目标项目 `scripts/` 并改名去掉 `.template`。
- `examples/` — 实例 prompt 与预期行为。

## Workflow

### 1. 解析目标与范式

- 参数：`target`（目标项目目录，必填）；`reference`（范式目录，可选——缺省用 skill 内置 `references/standards-template.md` 作为范式）。
- 若给了 `reference`：读它的 `DOCUMENTATION_STANDARDS.md`（若有）作为主要范式；否则读其 `AGENTS.md` 文档分工表 + 根目录 `.md` 清单归纳。**只提取结构要素（文档角色/单一事实来源/滚动约定），不复制其叙述内容。**

### 2. 审计目标现状 + 判档位

- 枚举目标根目录 `.md` 文件与 `scripts/` 现有脚本，对照范式列出差距（缺哪些文档、缺哪些检查脚本）。
- 按 `references/audit-reference.md` 判档：模块数 ≥ 8 且 文档 > 1 页 且 多场景引用 → **完整档**（+ CODE_WIKI + doc_sync）；否则 **标准档**。已有 `CODE_WIKI.md` 的直接按完整档处理。

### 3. 补建核心文档（只补缺、不重写已有）

- **标准档四件套**：`AGENTS.md`（行为规矩 + 文档分工表 + 怎么跑起来）、`PROJECT_REFERENCE.md`（项目介绍/技术栈/目录约定/当前状态）、`TO-TICKETS.md`（唯一任务池，活跃表 + 已完成归档）、`DEV_LOG.md`（已做记录）。已存在的核对职责声明与滚动约定，缺失才补。
- **完整档追加**：`CODE_WIKI.md`（技术细节单一权威源，含四类机械标记占位）+ 在 `AGENTS.md` 分工表登记 CODE_WIKI 行。**§3 文件树必须引用全部分发的 `scripts/*.py`**——doc_sync 的 files 双向覆盖要求「仓库全部 .py 必须被文档引用」，漏引分发的检查脚本会导致刚建好的完整档 `doc_sync --check` 立即报漂移；生成 CODE_WIKI 时把三道脚本的引用一并写入。
- **文档规范总表必建**：`DOCUMENTATION_STANDARDS.md`——复制 `references/standards-template.md`，按目标项目实际文档改写①登记表（每行一个核心文档 + 角色 + 单一事实来源）、②格式约定、④门禁表（引用实际分发的脚本）。**总表建立后，doc_standards_check 检查立即生效：登记表必须覆盖仓库根目录全部 `.md`，门禁表引用的脚本必须存在，pre-commit.sh 必须调用三脚本。**
- 其他按实际需要：`TECH_DEBT.md`（技术债候选池）、`CONTEXT.md`（领域词汇）、`KNOWLEDGE_BASE.md`（知识库登记点）、`README.md`/`MANUAL.md`（用户视角）——目标项目存在对应需求才建，不强求。

### 4. 分发机制脚本 + 挂载

- 复制 `pool_cleanup_check.py` + `doc_standards_check.py` 到目标 `scripts/`（两道标准库检查，任何档位都装）。
- 完整档另复制 `doc_sync.py`；标准档不复制（pre-commit 模板已对无 CODE_WIKI.md 情况自动跳过；doc_standards_check 门禁脚本存在性同样自适应——标准档门禁表引用 `doc_sync.py` 不要求其存在，模板门禁表可原样复制）。
- 复制 `pre-commit.sh.template` → `scripts/pre-commit.sh`、`install-hooks.bat.template` → `scripts/install-hooks.bat`（去掉 `.template`）。
- 运行 `install-hooks.bat`（或手动 `cp scripts/pre-commit.sh .git/hooks/pre-commit`）安装钩子。

### 5. 机械验证（完成门）

- 跑 `python scripts/pool_cleanup_check.py --check`、`python scripts/doc_standards_check.py --check`、`python scripts/doc_sync.py --check`（完整档）三检查全绿。
- 跑 `sh .git/hooks/pre-commit` 实测 EXIT=0。
- 目标项目有 pytest 的：全量测试 + 覆盖率门槛确认。

### 6. 输出报告

按 Output Protocols 报告差距→改动→验证。不 commit、不 push（除非用户明确要求）。

## 调用方与交接

- **规则源**：全局 AGENTS.md §3.6 文档体系档位制——本 skill 是该规则的执行器（档位判定 + 文档补建 + 机械门禁）；§3 任务池生命周期、§3.5 知识库闭环由分发的检查脚本机械落实，规则正文唯一权威仍在 AGENTS.md。
- **编排方**：project-kickoff 分支 B 步骤 0「骨架检查/搭建」——完整模式项目建骨架时调用本 skill，把最小骨架升级为标准档/完整档 + 机械门禁；轻量模式项目不建文档梯子，不调用。neat-freak 收尾发现文档体系缺失/机制未装时，可调用本 skill 补建（可选衔接）。
- **输入契约**：`target`（目标项目目录，必填）+ `reference`（范式目录，可选，缺省用 skill 内置模板）。
- **输出契约**：核心文档 + `scripts/` 三道检查 + pre-commit 挂载 + 验证报告（差距→改动→验证）；不 commit/push。
- **消费方**：目标项目的 pre-commit 钩子（每次提交的机械门禁）；后续 kickoff 会话的预检（TO-TICKETS 活跃表读取）与收尾（TO-TICKETS 归档、Neat 文档核对）。

## Output Protocols

完成报告形状：

```md
## Doc Scaffold 报告
- 目标项目：<路径> | 档位：<标准档/完整档>
- 范式来源：<reference 路径 | skill 内置模板>
- 差距清单：<缺的文档/脚本逐项>
- 补建/修改：<文档与脚本逐个列出，标注 新建/修改/核对通过>
- 机械验证：三检查各自 OK/FAIL + pre-commit 实测 EXIT + pytest 结果
- 未执行：<commit/push 等未做动作>
- 已知局限：<目标项目特有的偏差或未覆盖项>
```

文档清单表登记规则：登记名 = 根目录 `.md` 裸文件名（反引号包裹，如 `` `AGENTS.md` ``）；含路径引用（如 `docs/x.md`）只校验存在性、不入登记集合；跨仓库外部参考（如范式出处）进 doc_standards_check 的 `_KNOWN_EXTERNAL` 白名单。

## Boundaries

- **不碰业务代码**：只建文档与 `scripts/` 机制脚本，不改目标项目 `src/` 逻辑。
- **不重写已有文档**：已有文档核对职责声明与格式约定，缺什么补什么；不整篇替换用户已维护的内容。
- **不强制升档**：模块少的小工具按标准档装（无 CODE_WIKI/doc_sync），不硬塞完整档仪式。
- **不伪造事实**：文档中的测试数/覆盖率/模块行数由 doc_sync 机械标记生成或如实核验，不手写编造。
- **不越权 git**：不 init/commit/push/改历史，除非用户明确要求。
- **不复制叙述**：从范式目录只提取结构与约定，不照搬其业务描述/历史/遥测。

## Quality Standard

- 目标项目三检查全绿（标准档为两道 + 总表检查），`pre-commit` 实测 EXIT=0。
- 登记表与仓库根 `.md` 双向覆盖通过（doc_standards_check 反向覆盖：新增根级 `.md` 必须登记，防漏）。
- 门禁表引用的脚本全部真实存在（标准档引用 `doc_sync.py` 时豁免其存在性）；pre-commit.sh 调用全部已分发脚本。
- 有 pytest 的项目全量测试通过且覆盖率达标（≥90%）。
- 报告如实列出差距、改动、验证与未做动作，不夸大完成度。

## 自身回归

改脚本/模板后回放 `examples/README.md` 的回归 prompt，对照预期行为核验；快速干跑（标准档，约 2 分钟）：

1. 建临时项目：`mkdir -p <tmp>/repo/scripts && cd <tmp>/repo && git init`
2. 分发：复制 `scripts/` 三脚本 + `pre-commit.sh.template` → `scripts/pre-commit.sh`，再复制到 `.git/hooks/pre-commit`
3. 建最小标准档文档（AGENTS / PROJECT_REFERENCE / TO-TICKETS / DEV_LOG / TECH_DEBT / DOCUMENTATION_STANDARDS，登记表覆盖根目录全部 `.md`；**门禁表保留 doc_sync 行**——验证档位自适应豁免）
4. 断言：`sh .git/hooks/pre-commit` EXIT=0；负向——新增未登记根级 `.md` 或活跃表置 ✅ → EXIT=1
5. 完整档追加：`CODE_WIKI.md`（§3 文件树含 `scripts/*.py` 引用）+ 复制 `doc_sync.py`，断言 `doc_sync --check` 输出「同步 OK」

回滚：本 skill 目录在 `~/.zcode/skills` 仓库中为未跟踪状态，改动无法用 git 回滚——修改前先 `cp -r` 备份到 `D:\tmp\doc-scaffold-backup-<日期>`，回滚以备份为准。
