# project-kickoff 并行分发设计（2026-08-09 配置）

用户诉求：多分支工单时不再单发一个 implement 子智能体，改为先判依赖、串并行分发多个子智能体，并补 code-review 审核子智能体。

## 关键设计决策
1. **依赖分析在分发前由主会话执行**：plan-tickets 批准后提取工单阻塞边建 DAG，按最长依赖链分层波次（level 0 = 无阻塞）。串行链（A→B→C）交同一 Implement 智能体连续做；同 level 且文件范围互不相交 → 并行；文件范围相交 → 降级串行。
2. **文件范围标注是并行安全的前提**：通过 plan-tickets 调用 prompt 追加要求（每张工单标文件范围 + 摘要带工单元数据表）。不改 plan-tickets/to-tickets 本身。
3. **并行必须 git worktree 隔离**：每并行智能体 `git worktree add <path> -b kickoff/<编号>-<slug>`，在自己的工作树内完成、commit；波末主会话 `git merge --no-ff` 合并回主分支并仲裁冲突。同工作树多智能体并行会互相踩踏（git index/测试/文件写入冲突），不可行。
4. **适量 = 单波并发 ≤ 3 默认**，用户可调；超出分批。
5. **审核复用 code-review skill 而非新造 agent 类型**：全部波次完成后主会话加载 code-review（固定点 = 实施前基线 commit，spec = plan-tickets spec），其内部自动并行派发 Standards + Spec + Falsify + Architecture 四个审核子智能体（四轴）。波末另有降配增量审核（仅 Falsify 轴 + 文件范围核验）。为防审核爆炸，implement 智能体被指示不单独跑 /code-review。
6. **波间门禁**：波内测试（受影响模块 + 冒烟）全绿 + 波末增量审核（Falsify 轴 + 文件范围核验）无阻断性问题 + 汇报摘要等确认；用户授权「全自动跑完」时仅汇报不等待（增量审核照跑）。
7. **Implement 每工单验收口径（2026-08-11 M 批次）**：本工单范围测试（本工单新增/改动测试 + 受影响模块既有测试，**不做全量**）；覆盖率 ≥ 90% 按本工单文件范围（`--cov=<本工单源文件> --cov-fail-under=90`）；全局覆盖率 ≥ 90% 是期末全量测试的唯一全局口径验收点。

## 环境事实
- `C:\Users\Administrator\.zcode\skills`、`C:\Users\Administrator\.cc-switch\skills` 与 `D:\Desktop\cc\.claude\skills` 三处同源（2026-08-10 复核 md5 一致），改一处即生效；每次编辑后 md5/`ls -li` 复查防漂移。
- project-kickoff 真身在 `C:\Users\Administrator\.cc-switch\skills\project-kickoff\`（**非 git 仓库**，含 SKILL.md + TO-TICKETS.md + REVISIONS.md）；`.zcode/skills` 与 repo 中为符号链接，git 无法追踪其内容——该 skill 无 git 历史，provenance 用会话记录 + TO-TICKETS.md 归档（2026-08-10 复核，勿再尝试 commit）。
- project-kickoff 修订日志存同目录 `REVISIONS.md`（独立于 SKILL.md 防膨胀，运行流程无需读取），维护者改 skill 后补一行（日期+来源+动机）；`validate_skills.py` 已含正文软检查（计数式表述漂移、「（见X）」引用完整性，仅 WARNING）。
- plan-tickets 是 harness 内置 agentType，无 SKILL.md 可改；其输出风格与 to-tickets 一致（Blocked by 边）。
- 仓库中已有 wayfinder / grilling / prototype / to-tickets / code-review / implement / neat-freak 的 SKILL.md（2026-08-10 复核存在，含调用契约）；仅 plan-tickets 为 harness 内置 agentType，无 SKILL.md 可改。