---
name: code-review
description: "Review the changes since a fixed point (commit, branch, tag, or merge-base) along two axes: Standards (does the code follow this repo's documented coding standards?) and Spec (does the code match what the originating issue/spec asked for?). Runs both reviews in parallel sub-agents and reports them side by side. Use when the user wants to review a branch, a PR, work-in-progress changes, or asks to \"review since X\"."
---

Multi-axis review of the diff between `HEAD` and a fixed point the user supplies:

- **Standards**: does the code conform to this repo's documented coding standards?
- **Spec**: does the code faithfully implement the originating issue / spec?
- **Falsify** — construct inputs and states specifically designed to break the changes. Test failure paths before happy path. "Passed" is not the bar; "didn't test the failure" is the risk. Within this axis, run a **silent-failure hunt**: swallowed errors are the failure paths tests miss most. Hunt empty `catch {}` blocks, errors folded into `null`/empty arrays with no context, dangerous fallbacks (`.catch(() => [])`, default values that hide the real failure), lost stack traces, generic rethrows, missing async handling, and missing timeout/rollback around network, file, and DB paths.

Beyond the axes, this flow enforces **review-process disciplines** every axis shares: a deterministic file manifest (step 1), mandatory per-file coverage accounting, verbatim line anchoring, and a post-draft remove pass. They exist because an LLM reviewer's most common failures are silent — skipped files, drifted line numbers, and manufactured findings — and none of them shows up in the findings you do get.

The Standards and Spec axes run as **parallel sub-agents** so they don't pollute each other's context, then this skill aggregates their findings. Falsify runs as a third parallel sub-agent when the orchestrator requests it (see axis selection in the invocation prompt).

## Resource Guide

Running the Falsify axis, or consuming audit findings, read `references/falsify-pitfalls.md` first — knowledge-base-distilled review pitfalls (pin the defect's layer, red-before-green regression tests, cover the defense mechanism's own state machine, coverage figures need a `--cov` scope, audit output is a stale snapshot). Pass this reference into the Falsify sub-agent brief.

For language-specific do-not-report guidance, Standards and Falsify sub-agents read `references/negative-checklists.md`, taking the section matching the diff's languages (Python / TS·JS / Go today). It layers on top of the skip list in the credibility gate below.

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
- **Negative checklists layer on top of the skip list.** The skip list above is language-agnostic and heuristic. Sub-agents reviewing Python, TS/JS, or Go must additionally read the matching section of `references/negative-checklists.md` and honor its concrete "do not report" exclusions (e.g. mutable-default-argument patterns in a function that never mutates the argument; `.pyi` stub unused imports; Go timer `.Stop()` missing on Go 1.23+ where it is not a leak). A finding that trips an exclusion must carry diff evidence that proves the exclusion doesn't apply. The repo's own documented standards still override the checklists; anything tooling enforces is skipped regardless.

When tempted to flag one of the above, ask: "would a senior engineer on this team actually change this in review?" If no, skip it.

The gate applies to every sub-agent: the briefs in step 4 must carry it verbatim.

## The remove pass

Drafting findings and vouching for them are different jobs. After a sub-agent drafts its findings and before it reports them, it runs one remove pass:

1. Switch from reviewer to fact-checker. Your only job now is to remove comments the evidence **proves** wrong — not comments that are weak, low-value, or unprioritized.
2. The two mistakes are not equally bad: keeping an incorrect comment costs a reviewer a few seconds of attention; removing a correct comment silently destroys a real finding. It never reaches anyone, and nobody learns that it was dropped.
3. So when your evidence falls short of proof, **approve** (keep). "Suspicious", "I cannot verify this", "low value", "the flagged code looks fine to me", and "I would not have raised this" all mean keep. If the credibility gate says it's below reportable threshold, downgrade or drop it there — not here.
4. Record in your coverage table how many comments the remove pass cut and why, so the orchestrator can audit your deletion decisions.

The remove pass is deliberately asymmetric: it protects real findings from the reviewer's own later doubt. The credibility gate stops noise at the front door; the remove pass stops the reviewer from second-guessing correct findings at the back.

## Coverage discipline

An LLM reviewer's most common silent failure is reviewing the files it finds interesting and quietly skipping the rest. Every sub-agent must therefore account for every file in the manifest from step 1:

