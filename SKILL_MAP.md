# Skill 库功能图谱（67 个顶层 skill + 2 个 fetchflow 子模块 + 9 个插件条目）

> 条数与目录对得上：67 = 库根下每个 skill 目录一个 `SKILL.md`；`fetchflow-crawl` / `fetchflow-reverse` 是 `fetchflow/modules/*` 下的子模块 skill（也有独立 `name`，可被直接调用）；9 个插件条目由宿主插件提供、不在本仓库。
> 用途：按「要做的事 → 该用哪个 skill」反向检索。每个域一句话说清管什么，每条 skill 一句话说清何时用。
> 记忆线索：每个 skill 的用途里都含触发词（加粗部分），看到对应场景就能想起它。
> 库状态基线：2026-10-23（commit `c2db7a6`）。与 `README.md` 的 9 域划分、`ask-matt` 的路由表互为校验；三者漂移时以 `ask-matt` SKILL.md 为准。
> 文末「相对旧版的变更」列出本次对齐的增删改名，旧版（70 条，含已移除条目）不再维护。

---

## 域 0｜Skill 生态自治 —— 管"技能本身"的事

> 不知道用哪个 / 看上下文 / 补术语 / 造新 skill / 拆书蒸馏 / 逻辑检查。

| Skill | 一句话用途（含触发词） |
|---|---|
| **ask-matt** | **不知道该用哪个 skill** 时先问它，全库动态路由器（`disable-model-invocation`，手动 `/ask-matt`）；本 MAP 是静态速查图，与它互补 |
| **vibehub** | Vibe Coding 时把口语描述**翻译成准确术语**（"鼠标放上去有小提示" → tooltip / hover），任务照做、术语顺带补 |
| **dao-skill** | **设计/审计/优化/进化**一个 skill 的元设计器（道生万，Modes A–F：归根/设计/生成/评估/进化/吸收），找 skill 的根问题 |
| **skill-authoring** | **编写、结构化、打包** skill 与 agent 文档（SKILL.md / AGENTS.md / CLAUDE.md），含 frontmatter 与 agent 导向写作原则 |
| **cangjie-skill** | **拆书/蒸馏**书、长视频、播客、课程、访谈 → 一组可执行 skill（不做单纯摘要与书评） |
| **simple-logic** | 《简单的逻辑学》**9 张能力卡**（谬误识别/论证评定/事实确认/沟通清晰化/条件论证/量词审计/定义术语/根本原因/态度自检）；`code-review` 的 Falsify 轴与对抗性自检都拉它当具名检查表 |

---

## 域 1｜立项与规划 —— 把模糊想法变成可执行计划

> 立项先推导该有哪些面；想法还不清楚 → 先被访谈；想法清楚了 → 转 spec → 拆 tickets；大工程 → 先画地图；立项后 → 搭文档骨架装门禁。

| Skill | 一句话用途（含触发词） |
|---|---|
| **product-facets** | **立项时推导该有哪些正交「面」**（功能/UI/责任/安全/发布/运维/文档…），逐面设计/校验，反「功能能跑、其他面裸奔」，留自用→商用升级窗口 |
| **grilling** | **对计划/想法/决策做压力测试**的访谈原语，追问到你自相矛盾为止 |
| **grill-me** | **无状态访谈包装**：不在工作目录里（打磨计划/设计/一篇文字）时用，不留本地痕迹 |
| **grill-with-docs** | 同一套访谈，但**顺带产出 ADR 和术语表**；在工作目录里优先用它（有纸面痕迹） |
| **loop-me** | **关于工作流 spec** 的访谈，限定本工作区内、不出目录 |
| **to-questionnaire** | 一个**自己答不完的决策** → 转成给别人的问卷（卡点在别人脑子里时） |
| **to-spec** | **把对话合成 spec** 并发布到项目 issue tracker（不访谈） |
| **to-tickets** | **把计划/spec 拆成 tracer-bullet 工单**，每个工单声明阻塞边，发布到配置的 tracker |
| **wayfinder** | **超大工程（超过一次会话）**先画成决策 tickets 地图，逐票消解；地图清晰后**折回 to-spec**，不直接 implement |
| **project-kickoff** | **一句话工程目标** → 走完整个工程开发流水线（共识→spec→并行实现→评审→收尾）；仅用户显式点名 kickoff 时激活 |
| **doc-scaffold** | **给项目搭标准文档骨架**（AGENTS/PROJECT_REFERENCE/TO-TICKETS/DEV_LOG + DOCUMENTATION_STANDARDS + pre-commit 三道文档门禁） |

