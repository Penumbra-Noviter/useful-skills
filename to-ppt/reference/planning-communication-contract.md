# Planning: Communication Contract（沟通契约，论证先行）

> 来源：蒸馏自 [hugohe3/ppt-master](https://github.com/hugohe3/ppt-master)（MIT，© 2025-2026 Hugo He）`skills/ppt-master/references/plan-core.md` 的规划机制，改写为 to-ppt 的 PPTD 语境。核心主张：**先让论证在 outline 里成型，再动手设计页面**——排版是论证的载体，不是替代品。

## 1. 六问沟通契约（生成前必须回答）

任何 PPT 任务，在理解需求（step2）与生成（step3）之间，先回答这六个问题。答案不确定时问用户，不得自己静默假设；答案只影响内容组织，不改用户已确认的页数/范围：

| 字段 | 回答的问题 |
|---|---|
| `audience` | 谁必须接收到这份演示？他们已知什么、在乎什么？ |
| `communication_intent` | 这份演示要实现什么变化？（inform / explain / persuade / decide / align / teach / report / mobilize / record——可组合，写明优先级） |
| `audience_outcome` | 接收者听完后的可观察变化是什么——知道、理解、相信、决定或做什么？ |
| `core_message` | 即使其他全忘，也必须留下的主张/决策/行动是什么？ |
| `delivery_context` | 主导方式：presenter-led / reader-led / hybrid / recorded（无现场讲解）；次要用途、场合、时间约束 |
| `artifact_afterlife` | 文件之后要支撑什么——review、approval、audit、archive、hand-off、reuse？ |

### intent → outline 义务

intent 中出现的每个目的，outline 必须满足对应义务（这是推理清单，不是分类器；保留用户给的优先级与顺序）：

| intent | outline 必须做到 |
|---|---|
| Inform | 相关事实 + 足够上下文让人知道为何重要 |
| Explain | 机制/关系/因果可追溯 |
| Persuade | 主张 + 证据 + 明显的反对/替代方案 |
| Decide | 明确决策请求 + 选项 + 标准 + 权衡 + 延迟后果 |
| Align | 共享框架 + 优先级 + 负责人 + 下一步 |
| Teach | 前置条件 + 顺序 + 演练应用/理解检查 |
| Report | 基线 + 进展 + 偏差 + 证据 + 风险 + 归属 |
| Mobilize | 紧迫性 + 能动性 + 具体行动 + 立即下一步 |
| Record/hand-off | 上下文 + 决策 + 状态 + 负责人 + 未决项 + 来源 |

## 2. 阅读模式（信息承载方式）

| 模式 | 主要载体 | 页面语法 | 粒度/节奏 | 演讲者备注 |
|---|---|---|---|---|
| `text`（读阅型） | 页面/文档 | 完整断言、短段落、表格；bullet 仅用于真正并列/有序项 | 更少更满的页，偏 dense | 补充语境，不替代页面逻辑 |
| `balanced`（商务，默认） | 页面 + 讲解者 | 每页一个主要主张 + 简洁解释/结构化证据/必要列表 | 中等粒度，混合节奏 | 解释与过渡 |
| `presentation`（汇报型） | 讲解者 + 视觉 | 每页一个主张、关键词/短句、大视觉/数字；禁段落堆叠 | 更多更疏的页，偏 anchor/breathing | 承担解释、过渡与支撑细节 |

- 依据 `audience` / `delivery_context` / `artifact_afterlife` 推导初始模式：异步 review/approval/audit/留档偏 `text`；现场投影/大型活动/课堂偏 `presentation`；混合偏 `balanced`。
- 同一来源与契约下，`presentation` 与 `text` 版本必须在页面语法、页数、文本量、视觉负担、密度、节奏、备注上有实质差异——不是只改字号。
- 用户指定页数时以用户为准（见 step2 页数规则）。

## 3. 素材偏离度与事实溯源

- **Material divergence**（内容组织自由度）：`stay close`（跟结构跟措辞，只做清晰化）→ `balanced`（按所选模式重排叙事，保留全部实质，默认）→ `free`（重组、重构、扩展、连接，可自建结构与过渡）。从用户原话读取，空白默认 balanced。
- **硬规则——无论多 free，事实必须可溯源**：对源材料之外的事实、数据、主张保持克制；对外部量化/事实主张，若有 `sources/*.facts.json` 先读它，并在相关页标注 `Fact IDs: F001, …`；自造/演示用 KPI、比率、目标、路线图数字标注 `Data class: scenario`（场景数据），永不冒充事实。
- PPTD 语境：事实来自用户文档/URL/可信检索（见 SKILL.md step2 的扩展规则）；数据图表（`Chart`）与表格（`Table`）的值要么来自源材料，要么显式标注为场景数据。

## 4. 计划纪律

- outline 与页数一旦经用户确认，即为**不可变基线**：后续执行不得静默增删/合并/拆分/重排页面；需要调整必须回到用户确认。
- 每页先写「单页主张」再写内容与视觉：放不下的内容拆页或砍掉，不压进一页。