# Native Depth Checklist（原生深度，可编辑优先）

> 来源：蒸馏自 [hugohe3/ppt-master](https://github.com/hugohe3/ppt-master)（MIT，© 2025-2026 Hugo He）README 产品定位与 `skills/ppt-master/references/native-shape-authoring.md` 的实现哲学，改写为 to-ppt 的 PPTD 语境。核心主张：**交付的是真 PowerPoint——原生形状、数据图表、表格，不是扁平的文本块，也不是模板填空。**

## 为什么「可编辑」只是底线

- 一个优质 PPTX 的判据：接收者在 PowerPoint/WPS 里能**继续编辑**——改文字、改数据、拖形状、换图表类型，而不是只能整页替换。
- 扁平化 = 把每页内容画成一张图（文本块 + 色块）：看着像 PPT，动不了。禁止默认走这条路。
- 模板填空 = 只换文字不设计论证：内容与视觉脱节。禁止默认走这条路。

## 生成前检查（对照 step3 各分支）

- [ ] **论证先在 outline 成型**：先生成「六问沟通契约 + 大纲」（`reference/planning-communication-contract.md`），确认后再进视觉；不要先选模板再硬塞内容。
- [ ] **单页单主张**：每页一个可写出的核心主张；视觉服务于它，不装饰它。
- [ ] **数据用真图表，不用手画线**：数值对比/趋势/占比 → PPTD `Chart`（参考 `reference/pptd.md` Chart 结构），图表值可改、可换类型。
- [ ] **结构化内容用真表格**：对照矩阵、明细、排期 → PPTD `Table`（`TableStyleConfig`），带行/列样式，而非手工排列文本。
- [ ] **形状语义化**：连接用 connector/箭头（可调路由），分组用容器，层次用层级关系，而不是到处矩形+文本框。
- [ ] **数据有出处**：外部事实/数字标注来源（Fact ID 或来源名）；自造数字标 `Data class: scenario`。
- [ ] **文案真实**：不写「此处替换为…」「Lorem ipsum」类占位演示文字（除非用户要求占位）。

## 交付验证（与 Blank-PPTX rebuild safeguard 同一道门）

生成 PPTX 后，除 `scripts/export_pptx.py` 自身的结构/完整性检查外：

- [ ] 用 PowerPoint/WPS 实际打开验证（关键交付物必须），不满足「自定义 reader 能解析」即通过。
- [ ] 抽查 2-3 个关键页：选中元素确认是**可编辑对象**（文本框/形状/图表/表格），不是整页图片。
- [ ] 数据图表选中后能打开编辑数据表；表格能逐格编辑。
- [ ] 文字无溢出、无被遮挡；缩略图/渲染图与实际打开一致。

## 与 PPTD 能力边界对齐

- PPTD DSL 支持：Table 样式体系、Chart 系列/数据标签/图例、Theme 令牌、基础形状/连接器、动画、演讲者备注。
- PPTD 不承诺的部分（如复杂 SmartArt 语义、精确 master 继承）：不要声称；用户需要时提示局限，或建议用 officecli 的 Blank-PPTX 路线重建（见 SKILL.md「Blank-PPTX rebuild safeguard」）。