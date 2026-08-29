---
name: fetchflow-crawl
description: fetchflow 的采集模块。委托 crawl4ai 引擎采集网页/接口/SPA/批量页面数据，必要时对抗反爬。当 fetchflow 路由到 crawl，或用户要「爬取/采集/抓取/拿数据/提取字段/绕过反爬取数据」时使用。复用 crawl4ai，不重写其能力。
---

# Crawl 模块（委托 crawl4ai）

## Overview

本模块是 crawl4ai 引擎的**薄包装**：只做「选型决策 + 反爬回退决策 + 统一输出」，所有实际抓取、解析、提取、隐匿都由 crawl4ai 完成。绝不重写 crawl4ai 已有能力。

依赖：`pip install -U crawl4ai && crawl4ai-setup`。核心 API（已按实际源码核对）：
- `AsyncWebCrawler().arun(url, config=CrawlerRunConfig(...))` → `CrawlResultContainer`（可迭代；`__getattr__` 转发到首个结果）。
- `CrawlResult` 字段：`success`、`markdown`、`extracted_content`、`status_code`、`error_message`、`metadata`、`links`、`media`、`tables`、`cleaned_html`、`response_headers`。
- `CrawlerRunConfig(extraction_strategy=..., chunking_strategy=..., cache_mode=CacheMode.ENABLED, session_id=..., proxy_config=..., page_timeout=..., wait_for=..., css_selector=..., verbose=...)`。
- `CacheMode`：`ENABLED / DISABLED / READ_ONLY / WRITE_ONLY / BYPASS`。
- `arun_many(urls, config=...)` 批量。
- 提取策略：`LLMExtractionStrategy / JsonCssExtractionStrategy / JsonXPathExtractionStrategy / RegexExtractionStrategy / CosineStrategy`。

## Workflow

0. **授权预检**：跑 `../scripts/check_target.py <url>`，得 `ALLOW`/`CHECKPOINT`/`BLOCK`（见 `references/authorization-check.md`）；`CHECKPOINT` 先请用户确认，`BLOCK` 停止。
1. **判目标类型**：读 `references/strategy-selection.md`，按目标形态（静态 HTML / SPA / 接口 / 批量 / 表格）选定 `extraction_strategy` + 是否 LLM + 是否需 `wait_for`。
2. **抓取**：用 `AsyncWebCrawler().arun(...)`（或 `arun_many`）执行。可直接调用 `scripts/run_crawl.py`，或按需直接写 crawl4ai 调用。
3. **检查结果**：
   - `result.success` 为 False，或 `status_code` 为 403/503，或 `error_message` 提示 blocked → **反爬拦截**，进第 4 步。
   - 成功 → 取 `result.extracted_content`（结构化）或 `result.markdown`（文本），进第 5 步。
4. **反爬回退**：读 `references/antibot-fallback.md`，按决策树逐层升级（BYPASS 重试 → 隐匿/undetected → 代理轮换 → 会话/身份保持），每层记录证据。
5. **统一输出**：按 `references/shared-evidence-protocol.md` 产出报告，证据绑定 url / status_code / 提取结果。

## Output Protocol

遵循共享协议，其中爬取特有的关键证据字段：
- `url`、`status_code`、`success`
- 提取策略名（如 `JsonCssExtractionStrategy`）+ 命中字段数
- 反爬回退层级（如有）与每层结果
- 缓存/代理/会话等生效配置

## Boundaries

- 不重写 crawl4ai 的解析/提取/隐匿/反爬检测——只选型和编排。
- 不做拉满并发的压测式采集，注意频控与礼貌；不采集受法律保护的数据（红线，见 `references/trust-boundaries.md`）。

## Quality Standard

- 选型与目标形态匹配（SPA 用 wait_for，商品页用 JsonCss，复杂/歧义才上 LLM）。
- 反爬回退按层推进并留证据，不盲目堆代理。
- 结果可追溯：status_code + 提取策略 + 命中量都能对上。