---

## 域 2｜编码实施 —— 真正写代码

> 有 spec 就实现；整份 spec 一次跑完就 implement-spec；要验证设计先做原型；测试先行；工程环境配置一次到位；出 PR 写正文。

| Skill | 一句话用途（含触发词） |
|---|---|
| **implement** | **按 spec/单张 tickets 实现**：TDD 垂直切片 + 类型检查 + 全量测试 + 自审 |
| **implement-spec** | **整份 spec 一次实现**：把工单读成**任务图**，按 ready frontier 并行派 implementer 子智能体，全部落在一个集成分支 |
| **pr** | **写 PR 正文**：最小可视摘要 + 前后证据 + 单向/双向门判定 |
| **tdd** | **测试驱动开发**：先写失败测试 → 再实现 → 重构（red-green-refactor） |
| **prototype** | **一次性原型**回答设计问题（LOGIC 逻辑 or UI 分支），答完即弃、答案折回正式代码 |
| **setup-pre-commit** | **配 Husky pre-commit**：提交前自动格式化（lint-staged/Prettier）+ 类型检查 + 跑测试 |
| **setup-ts-deep-modules** | **给 TS 仓库接线 dependency-cruiser**，让每个包成为深模块（实现藏在子目录，只经入口文件可达） |
| **setup-matt-pocock-skills** | 首次使用工程类 skill 前**初始化仓库**（issue tracker、triage 标签词汇表、文档布局） |
| **migrate-to-shoehorn** | 测试文件里**把 `as` 断言迁移到 @total-typescript/shoehorn** |
| **scaffold-exercises** | **生成练习目录结构**（章节/问题/解答/讲解），通过 lint |

---

## 域 3｜架构与质量 —— 让代码变好、别坏

> 设计模块 / 领域建模 / 扫描架构 / 简化 / 评审 / 修疑难 bug / 会话复盘 / 解决冲突 / 收尾清理 / 沉淀与查经验 / 威胁建模。

| Skill | 一句话用途（含触发词） |
|---|---|
| **codebase-design** | **深模块设计**：模块接口怎么切、seam 放哪、怎么让代码可测试可导航（`tdd` 与 `improve-codebase-architecture` 共用这套词汇） |
| **domain-modeling** | **构建/打磨领域模型**：挑战模糊术语、消解一词多义、写 CONTEXT.md 或 ADR |
| **improve-codebase-architecture** | **扫描代码库找深化机会** → 视觉 HTML 报告 → 选一个 grill 下去 |
| **improve-python-architecture** | 同上，但**针对 Python 代码库**（结构报告 → 选中的候选 grill） |
| **simplify-codebase** | **简化审计**：基于证据删死代码、去重、拆冗余抽象、回收熵（不做通用评审与性能调优） |
| **code-review** | **评审定点以来的改动**：Standards + Spec 并行两轴，Falsify（构造崩溃输入）按编排方请求作第三轴，Architecture（模块结构）在 kickoff 期末审核语境加入；支持单轴增量 |
| **diagnosing-bugs** | **疑难 bug / 性能回归**诊断闭环：必须先建「已对这条 bug 变红的反馈环」，再根因、修、加回归测试 |
| **retro** | **会话复盘**：回看这次编码会话，改的是 agent 的**环境**（导航指针/自动检查/编码标准/steering 文件），不是代码 |
| **resolving-merge-conflicts** | **解决进行中的 git merge/rebase 冲突**：按意图追到双方一手来源，逐 hunk 解，从不 `--abort` |
| **git-guardrails-claude-code** | **给 Claude Code 装 git 安全钩子**，拦 push / reset --hard / clean / branch -D 等危险命令 |
| **triage** | **把 issue/外部 PR 走状态机**：分类、验证、必要时 grill、写 agent-ready 简报（自己产出的工单不 triage） |
| **neat-freak** | **收尾整理**：文档/规则/记忆与代码事实对齐，审计工作区残留，产出待删清单待确认 |
| **distill-lesson** | **把本次经验教训蒸馏成原子笔记**写入 Obsidian 知识库（沉淀/复盘触发），知识闭环的写入半环 |
| **kb-search** | **查程序开发知识库里的既有经验**（报错/调试失败时、写测试前、重构前必查），只读检索、命中 ≤5 条，是知识闭环的读取半环 |
| **threat-model** | **写码前做 STRIDE 威胁建模**：认证/授权/外部输入/密钥/多租户/加解密场景触发，产出可验证的安全需求清单 |

