# ADR-002：硬化 dao-skill → skill-authoring 创作路由

日期：2026-09-05

## 决策背景

ADR-001（2026-08-27）确立了协作契约：dao-skill 是元设计器（归根/设计/评估/进化/自化），文件产出步骤（Mode C 生成 / D/E 打补丁）路由到创作层 skill-authoring 执行写作。但该契约是「模型自觉的软路由」：

- dao-skill 源码零改动（为保 `git pull --ff-only`），路由从未写入其文件；
- dao-skill 自带 `skill-generation-template.md` + `production-skill-patterns.md`，自包含完整创作能力，官方 examples（`create-learning-coach-skill.md` 等）演示的产出形态全程未调用任何其他 skill；
- scripts 检查只验证文档结构（`## Mode Router` 等），无任何一项验证「创作时是否调用了 skill-authoring」。

2026-09-05 实证（本会话）：E2 回放确认 skill 可按流程工作，但路由是否生效完全取决于运行时模型是否把「skill 写作」识别为 skill-authoring 的职责 —— 机制在位、保障缺失。用户拍板：**硬化路由** —— dao 创作不仅使用自包含资产，也必须用到 skill-authoring。

## 前提拆解（第一性原理）

- **不可变事实**：
  - 模型每轮加载 dao-skill 时必读 `SKILL.md` → 强制规则必须写在 `SKILL.md` 内，写在独立文件若不从 SKILL.md 链接则不会生效；
  - skill-authoring 必须保持 model-invoked（保留 description），否则 dao 无法在运行时触发它（ADR-001 已确立，不变）；
  - skill-authoring 是本地整合资产（非上游），改动安全；dao-skill 是上游 clone，改动会弄脏工作区。
- **习得惯例**：quality_check 强制「references 下文件必须被 SKILL.md 链接」——正好约束契约文件必须挂指针，顺水推舟。

## 可选方案

1. **方案 A（采纳）：双侧硬化，改动最小** — dao-skill `SKILL.md` 加「Creation Routing Contract」节 + Resource Guide 加一行指针（契约细节进 `references/routing-authoring-contract.md`）；skill-authoring `SKILL.md` 加「Collaboration contract」声明职责边界；决策记录为 ADR-002。
2. 方案 B：只改 skill-authoring 侧，dao-skill 不动 — 触发侧未硬化，dao 自包含时照样不路由，等于没硬化。
3. 方案 C：建 wrapper skill 包裹 dao-skill — 新增一个加载入口，但用户触发原版 dao-skill 时路由仍不生效，且多一个常驻 skill。

## 最终选择

✅ **方案 A**

## 理由

- 强制规则进入 dao-skill 的 `SKILL.md` = 每轮加载必见，真正硬化触发侧；
- 改动面最小：SKILL.md 一节 + 一个新 references 文件（quality_check 链接检查天然覆盖）+ authoring 侧一段声明；
- 双侧闭合：dao 声明「必须路由」、authoring 声明「被路由时执行写作、不重做归根」；
- 方案 B 不解决触发侧，方案 C 增加认知负载且不覆盖原触发路径。

## 影响

- 正面：路由从「模型自觉」变为「显式契约」；Completion Contract 强制记录 authoring 的应用；authoring 不可用时显式降级（E1 封顶）。
- 代价：dao-skill 工作区变脏（modified `SKILL.md` + untracked `references/routing-authoring-contract.md`），打破「源码零改动」约束；上游 `git pull` 若更新 Resource Guide 段可能冲突，处理约定已写入契约文件（以上游为准、重放本段）。
- 回滚：`git checkout -- SKILL.md` + 删除 `references/routing-authoring-contract.md` 即恢复干净上游；authoring 侧声明与本文档独立可保留。

## 验证

dao-skill 全套 `python scripts/run_checks.py`（quality/evolution/evaluation/behavior contracts/repository boundary/installer+validator regression）必须通过；repository boundary 若因工作区脏而失败，属发布前检查的预期行为，不代表 skill 失效。
