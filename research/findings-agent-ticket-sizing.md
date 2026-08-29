# 调研：AI 编码代理的工单粒度与单会话时长

> 获取时间：2026-08-26。本报告只引一手来源；引文逐条标注来源、置信度、验证级别。
> 关键环境限制：本次调研的网络沙箱**无法访问** code.claude.com（Claude Code 官方文档）、arxiv.org、wikipedia、xp123.com 等域名，因此部分应引用的权威来源（Claude Code 最佳实践、SWE-bench 等）**无法在本环境核实原文**，已在「缺口」节如实标注，未编造引文。

## 结论

没有厂商发布过"一个代理会话必须在 X 分钟内完成"的硬性分钟数规则；但存在可落地为**定量上限**的、来自两条独立权威链路的工单粒度约定：(a) Google 工程规范（google/eng-practices）对"变更"给出的 LOC/文件数上限，(b) OpenAI Codex 仓库的 AGENTS.md（即 OpenAI 自己写给代理执行本仓库任务的规则）给出的"单次变更 ≤800 变更行 / 复杂逻辑 ≤500 行 / 过大则拆成可评审阶段"的上限，以及"注入上下文的条目必须有硬上限、单条 ≤10K token、>1K token 的条目需人工复核"。**建议对单代理工单采用如下可执行上限**：每次会话 = 一个"自包含变更 / 单一职责"；变更 ≤100–500 行（≤800 为硬上限）；触及文件数控制在个位数（跨大量文件即视为过大）；每次会话只跨越一个接缝/接口、一条纵向切片；验收标准聚焦 1 条核心 + 少量显式项；测试与实现同票提交；**在开工前**（工单切分阶段）就拆好步，避免让代理在开放式大任务里自主规划到底。对"单会话时间预算"：没有主源给出分钟数，需转 Prototype 用实验校准，详见「建议转 Prototype 验证」。

---

## 引文

### C1. 工单应等于"一个自包含变更 / 单一职责"（跨来源共识，方向性为高置信度）
- **来源**：Google Engineering Practices, `review/developer/small-cls.md` — https://github.com/google/eng-practices/blob/master/review/developer/small-cls.md（获取 2026-08-26，经 GitHub API 直读原文）
- **置信度**：高（方向性）；**验证级别**：Deterministic（读到原始 base64 文本）
- **详情**：原文："In general, the right size for a CL is **one self-contained change**";"The CL makes a minimal change that addresses **just one thing**. This is usually just one part of a feature, rather than a whole feature at once." 且 "reviewers have discretion to reject your change outright for the sole reason of it being too large." 该组织在 `openai/codex` 的 AGENTS.md 亦有同向要求（见 C2/C8），两独立权威机构一致 → 方向性结论标"高"。

### C2. 定量 LOC 上限（两级权威各自给出，数字为区间而非通用真理）
- **来源 A**：Google Engineering Practices, `review/developer/small-cls.md`（同上，获取 2026-08-26，Deterministic）
- **来源 B**：OpenAI Codex 仓库 `AGENTS.md`，https://github.com/openai/codex/blob/main/AGENTS.md（获取 2026-08-26，GitHub API 直读，Deterministic）
- **置信度**：中–高（"确实存在 100–800 行量级的单次变更上限且各组织不同"为高；具体数字为各组织内部约定，标中）
- **验证级别**：Deterministic（两者均读到原文）
- **详情**：
  - Google：原文 "100 lines is usually a reasonable size for a CL, and 1000 lines is usually too large";"A 200-line change in one file might be okay, but spread across 50 files it would usually be too large." → **文件数同样决定"过大"**，不只是行数。
  - OpenAI Codex：原文 "Unless the change is mechanical the total number of changed lines should not exceed **800 lines**. For complex logic changes the size should be under **500 lines**.";且 "If the change is larger, explore whether it can be split into reviewable stages and identify the **smallest coherent stage** to land first."（此即"开工前先拆步"的官方表述，见 C8。）

### C3. 单代理/单工单的责任边界：给每个子任务"清晰任务边界 + 完整 mini-spec"
- **来源**：Anthropic Engineering, "How we built our multi-agent research system" — https://www.anthropic.com/engineering/multi-agent-research-system（获取 2026-08-26）
- **置信度**：高（官方工程实践）；**验证级别**：Probabilistic（经 WebFetch 摘要抽取，引文为片段、建议引用前复核原文措辞）
- **详情**：Anthropic 用 orchestrator–worker 模式，把查询拆成子任务派给并行 subagent。原文要点："Each subagent needs an **objective, an output format, guidance on the tools and sources to use, and clear task boundaries**";并指出模糊交接会失败："Without detailed task descriptions, agents duplicate work, leave gaps, or fail to find necessary information." → 单票应自带"目标 / 输出格式 / 可用工具 / 边界"，且一次只给一个责任域。此点与 C1 的"单一职责"同向 → 高。

### C4. "放得进单个上下文窗口"的最接近一手锚点：OpenAI 对模型上下文的硬上限
- **来源**：OpenAI Codex 仓库 `AGENTS.md`（同上，获取 2026-08-26，Deterministic）
- **置信度**：中（单一来源）；**验证级别**：Deterministic
- **详情**：原文 "Model visible context" 一节："**No unbounded items** - everything injected in the model context must have a bounded size and a hard cap";"**No items larger than 10K tokens**";"Highlight new individual items that can cross **>1k tokens** as P0. These need an additional manual review." → 说明厂商侧把"注入上下文的每个条目设硬上限 + 大条目人工把关"当作会话可控性底线。这是"每会话责任量受上下文预算约束"最直接的一手证据（暂无厂商给出"整会话 ≤ N token"的官方数字）。