- Build a checklist from the manifest; use `(path, status)` as each entry's identity (workspace mode can report the same path twice — staged deletion plus untracked recreation).
- Give **every** entry its own pass. Reviewing an implementation file does not cover its header, interface, or configuration counterpart; a file being small or a secondary member of the change is not a reason to skip it. Zero-finding files are the point of the review, not a failure — a file marked reviewed with no findings is valid.
- A file may end as `skipped` only with a concrete reason (excluded as generated/test/lock in step 1, moved in a pure rename, deletion with no new content).
- Report a coverage table at the end of your findings: `path → reviewed | skipped(+reason)`, then `reviewed_files / total_files / coverage_rate`. One line per file.

The orchestrator reconciles all sub-agent coverage tables against the manifest in step 5; any file never marked reviewed on any axis is flagged `UNREVIEWED` in the final report.

## Line anchoring

Position drift is the second most common failure mode after skipped files: findings that are real but land on the wrong line or file cost the implementer a hunt and erode trust in every later finding. Anchor discipline:

- Every finding quotes the **exact snippet** (the verbatim lines from the diff, not a paraphrase) and cites the **new-file** line number, `file:line`.
- No snippet, no finding: if you cannot quote the code you mean, you do not yet have a finding. Paraphrase is the leading cause of drift — the same bug at line 82 reported "around line 70" because the reviewer summarized.
- For diff-only hunks, quote the `+` lines exactly. For findings in unchanged context, quote the unchanged lines.
- When you must locate a finding whose snippet spans deleted lines, anchor to the nearest surviving new-file line and say so.
- Unanchored by necessity → downgrade one severity. The orchestrator verifies every 🔴 against the working tree in step 5.

## Severity markers

Every finding opens with one marker, mapped to the severity language above:

- 🔴 blocker — must fix before merge: a documented-standard breach, exploitable flaw, data-loss/corruption risk, or broken contract.
- 🟡 suggestion — a real problem worth fixing, not merge-blocking: missing validation, unclear logic, duplication to extract.
- 💭 nit — optional polish: naming, doc gaps, style a linter does not already enforce.

Format every finding as `🔴 [Axis] file:line — what is wrong. Why: ...`. Severity inflation erodes trust faster than missed findings: a missing docstring is never 🔴, a single bad `any` in a test fixture is never 🔴.

## Process

### 1. Pin the fixed point and build the review-file manifest

Whatever the user said is the fixed point (a commit SHA, branch name, tag, `main`, `HEAD~5`, etc.). If they didn't specify one, ask for it.

Capture the diff command once: `git diff <fixed-point>...HEAD` (three-dot, so the comparison is against the merge-base). Also note the list of commits via `git log <fixed-point>..HEAD --oneline`.

Before going further, confirm the fixed point resolves (`git rev-parse <fixed-point>`) and the diff is non-empty. A bad ref or empty diff should fail here, not inside two parallel sub-agents.

Then build the **review-file manifest** every sub-agent must cover — `git diff <fixed-point>...HEAD --name-status`, plus `--numstat` where you need size or binary detection. Apply a deterministic filter before listing files. The filter is a hard constraint, not a suggestion; the manifest the sub-agents receive reflects only this filter, not the reviewer's judgement:

