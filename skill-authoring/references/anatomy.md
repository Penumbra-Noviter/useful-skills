# Anatomy of a Skill

The structure every skill follows — the files, what goes in each, and the disclosure ladder that keeps the top lean. Source: `skill-creator` (Anthropic), Apache-2.0.

## Directory shape

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter metadata (required: name, description)
│   └── Markdown instructions (required)
└── Bundled Resources (optional)
    ├── scripts/      - Executable code (Python/Bash/etc.)
    ├── references/   - Documentation loaded into context as needed
    └── assets/       - Files used in output (templates, icons, fonts)
```

Also common in distributed skills: `agents/openai.yaml` (model IDE/agent invocation config) and a `LICENSE` file.

## SKILL.md frontmatter

The `name` and `description` decide **when** the model will use the skill:

- `name` — hyphen-case identifier, lowercase letters/digits/hyphens only, matches the directory name.
- `description` — specific about what the skill does and when to use it. Third-person ("This skill should be used when…"). No angle brackets (`<`/`>`). For a **model-invoked** skill it carries the trigger branches; for a **user-invoked** skill it becomes a one-line human-facing summary.

**Metadata quality:** the description is the skill's top-level **context pointer** — front-load the leading word, one trigger per genuinely distinct branch, no synonyms restating one branch, cut identity the body already carries.

## Bundled resources

### scripts/ — executable code

For tasks needing deterministic reliability or that get rewritten repeatedly. Token-efficient: may be executed without loading into context. May still need reading for patching or environment adjustments.

### references/ — documentation loaded on demand

Database schemas, API docs, domain knowledge, detailed workflow guides. Keeps SKILL.md lean; loaded only when the model determines it's needed. If a file is large (>10k words), include grep search patterns in SKILL.md.

**Avoid duplication:** information lives in either SKILL.md or references, not both. Prefer references for detailed material unless it is truly core — keep SKILL.md lean while information stays discoverable without hogging the context window.

### assets/ — output resources

Files used within the output Claude produces, not loaded into context: templates, images, icons, fonts, boilerplate project directories. Separates output resources from documentation.

## Progressive disclosure

The three-level loading system for context efficiency:

1. **Metadata (name + description)** — always in context (~100 words)
2. **SKILL.md body** — when the skill triggers (<5k words)
3. **Bundled resources** — as needed (unlimited; scripts execute without reading into the window)

Push too little down and the top bloats; push too much and you hide material the agent actually needs. The tension is the whole decision. It is not primarily a token optimisation — it is how the **information hierarchy** is protected: inline what every branch needs, disclose behind a pointer what only some reach.

## Writing style

Write the entire skill in imperative/infinitive form, not second person: "To accomplish X, do Y", never "You should do X". Objective, instructional language keeps consistency and clarity for AI consumption.