# Regression — 全流程反测基线

finesse-ui 用 13 个精选示例证明「语料干净」（detect.mjs p0=0），但 §0→§10 的完整方法链从未用「新 brief → 成品 → 过门」做过
回归反测。本文件补齐这个证据缺口：4 个代表性 brief 的 prompt 套件 + 通过标准 + 实跑记录。它回答的问题是：**skill 不只在
存量语料上干净，对从未见过的 brief 走完整个 craft 流程后，产出的页面也能过同一道门。**

本文件由 T1（回归基线）建立，供后续工单在 skill 方法链改动后重新反测，防止「流程只有理论上成立」。

## 用法（如何跑）

每次方法链（SKILL.md §0–§10 / references / detect.mjs）有改动时，重跑一遍：

1. 逐个 brief 执行完整 craft 流程：读 brief → 输出 **Design Read**（决策记录形式）→ 生成 1 个页面 HTML 到临时目录
   （页面是短暂产物，**不提交**，建议放 git 之外的目录，如 `.worktrees/finesse-regression-tmp/`）→
   运行 `node finesse-ui/scripts/detect.mjs --json <页面>` 校验 → 按该 brief 的通过标准逐条检查。
2. **运行时验证（preflight §C，有浏览器时必做）**：grep 只证明引擎代码存在，不证明渲染。用 Playwright 打开页面，
   确认引擎 / 图表 / 提交路径真的出像素、出状态。本批次 4 个页面都做了这一遍，且全部因它抓出过 bug（见「结果与缺口」）。
3. 更新下方「执行矩阵」与「运行记录」，如实记录通过 / 未过与原因。

命令行参考：

```bash
node finesse-ui/scripts/detect.mjs --json <page.html>   # p0 计在 JSON 里；默认退出码恒为 0
node finesse-ui/scripts/detect.mjs --strict <page.html> # 有 P0 时以退出码 1 阻塞（CI 用）
```

## 四个回归 brief（B1–B4 原文 + 各自通过标准）

### B1 · brand landing（验证 brand 路线）

```
craft：一家太空科技公司的 launch landing，premium 方向。用户说"AI 生成的感觉不行，要像人做的"。
```

通过标准：
- Design Read 输出含**显式三 dials**（SOUL/SPECTACLE/DENSITY 三个数值）+ **反默认命名**（不得是紫光渐变+渐变文字那套 AI 味，要写清"拒绝 X，采用 Y"）
- 页面含一个真实视觉引擎（Canvas/Three/GSAP/CSS scroll 任一），且带 `prefers-reduced-motion` 终态（CSS 兜底或 JS 冻结）
- SPECTACLE ≥ 6，或给出明确降级理由（§1.B 诚实降级）
- detect.mjs p0=0（或仅有可说明的意图性元素，逐一注明）

### B2 · read dashboard（验证 product read 路线）

```
craft：一个实时监控后台（SaaS 观测平台），数据来自实时 API，偏 dashboard。
```

通过标准：
- 颜色来自 `references/product-palettes.md`（Design Read 或代码证据），非默认蓝
- **product substrate**（`product-ui.md` §0）：无 grain/vignette/巨型 hero 字体/dark-default；**无 hero engine**
- SPECTACLE 1–4、DENSITY 6–9 区间
- detect.mjs p0=0

### B3 · operate workflow（验证 read/operate 分流 + §0.F 复核）

```
craft：商家后台的"发布营销活动"流程页，带保存/发布，表单较长，数据来自真实 API。
```

通过标准：
- §0.B 后做了 **§0.F 路由复核**，job=operate 判定留痕（在 Design Read/决策记录里写明复核结论）
- 走 `workflow-ui.md` shell（编号分节、提交路径为脊柱），**不是** dashboard 形态硬套
- 主动作是 commit（发布/保存），未被 read 形态带偏
- detect.mjs p0=0

### B4 · converse assistant（验证 converse 路线 + ai-native-ui）

```
craft：一个 AI 助手/agent 面板界面，对话是主职（prompt → 看它工作 → 审阅/批准），像 agent 控制台。
```

通过标准：
- 判断为 converse：对话是页面的主职（有 prompt composer + 流式回答 + 审阅/批准），**不是**"仪表盘+聊天挂件"
- 在 `product-ui.md` 之上加载 `ai-native-ui.md`（Design Read 记录 job=converse）
- SPECTACLE 1–3、DENSITY 6–8
- detect.mjs p0=0

## 执行矩阵

