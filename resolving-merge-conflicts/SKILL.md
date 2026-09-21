---
name: resolving-merge-conflicts
description: "Use when you need to resolve an in-progress git merge/rebase conflict."
---

1. **See the current state** of the merge/rebase. Check git history, and the conflicting files.

2. **Find the primary sources** for each conflict. Understand deeply why each change was made, and what the original intent was. Read the commit messages, check the PRs, check original issues/tickets.

3. **Resolve each hunk.** Preserve both intents where possible. Where incompatible, pick the one matching the merge's stated goal and note the trade-off. Do **not** invent new behaviour. Always resolve; never `--abort`. For each hunk, record which side's intent its resolution keeps (and why) — step 4 verifies the merge against those intents, not just against the compiler.

4. Discover the project's **automated checks** and run them, typically typecheck, then tests, then format. Fix anything the merge broke. Passing checks are not the completion bar: for each hunk's recorded intent, verify the merged code still exhibits the kept side's behaviour (and the other side's where it was meant to be preserved). If a resolution silently dropped behaviour the checks can't see — a merged branch that changes what the merged feature should do — fix it before committing.

5. **Finish the merge/rebase.** Stage everything and commit. If rebasing, continue the rebase process until all commits are rebased.
