# ADR-001：整合创作层 skill（skill-creator + writing-great-skills + writing-for-agents）

## 决策背景

用户有三个「关于写 skill」的 skill，均落在创作/写作层：

- `skill-creator`（Anthropic 官方，Apache-2.0）— **操作/结构层**：skill 的目录结构（SKILL.md + scripts/references/assets）、progressive disclosure、六步创建流程、init/package/validate 三个脚本。
- `writing-great-skills`（Matt Pocock）— **写作/语言层**：Predictability 词汇表、信息层级、何时拆分、pruning、leading words、failure modes。`disable-model-invocation: true`（用户手动调用）。
- `writing-for-agents`（Matt Pocock）— **写作层（更宽）**：同一套 levers 推广到任何 agent 消费的文档（AGENTS.md/CLAUDE.md/pointer 文档），`SKILL-MECHANICS.md` 管 frontmatter/调用选择/router。

已调研的 `dao-skill`（gnipbao/dao-skill）不是平级，而是**元设计器/生命周期管理层**（归根→设计→生成→评估→进化→自化），它应该在 Mode C/D/E 里路由到创作层 skill，而不与之合并。

用户决定：把三个创作层 skill **整合成一个**；`dao-skill` 保持独立，作为上层路由者。

## 前提拆解（第一性原理）

- **不可变事实**：
  - 三个 skill 的核心能力必须全部保留，不得丢失（结构脚本、写作原则、广义文档写作）。
  - 整合后的 skill 必须**模型可调用**（保留 description），否则 `dao-skill` 无法在运行时路由到它。这与原 `writing-great-skills` 的 user-invoked 相反，是本次的关键反转。
  - 各来源的许可须保留归属：skill-creator 是 Apache-2.0；两个 writing-* 是 Matt Pocock 的（MIT/未标注，保留出处链接）。
- **习得惯例**：单一 SKILL.md 越精简越好（progressive disclosure / 防 sprawl），细节进 references。这条惯例本身来自被整合的 skill，予以沿用。

## 可选方案

1. **方案 A（采纳）：三个合一个 `skill-authoring`**，SKILL.md 精简为核心 + resource guide，四个 references 分别承载 anatomy / process / principles / invocation；scripts + LICENSE + agents 配置搬入；旧三个归档。
2. 方案 B：只合 skill-creator + writing-great-skills，writing-for-agents 独立保留（面向非 skill 文档）。
3. 方案 C：不合并，只加一个 router skill 指向三个。

## 最终选择

✅ **方案 A**

## 理由

- writing-great-skills 本质是 writing-for-agents 的 skill 特化版，二者高度重叠，合并不损失信息，还消除重复维护。
- 单一模型可调用入口让 `dao-skill` 有明确、稳定的路由目标（一个创作层协议面）。
- 用 references 分载防止 sprawl，符合被整合 skill 自身的写作原则。
- 方案 B 保留一个几乎重叠的独立 skill，违背「单一来源」；方案 C 不解决重复，还增加认知负载。

## 保留 / 裁掉明细

| 来源 | 保留 | 裁掉 / 合并 |
|---|---|---|
| skill-creator | SKILL.md 结构说明→`anatomy`；六步流程→`process`；init_skill.py / package_skill.py / quick_validate.py 脚本；LICENSE.txt | 拆散进 references，SKILL.md 只留 workflow 骨架 |
| writing-great-skills | Predictability/信息层级/pruning/leading words/failure modes/调用选择→`principles` + `invocation`；GLOSSARY 概念 | 不再单独成 skill；其 user-invoked 改为模型可调用 |
| writing-for-agents | 通用 agent 文档写作原则→`principles`；SKILL-MECHANICS→`invocation`（含 AGENTS.md/CLAUDE.md 场景） | 不再单独成 skill |

## 影响

- 正面：一个入口、消除重复、`dao-skill` 有稳定路由目标、脚本资源集中。
- 代价：三个原 skill 被归档（仍可回滚）；整合后 skill 需保证 coverage 不低于三者之和。
- 回滚：旧三个目录移到 `_archived/`，可随时移回。

## 后续：dao-skill 安装与协作（2026-08-27）

`dao-skill`（gnipbao/dao-skill，commit `1cae835`）已 clone 安装到 `C:\Users\Administrator\.zcode\skills\dao-skill`，其 `scripts/run_checks.py` 全部通过，git 工作区保持干净以便 `git pull --ff-only` 更新。两个 skill 均为 model-invoked、同处发现目录：

- `dao-skill` 决策：归根、设计、评估（Trust Gate/证据分级/P0-P2）、进化、自化（Mode A-F）。
- `skill-authoring` 执行写作：结构、frontmatter、披露、pruning、打包。

协作契约：`dao-skill` 先定根问题与模式，文件产出步骤（Mode C 生成 / D/E 打补丁）落到本 skill 的写作原则与 anatomy。`dao-skill` 源码零改动，避免破坏上游更新。
