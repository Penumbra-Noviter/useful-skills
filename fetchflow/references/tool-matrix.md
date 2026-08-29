# 工具/策略矩阵（tool-matrix）

按目标类型判定该走采集线、逆向线、还是组合。这是**路由决策表 + 工具并集**，不重写任何工具本身。

## 按目标类型路由

| 目标类型 | 典型特征 | 主路由 | 用到的底层能力 |
|---|---|---|---|
| 公开/授权网页、接口、SPA | 有 URL，内容在远端 | **crawl** | crawl4ai 提取策略 + 反爬回退 |
| 商品/列表/表格批量数据 | 结构重复 | **crawl** | JsonCss/Table + arun_many / deep crawl |
| 需登录/会话的目标 | 要 Cookie/身份 | **crawl** | crawl4ai 会话 + BrowserProfiler |
| 二进制（PE/ELF/Mach-O） | 本地文件 | **reverse** | reverse-flow native profile：Ghidra/radare2/DIE/capa/FLOSS/x64dbg/GDB |
| Android APK/DEX | 本地文件 | **reverse** | reverse-flow android profile：jadx/Apktool/Frida/Ghidra(native) |
| 固件 | 固件镜像 | **reverse** | reverse-flow firmware profile：Binwalk/Qiling/Unicorn |
| 脚本/文档样本 | .py/.js/ps1/doc | **reverse** | reverse-flow 静态 + 沙箱 |
| 客户端私有 API / 签名 / 加密 | 逆向产物是接口/算法 | **chain(reverse→crawl)** | 先 reverse 出协议，再 crawl 采接口 |
| 采集被反爬挡住 | crawl 层 L0-L4 无效 | **chain(crawl→reverse)** | 先 reverse 反爬机制，再带方案回 crawl |

## 采集线工具（全部来自 crawl4ai，直接复用）

- 提取：`LLMExtractionStrategy` / `JsonCssExtractionStrategy` / `JsonXPathExtractionStrategy` / `RegexExtractionStrategy` / `CosineStrategy`。
- 过滤：`BM25ContentFilter` / `PruningContentFilter` / `LLMContentFilter`。
- 反爬：`antibot_detector`（分层检测）、`UndetectedAdapter`、`navigator_overrider.js`、`RoundRobinProxyStrategy`、`BrowserProfiler`、`session_id`。
- 深爬：`BFS/DFS/BestFirstDeepCrawlStrategy` + URL scorer；`AsyncUrlSeeder`；`AdaptiveCrawler`。

## 逆向线工具（全部来自 reverse-flow，直接复用）

| profile | 工具 |
|---|---|
| native | Ghidra、radare2/Rizin、Detect It Easy、capa、FLOSS、YARA、x64dbg、GDB+pwndbg/GEF、Capstone、LIEF |
| android | jadx、Apktool、Frida、Ghidra(native)、adb |
| firmware | Binwalk、Qiling/Unicorn、YARA、strings |
| dynamic | x64dbg、WinDbg、GDB、lldb、Frida、Procmon/strace/tcpdump/Wireshark |
| vulnerability | AFL++、sanitizers、Ghidra、debuggers |
| 脚本/文档 | 对应运行时静态 + 沙箱 |

## 选型规则

1. 先按目标类型走路由表（采集 vs 逆向 vs 组合）。
2. 采集优先走 crawl4ai 确定性策略，反爬按 `antibot-fallback.md` 逐层升。
3. 逆向按 reverse-flow 的 profile 选最小可用工具链（先用手头已有的）。
4. 纯对抗无效且能力所及 → 转组合链。

## 不重复造轮子的检查

若你在做以下任何事，停手并改回复用：
- 自己写 HTML 解析器 / 反爬检测正则 / 隐匿 JS（→ 用 crawl4ai）。
- 自己编二进制分诊 / 反调试绕过 / 工具清单（→ 用 reverse-flow）。
- 自己的报告格式发明一套新的（→ 用 shared-evidence-protocol）。
