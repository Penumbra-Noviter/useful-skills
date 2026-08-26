---
version: alpha
name: Beautiful-UI-design-analysis
description: >
  A component-library design language for AI-native interfaces (chat, agent task panels, streamed answers, human-in-the-loop approvals). The substrate is a cool near-white canvas with white cards and crisp hairline borders; a three-step ink ramp carries text; a single blue-violet accent (`oklch(0.626 0.205 254.947)`) owns CTAs while green/orange/red semantics stay functional condiments. Instrument-grade density: small mono tabular figures, a locked radius scale (chip 6 / control 8 / card 10 / window 14), strong-out easing, and elevation via a hairline ring + layered shadow (dark mode flips the ring to translucent light). Not a single brand product — a reusable visual language for agent/assistant product surfaces.

colors:
  page: "oklch(0.985 0.001 286.376)"
  canvas: "oklch(0.961 0.002 247.84)"
  surface: "oklch(1 0 0)"
  inset: "oklch(0.979 0.002 247.839)"
  hover: "oklch(0.97 0.002 247.839)"
  hover-2: "oklch(0.933 0.003 247.86)"
  ink: "oklch(0.247 0.006 258.361)"
  ink-2: "oklch(0.506 0.01 264.477)"
  ink-3: "oklch(0.695 0.009 264.505)"
  line: "oklch(0.946 0.003 264.542)"
  line-strong: "oklch(0.912 0.005 258.326)"
  field: "oklch(0.961 0.001 286.375)"
  accent: "oklch(0.626 0.205 254.947)"
  accent-ink: "oklch(0.556 0.187 255.617)"
  accent-tint: "oklch(0.96 0.019 252.878)"
  green: "oklch(0.603 0.155 150.883)"
  green-tint: "oklch(0.958 0.017 159.118)"
  orange: "oklch(0.689 0.179 49.902)"
  orange-tint: "oklch(0.964 0.021 67.581)"
  red: "oklch(0.621 0.192 23.042)"
  red-tint: "oklch(0.956 0.017 17.462)"
  tooltip-bg: "oklch(0.272 0.008 264.435)"
  tooltip-fg: "oklch(0.976 0.002 247.839)"
  tooltip-muted: "oklch(0.731 0.008 260.731)"
  tooltip-border: "oklch(0.356 0.007 264.474)"
  dark-page: "oklch(0.209 0.004 264.477)"
  dark-canvas: "oklch(0.231 0.004 264.487)"
  dark-surface: "oklch(0.26 0.006 271.191)"
  dark-inset: "oklch(0.243 0.004 264.492)"
  dark-hover: "oklch(0.289 0.006 271.22)"
  dark-hover-2: "oklch(0.318 0.007 274.747)"
  dark-ink: "oklch(0.964 0.002 247.839)"
  dark-ink-2: "oklch(0.731 0.008 260.731)"
  dark-ink-3: "oklch(0.541 0.01 264.484)"
  dark-line: "oklch(0.308 0.006 258.354)"
  dark-line-strong: "oklch(0.356 0.007 264.474)"
  dark-accent: "oklch(0.68 0.173 253.301)"
  dark-accent-ink: "oklch(0.788 0.113 248.33)"
  dark-accent-tint: "oklch(0.68 0.173 253.301 / 0.16)"

typography:
  font-sans:
    fontFamily: "'Inter', ui-sans-serif, system-ui, sans-serif"
  font-mono:
    fontFamily: "ui-monospace, 'SF Mono', monospace"
  body:
    fontFamily: "{typography.font-sans.fontFamily}"
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: -0.01em
  body-sm:
    fontFamily: "{typography.font-sans.fontFamily}"
    fontSize: 13px
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: 0
  control:
    fontFamily: "{typography.font-sans.fontFamily}"
    fontSize: 12px
    fontWeight: 500
    lineHeight: 1.3
    letterSpacing: 0
  caption:
    fontFamily: "{typography.font-sans.fontFamily}"
    fontSize: 11.5px
    fontWeight: 500
    lineHeight: 1.4
    letterSpacing: 0
  micro-label:
    fontFamily: "{typography.font-sans.fontFamily}"
    fontSize: 10.5px
    fontWeight: 500
    lineHeight: 1.4
    letterSpacing: 0.04em
    textTransform: uppercase
  numeral:
    fontFamily: "{typography.font-mono.fontFamily}"
    fontSize: 12px
    fontWeight: 400
    lineHeight: 1.3
    letterSpacing: 0
    fontVariantNumeric: tabular-nums
  code:
    fontFamily: "{typography.font-mono.fontFamily}"
    fontSize: 12px
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: 0