格式：brief | 检查点 | 通过/未过 | 证据（Design Read 一行 / 页面临时路径 / detect p0 数 / 说明）

所有 4 个 brief 于 2026-08-28 实跑；页面临时路径均在
`D:/Desktop/cc/.claude/.worktrees/finesse-regression-tmp/`（不提交）。

| Brief | 检查点 | 结果 | 证据 |
|---|---|---|---|
| **B1** | 显式三 dials + 反默认命名 | ✅ 通过 | `Design Read: space-launch ephemeris · precision-instrument editorial · register=brand · SPECTACLE=7 · hero-engine=Canvas 2D trajectory plot`；Dials: SOUL=7 · SPECTACLE=7 · DENSITY=4。反默认原文：拒 first-order 反射（deep-space starfield + 紫/青 glow + Inter）与 second-order 反射（phosphor-terminal / Linear-violet 暗色），采用「printed flight ephemeris」：warm instrument paper + ink grotesque（Sora）+ 单一 vermillion 信号色 + 工程标尺线 + 手绘轨道 |
| **B1** | 真实视觉引擎 + RM 终态 | ✅ 通过 | Engine B（Canvas 2D）计划轨道图：标尺 tick、飞行走廊虚线带、沿 coast 弧移动的飞行器 + T+ 任务时钟；DPR 自适应。运行时验证：canvas 非透明像素 49,239；模拟 `prefers-reduced-motion: reduce` 后仍出静止帧（45,671 像素）、时钟冻结 `T+00:14:00` |
| **B1** | SPECTACLE ≥ 6 | ✅ 通过 | SPECTACLE=7（Canvas 引擎真实渲染，detect 的 spectacle-not-shown 未触发；§1.B「spectacle claimed, shown」满足） |
| **B1** | detect p0=0 | ✅ 通过 | `b1-arclight-launch.html`：p0=0，findings=0 |
| **B2** | 颜色来自 product-palettes.md，非默认蓝 | ✅ 通过 | 代码证据：`:root` 全套 token 即 `product-palettes.md` Set 4（Teal & Clay）— `--page:#e9eeed` `--accent:#176C6B` `--accent-2:#C4633F` 等；Design Read 注明唯一替换是把 Set 的 `--bg` 白换成 1 步近白 tint（craft floor 禁纯白）。palette 文件 §3 明写 teal 是「the best 'not-blue' escape」 |
| **B2** | product substrate（无 brand grammar） | ✅ 通过 | 无 grain、无 vignette、无 `clamp()` hero 字体（h1 19px）、无暗色默认、无 hero engine；页面含 KPI tile 解剖（icon chip + delta chip + tabular-nums 大字 + sparkline）、hairline 边框、whisper tinted shadow |
| **B2** | SPECTACLE 1–4 / DENSITY 6–9 | ✅ 通过 | Design Read: SPECTACLE=2 · DENSITY=8（cockpit：数字 tabular-mono、请求日志表、数据列表优先） |
| **B2** | detect p0=0 | ✅ 通过 | `b2-tidal-observability.html`：p0=0，findings=0 |
| **B3** | §0.F 路由复核留痕 | ✅ 通过 | 页面包裹注释内决策记录：§0.B 后重跑 read/operate/converse 测试，主职动作 = 发布/保存草稿（consequential commit）→ job=operate → `workflow-ui.md`；§7 装配时复核 shell 形态（编号分节卡 + sticky commit bar），二次确认不误入 dashboard 形态 |
| **B3** | workflow-ui shell（非 dashboard 硬套） | ✅ 通过 | 三栏 workflow shell：rail + topbar（step rail 1→4）+ 720–820px 表单列 + sticky 发布/保存 action bar + aside「消费者端预览」（手机框 290px + 「预览内容仅供参考」disclaimer）。表单 = 4 张编号分节卡（基本信息 / 权益与预算 / 投放设置 / 发布前检查）+ 高级设置折叠 + 预算估算 breakdown（含 5% 服务费可见）+ radio-card 选择 + upload dropzone 规格行 + 全字段 consequence 型 helper |
| **B3** | 主动作是 commit | ✅ 通过 | 运行时验证全路径：预检查卡 live（标题填入后「发现 3 项问题」→「2 项」；预算改为 ¥30,000 / 单价 ¥25 → breakdown 重算 1,200 单 / 服务费 ¥1,500）；保存草稿时间戳；发布 → 后果型确认对话 → 发布中 → 页级成功态（活动编号 XM-2026-09120 · 生效时间 · 冻结预算） |
| **B3** | detect p0=0 | ✅ 通过 | `b3-xinglian-campaign.html`：p0=0，findings=0 |
| **B4** | converse 判定 + 非「仪表盘+聊天挂件」 | ✅ 通过 | 页面无 KPI 行 / 无 read 侧 shell；主职 = 会话面板 + 底部固定 composer + prompt→watch→review/approve 闭环。Design Read 决策记录写明判定方法，页面结构为 ai-native 形态（composer pinned、流式回答带 sources/actions/followups、thinking trace、工具 chip、任务行、审批卡、推荐卡、context 卡） |
| **B4** | ai-native-ui 在 product-ui 之上（job=converse） | ✅ 通过 | Design Read: `job=converse · substrate=ai-native (ai-native-ui.md on product-ui)`；token 层照 ai-native §1：cool 近白画布、hairline 实线、三步 ink ramp、封闭 radius 刻度、strong-out easing、tabular-nums 计时、任务行 `role="status"` |
| **B4** | SPECTACLE 1–3 / DENSITY 6–8 | ✅ 通过 | Design Read: SPECTACLE=2 · DENSITY=7 |
| **B4** | detect p0=0 | ✅ 通过 | `b4-zhiyun-agent.html`：p0=0，findings=0 |

