---
name: writing-humanizer
description: "Writing, polish: 去除文本中的 AI 写作痕迹（去中文 AI 味），使其听起来更像人类书写。适用于成文后润色、审阅他人 AI 生成的文本、把 AI 味重的段落改写自然。触发词：去AI味、去 AI 味、去AI痕迹、人性化、写得像人、别这么像AI、AI味太重、humanize、de-AI、de-ai。不接管：explore（挖素材，writing-fragments）/ exploit 成文（writing-shape / writing-beats）——那是三件套的活；本 skill 只做成文后的去味润色。"
disable-model-invocation: true
---

<what-to-do>

The user has passed (or will pass) a piece of text — usually an already-written Chinese article, a paragraph, or someone else's AI-generated draft — and wants the AI smell taken out of it. This is **polish**: the writing is done, the job is to make it read like a person wrote it. You are a text editor, not a ghostwriter.

Read the text end-to-end. Scan it against the AI patterns below. Rewrite the offending passages in place — same meaning, same tone, natural voice. Then present the humanized version with a short summary of what changed.

If the user did not say where to output (replace the file / paste into chat / new file), ask once. Default: output in chat if the text was pasted; edit the file in place if a path was given.

</what-to-do>

<supporting-info>

## The one idea

LLMs pick the statistically most likely next word, so their prose leans toward whatever fits the widest audience: grand claims, tidy triads, hedging, and throat-clearing. Removing the smell is not about vocabulary purges — it is about **making the writer sound like a person with a point of view**. Clean is not enough; the result must have voice.

## Five core rules (scan against these constantly)

1. **Delete filler.** Openers and emphasis crutches ("值得注意的是", "不难发现", "总而言之", "在现代社会中") go first.
2. **Break formula.** No binary contrasts for their own sake, no dramatic single-line paragraph breaks, no rhetorical setups.
3. **Vary the rhythm.** Mix sentence lengths. Two beats beat three. Vary how paragraphs end.
4. **Trust the reader.** State facts directly; skip softening, apologizing, and hand-holding.
5. **Kill the quotable.** If a line sounds like it belongs on a poster ("这不是X，而是Y"), rewrite it.

## The pattern catalog (the reusable mechanism)

Work through these categories; each entry lists the tell and the fix. The vocabulary lists are the highest-leverage search terms — grep the text for them, then judge each hit.

### Content patterns

1. **夸大意义/遗产/趋势** — tells: 作为/充当、标志着、见证了、是……的体现/证明/提醒、极其重要/至关重要/核心/关键作用、凸显/彰显其重要性、反映了更广泛的、象征着其永恒的、为……奠定基础、标志着/塑造着、关键转折点、不断演变的格局、不可磨灭的印记。
   Fix: say what the thing actually is/does, drop the cosmic significance. "X 成立于 1989 年，负责收集和发布区域统计数据" not "X 的成立标志着西班牙区域统计演变史上的关键时刻，是更广泛运动的一部分".
2. **过度强调知名度/媒体报道** — tells: 独立报道、地方/区域/国家媒体、由知名专家撰写、活跃的社交媒体账号。
   Fix: keep the specific citation, drop the fame-claim. "在 2024 年《纽约时报》的采访中，她认为……" not "她的观点被《纽约时报》、BBC 引用，她在社交媒体上拥有超过 50 万粉丝".
3. **以 -ing 结尾的肤浅分析**（中文表现为句末"……，象征着/体现了/展现了/反映了/彰显着……"）— tells: 突出/强调/彰显、确保、反映/象征、为……做出贡献、培养/促进、涵盖、展示。
   Fix: end the sentence at the fact. "寺庙使用蓝色、绿色和金色。建筑师说这些颜色是为了呼应当地的蓝帽花" not "……与该地区自然之美产生共鸣，象征着社区与土地的深厚联系".
4. **宣传/广告式语言** — tells: 拥有（夸张用法）、充满活力的、丰富的（比喻义）、深刻的、增强其、展示、体现、致力于、自然之美、坐落于、位于……的中心、开创性的、著名的、令人叹为观止的、必游之地、迷人的。
   Fix: strip adjectives, give facts. "X 是贡德尔地区的一座城镇，以每周集市和 18 世纪教堂闻名" not "坐落于令人叹为观止的区域内，是一座充满活力的城镇，拥有丰富的文化底蕴和迷人的自然美景".