---

## 域 4｜情报与调研 —— 从外部拿信息

> 全网搜 / 高信任一手来源 / 爬取+逆向 / 纯逆向 / 社媒运营。

| Skill | 一句话用途（含触发词） |
|---|---|
| **agent-reach** | **全网调研/搜索**任何话题；用户贴平台名或 URL（如小红书）时**必走入口** |
| **research** | **对高信任一手来源**做调研，交给后台 agent 读、产出带引用的仓库内 markdown |
| **fetchflow** | **采集 + 逆向编排**：按意图路由 crawl / reverse / chain 组合，Step 0 授权预检（ALLOW / CHECKPOINT / BLOCK） |
| **fetchflow-crawl** | fetchflow 的**采集子模块**：委托 crawl4ai 采集网页/接口/SPA/批量页，必要时对抗反爬（不重写 crawl4ai 能力） |
| **fetchflow-reverse** | fetchflow 的**逆向子模块**：委托 reverse-flow 分析二进制/固件/APK/脚本/协议/校验/加密（不重写其阶段与证据协议） |
| **reverse-flow** | **纯逆向工作流**：二进制/固件/移动 app/脚本/文档样本/协议抓包，静态+动态分析、补丁对比、可利用性评估 |
| **museon-cli** | **社媒研究/运营**：内容、账号、排期、发布、自动化、数据复盘（装并操作 Museon CLI） |

---

## 域 5｜文档与内容生产 —— 输出文档、PPT、文章、图、笔记

> 演示文稿 / Office 文档 / 长篇写作三件套 + 去 AI 味 / 45 图型 / Obsidian 笔记。

| Skill | 一句话用途（含触发词） |
|---|---|
| **to-ppt** | **演示文稿**：创建/编辑/复刻/读取/导出，每次交付 PPTD 工程目录 + 本地 .pptx（内嵌字体、fade 转场） |
| **officecli** | **Office 文档 CLI**：创建/检查排版/校对/加图表/定向编辑/渲染 PNG，无需装 Office；与文档插件族协作（取它们的设计规格，用 officecli 执行与渲染） |
| **writing** | **长篇写作编排入口**：查产物文件判阶段 → 路由 fragments / shape / beats，成文后可选 humanizer |
| **writing-fragments** | 写作·**探索**：访谈式挖原始素材碎片，尚无结构（只 append 不删改） |
| **writing-shape** | 写作·**收束**：把素材线性排成文章，逐段成文 |
| **writing-beats** | 写作·**叙事**：把素材排成"节拍"旅程，叙事成文（与 shape 二选一，不接力） |
| **writing-humanizer** | **去掉文本里的 AI 味**（中文 AI 味），成文后润色；不接管 explore/exploit |
| **diagram-design** | **45 种示意图**（架构/架构增量/流程/时序/状态机/ER/泳道/甘特/象限/雷达/桑基/鱼骨/Wardley/服务蓝图/故事地图…）→ 内联 SVG 的独立 HTML；可导入并重绘 draw.io / Mermaid / Excalidraw |
| **obsidian-vault** | **Obsidian 笔记**：搜索/创建/整理，带 wikilink 和索引笔记 |

