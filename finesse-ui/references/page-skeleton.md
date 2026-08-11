# Page Skeleton — SKILL.md §7

Canonical section sequence (adapt to the soul, never ship all of it by rote):

```
HERO (100vh, the engine moment)  →  MARQUEE/TICKER (≤1 per page)  →
STATEMENT / MANIFESTO (word-reveal)  →  CORE CONTENT (specs grid · horizontal-pan · collection)  →
INDUSTRY SECTION (process · parallax imagery · pull-quote)  →  CTA / FINALE (oversized type)  →  FOOTER (mono, hairline top border)
```

- **Nav:** single line, ≤80px tall, `mix-blend-mode: difference` works beautifully over imagery. Backdrop-blur on scroll.
- **Layout diversification:** once a layout family is used (3-col cards, full-width quote, split image+text), it appears **at most once more**. Max 2 consecutive image+text zigzags. A page with 8 sections uses ≥4 layout families.
- **Eyebrow restraint:** the tiny-uppercase-tracked label above every headline is the #1 AI tell. Max **1 eyebrow per 3 sections**. Usually the headline alone is enough.
- **Theme lock:** one theme for the whole page. No warm-paper section dropped into a dark page (unless a deliberate one-time scroll theme-switch).

---

## Hero hard rules (distilled from taste-skill v2 §4.7 — Leonxlnx, MIT)

The hero is the most-tested section in AI output. These are hard rules, not taste notes:

- **The hero fits the initial viewport.** Headline max 2 lines on desktop; subtext max **20 words** AND max 3–4 lines; CTAs visible without scroll. If the copy is too long, cut copy or reduce font scale — never let the hero force a scroll to find the CTA.
- **Font scale is planned WITH the asset.** If the hero asset is large and the headline is >6 words, do not start at `text-7xl/8xl`. Default range `text-4xl md:text-5xl lg:text-6xl`; `6xl/7xl` only for a 3–5-word headline. A 4-line hero headline is always a font-size error, never a copy-length error.
- **Top padding cap: max `pt-24` (~6rem) at desktop.** More reads as a layout bug, not intentional space — increase font scale or asset size instead.
- **Hero stack discipline — max 4 text elements total:** ① eyebrow OR brand strip OR neither (pick zero or one), ② headline (≤2 lines), ③ subtext (≤20 words / ≤4 lines), ④ CTAs (1 primary + max 1 secondary). **Banned inside the hero:** taglines below CTAs, trust micro-strips ("Used by engineering teams at…"), pricing teasers, feature bullet lists, social-proof avatar rows — all move to the section directly below.
- **The logo wall ("Used by" / "Trusted by") belongs UNDER the hero, never inside it.**
- **CTA labels never wrap at desktop; primary CTAs ≤3 words** (ideally 1–2). A wrapped CTA is broken: shorten the label or widen the button — never constrain `max-width` on a CTA.
