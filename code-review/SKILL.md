---
name: code-review
description: "Review the changes since a fixed point (commit, branch, tag, or merge-base) along two axes: Standards (does the code follow this repo's documented coding standards?) and Spec (does the code match what the originating issue/spec asked for?). Runs both reviews in parallel sub-agents and reports them side by side. Use when the user wants to review a branch, a PR, work-in-progress changes, or asks to \"review since X\"."
---

Multi-axis review of the diff between `HEAD` and a fixed point the user supplies:

- **Standards**: does the code conform to this repo's documented coding standards?
- **Spec**: does the code faithfully implement the originating issue / spec?
- **Falsify** — construct inputs and states specifically designed to break the changes. Test failure paths before happy path. "Passed" is not the bar; "didn't test the failure" is the risk. Within this axis, run a **silent-failure hunt**: swallowed errors are the failure paths tests miss most. Hunt empty `catch {}` blocks, errors folded into `null`/empty arrays with no context, dangerous fallbacks (`.catch(() => [])`, default values that hide the real failure), lost stack traces, generic rethrows, missing async handling, and missing timeout/rollback around network, file, and DB paths.

The Standards and Spec axes run as **parallel sub-agents** so they don't pollute each other's context, then this skill aggregates their findings. Falsify runs as a third parallel sub-agent when the orchestrator requests it (see axis selection in the invocation prompt).

## Resource Guide

Running the Falsify axis, or consuming audit findings, read `references/falsify-pitfalls.md` first — knowledge-base-distilled review pitfalls (pin the defect's layer, red-before-green regression tests, cover the defense mechanism's own state machine, coverage figures need a `--cov` scope, audit output is a stale snapshot). Pass this reference into the Falsify sub-agent brief.

## Reviewer posture

The reviewer is an **auditor, not a collaborator**. 
- Do not propose fix suggestions or alternative implementations — report what's wrong, not how to fix it.
- Blocking issues are returned to the implementer for repair; the reviewer's job is to find them, not fix them.
- Distinguish hard violations (documented standard breaches) from judgement calls (smell heuristics).

The issue tracker should have been provided to you. If `docs/agents/issue-tracker.md` is missing, tell the user to run `/setup-matt-pocock-skills`.

## Report credibility gate

The reviewer is only as useful as its findings are trustworthy. An LLM reviewer's primary failure mode is manufactured findings, filler nits, and severity inflation — not missed ones. Enforce these rules on every axis:

- **Confidence filter.** Report a finding only if you are >80% sure it is a real problem for this codebase. Skip stylistic preferences unless they violate project conventions.
- **Pre-Report Gate (four questions).** Before writing any finding, all four must be answerable; if any is "no" or "unsure", downgrade severity or drop the finding:
  1. Can I cite the exact file and line?
  2. Can I name the concrete failure mode — input, state, and bad outcome? If you can't name the trigger, you are pattern-matching, not reviewing.
  3. Have I read the surrounding context (callers, imports, tests)? Many apparent issues are already handled one frame up or guarded by a type.
  4. Is the severity defensible? A missing docstring is never HIGH; a single bad `any` in a test fixture is never CRITICAL. Severity inflation erodes trust faster than missed findings.
- **HIGH/CRITICAL require proof** — exact snippet + line, the specific input→state→outcome scenario, and why existing guards (types, validation, framework defaults) don't catch it. Missing any of the three: demote to MEDIUM or drop.
- **Zero findings is a valid outcome.** A clean review is a clean review; do not manufacture findings to justify the invocation.
- **Skip the known false positives** unless this codebase gives you specific evidence to the contrary: "consider adding error handling" on calls whose error path is handled upstream (framework middleware, error boundaries, top-level try/catch); "missing input validation" on internal functions whose callers already validate; well-known constants (HTTP status codes, common timeouts, array index 0); exhaustive switches or generated code flagged as "too long"; N+1 queries on fixed-cardinality loops or batched paths; fire-and-forget calls (logging, metrics, queue pushes) flagged as "missing await"; `Math.random()` in non-cryptographic contexts; `eval`/`Function` in an explicitly code-loading plugin surface.

When tempted to flag one of the above, ask: "would a senior engineer on this team actually change this in review?" If no, skip it.

The gate applies to every sub-agent: the briefs in step 4 must carry it verbatim.

## Severity markers

Every finding opens with one marker, mapped to the severity language above:

- 🔴 blocker — must fix before merge: a documented-standard breach, exploitable flaw, data-loss/corruption risk, or broken contract.
- 🟡 suggestion — a real problem worth fixing, not merge-blocking: missing validation, unclear logic, duplication to extract.
- 💭 nit — optional polish: naming, doc gaps, style a linter does not already enforce.

Format every finding as `🔴 [Axis] file:line — what is wrong. Why: ...`. Severity inflation erodes trust faster than missed findings: a missing docstring is never 🔴, a single bad `any` in a test fixture is never 🔴.

## Process

### 1. Pin the fixed point

Whatever the user said is the fixed point (a commit SHA, branch name, tag, `main`, `HEAD~5`, etc.). If they didn't specify one, ask for it.

Capture the diff command once: `git diff <fixed-point>...HEAD` (three-dot, so the comparison is against the merge-base). Also note the list of commits via `git log <fixed-point>..HEAD --oneline`.

Before going further, confirm the fixed point resolves (`git rev-parse <fixed-point>`) and the diff is non-empty. A bad ref or empty diff should fail here, not inside two parallel sub-agents.

