# 示例：crawl 路由

## 触发 prompt

> 使用 fetchflow：爬取 https://example-shop.com/products 的所有商品价格，字段含 名称、价格、库存。

## 期望路由

`crawl` → `modules/crawl/`。目标形态 = 重复商品卡片（静态/半静态 HTML）。

## 期望执行

1. 判目标类型 → 商品/重复卡片页 → 选 `JsonCssExtractionStrategy` + schema。
2. 建 case：`python scripts/make_case.py --case products --goal "采集商品价格" --out ./work`。
3. 抓取：`python scripts/run_crawl.py https://example-shop.com/products --extraction jsoncss --schema '{"baseSelector":".product","fields":[{"name":"name","selector":".name","type":"text"},{"name":"price","selector":".price","type":"text"},{"name":"stock","selector":".stock","type":"text"}]}'`。
4. 检查结果：`success`、`status_code`、提取字段数。
5. 若 403/blocked → 走 `antibot-fallback.md`（BYPASS → 隐匿 → 代理 → 会话），记录每层。
6. 统一报告。

## 期望输出（节选）

```md
当前阶段: crawl（提取）
目标: https://example-shop.com/products
已路由模块: crawl
已验证事实: status_code=200；JsonCss 提取到 45 个商品（名称/价格/库存），success=True
关键证据: 提取策略 JsonCssExtractionStrategy，命中 45 条；缓存 enabled
推断与置信度: High（直接观察且可复现）
建议下一步: 1) 深爬分页/更多列表；2) 导出为 JSON/CSV；3) 若需语义字段改 LLM
```

## 回归检查

- 是否确实用了 crawl4ai 的提取策略（而非手写解析器）？是。
- 是否对目标做了授权判断？是（`trust-boundaries.md`）。
- 报告是否绑定 status_code + 提取策略 + 命中量？是。