rounded:
  chip: 6px
  control: 8px
  card: 10px
  window: 14px
  pill: 999px

spacing:
  xxs: 2px
  xs: 4px
  sm: 6px
  base: 8px
  md: 10px
  lg: 12px
  xl: 16px
  xxl: 20px
  section: 24px

components:
  button-primary:
    backgroundColor: "{colors.accent}"
    textColor: "#ffffff"
    typography: "{typography.control}"
    rounded: "{rounded.control}"
    padding: 0 12px
    height: 32px
  button-quiet:
    backgroundColor: transparent
    textColor: "{colors.ink-2}"
    typography: "{typography.control}"
    rounded: "{rounded.control}"
    padding: 0 10px
    height: 32px
  button-secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink-2}"
    typography: "{typography.control}"
    rounded: "{rounded.control}"
    border: 1px solid "{colors.line-strong}"
    padding: 0 10px
    height: 32px
  chat-panel:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    rounded: "{rounded.window}"
    border: 1px solid "{colors.line}"
  composer:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    rounded: "{rounded.window}"
    border: 1px solid "{colors.line}"
    padding: 10px 12px
  stream-answer:
    textColor: "{colors.ink}"
    typography: "{typography.body}"
  source-link:
    textColor: "{colors.accent-ink}"
    typography: "{typography.body-sm}"
  thinking-trace:
    backgroundColor: "{colors.inset}"
    textColor: "{colors.ink-2}"
    typography: "{typography.body-sm}"
    rounded: "{rounded.card}"
    padding: 10px 12px
  tool-chip:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    typography: "{typography.control}"
    rounded: "{rounded.control}"
    border: 1px solid "{colors.line-strong}"
    padding: 6px 10px
  task-row:
    textColor: "{colors.ink}"
    typography: "{typography.control}"
    padding: 8px 10px
  approval-card:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    rounded: "{rounded.card}"
    border: 1px solid "{colors.line}"
    padding: 12px
  recommendation-card:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    rounded: "{rounded.card}"
    border: 1px solid "{colors.line}"
    padding: 12px
  context-card:
    backgroundColor: "{colors.inset}"
    textColor: "{colors.ink-2}"
    typography: "{typography.body-sm}"
    rounded: "{rounded.card}"
    padding: 10px 12px
  status-chip:
    textColor: "{colors.ink}"
    typography: "{typography.caption}"
    rounded: "{rounded.pill}"
    padding: 2px 8px
  status-chip-success:
    backgroundColor: "{colors.green-tint}"
    textColor: "color-mix(in srgb, {colors.green} 92%, {colors.ink})"
  status-chip-fail:
    backgroundColor: "{colors.red-tint}"
    textColor: "color-mix(in srgb, {colors.red} 92%, {colors.ink})"
  loading-state:
    textColor: "{colors.ink-2}"
    typography: "{typography.numeral}"
  records-table:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    typography: "{typography.control}"
    rounded: "{rounded.card}"
    border: 1px solid "{colors.line}"
  sidebar-nav:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.ink}"
    width: 224px
  code-block:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.ink-2}"
    typography: "{typography.code}"
    rounded: "{rounded.card}"
    padding: 10px 12px
  selection-actions:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink-2}"
    typography: "{typography.control}"
    rounded: "{rounded.control}"
    border: 1px solid "{colors.line-strong}"
    padding: 4px 8px
---

## Overview

Beautiful UI is a **copy-paste component library for AI-native interfaces**, not a single brand product — it's a reusable visual language for the surfaces where a user converses with an agent, watches it work, and reviews its output. Its value to finesse is that it hands us a complete, cohesive token + component system for the product register's **assistant** morphology (`../references/ai-native-ui.md`), where finesse previously had no dedicated vocabulary.

The substrate is deliberately **instrument-grade, not brand-flashy**: a cool near-white canvas, white cards, crisp hairline borders (solid, not alpha), a three-step ink ramp for text, and semantic color used as a functional condiment. The single blue-violet accent `{colors.accent}` owns CTAs and focus; green/orange/red appear only as status, each with a same-hue tint.