---

## 域 6｜UI 设计 —— 页面长什么样

| Skill | 一句话用途（含触发词） |
|---|---|
| **finesse-ui** | **高质量 web 界面**：品牌页/产品页/工作流 UI/AI 助手 UI/电商/纸刊拼贴，按 register 路由，防廉价感；图表类 brief 路由到 diagram-design |
| **zine-ui** | **照片/诗意类 brief** 的纸面材料语言（拾景纸刊）：实景拼贴/影像蒸馏/抽象记忆面板三路径 |

---

## 域 7｜设备与环境自动化 —— 操作手机、浏览器、桌面、命令行

| Skill | 一句话用途（含触发词） |
|---|---|
| **wizard** | **生成交互式 bash 向导**：把只有人能做的步骤（配凭据/走第三方后台/一次性迁移）交给人类 |
| **vision** | **识别图片内容**：本地/网络图片的分析描述，或 View 不可用时的识图兜底 |
| **quarkclouddrive** | **夸克网盘**：上传/下载（断点续传）、分享/转存、搜索、批量重命名与整批撤销、相册整理、AI 助手 |

---

## 域 8｜交接与辅助 —— 会话之间、人机之间

> 交接文档 / 后台接手 / 重述 / 教学 / 考前速成 / 人生决策。

| Skill | 一句话用途（含触发词） |
|---|---|
| **handoff** | **把当前会话压缩成交接文档**给另一个 agent 接手（跨 harness/目录/同事，要的是可移植性） |
| **claude-handoff** | **立即把整个会话交给全新后台 agent** 继续干活，不写可移植文件 |
| **wait-what** | **上一条没被理解**（用户困惑/反驳/你读错了意图）：停下来重述上下文、用大白话 + 仓库通用词汇重新表达 |
| **teach** | **在本工作区教你一个新技能/概念**，跨会话状态化推进 |
| **universal-exam-cram-coach** | **考前极速复习**：解析大纲 → wiki 知识库 + 题库 → 刷题判分 → 错题复盘（内含 9 个子 skill：exam-ingest / exam-audit / exam-cram / exam-quiz / exam-review / exam-study-guide / exam-cheatsheet / exam-tutor / confusion-tracker） |
| **life-decision-guide** | **具体人生决策**：按《高性价比人生指南》先查条目再答，按成本×收益×证据等级 A/B/C 排序，每条注明出处节条 |

---

## 域 9｜插件族 —— 仓库外提供，按 `family:skill` 调用

> 不在此仓库，随宿主环境安装。9 个条目 / 6 个家族。

| 条目 | 一句话用途 |
|---|---|
| **documents:docx** | **Word 文档**：创建/编辑/修订/批注/格式保留/提取文本（原 `document-skills:docx`） |
| **pdf:pdf** | **PDF 专业工具箱**：报告/创意视觉/学术 LaTeX/既有 PDF 处理（原 `document-skills:pdf`） |
| **presentations:pptx** | **PPT 文件**：pptxgenjs / python-pptx 创建编辑（原 `document-skills:pptx`） |
| **spreadsheets:xlsx** | **表格文件**：读写 xlsx/xlsm/csv/tsv（原 `document-skills:xlsx`） |
| **browser-use:control-browser** | **主代理亲自操作浏览器**：导航/点击/输入/截图/验证（禁止下派子代理） |
| **browser-use:web-gui-tester** | **黑盒前端测试**：纯 GUI 模拟真实用户，截图验证 |
| **android-emulator:android-dev** | **Android app**：构建/运行/安装/截图/UI 自动化（截图、UI 树、日志、点击滑动输入） |
| **computer-use:computer-use** | **整机桌面控制**：浏览器/设备自动化都不合适时直接操作 GUI |
| **plugin-creator:plugin-creator** | **脚手架并打包新插件**（一族 skill） |

