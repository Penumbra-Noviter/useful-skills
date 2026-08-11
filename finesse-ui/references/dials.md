# Dials — Technical Reference (SOUL · SPECTACLE · DENSITY, levels 1–10)

The three dials (SKILL.md §1) are set once from the Design Read. This file defines what each level **means** in concrete CSS / motion / layout terms — the difference between a dial value and a vibe. The layout/motion/density anchors derive from taste-skill v2 §7 (github.com/Leonxlnx/taste-skill, MIT); the engine layer and the dial mapping are finesse's own.

---

## DENSITY — information per viewport (maps to taste's VISUAL_DENSITY)

- **1–3 · Art Gallery** — lots of white space; huge section gaps (`py-32` to `py-48`); expensive, clean; one idea per screen.
- **4–7 · Daily App** — standard web-app spacing (`py-16` to `py-24`); cards and grouped content at normal rhythm.
- **8–10 · Cockpit** — tight paddings; **generic card containers banned** (at >7 — data breathes in plain layout); 1px lines separate data; **mandatory `font-mono` for all numbers**.
- **Mobile override (hard):** dense layouts collapse to strict single column (`w-full`, `px-4`, `py-8`) below 768px.

## SOUL — personality commitment (two coordinated channels)

SOUL is expressed through layout variance AND color commitment; both move with the dial.

**Layout variance** (from taste's DESIGN_VARIANCE):

- **1–3 · Predictable** — symmetrical grid (12-col, equal fr-units), equal paddings, centered alignment.
- **4–7 · Offset** — `margin-top: -2rem` overlaps, varied image aspect ratios (4:3 next to 16:9), left-aligned headers over center-aligned data.
- **8–10 · Asymmetric** — masonry, fractional columns (`grid-template-columns: 2fr 1fr 1fr`), massive empty zones (`padding-left: 20vw`).
- **Mobile override (hard):** 4–10 asymmetric layouts collapse to strict single-column below 768px.

**Color commitment** (the style-personas ladder): 1–3 Restrained (tinted neutrals + accent ≤10%) · 4–6 Committed (one saturated color at 30–60%) · 7–8 Full (3–4 named color roles) · 9–10 Drenched (the surface IS the color).

## SPECTACLE — technical ambition of the visual engine

SPECTACLE measures the **engine**, not the page's liveliness — a static page with heavy motion is still SPECTACLE 3.

- **1–3 · Static** — CSS only; `:hover` / `:active` states; no automatic animation.
- **4–6 · Fluid CSS** — `transition` with `cubic-bezier(.16,1,.3,1)`; `animation-delay` cascades for load-ins; transform/opacity only. This is the micro-motion layer's ceiling without an engine (`motion.md`).
- **7–8 · Choreography** — scroll-pinned / scroll-driven reveals, parallax; GSAP ScrollTrigger or CSS `animation-timeline`; a Canvas 2D accent.
- **9–10 · Engine** — Three.js / WebGL FBO / GLSL; particles, generative or fluid visuals (`hero-engines.md`).
- **Gates:** SPECTACLE ≥7 MUST ship the working engine (§1.B "spectacle claimed, spectacle shown"); `prefers-reduced-motion` fallback mandatory at ≥4; if the engine can't ship in scope, **drop the dial** — never fake it.

## Cross-checks (dial contradictions = design bugs)

- **DENSITY ≥7 with cards everywhere** is a contradiction — cockpit spacing bans generic card containers.
- **SOUL 1–3 with SPECTACLE ≥7** is a contradiction — a predictable layout wearing a WebGL engine.
- **Mobile override is mandatory** for SOUL ≥4 and DENSITY ≥7 — asymmetric and dense layouts must collapse below 768px.