**Key Characteristics:**
- **Cool near-white + white cards + hairlines**: the page is a blue-tinted off-white (`{colors.page}`); cards are `{colors.surface}`; separations are solid `{colors.line}` hairlines.
- **Three-step ink ramp**: `{colors.ink}` / `{colors.ink-2}` / `{colors.ink-3}` for hierarchy.
- **One accent, semantic condiments**: `{colors.accent}` (blue-violet) for CTAs + focus; green/orange/red only for status, each with a derived same-hue tint.
- **Locked radius scale**: chip 6 · control 8 · card 10 · window 14 — the assistant's small instrument surfaces live at the low end.
- **Strong-out easing**: `cubic-bezier(0.23, 1, 0.32, 1)` for entrances/transitions — built-in easings are too weak for a surface that animates a lot of state.
- **Elevation = hairline ring + layered shadow**; dark mode flips the ring to a translucent light (`{colors.dark-line}`-adjacent) so elevation reads as one graduated stroke.
- **Mono tabular numerals** for everything that ticks — elapsed timers, counts, confidence, task metrics.

## Colors

### Brand & Accent
- **Accent** (`{colors.accent}` — oklch(0.626 0.205 254.947)): the single blue-violet. Primary CTAs, active chips, focus rings.
- **Accent Ink** (`{colors.accent-ink}` — oklch(0.556 0.187 255.617)): accent-colored text (source links) with enough contrast to read as text, not just a button.
- **Accent Tint** (`{colors.accent-tint}` — oklch(0.96 0.019 252.878)): the soft selected/focus fill.

### Surface (light)
- **Page** (`{colors.page}`): the cool near-white page floor.
- **Canvas** (`{colors.canvas}`): recessed page background (behind panels, code blocks).
- **Surface** (`{colors.surface}`): default white card — **deliberately pure white**; this is a locked token (finesse's no-`#fff` rule is pre-empted here, same as Apple's).
- **Inset** (`{colors.inset}`): inset wells (thinking traces, context cards).
- **Hover / Hover-2** (`{colors.hover}` / `{colors.hover-2}`): row / control hover fills.

### Text (the ink ramp)
- **Ink** (`{colors.ink}`): near-black primary text.
- **Ink-2** (`{colors.ink-2}`): secondary.
- **Ink-3** (`{colors.ink-3}`): tertiary / muted / metadata.

### Hairlines
- **Line** (`{colors.line}`): default 1px separation.
- **Line Strong** (`{colors.line-strong}`): stronger panel/border outline.

### Semantic (functional only)
- **Green** (`{colors.green}`) + **Green Tint**: success / completed.
- **Orange** (`{colors.orange}`) + **Orange Tint**: progress / attention.
- **Red** (`{colors.red}`) + **Red Tint**: error / failed.
- Semantic colors are never the page identity; the accent owns CTAs. Each carries a same-hue tint derived from the semantic hue.

### Dark Mode
A full parallel ramp under the `dark-` prefix: `{colors.dark-page}` / `{colors.dark-canvas}` / `{colors.dark-surface}` / `{colors.dark-inset}` / `{colors.dark-hover}` / `{colors.dark-ink…3}` / `{colors.dark-line…strong}` / `{colors.dark-accent…tint}`. In dark, elevation rings become low-alpha white instead of dark hairlines.

## Typography

