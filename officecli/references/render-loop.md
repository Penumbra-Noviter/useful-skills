# 渲染 → 目检 → 修复闭环（ZCode 环境实测，2026-09-07）

OfficeCLI 的价值核心：让 agent 看渲染结果而非猜 DOM。本机实测闭环：
`create/add → view screenshot → 目检（View）→ set 修复 → 重渲染 → 复验（View）`。

## 渲染（出 PNG）

```bash
OC="F:/tools/officecli/officecli-win-x64.exe"
export OFFICECLI_SKIP_UPDATE=1
$OC view demo.pptx screenshot --page 1 -o page-1.png   # 逐页渲染，1280x720
# 多页一起会输出单张竖向长图（--page 1-3 -o page → 3 页拼接 1280x2160），逐页渲染更利于逐页验收
```

## 目检（视觉通道）

**本环境 judge 子智能体不可用**（其底层模型不支持图像输入，对 PNG 一律返回
"Unverified"）。视觉验收降级顺序（AGENTS.md 视觉通道约定）：
judge 不可用 → 用 **View 子智能体**（Agent 工具 `subagent_type: "View"`），
传入图片绝对路径 + 逐项验收问题，其文字报告即唯一视觉依据。

## 修复

```bash
$OC set demo.pptx '/slide[1]/shape[@id=2]' --prop color=FFFFFF   # 元素用 get --depth 查路径
$OC set demo.pptx '/slide[2]/shape[@id=100001]' --prop width=26cm
$OC set demo.pptx '/slide[3]/shape[@id=100004]' --prop x=20cm --prop y=16cm
$OC view demo.pptx outline        # 结构性读回
```

## 本机实测抓到的 OfficeCLI 渲染行为（容易踩）

- **pptx 标题占位符默认主题黑**：`add --type slide --prop title=...` 的标题颜色
  继承主题（黑），设了深色 `background` 会黑字隐形 —— 必须显式
  `set .../shape[@id=2] --prop color=FFFFFF`。
- **文本溢出是静默截断，不换行不报错**：文本框窄于文字时末尾字符被裁切
  （如 "Revenue +25% YoY" 丢末尾 Y）。validate 不报，只能靠目检发现，修复=加宽。
- **越界元素不渲染也不报错**：x 超出画布（960pt≈33.9cm 宽）的形状在 PNG 里
  直接不出现。几何位置须以目检为准。
- `--page N -o x.png` 的 `-o` 不带扩展名也能写 PNG；输出多页时用逐页渲染。
