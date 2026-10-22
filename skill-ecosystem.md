# Skill 生态分工记录（2026-08-27 建档，2026-10-23 对齐）

> 整个用户 skill 库实际是一个 git 仓库目录 `D:\Desktop\cc\.claude\skills`（branch `main`）。
> `C:\Users\Administrator\.zcode\skills` 是指向它的 **Junction（目录联接）**，不是副本、不是软链符号——所以「zcode 侧路径」与「真实仓库路径」指的是同一份文件，改哪边都是改这里。
> dao 三件套与下面的同构 skill 同处一库，无物理分仓。
> 本文与 `SKILL_MAP.md`（功能反向检索）、`README.md`（对外介绍 + 9 域表）、`ask-matt`（动态路由表）四者互为校验；冲突时以 `ask-matt` SKILL.md 为准。

## 一、dao 三件套（skill 领域的元编排，2026-08-27）

### 分层架构

```text
dao-skill（元设计器/生命周期管理层）
  ├── 归根（Mode A）— 根问题分析
  ├── 设计（Mode B）— skill 形态定位
  ├── 生成（Mode C）— 路由到执行器
  ├── 评估（Mode D）— Trust Gate + 证据分级 + 评分 + P0/P1/P2
  ├── 返观进化（Mode E）— 失败复盘 + 保守补丁 + 回滚
  └── 自化吸收（Mode F）— 外部方法论/证据 → 体系内规则/参考/SkillBank
                            ↓
              ┌───────────────┴──────────────┐
              ↓                              ↓
      skill-authoring                cangjie-skill
      （创作层：写 skill 内容）            （长内容蒸馏：书/视频/播客→skill）
       
      - 结构（anatomy）              - RIA-TV++ 流水线
      - 写作原则（principles）        - 5 并行提取器 → 三重验证 → RIA++ 构造
      - 调用机制（invocation）        - 压力测试（诱饵/跨 skill 混淆）
      - 创建流程（process）           - 输出 darwin-compatible skill
      - 脚本（init/package/validate）
```

### 分工

| 职责 | 谁做 | 谁触发 |
|---|---|---|
| 根问题分析、评估、进化、吸收外部方法论 | **dao-skill** | 用户说"评估/进化/吸收" |
| 写具体 skill 文件（SKILL.md + 结构 + 原理） | **skill-authoring** | dao-skill 的 Mode C/D/E 路由，或用户直接说"写个 skill" |
| 从书/长视频/播客/课程蒸馏出一组 skill | **cangjie-skill** | dao-skill 的 Mode F 吸收外部方法论时路由，或用户直接说"拆书/蒸馏" |

### 安装位置

三个都在库根，直接用路径 `D:\Desktop\cc\.claude\skills\<name>`：

- `dao-skill` — 外部实装，自带 `.git`、可独立 `git pull --ff-only`（源码零改动），因此被 `.gitignore` 排除，**不入本库版本治理**
- `skill-authoring` — 整合版（含 ADR-001），入库
- `cangjie-skill` — 复制落地，AGPL v3 上游，排除了营销 assets；v2.5.0 起上游转 MIT；入库

## 二、同构 skill 树（编排/分工盘点，2026-08-29 建档，2026-10-23 复核）

库中与 dao 三件套同模式（编排入口 + 路由到执行器 / 领域内分工）的结构，按编排强度分三层。

### 第一层 · 编排/路由型（自己不干活，路由到命名执行器）

**ask-matt（全库路由器）** — 库中编排层级最高
- 定位：`Router over the skills in this repo`；整个库的顶层路由图，`disable-model-invocation`，用户手动 `/ask-matt` 触发
- 路由契约：
  - 主流程（idea → ship）：`/grill-with-docs`（有工作目录时；无目录用 `/grill-me`）→（跨 phase 用 `/handoff` 桥接 `/prototype` 验证回路）→ 多会话工程走 `/to-spec` → `/to-tickets`（tracer-bullet 工单带阻塞边）→ 每票 `/implement`（内部驱动 `/tdd`，一个红绿切片一次）；想把整份 spec 一次 orchestrate 完 → `/implement-spec`（任务图 + ready frontier 并行 implementer + 单集成分支）→ 上 PR 时 `/pr` 塑形 PR 正文 → 提交前 `/code-review` → 事后 `/retro` 复盘环境
  - on-ramp：`/product-facets`（新项目或审计既有项目 → 面图带进主流程）；`/triage`（外部来的 bug/请求 → agent-ready issue → `/implement` 认领，自己产出的工单不 triage）；`/diagnosing-bugs`（硬 bug，修后依情况衔接 `/improve-codebase-architecture`，事后跑 `/retro`）；`/wayfinder`（浓雾大工程 → 地图清晰后**折回 `/to-spec`**，不可直接 `/implement`）
  - 词汇下垫层（model-invoked，跑在别的 skill 底下）：`/domain-modeling`（领域词汇 + ADR）、`/codebase-design`（深模块词汇，`/tdd` 与 `/improve-codebase-architecture` 共用）
  - 推理下垫层：`/simple-logic`（9 张逻辑能力卡，Falsify 轴、AGENTS.md 对抗性自检、grill 家族共用的具名检查表）
  - 前置条件：先跑 `/setup-matt-pocock-skills`（配置 issue tracker / triage 标签 / 文档布局）
