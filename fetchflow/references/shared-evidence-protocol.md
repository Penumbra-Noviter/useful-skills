# 统一证据协议（shared-evidence-protocol）

fetchflow 两个模块的共同输出语言。核心原则：**事实与推断分离，每条结论绑定证据，置信度分级**。本协议是"格式契约"，不是实现——采集侧由 crawl4ai 产出原始证据，逆向侧沿用 reverse-flow 的证据体系，这里统一它们的"壳"。

## 报告模板

```md
# FetchFlow 报告

## 当前阶段 / Current phase
（Analysis / Report / Reverse / Deep / Vuln，或采集流程的哪一步）

## 目标 / Target
（url / 文件路径 / 样本哈希 / 目标描述）

## 授权预检 / Authorization pre-flight
（ALLOW | CHECKPOINT(<signals>) | BLOCK(<reason>)；由 `scripts/check_target.py` 产出，见 `references/authorization-check.md`）

## 已路由模块 / Routed module
crawl | reverse | chain(→)

## 已验证事实 / Verified facts
| ID | 证据 | 来源/位置 | 解释 | 置信度 |
|---|---|---|---|---|
| F1 | status_code=200, 提取到 12 个产品字段 | https://…/products, JsonCss | 商品页抓取成功 | High |

## 关键证据 / Key evidence
（采集：url / status_code / 提取策略 / 命中量；逆向：offset / 函数名 / 字符串 / 哈希）

## 推断与置信度 / Inference and confidence
（High：直接观察到；Medium：多静态指示；Low：有限证据推测。每条给一句理由）

## 风险/漏洞候选 / Risk or vulnerability candidates
（逆向时才有；含 root cause / 影响面 / 修复）

## 边界提示 / Risk or boundary note
（授权/合规相关，若触及红线明确标注）

## 建议下一步 / Suggested next steps
1. ...
2. ...
```

## 置信度词汇表

- **High**：在代码或运行时直接观察且可复现。
- **Medium**：多个静态指示支持但未完整执行/验证。
- **Low**：有限证据的合理假设，未验证。

## 证据绑定规则

- 用稳定标识符：url、offset、函数名、字符串、哈希、status_code、命令输出、日志片段。
- 原始日志/输出留在 case 工作区，报告里只保留相关行 + 摘要。
- 未知项明确列出，不脑补。

## 适用范围

- 纯采集任务：facts 以 status_code/提取结果/反爬回退记录为主。
- 纯逆向任务：facts 以 reverse-flow 证据表为准。
- chain 任务：两段证据都保留，且标注交接点。