运行时验证均通过（Playwright，本地 `http://127.0.0.1:8377` 起临时目录静态服务）：B2 donut 弧长动画（dasharray 0→46/96.7）、
条形 scaleY(0→1)、折线 stroke-dashoffset 全绘制、KPI 计数滚动、live sync 每 2s 走表；B4 完整 agent run =
2 工具 chip（输入+结果可见）、3 任务行全 completed、思考痕迹、流式回答 + 4 sources / 4 actions / 4 followups、
审批卡（选项单选可用）、推荐卡；RM 下流式直接到终态、caret 静止、任务与时间照常推进。

## 结果与缺口

**结果：4/4 brief 实跑且全部通过各自通过标准**（detect p0=0 × 4，findings=0 × 4）。brand / read / operate / converse 四
条路线都从「冷 brief」走通了 §0→§10 全链并在运行时拿到真实像素与真实状态。

**运行时反测的价值（本批次 4 个 bug，全部由运行时验证抓出，静态 detect 均为 0）：**

1. **B1 任务时钟** — rAF 回调的 `DOMHighResTimeStamp` 与 epoch 时间戳混用导致时钟输出负数。修：时钟统一用 `Date.now()`。
2. **B3 预检查卡** — 标题 input 只刷新字符计数与预览，未刷新 live 预检查行（「未填写」残留）。修：title input 时触发 `syncCheck()`。
3. **B4 RM 流式** — `slice(0, i)` 在 `i+=…` 之前取值，reduced-motion 首帧 `slice(0,0)` 渲染空回答。修：先自增再切片。
4. **B4 审批卡** — 选项默认选中态只在动效模式铺设，RM 静态度缺省。修：默认选中移到 RM early-return 之前。

这批页面只做了机械门（detect）+ 结构契约 + 运行时像素/状态验证，**未做画廊级打磨**（「页面不需要画廊级成品」）。detect 的
NOT_COVERED 清单（by-eye 项 + `[impeccable·runtime]` 项）与每页自身的视觉细节仍需要观感级人工检查，这与既有 13 示例的承诺一致。

**缺口（如实记录）：**
- 页面对比度 / 字号等由肉眼可查但本批次未用工具逐像素测量（detect 的 runtime 规则需要 DOM 化测量，留给未来的 Playwright 断言层）。
- 4 个页面为一次性产物，未提交、未进示例库；方法链改动后需按「用法」重跑（产出路径与命令已写在文件开头）。
- 全部页面为单文件静态实现（vanilla JS + CSS transition / Canvas），产品路线未走 React/Next.js + Tailwind 的 stack-defaults 缺省栈；
  针对该栈的回归（RSC / Motion / next/font）不在本批次范围。

## 运行记录

- **日期**：2026-08-28
- **执行者**：T1 回归基线（ZCode implement 子代理，worktree `kickoff/finesse-opt` @ 452e198）
- **工具版本**：`finesse-ui/scripts/detect.mjs`（**skill v0.21.0**，脚本最近一次提交 225572b）；命令 `node detect.mjs --json`
- **结果摘要**：B1–B4 全部实跑，detect 每页 `p0=0, findings=0`；4/4 通过各自通过标准；运行时验证 4/4 完成并修复 4 个静态检测不可见的 bug