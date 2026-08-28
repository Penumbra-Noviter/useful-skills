# PROVENANCE — Skill 库来源登记

本文件记录 skill 库中每个 skill 的上游来源、本地版本与本地改动，是**更新 skill 库时的事实依据**。同步上游前先查本文件对应条目；同步后更新本文件的「同步日期 / 上游版本 / 改动摘要」。

判定口径：**vendored** = 直接复制上游文件；**distilled** = 蒸馏/改写，非逐字复制；**自研** = 无上游，本地原创；**封装** = 本地写的外壳 + 调用第三方工具。

---

## 总览

| Skill | 类型 | 上游 | License | 本地版本 | 导入 | 可追踪更新 |
|---|---|---|---|---|---|---|
| mattpocock 批次 ~46 个 skill | vendored | [mattpocock/skills](https://github.com/mattpocock/skills)（**用户 2026-08-13 确认**） | 见上游 | 无版本号 | 2026-08-06 | ✅ |
| skill-creator | vendored | mattpocock/skills（随批次导入；Apache 2.0 LICENSE.txt 系上游随附） | Apache 2.0 | — | 2026-08-06 | ✅（并入批次） |
| vibehub | vendored | [oil-oil/vibe-hub-skill](https://github.com/oil-oil/vibe-hub-skill) | MIT | — | 2026-08-11 | ✅（config.json 已记） |
| zine-ui | distilled | [Zeejay0/gathered-scenes-zine-skill](https://github.com/Zeejay0/gathered-scenes-zine-skill) + photo-abstract-editorial（Codex） | personal non-commercial | 1.0.0 | 2026-08-11 | ✅ |
| diagram-design | vendored + 修复 | [cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design) | MIT | 2.2（上游已 2.3） | 2026-08-13（未 commit） | ✅ **上游有新版本** |
| museon-cli | 封装 | [Museon-AI/museon-cli](https://github.com/Museon-AI/museon-cli) | — | — | 2026-08-11 | ✅（wheel URL） |
| vision | vendored + 改造 | [asuojun/claude-vision-skill](https://github.com/asuojun/claude-vision-skill) | — | — | 2026-08-06 | ✅（README 已记） |
| finesse-ui | 自研 + 部分派生 | 派生自 taste-skill v2 / emilkowalski/skills / VoltAgent/awesome-design-md | MIT | 0.21.0 | 快照 2026-08-28 · v0.21.0，**非 mattpocock 内容** | 部分（仅派生源） |
| open-kimi-ppt | 自研（逆向） | 无（依赖 Moonshot PPTD 格式） | 无 | — | 2026-08-08 | ❌ |
| neat-freak | vendored + 本地化 | [KKKKhazix/khazix-skills](https://github.com/KKKKhazix/khazix-skills)（neat-freak/，用户 2026-08-13 确认） | — | 3.0.0（上游同版） | 2026-08-11 | ✅ |
| context-monitor | 自研（推断） | 无 | 无 | — | 2026-08-06 | ❌ |
| project-kickoff | 自研 | 无（符号链接 → `.cc-switch/skills/project-kickoff/`） | 无 | 有 REVISIONS.md | 独立维护 | ❌ |

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

### 2. skill-creator — vendored

- **上游**：mattpocock/skills（用户 2026-08-13 确认整批来源；上游当前 main 已无此目录，属导入后上游删除）
- **License**：仓库内自带 `LICENSE.txt`（Apache 2.0）——Apache 2.0 是 anthropics/skills 的特征、mattpocock 系内少见；若重发布此 skill 请按 Apache 2.0 条款处理并保留版权声明
- **导入**：随 mattpocock 批次 `77430e9`

### 3. vibehub — vendored（来源记录最规范）

- **上游**：https://github.com/oil-oil/vibe-hub-skill（skills/vibehub 路径）
- **License**：MIT，Copyright (c) 2026 oil-oil
- **记录**：`vibehub/LICENSE` 末尾 + `vibehub/vibehub.config.json`（schemaVersion 1，siteUrl/repositoryUrl/skillPath 齐全）
- **导入**：`fdc181e`（2026-08-11）

### 4. zine-ui — distilled

- **上游 1**：https://github.com/Zeejay0/gathered-scenes-zine-skill（拾景纸刊）— personal, non-commercial use only，商业使用需作者书面许可；共享输出需保留署名 "Visual language: 拾景纸刊 by @Zeejay0"
- **上游 2**：photo-abstract-editorial（Codex skill，2026-08-09 下载）— 无 license，作参考材料
- **License**：personal non-commercial，**不覆盖于 finesse-ui 的 MIT 条款**
- **导入**：`fdc181e`（2026-08-11）
- **本地改动**：蒸馏为三路径（实景拼贴/影像蒸馏/抽象记忆面板），继承 finesse-ui craft floor

### 5. diagram-design — vendored + 上游缺陷修复

- **上游**：https://github.com/cathrynlavery/diagram-design（作者 Cathryn Lavery，littlemight.com，MIT）
- **本地版本**：2.2；**上游最新 2.3（2026-08 已发布）——待同步检查**
- **导入**：2026-08-13（用户交付 `D:\Desktop\downloads\diagram-design-main`），**未 commit**
- **本地修复的 4 个上游缺陷**（同步时勿被上游覆盖）：
  1. style-guide gate 检测旧皮肤 token（rust #b5523a）→ 统一为 style-guide.md 实际值（atomic-tangerine #eb6c36）
  2. style-guide.md Inversion rule 遗留旧皮肤色 rgba(28,25,23) → 当前 ink rgba(45,49,66)
  3. 4 个 type 参考文档承诺的 11 个 `*-extended` 示例文件在上游 main 也不存在 → 改为 "not shipped as a file" 描述
  4. reference 文件为 CRLF 行尾，grep 校验需 `tr -d '\r'`
- **frontmatter 改造**：本地加了 when_to_use/user-invocable/argument-hint，description 双语触发词，version 展平为 2.2

### 6. museon-cli — 封装

- **上游**：https://github.com/Museon-AI/museon-cli（SKILL.md 安装命令里的 wheel URL 即上游发布物）
- **本地角色**：安装 + 操作指南外壳，非复制上游代码
- **导入**：`fdc181e`（2026-08-11）

### 7. vision — vendored + 改造

- **上游**：https://github.com/asuojun/claude-vision-skill（README.md 内记录 clone 地址）
- **本地改动**：`9b36024`（2026-08-11）精简脚本与 SKILL 文档
- **导入**：`77430e9`（2026-08-06）

### 8. finesse-ui — 自研 + 部分派生

> **⚠️ 保护条款（2026-08-13 用户确认）**：finesse-ui 经用户编写 + 蒸馏其它仓库后，**已与任何原生 skill 不一致**。SKILL.md 主体、references 大部分、examples、design-md、scripts 均为用户原创/深度改写。**任何同步/更新操作只允许人工定点合入受影响的具体段落，禁止整文件、整目录覆盖或批量替换。** 更新后必须人工复核保护条款涉及的改动未丢失。

- **来源声明**：无统一 origin 段，派生来源分散于 references：
  - `references/dials.md:3` — layout/motion/density anchors 派生自 taste-skill v2 §7（github.com/Leonxlnx/taste-skill，MIT）
  - `references/page-skeleton.md:18` — Hero hard rules 蒸馏自 taste-skill v2 §4.7（Leonxlnx，MIT）
  - `references/motion.md:359` — 决策框架/数值表/配方蒸馏自 emilkowalski/skills（github.com/emilkowalski/skills，React→vanilla JS 翻译）
  - `design-md/README.md:9` — design-md 语料来源 VoltAgent/awesome-design-md（github.com/VoltAgent/awesome-design-md）
- **License**：MIT（frontmatter）；仓库根 LICENSE 为 Penumbra-Noviter 本人
- **本地版本**：0.20.0（演进自导入时的初版）
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
- **更新提示**：正文为中文改写版，同步上游时人工合入；若上游更新 references，优先把缺失的 4 个 reference 文件补齐而非只更新 SKILL.md

### 11. context-monitor — 自研（推断）

- 77430e9 导入时即存在；中文内容、无 LICENSE、无来源标记 → 判为自研。若实际来自某处请补记

### 12. project-kickoff — 自研（独立位置）

- **物理位置**：符号链接 → `/c/Users/Administrator/.cc-switch/skills/project-kickoff/`（独立目录，自带 REVISIONS.md / TO-TICKETS.md）
- **同步**：在真实位置维护，本仓库仅指针

---

## 同步更新流程（按此执行）

1. **查本文件**对应条目 → 拿到上游 URL、本地版本、本地改动点
2. **确认上游最新版本**（git clone / gh api / 上游 README）
3. **对账 diff**：`git diff <本仓库导入commit> <上游文件>`，逐项评估
4. **保留本地改动点**（每条目已列；diagram-design 的 4 个修复、finesse-ui 的 references 尤其注意）。**自研/深度改写类条目（finesse-ui、open-kimi-ppt、neat-freak、context-monitor）默认只允许人工挑选合入，禁止任何形式的覆盖**
5. **同步后更新本文件**：同步日期、上游版本、改动摘要
6. 若同步牵涉 license 变化 → 同步更新对应 LICENSE 与 frontmatter

## 已知缺口（待补）

- [ ] mattpocock 批次中「本地有、上游当前 main 无」的 12 个目录（batch-grill-me 等），删除/迁移时间未用上游 git 历史核实——同步时若上游恢复目录则正常对账，若确认已删则决定本地去留
- [ ] skill-creator 的 Apache 2.0 LICENSE.txt 与 mattpocock 批次其余 skill 不协调（疑源自 anthropics/skills），重发布时需注意条款差异
- [ ] diagram-design 上游 2.3 变更内容未评估
- [ ] context-monitor 的来源判定为推断，若实际有上游请补记