- 与 dao-skill 关系：同为"元路由"，作用域不同——ask-matt 路由全库工程流，dao-skill 路由 skill 领域

**fetchflow（采集+逆向薄编排层）** — 与 dao-skill 结构同构度最高
- 定位：不重写底层能力，只做三件事——路由决策、跨模块组合、统一证据协议
- 路由契约：按意图 route → **crawl**（`modules/crawl`，svc 名 `fetchflow-crawl`，委托 crawl4ai 引擎）/ **reverse**（`modules/reverse`，svc 名 `fetchflow-reverse`，委托 `reverse-flow` skill）/ **chain**（`crawl→reverse`：被反爬挡 → 先逆向 → 带对抗方案回 crawl；`reverse→crawl`：逆向出私有 API → 直接采）
- 门禁：Step 0 授权预检 `scripts/check_target.py <target>` → `ALLOW` / `CHECKPOINT`（停止摆给用户确认）/ `BLOCK`（红线停止，预检结果作为报告第一项证据）
- 输出：统一 `shared-evidence-protocol` 结构；证据绑 url/offset/函数/字符串/哈希/status_code
- 边界：不重写 crawl4ai 提取策略与反爬逻辑、不重写 reverse-flow 阶段流程与证据协议；红线=不采集受法律保护数据、不做 DoS

**project-kickoff（工程全流程总编排）**
- 定位：一句工程目标 → 走完整工程开发规范直到交付；是 ask-matt 主流程的"自动化版执行器"
- 激活契约：**仅用户显式点名时激活**（kickoff / 用 kick / 接续 kick / 继续 kick 流），不自动触发；支持从部分完成的任务续接
- 编排契约（以派发子智能体为主，非命名 skill 路由）：
  - 路由决策四维：产品效果确定度 / 实现路径确定度 / 规模初判 / 确认档位（谨慎/快速/全自动，任意档下阻断性修复、删除清场、最终交付都要用户确认）+ 项目模式（完整/轻量）
  - 分支 A（雾厚）：**Wayfinder 子智能体** → 地图内 prototype / research / grilling 类型票嵌套对应子智能体 → 折回主线；no-fog 早退 = 空地图直接进主线
  - 分支 B（主线）：preflight（知识库预检 → 工程 preflight → 技术债预检 → 交付形态确认 → 骨架检查）→ **Grilling 子智能体** → **plan-tickets 子智能体**（spec + 工单带文件范围/共享文件清单/阻塞边/元数据表，切票上限 1000 行/10 源文件）→ spike/research 分流（技术风险点）→ 依赖分析后**串并行分发多个 Implement 子智能体**（worktree 隔离）→ 测试诚实协议 + 四状态报告 + 完成门校验 → **code-review 子智能体**（含修复轮次上限）→ **Neat 收尾**
- 空返回降级：spike/research 子智能体连续 2 次空返回 → 有界验证任务主会话直做，不三派不上报

**finesse-ui（UI 域路由入口）**
- 定位：高端 Web 界面 skill 入口，按 register 路由
- 路由契约（§0.A）：brand（设计即产品）/ product（产品 UI，再分 dashboard/analytics、workflow、AI assistant 三 sub-register）/ zine / diagram 四 register；
  - 纸刊/拼贴/照片类 brief → 路由到独立 **`zine-ui`** skill（实景拼贴/影像蒸馏/抽象记忆面板三路径）
  - 架构图/流程图/时序图/ER 图等 → 路由到独立 **`diagram-design`** skill（**45 图型**，含架构增量/轴测/桑基/鱼骨/Wardley/服务蓝图/故事地图；draw.io/Mermaid/Excalidraw 导入；HTML/SVG/PNG 导出）
