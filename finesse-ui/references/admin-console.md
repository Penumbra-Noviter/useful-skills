# Admin Console — Data Grids, CRUD Pages, Settings Families, Auth Screens

The product register's **manage** morphology. Where `workflow-ui.md` covers the one-shot **commit** (a wizard that produces one consequential thing), this file covers the **continuous manage** (a console that lists, filters, edits, and deletes many things day after day) — plus the screens that surround it: settings families, auth, error pages. Load it **on top of** `product-ui.md` + `workflow-ui.md`.

> **Inherits everything from both:** `product-ui.md`'s §0 substrate, **§2 base table rules** (row density, sort, filter, pagination — the operating layer below assumes them, doesn't repeat them), §4 forms, §5 interaction states, §9 anti-patterns; `workflow-ui.md`'s shell, pre-submit check, and commit discipline. Palette from `product-palettes.md`. SPECTACLE 1–2; DENSITY 7–9. Icon families follow `stack-defaults.md` (§3) — the corpus this file is distilled from uses lucide/radix; that's a library choice, not a pattern.
>
> **Distilled from** the path-referenced `shadcn-admin` corpus (MIT © Sat Naing, 2024 — see `examples/EXAMPLES.md`, "Component-system corpus"). Read the corpus for the shipped implementation; this file is the pattern layer. Lift patterns, not files; keep the MIT attribution when copying code.
>
> **Covers:** data-grid systems · CRUD list pages · settings suites · config drawer · auth/error screens (product register, **manage** side). **Adjacent:** stacks on `workflow-ui.md` (commit side) · base table rules in `product-ui.md` §2 (assumed, not repeated) · runtime-config tokens in `theming.md`. **Does not cover:** read-side dashboard morphology (`product-ui.md` §1) · one-shot commit flows (`workflow-ui.md` §1–7) · charts (`dataviz.md` / `chart-crafting.md`).

---

## 0. Is this a console page?

A product-register app shell usually holds all three jobs at once — the routing split is **per page**, not per app:

| Page job | Home | Example |
|----------|------|---------|
| **read** — monitor, analyze | `product-ui.md` | the dashboard home |
| **manage** — list, filter, edit, delete many | **this file** | tasks / users / orders tables |
| **commit** — one consequential action | `workflow-ui.md` | a publish wizard, a config flow |

The tell for a manage page: the user's loop is **"find the row → act on it → find the next row"**. If the loop is "fill → commit → done", it's a workflow page; if it's "look → understand", it's a read page. A manage page built as a workflow shell is as wrong as a workflow built as a manage page.

---

## 1. The Data-Table System

The base table (density, sort, filter, pagination) is `product-ui.md` §2. A **console-grade** table adds a coherent operating layer — the six pieces shipped as **one system**, not a loose stack of widgets:

1. **Toolbar** — search input + faceted filters + view options + a one-click **clear-all** that appears only when something is filtered. The toolbar is where the user composes a query; it earns its place only if it reflects real data ("N results", facet counts) — a toolbar with decorative dropdowns is the console version of a fake chart.
2. **Faceted filter** — a multi-select filter (popover + searchable option list) where **every option shows its live facet count** ("12 of 30"). The count is what makes a 10,000-row table navigable; a bare value dropdown is the cheap version. Selected options carry a check glyph, and the filter itself shows a count badge when active.
3. **Column-header menu** — sort asc/desc **and** hide-column from the header itself, not from a separate settings panel. Sort indicators: arrow on hover, active = bold header + ▲/▼ + `aria-sort` (`product-ui.md` §2).
4. **Pagination** — page-size selector (10/20/50/100) **plus** numbered pages with ellipsis + first/last. The page-size choice is a density preference, not decoration; numbered pages keep deep lists navigable where "load more" doesn't.
5. **View options** — a column-visibility toggle. The user's column layout is *their* working state — it must **survive navigation** (URL or provider state), or the console forgets how they work.
6. **Bulk actions** — appear **only when rows are selected**: a sticky bar with the selected count + actions (delete, status change, export) + clear. Announce selection to screen readers (`aria-live` region: "12 tasks selected. Bulk actions toolbar is available."). Selection state is part of the table state that survives navigation.

**State lives in the URL** (sorting, filters, pagination, selection). A console is a tool the user comes back to — bookmarkable, shareable, refresh-safe. Table state in component memory only is a page you finish, not a console you use.

**Rules:**

