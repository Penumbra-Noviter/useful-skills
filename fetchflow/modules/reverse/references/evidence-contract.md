# 逆向产出 → 统一证据协议 映射（evidence-contract）

reverse-flow 自带成熟的证据/置信度体系（`evidence-reporting.md`）。fetchflow 不重写它，只做**字段映射**，让逆向产出能进统一的 `shared-evidence-protocol`，并能被 crawl 模块消费。

## 字段映射表

| fetchflow 共享协议 | reverse-flow 出处 | 说明 |
|---|---|---|
| 当前阶段 / Current phase | reverse-flow 的阶段（Analysis/Report/Reverse/Deep/Vuln） | 沿用 |
| 已验证事实 / Verified facts | `evidence-reporting.md` 的 Verified facts 表（ID/证据/来源/解释/置信度） | 直接沿用 |
| 关键证据 / Key evidence | offset、函数名、字符串、导入、哈希、日志 | 保留原文标识符 |
| 推断与置信度 | High/Medium/Low 词汇表 | 沿用，并给理由 |
| 风险/漏洞候选 | vulnerability-review 的候选弱项（root cause/影响面/修复） | 沿用 |
| 建议下一步 | reverse-flow 的编号下一步菜单 | 沿用 |

## 给 crawl 的 chain 线索（逆向→采集）

逆向过程中，只要发现以下**可采集线索**，单独用一段标注，方便路由回 crawl 模块：

- 发现的私有/公开 API 端点（method + URL + 参数 + 鉴权）。
- 请求签名/加密算法（含 key 来源、nonce、时间戳逻辑）。
- 需要绕过才能采集的机制（验证码、指纹校验、频控）及其对抗方案。
- 协议/数据格式（可用于直接构造请求）。

```md
chain 线索（reverse → crawl）：
- 接口: POST https://api.example.com/v2/search
- 参数: {q, page, ts, sig}
- 签名: HMAC-SHA256(secret, q|page|ts) ，secret 在客户端资源中
- 待办: 用 crawl 模块直接采该接口
```

## 规则

- 一切沿用 reverse-flow 的原始证据绑定与置信度口径，不做二次放大。
- 模糊目标（破解/解锁/绕过）先归一化为本地逆向目标，不预设拒绝。
