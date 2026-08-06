# DESIGN.md Locked Design Systems (`design-md.md`)

Load this reference when the brief names a real product/brand, or hands over a `DESIGN.md` file — the page is being built to a **locked external design language**, not invented from defaults.

## When this applies

- Brief says "looks like X" / "in the style of X" / "X 风格" and X is in `design-md/INDEX.md`.
- The `match <brand>` command is invoked.
- The user drops a `DESIGN.md` at the project root (from getdesign.md / the `design-md/` library, or one you wrote).

If the brief just wants "premium" / "minimal" / "bold" without a named system, do **not** route here — stay on the normal §2 soul / §3 palette path.

## The model: who owns what

A DESIGN.md is the **design-DNA + component layer** of a known product's visual language. It answers *how it looks*. finesse answers *how it's built and whether it's good*. Clean separation — neither tries to do the other's job.

| Layer | Owner |
|---|---|
| Palette, type scale, spacing, radius | DESIGN.md (locked) |
| Components (buttons, cards, inputs, nav, tabs, badges) | DESIGN.md (locked) |
| Do's / Don'ts | DESIGN.md (binding contract) |
| Register inference (brand vs product vs commerce) | finesse §0.A — the page's job decides, not the brand |
| SOUL / SPECTACLE / DENSITY dials | finesse §1 — dials are per-brief; the file doesn't state them |
| Hero engine (brand register) | finesse §4 — DESIGN.md has no engine; pick one that honors the brand's soul |
| Product substrate + data-viz (product register) | finesse (`product-ui.md`, `dataviz.md`) using the DESIGN.md tokens |
| Page skeleton (§5), cheapness blacklist (§6), a11y/perf (§7), pre-flight (§8) | finesse |
| Responsive / breakpoints | finesse §7 + the DESIGN.md's Responsive section if present |

## Workflow

1. Look up the brand in `design-md/INDEX.md` → folder + default register.
2. Read `design-md/<folder>/DESIGN.md` — at minimum the frontmatter tokens, Overview, Components, Do's/Don'ts.
3. Set the §1 dials from the brief (the file doesn't state them).
4. Lay the register-appropriate substrate, but **swap the palette / type / spacing for the DESIGN.md's tokens**.
5. Emit every component from the file's `components:` list (e.g. `button-primary`, `code-window-card`) resolved to concrete CSS.
6. Run §6 blacklist + §8 pre-flight with the brand-token exemption (§ below).

## Precedence & lock rules

- **One design system per page.** Never blend two DESIGN.mds, and never sprinkle one brand's accent onto an otherwise-default page. Lock it like a §3 color lock.
- **Resolve references, don't copy names.** `{colors.primary}`, `{typography.display-xl}`, `{component.button-primary}` → concrete values in the output. Never emit the braces.
- **Do's/Don'ts are binding.** The Don't list is a contract (Claude: no cool grays, no bold serif display, no cyan; Linear: accent never decorative). Violating it is off-brand by definition.
- **Missing token? Derive, don't invent.** Use the nearest existing token or a documented variant (`-active` / `-disabled` / `-pressed`). Never introduce a hue the system doesn't have.
- **Font substitutes come from the file.** Licensed faces (Copernicus, StyreneB, Linear Display…) are documented with their own fallback notes inside each DESIGN.md. Use those substitutes — never silently default to Inter when the file calls for a serif display.
- **States are in the file.** `-active`, `-pressed`, `-focused`, `-disabled` variants live as separate component entries. Emit only the states the file defines — most files say "never document hover".

## Blacklist adaptation (brand-locked pages)

Palette-level "default-tell" rules are **pre-empted by the brand's real tokens**: if Apple's DESIGN.md says `#fff`/`#000`, that is intentional, not untinted-default slop. The `pure-bw` and `default-palette-token` checks in `scripts/detect.mjs` may fire — treat them as false positives **only** when the value is a deliberate locked token, and say so in the audit.

Everything structural still applies, unchanged:

- em-dash flourishes, identical card grids, eyebrow on every section, numbered `01·02·03` scaffolding, fake-precise metrics, unmotivated motion.
- A brand-locked page that is also sloppy is still broken. Locking the palette buys you nothing on structure.

## Stubs, gaps, missing files

- **Prose-format entries.** A few files (e.g. `kraken`) are an older prose spec without YAML frontmatter/token refs — still usable; extract the values from the prose yourself.
- **No frontmatter description** on some files → classify register from the brand + the page's job; when genuinely unsure, ask the user whether the page is a marketing surface (brand) or a product surface (product).
- **Brand not in `INDEX.md`?** Either (a) treat the user's description as a normal finesse brief and *note the absence*, or (b) offer to write a DESIGN.md for it (the format the library's files follow is described in `design-md/README.md`).

## When the user only describes the vibe

No file, no brand in the index → build as a normal finesse brief, but tell the user that a DESIGN.md would make the look reproducible, and offer to write one for them.
