# Skill Mechanics — Invocation and Frontmatter

The skill-specific branch of `skill-authoring`: what changes when the document is a skill — frontmatter, the invocation choice, and router skills. Everything else about writing it is the universal reference in `principles.md`; structure and workflow in `anatomy.md` / `process.md`. Merged from `writing-for-agents` (`SKILL-MECHANICS.md`) and `writing-great-skills` (Matt Pocock).

## Invocation

Two choices, trading the two loads:

- A **model-invoked** skill keeps a `description`, so the agent can fire it autonomously — and other skills can reach it. You can still type its name: model-invocation always _includes_ user reach; a description only ever adds agent discovery, never removes the human's. The description is the skill's top-level **context pointer**, forced to stay loaded at all times — permanent context load in exchange for discoverability. A model-invoked skill whose content is all reference is also one home for shared reference: another skill can invoke it, so reference needed by several skills lives in one place. Mechanics: omit `disable-model-invocation`, and write a model-facing description carrying the trigger branches (the pointer-writing rules in `principles.md` apply in full).
- A **user-invoked** skill strips the description from the agent's reach: only the human typing its name can invoke it, and no other skill can. Zero context load, but it spends **cognitive load** — you are the index that must remember it exists. Mechanics: set `disable-model-invocation: true`; the `description` becomes human-facing — a one-line summary, trigger lists stripped.

Pick model-invocation only when the agent must reach the skill on its own, or another skill must. If it only ever fires by hand, make it user-invoked and pay no context load.

Shared reference that two user-invoked skills both need can live in neither — with no descriptions, neither can fire the other. Push it to a plain file outside the skill system: external reference any skill can point at.

## Splitting by invocation

The invocation cut of splitting (the sequence cut lives in `principles.md`): split off a model-invoked skill when you have a distinct leading word that should trigger it on its own — a trigger word you actually use in your prompts — or another skill must reach it. You pay context load for the new always-loaded description, so that independent reach has to be worth it.

## Router skills

When user-invoked skills multiply past what you can remember, that piled-up cognitive load is cured by a **router skill**: one user-invoked skill that names the others and when to reach for each, so the human has one skill to remember instead of many. It can only hint, never fire them: user-invoked skills have no description, so nothing but the human can reach them.

## Frontmatter

A model-invoked skill's description is where its invocation work happens:

- `name` — hyphen-case, lowercase letters/digits/hyphens only, matches the directory name.
- `description` — third-person, specific about what and when. No angle brackets. For model-invoked skills: front-load the leading word, one trigger per genuinely distinct branch, cut identity the body carries.

## Relationship to the meta-designer

`dao-skill` (gnipbao/dao-skill) is the **meta-designer** / lifecycle manager, not a peer writing skill: it does root-problem analysis, design, evaluation (Trust Gate, evidence levels), optimisation, evolution, and absorption. When `dao-skill` reaches the concrete job of _writing or editing a skill's actual content_, it routes here — this skill owns the writing. Keep this skill model-invoked so that routing is possible.

**Installation state (2026-08-27):** `dao-skill` is installed at `C:\Users\Administrator\.zcode\skills\dao-skill` (git clone, passing its own `scripts/run_checks.py`). Both skills are model-invoked in the same discovery directory, so the division of labour is:

- **dao-skill decides** — root problem, production pattern, evaluation (Trust Gate / evidence levels / P0-P2), evolution, absorption. It triggers on 归根 / 设计 / 生成 / 评估 / 优化 / 进化 / 自化.
- **skill-authoring executes the writing** — structuring SKILL.md, frontmatter, disclosure, pruning, packaging. It triggers on concrete document work.

A combined run: `dao-skill` first establishes root and mode (A-F), then for any file-producing step (Mode C generation, Mode D/E patching) applies the writing principles and anatomy here. The `dao-skill` source stays untouched so upstream updates remain `git pull --ff-only` clean.