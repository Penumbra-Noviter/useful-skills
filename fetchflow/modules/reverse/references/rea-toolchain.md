# REA 工具链（吸收自 morluto/rea）

reverse-flow 覆盖面之外的目标类型，用 REA 取 Evidence；流程与证据输出仍走 reverse-flow。本文件只装**决策层**：何时用 REA、怎么接入、Evidence 纪律。工具细节以连接服务器实际的 `tools/list` 与已装 skill（`~/.zcode/skills/reverse-engineer-anything`）为准，上游 https://github.com/morluto/rea 。

## 源边界

- 来源：morluto/rea，MIT license；上游 https://github.com/morluto/rea ，快照 `F:\downloads\rea-main`（v6.8.0）。
- 本机已装：rea-agents 6.7.0（npm 全局 `F:\tools\npm-global`），MCP 已注册 ZCode + DSH（2026-11-09 `rea setup`），bundled skill 装于 `~/.zcode/skills/reverse-engineer-anything`（552 行 SKILL.md + 7 篇 references，工具细节的单一权威源）。
- 原生分析引擎（Ghidra/IDA/jadx-MCP/Kuna）setup 不安装，按 doctor 提示另行配环境变量；未配置时 JS/打包/捕获类目标仍全可用。
- REA 是 MCP server（`rea-agents mcp`，stdio，实测 207 工具）+ CLI（`rea-agents <command>`）。

## 分工规则（不重写）

- **reverse-flow**：阶段流程（Intake → Analysis → Report → Deep → Vuln review）、证据/置信度协议、native/android/firmware/dynamic 工具 profile。常规 PE/ELF/Mach-O、APK/DEX、固件镜像仍走 reverse-flow profile。
- **REA**：工具加速器，只接 reverse-flow 工具目录覆盖不到的目标类型（见下表）。先用 REA 拿 Evidence，再套 reverse-flow 流程与 fetchflow 统一报告。
- 不自己写 ASAR 解包 / HAR 解析 / IL2CPP metadata 解析 / 打包格式 carving——REA 已有对应工具，停手改复用。

## 接入探针（三档，按序判定）

1. **MCP 已注册**：工具列表出现 `inspect_*` / `analyze_*` / `capture_*` → 直接用，不做诊断仪式。
2. **仅 CLI**：`rea` 命令存在，或从受信目录（目标项目之外）用 `npx -y rea-agents@latest <command> <绝对路径> --json`。JS/ASAR 静态分析无需任何原生引擎：
   ```bash
   npx -y rea-agents@latest analyze-javascript-application /absolute/path/to/app --json
   ```
3. **两者都无**：回落 reverse-flow tool-catalog 对应 profile，不硬造工具；把「安装 REA 可加速」写进建议下一步。

## 覆盖面路由表（仅列 reverse-flow 目录之外）

| 目标 | REA 入口 |
|---|---|
| Electron/ASAR/JS 打包树 | `analyze_javascript_application` |
| PyInstaller / Bun --compile / ZIP·APK·IPA·MSIX·DMG 成员清点 | `open_binary` + `inspect_artifact`（大清单先 `detail: "summary"`） |
| .NET managed PE/CLI | `inspect_managed_artifact`；NativeAOT 走 Ghidra native 路线 |
| 网络捕获文件（HAR/SAZ/mitmproxy/qlog） | `inspect_web_network_capture` |
| PCAP 抓包记录 | `inspect_packet_capture` / `inspect_pcap_capture` |
| APK 签名与完整性（v1/v2/v3、证书指纹） | `inspect_apk_signature` |
| Unity IL2CPP `global-metadata.dat` | `inspect_il2cpp_metadata` |
| GGUF / safetensors 模型声明 | `inspect_model_artifact` |
| Go 构建元数据 / WASM / 固件区域提取 | `inspect_go_binary` / `inspect_wasm_artifact` / `inspect_firmware_regions` |

## Evidence 纪律（吸收自 rea evidence-workflows）

1. Evidence record 的 limitations、coverage、unknowns 完整保留进统一报告的「推断与置信度」，不删减后只报结论。
2. `source_complete` 与分页耗尽是两回事：部分 Evidence 里没搜到 ≠ 不存在。
3. 静态差异是候选不是因果；等价/缺失声明需两侧完整可比页集。
4. 进程捕获是行为证据，不是安全沙箱——「不执行未知样本」的沙箱约定仍由 reverse-flow 承担，REA 运行时工具只在样本归属已确认时使用。
5. 未决问题用 `record_unknown` 记录，不静默丢弃。

## chain 价值（reverse→crawl）

HAR Evidence 经 `inspect_analysis_view`（`kind: "environment-manifest"`）可投影出 API origins、路径模板、无值 body shape——这就是 crawl 模块要的接口画像。注意：模板与参数是推断，不复制 header/cookie/body 值；把 `completeness.excluded` 计数摆进报告，不据此宣称「没有别的 API」。

## 连接与恢复（阶梯，不重复 setup）

- 调用超时 ≠ 失败：不原样重发同一调用，先读恢复指南的期限区分。
- MCP 掉线：仅在确认可安全重试时重试一次；可能已改变目标或再次失败 → 停手让用户重启 MCP 客户端。
- 工具缺失/被拒：区分注册缺失、客户端审批、PATH 三层，各层对症修复，不无脑重跑 setup。
- 详表：已装 skill 的 `references/connection-and-recovery.md`（`~/.zcode/skills/reverse-engineer-anything/references/`）。
