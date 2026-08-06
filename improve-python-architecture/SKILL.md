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

## 3. Grill

When the user picks a candidate, run `/grilling` to walk the decision tree. Side effects during the conversation:

- **New concept named?** Add it to `ARCHITECTURE-VOCABULARY.md`.
- **Fuzzy term sharpened?** Update it.
- **Rejected with a load-bearing reason?** Offer an ADR.
- **Alternative protocol surfaces wanted?** Run `/codebase-design` for the design-it-twice pattern.

**Completion criterion:** candidate accepted or rejected, with a recorded reason.
