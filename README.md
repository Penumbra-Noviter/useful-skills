# useful-skills

Claude Code / zcode 的个人技能库：**63 个可执行 skill（本仓库）+ 7 个插件族条目**，覆盖从立项、编码、质量到情报、内容生产、UI 设计、设备自动化的完整工程流。每个 skill 是一个自包含目录（`SKILL.md` + 可选 `references/` / `scripts/` / `examples/`），按触发词被模型自动调用或由用户显式 `/` 唤起。

## 快速开始

```bash
git clone https://github.com/Penumbra-Noviter/useful-skills.git
# 把各 skill 目录放进你的 agent skills 目录（如 ~/.claude/skills/），或用符号链接
# zcode 环境的实际指向：D:\Desktop\cc\.claude\skills
```

不知道怎么用哪个技能时，直接问 **`/ask-matt`** ——它是全库的动态路由器（`disable-model-invocation`，用户手动触发），按「要做的事」路由到正确 skill 或流程。

## 生态总览（9 域）

本仓库 63 个 skill 按功能分成 9 个域；另有 7 个插件族条目（`document-skills` 四件套、`android-emulator`、`browser-use` 两件套）随宿主环境提供，不在此仓库。

### 域 0 · Skill 生态自治

| Skill | 用途 |
|---|---|
| `ask-matt` | 全库动态路由器——不知道该用哪个 skill 时先问它 |
| `context-monitor` | 查看当前会话上下文占用（token 用量） |
| `vibehub` | Vibe Coding 时把口语描述翻译成准确术语 |
| `dao-skill` | 设计/审计/优化/进化 skill 的元设计器 |
| `skill-authoring` | 编写、结构化、打包 SKILL.md / AGENTS.md 等 agent 文档 |
| `cangjie-skill` | 拆书/蒸馏长内容（书/视频/播客/课程）→ 一组可执行 skill |

### 域 1 · 立项与规划

| Skill | 用途 |
|---|---|
| `product-facets` | 立项时推导正交「面」（功能/UI/责任/安全/发布/运维…），逐面设计校验 |
| `grilling` | 对计划/想法做压力测试 |
| `grill-me` | 无状态访谈包装，打磨计划或设计 |
| `grill-with-docs` | 同 grill-me，顺带产出 ADR 与术语表 |
| `loop-me` | 关于工作流 spec 的访谈（限定工作区内） |
| `to-questionnaire` | 自己答不完的决策 → 转成给别人的问卷 |
| `to-spec` | 把对话合成 spec 发布到 issue tracker |
| `to-tickets` | 把计划/spec 拆成带阻塞边的工单 |
| `wayfinder` | 超大工程 → 画成决策 tickets 地图逐个攻破 |
| `project-kickoff` | 一句话工程目标 → 走完整开发流水线（共识→spec→并行实现→评审→收尾） |
| `doc-scaffold` | 搭标准文档骨架（AGENTS/TO-TICKETS/DEV_LOG + pre-commit 门禁） |

### 域 2 · 编码实施

| Skill | 用途 |
|---|---|
| `implement` | 按 spec/tickets 实现：TDD 垂直切片 + 类型检查 + 全量测试 + 自审 |
| `tdd` | 测试驱动开发（red-green-refactor） |
| `prototype` | 一次性原型回答设计问题，答完即弃 |
| `setup-pre-commit` | Husky pre-commit：格式化 + 类型检查 + 测试 |
| `setup-ts-deep-modules` | 给 TS 仓库接线 dependency-cruiser 深模块约束 |
| `setup-matt-pocock-skills` | 首次使用工程类 skill 前初始化仓库（issue tracker、triage 词汇表） |
| `migrate-to-shoehorn` | 测试里 `as` 断言迁移到 @total-typescript/shoehorn |
| `scaffold-exercises` | 生成练习目录结构（章节/问题/解答/讲解） |

### 域 3 · 架构与质量

| Skill | 用途 |
|---|---|
| `codebase-design` | 深模块设计：接口切分、seam 位置、可测试可导航 |
| `domain-modeling` | 构建/打磨领域模型（CONTEXT.md / ADR） |
| `improve-codebase-architecture` | 扫描代码库找深化机会 → HTML 报告 → grill |
| `improve-python-architecture` | 同上，针对 Python |
| `simplify-codebase` | 基于证据的简化审计：删死代码、去重、拆冗余抽象 |
| `code-review` | 定点 diff 多轴评审（Standards + Spec 并行，Falsify 按需第三轴） |
| `diagnosing-bugs` | 疑难 bug / 性能回归诊断闭环 |
| `resolving-merge-conflicts` | 解决进行中的 git merge/rebase 冲突 |
| `git-guardrails-claude-code` | 给 Claude Code 装 git 安全钩子，拦危险命令 |
| `triage` | issue/外部 PR 状态机：分类、验证、写 agent-ready 简报 |
| `neat-freak` | 收尾整理：文档/规则/记忆与代码事实对齐 |
| `distill-lesson` | 经验教训蒸馏成原子笔记写入 Obsidian 知识库 |
| `kb-search` | 程序开发知识库的实时经验检索（只读） |
| `threat-model` | 写码前 STRIDE 威胁建模 → 可验证的安全需求清单 |

