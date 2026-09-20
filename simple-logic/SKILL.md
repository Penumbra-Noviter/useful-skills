---
name: simple-logic
description: |
  用户想系统掌握《简单的逻辑学》的思维方法（谬误识别、论证评定、事实确认、
  沟通清晰化、因果分析、态度自检）时使用本入口；也用于不确定具体该用哪个能力、
  需要整书方法导航的场合（whole-book / 整本书 / 逻辑思维方法 / critical thinking /
  logical thinking）。入口给出全书记忆主题、能力地图与使用顺序；若意图明确命中单个能力，直接进入该能力。
metadata:
  cangjie.generated-by: cangjie-tools v2.5.0
  cangjie.variant: single
  cangjie.bundle-id: bundle.simple-logic
  cangjie.capability-count: 9
  cangjie.entrypoint-count: 1
---
# 简单的逻辑学 — 全书能力入口

## 触发与不触发

**适用**：与本书能力域相关的咨询与任务（见下方路由表的意图列）。
**不适用**：
- 作者人设角色扮演（那是 nuwa-skill 的职责）
- 纯书摘、读后感和出版社营销内容
- 需要统计模型的因果推断与概率决策（应走数据方法）

## 核心原则（常驻速览，概览类问题读到这里即可回答）

1. 论证成败 = 前提真实 + 结构有效，两者缺一不可
2. 谬误常伪装得比正确推理更合理，因为它直接作用于情感
3. 先确认事实，再谈观念、语言与论证
4. 结论的量与质不能超越前提；省略量词默认按全称理解
5. 因果要沿链追到根本原因，不能停在直接原因
6. 论证求真相，争吵求击败；真诚是必要非充分，更要正确

## 能力路由（先读本表，按意图加载 1 张能力卡）

| 用户意图 | 先读 | 补读/备注 |
|---|---|---|
| 识别或命名逻辑谬误；审查广告/辩论/情绪化标题中的操纵手法；自查自己的论证哪里有逻辑错误 | references/capabilities/fallacy-detector.md | references/capabilities/argument-evaluator.md |
| 评定提案/观点/文章的论证是否成立；构造说服性论证前自查；区分观点与论证、必然与可能 | references/capabilities/argument-evaluator.md | references/capabilities/fact-confirmation.md、references/capabilities/quantifier-audit.md |
| 把含混/歧义/绕弯的表达改清楚；识别并治理闪避式语言（再研究研究/再说吧）；补全被省略的主语与量化词 | references/capabilities/clear-communication.md | references/capabilities/define-terms.md |
| 评估条件句/预测/承诺的推理是否成立；按历史规律外推时判断可信度；技术风险评估中的 if-then 断言 | references/capabilities/conditional-argument.md | references/capabilities/argument-evaluator.md |
| 核实说法/传言/新闻是否为真；评估信息来源可靠性；区分可核查事实与价值判断 | references/capabilities/fact-confirmation.md | references/capabilities/argument-evaluator.md、references/capabilities/root-cause.md |
| 审计全称化概括是否越界；修正'大部分=全部'类表述；识别省略量词的暗示 | references/capabilities/quantifier-audit.md | references/capabilities/argument-evaluator.md |
| 为模糊概念建立可操作定义；破解词义分歧导致的争论绕圈；辩论/写作前先定义关键术语 | references/capabilities/define-terms.md | references/capabilities/clear-communication.md |
| 追问题反复出现的根本原因；区分直接原因与根本原因；归因争论时用因果链分析 | references/capabilities/root-cause.md | references/capabilities/fact-confirmation.md |
| 自检怀疑论/玩世不恭/情感压倒论证的心态；区分论证与争吵，决定是否继续辩论；打断'信得深就对'的自我辩护 | references/capabilities/attitude-check.md | references/capabilities/argument-evaluator.md |

**非能力类查询**：
- 书名/作者/章节/整书概览 → references/overview.md
- 术语解释 → references/glossary.md
- 决策规则速查（不需要原文依据时） → references/cheatsheet.md
- 完整意图与关键词索引（本表未覆盖的意图先查这里） → references/capability-index.md

## 加载规则

- 每次任务先读本文件，再按路由表加载 **1** 张能力卡；任务明确跨域时最多加载 2 张。
- 概览/书名类问题不加载能力卡，用「核心原则」与 overview.md 回答。
- 路由表与 capability-index.md 都无法命中的意图，明确告知超出本书范围，不要硬套。

## 边界与判停

- 用户只做纯事实查询，不需要方法论应用
- 用户明确指名某一具体能力（直接进对应 Skill，不经入口）
- 目标内容明显超出该书的亚里士多德式经典逻辑框架（如非经典逻辑、贝叶斯决策）
