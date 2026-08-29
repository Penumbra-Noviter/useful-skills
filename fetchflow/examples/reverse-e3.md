# 示例：reverse 路由 — E3 验证记录

## 触发 prompt

> 使用 fetchflow：逆向这个样本 `D:\Desktop\Craft\model-fingerprint\dist\ModelFingerprint.exe`，走通分诊到初始报告。

## 期望路由

`reverse` → 委托 `reverse-flow`（`~/.zcode/skills/reverse-flow`）。

## E3 实测结果（2026-08-28）

委托链三步全部真实跑通（Deterministic，静态分析，未执行样本）：

```text
# 1. 建 case（fetchflow 脚本）
python scripts/make_case.py --case mfp --goal "..." --out <work>
   → case 已创建: <work>/mfp

# 2. reverse-flow 分诊
python <reverse-flow>/scripts/triage_artifact.py <样本> --out <work>/mfp/triage
   → 产出 ModelFingerprint.exe.triage.{json,md}

# 3. reverse-flow 初始报告
python <reverse-flow>/scripts/report_from_triage.py <work>/mfp/triage/*.json --out <work>/mfp/reports/initial-report.md
   → 产出 initial-report.md
```

**样本静态结论**：Windows PE，50,691,456 字节，SHA-256 `3d690afd…106f85`；PyInstaller 打包的 **PySide6/Qt6 桌面 GUI 应用**（入口脚本 `gui_app`，捆绑 Qt6 全栈 + `MANUAL.md`，运行时钩子含 cryptography-openssl、multiprocessing）；前缀熵 7.992（PYZ 压缩）。

**关键证据**：`pyi-archive_viewer -l` 列出 PKG/CArchive 内容（`gui_app`、`PySide6\Qt6*.dll`、`pyi_rth_*`）；完整报告见 `fetchflow-e3/mfp/reports/fetchflow-e3-report.md`。

## 回归检查

- 是否委托了 reverse-flow 阶段/证据/工具（而非自行重造）？**是**（triage_artifact + report_from_triage 真实调用）。
- 事实与推断分离、结论绑 hash/尺寸/归档结构？**是**。
- 静态分析不执行样本、操作副本？**是**。
