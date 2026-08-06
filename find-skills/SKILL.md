---
name: find-skills
description: Search for, discover, and get help with available skills from any skill repository
---

# Find Skills

Help the user search for, discover, and install skills from skill repositories.

## When to use

Use this skill whenever the user wants to:
- Search or discover available skills (`find skills`, `search for skills`, `look for a skill that...`)
- Ask what skills are installed or available
- Explore skill repositories to find something useful
- Get help finding the right skill for a task

## Instructions

1. **List installed skills** — Run `npx skills ls -g --json` to show currently installed global skills, or `npx skills ls --json` for project-level skills. Present them in a readable format.

2. **Search for skills** — When the user has a specific need, search for relevant skills:
   - Use `npx skills find <query>` to search interactively for skills matching a keyword
   - Or browse repositories like `https://github.com/anthropics/skills` (18+ skills: claude-api, docx, pdf, pptx, xlsx, algorithmic-art, brand-guidelines, canvas-design, doc-coauthoring, frontend-design, internal-comms, mcp-builder, skill-creator, slack-gif-creator, theme-factory, web-artifacts-builder, webapp-testing, template-skill)
   - Also check `https://skills.sh/` for the public skill directory

3. **List skills from a repository without installing** — Use `npx skills add <repo-url> --list` to see what skills a repository offers before installing any.

4. **Install a skill** — Once found, install with:
   - Global: `npx skills add <repo-url> --skill <name> --global --yes`
   - Project: `npx skills add <repo-url> --skill <name> --yes`

5. **Get skill details** — Read the SKILL.md file in the skill's directory to understand what it does and how it works. Skills are stored globally in the directory configured by the junction/CLAUDE_CONFIG settings.

6. **Update skills** — Run `npx skills update -g --yes` to update all global skills to their latest versions.

7. **Remove skills** — Use `npx skills remove <name>` to remove a skill you no longer need.