5. **模糊归因** — tells: 行业报告显示、观察者指出、专家认为、一些批评者认为、多个来源/出版物（却拿不出具体引用）。
   Fix: name the source or drop the claim. "根据中科院 2019 年的调查，X 支持多种特有鱼类" not "专家认为它在区域生态系统中发挥着至关重要的作用".
6. **提纲式"挑战与未来展望"** — tells: 尽管其……面临若干挑战、尽管存在这些挑战、挑战与遗产、未来展望。
   Fix: name the actual problem and what happened. "2015 年三个新 IT 园区开业后交通拥堵加剧。市政公司 2022 年启动了雨水排水项目" not "尽管工业繁荣，X 面临着典型的城市挑战，凭借其战略位置继续蓬勃发展".

### Language & grammar patterns

7. **AI 高频词** — tells: 此外、与……保持一致、至关重要、深入探讨、强调、持久的、增强、培养、获得、突出（动词）、相互作用、复杂/复杂性、关键（形容词）、格局（抽象名词）、关键性的、展示、织锦（抽象名词）、证明、强调（动词）、宝贵的、充满活力的。
   Fix: use plain equivalents or restructure. "索马里菜肴还包括骆驼肉，被认为是美味" not "此外，索马里菜肴的一个显著特征是加入骆驼肉".
8. **系动词回避** — tells: 作为/代表/标志着/充当 [一个]、拥有/设有/提供 [一个]。
   Fix: use "是"/"有" plainly. "Gallery 825 是 LAAA 的当代艺术展览空间，有四个房间" not "Gallery 825 作为 LAAA 的当代艺术展览空间，设有四个独立空间，拥有超过 3000 平方英尺".
9. **否定式排比** — tells: "不仅仅是……而是……""这不仅仅是……，更是……"。
   Fix: say the thing once, directly. "沉重的节拍增加了攻击性的基调" not "这不仅仅是节拍在人声下流动；它是攻击性和氛围的一部分".
10. **三段式法则** — tells: 强行把想法分成三组显得全面。
    Fix: two items, or four. "活动包括演讲和小组讨论。会议之间还有非正式社交的时间" not "活动包括主题演讲、小组讨论和社交机会".
11. **刻意换词（同义词循环）** — tells: 同一对象在不同句用不同称呼换来换去。
    Fix: keep the same word, collapse. "主人公面临许多挑战，但最终获胜并回到家中" not "主人公面临挑战。主要角色克服障碍。中心人物最终获胜。英雄回家".
12. **虚假范围** — tells: "从 X 到 Y"，而 X、Y 不在同一尺度上。
    Fix: name the actual span. "这本书涵盖了大爆炸、恒星形成和当前关于暗物质的理论" not "我们穿越宇宙的旅程从大爆炸的奇点带到宏伟的宇宙网，从恒星的诞生到暗物质的神秘舞蹈".

### Style patterns

13. **破折号过度使用** — tells: 句子里塞进 — 来制造"有力"感。
    Fix: use commas or full stops. (中文尤见于半角/全角破折号滥用。)
14. **粗体过度使用** — tells: 机械地用 **加粗** 强调短语。
    Fix: keep only the truly structural emphasis, drop the rest.
15. **内联标题垂直列表** — tells: 列表项以**粗体标题：**开头。
    Fix: fold into prose. "更新改进了界面，加快了加载时间，加了端到端加密" not "- **用户体验：**……- **性能：**……".
16. **标题大写** — 中文标题无大小写问题，此模式不适用，跳过。
17. **表情符号装饰** — tells: 🚀💡✅ 等装饰标题/列表。
    Fix: plain text.
18. **弯引号/引号混乱** — tells: 中文文本里混入英文直引号 ""，或全角引号不统一。
    Fix: 统一用中文引号「」或“”（按上下文约定，全文一致）。

### Conversational patterns

19. **协作交流痕迹** — tells: 希望这对您有帮助、当然！、您说得完全正确！、请告诉我、这是一个……、如果您需要我扩展任何部分。
    Fix: delete the meta-talk; the content should stand alone. "法国大革命始于 1789 年" not "这是法国大革命的概述。希望这对您有帮助！"
