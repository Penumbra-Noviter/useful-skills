> 来源 / Source: [NationalSecurityAgency/ghidra](https://github.com/NationalSecurityAgency/ghidra) Apache-2.0（GitHub）
> 吸收 / Vendored: 2026-09-22 · 依据本地参考 clone 提炼（`F:\tools\src\ghidra`，稀疏检出，HEAD `d6192cb`）
> 本机运行工具: `F:\tools\apps\ghidra`（check-tools.py 已验证 `analyzeHeadless` / `ghidraRun` 可用）
> 权威详情见 `F:\tools\src\ghidra\GhidraDocs\GhidraClass\Intermediate\HeadlessAnalyzer.html` 与安装目录 `support/analyzeHeadlessREADME.html`

# Ghidra 实践速查

> 聚焦两条主线：**headless 批量工作流**（静态自动分析主入口）与**版本比对 / Version Tracking**（补丁 diff、两版本找差异）。脚本默认 Java，运行期支持 Jython `.py`。官方示例脚本在 `ghidra_scripts/` 目录（Base/Decompiler/VersionTracking 各 Features 下均有）。

---

## 一、Headless 批量工作流（analyzeHeadless）

### 命令骨架

```
analyzeHeadless <项目目录> <项目名>[/<子目录>]
    [[-import <文件|目录>+ ] | [-process [<项目内文件>]]]
    [-preScript <脚本名> [<参数>]*]    [-postScript <脚本名> [<参数>]*]
    [-scriptPath "<路径1>;<路径2>..."]
    [-log <日志>] [-scriptlog <脚本日志>]
    [-overwrite] [-recursive [<深度>]] [-readOnly] [-deleteProject]
    [-noanalysis] [-analysisTimeoutPerFile <秒>] [-max-cpu <核心数>]
    [-processor <languageID>] [-cspec <compilerSpecID>] [-loader <loader名>]
```

- **项目目录必须已存在**，不会自动创建。
- `-import` 与 `-process` 二选一，不能同时出现。
  - `-import`：导入新文件（支持目录/通配符/重复 -import），导入后自动分析。
  - `-process`：对项目里已有文件跑脚本/分析；文件名只给文件名不带路径（路径放项目名后的 `/folder`），通配符需单引号包裹 `'a*.exe'`，`-process` 只能出现一次。
- **preScript 在分析前跑，postScript 在分析后跑**；多个脚本按命令行顺序执行；分析超时后可用 postScript 检测（`getState()` 存在超时标志）。

### 常用组合

```bash
# 1) 单目录批量导入 + 自动分析 + 后处理脚本，分析完删项目（一次性任务）
analyzeHeadless C:/tmp/reproj Repro -import C:/samples/ -recursive \
    -postScript ExportFunctions.java -scriptlog C:/tmp/funcs.log -deleteProject

# 2) 对已有项目全部文件跑脚本（不带文件参数 = 项目内全部）
analyzeHeadless C:/tmp/reproj Repro -process -postScript PrintScript

# 3) 覆盖冲突文件 + 限制分析超时
analyzeHeadless C:/tmp/reproj Repro -import a.exe b.exe -overwrite -analysisTimeoutPerFile 300

# 4) 只导入+分析，不保留项目（-readOnly 模式改动不落盘）
analyzeHeadless C:/tmp/reproj Repro -import C:/samples/ -readOnly -deleteProject
```

### 关键开关

| 参数 | 行为 |
|---|---|
| `-overwrite` | 覆盖同名已导入文件；缺省时跳过冲突 |
| `-recursive` | 递归目录；可选深度值深挖 zip/tar/.a 等容器 |
| `-readOnly` | 分析/脚本改动不保存；批量只读扫描用 |
| `-deleteProject` | 分析完删除项目（仅限本次 -import 新建的项目，已有项目永不删） |
| `-noanalysis` | 关掉自动分析，只跑脚本（脚本自行分析常配） |
| `-analysisTimeoutPerFile <秒>` | 单文件分析超时，超时跳过继续 |
| `-max-cpu <n>` | 限核数，控制并发 |
| `-processor` / `-cspec` | 强制语言/编译器规范，未识别文件头时兜底 |

### Headless 脚本要点

- 同一脚本可同时兼容 GUI 与 headless：`if (isRunningHeadless())` 分支。
- 批量判断「哪些二进制值得留」：脚本里 `currentProgram.setTemporary(true)` 阻止该导入被保存，其余照常入库。
- 脚本间可传递 Selection（前一个脚本的选择带到下一个，直到被改/清空）。
- 分析选项可在脚本里动态改：`setAnalysisOption(currentProgram, "Stack", "false")`、`setAnalysisOptions(program, map)`、`resetAllAnalysisOptions(program)`、`getCurrentAnalysisOptionsAndValues(program)`。
- 控制后续流程（脚本内设 continuation）：`CONTINUE`（默认）/ `CONTINUE_THEN_DELETE`（不保存）/ `ABORT`（停下保存）/ `ABORT_AND_DELETE`，通过 `getState().addEnvironmentVar(SCRIPT_SET_CONTINUATION_STATUS, HeadlessContinuationOption.ABORT)`。
- 批量导入时点号开头的文件（`.hidden.exe`）被忽略，需显式指名导入。
- 项目/库的公共 API 别用 `setServerCredentials`（headless 已自动处理，两者冲突）。

---

## 二、版本比对 / Version Tracking（VT）

适用场景：同一程序两个版本找差异函数（补丁 diff）、把旧版注释/命名迁移到新版、核对固件更新点。

### 概念

- **Source 程序**（旧版/已知版）与 **Destination 程序**（新版/目标）做匹配。
- **Correlator**（相关器）= 匹配算法；**Match** = 一对函数/数据的匹配；**Markup** = 把 source 的分析结果（命名、注释、结构体）搬运到 destination。
- **Auto Version Tracking（AutoVT）** 按固定顺序串行跑相关器，自动接受可信匹配并应用 markup，保守优先（官方明示「不保证全对，只求省时 + 不出错」）。

### AutoVT 相关器顺序（全部默认开启）

1. Exact Symbol Name（符号名精确）
2. Exact Data（数据）
3. Exact Function Bytes（函数字节）
4. Exact Function Instructions（指令）
5. Exact Function Mnemonics（助记符）
6. Duplicate Function Instructions（重复函数指令）
7. Reference Correlators：Data Ref / Function Ref / Combined（按前 6 步产出的匹配类型择一）

隐含匹配（Implied Matches）在存在被接受的匹配时创建，投票数 ≥ `Minimum Votes Needed`(默认2) 且冲突 ≤ `Maximum Conflicts Allowed`(默认0) 才应用。宽松下限可调：`Reference Correlators Minimum Score` 默认 9.5、`Minimum Confidence` 默认 10.0。

### Headless 下跑 AutoVT（官方示例，非共享项目）

```
<ghidra>/support/analyzeHeadless.bat c:/MyGhidraProjectFolder \
    MyProjectName/OptionalFolderContainingDestProgram -process DestinationProgram.exe \
    -postScript MyOptionsSetupScript -postScript AutoVersionTrackingScript.java \
    "/FolderContainingSession" "MySessionName" "/OptionalFolderContainingSourceProgram/SourceProgram.exe"
```

要点：
- destination 程序用 `-process` 指定；source 程序路径是 AutoVersionTrackingScript 的第 3 个参数。
- 第一个参数 = 存 session 的文件夹，第二个 = session 名（新 session，不能复用已有）。
- 选项设置脚本（`SetAutoVersionTrackingOptionsScript` 模板）在 AutoVT 脚本之前的 `-postScript` 执行；不写则用脚本默认值。
- destination 若未分析会自动分析（不带 `-noanalysis` 时）。

### 手工建 session 的示例脚本

- `CreateAppliedExactMatchingSessionScript`：建 session → 跑若干 correlator → 保存 session（改参数可控制跑哪些相关器）。
- `FindChangedFunctionsScript`：两版本程序间找「匹配/不匹配」的函数对，直接适合补丁 diff 报告；基于 `AbstractGhidraVersionTrackingScript`（headless 可跑，prompt 选程序只在 GUI 模式）。
- `OpenVersionTrackingSessionScript`：打开既有 session 继续处理。

### 与 Diaphora/BinDiff 的取舍

- **好用优先、单机快速**：Ghidra AutoVT（本机已装，零额外部署）。
- **批处理脚本化**：Ghidra headless + AutoVersionTrackingScript（上面这条）。
- **规模/去重敏感**：Diaphora/BinDiff（需额外装，比对更像与更细的 diff 报告）——需要时装。

---

## 三、参考源码位置（本机）

| 用途 | 路径 |
|---|---|
| 运行工具（已装） | `F:\tools\apps\ghidra`（`analyzeHeadless.bat` 在 `support/`） |
| 参考 clone（稀疏检出） | `F:\tools\src\ghidra`：`GhidraDocs/` 文档、`Ghidra/Features/*/ghidra_scripts/` 官方示例、`Ghidra/Features/VersionTracking/` VT 源码与帮助文档 |
| 需要追加目录时 | `git -C F:/tools/src/ghidra sparse-checkout add <path>` |

脚本示例索引：`Ghidra/Features/Base/ghidra_scripts/`（通用）、`Ghidra/Features/Decompiler/ghidra_scripts/`（反编译器专项，如 `DecompilerStackProblemsFinderScript`）、`Ghidra/Features/VersionTracking/ghidra_scripts/`（VT 专项）。