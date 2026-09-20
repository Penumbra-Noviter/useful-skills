# PROVENANCE — Skill 库来源登记

本文件记录 skill 库中每个 skill 的上游来源、本地版本与本地改动，是**更新 skill 库时的事实依据**。同步上游前先查本文件对应条目；同步后更新本文件的「同步日期 / 上游版本 / 改动摘要」。

判定口径：**vendored** = 直接复制上游文件；**distilled** = 蒸馏/改写，非逐字复制；**自研** = 无上游，本地原创；**封装** = 本地写的外壳 + 调用第三方工具。

---

## 总览

| Skill | 类型 | 上游 | License | 本地版本 | 导入 | 可追踪更新 |
|---|---|---|---|---|---|---|
| cangjie-skill | vendored（官方 Release 包） | [kangarooking/cangjie-skill](https://github.com/kangarooking/cangjie-skill) | MIT（v2.5.0 起） | 2.5.0 | 2026-08-27 → 2026-09-16 更新 | ✅ |
| mattpocock 批次 ~46 个 skill | vendored | [mattpocock/skills](https://github.com/mattpocock/skills)（**用户 2026-08-13 确认**） | 见上游 | 无版本号 | 2026-08-06 | ✅ |
| skill-creator | vendored | mattpocock/skills（随批次导入；Apache 2.0 LICENSE.txt 系上游随附） | Apache 2.0 | — | 2026-08-06 | ✅（并入批次） |
| vibehub | vendored | [oil-oil/vibe-hub-skill](https://github.com/oil-oil/vibe-hub-skill) | MIT | — | 2026-08-11 | ✅（config.json 已记） |
| zine-ui | distilled | [Zeejay0/gathered-scenes-zine-skill](https://github.com/Zeejay0/gathered-scenes-zine-skill) + photo-abstract-editorial（Codex） | personal non-commercial | 1.0.0 | 2026-08-11 | ✅ |
| diagram-design | vendored + 修复 | [cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design) | MIT | 2.6.27 | 2026-08-13（未 commit） | ✅ |
| museon-cli | 封装 | [Museon-AI/museon-cli](https://github.com/Museon-AI/museon-cli) | — | wheel v0.6.0 | 2026-08-11 | ✅（wheel URL） |
| vision | vendored + 改造 | [asuojun/claude-vision-skill](https://github.com/asuojun/claude-vision-skill) | — | — | 2026-08-06 | ✅（README 已记） |
| finesse-ui | 自研 + 部分派生 | 派生自 taste-skill v2 / emilkowalski/skills / VoltAgent/awesome-design-md | MIT | 0.21.0 | 快照 2026-08-28 · v0.21.0，**非 mattpocock 内容** | 部分（仅派生源） |
| open-kimi-ppt | 自研（逆向） | 无（依赖 Moonshot PPTD 格式） | 无 | — | 2026-08-08 | ❌ |
| neat-freak | vendored + 本地化 | [KKKKhazix/khazix-skills](https://github.com/KKKKhazix/khazix-skills)（neat-freak/，用户 2026-08-13 确认） | — | 3.0.0（上游同版） | 2026-08-11 | ✅ |
| context-monitor | 自研（推断） | 无 | 无 | — | 2026-08-06 | ❌ |
| project-kickoff | 自研 | 无（符号链接 → `.cc-switch/skills/project-kickoff/`） | 无 | 有 REVISIONS.md | 独立维护 | ❌ |
| simplify-codebase | vendored + 适配 | [tt-a1i/simplify-codebase](https://github.com/tt-a1i/simplify-codebase) | MIT | — | 2026-08-29 | ✅ |
| agent-reach | vendored（skill 文档层） | [Panniantong/Agent-Reach](https://github.com/Panniantong/Agent-Reach) | MIT（上游） | 15 平台（上游已 16） | 2026-08-26（未登记，本次补） | ✅（上游有更新未合入） |
| reverse-skill（选择性吸收） | vendored(3 refs) + distilled(1) | [zhaoxuya520/reverse-skill](https://github.com/zhaoxuya520/reverse-skill) | MIT（主体；CTF 子包 GPLv3 未吸收） | v1.0.1 | 2026-09-01 | ✅ |
| writing-humanizer | distilled | [op7418/Humanizer-zh](https://github.com/op7418/Humanizer-zh)（← blader/humanizer + stop-slop + 维基百科 Signs of AI writing） | MIT | — | 2026-09-01 | ✅ |
| code-review（本地蒸馏补强） | distilled（补 2 机制） | [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code)（agents/code-reviewer + silent-failure-hunter） | MIT | — | 2026-09-01 | ✅ |
| simple-logic | distilled（cangjie-tools v2.5.0 生成） | 《简单的逻辑学》(D. Q. McInerny) 经 [kangarooking/cangjie-skill](https://github.com/kangarooking/cangjie-skill) 蒸馏 | 原书文本衍生 | v2.5.0（生成器） | 2026-09-16 | — |

---

## 逐条详情

### 1. mattpocock 批次（~46 个 skill）— vendored

- **上游**：https://github.com/mattpocock/skills（"Skills for Real Engineers"，main 分支，无 tag 版本）
- **导入**：`77430e9 feat: 添加全部 skills 集合`（2026-08-06）+ `6af0bfd sync: 同步 mattpocock/skills 最新版本`（2026-08-06）
- **涉及目录**（77430e9 快照，含后来移除/改名者）：ask-matt, batch-grill-me, claude-handoff, code-review, codebase-design, context-monitor, design-an-interface, diagnosing-bugs, domain-modeling, edit-article, find-skills, finesse-ui, git-guardrails-claude-code, grill-me, grill-with-docs, grilling, handoff, implement, improve-codebase-architecture, improve-python-architecture, loop-me, migrate-to-shoehorn, neat(已移除), obsidian-vault, prototype, qa, request-refactor-plan, research, resolving-merge-conflicts, scaffold-exercises, setup-matt-pocock-skills, setup-pre-commit, setup-ts-deep-modules, skill-creator, tdd, teach, to-questionnaire, to-spec, to-tickets, triage, ubiquitous-language, vision, wayfinder, wizard, writing-beats, writing-fragments, writing-great-skills, writing-shape, wait-what
- **确认**：2026-08-13 用户确认整批（77430e9 导入的全部目录）均来自 https://github.com/mattpocock/skills
- **上游当前（main）目录结构**：`skills/` 下分 engineering / productivity / misc / in-progress / deprecated 五类；**deprecated 为空**，说明上游清理过一轮
- **本地有、上游当前 main 已无的目录**（导入时或上游历史中存在；同步时需区分「上游删除」vs「本地自研/另源」）：
  - 推断上游曾存在后被删：batch-grill-me、design-an-interface、edit-article、find-skills、improve-python-architecture、obsidian-vault、qa、request-refactor-plan、ubiquitous-language、skill-creator、writing-great-skills（旧 `neat/` 目录另属 khazix-skills 来源，见 §10，非 mattpocock 内容）
  - 本地自研/另源（与 mattpocock 无关，保留各自条目）：finesse-ui（§8）、context-monitor（§11）、vision（§7，来源 asuojun）
  - 注：以上「被删」基于当前 main 快照推断，删除时间可用上游 git 历史核实
- **本地是否改过内容**：未逐一记录，同步时用 `git diff <导入commit> <上游最新>` 对账
- **同步方式**：clone 上游 → 逐目录 diff → 合并上游改动（保留本地非官方条目）。
- **最近同步（2026-08-29）**：
  - 上游 head：`6654f6b`（2026-08-24，"feat: add 'Information access' category to retrospective skill"）；CHANGELOG 最新 1.2.3；github.com 直连被墙，经 gh-proxy.com 克隆
  - 34 个共有 skill 全部与上游对齐：30 个无本地改动者批量复制；4 个有本地改动者人工合并（code-review 保 Falsify 轴 + Reviewer posture、grilling 保钢人模式、implement 保交付标准/四状态报告、to-tickets 保切片规模上限）
  - **code-review 另有本地蒸馏补强（2026-09-01，§16）**：新增 Report credibility gate 小节 + Falsify 轴静默失败专项 + Step 4 子智能体 brief 约束——上游同步时保留，勿被上游覆盖（详见 §16）
  - 本地独有文件保留未动：research/findings-agent-ticket-sizing.md
  - 本地已删除者未恢复：writing-for-agents（上游仍有，本地有意删）、writing-great-skills、skill-creator（上游均已删）
  - **2026-08-29 用户决定**：删除 batch-grill-me、design-an-interface、edit-article、find-skills、qa、request-refactor-plan、ubiquitous-language（7 个，未 commit，git 可恢复）；保留 improve-python-architecture、obsidian-vault；上游新增的 implement-spec、retro **用户决定暂不引入**（依赖本地已删的 writing-for-agents / 任务图体系，尚属 in-progress）
- **2026-09-16 核对**：上游 head `959a8e9`（2026-09-15）。自上次同步点 `6654f6b` 后上游仅两处变动：retro deterministic-checks（本地未引入，维持原决定）、link-skills misc 收录逻辑（本地无此 skill）。**34 个共有 skill 无内容变更，无需重新同步。**

### 2. skill-creator — vendored

- **上游**：mattpocock/skills（用户 2026-08-13 确认整批来源；上游当前 main 已无此目录，属导入后上游删除）
- **License**：仓库内自带 `LICENSE.txt`（Apache 2.0）——Apache 2.0 是 anthropics/skills 的特征、mattpocock 系内少见；若重发布此 skill 请按 Apache 2.0 条款处理并保留版权声明
- **导入**：随 mattpocock 批次 `77430e9`

### 3. vibehub — vendored（来源记录最规范）

- **上游**：https://github.com/oil-oil/vibe-hub-skill（skills/vibehub 路径）
- **License**：MIT，Copyright (c) 2026 oil-oil
- **记录**：`vibehub/LICENSE` 末尾 + `vibehub/vibehub.config.json`（schemaVersion 1，siteUrl/repositoryUrl/skillPath 齐全）
- **导入**：`fdc181e`（2026-08-11）
- **2026-09-16 核对**：上游 head `8d77154`（2026-09-10，「明确 Skill 功能、首次使用与执行边界」）。逐文件 diff 后确认**本地版 = 上游当前内容 + 本地「## 边界」小节（finesse 分工）+ 本地 LICENSE**，本地已是超集，无需合入。

### 4. zine-ui — distilled

- **上游 1**：https://github.com/Zeejay0/gathered-scenes-zine-skill（拾景纸刊）— personal, non-commercial use only，商业使用需作者书面许可；共享输出需保留署名 "Visual language: 拾景纸刊 by @Zeejay0"
- **上游 2**：photo-abstract-editorial（Codex skill，2026-08-09 下载）— 无 license，作参考材料
- **License**：personal non-commercial，**不覆盖于 finesse-ui 的 MIT 条款**
- **导入**：`fdc181e`（2026-08-11）
- **本地改动**：蒸馏为三路径（实景拼贴/影像蒸馏/抽象记忆面板），继承 finesse-ui craft floor
- **2026-09-16 核对**：上游 head `b9edb83`（2026-09-03，「Consolidate Live edition files into one skill folder」结构重组）。本地为 distilled 深度改写，不整目录跟随；核对内容语义未变，暂不更新。

### 5. diagram-design — vendored + 上游缺陷修复

- **上游**：https://github.com/cathrynlavery/diagram-design（作者 Cathryn Lavery，littlemight.com，MIT）
- **本地版本**：**2.6.27（2026-09-16 同步上游 main @`9874ad7`，plugin manifest 2.6.27）**；同步前为 2.2（27 型精简版）
- **导入**：2026-08-13（用户交付 `D:\Desktop\downloads\diagram-design-main`），**未 commit**
- **2026-09-16 同步内容**：
  - 上游 2.2 → 2.6.x 为 **40 型完整版**：新增 semantic-patterns 行为路由、animation 动画层、Excalidraw 导入、Non-Latin（韩/繁中/西里尔）标签指南、profiles/doctor/export-registry 等通用 reference、13 个扩展型（polar/waterfall/treemap/sankey/fishbone/wardley/kanban/journey/deployment/dependency/uml-class/story-map/db-schema）及其 example HTML
  - 本地 86 个上游新增文件拷贝（新 type references/assets/脚本）；17 个共有 references 取上游新版；4 个脚本（drawio/mermaid/excalidraw_extract.py、self_check.py）取上游新版并清 pycache
  - SKILL.md 以上游正文为基底，**重放本地定制层**：frontmatter 40 型双语触发词（when_to_use/user-invocable/argument-hint/version 2.6.27/license MIT）、finesse 继承段（Inherited constraints）、Origin & license 段、本地 onboarding gate 5 分支话术
  - assets 同名文件（example-*.html、template*.html、index.html）**保留本地版未覆盖**（内容级微调无法判归属，防误删本地成果）
- **本地修复的 4 个上游缺陷**（同步时勿被上游覆盖）：
  1. style-guide gate 检测旧皮肤 token（rust #b5523a）→ 统一为 style-guide.md 实际值（atomic-tangerine #eb6c36）——**上游新版 SKILL 的 gate 已采用 #eb6c36 值，本修复并入本地 gate 段**
  2. style-guide.md Inversion rule 遗留旧皮肤色 rgba(28,25,23) → 当前 ink rgba(45,49,66)——**上游 2.6.27 仍未修，本次同步后已重新应用**
  3. 4 个 type 参考文档承诺的 11 个 `*-extended` 示例文件在上游 main 也不存在 → **上游新版已改为文档内置完整示例（如 type-process.md §12），从根上解决，无需再改**
  4. reference 文件为 CRLF 行尾，grep 校验需 `tr -d '\r'`
- **frontmatter 改造**：本地加了 when_to_use/user-invocable/argument-hint，description 双语触发词，version 展平（现 2.6.27）
- **更新提示**：assets 同名文件为本地保留版，下次同步前先 diff 判定归属；style-guide Inversion 修复与 gate 段为本地保护点

### 6. museon-cli — 封装

- **上游**：https://github.com/Museon-AI/museon-cli（SKILL.md 安装命令里的 wheel URL 即上游发布物）
- **本地角色**：安装 + 操作指南外壳，非复制上游代码
- **导入**：`fdc181e`（2026-08-11）
- **2026-09-16 更新**：wheel pin v0.5.9 → **v0.6.0**（上游 2026-09-12 release，asset `museoncli-0.6.0-py3-none-any.whl`）

### 7. vision — vendored + 改造

- **上游**：https://github.com/asuojun/claude-vision-skill（README.md 内记录 clone 地址）
- **本地改动**：`9b36024`（2026-08-11）精简脚本与 SKILL 文档
- **导入**：`77430e9`（2026-08-06）
- **2026-09-16 核对**：上游 head `fa5ca17`（2026-08-11，PR #9 剪贴板读取）——本地改造版无该能力，评估后**暂不合入**（本地已有截屏/文件路径通道，剪贴板路径收益低）

### 8. finesse-ui — 自研 + 部分派生

> **⚠️ 保护条款（2026-08-13 用户确认）**：finesse-ui 经用户编写 + 蒸馏其它仓库后，**已与任何原生 skill 不一致**。SKILL.md 主体、references 大部分、examples、design-md、scripts 均为用户原创/深度改写。**任何同步/更新操作只允许人工定点合入受影响的具体段落，禁止整文件、整目录覆盖或批量替换。** 更新后必须人工复核保护条款涉及的改动未丢失。

- **来源声明**：无统一 origin 段，派生来源分散于 references：
  - `references/dials.md:3` — layout/motion/density anchors 派生自 taste-skill v2 §7（github.com/Leonxlnx/taste-skill，MIT）
  - `references/page-skeleton.md:18` — Hero hard rules 蒸馏自 taste-skill v2 §4.7（Leonxlnx，MIT）
  - `references/motion.md:359` — 决策框架/数值表/配方蒸馏自 emilkowalski/skills（github.com/emilkowalski/skills，React→vanilla JS 翻译）
  - `design-md/README.md:9` — design-md 语料来源 VoltAgent/awesome-design-md（github.com/VoltAgent/awesome-design-md）
- **License**：MIT（frontmatter）；仓库根 LICENSE 为 Penumbra-Noviter 本人
- **本地版本**：0.21.0（演进自导入时的初版；快照 2026-08-28）
- **更新提示**：taste-skill 只影响两个 reference 文件（dials.md、page-skeleton.md），其余为本地演化；上游更新时**不要整文件覆盖**

### 9. open-kimi-ppt — 自研（逆向）

- **无上游 repo**：`756d46d`（2026-08-08）"逆向 Kimi 制作 PPT 的能力"
- **依赖**：Moonshot AI 的 PPTD 格式 + neo-ppt 浏览器编辑器（`editor/neo-ppt/` 为离线镜像）；官方 PPTX 导出 WASM 本地打补丁（`scripts/local-export/export-pptd.mjs --no-sign`）
- **License**：无

### 10. neat-freak — vendored + 本地化（来源已确认）

- **上游**：https://github.com/KKKKhazix/khazix-skills（路径 `neat-freak/`），**用户 2026-08-13 确认**
- **上游结构**：SKILL.md（v3.0.0）+ `evals/` + `references/`（agent-paths / governance / sync-matrix / verification）+ `scripts/`（audit-inventory.sh）
- **本地结构**：SKILL.md + **references/（agent-paths / governance / sync-matrix / verification）+ scripts/audit-inventory.sh（2026-08-13 从上游补齐）**；版本与上游一致（3.0.0）。evals/ 未带入（正文不引用，保持轻量）
- **本地改动**：
  - description 由 `>-` 块式压缩为单行式
  - 新增 `when_to_use` frontmatter（上游无）
  - 2026-08-13 补齐缺失的 4 个 reference + audit-inventory.sh，正文 6 处引用已验证闭合（注意：SKILL.md 为 CRLF 行尾，校验引用需 `tr -d '\r'`）
- **导入**：`fdc181e`（2026-08-11，移除旧 `neat/` 目录并改名）。旧 `neat/` 目录（77430e9 导入时 name 已是 neat-freak）推断同为 khazix-skills 来源的早期引入
- **2026-09-16 核对**：上游 `neat-freak/` 路径自 2026-08-13 后**零提交**（上游 9-16 的 aihot v1.7.1 更新是另一 skill），无需更新
- **更新提示**：正文为中文改写版，同步上游时人工合入；若上游更新 references，优先把缺失的 4 个 reference 文件补齐而非只更新 SKILL.md

### 11. context-monitor — 自研（推断）

- 77430e9 导入时即存在；中文内容、无 LICENSE、无来源标记 → 判为自研。若实际来自某处请补记

### 12. project-kickoff — 自研（独立位置）

- **物理位置**：符号链接 → `/c/Users/Administrator/.cc-switch/skills/project-kickoff/`（独立目录，自带 REVISIONS.md / TO-TICKETS.md）
- **同步**：在真实位置维护，本仓库仅指针

### 13. simplify-codebase — vendored + 适配（dao-skill 评估后入库）

- **上游**：https://github.com/tt-a1i/simplify-codebase（"先证明，再删除"的代码简化审计/执行器；Survey 只读 / Change 授权修改 × Focused / Broad；9 字段证明记录制；5 个 references + docs/validation.md + agents/openai.yaml + 双语 README）
- **License**：MIT（© 2026 simplify-codebase contributors）
- **导入**：2026-08-29；来源 `D:\Desktop\downloads\skill respority\simplify-codebase-main\simplify-codebase-main\`（下载物为双层目录，有效根在内层）
- **dao-skill 评估**：E1 结构级 78/100，Trust Gate PASS；P0 无；仅做最小适配（见下）
- **本地改动**（同步上游时保留以下三处即可）：
  1. description 中文触发词扩展（原版仅"代码简化/熵回收"→ 补 简化代码 / 删除死代码 / 清理冗余 / 减少复杂度 / 冗余审计 / 墓碑代码 / 交付前清理 / 临时代码清理）
  2. description 尾部加路由边界：模块加深→improve-codebase-architecture，变更评审→code-review
  3. 5 处 reference 链接文本改为完整路径反引号标记 `` `references/x.md` ``（dao-skill 检索约定）
  4. 证明记录 9 字段精简为 7 字段（去 Finding ID/Locus/Topology，留 Candidate/Burden/Reachability/Rationale/Cut/Consequence/Confidence/Proof/Net effect 中与本地工作流契合的 7 个）；新增墓碑代码段落（`references/tombstone-code.md`，本地独有）
- **放置决策**：独立 skill（不路由进 ask-matt / improve-codebase-architecture 等），model-invoked 触发，接线方式与库内 diagram-design 同构
- **2026-09-16 同步**：上游 9-04 新增「可视化 companion」能力——合入 `references/visual-reporting.md`、`visualization/`（29 文件：render-cleanup-map.mjs + archify-core 渲染器 + schema + examples + tests）、`docs/visual-report-example.md`；SKILL.md 并入 visual companion 段落（保留本地 7 字段体系，不引入冲突的 Finding ID 条款）。`.github/workflows`（CI）与 `PRODUCT.md`（产品说明）不引入
- **更新提示**：上游更新时逐文件对账；SKILL.md 需保留上述本地改动，其余文件可整体覆盖

### 14. reverse-skill（选择性吸收）— vendored + distilled

- **上游**：https://github.com/zhaoxuya520/reverse-skill（v1.0.1，2026-08-08 release）
- **License**：主体 MIT（Copyright (c) 2026 zhaoxuya520）；`CTF-Sandbox-Orchestrator/` 为 GPLv3 —— **GPL 子包未吸收**
- **导入**：2026-09-01，来源 `D:\Desktop\downloads\skill respority\reverse-skill-main\`
- **吸收方式**：只取高价值 references，**未引入路由矩阵/脚本链/MCP 全家桶**（评估：48 skill 路由包对当前体系属过度设计）
- **吸收清单**（4 个文件，3 vendored + 1 distilled）：
  1. `reverse-flow/references/frida-cookbook.md`（472 行，vendored；文件头有来源标注）
  2. `reverse-flow/references/ollvm-deobfuscation.md`（501 行，vendored；文件头有来源标注）
  3. `reverse-flow/references/apk-security-checklist.md`（230 行，vendored；文件头有来源标注）
  4. `fetchflow/references/network-profile.md`（distilled：吸收 scope-contract 四档网络画像+离线样本合法化概念，fetchflow 术语改写，非逐字复制）
- **本地接线**：
  - reverse-flow/SKILL.md「Bundled resources」新增 3 行引用
  - fetchflow/SKILL.md「Resource Guide」+「Workflow Step 0」+「Output Protocol」补 network-profile 引用与字段
- **验证**：全部 .py 语法 OK；`check_target.py` 冒烟通过（本地路径 → ALLOW）
- **2026-09-16 核对**：上游 head `7e2097f`（2026-09-03，docs-only 安全集成记录），与吸收的 4 个文件无交集，无需更新
- **更新提示**：上游更新时只对账上述 4 个吸收文件；SKILL.md 侧改动为本地接线，勿被上游覆盖

### 15. writing-humanizer — distilled（dao-skill 模式 F 自化吸收）

- **上游**：https://github.com/op7418/Humanizer-zh（"去中文 AI 味" skill；核心翻译自 blader/humanizer，实用部分参考 hardikpandya/stop-slop，知识基底为维基百科 [Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)）
- **License**：MIT，Copyright (c) 2026 歸藏
- **导入**：2026-09-01，经 gh-proxy.com 克隆验证后蒸馏（github.com 直连被墙）
- **吸收方式**：distilled 而非 vendored —— 保留 24 种 AI 写作模式的完整目录（词汇表/问题/改写示例 = 可移植机制）与五核心规则、质量评分表；改写为 writing 家族子 skill 格式（`disable-model-invocation: true` + `<what-to-do>/<supporting-info>`），新增与三件套的分工边界与触发词
- **本地接线**：
  - 新增 `writing-humanizer/SKILL.md`（唯一文件）
  - `writing/SKILL.md`：Step 4 新增"成文后润色（去 AI 味）"路由 → writing-humanizer；description 补去 AI 味触发词；通过标准/边界同步更新
- **放置决策**：并入 writing 家族作润色 pass（不是第四写作阶段，不路由进 ask-matt）
- **验证**：dao-skill `quality_check.py` 结构检查通过（E1）；行为抽查含 5 核心规则 + 24 模式 + 质量评分自检
- **2026-09-16 核对**：上游仅 README 安装方式更新（npx 一键安装），与本地 distilled 内容无关，无需更新
- **更新提示**：上游更新时对账 24 模式清单与示例即可；writing-humanizer 为本地改写版，SKILL.md 勿整文件覆盖

### 16. code-review（本地蒸馏补强）— distilled（dao-skill 模式 F 自化吸收）

- **上游**：https://github.com/affaan-m/everything-claude-code（ECC，140K+ stars；取 `agents/code-reviewer.md` 与 `agents/silent-failure-hunter.md` 两处机制）
- **License**：上游 MIT
- **导入**：2026-09-01；本地路径 `D:\Desktop\downloads\skill respority\ECC-main\ECC-main\`
- **吸收方式**：distilled，只取 2 个高杠杆机制，不引入 ECC 整体体系（68 agents / 数百 skills 对 ZCode 单链属过度设计）：
  1. **Report credibility gate**（来自 code-reviewer）：置信度过滤（>80% 才报）+ Pre-Report Gate 四问（能否引具体行/能否说具体失败模式/是否读过上下文/严重级是否站得住）+ HIGH/CRITICAL 必须三件套证据 + 零发现合法 + 常见误报清单——直击 LLM 审查者编造发现/严重级通胀的失败模式
  2. **Silent-failure hunt**（来自 silent-failure-hunter）：Falsify 轴内新增静默失败专项——空 `catch {}`、错误折成 null/空数组、危险 fallback、丢失堆栈、泛化重抛、缺超时/回滚
- **本地接线**：`code-review/SKILL.md` 新增 `## Report credibility gate` 小节；Falsify 轴定义与 Step 4 子智能体 brief 同步补静默失败 + gate 约束；与既有 Falsify/Reviewer posture 本地改动合流
- **放置决策**：并入既有 code-review skill（同一 root/trigger，merge 优于 create），不新增独立 skill、不路由进 ask-matt
- **验证**：YAML frontmatter 解析通过（E1）；通读防矛盾；无独立 judge（E2 未做，dry-run 级）
- **2026-09-16 核对**：上游 ECC head `8321021`（2026-09-12，fix memory 目录遍历），与本地吸收的 code-reviewer/silent-failure-hunter 两处无交集，无需更新
- **更新提示**：上游同步时保留 §1 所列 code-review 既有本地改动 + 本 §16 新增内容，勿整文件覆盖；上游更新时只对账 code-reviewer/silent-failure-hunter 两处

### 17. agent-reach — vendored（skill 文档层，2026-09-16 补登记）

- **上游**：https://github.com/Panniantong/Agent-Reach（Python 包形态：`agent_reach/` + channels/backends/guides + `agent_reach/skill/` 为 skill 文档源）
- **License**：上游 MIT；本地 frontmatter `homepage` 已指向上游
- **导入**：2026-08-26（本地 SKILL.md 时间戳）；PROVENANCE 首次登记于 2026-09-16
- **本地形态**：skill 文档层（SKILL.md + 7 个 references：search/social/career/dev/web/video/finance），依赖用户独立安装上游 `agent-reach` CLI（pip/pipx）
- **本地改动**：SKILL.md 双语触发词 + 路由表 + 零配置命令 + check-update 提醒；references 为上游 docs 的精简适配
- **2026-09-16 核对**：上游 head `a19a171`（2026-09-15）新增 **Boss直聘 channel（#627）**，平台数 15→16，career 分类需更新（`channels/boss.py` + `references/career.md` 增补 + SKILL 平台数/路由）。**本次用户未选合入，待下轮执行**
- **更新提示**：合入时对账上游 `agent_reach/skill/` 的 SKILL.md 与 career.md，保留本地路由表/触发词结构

### 18. simple-logic — distilled（cangjie-tools v2.5.0 生成）

- **来源**：《简单的逻辑学》（D. Q. McInerny）全书经 [cangjie-skill](https://github.com/kangarooking/cangjie-skill)（v2.5.0）拆书蒸馏为 9 张能力卡 + 全书入口
- **导入**：2026-09-16（cangjie-tools v2.5.0 生成，committed 73f763e）
- **本地形态**：整书入口 SKILL.md + `references/`（overview / glossary / cheatsheet / capability-index）+ `references/capabilities/` 9 张能力卡（fallacy-detector、argument-evaluator、fact-confirmation、clear-communication、conditional-argument、quantifier-audit、define-terms、root-cause、attitude-check）
- **生成元数据**：`cangjie.bundle-id: bundle.simple-logic`、`cangjie.capability-count: 9`
- **定位**：AGENTS.md「对抗性自检」的执行层——Falsify/评审需要具名检查表时调用其能力卡（fallacy-detector / argument-evaluator / root-cause）；ask-matt 路由见其 Reasoning underneath 小节
- **上游同步**：再生成/模板升级用同一 cangjie-tools 版本，勿手工混改「生成元数据」区

---

## 同步更新流程（按此执行）

1. **查本文件**对应条目 → 拿到上游 URL、本地版本、本地改动点
2. **确认上游最新版本**（git clone / gh api / 上游 README）
3. **对账 diff**：`git diff <本仓库导入commit> <上游文件>`，逐项评估
4. **保留本地改动点**（每条目已列；diagram-design 的 4 个修复与 frontmatter/gate、finesse-ui 的 references 尤其注意）。**自研/深度改写类条目（finesse-ui、open-kimi-ppt、neat-freak、context-monitor）默认只允许人工挑选合入，禁止任何形式的覆盖**
5. **同步后更新本文件**：同步日期、上游版本、改动摘要
6. 若同步牵涉 license 变化 → 同步更新对应 LICENSE 与 frontmatter

## 已知缺口（待补）

- [x] mattpocock 批次中「本地有、上游当前 main 无」的目录——**2026-08-29 已核实**（上游 main 快照）：batch-grill-me、design-an-interface、edit-article、find-skills、improve-python-architecture、obsidian-vault、qa、request-refactor-plan、ubiquitous-language、skill-creator、writing-great-skills 均不在上游，属上游删除；本地去留见 §1「最近同步」
- [ ] skill-creator 的 Apache 2.0 LICENSE.txt 与 mattpocock 批次其余 skill 不协调（疑源自 anthropics/skills），重发布时需注意条款差异
- [x] diagram-design 上游 2.3+ 变更内容评估——**2026-09-16 已同步至 2.6.27（40 型）并重放本地定制**
- [x] context-monitor 的来源判定为推断——仍无上游线索，维持自研判定
- [ ] agent-reach 上游 Boss直聘 channel 合入（用户 2026-09-16 未选，挂起）
