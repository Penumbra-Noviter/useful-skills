# 示例：chain 路由（组合）

两条方向：`crawl→reverse`（采集被反爬挡 → 逆向反爬）和 `reverse→crawl`（逆向出接口 → 采集）。

## 场景 A：crawl → reverse

### 触发 prompt

> 使用 fetchflow：https://api-target.com/search 一直用 Cloudflare 反爬挡我，抓不到。先看看它的反爬/签名是怎么做的，再想办法把数据抓下来。

### 期望执行

1. 主路由 `crawl`，进 `antibot-fallback.md` 逐层试（BYPASS → 隐匿 → 代理 → 会话）。
2. 纯对抗无效 → 转 `reverse` 委托 reverse-flow：分析返回的 challenge 页/客户端脚本，定位验证码/签名/指纹校验机制。
3. 得出对抗方案（如：复现签名算法、确认需要的 header/顺序、或识别某字段来源）。
4. 带方案回 `crawl`：用 `run_crawl.py` 的 `--session`/`--proxy`/自定义配置重试，或直接构造请求。
5. 统一报告两段证据 + 交接点。

### 期望输出（节选）

```md
已路由模块: chain(crawl→reverse)
已验证事实: crawl L0-L4 均 403；reverse 定位到 __cf_chl_f_tk= 的 Cloudflare challenge，签名字段由页面 JS 生成
关键证据: crawl status_code=403；reverse 命中挑战脚本 /cdn-cgi/challenge-platform/…
推断与置信度: Medium（静态识别，未完整复现）
建议下一步: 1) 复现 challenge token 生成；2) 用 headful+隐匿重试；3) 评估该接口是否为授权可采目标
```

## 场景 B：reverse → crawl

### 触发 prompt

> 使用 fetchflow：逆向这个 APK，找到它调用的私有搜索接口，然后把数据抓下来。

### 期望执行

1. 主路由 `reverse`，委托 reverse-flow：jadx/Apktool 反编译，定位网络层，找出 API 端点、参数、签名算法。
2. 产出 chain 线索（`evidence-contract.md` 的 chain 段）：method + URL + 参数 + 鉴权/签名。
3. 转 `crawl`：用 `run_crawl.py`（或直接构造请求）采该接口。
4. 统一报告：逆向证据 + 采集结果。

### 期望输出（节选）

```md
chain 线索（reverse → crawl）:
- 接口: POST https://api.example.com/v2/search
- 参数: {q, page, ts, sig}; 签名 HMAC-SHA256(secret, q|page|ts)，secret 在客户端资源
已路由模块: chain(reverse→crawl)
已验证事实: reverse 在 DEX 中定位到上述端点与签名；crawl 带签名请求 status_code=200，返回 20 条结果
关键证据: DEX 字符串 "v2/search" + secret 常量；crawl status_code=200
边界提示: 该接口/secret 涉及的数据是否受法律保护——已按 trust-boundaries.md 红线判定
```

## 回归检查

- 两条链的交接点是否明确标注（`chain 线索`段）？是。
- 是否避免无限对抗（L5 后转 reverse，不是死磕代理）？是。
- 红线判定是否落在最终输出？是。
