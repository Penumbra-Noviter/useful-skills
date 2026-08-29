# Skill Creation Process

The end-to-end workflow for creating or updating a skill, from concrete examples to distribution. Source: `skill-creator` (Anthropic), Apache-2.0. Follow in order; skip a step only with a clear reason it does not apply.

## Step 1 — Understand the skill with concrete examples

Skip only when usage patterns are already clearly understood; valuable even when working with an existing skill. Gather concrete examples of how the skill will be used:

- What functionality should the skill support?
- What would a user say that should trigger it?
- What are concrete example requests?

Avoid overwhelming with questions in one message: start with the most important, follow up as needed. Conclude when the functionality is clear.

## Step 2 — Plan the reusable skill contents

Turn concrete examples into content by analyzing each: (1) how to execute it from scratch, (2) what scripts, references, and assets would help when executing these workflows repeatedly.

- A script when the same code gets rewritten each time (e.g. `scripts/rotate_pdf.py`).
- An asset template when the same boilerplate is needed each time (e.g. `assets/hello-world/`).
- A reference when schemas/relationships get re-discovered each time (e.g. `references/schema.md`).

## Step 3 — Initialize the skill

Skip only if the skill already exists and iteration/repackaging is needed.

```bash
scripts/init_skill.py <skill-name> --path <output-directory>
```

Creates the skill directory, a SKILL.md template with proper frontmatter and TODO placeholders, and example `scripts/`, `references/`, `assets/` directories. Customize or remove generated examples as needed.

## Step 4 — Edit the skill

The skill is being created for another agent instance. Focus on what is beneficial and _non-obvious_: procedural knowledge, domain-specific details, reusable assets.

1. **Start with reusable contents** — build the scripts/references/assets identified above. May require user input (brand assets, documentation). Delete example files and directories not needed — most skills won't need all three.
2. **Update SKILL.md** — imperative/infinitive form throughout. Answer: what is the purpose (a few sentences)? When should it be used? In practice, how should the agent use it, referencing the reusable contents?

## Step 5 — Validate and package

Packaging validates first, then zips:

```bash
scripts/package_skill.py <path/to/skill-folder>
scripts/package_skill.py <path/to/skill-folder> ./dist   # optional output dir
```

Validation checks: YAML frontmatter format and required fields, naming conventions and directory structure, description completeness and quality, file organization and resource references. If validation fails, fix errors and rerun — nothing is packaged until it passes.

Quick structural check without packaging:

```bash
scripts/quick_validate.py <skill_directory>
```

## Step 6 — Iterate

After testing on real tasks, iterate:

1. Use the skill on real tasks.
2. Notice struggles or inefficiencies.
3. Identify how SKILL.md or bundled resources should update.
4. Implement and test again.

Improvements most often arrive right after use, with fresh context of how the skill performed. Before iterating, consult the failure modes and pruning rules in `references/principles.md` — most skill problems are diagnosing misbehaviour, not adding content.