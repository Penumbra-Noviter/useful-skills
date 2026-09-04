# DOCUMENTATION_STANDARDS — Model Fingerprint 文档规范总表

> 2026-09-04 固化（对齐 Craft 项目范式，见 hanhua `docs/documentation-standards.md`）。本文件是各核心文档的**规范总表**（角色 / 单一事实来源 / 格式与滚动约定）。
> 核心原则：**同一信息只允许存在于一个文档，其他文档引用而非复制**——凡在两处出现即漂移信号，须合并或改为引用。
> 明细规则以 `AGENTS.md`（行为规矩）与各文档头部声明为准，本表只做索引与对照，不复制规则正文。

---

## 一、文档清单与单一事实来源分配

| 文档 | 角色 | 唯一来源（什么信息只归它管） |
|------|------|------------------------------|
| `AGENTS.md` | 行为规矩（标准档必配） | 项目模式判定 / 任务池生命周期 / 文档体系档位 / 知识库路由 / 编码惯例。**agent guide 一律命名 AGENTS.md** |
| `PROJECT_REFERENCE.md` | 项目介绍（标准档） | 背景、目标、技术栈、架构概述、目录约定、当前状态。**不复制技术细节** |
| `TO-TICKETS.md` | **唯一任务池**（标准档） | 已立项/在执行的工单 + 已完成归档。待办**绝不落** DEV_LOG / memory / 个人笔记 |
| `DEV_LOG.md` | 已做 + 叙述（标准档） | 完成记录、来源/Grilling 共识/验证链/过程遥测、bug 根因。只记「已做」，不记待办（TO-TICKETS 唯一事实源） |
| `TECH_DEBT.md` | 技术债候选池 | 未立项候选（编号/来源/强度/状态/归属方向）+ 复核关闭表 + 处置记录；不自动进入 preflight 认领 |
| `CODE_WIKI.md` + `scripts/doc_sync.py` | 完整档（升档后） | 技术细节单一权威源 + 代码导览（**兼 CODE_MAP 职能，不另建 CODE_MAP**）；机械标记防漂移 |
| `CONTEXT.md` | 领域词汇 | load-bearing 术语登记（维度/判定/报告/中转站等），供架构评审、设计与编码统一使用 |
| `KNOWLEDGE_BASE.md` | 知识库路由（项目侧登记点） | 所属 vault / 项目页 / persona / 经验路径（当前：Obsidian `demo` 程序开发 vault） |
| `README.md` | 用户视角 | 它是解决什么问题、两种探测模式、安装、CLI 用法、权重表、已知局限 |
| `MANUAL.md` | 用户手册 | 面向桌面程序的全流程操作手册（GUI 内嵌渲染，`gui_app.py` 读取并展示） |
| `CONSENSUS.md` | 需求 + 架构决策 | 需求定义（用户画像/核心需求/非目标）+ ADR 决策记录（当前到 ADR-0011）。**ADR 内嵌本文件，不另建 docs/adr/** |
| `ALGORITHM_OPTIMIZATION.md` | 算法交接文档 | 评分算法（贝叶斯融合/校准）现状、严谨性缺口、候选方法、实验数据的完整汇总，供后续 Agent 优化评分逻辑 |
| `RESEARCH_BACKGROUND.md` | 调研落盘 | 学术资料（模型识别/水印/MGT 检测/替换审计/校准理论）的文献综述，全部经一手来源在线核实 |
| `DOCUMENTATION_STANDARDS.md` | 本文件（规范总表） | 上表全部文档的角色分配与滚动约定索引。**单一事实来源在各自文档**，本表只做指针 |

## 二、格式约定

### DEV_LOG.md（滚动机制）
- 排序：主区**日期倒序（最新在前）**；尾部「批次补录区」为历史批次正序流水（批次 7~50 补录，既有布局不重排）；中段为「归档方式 / 已完成 / Bug 修复记录」说明区
- 会话节格式：`### YYYY-MM-DD — 标题`，每节含：背景/改动/验证/流程遥测
- 只记「已做」；Bug 修复条目带 文件、行号、症状、修复方案、回归测试
- 溯源：被后续整理压缩的叙述由 git 历史承担——`git log -p -- DEV_LOG.md`
- 注：DEV_LOG 为主题分区布局（非纯编年），不做日期顺序机械强制（补录区正序为既有事实）

### TO-TICKETS.md（任务池生命周期，`AGENTS.md` §3）
- 状态流转：📝 已录入 → 🔄 进行中（开始实现前认领）→ ✅/❌ 完成 → 移入「已完成归档」并记完成日期
- 归档 = **每批一行的纯索引**（批次/工单+提交/一句话摘要/DEV_LOG 会话指针）；「历史归档索引」行数上限 60，超限删最旧
- 活跃表禁止 ✅ 滞留（会话结束 commit 前检查）；多 session 防污染（条目带来源，只认领匹配方向的条目）
- 叙述职责归位：工单事实（编号/标题/日期/提交）入归档行，来源/共识/验证链/遥测只写 DEV_LOG.md

### TECH_DEBT.md（候选池清出机制）
- 候选区条目含 6 字段（编号/遗留项/来源/强度/状态/归属方向，详见文件头部「规范说明」）
- 候选区只留开放条目（📝 待立项 / 🔄 进行中）；处置后整行移出，处置详情写入「技术债处置记录」（滚动保留最近 2 节）
- ❌ 关闭条目：具复核价值的压缩为单行摘要（防 review 重复提出），其余删除
- 消费 = 显式立项（候选区 → TO-TICKETS 活跃工单，或标记 ❌ 不立项附理由）

## 三、测试规范（Testing Standards）

- `pytest` + `pytest-cov`，覆盖率门槛 ≥ 90%（机械门控，`pytest.ini` 固化为 `--cov-fail-under=90`；当前全量 2065 项 / 98.20%）
- 每个 bug fix 先加复现测试再修；验证默认取向是**证伪**（先测失败路径，再测 happy path）
- 全量测试基线数字以 DEV_LOG 最新会话与 CODE_WIKI `tests_total` 标记为准（引用而非复制）

## 四、机械门禁

| 门禁 | 挂载点 | 作用 |
|------|--------|------|
| `scripts/pool_cleanup_check.py --check` | pre-commit（`scripts/pre-commit.sh`，可执行） | TO-TICKETS/TECH_DEBT 清出机制机械合规（候选区状态/复核关闭/活跃表无 ✅❌/归档索引 ≤60/脚注编号一致/必要节/表格列数异常），失败拒提交 |
| `scripts/doc_sync.py --check` | pre-commit（依赖 pytest，未装则跳过不阻塞） | CODE_WIKI 机械标记（tests_total/模块行数/方法签名/文件引用双向覆盖）防漂移；漂移时先 `python scripts/doc_sync.py` 刷新再提交 |
| `scripts/doc_standards_check.py --check` | pre-commit | 本文档（文档规范总表）合规：文档清单表格式/登记文档与根目录 .md 双向覆盖/门禁表脚本存在/pre-commit 挂载三脚本，失败拒提交 |

钩子由 `scripts/install-hooks.bat` 安装到 `.git/hooks/pre-commit`（不入库）；手动测试 `sh .git/hooks/pre-commit` 应 EXIT=0。

## 五、知识库闭环（`AGENTS.md` §3.5）

- 库路由：`KNOWLEDGE_BASE.md` 声明 vault（当前 Obsidian `demo` 程序开发 vault；注册表在 `demo/项目/README.md`）
- 预检（读）：先按路由选库，按 frontmatter `project:` 限定范围，两级加载（先扫摘要再精读），单次注入 ≤5 条 / ≤1000 字
- 蒸馏（写）：阶段完成有教训时经 `distill-lesson` skill 写原子笔记（`summary` + `provenance` 必填）；无教训不写
- 记忆分工：经验本体入知识库，zcode 会话 memory 只留快速指针（单向权威，细节以知识库为准）

## 六、档位制（`AGENTS.md` §3.6）

| 档位 | 文档 | 启用条件（全部满足才升档） |
|------|------|------|
| 标准档（默认） | AGENTS.md + PROJECT_REFERENCE.md + TO-TICKETS.md + DEV_LOG.md | — |
| 完整档 | 标准档 + CODE_WIKI.md + `scripts/doc_sync.py` | 模块数 ≥ 8 且 文档 > 1 页 且 多场景引用 |

**本项目当前状态：完整档（2026-08-15 升档通过，批次数 ≥ 50）**。新增核心文档须先在本表登记角色与单一事实来源，再落盘。