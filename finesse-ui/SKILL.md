---
name: finesse-ui
description: 'High-craft, never-cheap web interfaces: brand surfaces, product UI, workflow UI, AI-native assistant UI, commerce, paper-zine (拾景/拼贴), diagrams (架构图/流程图/时序图/ER 图 → routed to the standalone diagram-design skill). Routes by register; anti-slop. Triggers: landing page, dashboard, admin panel, 商家后台, 工作台, AI 助手界面, 聊天界面, 对话界面, agent 面板, chat UI, assistant UI, looks like Linear, X 风格, make this look premium, 动效, 纸刊, zine, 拾景, 拼贴, 抽象记忆面板, 把这张照片做成页面, 架构图, 流程图, ER 图, diagram, /finesse.'
when_to_use: >
  Full trigger vocabulary: make this look premium · landing page · launches · portfolios · hero page · dashboard · admin panel · analytics · data tables · app shell · 商家后台 · 工作台 · back-office · console · wizard · settings page · review queue · AI 助手 / 聊天界面 / 对话界面 / agent 面板 / assistant UI / chat UI · PDP · PLP · cart · checkout · dashboard colors · give it a soul · anti-slop · X 风格 · looks like Linear/Stripe/Supabase/Grafana · micro-interaction · button press · tooltip · toast · drawer · 动效 · /finesse.
  Routes by register: brand → soul + spectacle (design-dna substrate, hero engine, style personas); product → palette first (product-palettes), then split READ pages (dashboards/analytics → product-ui) vs OPERATE pages (wizards/consoles/settings/review queues → workflow-ui on top) vs ASSISTANT pages (AI chat/agent surfaces → ai-native-ui on top); commerce → PDP/PLP + anti-dark-pattern rules; photographic/poetic briefs (a real photo, 纸刊/zine/拼贴/poster) → routed to the standalone **zine-ui skill** (photo-as-anchor 实景拼贴 · distillation 影像蒸馏 · hybrid photo-abstract 抽象记忆面板 + paper material language); diagram briefs (架构图 · 流程图 · 时序图 · ER 图 · 泳道图 · 甘特图 · mermaid · drawio · a standalone architecture/flowchart/ER diagram) → routed to the standalone **diagram-design skill** (27 图型, editorial design system, draw.io/Mermaid import + HTML/SVG/PNG export).
  Verb commands: craft · audit · bolder · quieter · soul · animate · depth · densify · redesign · match <brand> · init · document.
  Locked design systems: brief names a real brand, "looks like X", or a DESIGN.md exists → that file overrides soul/palette picks; everything else (register, dials, engine, skeleton, blacklist, a11y, pre-flight) still runs.
version: 0.21.0
user-invocable: true
argument-hint: "[craft · audit · bolder|quieter|soul · animate|depth|densify · redesign · match <brand> · zine · diagram · init|document] [target]"
license: MIT
---

# finesse — Technically Spectacular · Soul-Distinct · Never Cheap

> **finesse routes by register (§0):** **brand** — design IS the product (spectacle + soul; §5 substrate `design-dna.md`, hero engine §6) · **product** — design SERVES the product (clarity + density; `product-ui.md` §0 substrate, component system + data viz) · **zine** — design MEMORIALIZES the real (photo-led 纸刊/zine/拼贴 briefs; routed to the standalone `zine-ui` skill). **No cross-inheritance:** a dashboard is not a brand page with charts; a zine page gets no hero engine.
>
> The through-line is identical: **high craft, zero AI-slop** — the universal craft floor (tinted neutrals, no `#fff`/`#000`, translucent borders, tinted shadows), the cheapness blacklist (§8), the pre-flight (§10). Every rule below is **contextual** — read the brief, set the register, pull only what fits. A skill that produces the same page for every brief has failed.

---

## How to use this skill

1. Run **§0 Brand Read** — infer **register** (brand vs product) + soul before touching code. Output a one-line Design Read.
2. Set the **§1 Three Dials** (SOUL · SPECTACLE · DENSITY) — declared in the Design Read **before** any code; a silent dial pick is how flat pages ship. Product register pins SPECTACLE low, DENSITY high.
3. **Lay the substrate — the right one for the register.** Both share the **universal craft floor** (tinted neutrals, no `#fff`/`#000`, translucent/hairline borders, tinted shadows, contrast floors — `references/design-dna.md` §1). Above that floor the substrate forks:
   - **brand** → the **§5 brand substrate** (`references/design-dna.md`): grain, vignette, `clamp()` display type, dark-default, layered hero depth.
   - **product** → the **product substrate** (`references/product-ui.md` §0): premium surfaces/cards, KPI tiles, floating panels, fixed type scale, feedback-only motion. **Never** pour grain / vignette / giant hero type / dark-default / a hero engine into a dashboard — that's brand grammar, not product grammar.
4. **Then the paths fork further:**
   - **brand** → pick a **§4 Soul** (`references/style-personas.md`) and build **one §6 Hero Engine** (`references/hero-engines.md`). Brief is photographic/poetic (a real photo, 纸刊/zine/拼贴/poster)? **Route to the standalone `zine-ui` skill instead** — the anchored photo + paper material language replaces the persona + engine pair.
   - **product** → **pick a palette from `references/product-palettes.md` first** (the neutral ramp is 80% of the pixels; skipping this step is how every dashboard comes out blue). Then split by the page's job:
     - **pages you read** — dashboards, analytics, monitoring → `references/product-ui.md` (density, tables, charts, interaction states). **Before writing, open the closest dashboard in `examples/`** (index: `examples/EXAMPLES.md`) to see `product-ui.md` §0 applied in shipped code — lift patterns, not whole files.
     - **pages you operate** — publish/create wizards, merchant & admin consoles, config, settings, review queues → `references/workflow-ui.md` **on top of** `product-ui.md` (workflow shell, numbered sections, radio-card choices, live preview, pre-submit check, derived totals, draft/commit). **Pages you manage** — data-grid-heavy consoles, CRUD lists, settings suites, auth/error screens → add `references/admin-console.md` on top (the data-table system, CRUD page morphology, settings family, config drawer). There is **no form-workflow page in `examples/`** — build from the reference, and do **not** force-fit a dashboard example onto a form. **Verify the read/operate route at both §0.F checkpoints** — the §0.A call is made once and can be wrong; a misroute costs a full rebuild.
     - **pages you converse with** — AI chat / assistant / agent surfaces (the loop is prompt → watch it work → review/approve) → `references/ai-native-ui.md` **on top of** `product-ui.md` (streamed answers, thinking traces, tool chips, task rows, approvals, prompt composers). Want the locked AI-native look? `match beautifului` (`design-md/beautifului`) for the token language. No assistant example in `examples/` — build from the reference; do **not** force-fit a dashboard shell onto a chat.