- 继承契约：zine-ui 与 diagram-design 继承 finesse 的 craft floor + cheapness blacklist + a11y 门（全表在 finesse `references/design-dna.md` §1 与 `references/anti-cheap.md`）；无跨 register 继承（dashboard 不是品牌页加图表）

### 第二层 · skill 内子智能体分派（编排但不跨命名 skill）

- **code-review**：按固定点 diff 派轴评审——Standards 与 Spec **并行**；Falsify（构造让改动崩溃的输入/状态）在编排方请求时作**第三轴**；Architecture（模块结构评估）在 kickoff 期末审核语境加入成四轴。支持编排方要单轴（单轴增量跑）；审计者姿态（只报问题不修）；本文件是 `agents/code-review.md` 的唯一来源
- **implement-spec**：读 to-tickets 产物成**任务图** → 按 ready **frontier** 并行派 implementer 子智能体 → 全部落在**一个集成分支**；适合"想编排整份 spec"而非逐票手动推
- **wayfinder**：大工程 → issue tracker 上的共享地图 + decision tickets（research / prototype / grilling / task 四类，HITL vs AFK），逐票消解到路径清晰；每张 grilling 票**同时调用 grilling + domain-modeling 两个 skill**；产**决策不产交付物**，地图清晰即交棒回 `/to-spec`；（project-kickoff 分支 A 以子智能体方式嵌套消费它）
- **research**：委托后台 agent 读 primary source，产出带引用的 markdown 文件，供主流程消费（喂给 grill-with-docs / to-spec）

### 第三层 · 领域内分工流水线（writer 域）

- **writing 三件套**（fragments/shape/beats 全部 `disable-model-invocation`，由编排层代跑）
  - **编排层 `writing`**（model-invoked，2026-08-29 补）：接写作意图 → 查产物文件判阶段（文件即状态）→ 路由到三件套并显式传 pile/产物路径，替代手动串联、提高触发命中率。默认产物路径 `writing/fragments.md`（explore）+ `writing/article.md`（exploit）；阶段可跳过（有素材直接 exploit）；不重写三件套机制，执行时 Read 子 skill 的 SKILL.md，冲突以子 skill 为准。成文后有去味需求 → 路由 `writing-humanizer`
  - 分工契约：`writing-fragments`（explore：grilling 式访谈挖碎片，产出 H1 + `---` 分隔的碎片文件，只 append 不删改）→ `writing-shape`（exploit：起点驱动逐段成文，线性正式文章）**|** `writing-beats`（exploit：选择冒险式逐 beat 推进，叙事旅程）；**shape 与 beats 是替代关系不是接力**
  - 核心纪律：Grounding（概念先落地才能被引用；prerequisite 读者自带 vs introduced 文内引入；两块均可 lean 只能落在 grounded 上）；explore 声明"定结构越界"、exploit 声明"挖新料越界"——互斥认知模式的拆分
  - 产物契约：碎片文件手动喂给 exploit；exploit 视碎片文件为只读采石场，产出独立文章文件
  - `writing-humanizer` 只做**成文后的去味润色**，不接管 explore / exploit
- **grilling 原语 + 包装**：`grilling`（访谈原语，无包装）→ `grill-me`（无状态包装，无工作目录时）/ `grill-with-docs`（留 CONTEXT.md + ADR 纸面痕迹，有工作目录时）/ `loop-me`（限定本工作区内的工作流 spec 访谈）；triage / wayfinder / improve-codebase-architecture 内部也消费 grilling 原语
- **知识闭环双半环**：`kb-search`（读取：报错/写测试前/重构前查既有经验，只读）↔ `distill-lesson`（写入：把本次教训蒸馏成 Obsidian 原子笔记）

## 三、治理文档与门禁（2026-10-23 新增）

### 入库边界

