---
name: skill-authoring
description: Author, write, structure, and package skills and other documents agents consume (SKILL.md, AGENTS.md, CLAUDE.md, referenced docs). Use when creating a new skill or editing an existing one, structuring a skill directory, writing skill frontmatter, packaging or validating a skill, or applying agent-oriented writing principles (predictability, information hierarchy, pruning, leading words) to any document an agent reads.
---

# Skill Authoring

The integrated creation-layer skill for anything an agent consumes: skills first, then `AGENTS.md` / `CLAUDE.md` and any doc reached by a pointer. The packaging differs; the writing does not — the same levers make each predictable, the agent taking the same _process_ every run, not producing the same output.

**Bold terms** are defined in `references/principles.md`; look them up there for the full meaning.

## When to use

- Create a new skill, or update an existing one.
- Decide a skill's structure and structure the directory (SKILL.md, `scripts/`, `references/`, `assets/`).
- Write or edit `AGENTS.md` / `CLAUDE.md`, or any document an agent reads.
- Package, validate, or distribute a skill.
- Diagnose why an existing skill misbehaves (failure modes).

## Invocation decision first

Before writing, decide how the document is reached — it changes what you write:

- A **model-invoked** skill keeps a `description`, so the agent can fire it autonomously and other skills (e.g. `dao-skill`) can reach it. Pays permanent **context load**. Mechanics: omit `disable-model-invocation`, write a model-facing description carrying trigger branches.
- A **user-invoked** skill strips the description: only the human typing its name can invoke it. Zero context load, but the human is the index. Mechanics: set `disable-model-invocation: true`; the description becomes a one-line human-facing summary.

Pick model-invocation only when the agent must reach the document on its own, or another skill must. Full mechanics in `references/invocation.md`.

## Authoring workflow

1. **Locate** — SKILL.md is the primary tier. For skills, follow the anatomy in `references/anatomy.md`; keep the top legible, push detail down.
2. **Write by hierarchy** — steps (ordered actions) end on a **completion criterion**; reference (facts, rules) is consulted on demand. Apply the principles in `references/principles.md`.
3. **Disclose** — push reference behind **context pointers** into sibling files, inline only what every branch needs. Co-locate a concept's definition, rules, and caveats under one heading.
4. **Prune** — single source of truth; no meaning in two places; no no-ops; no restatement where a **leading word** collapses it.
5. **Scaffold & package** — for new skills, `scripts/init_skill.py <name> --path <dir>` then `scripts/package_skill.py <dir>` (validates first). Commands in `references/process.md`.
6. **Check** — run `scripts/quick_validate.py <dir>` before packaging; walk the failure modes in `references/principles.md` before declaring done.

## Non-negotiables

- Write the entire document in **imperative/infinitive form**, objective and instructional (e.g. "To accomplish X, do Y").
- Front-load the document's leading word in any always-loaded pointer (description, AGENTS.md line).
- Never claim progress by adding bulk — "better" means the same behaviour more predictably, not more text.
- Preserve a single source of truth: a change to behaviour is a one-place edit.

## Source of this skill

Integrated (2026-08-27) from three skills, per `ADR-001-integrate-creation-layer.md`: `skill-creator` (Anthropic, Apache-2.0 — structure, workflow, scripts), `writing-great-skills` (Matt Pocock — vocabulary, failure modes), `writing-for-agents` (Matt Pocock — universal agent-doc principles, skill mechanics).