20. **知识截止/信息免责声明** — tells: 截至 [日期]、根据我最后的训练更新、虽然具体细节有限/稀缺……、基于可用信息……。
    Fix: state what is known. "根据注册文件，该公司成立于 1994 年" not "虽然关于成立的具体细节在现成资料中没有广泛记录，但它似乎是在 20 世纪 90 年代成立的".
21. **谄媚/卑躬屈膝** — tells: 好问题！、您说得完全正确！、这是一个很好的观点。
    Fix: neutral acknowledgment. "您提到的经济因素在这里是相关的" not "好问题！您说得完全正确，这是一个复杂的话题".

### Filler & hedging

22. **填充短语** — "为了实现这一目标"→"为了这一点"；"由于……的事实"→"因为……"；"在这个时间点"→"现在"；"在您需要帮助的情况下"→"如果您需要帮助"；"系统具有处理的能力"→"系统可以处理"；"值得注意的是数据显示"→"数据显示"。
23. **过度限定** — "可以潜在地可能被认为该政策可能会对结果产生一些影响"→"该政策可能会影响结果"。
24. **通用积极结论** — "公司的未来看起来光明。激动人心的时代即将到来"→"该公司计划明年再开两个地点"。结论落到事实，不落到气氛。

## Putting a soul back in (clean is the floor, voice is the goal)

Even with every pattern removed, flat prose still smells machine-made. Watch for these warning signs and fix them while you edit:

- Every sentence the same length and shape.
- No point of view — neutral reportage only.
- No acknowledgment of uncertainty or mixed feelings.
- No first person where it's natural.
- No humor, no edge, no personality.
- Reads like a Wikipedia article or press release.

How to add tone: **have a take** (react to the facts, don't just report them); **vary the rhythm** (a short punchy sentence, then a long one that unfolds); **acknowledge complexity** ("这令人印象深刻但也有点不安" beats "这令人印象深刻"); **use "我" when honest** ("我一直在想……" signals a real person thinking); **allow some mess** (digressions, half-formed thoughts are human); **be specific about feelings** (not "这令人担忧" but "凌晨三点没人看着的时候，智能体还在不停地运转，这让人不安").

## Workflow

1. Read the input text fully.
2. Scan for the 24 patterns (grep the vocabulary lists first — they surface most hits fast).
3. Rewrite each offending passage in place; keep meaning, tone, and the writer's existing voice where there is one.
4. Before delivering, run the quick checklist (below).
5. Deliver the humanized version + a brief change summary (what was removed/replaced and why).

## Quick checklist (run before delivery)

- [ ] Three sentences in a row the same length? Break one.
- [ ] Paragraph ends on a neat one-liner? Vary the ending.
- [ ] A dash before a reveal? Delete it.
- [ ] Metaphor being explained? Trust the reader.
- [ ] "此外/然而/值得一提的是" connectors? Consider deleting.
- [ ] Rule-of-three lists? Make it two or four.
- [ ] Does it have a point of view, or does it just report?

## Quality scoring (self-assessment, /50)

| 维度 | 标准 | 得分 |
|---|---|---|
| 直接性 | 直接陈述还是绕圈宣告（10=直截了当，1=充满铺垫） | /10 |
| 节奏 | 句子长度有变化（10=长短交错，1=机械重复） | /10 |
| 信任度 | 尊重读者（10=简洁明了，1=过度解释） | /10 |
| 真实性 | 像真人说话（10=自然流畅，1=机械生硬） | /10 |
| 精炼度 | 无可删（10=无冗余，1=大量废话） | /10 |

45-50 优秀；35-44 良好，仍有改进空间；低于 35 需要重新修订。

## Source and boundaries

- Mechanism distilled from [Humanizer-zh](https://github.com/op7418/Humanizer-zh) (MIT, © 歸藏; translated from blader/humanizer, referencing hardikpandya/stop-slop), itself based on Wikipedia's [Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing). See `PROVENANCE.md` §15.
- Out of scope: mining new material (fragments), structuring/exploit (shape/beats), publishing or platform formatting. This skill polishes text that already exists.
- If the input has no AI smell to begin with, say so plainly — do not invent edits to justify the pass.

</supporting-info>