| 文件 | 是否入库 | 说明 |
|---|---|---|
| `README.md` | 入库 | 对外介绍 + 9 域 skill 表 + 编排架构 + 来源许可 |
| `PROVENANCE.md` | 入库 | 全库来源登记（vendored / distilled / 自研 / 封装判定、上游 URL、本地改动点、同步流程）；改 skill 前先查它 |
| `SKILL_MAP.md`（本文档同目录） | 入库 | 功能反向检索表（"要做的事 → 用哪个 skill"），含触发词 |
| `skill-ecosystem.md` | 入库 | 本文档：生态分工与编排层级记录 |
| `TO-TICKETS.md` / `TECH_DEBT.md` / `DEV_LOG.md` | **不入库**（`.gitignore`） | 本地参考，不纳入 git 版本治理 |

> 变更说明：2026-10-23 之前，本文件与 `SKILL_MAP.md` 放在 zcode 默认工作区（`C:\Users\Administrator\.zcode\workspace\default\`），README 里写着"仓库内不重复维护"。该约定已废止——两份图谱移入库根，README 对应条目同步改写，此后随仓库一起版本化。

### pre-commit 门禁

`.githooks/pre-commit`（已启用：`core.hooksPath = .githooks`）在**新增/删除/变更 skill** 时强制两件事同步：

1. `ask-matt` 的全库路由表登记（新增 skill 未登记 → 拦截；删除 skill 未清残 → 拦截）
2. `README` 的 skill map 同步（commit 后的库事实与地图漂移 → 拦截）

因此任何 skill 增删改的提交，实际要一并改的是：`SKILL.md` + `ask-matt` + `README`（+ 涉及来源时 `PROVENANCE.md`）；若新增/删除改变了数量与归类，再同步 `SKILL_MAP.md` 与本文件。

## 四、与 dao 三件套的关系

| 维度 | dao 三件套 | 同构 skill |
|---|---|---|
| 编排作用域 | skill 领域（元设计器 → 执行器） | 全库工程流（ask-matt）/ 采集逆向（fetchflow）/ 工程流程（project-kickoff）/ UI 域（finesse-ui） |
| 编排机制 | 命名 skill 路由（dao → skill-authoring / cangjie） | 命名 skill 路由（fetchflow → crawl4ai+reverse-flow；finesse-ui → zine-ui+diagram-design）；writing 薄路由（→ fragments/shape/beats/humanizer）；或子智能体分派（project-kickoff / implement-spec / code-review / wayfinder） |
| 分工层级 | 元设计器 → 执行器（创作/蒸馏） | 路由器 → 执行器（同）；原语 → 包装（grilling；writing explore/exploit；kb-search/distill-lesson 读写双半环） |
| 编排强度 | 强（dao 决策、执行器干活） | 最强 ask-matt（全库路由）→ project-kickoff/fetchflow/finesse-ui（域编排）→ implement-spec（spec 级并行）→ writing 编排层（域内薄路由）→ code-review/wayfinder/research（内部分派）→ 最弱 grilling 原语（纯分工） |

## 五、本次对齐的变更（2026-10-23）

| 项 | 旧记录 | 现事实 |
|---|---|---|
| 库路径表述 | `~/.zcode/skills` → 符号链接 | Junction（目录联接）→ `D:\Desktop\cc\.claude\skills`，同一份文件 |
| dao 三件套安装位置 | 写作 `C:\...\.zcode\skills\<name>` | 写作真实路径 `D:\Desktop\cc\.claude\skills\<name>`（Junction 侧等价但易误判为独立副本） |
| 库规模 | 70 个 skill（含 4 条已失效条目） | 67 个仓库内 skill + 9 个插件族条目 |
| diagram-design | 27 图型 | 45 图型 |
| code-review 轴 | Standards / Spec / Falsify 三子智能体并行 | Standards+Spec 并行、Falsify 按需第三轴、Architecture 入 kickoff 期末；支持单轴增量 |
| 实现侧 | 只有 implement | 增 implement-spec（任务图 + frontier 并行 + 单集成分支）、pr（PR 正文） |
| 复盘 | 未记录 | retro（复盘改环境不改代码），diagnosing-bugs 修完也跑它 |
| 推理层 | 未记录 | simple-logic（9 张逻辑能力卡），ask-matt 有独立 `Reasoning underneath` 章节 |
| 文档族命名 | `document-skills:docx/pdf/pptx/xlsx` | `documents:docx` / `pdf:pdf` / `presentations:pptx` / `spreadsheets:xlsx` |
| 图表编排 | `open-kimi-ppt` | 已改名 `to-ppt`（PPTD 工程 + 本地 .pptx） |
| context-monitor | 列为域 0 成员 | 目录已不存在，已移除 |
