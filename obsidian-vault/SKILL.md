---
name: obsidian-vault
description: Search, create, and manage notes in the Obsidian vault with wikilinks and index notes. Use when user wants to find, create, or organize notes in Obsidian.
---

# Obsidian Vault

## Vault location

This skill targets Obsidian's multi-vault knowledge base rooted at `D:/Desktop/knowledge base/` (domains such as `demo` for programming, `Studying Game` for game research). Resolve the target vault root for this session via the library-routing rule in AGENTS.md §3.5 — a project's `KNOWLEDGE_BASE.md` first, then the vault's own `README.md`, defaulting to `demo` for programming. Let the user name the vault explicitly otherwise (e.g. `D:/Desktop/knowledge base/well-being`). All commands below use `<VAULT_ROOT>` for that resolved root.

`<VAULT_ROOT>` must be a Windows / Git-Bash-resolvable path (`D:/...` or `/d/...`) — never a WSL `/mnt/...` path, which is unresolvable in this environment.

The vault is mostly flat at its root level.

## Naming conventions

- **Index notes**: aggregate related topics (e.g., `Ralph Wiggum Index.md`, `Skills Index.md`, `RAG Index.md`)
- **Title case** for all note names
- No folders for organization - use links and index notes instead

## Linking

- Use Obsidian `[[wikilinks]]` syntax: `[[Note Title]]`
- Notes link to dependencies/related notes at the bottom
- Index notes are just lists of `[[wikilinks]]`

## Workflows

### Search for notes

```bash
# Search by filename
find "<VAULT_ROOT>" -name "*.md" | grep -i "keyword"

# Search by content
grep -rl "keyword" "<VAULT_ROOT>" --include="*.md"
```

Or use Grep/Glob tools directly on the vault path.

### Create a new note

1. Use **Title Case** for filename
2. Write content as a unit of learning (per vault rules)
3. Add `[[wikilinks]]` to related notes at the bottom
4. If part of a numbered sequence, use the hierarchical numbering scheme

### Find related notes

Search for `[[Note Title]]` across the vault to find backlinks:

```bash
grep -rl "\\[\\[Note Title\\]\\]" "<VAULT_ROOT>"
```

### Find index notes

```bash
find "<VAULT_ROOT>" -name "*Index*"
```