### 域 4 · 情报与调研

| Skill | 用途 |
|---|---|
| `agent-reach` | 全网调研/搜索任何话题 |
| `research` | 对高信任一手来源做调研，结果存为仓库内 markdown |
| `fetchflow` | 采集 + 逆向编排（爬取/反爬对抗/接口逆向，可组合） |
| `reverse-flow` | 纯逆向工作流（二进制/固件/APK/脚本/协议/样本） |
| `museon-cli` | 社媒研究/运营：内容、账号、排期、发布、复盘 |

### 域 5 · 文档与内容生产

| Skill | 用途 |
|---|---|
| `open-kimi-ppt` | 演示文稿创建/编辑/复刻/导出（PPTD 工程 + 本地 .pptx） |
| `officecli` | Office 文档 CLI：创建/检查/排版/渲染 docx/xlsx/pptx |
| `writing` | 长篇写作编排入口 → 路由三件套正确阶段 |
| `writing-fragments` | 写作探索：挖原始素材碎片 |
| `writing-shape` | 写作收束：素材线性排成文章 |
| `writing-beats` | 写作叙事：素材排成节拍旅程 |
| `writing-humanizer` | 去 AI 味润色，让文本像人写的 |
| `diagram-design` | 27 种示意图 → 内联 SVG HTML，可导入 draw.io/Mermaid |
| `obsidian-vault` | Obsidian 笔记搜索/创建/整理（wikilink + 索引） |

### 域 6 · UI 设计

| Skill | 用途 |
|---|---|
| `finesse-ui` | 高质量 web 界面（品牌/产品/工作流/AI 助手），防廉价感 |
| `zine-ui` | 照片/诗意类 brief 的纸面材料语言（实景拼贴/影像蒸馏/抽象记忆面板） |

### 域 7 · 设备与环境自动化

| Skill | 用途 |
|---|---|
| `wizard` | 生成交互式 bash 向导，把只有人能做的步骤交给人类 |
| `vision` | 本地/网络图片的识别与分析 |
| `quarkclouddrive` | 夸克网盘：上传/下载（断点续传）、分享/转存、搜索、批量重命名、相册、AI 助手 |

### 域 8 · 交接与辅助

| Skill | 用途 |
|---|---|
| `handoff` | 当前会话压缩成交接文档 |
| `claude-handoff` | 立即把会话交给全新后台 agent |
| `wait-what` | 上一条没被理解：停下来重新表述 |
| `teach` | 在本工作区教一个新技能/概念 |
| `universal-exam-cram-coach` | 考前极速复习：解析大纲 → 知识库+题库 → 刷题判分 → 错题复盘 |

## 编排架构

仓库内有几层编排结构，理解它们能更快找到正确入口：

- **`ask-matt`（全库路由器）**：`disable-model-invocation`，用户手动触发；主流程 `grill-with-docs → to-spec → to-tickets → implement → code-review`，on-ramp 走 `triage` / `diagnosing-bugs` / `wayfinder`。
- **dao 三件套（skill 领域元编排）**：`dao-skill`（元设计器/生命周期管理）→ 路由到 `skill-authoring`（创作层）与 `cangjie-skill`（长内容蒸馏）。
- **`project-kickoff`（工程全流程总编排）**：一句目标 → Grilling 共识 → spec/tickets → 串并行分发多个 Implement 子智能体（worktree 隔离）→ 测试诚实协议 → code-review 审核 → Neat 收尾。
- **`fetchflow`（采集+逆向薄编排）**：按意图路由到 crawl（crawl4ai）/ reverse（`reverse-flow`）/ chain 组合，Step 0 授权预检。
- **`finesse-ui`（UI 域路由入口）**：按 register 路由到 `zine-ui` / `diagram-design`，共享 craft floor + anti-cheap 黑名单 + a11y 门。
- **`writing`（域内薄路由）**：核对产物文件判阶段 → 路由 `writing-fragments`（explore）与 `writing-shape` / `writing-beats`（二选一的 exploit），成文后 `writing-humanizer` 润色。
- **原语 → 包装**：`grilling`（原语）→ `grill-me` / `grill-with-docs`；`code-review` / `wayfinder` / `research` 内部以子智能体分派。

## 来源与许可

- 本仓库根 `LICENSE` 为 **MIT**（Copyright 2026 Penumbra-Noviter），覆盖自研/深度改写内容。
- 各 vendored / distilled skill 保留各自上游许可，**重新分发前请逐条核对** `PROVENANCE.md`：
  - `cangjie-skill` — AGPL v3
  - `zine-ui` — personal non-commercial（商业使用需作者书面许可）
  - `diagram-design` / `simplify-codebase` / `vibehub` / `writing-humanizer` — MIT 等（见各自 LICENSE）
  - mattpocock 批次 ~46 个 — 见上游 https://github.com/mattpocock/skills
- `PROVENANCE.md` 是全库来源登记（vendored / distilled / 自研 / 封装判定、上游 URL、本地改动点、同步流程），更新 skill 前先查它。

## 维护约定

- 新增/改版 skill 后同步 `PROVENANCE.md`（来源登记）与 `ask-matt`（路由）。
- 全库功能图谱（反向检索表）与生态分工记录位于 zcode 工作区，仓库内不重复维护。