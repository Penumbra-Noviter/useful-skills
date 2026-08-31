---
name: ask-matt
description: Ask which skill or flow fits your situation. A router over the skills in this repo.
disable-model-invocation: true
---

# Ask Matt

You don't remember every skill, so ask.

A **flow** is a path through the skills. Most paths run along one **main flow**, and two **on-ramps** merge onto it. Everything else is standalone, or a vocabulary layer that runs underneath.

## The main flow: idea → ship

The route most work travels. You have an idea and want it built.

1. **`/grill-with-docs`** sharpens the idea by interview. Start here whenever you are **working in a working directory**: it's stateful, retaining what it learns in `CONTEXT.md` and ADRs. (No working directory? Use `/grill-me` instead, covered under Standalone. Both run the same `/grilling` primitive; `grill-with-docs` is the one that leaves a paper trail, which makes it the better of the two whenever a repo is there to leave it in.)
2. **Branch: can you settle every question in conversation?** If a question needs a runnable answer (state, business logic, a UI you have to see), detour through a prototype, bridged by **`/handoff`** in both directions (a prototype lives in its own directory, which is exactly what `/handoff` is for; see Phase boundaries):
   - **`/handoff`** out, then open a fresh session against that file,
   - **`/prototype`** to answer the question with throwaway code,
   - **`/handoff`** back what you learned, and reference it from the original idea thread.
3. **Branch: is this a multi-session build?**
   - **Yes** → **`/to-spec`** (turn the thread into a spec), then **`/to-tickets`** to split it into tracer-bullet tickets, each declaring its **blocking edges**. On a local tracker that's one file per ticket under `.scratch/<feature>/issues/`, worked blockers-first by hand; on a real tracker the edges become native blocking links, so any ticket whose blockers are done can be grabbed: kick off **`/implement`** per ticket, **`/clear`ing context between each one**. Each ticket is self-contained, so the last one's context is disposable.
   - **No** → **`/implement`** right here, in the same context window.

   Either way, **`/implement`** builds each issue by driving **`/tdd`** internally (one red-green slice at a time), then closes out by running **`/code-review`**, a two-axis review (Standards + Spec) of the diff, before committing. Reach for **`/tdd`** on its own when you just want to build a concrete behaviour test-first without a full spec, and **`/code-review`** on its own whenever you want to review a branch or PR against a fixed point.

### Context hygiene

