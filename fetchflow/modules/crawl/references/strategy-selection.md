# 提取策略选型（strategy-selection）

这是**选型决策表**，不是实现。实际提取全交给 crawl4ai 的 `ExtractionStrategy`。原则：**用确定性策略优先，只有结构复杂或语义歧义才上 LLM（慢且贵）**。

## 按目标形态选策略

| 目标形态 | 识别特征 | 推荐策略 | 关键配置 |
|---|---|---|---|
| 商品/重复卡片页 | 多行结构一致，如商品、列表项 | `JsonCssExtractionStrategy` + 手写 schema | schema 含 `baseSelector`（容器选择器）+ `fields`（字段选择器列表） |
| 表格/数据表 | `<table>` 语义清晰 | `DefaultTableExtraction` / `TableExtractionStrategy` | 无 |
| 纯文本/文章 | 正文散文，需清洗噪声 | 默认 markdown + `BM25ContentFilter`（`query` 按主题） | `content_filter` 用 BM25 |
| SPA/动态渲染 | 内容靠 JS 异步加载 | 任意策略 + `wait_for`（CSS/JS 条件） | `wait_for` 等元素出现，必要时 `wait_for_images` |
| 半结构化/歧义 | 无固定模板、字段不统一、需语义理解 | `LLMExtractionStrategy`（`llm_config` + `extraction_type="schema"`） | 给 schema + prompt，设 `word_count_threshold` |
| 接口/JSON 型页面 | 页面即数据、返回 JSON | 直接用 `JsonCssExtractionStrategy` 取 script 内嵌，或抓原始响应 | 必要时看 `network_requests` 取 XHR |
| 阴影 DOM / iframe | 内容在 shadow root 或 iframe | crawl4ai 的 shadow_dom / iframe 处理 | 启用对应 js_snippet / iframe 提取 |
| 批量/整站 | 大量 URL | `arun_many` 或 deep crawl | `deep_crawling` 的 BFS/DFS + URL scorer |

## chunking 选择（配合 LLM 提取时）

- 主题分块：`TopicChunking`（内容长、主题清晰）。
- 正则/句子分块：`RegexChunking`（默认，快）。
- 只需精确字段：跳过 LLM 分块，直接 CSS/XPath。

## 决策规则

1. 有固定模板 → CSS/XPath（确定性，免费）。
2. 无模板但结构平坦 → Regex + 表提取。
3. 语义歧义 / 字段不定 → 才上 LLM，且先试小样本验证 schema。
4. 任何选择都记录：**为何选它、命中多少字段、失败信号是什么**。