### 2. Identify the spec source

Look for the originating spec, in this order:

1. Issue references in the commit messages (`#123`, `Closes #45`, GitLab `!67`, etc.), fetched via the workflow in `docs/agents/issue-tracker.md`.
2. A path the user passed as an argument.
3. A spec file under `docs/`, `specs/`, or `.scratch/` matching the branch name or feature.
4. If nothing is found, ask the user where the spec is. If they say there isn't one, the **Spec** sub-agent will skip and report "no spec available".

### 3. Identify the standards sources

Anything in the repo that documents how code should be written, such as `CODING_STANDARDS.md` or `CONTRIBUTING.md`.

On top of whatever the repo documents, the Standards axis always carries the **smell baseline** below: a fixed set of Fowler code smells (_Refactoring_, ch.3) that applies even when a repo documents nothing. Two rules bind it:

- **The repo overrides.** A documented repo standard always wins; where it endorses something the baseline would flag, suppress the smell.
- **Always a judgement call.** Each smell is a labelled heuristic ("possible Feature Envy"), never a hard violation. Like any standard here, skip anything tooling already enforces.

Each smell reads *what it is* → *how to fix*; match it against the diff:

- **Mysterious Name**: a function, variable, or type whose name doesn't reveal what it does or holds. → rename it; if no honest name comes, the design's murky.
- **Duplicated Code**: the same logic shape appears in more than one hunk or file in the change. → extract the shared shape, call it from both.
- **Feature Envy**: a method that reaches into another object's data more than its own. → move the method onto the data it envies.
- **Data Clumps**: the same few fields or params keep travelling together (a type wanting to be born). → bundle them into one type, pass that.
- **Primitive Obsession**: a primitive or string standing in for a domain concept that deserves its own type. → give the concept its own small type.
- **Repeated Switches**: the same `switch`/`if`-cascade on the same type recurs across the change. → replace with polymorphism, or one map both sites share.
- **Shotgun Surgery**: one logical change forces scattered edits across many files in the diff. → gather what changes together into one module.
- **Divergent Change**: one file or module is edited for several unrelated reasons. → split so each module changes for one reason.
- **Speculative Generality**: abstraction, parameters, or hooks added for needs the spec doesn't have. → delete it; inline back until a real need shows.
- **Message Chains**: long `a.b().c().d()` navigation the caller shouldn't depend on. → hide the walk behind one method on the first object.
- **Middle Man**: a class or function that mostly just delegates onward. → cut it, call the real target direct.
- **Refused Bequest**: a subclass or implementer that ignores or overrides most of what it inherits. → drop the inheritance, use composition.

### 4. Spawn the sub-agents in parallel

Every brief below must carry the **Report credibility gate** and the **Severity markers** from above (verbatim): confidence filter, Pre-Report Gate, HIGH/CRITICAL-proof requirement, zero-findings-are-valid, the false-positive skip list, and the 🔴/🟡/💭 finding format. The gate and markers are what keep a multi-axis review from collapsing into noise.

**Standards sub-agent prompt** should include:

- The full diff command and commit list.
- The list of standards-source files you found in step 3, **plus the smell baseline from step 3** pasted in full (the sub-agent has no other access to it).
- The brief: "Report, per file/hunk where relevant, (a) every place the diff violates a documented standard: cite the standard (file + the rule); and (b) any baseline smell you spot: name it and quote the hunk. Distinguish hard violations from judgement calls: documented-standard breaches can be hard, but baseline smells are always judgement calls, and a documented repo standard overrides the baseline. Skip anything tooling enforces. Under 400 words."

**Spec sub-agent prompt** should include:

- The diff command and commit list.
- The path or fetched contents of the spec.
- The brief: "Report: (a) requirements the spec asked for that are missing or partial; (b) behaviour in the diff that wasn't asked for (scope creep); (c) requirements that look implemented but where the implementation looks wrong. Quote the spec line for each finding. Under 400 words."

If the spec is missing, skip the Spec sub-agent and note this in the final report.

**Falsify sub-agent prompt** (when the axis is requested) should include:

- The diff command and commit list.
- The brief: "Construct inputs and states specifically designed to break these changes. Test failure paths before happy path; a test or code path that only proves the happy case is not evidence. Also hunt silent failures: empty `catch {}` blocks, errors folded into `null`/empty arrays with no context, dangerous fallbacks (`.catch(() => [])`, default values that hide the real failure), lost stack traces, generic rethrows, missing async handling, and missing timeout/rollback around network, file, and DB paths. For every finding cite the exact line, the input→state→outcome scenario, and why existing guards don't catch it. Under 400 words."

### 5. Aggregate

Present the reports under `## Standards` and `## Spec` headings, verbatim or lightly cleaned. When the Falsify axis was requested, present its findings under a `## Falsify` heading as well. Do **not** merge or rerank findings, because the axes are deliberately separate (see _Why two axes_).

End with a one-line summary: total findings per axis, and the worst issue _within each axis_ (if any). Don't pick a single winner across axes: that's the reranking the separation exists to prevent.

## Why two axes

A change can pass one axis and fail the other:

- Code that follows every standard but implements the wrong thing → **Standards pass, Spec fail.**
- Code that does exactly what the issue asked but breaks the project's conventions → **Spec pass, Standards fail.**

Reporting them separately stops one axis from masking the other.