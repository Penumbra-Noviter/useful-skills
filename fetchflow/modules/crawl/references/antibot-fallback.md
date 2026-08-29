# 反爬回退决策（antibot-fallback）

crawl4ai 自带反爬检测（`antibot_detector`）与隐匿能力。本表是**升级决策树**，逐层推进并留证据，不盲目堆代理。

## 检测信号（判定是否被挡）

- `result.success == False`，或 `status_code` 为 `403/503`。
- `result.error_message` 提示 blocked/challenge。
- 页面内容命中 crawl4ai `antibot_detector` 的 Tier1 结构特征（如 Cloudflare `__cf_chl_f_tk=`、Akamai `Reference #`、`_Incapsula_Resource` 等）。
- 泛化词（"Access Denied"）只在短页面（<10KB）时才算，避免误伤正常内容。

## 升级层级（按需逐层，能过就停）

| 层 | 动作 | 用到的 crawl4ai 能力 | 适用场景 |
|---|---|---|---|
| L0 | 用 `cache_mode=CacheMode.BYPASS` 重试一次 | CacheMode | 误命中缓存/偶发 |
| L1 | 隐匿指纹 | `navigator_overrider.js`（webdriver→undefined、plugins/languages 伪造）+ `UndetectedAdapter` | 基础 JS 指纹检测 |
| L2 | 代理轮换 | `RoundRobinProxyStrategy` / `proxy_config` + `proxy_rotation_strategy` | IP 频控/地域限制 |
| L3 | 会话与身份保持 | `session_id` 复用 + `BrowserProfiler` 持久身份/Cookie | 需要登录态或行为连续性 |
| L4 | 动态内容真实渲染 | `wait_for` + 完整浏览器（非 headless） | 前端校验/需真实交互 |
| L5 | 深挖反爬机制 → 转 reverse | 交给逆向模块分析验证码/签名/加密 | 纯对抗手段无效时 |

## 决策规则

1. 每层**只试一次并记录结果**（改了什么、status_code、成功与否），过即停。
2. L5 前如果纯对抗无效，**别无限试**——转 reverse 模块分析该反爬的机制，再带针对性方案回来。
3. 全程不做拉满并发的压测，不采集受法律保护的数据（红线，见 `trust-boundaries.md`）。