---

## 记忆口诀（速记版）

```
生态自洽问 ask-matt（全库动态路由），术语找 vibehub，造/审/进化 skill 走 dao-skill，
逻辑检查 simple-logic，拆书蒸馏 cangjie-skill；
立项先想有哪些面 product-facets，想法模糊上 grill 系（grilling / grill-me / grill-with-docs / loop-me），
要立项就 to-spec → to-tickets，大工程 wayfinder，整条流水线 project-kickoff，文档骨架 doc-scaffold；
动手写码 implement + tdd，整份 spec 并行跑 implement-spec，要验证先 prototype，出 PR 用 pr，
环境一次 setup-pre-commit / setup-ts-deep-modules / setup-matt-pocock-skills；
设计模块 codebase-design + domain-modeling，扫描 improve-*-architecture，删冗余 simplify-codebase；
交付前 code-review + threat-model，出 bug 找 diagnosing-bugs，冲突 resolving-merge-conflicts，危险命令 git-guardrails；
事后 retro 复盘环境，收尾 neat-freak，沉淀 distill-lesson，写码前查经验 kb-search，issue 走 triage；
查资料 agent-reach / research，爬+逆 fetchflow（crawl / reverse 子模块），纯逆向 reverse-flow，社媒 museon-cli；
文档 to-ppt + officecli（插件族 docx / pdf / pptx / xlsx），长文 writing（fragments→shape/beats，完稿 humanizer 去 AI 味），
图示 diagram-design（45 型），笔记 obsidian-vault；
界面 finesse-ui / zine-ui；
手机 android-dev，浏览器 control-browser / web-gui-tester，桌面 computer-use，向导 wizard，看图 vision，网盘 quarkclouddrive；
交接 handoff / claude-handoff，没说清 wait-what，教学 teach，考前 cram-coach，人生决策 life-decision-guide。
```

---

## 相对旧版的变更（对齐 2026-10-23 库状态）

旧版记 70 条，与当前库的差异如下，逐条已在上文落实：

| 变更 | 说明 |
|---|---|
| 移除 **context-monitor** | 目录已不在库中（`Test-Path` 为假），上下文占用问题改由会话侧 `/compact` 处理 |
| 改名 **open-kimi-ppt → to-ppt** | 现覆盖 PPTD 工程 + 本地 .pptx，含读取与复刻 |
| 拆名 **document-skills:\* → documents:docx / pdf:pdf / presentations:pptx / spreadsheets:xlsx** | 原单插件在宿主侧拆成 4 个家族 |
| 新增 **simple-logic** | 《简单的逻辑学》9 张能力卡，Falsify 轴与对抗性自检的执行层 |
| 新增 **implement-spec** | 任务图 + implementer 子智能体并行 + 单集成分支 |
| 新增 **pr / retro** | PR 正文模板；会话复盘改环境而非改代码 |
| 新增 **life-decision-guide** | 《高性价比人生指南》决策咨询 |
| 新增 **fetchflow-crawl / fetchflow-reverse** | 原只列 fetchflow 一个名字，其子模块也是可调用 skill |
| 补全 **universal-exam-cram-coach** 子 skill | 9 个子 skill 名列出 |
| 图型 **27 → 45** | diagram-design 扩到 45 型，新增架构增量/轴测/桑基/鱼骨/Wardley/服务蓝图/故事地图等 |
| 评审轴表述更新 | code-review 现为 Standards + Spec 并行、Falsify 按编排方请求、Architecture 入 kickoff 期末审核 |
| 新增 **域 9 插件族表** | computer-use / plugin-creator 等 9 条目单列，不混进仓库内统计 |
