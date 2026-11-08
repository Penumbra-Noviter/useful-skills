---
name: fetchflow
description: 目标驱动的「采集 + 逆向」编排。路由到爬取（crawl，复用 crawl4ai 引擎采集数据、必要时对抗反爬）或逆向（reverse，委托 reverse-flow-skill 分析二进制/固件/APK/脚本/协议），并在两者之间编排组合任务。触发场景：爬取/采集/抓数据/拿数据/批量获取网页内容、网站反爬被挡/绕过反爬/破解验证码/接口签名、逆向/分析样本/二进制/APK/固件/协议/校验/加密逻辑、从客户端逆向出接口再去抓取。当用户给出一个「目标」并要求取得其数据或理解其内部机制时使用。采集按方法可行性即可推进，逆向按能力以内即可推进。
---

# FetchFlow：采集 + 逆向编排

## Overview

FetchFlow 是一个薄编排层：它**不重写**任何底层能力，而是把两个成熟仓库编排起来——用 `crawl4ai`（采集引擎）做「爬取」，用 `reverse-flow`（逆向方法论 skill）做「逆向」。它的价值只在三处：**路由决策、跨模块组合、统一证据协议**。

- 爬取模块 → 委托 crawl4ai 引擎（`pip install crawl4ai`），复用其全部提取策略、反爬检测、隐匿指纹、代理、深爬。
- 逆向模块 → 委托 `reverse-flow` skill（已安装于 `~/.zcode/skills/reverse-flow`），复用其阶段流程、证据/置信度协议、工具目录、分诊脚本。
- 本 skill 只做：判断该采还是该逆向（还是组合），统一两份产出的报告格式，守住授权边界。

## 边界与 Trust（用户约定，最高优先级）

- **爬取**：方法可行性出发可以爬取的数据都尝试采集，不预设放弃。
- **逆向**：能力以内的目标都逆向，不预设拒绝。
- **红线**：不违背法律采集受法律保护的数据（不做 DoS/不压垮目标；数据使用不侵犯他人合法权利）。
- 全部边界细节、预检衔接、沙箱约定与工程安全的**唯一权威源**：`references/trust-boundaries.md`（预检执行层见 `references/authorization-check.md`）。

## Resource Guide

- 路由判定不明确时：读 `references/tool-matrix.md` 判断目标类型该走哪条线。
- 需要统一报告：读 `references/shared-evidence-protocol.md`。
- 边界细节：读 `references/trust-boundaries.md`。
- 授权预检：任何采集/逆向前，读 `references/authorization-check.md` 并跑 `scripts/check_target.py`。
- 任务级网络画像：离线样本/lab/授权目标四档分档与离线样本合法化标准，读 `references/network-profile.md`（吸收自 reverse-skill scope-contract）。
- 本机工具检测与调用：读 `references/local-toolchain.md`（唯一权威源，含检测命令、C1/C2 阶段调用映射与回退顺序）；任务启动时先检测本机工具，直接 CLI/库调用，不让用户手动开工具。
- 爬取细节：进 `modules/crawl/`（含选型与反爬回退决策）。
- 逆向细节：委托 `reverse-flow`，输出契约见 `modules/reverse/references/evidence-contract.md`。
- 逆向目标在 reverse-flow 覆盖面之外（Electron/ASAR、打包应用、.NET、网络捕获文件、IL2CPP、模型文件）：读 `modules/reverse/references/rea-toolchain.md`，用 REA 工具链取证据。

## Workflow

**Step 0 · 授权预检（自动化）**：对目标跑 `scripts/check_target.py <target>`（见 `references/authorization-check.md`）。脚本只产出两种判定：
- `ALLOW` → 继续。
- `CHECKPOINT`（登录墙 / 鉴权 / robots 禁止 / 样本缺失 / **探测失败不可观测**）→ **停下把信号摆给用户确认**，确认后继续。
- `BLOCK` 不是脚本输出：由人工红线判定触发（受法律保护数据的定性），触发即停止。
- 预检结果作为报告第一项证据。
- 任务级网络画像（见 `references/network-profile.md`）：`offline` 的本地自持样本无需再确认；其余任务选定一档 `lab_only` / `authorized_target_only` / `unrestricted_lab`，网络行为超出所选档位时停下问用户。

路由（Routing）：接到目标后，先判断意图属于哪一类：

1. **crawl（采集）**：用户要「取得某个来源的数据」——网页、接口、SPA、批量页面。→ 路由到 `modules/crawl/`。
   - 触发词：爬取、采集、抓取、拿数据、批量、导出所有、提取字段、绕过这个反爬去取数据。
2. **reverse（逆向）**：用户要「理解某个目标的内部机制」——二进制、固件、APK、脚本、加密/校验/协议。→ 委托 `reverse-flow`（逆向模块）。
   - 触发词：逆向、分析样本/二进制/APK/固件、破解、解锁、校验逻辑、签名算法、这个加密是怎么做的、反调试。
3. **chain（组合）**：意图横跨两者，或需要互相喂数据。→ 先按主目标路由，再补第二条链。
   - `crawl→reverse`：采集被反爬挡住 → 先进逆向模块分析该反爬/验证码/签名 → 带对抗方案回 crawl 重试。
   - `reverse→crawl`：逆向客户端/APK 时发现其私有 API → 用 crawl 模块直接采那个接口。
   - 触发词：抓不到、被挡、先看它怎么校验的、逆向出接口、把接口抓下来。

**路由规则**：
- 意图明显 → 直接路由，不重复确认。
- 模糊或多意图 → 最多问 1 个改变下一步的问题；问完立即按主目标进入，不空等。
- 本 Router **不亲自执行**采集或逆向的深度工作——只路由、组合、统一报告。

## Output Protocol

每个任务统一产出统一报告。**模板唯一权威源：`references/shared-evidence-protocol.md`**（此处只列字段，不重抄模板）：

- 当前阶段 / 目标 / 授权预检（ALLOW·CHECKPOINT，BLOCK 为人工判定）/ 网络画像（四档之一）/ 已路由模块
- 已验证事实（表格，含置信度）/ 关键证据 / 推断与置信度 / 风险与漏洞候选 / 边界提示 / 建议下一步

各字段语义、置信度词汇表（High/Medium/Low）与证据绑定规则见权威源文件。

## Boundaries

- 不重写 crawl4ai 的提取策略、反爬检测、隐匿逻辑。
- 不重写 reverse-flow 的阶段流程、证据协议、工具目录。
- 不采集受法律保护的数据（红线）；不做 DoS/压垮目标。
- 不把凭证、Cookie、私有绝对路径写入公开产物或代码；走环境变量。
- 组合任务到尽头要收敛——链结束后给统一报告，而不是无限展开。

## Quality Standard

- 路由正确：目标类型与所选模块匹配，不重复确认已确定事项。
- 复用到位：爬取确实用了 crawl4ai 的 API/策略，逆向确实委托了 reverse-flow，而非自行重造。
- 证据可追溯：每条结论绑 url/offset/函数/字符串/哈希/status_code。
- 红线守住：不采集受法律保护的数据；不做 DoS/压垮目标。
- 报告统一：符合 shared-evidence-protocol 结构。
