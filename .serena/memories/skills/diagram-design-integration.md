# diagram-design skill 整合（2026-08-13）

用户交付 `D:\Desktop\downloads\diagram-design-main`（Cathryn Lavery 的 diagram-design v2.2，MIT），要求整合进 skills 仓库、合乎规范。

## 整合决策（按 domain-integration.md 协议）
- diagram-design 通过 zine test（自有 substrate=editorial 设计系统/style-guide.md、自有触发词=27 图型、自有 pre-flight=style-guide gate+§9 taste gate、自有输出契约=独立 HTML+inline SVG）→ 分类为**新 register** → 落为**独立 skill**：`D:\Desktop\cc\.claude\skills\diagram-design\`（SKILL.md + 37 references + 100 assets + 2 scripts + LICENSE），非合并进 finesse-ui。
- finesse-ui 按 §4 Wire 填槽：description/when_to_use/argument-hint 加 diagram 触发词（架构图/流程图/时序图/ER 图/mermaid/drawio/画一张XX图）、§0.A 加 diagram register 路由行、Commands 表加 `diagram` 行、Routing rules 加映射、新 §12 THE DIAGRAM REGISTER 路由 stub（原 OUT OF SCOPE 顺延为 §13）、version 0.19.0→0.20.0。zine-ui 先例同款。
- diagram-design 继承声明（declared not copied）：universal craft floor + cheapness blacklist + a11y 门，full list 指回 finesse-ui references（跨 skill 指针，非坏链接）。
- frontmatter 改造为仓库规范：加 when_to_use/user-invocable/argument-hint，description 双语触发词，version 展平为 2.2。

## 源仓库缺陷修复（对抗性自检发现）
1. SKILL.md §0 style-guide gate 检测旧皮肤 token（rust #b5523a），实际默认是 atomic-tangerine #eb6c36 → gate 永不触发；已统一为 style-guide.md 实际值。
2. style-guide.md Inversion rule 遗留旧皮肤 rgba(28,25,23)→已改为当前 ink rgba(45,49,66)。
3. **4 个 type 参考文档 promise 了 11 个 `*-extended` 示例文件，上游 main 分支也不存在**（git trees API 确认 0 命中）→ 改为 "Extended pattern (not shipped as a file)" 描述 + 按需再生说明，保留知识、删假文件承诺。type-process.md §12 YAML 保留为 canonical parametric proof。
4. 注意：reference 文件是 CRLF 行尾，grep -o 匹配带 \r 会导致 -f 全误报；验证需 tr -d '\r'。

## 环境事实
- `.zcode/skills` 是指向本仓库的符号链接 → 仓库改动自动部署，无需手动同步。三处同源复核见 skills/project-kickoff-parallel-dispatch memory。
- 未 commit（用户未要求）。git 状态：finesse-ui/SKILL.md 修改 + diagram-design/ 未跟踪。
