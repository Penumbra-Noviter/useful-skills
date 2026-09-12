---
name: distill-lesson
description: 按 AGENTS.md 3.5 知识库闭环约定，把本次会话的经验教训蒸馏为原子笔记写入 Obsidian 知识库。触发词：沉淀、沉淀经验、总结教训、复盘、蒸馏经验；阶段完成有教训时也应主动调用。禁止把经验本体写入 zcode memory 等其他记忆系统。
---

# 经验蒸馏（Distill Lesson）

执行 AGENTS.md「3.5 知识库闭环」的蒸馏（写）流程。知识库根目录：`D:\Desktop\knowledge base\demo`。

## 步骤

1. **读模板**：读取 `模板/经验模板.md`，严格按其 frontmatter 字段与章节结构写笔记。

2. **盘点教训**：回顾本次会话，列出可迁移的教训。判定标准：根因非显然、换项目仍可能踩、有防复发措施。**无教训则明确回复「无教训，不写」并结束，不制造噪音。**

3. **查重**：在 `经验/` 目录按关键词搜索（文件名 + grep 内容）。已有同根因条目 → 更新旧条目（补充新证据/新场景），不新建。

4. **写笔记**：每条教训一个文件，写入 `经验/<教训标题>.md`：
   - frontmatter 必填：`summary`（≤50 字，预检扫描只读此行）、`provenance`（来源可追溯：会话 id / commit / DEV_LOG 条目）、`project`、`date`、`status`（已验证 `verified`，未复现验证 `candidate`）
   - frontmatter 可选：`agents_md_feedback`——核对「本条经验与全局 AGENTS.md 哪条规则冲突/印证」（冲突 = 生成宪法清理候选，随蒸馏汇报提出；印证 = 宪法吸收门禁的观察点；无则留空，不制造噪音）
   - 章节按模板：症状 / 根因 / 代价 / 教训 / 防复发 / 关联（wikilink 到 `经验/` 已有相关条目）
   - 一条笔记一个教训（原子性），不合并多个教训

5. **降级 memory**：若 zcode 会话 memory（`~/.zcode/cli/memories/`）已有相关条目，将其改写为一句话摘要 + 指向知识库笔记的链接，不保留经验本体（单向权威：细节以知识库为准）。

6. **汇报**：列出写入的笔记路径与每条 summary；如有查重合并或 memory 降级动作，一并说明。

## 红线

- 经验本体不得写入 `~/.zcode/cli/memories/`——memory 只留指针
- 无教训不写；宁缺毋滥
- `provenance` 缺来源的笔记不落盘
