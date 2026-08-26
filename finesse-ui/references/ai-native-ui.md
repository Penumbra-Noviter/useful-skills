# AI-Native UI — Chat, Agent, Assistant Surfaces

The product register's **assistant** morphology. Where `product-ui.md` covers the page you **read** and `workflow-ui.md` covers the page you **operate**, this file covers the page you **converse with** — an AI chat surface, an agent task panel, a streamed answer with sources, a human-in-the-loop approval. Load it **on top of** `product-ui.md` (the substrate, base tables, forms, interaction states) + the shared craft floor.

> **Inherits everything from** `product-ui.md`'s §0 substrate and §2–§5, the universal craft floor, and the cheapness blacklist. Palette from `product-palettes.md`. SPECTACLE 1–3; DENSITY 6–8. Fonts + icons re-route through `stack-defaults.md` (§3) — the source corpus runs Inter + Tailwind; that's a library choice, not a pattern.
>
> **Distilled from** the path-referenced **beautifului** corpus (MIT © Shane Levine, 2026 — `design-md/beautifului/DESIGN.md` + the live gallery at https://www.beautifului.dev, source repo `github.com/slev12397/beautiful-ui`). Read the corpus for shipped implementations; this file is the pattern layer. Lift patterns, not files; keep the MIT attribution when copying code.
>
> **Covers:** AI chat/assistant surfaces · streamed answers · thinking/reasoning traces · agent task logs · tool-call chips · human-in-the-loop approvals · recommendation cards · retrieval context cards · prompt composers (product register, **assistant** side). **Adjacent:** stacks on `product-ui.md` (read-side substrate) · `workflow-ui.md`'s commit discipline carries into approval flows · `theming.md` for a light/dark toggle. **Does not cover:** read-side dashboard morphology (`product-ui.md` §1) · one-shot commit flows (`workflow-ui.md`) · manage-side consoles (`admin-console.md`) · brand/grain/vignette spectacle (brand register).

---

## 0. Is this an assistant page?

The product-register split is **per page, by the user's loop**:

| Page job | User's loop | Home |
|----------|-------------|------|
| **read** — monitor, analyze | "look → understand" | `product-ui.md` |
| **manage** — list, filter, edit | "find row → act → next row" | `admin-console.md` |
| **commit** — one consequential action | "fill → commit → done" | `workflow-ui.md` |
| **assistant** — converse with an agent | "**prompt → watch it work → review/approve**" | **this file** |

The tell: the page's spine is a **conversation or a live agent run**, and the user's decisions land on the agent's *output* (accept / reject / redirect / ask again) rather than on forms or rows. A chat window, a copilot sidebar, an agent task console, a RAG answer with citations, a "let the AI draft this and I'll approve" surface — all assistant. A dashboard that merely has a chat widget bolted on is still read; the assistant file earns its place when the *conversation is the primary job*, not a sidebar garnish.

Two moves decide it: **does the user prompt something, and does the outcome depend on reviewing streamed/agent-produced content?** Yes on both → here.

---

## 1. The token layer — what makes an AI surface read as instrument-grade

Distilled from beautifului's `globals.css`. This is the substrate an assistant surface sits on — deliberately quieter than a brand page, denser than a dashboard's prose.

- **Cool near-white canvas, white cards, hairline borders.** The page sits on a *cool, blue-tinted* off-white (lightness ~0.96–0.985 in OKLCH), cards are near-pure surface, and every separation is a **solid hairline** (`--line` at ~0.95 lightness, a `--line-strong` at ~0.91) — crisp, not alpha-smudged. The cool tint is what stops it reading as a warm editorial or a grey admin default.
- **A three-step ink ramp for text hierarchy.** Near-black ink (`L≈0.25`), a mid grey for secondary, a light grey for tertiary/muted. No more than three text tones on a surface; tertiary is for metadata, captions, timestamps.
- **Semantic color as a condiment, with same-hue tints.** Green / orange / red each carry a **same-hue tint** (the hue at ~0.14–0.02 alpha over surface) used as the status chip fill — the tint is derived from the semantic hue, not a pastel you pick. Semantic colors stay functional (status, success/fail), never the page's identity; the brand accent owns CTAs.
- **Radius is a disciplined scale, not a coin-flip.** chip 6px · control 8px · card 10px · window 14px. The assistant's small instrument surfaces use the low end; only the outermost window/card goes to 14. Lock the scale once.
- **Strong easing as the default.** `cubic-bezier(0.23, 1, 0.32, 1)` (strong-out) for entrances and transitions — built-in easings are too weak for a surface that animates a lot of state (streaming, task progress). One in-out curve for reveals.
- **Elevation = hairline ring + layered shadow; dark mode flips the ring to translucent light.** A surface floats via a **solid 1px ring** (not a border) plus a soft multi-layer shadow. In dark mode the ring becomes a **low-alpha white** (0.10–0.15) and the shadow deepens — the ring paints over what's behind the element, so elevation reads as one continuous graduated stroke. This is the "smooth-shadow-ring" idea: ring brightness + shadow depth, not a single drop shadow.
- **`tabular-nums` everywhere numbers tick** — elapsed timers, counts, confidence, task metrics. A mono-figure count that jitters as it updates reads broken.
- **Status regions announce progress.** Loaders and task rows use `role="status"`; anything that completes/fails mid-session announces it. A chat/agent surface is *lived in* — screen-reader users are following the same live updates.

---

## 2. The assistant surface morphology

The assistant register has a distinct spine, not the dashboard's sidebar-of-cards. Assemble from these, in this order:

1. **The conversation shell.** The primary frame is a **panel** (not a full-bleed dashboard) holding the message list, with a **composer pinned at the bottom**. Tabs split sub-conversations (e.g. "Flavors" / "Suppliers"). The panel is the window; content scrolls, the composer stays.
2. **Streamed answers with an anatomy.** A streamed reply isn't a static paragraph — it reveals progressively and carries its **evidence on the surface**: inline **source links** (openable), a row of **action buttons**, and **follow-up suggestions** as chips below. The sources are visible by default, not hidden in a footnote.
3. **Thinking traces that expand, don't hide.** Reasoning is a **collapsible trace** above/inside the answer — with an explicit state axis (steps / reasoning / search / coding), each step expandable. The failure mode to avoid is a "thinking…" spinner that reveals nothing; the pattern is a trace the user can open, skim, and close.
4. **Tool calls as compact chips with a detail layer.** Each tool call (a code write, a search, a build-and-verify) renders as a **chip** — verb + target — that expands to show **both input and outcome** (the diff, the result, ✓/✗). One collapsed line per call; the detail is one tap away.
5. **Agent tasks as status rows.** A live agent run renders as a **list of status rows** — title, running/completed/failed state, sub-steps with counts/metrics. The rows are the progress the user is waiting on; they must read at a glance and update live (`role="status"`).
6. **Human-in-the-loop as sequenced approval.** When the agent must ask before acting, the pattern is a **sequenced approval** — one question per card, each with concrete options + a free-text fallback, plus **skip / back / continue** so the user is never trapped. An approval that blocks with no way forward is broken.
7. **Recommendations with confidence and alternatives.** A recommendation card leads with the **primary suggestion**, signals **confidence** honestly, and lists **alternatives with verdicts** ("needs review", "no signal") before the accept/reject buttons. Confidence without a visible basis is a fake metric.
8. **Retrieval shown as attributed context.** Retrieved chunks render as **context cards** — the chunk text plus its **source file/kind** always visible. Retrieval is the trust surface of a RAG answer; attribution is not optional.
9. **The composer is a tool, not a textarea.** A proper prompt bar offers **@ source mentions, / commands, a model picker, attachments, dictation** — but only what the product actually supports. A composer advertising sources that don't resolve is the assistant version of a fake screenshot.

---

## 3. The AI-native component vocabulary

The primitives, each with its job. Build from these; don't improvise a chat surface out of generic cards.

| Primitive | Job | Failure mode it prevents |
|---|---|---|
| **Loading / thinking state** | signal long-running work with a label + elapsed time, not a blank spinner | dead time with no feedback |
| **Streaming text** | reveal an answer progressively with caret + evidence on the surface | a static wall of text passed off as live |
| **Thinking trace** | expandable reasoning with a state axis | a "thinking" spinner that hides the work |
| **Tool chip** | a collapsed tool call that expands to input + outcome | a black-box "agent did things" |
| **Task row** | live agent status: running / failed / completed + sub-steps | an opaque "working…" that can't be acted on |
| **Chat panel** | tabbed conversation + composer | a one-way static FAQ dressed as chat |
| **Prompt bar** | @ sources, / commands, model picker, dictation | a plain input pretending to be a composer |
| **Approval card** | sequenced human-in-the-loop with skip/back | a blocking prompt with no way forward |
| **Recommendation card** | one suggestion + confidence + alternatives + accept | a bare "should I do this?" with no basis |
| **Context card** | retrieved chunk + its source, always attributed | an answer with invisible provenance |
| **Diff table** | AI-proposed edits as a toggle-able table | a silent data mutation the user can't audit |
| **Code block** | line numbers + unified diff for AI-authored code | un-auditable AI code output |
| **Selection actions** | AI actions (explain / improve / shorten / change tone) on selected text | copying text out to another tool |

**Rules:**
- **Every agent-produced artifact is auditable** — a streamed claim links its source, a tool call shows its diff, a data edit is a toggle-able diff, a recommendation shows its basis. The user approves *evidence*, not trust.
- **States are explicit, not implied.** Loading has a terminal state; streaming has a settle state; tasks have running/failed/completed. A surface that can't say "done, here's what happened" is unfinished.
- **Live content is real content.** Real timers tick, real counts count, real statuses change. Static text styled as streaming, or fake `68%` confidence with no source, is the assistant version of `anti-cheap.md`'s fake-precise ban.

---

## 4. Interaction & motion craft

Feedback-only motion (SPECTACLE 1–3), each with a reduced-motion terminal state:

- **The streaming caret** — solid while streaming, blinks once it settles; reduced-motion freezes it (no blink). The caret is the honest signal of "still producing".
- **Streaming reveal** — newest characters may carry a **soft masked blur** on the leading edge so the reveal resolves smoothly (`.stream-tail`). Optional flourish; the caret alone is enough. Reduced-motion drops the blur and mask.
- **Pop-in for floating panels / approval cards** — `scale(0.95)→1` with strong-out easing, transform-origin at the edge the panel emerges from. Used for the collapsible traces, tool-chip details, filter menus — the small floating layers, not the whole page.
- **Elapsed-time loaders in tabular mono** — a label + a live `12.4s` counter, reduced-motion freezes the grid but the timer still ticks (time is information, not decoration).
- **Hover-neutralize on touch** — `@media (hover: none)` drops row/header hovers so a tap doesn't leave a stuck hover state. Any interactive list or table needs this.
- **Focus-visible on every control** — a visible accent focus ring on buttons, chips, menu items, selection rows. In a dense instrument surface the keyboard path is how power users move; it must be visibly navigable.
- **The theme flip is one repaint** — when swapping light/dark, freeze transitions for the swap (a `theme-switching` class that sets `transition: none`) so the flip is one clean repaint, not hundreds of mismatched color fades. (`theming.md` for the token-role rules.)

---

## 5. AI-native anti-patterns *(add to `product-ui.md` §9 / the shared blacklist)*

These are the assistant register's own traps, on top of the shared `anti-cheap.md`:

- **Static text styled as streaming** — a finished paragraph that pretends to reveal, or a blinking caret with nothing coming. Honesty: it's either live or it's static.
- **A "thinking…" that hides the work** — a spinner where an expandable trace belongs. The user should be able to open the reasoning; an opaque thinking state is the AI-native version of a fake screenshot.
- **Fake agent metrics** — `68% confidence`, `12/12` sub-steps, `4.1×` speed-up with no visible basis. Same ban as fake-precise numbers; on an agent surface it's worse because the user is being asked to *trust* on it.
- **Approval cards that dead-end** — a human-in-the-loop prompt with no skip / back / free-text path. Blocking without options is broken.
- **Invisible provenance** — a streamed claim or retrieved chunk with no source link, or a source that resolves nowhere. Attribution is the trust surface.
- **Composer advertising what it can't do** — a prompt bar with @ mentions / commands / dictation the product doesn't actually support. A tool bar that lies about its affordances is a UI defect.
- **Every answer the same card** — no chat interleaving rhythm, no distinction between a short confirm, a long streamed report, and a tool-call interlude. An assistant surface has texture; flattening it to one repeated bubble is the chat version of the identical-card-grid tell.
- **Uniform action-button rows** — four identical `Action` buttons on every streamed answer. Label actions with their verb+object; drop the ones that don't apply per-answer.

---

## 6. Assistant pre-flight *(in addition to the shared §10 / `product-ui.md` §10)*

- [ ] The primary loop is **prompt → watch → review/approve** (route-verified); a dashboard with a chat widget bolted on stayed in `product-ui.md`.
- [ ] Every streamed/live element has a **terminal state**, and `prefers-reduced-motion` freezes the animation while keeping time/count information (timer still ticks).
- [ ] Every agent artifact is **auditable** — streamed claims link sources, tool calls show input + outcome, data edits are diff-able, recommendations show a basis.
- [ ] Approval flows have **skip / back / continue** and no dead-ends; recommendations show alternatives + verdicts.
- [ ] Sources resolve somewhere real; context cards name their source file/kind.
- [ ] Loaders/tasks use `role="status"`; timers/counts use `tabular-nums`; every control has a visible focus ring.
- [ ] The token layer holds: cool near-white canvas, three-step ink ramp, hairline borders, radius scale locked, semantic colors as condiment with same-hue tints.
- [ ] Palette from `product-palettes.md`; fonts/icons per `stack-defaults.md` (the corpus's Inter is a library choice — rotate per the font rules, don't inherit it); no lucide without explicit request.
- [ ] Anti-patterns §5 scanned: no static-as-streaming, no opaque thinking, no fake metrics, no invisible provenance.

---

**Source & attribution.** Distilled from **beautifului** (MIT © Shane Levine, 2026) — `https://www.beautifului.dev`, source repo `github.com/slev12397/beautiful-ui`. The design tokens and component recipes here are the pattern layer; when you copy actual code from the corpus, keep the MIT attribution. The corpus is **not `detect.mjs`-scanned** — no slop-cleanliness promise; the distilled rules above already carry the blacklist filter. Cut on distillation: the demo canvas's diagonal-stripe page background and the "Surfer / Subway Surfers meme video" loader variant (showcase chrome, not a pattern), and the corpus's Inter font choice (a library default, re-routed via `stack-defaults.md`).