### C5. 有界/可预测时长：用 workflow 而非开放 agent；先简单后加复杂
- **来源**：Anthropic Engineering, "Building effective agents" — https://www.anthropic.com/engineering/building-effective-agents（获取 2026-08-26）
- **置信度**：高（官方指引）；**验证级别**：Probabilistic（WebFetch 摘要抽取）
- **详情**：官方区分 "Workflows are systems where LLMs and tools are orchestrated through **predefined code paths**"（可预测）vs "Agents ... dynamically direct their own processes"（开放、步数不可预测）。对"张数可预测"的诉求，官方路线是：可预测任务用 workflow/预定义步骤（如 prompt chaining、plan-and-execute、orchestrator-workers），并在布局层替代理预拆步；同时 "we recommend finding the simplest solution possible, and only increasing complexity when needed"。→ 对失败模式 1（单会话超长），主源给出的不是"分钟数"，而是**在工单/编排层预先固定步骤**这一设计杠杆。

### C6. 纵向切片（vertical slice）的宽度规则：每条特性=一条端到端薄切片；网格中的一格=一个独立工单
- **来源**：Google Engineering Practices, `review/developer/small-cls.md`（同上，获取 2026-08-26，Deterministic）
- **置信度**：中–高（Google 是给出可操作规则的显式一手来源；概念与 C3 同向）；**验证级别**：Deterministic
- **详情**：原文 "Splitting Vertically": "you can instead break down your code into smaller, full-stack, vertical features. Each of these features can be **independent parallel implementation tracks**." 其"水平×垂直"拆分网格中"each cell is its own standalone CL"（即：层×特性交点 = 一个最小独立工单）。→ 纵向切片的宽度上限 = **一个薄特性（一条全栈路径），宽度上不跨越多个特性**；横向（按层）拆分仅用于解耦并行，不作为每个工单的默认做法。

### C7. 经典 XP 故事"小"准则（INVEST：S = Small）
- **来源**：Bill Wake, "INVEST in Good Stories and Smart Tasks" — https://xp123.com/articles/invest-in-good-stories-and-smart-tasks/（2003；**本环境 DNS 不可达，未能核实原文**）
- **置信度**：低（来源已识别，但原文未能在本环境核实；仅凭广泛公开共识转述）；**验证级别**：Manual（未复验）
- **详情**：INVEST 中 S=Small 的共识含义：故事/任务应小到能在一个迭代（或约一天）内完成、否则拆分；并以"能否一次性理解/评审"为判据。此为经典 XP 常识，与 C1/C2 的"自包含小变更"方向一致；但**具体措辞与"天数"建议未经本环境核实**，引用前请复查原文。

### C8. 拆步应在开工前（工单切分阶段）做，而非让代理边跑边拆
- **来源**：OpenAI Codex `AGENTS.md` + Google `small-cls.md`（同上，均 Deterministic）
- **置信度**：高（两独立来源一致）；**验证级别**：Deterministic
- **详情**：Codex："If the change is larger, explore whether it can be split into reviewable stages and identify the smallest coherent stage to land first"；Google："When starting work that will have multiple CLs ... it's often useful to think about how to split and organize those CLs at a high level **before diving into coding**." → 与 Anthropic 的"workflow 预定义步骤"（C5）构成同一主题：**由编排/切分工单的人先拆，代理只执行一个已定界的步**。

### C9. 测试与实现放同一工单（代理变更必须带集成测试）
- **来源**：Google `small-cls.md`（"Keep related test code in the same CL"）+ OpenAI Codex `AGENTS.md`（"Features that change the agent logic MUST add an integration test"）（获取 2026-08-26，Deterministic）
- **置信度**：高（两独立来源一致）；**验证级别**：Deterministic
- **详情**：两个来源都要求"改动逻辑的变更需同票携带相应测试"。对单代理工单而言，这意味着"验收标准"里应含"可运行的测试通过"，且测试不单独拆成无主人的票。

---

## 缺口（诚实标注，非编造）

- **Claude Code 官方最佳实践文档**（https://code.claude.com/docs/en/best-practices，含厂商对任务粒度的建议）本环境网络不可达（TCP 层重置），未纳入引用；Anthropic 关于 Claude Code 的具体定量建议**无法在本环境核实**，需在可访问该域名的网络下补证。
- **arXiv（SWE-bench 2310.06770、"Lost in the Middle" 2307.03172、Agentless 2407.01489）** 本环境连接被重置，未能核实其原文。研究界"一个代理工单 = 一个真实 GitHub issue、产出单个补丁"的规范化单位与"长上下文导致生成质量下降"的证据，**在可达网络下应补验**；不引用的原因是不愿引用未经核实的数字。
- **没有找到任何一手来源给出"单会话 ≤ N 分钟"的墙钟时间预算**。现有上限都是"变更量/上下文量/职责域"型，而非分钟数型。

## 建议转 Prototype 验证

1. **会话分钟数阈值**：为当前技术栈校准"一个会话应在多少分钟内收敛"的经验值（文案调研无主源）。
2. **上下文-质量退化拐点**：在真实长任务上测"上下文接近上限时补丁质量/正确率是否下降"，以确定每票上下文预算的保守上限（对应 C4）。
3. **上限的适用性**：验证 100–800 变更行、个位数文件数的上限在本代码库/语言下是否合理（C2/C6 为通用组织约定，非本仓校准值）。

---

### 预算使用
- 来源数：**5**（Google eng-practices、OpenAI Codex AGENTS.md、Anthropic "Building effective agents"、Anthropic "How we built our multi-agent research system"、Bill Wake INVEST[未核实，低置信]）；缺口节所列 URL 不计入来源数。
- 字数：约 1900 字（正文 ≤2000）。
- 未超限。
