# 自动化授权预检（authorization-check）

采集/逆向开始前，对目标做**可观测信号**的机械预检，作为法律红线的自动化执行层。核心理念：**能判的机械判，判不了的升 CHECKPOINT 交给用户**——不静默放行，也不机械误伤。

执行方式：`python scripts/check_target.py <target>`。

## 判定输出

| 结果 | 含义 | 后续 |
|---|---|---|
| `ALLOW` | 无可观测风险信号，目标属公开/用户自持 | 进入 crawl / reverse 执行 |
| `CHECKPOINT` | 命中一个或多个风险信号（登录墙、robots 禁止、样本缺失等） | **停下询问用户**，由其确认后再继续 |
| `BLOCK` | 明确红线（受法律保护且明显不可采） | 停止，不执行 |

## 采集侧可观测信号

对 URL 目标，自动检查：

1. **robots.txt**：抓 `{origin}/robots.txt`，若目标路径被 `User-agent: *` + `Disallow:` 覆盖 → 信号（方法可行仍可采，但记录并提示）。
2. **登录墙 / 受保护数据**：无凭证 GET 目标，若返回 `401/403`，或重定向到 `login` 类地址 → **强信号**（非公开内容），升 `CHECKPOINT`。
   - 这是"受法律保护数据"最可自动化的可观测代理：**需要登录才能看的内容**通常属于受保护范围。
3. 其余（公开页面、无鉴权、robots 放行）→ `ALLOW`。

## 逆向侧信号

- **本地文件**：目标为本地路径且存在 → 用户自持样本，`ALLOW`；路径不存在 → `CHECKPOINT`（疑似笔误/需用户给路径）。
- 远程下载的可执行文件/固件：提示来源（用户提供 vs 他处下载），若来源不明 → `CHECKPOINT`。

## 判定原则

- 只做**可观测信号**的机械判定，不替用户做法律定性。
- 凡无法确定是否受保护（登录墙、鉴权重定向、来源不明）→ 一律 `CHECKPOINT`，不默认放行。
- 用户确认后仍按"方法可行即可采 / 能力以内即做"推进；预检的职责是**在触碰红线前把它摆到用户面前**，不是设死门槛。

## 结果进证据协议

预检结果作为报告第一项证据写入 `shared-evidence-protocol`：

```md
授权预检 / Authorization pre-flight: ALLOW | CHECKPOINT(<signals>) | BLOCK(<reason>)
信号明细 / Signals: robots=…, auth_required=…, provenance=…
```