5. Assemble the **§7 page skeleton** per `references/page-skeleton.md`, motion-motivated only. When writing components, load `references/stack-defaults.md` first — its hard rules (§3: RSC safety, no `useState` for continuous input, icon family lock, verify every import) are mandatory.
6. Run the **§8 Cheapness Blacklist** (`references/anti-cheap.md`) and **§10 Pre-Flight** (`references/preflight.md`) before shipping.

**Locked design systems (the brand library).** If the brief names a real product/brand ("looks like Linear", "Airbnb 风格") or the user drops a `DESIGN.md` into the project, that file becomes the **locked design source**: it overrides the §4 soul and §5 palette/type picks with its own colors / type / spacing / radius / components. Everything else (register, dials, engine, skeleton, blacklist, a11y, pre-flight) still runs. Route via `design-md/INDEX.md`; merge contract in `references/design-md.md`; `match <brand>` is the explicit entry point.

The `references/*.md` files are the deep material. Load the one you need for the current phase — do not inline all of them.

| Reference | When to load |
|-----------|-------------|
| `design-dna.md` | Laying the **brand** substrate (grain, vignette, display type, color tokens, palette families). Product/dashboard inherits only its **universal craft floor** (§1: tinted neutrals, translucent borders, contrast floors) — the surfaces/cards/type/motion of a dashboard come from `product-ui.md` §0, not here |
| `theming.md` | Brief asks for a light/dark toggle or multiple swappable named themes — the token-role and hardcoded-color pitfalls of a runtime palette switch (not the single-locked-palette default) |
| `hero-engines.md` | Building the hero engine (brand register); also covers a secondary motion vocabulary (split-char reveal, magnetic buttons, curtain wipe, scan-line, per-card fly-in) for non-hero moments elsewhere on the page |
| `motion.md` | Any interactive UI — buttons, dropdowns, tooltips, toasts, drawers, modals, tabs, drag. The **micro-interaction motion layer**: the should-it-animate gate, purpose naming, tool choice (transition / `@starting-style` / WAAPI / Motion), easing/duration/spring value tables, vanilla recipes, interruption/exit rules, reduced-motion + hover gating. Product register: the values under `product-ui.md` §0.4's "feedback only"; brand register: everything that isn't the hero engine. Never loaded for the hero itself (that's `hero-engines.md`) |
| `3d-effects.md` | Adding a 3D moment — CSS tilt/flip/coverflow/depth-parallax or Three.js model/displacement |
| `style-personas.md` | Picking a soul (brand register) |
| `inspiration-catalog.md` | Persona picked but you want a wider menu of proven techniques for that soul, or the brief doesn't fit any of the 10 personas cleanly |
| `anti-cheap.md` | Before any delivery — cheapness scan |
| `product-ui.md` | Dashboard / admin / data app — pages you **read** (product register) |
| `workflow-ui.md` | Pages you **operate** (product register): publish/create wizards, merchant & admin consoles, config, settings, review queues — the workflow shell, numbered section cards, radio-card choices, live-preview aside, pre-submit check, derived budget panels, draft/commit |
| `admin-console.md` | Pages you **manage** (product register): data-grid-heavy consoles, CRUD list pages, settings suites, auth + error screens — the data-table system (toolbar / faceted filters / column menus / pagination / view options / bulk actions), CRUD page morphology, settings family, config drawer. Load **on top of** `workflow-ui.md`; distilled from the `shadcn-admin` corpus |
| `ai-native-ui.md` | Pages you **converse with** (product register): AI chat / assistant / agent surfaces — streamed answers with sources, thinking traces, tool chips, agent task rows, human-in-the-loop approvals, recommendation cards, context cards, prompt composers. Load **on top of** `product-ui.md`; distilled from the `beautifului` corpus. Pair with `design-md/beautifului` for the locked AI-native token language |
| `product-palettes.md` | **Any product-register page** — the color layer `design-dna.md` §8 doesn't cover: 5 tinted neutral ramps, 16 accents with light/dark + text-on-accent contrast, 12 paste-ready sets, the known-SaaS palettes (Linear/Stripe/Supabase/Grafana…). Load it **before** picking a color, or you will reach for blue |
| `examples/EXAMPLES.md` | The positive-reference corpus — real shipped pages (5 brand + 8 dashboards) with a per-file "what to study" table. **Open the closest one before building**, especially for dashboards (lift patterns, not whole files) |
| `dataviz.md` | Chart-heavy product UI beyond the starter table — full 25-type selection matrix, a11y grade + mandatory fallback, library picks (the **decision** layer) |
| `chart-crafting.md` | **Any** hand-built dashboard chart in a single self-contained file (mandatory for bars — the barcode-chart trap) — the no-library **implementation** layer: the value→height rule, `div height:value/max%` bar recipe, SVG coordinate normalization, line/area draw-in, donut/gauge grow, stacked bars, sparklines, the three animations × reduced-motion pairing, slider-driven live update |
| `commerce-ui.md` | Product detail page (PDP), listing/category page (PLP), cart, checkout — commerce register |
| `asset-sourcing.md` | Brief implies real imagery but no assets provided — generate vs. real stock vs. placeholder fallback, with the authorization step for each |
| `preflight.md` | Final checklist before saying "done" |
| `design-model.md` | Multi-page projects — token consistency |
| `redesign-mode.md` | Upgrading an existing page — audit-first protocol |
| `audit.md` | Read-only diagnostic — cheapness + spectacle + preflight scan |
| `init.md` | New project — write `PRODUCT.md` (the persistent brief) |
| `document.md` | Existing codebase — extract `design-model.yaml` from real code |
| `domain-integration.md` | A design repo / corpus is dropped in and the user asks to integrate it into finesse — the classify → **overlap gate** (is it already covered? reject / merge / add) → locate → distill → wire → guard protocol for adding (or rejecting) new domain material |
| `design-md.md` | Brief names a known brand ("looks like X" / "X 风格") or a `DESIGN.md` is provided — the `design-md/` brand library; the file is the **locked design source** (palette/type/spacing/components); finesse still owns register, engine, dials, audit |
| `stack-defaults.md` | Implementation phase — §3 default architecture: RSC safety, Tailwind v4 + Motion, state rules (never `useState` for continuous input), icon families, responsiveness, dependency verification. Load before writing components |
| `dials.md` | Setting or adjusting the §1 dials — what each level 1–10 means in concrete CSS/motion/layout terms, plus dial-contradiction cross-checks |
| `page-skeleton.md` | Assembly phase — §7 canonical section sequence + layout-diversification / eyebrow / theme-lock rules |
| `iteration.md` | Post-delivery — §10.A the "user says → command → action" feedback table |
| `design-systems.md` | A §2.A system is chosen (need its install command) or a canonical source URL needs verifying — the Appendix A+B material |

---

## Commands

finesse runs as a full build by default, but supports **verb commands** for targeted iteration on an existing page — so you don't re-run the whole Brand Read for a single complaint. Each command loads one reference and does one job.

| Command | Category | Does | Reference |
|---------|----------|------|-----------|
| `craft [brief]` | Build | The full flow: Brand Read → Dials → substrate → engine → assemble (the default) | all |
| `match <brand> [brief]` | Build | Build in a named design language from `design-md/` — the DESIGN.md is the locked design source (palette/type/spacing/components); finesse still owns register, spectacle, density, a11y, pre-flight | `design-md.md` |
| `init` | Setup | New project: write `PRODUCT.md` (register, soul, locked dials, anti-references) — the brief every later task reads | `init.md` |
| `document` | Setup | Existing codebase: extract the built design system into `design-model.yaml`; report drift | `document.md` |
| `audit [target]` | Evaluate | **Read-only** diagnostic: run the cheapness blacklist + spectacle-shown + pre-flight, output a findings list. **Changes nothing.** | `audit.md` |
| `bolder [target]` | Refine | Raise SPECTACLE +2, upgrade the engine (e.g. Canvas → Three.js) | `hero-engines.md` |
| `quieter [target]` | Refine | Lower SPECTACLE −2, step down to GSAP / CSS-only; calm an overloaded page | `hero-engines.md` |
| `soul [target]` | Refine | Re-pick the persona / soul when a page "feels generic" or wrong-vibe | `style-personas.md` |
| `animate [target]` | Enhance | Add or swap motion in isolation; motion only. Routes by target: the hero / spectacle moment → the engine (`hero-engines.md`); an interactive element's *interaction feedback* (button press, dropdown, tooltip, toast, drawer, drag) → the micro-interaction layer (`motion.md`). Decorative spectacle on an interactive element (magnetic buttons, cursor followers) stays with `hero-engines.md` | `hero-engines.md` · `motion.md` |
| `depth [target]` | Enhance | Add **one** 3D moment — CSS pseudo-3D (tilt · flip · coverflow · depth-parallax) or Three.js (model viewer · image displacement) | `3d-effects.md` |
| `densify [target]` | Enhance | Adjust DENSITY ± — add/remove content, tune information-per-viewport | `product-ui.md` |
| `redesign [target]` | Iterate | Upgrade an existing page, audit-first; never full-rebuild for one complaint | `redesign-mode.md` |
| `zine [target]` | Build/Refine | Apply the paper-zine treatment to a photo-led page — decide 实景拼贴 (keep the photo as anchor) vs 影像蒸馏 (distill it away) vs photo-abstract (photo + derived abstract panel), lay the paper material language. **Routes to the standalone `zine-ui` skill** | `zine-ui` skill |
| `diagram [target]` | Build | A technical/product diagram as a standalone HTML+SVG file — 27 图型 (architecture, flowchart, sequence, ER…), import draw.io/Mermaid source, export HTML/SVG/PNG. **Routes to the standalone `diagram-design` skill** | `diagram-design` skill |

### Routing rules

1. **First word matches a command** → load that command's reference and follow it. Everything after the command name is the target. Lay the **§5 substrate** and run the relevant **§8/§10 checks**, but skip the parts of §0–§7 that don't apply to that single action (e.g. `quieter` doesn't re-pick a soul).
2. **First word doesn't match, but intent clearly maps to one command** ("too plain / boring" → `bolder`; "too flashy" → `quieter`; "feels generic" → `soul`; "make it pop" → `animate`; "add depth / make it 3D / tilt / parallax" → `depth`; "too sparse / too dense" → `densify`; "improve / fix this page" → `redesign`; "make it look like X / X 风格 / in the style of X" → `match`; "make it a zine / 纸刊 / 拾景 / 拼贴 / 抽象记忆面板 / photo-abstract / 把这张照片做成页面 / this photo" → `zine`; "make a diagram / architecture diagram / flowchart / sequence diagram / ER 图 / 架构图 / 流程图 / 时序图 / mermaid / drawio" → `diagram`) → route to that command and proceed as if invoked. If two fit, ask once which.
2a. **`match` / a brief naming a known brand** ("looks like Linear", "Airbnb 风格") → look the brand up in `design-md/INDEX.md`, read its DESIGN.md, and build with it as the **locked design source** per `references/design-md.md`. Register still follows the page's job (§0.A), not the brand.
3. **No argument at all** (bare `/finesse`) → the user is asking *"what should I do here?"* Don't dump the static menu. Read a few cheap signals and **lead with the 2-3 highest-value commands**, each with a one-line reason, then offer the full table as fallback. Never auto-run — recommend, the user confirms. Signal → pick:
   - **no `PRODUCT.md`** and there's real code/pages → lead with `document` (capture what's built) and/or `init` (write the brief). Brand-new empty project → `init` then `craft`.
   - **`PRODUCT.md` exists, has built pages, never audited** → lead with `audit <surface>` (read-only health check).
   - **git working tree points at one page/file** → scope `audit` or `redesign` to those files, naming them.
   - **a recent `audit` found P0/P1** → lead with `redesign` (fix the backlog) or the specific refine verb the findings point to (gradient-text/eyebrows → `quieter`/`soul`; flat motion → `animate`).
   - **nothing built yet, clear brief** → `craft`.
   Keep it to 2-3 pointed picks with the exact command to type. The menu is the fallback, not the lede.
4. **A target but no command, building something new** → run the full `craft` flow (§0 → §10). The default for "build me a landing page / dashboard".
5. **`audit` is read-only.** It only reports findings; it never edits code. Every other command is allowed to modify the target.

> Auto-trigger is unchanged: finesse still activates from natural language via its `description`. Commands are an **added** precision entry-point (`/finesse quieter page.html`), not a replacement — both routes lead to the same references.

After any command that modified the page, run the relevant **§10 Pre-Flight** gates before declaring done.

---

## 0. BRAND READ (Before Anything Else)

Most AI design output is bad because the model jumps to a default aesthetic instead of reading the brief. Don't.

### 0.A Determine the Register (this forks every later decision)

Read these signals before deciding the register. Do not jump to a default:

1. **Page kind** — landing, portfolio, product (dashboard / admin / analytics / settings / console), commerce (PDP / PLP / cart / checkout), editorial.
2. **Vibe words** — "minimalist", "calm", "Linear-style", "Awwwards", "brutalist", "premium consumer", "Apple-y", "playful", "serious B2B", "editorial", "agency-y", "glassy", "dark tech".
3. **Reference signals** — URLs linked, screenshots pasted, products named, brands competing with.
4. **Audience** — the audience picks the aesthetic, not your taste.
5. **Brand assets that already exist** — logo, color, type, photography. For redesigns these are starting material, not optional input.
6. **Quiet constraints** — accessibility-first audiences, public-sector, regulated industries, trust-first commerce, kids' products. These **OVERRIDE** aesthetic preference.

Then determine the register:

- **brand** — design IS the product: landing page, brand site, launch, portfolio, campaign, hero page. Be bold, opinionated, spectacular. Goes the soul + hero-engine route (§4, §6).
  - **Zine register.** A **photographic / poetic brief** — the user supplies or names a real photo, or asks for 纸刊 / zine / 拼贴 / poster / 抽象记忆面板 / "把这张照片做成页面" — **routes out of finesse to the standalone `zine-ui` skill** (the paper-material register: 实景拼贴 photo-as-anchor / 影像蒸馏 distillation / photo-abstract 抽象记忆面板). It inherits finesse's craft floor + blacklist + a11y gates and carries its own compact rules, depth files, and pre-flight (§11).
- **product** — design SERVES the product: dashboard, admin, analytics, data table, app shell, settings, tool. Optimize for clarity, density, usability. Goes the component-system route (`references/product-ui.md`), inherits the **universal craft floor** (§5's last three bullets) + the cheapness blacklist (§8), and builds on the **product substrate** (`product-ui.md` §0) — not the brand substrate's grain/vignette/hero-type/dark-default.
  - **Split once more by the page's job — read vs. operate vs. converse.** A dashboard you *read* fails by being unreadable; a console you *operate* fails by being **unfinishable** (abandoned at step 3, or submitted wrong); an **assistant surface you converse with** (AI chat / agent panel — the loop is prompt → watch it work → review/approve) fails by being un-auditable. If the primary action is a **consequential commit** (发布 / 上线 / 提交 / 保存配置) — a merchant publishing a campaign, an admin configuring a rule, a long form that produces a real thing — it's a **workflow page**: load `references/workflow-ui.md` on top of `product-ui.md`. Login forms and search filters don't count; `product-ui.md` §4 covers those. If the page's spine is a **conversation or a live agent run** and the user's decisions land on the agent's *output* (accept / reject / redirect / ask again) rather than on forms or rows, it's an **assistant page**: load `references/ai-native-ui.md` on top of `product-ui.md`. A dashboard with a chat widget bolted on stays read — the conversation must be the primary job.
  - **Color is not optional here.** Pick from `references/product-palettes.md` before writing CSS. "Dashboard" predicts blue; the *product* predicts a color.
- **commerce** — the hybrid case: PDP / PLP / cart / checkout. Doesn't fit either bucket cleanly — route by the specific page's job:
  - A **PDP selling one hero item** (a single SKU, a launch, a flagship product) leans **brand**: pick a soul (§4), but keep DENSITY up for specs/reviews/trust signals — see `references/commerce-ui.md`.
  - A **PLP / marketplace with many SKUs** (filters, sort, grid of many products) leans **product**: DENSITY high, SPECTACLE low, same as a dashboard — `references/product-ui.md` grid/filter patterns + `references/commerce-ui.md` commerce rules (price/CTA placement, cart, checkout, dark-pattern bans).
  - When unsure, ask: *"is this page trying to sell the vibe of one product, or help someone compare/filter many?"*
- **diagram** — the deliverable is a diagram, not a page: an architecture / IT current-state / flowchart / sequence / state machine / ER / timeline / swimlane / quadrant / radar / loop / nested / tree / org chart / layer stack / venn / pyramid / bar / line / Gantt / scatter / high-level / process / medallion / data flow / DP integration / DP security matrix as a standalone HTML+SVG file, or importing draw.io / Mermaid source — **routes out of finesse to the standalone `diagram-design` skill** (its own editorial design system + complexity budget + connector rules + accessible-SVG contract; inherits finesse's craft floor + blacklist + a11y gates; §12).

**Read project memory first.** If a `PRODUCT.md` exists at the project root, read it (register, users, brand personality, locked dials, anti-references) — it **overrides your guesses**. If a `design-model.yaml` exists, read it for the locked palette/type/substrate so this page matches existing ones. Written by `init` / `document` (see Commands).

- **Brand library.** If the brief names a known design system (see `design-md/INDEX.md`), read its DESIGN.md before picking a soul/palette — it overrides the §4/§5 defaults. Proceed per `references/design-md.md`.
- **No `PRODUCT.md`, multi-page or repeat project, thin brief** → offer to run `init` first (one `PRODUCT.md` keeps every later page consistent). Don't force it on a one-off page.
- **Existing codebase, no `design-model.yaml`** → offer `document` to capture what's there before adding to it.
- If memory exists but the new request contradicts it, surface the conflict — don't silently override the lock.

### 0.B Output a one-line "Design Read" before generating

Format: `Design Read: {industry} · {soul in 2-3 words} · register={brand|product|zine|diagram} · job={read|operate|converse} (product only) · SPECTACLE={n} · hero-engine={type}` — for product/zine/diagram, `hero-engine` becomes `none` + the substrate/material system: `component-system` (read) · `workflow-shell` (operate) · `ai-native` (converse/assistant) · `paper-zine` · `editorial-tokens`.

Example: `Design Read: deep-space astronomy · cinematic + reverent · register=brand · SPECTACLE=8 · hero-engine=Three.js particle galaxy`

**Interactive session (a user is present and will respond): STOP after the Design Read. Do not generate any code yet.** Wait for the user to confirm the direction or redirect. Only proceed to §1 once the user says "go ahead", "looks good", "yes", or provides additional guidance.

**Autonomous execution (no user at the other end — a sub-agent, a batch/one-shot task, or the brief says "end to end" / "不用确认"): skip the wait.** State the Design Read as a **decision record** in the output (register, dials, engine or material system, one-line reason), then proceed straight into §1 and complete the build; the human can still redirect by reviewing the result. When unsure which mode this is and asking is possible, ask once — if asking is impossible, default to autonomous.

### 0.C If the brief is ambiguous, ask ONE question — do not guess blind

One sharp question beats five rounds of wrong defaults. Ask the thing that most changes the output: *"Is this meant to feel restrained-editorial or maximal-spectacle?"* / *"What should a visitor remember 10 seconds after leaving?"* / *"Should this feel closer to Linear-clean or Awwwards-experimental?"* Then commit. **Wait for the answer before proceeding.** *(Autonomous mode — see §0.B: skip the question, commit to the best inference, and record it in the decision record.)*

**Never ask a multi-question dump.** If you can confidently infer from context, do not ask — just declare the Design Read and proceed.

### 0.D Anti-Default Discipline

Name the lazy default for this brief, then beat it. "Coffee brand → the default is warm-beige + brass serif. I'm rejecting that for {x}." The single most-tested AI tell is reaching for the obvious aesthetic of the category. (Reflex-reject lists live in `references/anti-cheap.md`.)

### 0.E Quick-Start Dial Mapping

If the brief contains these cues, use these presets as a starting point before refining in §1:

| User says | SOUL | SPECTACLE | DENSITY |
|-----------|------|-----------|---------|
| "premium", "luxury", "high-end" | 8 | 6 | 3 |
| "minimal", "clean", "understated" | 6 | 3 | 3 |
| "bold", "striking", "impactful" | 7 | 7 | 4 |
| "editorial", "magazine", "publication" | 8 | 6 | 6 |
| "tech", "AI", "SaaS" marketing | 6 | 7 | 5 |
| "corporate", "B2B", "enterprise" | 4 | 5 | 6 |
| "playful", "vibrant", "creative" | 7 | 6 | 5 |
| "data-heavy", "dashboard", "analytics" | 4 | 2 | 9 |
| "商家后台", "工作台", "admin console", "back-office" | 5 | 2 | 7 |
| "发布/创建流程", "wizard", "publish flow", "配置", "settings" | 4 | 1 | 7 |
| "landing page" (no other cues) | 7 | 6 | 4 |
| "portfolio" | 8 | 6 | 3 |
| "product page", "PDP", "product detail" | 6 | 4 | 6 |
| "商品列表", "PLP", "category page", "marketplace" | 3 | 2 | 8 |

Override these immediately if the brief provides stronger or contradicting signals.

### 0.F Route Verification — catch a misroute before it costs a page

The §0.A route is a first call, not a lock. Verify it at two points — a wrong route costs a full rebuild, and the check is cheaper than the fix:

1. **Right after the Design Read is confirmed (§0.B):** re-run §0.A's read / operate / converse test against the confirmed direction (the `job` field in the Design Read). A page whose primary action **commits** (保存 / 发布 / 提交 / 配置 / 上线) belongs in `workflow-ui.md`; one that **presents** (monitor / analytics / tables) belongs in `product-ui.md`; one whose spine is a **conversation or live agent run** (prompt → watch → review/approve) belongs in `ai-native-ui.md`. Contradiction → **re-route now**: swap the reference before laying the shell, and record the change in the decision record.
2. **At assembly time (§7), before the shell is committed:** if the page under construction starts reading like the other job — a dashboard shell gaining a dominant save/config form, or a workflow shell with no commit path — stop and re-route. Do not finish in the wrong morphology; by §10 the rebuild is the whole page.

The references self-check too: `product-ui.md` and `workflow-ui.md` open with the job test, and `preflight.md` §L re-gates the fit at the end.

---

## 1. THE THREE DIALS

Set these explicitly from the Design Read. They drive everything downstream. Concrete level definitions (1–10 in CSS/motion/layout terms) and dial-contradiction cross-checks: `references/dials.md`.

| Dial | 1–3 | 4–6 | 7–10 |
|------|-----|-----|------|
| **SOUL** — how opinionated / branded the personality is | neutral, safe, system-default | a clear vibe | unmistakable, one-of-a-kind identity |
| **SPECTACLE** — how technically-ambitious the visual engine is *(finesse's signature dial)* | static + CSS only | GSAP scroll, Canvas 2D accents | Three.js / GLSL / WebGL-FBO hero, generative, scroll-pinned cinema |
| **DENSITY** — information per viewport | airy, one idea per screen | balanced | editorial, data-rich |

### 1.A Dial inference (Design Read → values)

- Astronomy / music / game / crypto / fashion-tech → **SPECTACLE 7–10** (the genre rewards a real engine).
- Law / finance / healthcare / B2B SaaS marketing → **SPECTACLE 3–5** (craft over fireworks; one restrained motion moment).
- Heritage / luxury / editorial / publication → **SOUL 8–10, SPECTACLE 4–6** (the type and substrate carry it, not WebGL).
- **Any product register** (dashboard / admin / analytics / app) → **SPECTACLE 1–4, DENSITY 6–9** — clarity beats fireworks. Skip §4/§6 and go to `references/product-ui.md`.

### 1.B "Spectacle claimed, spectacle shown" (mandatory)

If `SPECTACLE ≥ 7`, the page MUST actually contain a working visual engine (a real Three.js/Canvas/GLSL/scroll-pinned moment), degrade gracefully, and hold 60fps on a mid-range device. A page that claims SPECTACLE 8 but ships a gradient blob is **broken**. If you cannot ship working spectacle in scope, drop the dial to 4 and ship an impeccably-crafted static page instead. Never half-build an engine that janks or cuts off.

### 1.C Dials must be declared — and plain is a failure

Dials are fixed in the Design Read (§0.B) **before any code**: interactive mode stops there for confirmation, autonomous mode records them as a decision record. A Design Read without an explicit dials line is incomplete — restate it before building. The failure mode this section kills: a dial picked at the **bottom of a range** because the model played it safe.

- **Take the upper end.** §1.A inference bands and §0.E cue rows are starting points, not ceilings. When the brief doesn't pin a dial, pick the **upper** end of the applicable range — law/finance/B2B is SPECTACLE 5 (one restrained motion moment, not static), heritage/editorial is 6, never the band floor.
- **Brand register floor: SPECTACLE ≥ 6.** A brand page without a quiet cue starts at **6**. Only the brief's own quiet words ("minimal", "clean", "understated", "restrained", "静态", "不动效") license going lower. A static brand page with no such cue is a dial-3 output — wrong. Quiet constraints (§0.A #6 — a11y-first, public-sector, regulated, trust-first) still override this floor, and §1.B's honest fallback (can't ship the engine → 4 + impeccably crafted static) stands.
- **Product register: pins stand, plainness is diagnosed — not dial-raised.** SPECTACLE 1–4 / DENSITY 6–9 is a clarity pin, not a license for boring. A product page that reads *plain* is a **palette or density failure**: re-check `references/product-palettes.md` (tinted neutral ramp + a real accent, never the default blue) and raise DENSITY before anything else. Raising SPECTACLE to fix a plain dashboard is a misroute.
- **Silent pick = flat page.** If a delivered page reads plain, the first suspect is a dial never declared, or declared at the band bottom without a brief cue. Re-run §0.B and state all three dials with a one-line reason before touching the code again.

---

## 2. BRIEF → DESIGN SYSTEM MAP

Once you have the Design Read (Section 0) and dials (Section 1), pick the right foundation. Do not invent CSS for things that have an official package. Do not pretend an aesthetic trend is an official system.

### 2.A When to reach for a real design system (use official packages)

| Brief reads as… | Reach for | Why |
|---|---|---|
| Microsoft / enterprise SaaS / dashboards | `@fluentui/react-components` or `@fluentui/web-components` | Official Fluent UI, Microsoft tokens, accessibility done |
| Google-ish UI, Material-flavored product | `@material/web` + Material 3 tokens | Official, theme-able via Material Theming |
| IBM-style B2B / enterprise analytics | `@carbon/react` + `@carbon/styles` | Official Carbon, mature data-density patterns |
| Shopify app surfaces | `polaris.js` web components / Polaris React | Required for Shopify admin UI |
| Atlassian / Jira-style product | `@atlaskit/*` + `@atlaskit/tokens` | Official Atlassian DS |
| GitHub-style devtool / community page | `@primer/css` or `@primer/react-brand` | Official Primer; Brand variant for marketing |
| Public-sector UK service | `govuk-frontend` | Legally / regulatorily expected |
| US public-sector / trust-first | `uswds` | Same |
| Fast local-business / agency MVP | Bootstrap 5.3 | Boring, fast, works |
| Modern accessible React foundation | `@radix-ui/themes` | Primitives + polished theme |
| Modern SaaS where you own the components | shadcn/ui (`npx shadcn@latest add ...`) | You own the code, easy to customise; never ship default state |
| Tailwind-based modern SaaS / AI marketing | Tailwind v4 utilities + `dark:` variant | Default for indie + small team builds |

**Honesty rule:** if the brief reads as one of the systems above, install and use the **official** package. Do not recreate its CSS by hand. Do not import a system's tokens but then override 90% of them. Exact install commands per system: `references/design-systems.md`.

**One system per project.** Do not mix Fluent React with Carbon in the same tree. Do not import shadcn/ui components into a Material 3 app.

### 2.B When the brief is an aesthetic, not a system

For these directions, there is **no single official package**. Build with native CSS + Tailwind + a maintained component library. Be honest in code comments about what is borrowed inspiration vs. official material.

| Aesthetic | Honest implementation |
|---|---|
| Glassmorphism / "frosted glass" | `backdrop-filter`, layered borders, highlight overlays. Provide solid-fill fallback for `prefers-reduced-transparency`. |
| Bento (Apple-style tile grids) | CSS Grid with mixed cell sizes. No single library owns this. |
| Brutalism | Native CSS, monospace, raw borders. No library. |
| Editorial / magazine | Serif type, asymmetric grid, generous whitespace. No library. |
| Dark tech / hacker | Mono + accent neon, terminal motifs. No library. |
| Aurora / mesh gradients | SVG or layered radial gradients. No library. |
| Kinetic typography | Native CSS animations, scroll-driven animations, GSAP for hijacks. No library. |
| **Apple Liquid Glass** | Apple documents this for Apple platforms only. There is no official `liquid-glass.css`. Web implementations are approximations using `backdrop-filter` + layered borders + highlights. Label clearly as approximation. |

---

## 3. DEFAULT ARCHITECTURE & CONVENTIONS

> **Load `references/stack-defaults.md` before writing components — its hard rules are mandatory:** RSC safety (global state only in Client Components; interactivity isolated to `'use client'` leaves) · **NEVER `useState` for continuous input-driven values** (`useMotionValue` / `useScroll` instead) · icon families locked (Phosphor / HugeIcons / Radix / Tabler; never hand-roll SVG; one family per project) · Tailwind v4 · every import verified against `package.json`.
>
> Unless the Design Read picks a real design system (§2.A) or a non-React stack (vanilla HTML, Vue, Svelte — adjust accordingly), the defaults are React/Next.js + Tailwind v4 + Motion + `next/font`.

---

## 4. PICK A SOUL (Industry → Persona) · brand register

> **Product register:** soul still matters (brand accent, one type system, the substrate), but skip the spectacle personas below — go to `references/product-ui.md`. The rest of §4 and §6 are for **brand**.
>
> **Locked design system?** If the brief named a brand (routed via `match`), skip persona picking — the DESIGN.md's own voice *is* the soul. Jump to §5 with its tokens locked in.

finesse's job is **soul diversity**: the same method must yield visually unrelated pages for different briefs. Reach into `references/style-personas.md` for the industry→persona map — 10 personas with palette family, type pairing, hero-engine fit, and signature effect — then the wider technique bench in `references/inspiration-catalog.md` when the brief fits none cleanly.

Rules:
- **One soul per page.** Don't fluctuate warm and cool greys, or swap accent colors mid-scroll. Lock it (see §5, color lock).
- **Rotate, don't repeat.** If the last brief used editorial-serif, this one must not. Saturated aesthetic lanes (editorial-typographic, beige-brass craft, AI-purple-glow) are banned as *defaults* — earn them or avoid them (`references/anti-cheap.md`).

---

## 5. THE PREMIUM SUBSTRATE (Why It Reads as Expensive)

The difference between a cheap page and an expensive one is mostly a thin physical layer, applied consistently. Full recipes and exact values in `references/design-dna.md`. The non-negotiables below are the **brand** substrate.

> **Register note.** The last three bullets — **translucent borders**, **no pure `#fff`/`#000`**, **color lock** — are the *universal craft floor*: they hold for **product/dashboard** too. The first four — **grain, vignette, `clamp()` type tension, layered hero z-index** — are **brand-only**; a dashboard replaces them with the product substrate in `references/product-ui.md` §0 (premium surfaces/cards, KPI tiles, fixed type scale, feedback motion). Don't apply brand grain/vignette/giant-type to a dashboard.
>
> **Locked design system?** A DESIGN.md as design source (`references/design-md.md`) overrides the palette/type picks in this section with the brand's own tokens. The craft floor still holds — except where the brand deliberately uses pure `#fff`/`#000`; then those values are locked-in and exempt, and the audit notes it.

- **Grain** — a fixed SVG `feTurbulence` noise layer at `opacity .025–.05`. Static, but kills the flat "vector slop" look. (Light pages too, lower opacity.)
- **Vignette** — a radial-gradient darken on dark heroes to create an optical focal point.
- **Type tension** — display headings at `clamp()` with **negative tracking** (`-.02 to -.045em`) and `line-height .86–.95`; extreme weight contrast against a light body (e.g. 900 against 300). Tight, large, confident.
- **Layered z-index** — engine(0) · grain(1) · vignette · content(5). Depth, not flatness.
- **Translucent borders** — `rgba(255,255,255,.07–.22)` on dark, `rgba(0,0,0,.06–.08)` on light. Never a hard `#333` line.
- **No pure `#fff` / `#000`.** Tint every neutral a few points toward the brand hue.
- **Color lock (mandatory):** once an accent is chosen, it owns the whole page. No surprise teal badge on a rose page. Audit every component before shipping. If the brief actually asks for a swappable/multi-theme experience instead of one locked palette, see `references/theming.md` — the token-role and hardcoded-color pitfalls there are different from a single-palette build.

> Internally reason in **OKLCH** for palettes (perceptual consistency, easy light/dark pairing), even if you emit hex. Design light and dark together; test contrast in each — never just invert.

---

## 6. THE HERO ENGINE (finesse's Differentiator) · brand register

> **Product register:** no hero engine — reach for a data-viz + component system instead (`references/product-ui.md`). This section is for **brand**.

A finesse page earns its name with **one** technically-spectacular moment — usually the hero. Not five. One, done at 100%. Pick the engine that fits the soul; full mount/render/scroll skeletons + reduced-motion fallbacks live in `references/hero-engines.md`.

| Engine | Use when | Cost |
|--------|----------|------|
| **Three.js + GLSL** | 3D depth, particle systems (galaxies, networks, DNA), metaballs, bloom | heavy; lazy-load `three`, gate on SPECTACLE ≥ 7 |
| **Canvas 2D** | particles, fields, real-time data (K-lines, waveforms, fire), flow | light; DPR-adapt for retina |
| **WebGL FBO shader** | fluid (Navier-Stokes), reaction-diffusion, ray-marching, iridescence | heavy; one fullscreen quad, multi-pass |
| **GSAP ScrollTrigger** | scroll-pinned story, horizontal pan, parallax, reveal stagger | medium; the single most reusable engine |
| **CSS-only** | dual-layer mask, 3D transforms, variable-font morph, scroll-driven `animation-timeline` | free; no JS, best perf |

> **Component-level 3D ≠ hero engine.** The table above is for the one full-bleed hero moment. For *reusable, in-page* 3D — pointer-tilt cards, flip cards, coverflow, depth-parallax layers, or a Three.js product/model viewer — reach for `references/3d-effects.md` (the `depth` command). Default to its CSS tier; it ships in any page at zero cost and rarely janks. One 3D moment per page still applies: don't stack a hero engine *and* a tilt grid *and* a coverflow.

**Engine discipline (mandatory):** progressive enhancement (the page is readable and complete with the engine removed — it's never load-bearing) · 60fps or simplify (animate `transform`/`opacity` only; test on a mid-range device) · `prefers-reduced-motion` mandatory (freeze to a still frame; never ship motion with no fallback) · motivated motion only (one-sentence reason per effect — hierarchy, storytelling, feedback, state; max **one** marquee per page).

---

## 7. PAGE SKELETON

Assemble per `references/page-skeleton.md` — the canonical sequence (HERO → ≤1 MARQUEE → STATEMENT/MANIFESTO → CORE CONTENT → INDUSTRY SECTION → CTA/FINALE → FOOTER) plus the hard rules: ≥4 layout families on an 8-section page (max 2 consecutive image+text zigzags) · max 1 eyebrow per 3 sections · one theme locked per page.

---

## 8. THE CHEAPNESS BLACKLIST

Before declaring done, scan against `references/anti-cheap.md` — the merged anti-slop list (AI tells + absolute bans + reflex-reject fonts/palettes/aesthetics). The headline offenders:

- **em-dashes** in copy as a flourish — banned outright (the single most-violated tell).
- **gradient text**, default **glassmorphism**, side-stripe card borders, **AI-purple glow**.
- **eyebrow on every section**, numbered `01 · 02 · 03` markers as default architecture.
- **identical card grids** (icon + title + text × 6), div-based fake screenshots / fake dashboards.
- **fake-precise numbers** (`92%`, `4.1×`) with no real source.
- **default-category palette** (beige+brass for craft, purple-glow for AI/SaaS) — name it, reject it.
- **`Inter`/`Fraunces`/`Instrument Serif` as unexamined defaults** — fine if chosen with a reason, a tell if reached for blindly.
- **zero imagery** on an image-implied brief (food, hotel, fashion, travel) — that's a bug, not minimalism.

> **Brand-locked pages** (design source from `design-md.md`): palette-level default-tells are pre-empted by the brand's real tokens — a locked Apple page may legitimately use `#fff`. Structural tells (em-dashes, identical grids, eyebrow everywhere, fake metrics) still apply unchanged.

---

## 9. PERFORMANCE & ACCESSIBILITY GUARDRAILS

- Animate `transform`/`opacity` only; never `top/left/width/height`. `will-change` sparingly. Micro-interaction values and recipes (curves, durations, springs, origins, the should-it-animate gate): `references/motion.md`.
- `prefers-reduced-motion`: stop canvas loops, freeze grain, swap to static. **Mandatory on every animated page — no exceptions, decorative motion included.** A page that animates without a reduced-motion terminal state is shipping broken.
  - **Capability-probe pattern (the ship-ready shape):** read the probes once at the top — `const RM = matchMedia('(prefers-reduced-motion:reduce)').matches; const FINE = matchMedia('(hover:hover) and (pointer:fine)').matches;` — then branch **per effect**: `if (RM) <set final state> else <animate>`. Gate pointer-dependent motion (magnetic buttons, cursor followers, hover accordions) behind `FINE` so it never fires on touch. Pair with the CSS backstop `@media (prefers-reduced-motion:reduce){*{animation-duration:.01ms!important;transition-duration:.01ms!important}}`. Every hand-built chart draw-in ships its terminal state the same way (`chart-crafting.md` §6).
- Color contrast WCAG AA: body ≥ 4.5:1, large text ≥ 3:1. Includes buttons over photos (add scrim/stroke), placeholders, focus rings.
- Visible focus states on every interactive element. Nav and CTAs reachable by keyboard.
- Core Web Vitals: lazy-load heavy engines, `min-h-dvh` over `100vh` on mobile, responsive images (WebP/AVIF), CLS < 0.1.
- Mobile collapse declared explicitly per multi-column section. Touch targets ≥ 44px.

---

## 10. PRE-FLIGHT CHECK

Run the full checklist in `references/preflight.md` before saying "done." It merges the substrate check, the cheapness scan, the spectacle-claimed verification, the register-fit gate (§L), and the a11y gates. If any hard rule fails, it is shipping broken work — fix before delivery.

**Verify in bounded passes, not a loop** (from impeccable's QA discipline, Apache-2.0): build fully → inspect **once** with a batched round (desktop + mobile together — screenshot, `detect.mjs`, by-eye) → fix everything it shows in **one batch** → confirm with **at most one more round** → stop. Open-ended self-QA burns budget re-checking what the finish handoffs already covered; the pre-flight gates run inside that bounded loop, not instead of it.

---

## 10.A POST-DELIVERY ITERATION GUIDE

After the user receives the output, map feedback to the correct targeted fix via `references/iteration.md` — the full "user says → command → action" table. **Never rebuild from scratch for a single complaint** — identify the dial or module responsible and adjust only that; if the user typed the command, you're already there.

---

## 11. THE ZINE REGISTER → routed to the zine-ui skill

Photographic / poetic briefs (a real photo, 纸刊 / zine / 拼贴 / poster / "把这张照片做成页面") are **routed out of finesse** to the standalone **`zine-ui` skill**: the paper-material register with its own substrate, five principles, three paths (实景拼贴 / 影像蒸馏 / photo-abstract), output contract, and pre-flight. Route at §0.A; the compact rules and trigger vocabulary live in zine-ui's SKILL.md. zine-ui **inherits** finesse's universal craft floor, cheapness blacklist, and a11y gates (declared in its SKILL.md; the full lists live in `references/design-dna.md` §1 and `references/anti-cheap.md` when finesse is also loaded).

---

## 12. THE DIAGRAM REGISTER → routed to the diagram-design skill

Diagram briefs — the deliverable is a standalone diagram, not a page (architecture, IT current-state, flowchart, sequence, state machine, ER / data model, timeline, swimlane, quadrant, radar, loop / flywheel, nested, tree, org chart, layer stack, venn, pyramid / funnel, bar / line chart, Gantt, scatter, high-level, process, medallion, data flow, DP integration, DP security matrix; or importing draw.io / Mermaid source) — are **routed out of finesse** to the standalone **`diagram-design` skill**: 27 图型, its own editorial design system (paper/ink/accent tokens in `style-guide.md`, first-run style-guide gate), complexity budget (density 4/10, ≤9 nodes), mandatory orthogonal connectors, accessible-SVG contract, import/export machinery. Route at §0.A; the compact rules and trigger vocabulary live in diagram-design's SKILL.md. diagram-design **inherits** finesse's universal craft floor, cheapness blacklist, and a11y gates (declared in its SKILL.md; the full lists live in `references/design-dna.md` §1 and `references/anti-cheap.md` when finesse is also loaded). Source: MIT © Cathryn Lavery (littlemight.com) — keep attribution.

---

## 13. OUT OF SCOPE

finesse covers **both** brand and product UI, so its scope is wide. Hand off only when the work is a **pure backend / API / data task with no interface**, or a brief that explicitly wants a **generic, conventional, zero-craft page** (finesse always brings craft — if the user truly wants bland, that's a different tool). Everything from a spectacle landing page to a dense admin dashboard is in scope: set the register in §0 and route accordingly.

---

## Appendix — Install Commands & Canonical Sources

Install commands per design system and the canonical source URLs now live in `references/design-systems.md`. Load it when a §2.A system is chosen (exact command needed) or a source URL needs verifying.