1. **Binary files** — `git` reports `-`/`-` for their numstat; drop.
2. **Test files** — `**/*_test.go`, `**/*.test.{js,jsx,ts,tsx}`, `**/*.spec.{js,jsx,ts,tsx}`, `**/__tests__/**`, `**/*_test.py`, `**/test_*.py`, `**/*_spec.rb`, `**/*Test.java`, `**/*Tests.java`, `**/src/test/**`, `**/spec/**`. These stay readable as *context* by sub-agents (a test can prove a contract), but they are not comment targets.
3. **Generated / dependency trees** — `**/generated/**`, `**/vendor/**`, `**/node_modules/**`, `**/dist/**`, `**/build/**`, `**/target/**`.
4. **Lock and manifest lockfiles** — `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `poetry.lock`, `Cargo.lock`, `go.sum`.
5. **Oversized** — a single diff larger than roughly 2000 changed lines is marked `oversized` in the manifest (kept as a stub entry, not silently dropped): it gets a coverage line of its own so nobody pretends it was reviewed.

Any file the user explicitly named overrides the filter and is kept. If the manifest holds more than ~12 files or ~400 total changed lines, mark the run `LARGE_CHANGESET` — the Falsify axis then runs plan-first (see step 4).

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

Every brief below must carry, verbatim: the **Report credibility gate** (including the negative-checklists rule), the **Severity markers**, the **remove pass**, the **coverage discipline**, and the **line anchoring** rules from above. These are what keep a multi-axis review from collapsing into noise — and what stop it from silently skipping files or drifting off their actual lines. Every brief also receives the **review-file manifest from step 1** in full, with status and +/- counts, and must end its findings with its coverage table. No comment may target a file outside the manifest, however loudly the context tools argue for it; context is for understanding, not for comment targets. The Falsify brief additionally receives `references/falsify-pitfalls.md`; the Standards and Falsify briefs additionally receive the relevant language section of `references/negative-checklists.md` (the orchestrator resolves it by the diff's languages).

**Standards sub-agent prompt** should include:

- The full diff command and commit list.
- The review-file manifest.
- The list of standards-source files you found in step 3, **plus the smell baseline from step 3** pasted in full (the sub-agent has no other access to it), plus the resolved language negative checklist.
- The brief: "Report, per file/hunk where relevant, (a) every place the diff violates a documented standard: cite the standard (file + the rule); and (b) any baseline smell you spot: name it and quote the hunk. Distinguish hard violations from judgement calls: documented-standard breaches can be hard, but baseline smells are always judgement calls, and a documented repo standard overrides the baseline. Skip anything tooling enforces. Cover every manifest entry; end with your coverage table. Findings under 400 words (coverage table separate)."

**Spec sub-agent prompt** should include:

- The diff command and commit list.
- The review-file manifest.
- The path or fetched contents of the spec.
- The brief: "Report: (a) requirements the spec asked for that are missing or partial; (b) behaviour in the diff that wasn't asked for (scope creep); (c) requirements that look implemented but where the implementation looks wrong. Quote the spec line for each finding. Cover every manifest entry; end with your coverage table. Findings under 400 words (coverage table separate)."

If the spec is missing, skip the Spec sub-agent and note this in the final report.

**Falsify sub-agent prompt** (when the axis is requested) should include:

- The diff command and commit list.
- The review-file manifest.
- The language negative checklist section (so its exclusions are honored while hunting failures).
- The brief: "Construct inputs and states specifically designed to break these changes. Test failure paths before happy path; a test or code path that only proves the happy case is not evidence. Also hunt silent failures: empty `catch {}` blocks, errors folded into `null`/empty arrays with no context, dangerous fallbacks (`.catch(() => [])`, default values that hide the real failure), lost stack traces, generic rethrows, missing async handling, and missing timeout/rollback around network, file, and DB paths. For every finding cite the exact line, the input→state→outcome scenario, and why existing guards don't catch it. Cover every manifest entry; end with your coverage table. Findings under 400 words (coverage table separate)."
- If the run was marked `LARGE_CHANGESET` in step 1, prepend to the brief: "Start with a plan section: the three riskiest areas of the change and the verification strategy for each (which files, which states, which inputs). Then execute it. Keep the plan in the report; findings must trace to a planned risk or explicitly note they surfaced outside it."

### 5. Aggregate

Reconcile, verify, then present.

**Reconcile coverage.** Build the union of the three coverage tables and compare it against the step-1 manifest. Any manifest file never marked `reviewed` on any axis gets a `UNREVIEWED` note in the summary — review it at this point if it is cheap, or list it explicitly as open.

**Verify anchors.** For every 🔴 finding, confirm the quoted snippet exists at the cited `file:line` in the working tree (read the file, or `git grep -n` a distinctive line from the snippet). A 🔴 whose snippet does not match its cited location is demoted to 🟡 or dropped, per the gate.

Then present the reports under `## Standards` and `## Spec` headings, verbatim or lightly cleaned. When the Falsify axis was requested, present its findings under a `## Falsify` heading as well. Do **not** merge or rerank findings, because the axes are deliberately separate (see _Why two axes_).

End with a one-line summary: total findings per axis, the worst issue _within each axis_ (if any), and the coverage reconciliation result (X/Y files reviewed across axes; Z flagged UNREVIEWED). Don't pick a single winner across axes: that's the reranking the separation exists to prevent.

## Why two axes

A change can pass one axis and fail the other:

- Code that follows every standard but implements the wrong thing → **Standards pass, Spec fail.**
- Code that does exactly what the issue asked but breaks the project's conventions → **Spec pass, Standards fail.**

Reporting them separately stops one axis from masking the other.