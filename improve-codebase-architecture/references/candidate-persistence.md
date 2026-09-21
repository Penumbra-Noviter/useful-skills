# Candidate-Persistence Contract（architecture-report → TECH_DEBT.md）

本文件是 `improve-codebase-architecture` 与 `improve-python-architecture` **共享**的候选持久化契约的唯一权威源。两篇 SKILL.md 不内联本契约，只在此引用（codebase 版直接用本文件；python 版经 `../improve-codebase-architecture/references/candidate-persistence.md` 指向同一份）。

## Candidates must not leak

The report is a throwaway file in the OS temp dir — once the session ends it is gone, and the next scan will re-suggest the same candidates verbatim, turning into a repeat-suggestion loop. So after the user picks or declines, persist the **unpicked candidates** into the repo's `TECH_DEBT.md` candidate section (source = architecture report, recommendation strength → strength column, status 📝 待立项) so future scans can dedupe against them; dedupe key = `file:line + problem description` — a match appends a re-confirmation note to the existing entry instead of opening a new one.

## Dedupe against past suggestions before scanning

Read the `TECH_DEBT.md` entries whose source is the architecture report. A candidate already suggested before (unpicked, deferred, or adopted-then-reverted — the latter tracked by a rollback note on its entry) is flagged "Nth suggestion" with a pointer to the existing entry instead of being spread out again; one scan presents each candidate once. If an adopted candidate was later reverted (A→B→A′), append the rollback fact to its entry so the next scan does not re-suggest the reverse direction.

---

*Vendored mattpocock 技能共享契约（2026-09-22 抽离，原双源逐字重复于两篇 SKILL.md）。改契约只改本文件，两篇 SKILL.md 保持指针不变。*