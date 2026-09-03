# Tombstone-Code Preflight

Purpose: before delivery or after a feature stabilizes, remove temporary code that served an immediate debugging or verification need and holds no ongoing obligation — without touching the project's protection net.

Trigger: the feature is stable and user-verified, or delivery is imminent. Do not sweep during active development while the temporary code is still earning its keep.

## The five tombstone classes

Every class shares one property: it was useful at the time and is due for removal once its purpose is spent.

1. **One-off temporary tests** — written to verify a behavior on the spot; dead once verified.
2. **Debug prints** — print/log statements added to trace a problem and never removed.
3. **Throwaway endpoints** — test-only routes used to inject data or skip validation.
4. **Hardcoded test data** — fake users, orders, amounts seeded while testing.
5. **One-off scripts** — code written for a single transactional task, discarded after the run.

## Hunt and prove

Run the five classes as an explicit scope of a Broad investigation; do not silently narrow the sweep to unused-symbol hunting. For every candidate record the standard proof record fields, and stress two classes:

- **Throwaway endpoint** — trace the runtime path and prove zero production consumers; flag whether it lacks authorization. An auth-free write endpoint left in a delivered build is a security exposure, not just clutter. Removing a reachable endpoint is a product decision: describe the consequence and obtain direction per SKILL.md before cutting.
- **Hardcoded test data** — check whether a formal test fixture references it; data consumed by the regression suite is alive and must stay.

Keep or downgrade the candidate when a real consumer exists or reachability is unresolved, per the main contract's rules.

## Red lines: never delete

1. **Formal regression tests** — the project's long-term protection net that every change is verified against.
2. **Deliberate operational logging on critical paths** (login, order, payment) — these resemble debug prints but are the production troubleshooting surface.

Name both classes explicitly in the confirmation list so pattern matching cannot sweep them up.

## Confirmation gate

Present the candidate list with location, purpose, reachability, recommendation, and confidence. The user confirms each deletion; unexplained items get a plain-language explanation on request. This is a hard gate: nothing is deleted before the user confirms.

## Execute and verify

Delete in ownership-boundary batches. After each batch, rerun the full regression suite. A green unit-test run is not proof of runtime health — deployment and user acceptance remain separate gates.

中文触发场景：墓碑代码 / 临时测试清理 / 调试打印清理 / 临时接口清理 / 写死假数据清理 / 一次性脚本清理 / 交付前清理 / 功能稳定后清理。