- **Real geometry everywhere** — counts, totals, "N results", facet numbers all derive from the data (`anti-cheap.md`'s fake-precise ban).
- **Row density** per `product-ui.md` §2 — pick one, lock it.
- **Bulk ops confirm with the count**, and the consequence is spelled out: "删除 12 个任务？" — `workflow-ui.md` §7's confirm discipline applies to every destructive bulk action.
- **Select-all is two distinct states, stated**: "this page" vs "all filtered rows". A single ambiguous checkbox is how someone deletes 4,000 rows by accident.
- **Keyboard**: column headers focusable, row selection via labeled checkbox, pagination keyboard-navigable. Selection announcements are not optional — a visually-hidden `aria-live` region costs three lines and is the difference between usable and unusable for screen-reader users.

---

## 2. CRUD List Page Morphology

The manage page's canonical shape: page header → toolbar → table → dialogs. The dialogs are **owned by a page-level provider**, not scattered inline.

- **Provider pattern** — one provider per page owns dialog state (closed · create · update · delete · import) + the row being edited. Dialogs render once, at the bottom of the page, driven by that state. Per-row inline forms or per-row modal state is how CRUD pages get a thousand-line file and a broken row.
- **Create/edit in a drawer; destructive in a centered AlertDialog.** A drawer (or side sheet) keeps the list context visible while mutating; a destructive confirm gets the centered dialog with the count + consequence. `motion.md` for the enter/exit values; never a full-page overlay for a row edit.
- **Primary actions row** — [新建] accent + [导入] outline + contextual bulk bar. Page header states the count ("User List · 128") so the table's "N results" can disagree visibly when filtered.
- **Row actions** — a per-row menu (edit / duplicate / delete), never more than ~2 always-visible icon buttons per row (density death beyond that). Icon-only row buttons each need `aria-label`.
- **Empty states are load-bearing** — a filtered-to-zero table shows *why* ("No tasks match these filters") with a one-click clear, not an empty `<tbody>`.

---

## 3. Settings Family

Settings is a **route group with sub-navigation**, not one long page. Sub-nav on desktop, **Select dropdown on mobile** (never a drawer for settings nav — the user needs to see all sections to know what exists).

- **Sub-nav + content-section pattern** — vertical nav (title + icon, active state) + content sections each with: title, one-line description, hairline separator, scrollable content column capped at ~`max-w-xl` (the `workflow-ui.md` §1 readable-width rule, tighter for settings). A settings form stretched full-width is a checklist, not a form.
- **One form per section, one concern per form** — appearance (theme + font radios), display (layout density + sidebar style), notifications (switch rows), profile/account (text forms). Four unrelated forms stacked on one scroll is a settings failure — the user can't tell what saving one of them commits.
- **Theme preference lives in a provider + cookie/localStorage, applies instantly** (light/dark/system). This is `theming.md` §1's *real mode swap* — a settings "appearance" section whose radios only relabel one palette is the near-miss that section bans.
- Each form validates on blur (`workflow-ui.md`'s discipline) and confirms nothing — settings are low-consequence commits; `AlertDialog` only where the form has a real consequence (danger zone).

---

## 4. The Config Drawer (runtime appearance/layout config)

When the brief asks for a **user-facing appearance panel** (not just a theme toggle): a sheet/drawer with labeled sections — theme · sidebar · layout · direction · font — each section with its **own per-section reset** (a small circular reset icon button) and **one global Reset** at the bottom.

- **Icon-only controls need `aria-label`** — every section toggle and reset button in a config drawer is icon-only; unlabeled is broken.
- **Persist every knob independently** (cookie/localStorage), and reapply on load — `theming.md` §3: nothing may hardcode the first theme's colors, and a knob that doesn't survive reload is a lie about what it configures.
- **Reset = restore the section's defaults**, global reset restores all. Never a "undo my last change" — that's a different, harder feature; don't fake it with reset.
- **Boundary per `theming.md` §1** — accent-only pickers and full theme swaps stay conceptually separate controls; each knob says honestly what it changes. A drawer mixing both is fine; a hue swatch presented as "a theme" is not.

---

## 5. Auth & Error Screens

**Auth family** — sign-in / sign-up / OTP / forgot-password as **one shell**: centered card on the app's background, logo, one primary path, the alternate path as a text link, the field kit from `product-ui.md` §4. Split-screen auth layouts only when brand assets justify them (product register usually doesn't). The family rule: same shell, different steps — a sign-in that looks like a different product than sign-up is a family failure.

**Error screens** — 401 / 403 / 404 / 500 / 503 as one component family: code + message + **what to do next** + a working path home. Never a bare "404": the screen must name the fix (back / retry / sign in). The 503 (maintenance) carries a time expectation ("back at 14:00"). Error pages are product register — no brand grammar (grain/vignette/hero type), per `workflow-ui.md` §8.

---

## 6. Console Anti-Patterns *(add to `product-ui.md` §9 / `workflow-ui.md` §8)*

- **Pagination with no real pages** — "load more" pretending to be pagination, or page numbers with nothing behind them. Deep lists get real numbered pagination.
- **Bulk actions hidden in a context menu** — selection must surface the action bar; discoverability is the feature.
- **Every row an icon-button minefield** — ≤2 visible row actions, the rest in a menu.
- **Settings as one endless scroll** — sub-nav + sections, one concern per form.
- **Auth as a brand page** — login with hero type and a gradient band; a tool, not a landing page.
- **Config knobs that don't survive a reload** — persistence is not optional.
- **Ambiguous select-all** — page vs filtered must be two stated states.
- **Row density as an afterthought** — picked per-page differently; lock one (`product-ui.md` §2).

---

## 7. Console Pre-Flight *(in addition to the shared §8 / `product-ui.md` §10 / `workflow-ui.md` §9)*

- [ ] Data-table system ships as a system: toolbar (search + faceted filters with live counts + clear-all), column-header sort/hide, page-size + numbered pagination, view options, bulk actions with `aria-live` announcement.
- [ ] Table state (sort / filter / page / selection) survives navigation.
- [ ] CRUD: provider owns dialog state; create/edit in drawer; destructive in AlertDialog with count + consequence; import present where the corpus has it.
- [ ] Settings: sub-nav (mobile Select), content-section pattern, one concern per form, ~`max-w-xl` content column.
- [ ] Config drawer: per-section reset + global reset, aria-labels on every icon-only control, independent persistence per knob.
- [ ] Auth family shares one shell; error screens name the fix.
- [ ] Palette from `product-palettes.md`; icon family per `stack-defaults.md`; no lucide without explicit user request.