### Font Family
Sans: **Inter** (the corpus's choice — a library default; per finesse `../references/stack-defaults.md`, rotate through the font rules rather than inheriting Inter blindly). Mono: `ui-monospace, 'SF Mono', monospace` for numerals, code, diffs.

### Hierarchy

| Token | Size | Weight | Line Height | Tracking | Use |
|---|---|---|---|---|---|
| `{typography.body}` | 14px | 400 | 1.5 | -0.01em | Default body, message text |
| `{typography.body-sm}` | 13px | 400 | 1.5 | 0 | Secondary / chunk text |
| `{typography.control}` | 12px | 500 | 1.3 | 0 | Buttons, chips, task rows, table cells |
| `{typography.caption}` | 11.5px | 500 | 1.4 | 0 | Status chips, metadata |
| `{typography.micro-label}` | 10.5px | 500 | 1.4 | 0.04em / uppercase | Tiny section labels |
| `{typography.numeral}` | 12px | 400 | 1.3 | tabular-nums | Elapsed timers, counts, confidence |
| `{typography.code}` | 12px | 400 | 1.5 | 0 | Code blocks, unified diffs |

### Principles
- **Instrument density, mono for numbers.** The scale stays tight (10.5–14px); everything that ticks uses mono tabular figures so counts don't jitter.
- **No display type.** This is a product surface — no hero type, no brand headline scale. Hierarchy is done with size, weight, and ink-ramp steps.

### Note on Font Substitutes
Inter is the corpus font. Per finesse's font-rotation rule, substitute a non-reflex sans-display (Geist, Cabinet Grotesk, PP Neue Montreal, ABC Diatype) and keep the same weights/steps. Mono stays `ui-monospace`/`SF Mono`.

## Layout

### Spacing System
- **Base unit:** 4px, with a 2px floor for tight gaps.
- **Card padding:** 12px (`{spacing.lg}`); toolbar/bar padding 10px 12px; table cells 10px 12px.
- **Gaps:** 2.5–4px inside a chip, 6–8px between chips, 8–12px between rows.

### Grid & Shell
- The primary frame is a **panel** (chat/agent panel, not a full-bleed dashboard), content scrolls, composer pinned bottom.
- Component nav / sidebar: a persistent ~224px rail.
- Content column caps around ~`max-w-xl` for readable prose/chunks.

### Whitespace Philosophy
Dense but not cramped. The cool canvas + hairlines create structure without needing heavy spacing; small instrument surfaces sit close, separated by hairlines rather than whitespace.

## Elevation & Depth

The system uses **ring + layered shadow** elevation, with the ring flipping to translucent light in dark mode:

| Level | Treatment |
|---|---|
| Flat | `{colors.canvas}` / `{colors.page}` |
| Card | `{colors.surface}` + `1px {colors.line}` ring + soft `--shadow-sm` |
| Raised | ring `{colors.line}` + `--shadow-md` |
| Overlay (menus, tooltips, chips) | ring `{colors.line}` / `{colors.line-strong}` + `--shadow-lg`; `pop-in` scale animation |

- **Dark mode:** rings become low-alpha white (0.10–0.15) + deeper dark shadows — the ring paints over the surface behind the element, so elevation reads as one continuous stroke.
- No accent-glow sprinkling; accent-glow shadows belong on the primary CTA / active chip only.

## Shapes

### Border Radius Scale

| Token | Value | Use |
|---|---|---|
| `{rounded.chip}` | 6px | Small chips, inline tags, checkboxes |
| `{rounded.control}` | 8px | Buttons, inputs, tool chips, menu items |
| `{rounded.card}` | 10px | Cards, traces, context cards, tables |
| `{rounded.window}` | 14px | The outermost chat/app panel |
| `{rounded.pill}` | 999px | Status chips, avatars |

Compact instrument radii — 6–8px controls, 10px cards, 14px only at the outer window. Signals "tool" not "consumer brand".

## Components

### Buttons
**`button-primary`** — The accent CTA. Background `{colors.accent}`, white text, `{typography.control}` (12px/500), height 32px, rounded `{rounded.control}` (8px). Active/pressed: darker accent.
**`button-quiet`** — Transparent, `{colors.ink-2}` text; hover `{colors.hover}`. For in-panel actions (tool chips, dismiss).
**`button-secondary`** — Surface + `1px {colors.line-strong}` border, `{colors.ink-2}` text. For the "other option" / alternatives buttons.

### The Assistant Primitives
**`chat-panel`** — The outer window: `{colors.surface}`, `{rounded.window}` (14px), `1px {colors.line}`. Holds the message list + composer. Optional tabs split sub-conversations.
**`composer`** — The pinned prompt bar: surface, window radius, with @ sources / / commands / model picker / dictation as the product supports.
**`stream-answer`** — Progressive reveal of an answer in `{typography.body}`; carries inline `source-link`s (accent text), an action-button row, and follow-up chips. Newest characters may carry a soft masked blur (`.stream-tail`) while streaming.
**`thinking-trace`** — Collapsible reasoning: `{colors.inset}`, `{rounded.card}`, `{colors.ink-2}` small text; state axis (steps / reasoning / search / coding), each step expandable.
**`tool-chip`** — A collapsed tool call (verb + target) that expands to input + outcome. Surface, `1px {colors.line-strong}`, control radius.
**`task-row`** — Live agent status row: title + running/completed/failed state + sub-step counts. `role="status"`.
**`approval-card`** — Sequenced human-in-the-loop: one question per card, concrete options + free-text fallback, skip / back / continue.
**`recommendation-card`** — Primary suggestion + confidence + alternatives with verdicts + accept/reject.
**`context-card`** — Retrieved chunk + its source file/kind, always attributed. `{colors.inset}`, small text.
**`status-chip`** (+ `-success` / `-fail`) — Pill using the semantic tint fills + same-hue text.
**`loading-state`** — Pixel-grid loader (Drive/Dots/Orbit variants) + label + elapsed mono timer; reduced-motion freezes the grid, timer ticks on.

### Tables & Nav
**`records-table`** — CRM-style grid: sticky header + first column, column resize handles, sort, tags with `--tag-base` same-hue derivation, row-number gutter that swaps to a checkbox on hover/select.
**`code-block`** — Code + unified diff in `{typography.code}` on `{colors.canvas}`.
**`sidebar-nav`** — 224px collapsible rail; active row = accent-tint.
**`selection-actions`** — Floating AI actions (explain / improve / shorten / change tone) on selected text.

## Do's and Don'ts

### Do
- Keep the canvas cool near-white and cards on `{colors.surface}`; separate with crisp `{colors.line}` hairlines, not alpha smudges.
- Use the three-step ink ramp for hierarchy; reserve `{colors.ink-3}` for metadata.
- Let the single accent own CTAs and focus; keep green/orange/red strictly as status condiments with same-hue tints.
- Lock the radius scale — small controls at 6–8, cards 10, only the outer window 14.
- Set every number that ticks in mono tabular figures.
- Signal elevation with a hairline ring + layered shadow; flip the ring to translucent light in dark mode.
- Make every agent artifact auditable — streamed claims link sources, tool calls show diffs, recommendations show a basis.
- `role="status"` on loaders and task rows; visible accent focus ring on every control.
- Honor `prefers-reduced-motion`: freeze streaming blur and loader grids, but keep time/count information.

### Don't
- Don't add a second accent or let semantic green/red become the identity — the single blue-violet owns CTAs.
- Don't use brand grammar here: no grain, no vignette, no hero display type, no gradient-text, no AI-purple glow.
- Don't ship a static paragraph styled as streaming, or a "thinking" spinner with no expandable trace.
- Don't show fake agent metrics (`68% confidence` with no visible basis) — `anti-cheap.md`'s fake-precise ban applies.
- Don't let an approval card dead-end (no skip / back / free-text path).
- Don't paste `#fff`/`#000` outside the locked tokens; `{colors.surface}` is the only deliberate pure-white.
- Don't inherit Inter as a reflex — substitute per finesse's font-rotation rule.

## Responsive Behavior

### Breakpoints

| Name | Width | Key Changes |
|---|---|---|
| Mobile | < 640px | Panel becomes full-bleed; sidebar collapses to icons or a hamburger; table scrolls horizontally with sticky first column. |
| Tablet | 640–1024px | Sidebar collapses; approval cards stack; toolbar wraps. |
| Desktop | ≥ 1024px | Full shell: panel + optional sidebar; multi-column assistant + context. |

### Touch Targets
- Controls at 32px height — pad to ≥44px where touch-primary.
- `@media (hover: none)`: neutralize row/header hovers so a tap doesn't leave a stuck hover state.

### Collapsing Strategy
- Panel takes the full width below 640px; composer stays pinned.
- Tool-chip details and thinking traces collapse to chips/toggles at every breakpoint.

## Iteration Guide

1. Build the shell as a **panel** (conversation + composer), not a dashboard grid.
2. Compose from the assistant primitives (`chat-panel`, `stream-answer`, `thinking-trace`, `tool-chip`, `task-row`, `approval-card`, `recommendation-card`, `context-card`) per `../references/ai-native-ui.md` §3.
3. Lay the token layer first: cool near-white, ink ramp, hairlines, radius scale, strong-out easing.
4. Set accent/semantic from this file; lock one accent, keep semantics functional.
5. Every streamed/live element gets a terminal state + reduced-motion fallback.
6. Use `{token.refs}`, never inline hex, and don't hand-roll diffs/carets where the corpus ships them.

## Known Gaps

- The corpus is a **component library**, not one coherent product page — there's no single "homepage" to copy; assemble the primitives.
- Inter is the corpus font; finesse substitutes per its rotation rule (font is a library choice).
- The demo's diagonal-stripe page background and the "Surfer / Subway Surfers" meme-video loader variant are showcase chrome, not patterns — cut on distillation.
- Animation timings beyond the strong-out easing and streaming/loading keyframes are out of scope.
