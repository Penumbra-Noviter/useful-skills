---
name: improve-python-architecture
description: Scan a Python codebase for deepening opportunities, present a structured report, then grill through whichever you pick.
disable-model-invocation: true
---

# Improve Python Architecture

Surface architectural friction in Python codebases and propose **deepenings** — refactors that turn shallow packages into deep ones. Testability improves through the module's protocol surface; AI-navigability improves through locality.

Read [`ARCHITECTURE-VOCABULARY.md`](ARCHITECTURE-VOCABULARY.md) and use its terms exactly — never substitute. References that only some branches reach live in separate files; follow the pointer when it fits your path.

## 1. Explore

Scope before you scan. If the user named a module or pain point, start there. Otherwise **excavate** hot spots from `git log --oneline`, then walk the chosen paths.

Read [`PYTHON-FRICTION-SIGNALS.md`](PYTHON-FRICTION-SIGNALS.md) and apply every signal to the code under review.

**Completion criterion:** every signal checked against the scope; candidate list non-empty.

## 2. Present

Build a structured report following [`PRESENTATION-GUIDE.md`](PRESENTATION-GUIDE.md). Write it to the OS temp directory and open it for the user. End with a **top recommendation**.

**Completion criterion:** every candidate card complete; top recommendation stated.

**Candidates must not leak.** The report is a throwaway file in the OS temp dir — once the session ends it is gone, and the next scan will re-suggest the same candidates verbatim, turning into a repeat-suggestion loop. So after the user picks or declines, persist the **unpicked candidates** into the repo's `TECH_DEBT.md` candidate section (source = architecture report, recommendation strength → strength column, status 📝 待立项) so future scans can dedupe against them; dedupe key = `file:line + problem description` — a match appends a re-confirmation note to the existing entry instead of opening a new one.

## 3. Grill

**Dedupe against past suggestions before scanning.** Read the `TECH_DEBT.md` entries whose source is the architecture report. A candidate already suggested before (unpicked, deferred, or adopted-then-reverted — the latter tracked by a rollback note on its entry) is flagged "Nth suggestion" with a pointer to the existing entry instead of being spread out again; one scan presents each candidate once. If an adopted candidate was later reverted (A→B→A′), append the rollback fact to its entry so the next scan does not re-suggest the reverse direction.

When the user picks a candidate, run `/grilling` to walk the decision tree. Side effects during the conversation:

- **New concept named?** Add it to `ARCHITECTURE-VOCABULARY.md`.
- **Fuzzy term sharpened?** Update it.
- **Rejected with a load-bearing reason?** Offer an ADR.
- **Alternative protocol surfaces wanted?** Run `/codebase-design` for the design-it-twice pattern.

**Completion criterion:** candidate accepted or rejected, with a recorded reason.
