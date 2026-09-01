---
name: writing
description: 写作编排层：一个入口把长篇写作意图路由到 writing 三件套的正确阶段——writing-fragments（explore，访谈挖素材）/ writing-shape（exploit，线性成文）/ writing-beats（exploit，叙事成文）。通过检查已有写作产物文件判定当前阶段并自动衔接，替代用户手动串联三件套。成文后若有去 AI 味需求，路由到 writing-humanizer 做润色。Use when the user wants to write an article, essay, long post, story, or long-form prose; turn notes, material, or a transcript into a piece of writing; continue or reshape an already-started piece; or doesn't know how to start. 触发词：写文章、写一篇、写长帖、把素材写成文、这篇怎么写、帮我写个东西、write an article/essay/story/long post、turn this into prose、write this up、去AI味、去AI痕迹、人性化、写得像人、AI味太重、humanize、de-AI. 不接管：短回复、评论、commit message、一句话文案——那不属于三件套的成文工作。
---

# Writing（编排层）

**写作编排层，不是第四种写法。** 你路由到三件套既有机制，不重写。你的工作是接住意图、判定阶段、传好文件路径——然后按对应子 skill 的 SKILL.md 执行，冲突以子 skill 为准。

## 何时接，何时不接

**接**：用户要一篇**独立成文的写作物**（文章、长帖、essay、叙事、把一堆素材/笔记/录屏文字整理成文），或在写一篇的途中。
**不接**：
- 短回复、评论、commit message、一句话文案（非成文）；
- 情感陪伴、闲聊（不是写作任务）；
- 界面/海报文案、PPT 文案（属于 finesse-ui / zine-ui / open-kimi-ppt 域）。
不接时直接言明"这不是三件套的成文工作"，不强行路由。

## Step 1 · 判定阶段（先查文件系统，再问）

**文件即状态**：写作进度承载在产物文件上，先查文件，别先问。

约定产物路径（当前工作目录下）：
- `writing/fragments.md` — explore 产物（碎片堆）
- `writing/article.md` — exploit 产物（成文）

检查顺序：
1. 用户显式指定了路径？→ 用指定路径，不发明。
2. 否则查 `writing/fragments.md` 与 `writing/article.md` 是否存在。

| 文件状态 | 阶段判定 | 动作 |
|---|---|---|
| 无产物文件 | 未开始 | 看意图：有素材 → 直接 exploit；只有话题 → explore |
| 有 `fragments.md`，无 `article.md` | explore 完成，待成文 | 进入 exploit（形状见 Step 2） |
| 有 `fragments.md` 且最近会话在挖 | explore 中 | 继续 fragments（追加/就编辑），除非用户要成文 |
| 有 `article.md` | exploit 中 | 续写/改写文章文件 |
| 无产物但用户口头给了素材 | 直接 exploit | 素材即 pile，跳过 explore |

**阶段可跳过**：用户已有完整素材时，explore 不是必经仪式。先查文件，再按表走；只有文件缺失且意图不明时才问"存哪/写哪"。

## Step 2 · 路由（阶段 → 子 skill）

| 阶段 | 子 skill | 传参 |
|---|---|---|
| explore（挖素材） | `writing-fragments` | 产物路径（默认 `writing/fragments.md`） |
| exploit · 论述/说明/教程/观点型 | `writing-shape` | pile=碎片文件路径 + 产物路径（默认 `writing/article.md`） |
| exploit · 叙事/旅程/场景/回忆型 | `writing-beats` | 同上 |

**shape 与 beats 是替代关系，不是接力**：同一篇素材只需跑其一。形状模糊时按体裁判——论点推进、解释说明、how-to → shape；讲故事、带旅程感的体验/复盘 → beats；仍不清问一次，不问成默认 shape。

**路由前不用重新盘点三件套能力**——你的工作是路由和传参，不是复述机制。

## Step 3 · 衔接契约

1. **执行时读子 skill**：路由到哪个阶段，就 Read 那个子 skill 的 `SKILL.md` 并按其流程执行（三件套是 user-invoked，由你代跑）。本文件不复制其机制（grounding/append/只读 pile/改写规则一律以子 skill 为准）。
2. **路径在调用时显式传入**：explore 传产物路径；exploit 传 pile 路径 + 产物路径。子 skill 内部"没给路径就问一次"的兜底永远不该触发——你已经传了。
3. **产物文件冲突**：`article.md` 已存在且是新一篇 → 问一次（覆盖/另起名），不静默覆盖。
4. **跨 session 衔接**：新会话靠产物文件判定阶段，直接续。本 skill 自身不留状态文件——状态 = 产物文件本身（`skill-ecosystem.md` 只记编排关系，不记单个写作事项）。

## Step 4 · 成文后润色（可选，去 AI 味）

成文完成后（`article.md` 已存在），用户若要求"去 AI 味 / 人性化 / 写得像人 / AI 味太重 / humanize"，路由到 **`writing-humanizer`**：传产物文件路径或粘贴的文本。

- **这是润色即输出，不是第四写作阶段**：它不改写文章结构、不重新成文，只做去味编辑。执行时 Read `writing-humanizer/SKILL.md` 按其流程做，本文件不复制其模式清单。
- 触发时机：成文后用户主动要求，或成文的 AI 味明显时提议一次（"要不要我去一遍 AI 味？"），不默认自动跑。
- 无成文产物、用户直接甩一段外部 AI 文本要"去 AI 味" → 也路由到 `writing-humanizer`（它本来就是审阅/润色工具，不要求先经过三件套）。

## 通过标准

本轮路由"做对了"的判定清单：

- [ ] 接住了成文意图：用户说"写文章/写长帖/把素材写成文"，你路由到了本编排层，而不是当普通聊天处理
- [ ] 阶段判定先查文件：产物文件存在时，没有要求用户重新解释进度
- [ ] 路由命中正确子 skill：explore（fragments）/ exploit 论述（shape）/ exploit 叙事（beats）三者选对了，或只在形状模糊时问了 1 次
- [ ] 路径显式传入：子 skill 执行时拿到了 pile 与产物路径，没触发它"问一次存哪"的兜底
- [ ] 去 AI 味路由正确：成文后或外部文本要求人性化时，路由到了 `writing-humanizer` 而非当普通改写处理
- [ ] 未越界：没有新增第四阶段（去 AI 味是成文后润色，不是写作阶段），没有在编排层重述 grounding/append/模式清单等子 skill 既有机制
- [ ] 冲突先问：`article.md` 已存在且是新一篇时，先确认覆盖/另起名，没有静默覆盖

## 边界

- 不重写三件套的写作机制、文件格式、改写纪律；不把它们的规则复制到本文件。
- 不替三件套发明第四阶段（如"发布""排版"）——用户要求发布/排版时说明不在编排层内，按需走 open-kimi-ppt 等其他 skill。`writing-humanizer` 的去 AI 味同样不是第四阶段：它是成文后的润色 pass，机制在子 skill，不在本文件。
- 唯一职责：意图 → 阶段/润色 → 子 skill → 文件路径。路到了，执行就交给子 skill 的 SKILL.md。