Keep steps 1–3 in **one unbroken context window** (don't compact or clear until after `/to-tickets`) so the grilling, spec, and tickets all build on the same thinking. Each `/implement` then starts fresh, working from the ticket.

The limit on this is the **[smart zone](https://www.aihero.dev/ai-coding-dictionary/smart-zone)**: the window (~150k tokens on state-of-the-art models) within which the model still reasons sharply. If a session approaches it before `/to-tickets`, don't push on degraded; `/compact` at the nearest phase boundary and carry on (see Phase boundaries).

## On-ramps

A starting situation that generates work, then merges onto the main flow.

- **Bugs and requests piling up** → **`/triage`**. It moves issues through triage roles and produces agent-ready issues, which **`/implement`** later picks up.

  Triage is only for issues **you didn't create**: bug reports, incoming feature requests, anything that arrives raw. Tickets that `/to-tickets` produced are already agent-ready, so **don't triage them**.

- **Something's broken** → **`/diagnosing-bugs`**. For the hard ones: the bug that resists a first glance, the intermittent flake, the regression that crept in between two known-good states. It refuses to theorise until it has a **tight feedback loop** (one command that already goes red on *this* bug), then fixes with a regression test. Its post-mortem hands off to **`/improve-codebase-architecture`** when the real finding is that there's no good seam to lock the bug down.

- **A huge, foggy effort: a greenfield project or a huge feature build, too big for one session** → **`/wayfinder`**, the most cognitively demanding flow here. When the way from here to the destination isn't visible yet, it charts a **shared map** of **decision tickets** on the issue tracker and resolves them one at a time, producing **decisions, not deliverables**, until the fog is pushed back and the way is clear. Where **`/grill-with-docs`** sharpens an idea you can hold in one session, wayfinder is for the idea you can't, and it's slower and denser, so save it for exactly that, never a well-scoped feature.

  When the map clears, **it hands off, it doesn't build**: merge onto the main flow at **`/to-spec`**, which collapses the map's linked decisions into a buildable plan, then `/to-tickets` and `/implement` as usual. Looping the map straight into `/implement` skips that collapse and throws the linked detail away, so go straight to `/implement` only when the effort turned out genuinely small.

## Codebase health

Not feature work, just upkeep.

- **`/improve-codebase-architecture`** runs whenever you have a spare moment to keep the codebase good for agents to operate in. It surfaces **deepening opportunities**; picking one _generates an idea_ you can take into the main flow at `/grill-with-docs`. It's the survey that finds the candidates; **`/codebase-design`** (below) is the bench you design the chosen one on.
- **`/improve-python-architecture`** is the same deepening scan scoped to a Python codebase: structural report first, then grill the candidate you pick. Python repo → this one; anything else → `/improve-codebase-architecture`.

## Vocabulary underneath

Two model-invoked references that run *beneath* the other skills, each the single source of truth for its vocabulary. Reach for them directly when the **words**, not the process, are the problem; or let the skills above pull them in.

- **`/domain-modeling`**: sharpen the project's *domain* language: challenge a fuzzy term, resolve an overloaded word ("account" doing three jobs), record a hard-to-reverse decision as an ADR. It's the active discipline `/grill-with-docs` drives to keep `CONTEXT.md` a clean glossary.
- **`/codebase-design`** is the deep-module vocabulary (module, interface, depth, seam, adapter, leverage, locality) for designing a module's *shape*: a lot of behaviour behind a small interface at a clean seam. `/tdd` and `/improve-codebase-architecture` both speak it.

## Phase boundaries

A **phase** is a chunk of work inside a session: the grilling, the implementation, the QA. At the **boundary** between two of them you have five options, and picking between them is the fuzziest decision in this whole map:

- **Continue**: stay put. Costs nothing, loses nothing.
- **`/clear`**: empty the window, when nothing here matters to what's next.
- **`/handoff`** writes a portable markdown file. Narrow: only for a **new harness**, a **new directory**, a **colleague**, or forking a side task **mid-phase**. What it buys is portability.
- **Subagent**: send a tightly-scoped task to its own window and get a report back.
- **`/compact`** compresses this context and seeds a fresh session with it. The **default**, at the bottom of the tree rather than the first reach.

Read [PHASE-BOUNDARIES.md](PHASE-BOUNDARIES.md) for the ordered tree: the five questions, the reasoning behind each branch, and why the primary-source cost makes **Continue** the one to rule out first. Make the decision **at** a boundary; mid-phase, continue or split the rest into subagents.

## Standalone

Off the main flow entirely.

- **`/grill-me`**: the same relentless interview as `/grill-with-docs`, but **stateless**: it saves nothing locally and builds no `CONTEXT.md`. Reach for it when you are **not working in a working directory** (sharpening a plan, a design, a piece of writing, anything with no repo under it). If you are in a working directory, use `/grill-with-docs` instead: it runs the same interview and leaves a paper trail, so it is strictly the better one.
- **`/grilling`** is the interview primitive itself: rounds, the frontier, facts are the agent's job and decisions are yours. `/grill-me` and `/grill-with-docs` are the two named ways in, and `/triage`, `/wayfinder` and `/improve-codebase-architecture` all run it internally. Reach for it directly only when you want the interview with no wrapper around it.
- **`/loop-me`** is `/grilling` scoped to this workspace: grill me about the specs for the workflows I want to build here, without leaving the directory. In-repo counterpart of `/grill-me`'s stateless interview.
- **`/resolving-merge-conflicts`** works an in-progress merge or rebase conflict hunk by hunk, resolving by **intent** traced to each side's primary source rather than by picking lines, then finishes the operation. It never runs `--abort`. Standalone and off every flow: reach for it when you are already mid-conflict.
- **`/prototype`** is a small, throwaway program that answers one design question: does this state model feel right, or what should this UI look like. Throwaway is a constraint on how the code is written, not a promise to destroy it: the answer folds into the real code, and the prototype itself is kept as a **primary source** on a `prototype/<name>` branch out of main, pointed at from the implementation issue. It's the detour in step 2 of the main flow, but reach for it any time a design question is hard to settle on paper.
- **`/research`**: delegate reading legwork to a **background agent**: it investigates a question against **primary sources**, then leaves a cited Markdown file in the repo. Keep working while it reads. The file it produces is something to take *into* the main flow at `/grill-with-docs`, since research feeds the thinking rather than replacing it.
- **`/to-questionnaire`** comes in when the thing blocking you isn't in your head or the codebase but in **someone else's**, and it writes them a questionnaire to fill in. It's the inverse of `/grill-me`: instead of interviewing you about the subject, it interviews you about the **send** (who it's going to, what you need back) and aims the questions at the gap. What comes back is material for `/grill-with-docs` or `/to-spec`.
- **`/wizard`** is for the steps only a **human** can take: provisioning infrastructure, setting up credentials or CI secrets, clicking through an unfamiliar third-party dashboard, running a one-off migration or cutover. It generates an interactive bash script that opens each URL, captures each value, and writes it into `.env` and GitHub secrets, so the procedure stops being something you re-explain to an agent every time. Model-invoked, so the agent reaches for it the moment it hits a wall only you can pass. If the agent could just do it itself, it should; this is for where a human is genuinely in the loop.
- **`/wait-what`** is the corrective for a message that didn't land. Use it mid-conversation, inside any other skill, and the agent re-pitches what it just said with the context you were missing, in plain English, using the `CONTEXT.md` vocabulary. It works after the fact; `/grill-with-docs` is the upfront cure, because a shared language agreed early is what stops the jargon arriving at all.
- **`/teach`**: learn a concept over multiple sessions, using the current directory as a stateful workspace.
- **`/universal-exam-cram-coach`**: structured last-minute exam prep — parse materials/outline into a wiki + question bank, drill with scoring, review mistakes. Reach for it when a deadline drives the learning, not the other way around.
- **`/claude-handoff`** (distinct from `/handoff`): hands the **whole current conversation** to a fresh background agent that picks the work up immediately — forward progress without writing a portable file.
- **`/skill-authoring`** is the reference for writing documents agents consume: skills, AGENTS.md, pointed-at docs.

## Other families

Beyond the engineering flow. Ask here when the work isn't shipping application code: content and design, intelligence and reverse engineering, the skill ecosystem itself, one-shot tooling, and the plugin families that live outside this repo. Routing rule is the same as everywhere in this map — each entry names its trigger, not its whole manual.

### Content & design

- **`/writing`**: the orchestration entry for long-form writing. It checks which piece already exists and routes to the right stage: `/writing-fragments` (explore, mine raw material), `/writing-shape` (exploit, linear paragraphs), `/writing-beats` (exploit, narrative beats). Long article/essay/story → start here.
- **`/finesse-ui`**: high-craft web interfaces — brand surfaces, product UI, workflow UI, AI-assistant UI. Anti-slop; routes diagram requests to `/diagram-design`.
- **`/zine-ui`**: paper-zine visual language for photo/poetic briefs (拾景纸刊): photo collage, image distillation, abstract memory panels. "把这张照片做成页面" → here.
- **`/diagram-design`**: 27 diagram types (architecture, flow, sequence, ER, timeline, swimlane…) rendered as inline-SVG HTML, importable to draw.io.
- **`/open-kimi-ppt`**: presentations — create/edit/replicate/export, delivering a PPTD project folder plus a local .pptx.
- **`/obsidian-vault`**: search, create, and organize notes in the Obsidian vault with wikilinks and index notes.
- **`/cangjie-skill`**: distill a book/video/podcast/course into an executable skill set (拆书/蒸馏).

### Intel & reverse engineering

- **`/agent-reach`**: full-web research on any topic, and the **mandatory entry whenever a platform name or URL is shared** (小红书 etc.). Search/调研/查 → here, not the engineering flow.
- **`/research`** also investigates, but against high-trust primary sources, leaving a cited Markdown file in the repo (detailed under Standalone).
- **`/fetchflow`**: orchestrates scraping and reverse engineering toward one data target; pre-audits automation red lines before executing.
- **`/reverse-flow`**: guided RE of binaries, firmware, mobile apps, scripts, protocol captures, document samples. Malware/suspicious-file analysis also lives here.
- **`/museon-cli`**: social-media research, content, accounts, scheduling, publishing, automation, and performance review.

### Skill ecosystem & housekeeping

- **`/dao-skill`**: the meta-designer — design, audit, optimize, or evolve a skill; find a skill's root problem before refactoring it.
- **`/vibehub`**: translate vibe-coded descriptions into precise terminology mid-task (tooltip, hover…).
- **`/vision`**: identify/analyze local or web images via vision.js (fallback when the View agent is unavailable).
- **`/context-monitor`**: read current context/token usage to decide model switches.
- **`/distill-lesson`**: distill this session's lessons into atomic notes in the Obsidian knowledge base (沉淀/复盘).
- **`/neat-freak`**: knowledge & governance closeout — reconcile docs/rules/memory with code reality, audit workspace residue, produce a pending-deletion list for confirmation.
- **`/simplify-codebase`**: evidence-backed code simplification audit — dead code, duplicate state, redundant abstractions.
- **`/git-guardrails-claude-code`**: install Claude Code hooks that block destructive git commands (push, reset --hard, clean, branch -D).

### One-shot tooling (engineering ecosystem)

- **`/setup-matt-pocock-skills`** is the Precondition above — one-time repo bootstrap.
- **`/project-kickoff`** is the full engineering pipeline from one goal sentence: Grilling consensus → spec/tickets → parallel Implement agents → code-review → Neat cleanup. If the user says "启动项目 / 布置任务 / 开始这个工程" without a scoped ticket yet, that's this one — it pre-empts the main flow's manual steps 1–3.
- **`/setup-pre-commit`**: Husky + lint-staged (Prettier), typecheck, and tests on commit.
- **`/setup-ts-deep-modules`**: wire dependency-cruiser so each package is a deep module; implementation reaches main through entry-point files.
- **`/migrate-to-shoehorn`**: migrate test `as` assertions to @total-typescript/shoehorn.
- **`/scaffold-exercises`**: create exercise structures (sections/problems/solutions/explainers) that pass linting.

### Plugin families (outside this repo)

Provided by plugins, not files in this repo; amount to `family:skill` invocations.

- **`document-skills:docx`** / **`document-skills:pdf`** / **`document-skills:pptx`** / **`document-skills:xlsx`**: office-document workflows — Word edits with tracked changes, PDF production (reports/LaTeX/creative), PPTX via pptxgenjs/python-pptx, spreadsheet handling with a visual acceptance gate.
- **`browser-use:control-browser`**: main-agent-only browser automation — navigate, click, type, fill, screenshot, verify. Delegating to a subagent is forbidden.
- **`browser-use:web-gui-tester`**: GUI-based black-box frontend testing — simulate real user clicks/input/scrolling, verify by screenshot.
- **`android-emulator:android-dev`**: Android app build/run/inspect/light automation (screen capture, UI tree, logs, tap/swipe/type).

## Precondition

**`/setup-matt-pocock-skills`**: run before your first engineering flow to configure the issue tracker, triage labels, and doc layout the other skills assume. Custom issue trackers also work.
