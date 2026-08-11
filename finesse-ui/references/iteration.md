# Post-Delivery Iteration Guide — SKILL.md §10.A

After the user receives the initial output, map their feedback to the correct targeted fix. **Never rebuild from scratch for a single complaint** — identify the dial or module responsible and adjust only that. The **Command** column is the verb to route through (see SKILL.md `## Commands`); if the user typed the command, you're already there.

| User says | Command | Action |
|-----------|---------|--------|
| "too plain / boring" | `bolder` | Raise SPECTACLE +2; consider upgrading the engine type (e.g. Canvas → Three.js) |
| "too flashy / overwhelming" | `quieter` | Lower SPECTACLE −2; simplify or swap to Engine D (GSAP) or E (CSS-only) |
| "wrong vibe / feels off" | `soul` | Re-run §4 with a different persona from `references/style-personas.md` |
| "too much whitespace" | `densify` | Raise DENSITY +2; add one content section |
| "too cluttered" | `densify` | Lower DENSITY −2; cut a section, increase section padding |
| "more personality / bolder" | `bolder` | Raise SOUL +2; push color commitment level up one step in `references/design-dna.md` |
| "feels generic / like every other AI site" | `soul` | Trigger §0.D anti-default: name and reject the current soul, pick a non-obvious persona |
| "change the colors" | `soul` | Re-run color strategy in `references/design-dna.md`; maintain the accent lock rule |
| "different animation" | `animate` | Swap engine type in §6; re-run `references/hero-engines.md` for that engine's skeleton |
| "motion feels off / slow / wrong easing" | `animate` | Route by target: an interactive element → fix per `references/motion.md` (curve · duration · origin · the gate); the hero → engine swap per `hero-engines.md` |
| "add depth / make it 3D / tilt / parallax" | `depth` | Add **one** 3D moment from `references/3d-effects.md` — default to the CSS tier (tilt/flip/coverflow/depth-parallax); Three.js only for a real rendered object |
| "remove a section" | `redesign` | Remove it, then re-audit the layout-family rule (`references/page-skeleton.md` — ensure ≥4 families remain) |
| "feels slow / heavy" | `quieter` | Lower SPECTACLE; switch to Engine E (CSS-only) or reduce particle count/FBO resolution |
| "needs to work on mobile" | `redesign` | Declare mobile layout per multi-column section; `min-h-dvh`, touch targets ≥44px |
| "is this any good? / review it" | `audit` | Read-only: run the blacklist + spectacle-shown + pre-flight, report findings |
| "make it a zine / 纸刊 / 拾景 / 拼贴 / 把这张照片做成页面" | `zine` | Apply the paper-zine treatment: decide 实景拼贴 vs 影像蒸馏, lay the paper material language |
