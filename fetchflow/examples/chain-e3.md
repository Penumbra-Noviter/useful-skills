# 示例：chain 路由 — 组合链 E3 验证记录

## 触发 prompt

> 使用 fetchflow：https://aigirlfriendstudio.com/zh?ref_id=… 会挡爬取，逆向它的反爬再帮我抓下来。

## 期望路由

`chain(crawl → reverse → crawl)`：crawl 首采被挡 → reverse 定位阻挡层 → crawl 带策略重试。

## E3 实测结果（2026-08-28，Live）

授权预检：`check_target.py` 返回 `CHECKPOINT`（robots 禁止 `/zh`）→ **用户显式确认授权**后继续。

| 阶段 | 动作 | 证据 |
|---|---|---|
| crawl 首采 | `run_crawl.py --extraction markdown` | status=200, markdown_len=**245**（只有加载壳 + 标题"AI风月"） |
| reverse 定位 | 扫 shell HTML + 网络主机 | **Next.js/Turbopack SPA**，真实数据由客户端渲染；主机 `static.catai.wiki` / `awsprod.aiero.cc`；无 Cloudflare/captcha 标记 → 阻挡=动态渲染，非 WAF |
| crawl 重试 | `wait_for="!img[src*=fyloading] && body.innerText.length>300"` | markdown_len **245→29467**，渲染出真实陪伴卡片 |

**结论**：阻挡层是 **SPA 动态内容加载**（非 WAF/验证码）。方法学"绕过"= 等待 JS 渲染（标准 SPA 采集手法），非规避访问控制。产物 `shell.html`、`aigs_success.md`、`combo-chain-e3.md` 存于 case `aigs/`。

## 回归检查

- 组合链三态是否真实走通（被挡→逆向→重试成功）？**是**（245→29467）。
- 逆向定位是否有证据（SPA 判定、主机、无 WAF 标记）？**是**。
- 授权预检 CHECKPOINT 是否经用户确认？**是**。
- 是否规避访问控制拿受保护数据？**否**（公开页面 SPA 渲染）。
