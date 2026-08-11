---
name: zine-ui
description: '照片/诗意类 brief 的纸面材料语言设计（拾景纸刊）。三路径：实景拼贴（照片为锚）/ 影像蒸馏（蒸馏掉照片）/ 抽象记忆面板（照片 + 派生抽象面板）。触发词：纸刊, zine, 拾景, 拼贴, poster, 抽象记忆面板, photo-abstract, 把这张照片做成页面, this photo, /zine。独立自 finesse-ui §11（2026-08-10），继承其 universal craft floor + cheapness blacklist + a11y 门。'
when_to_use: >
  Fires when the brief centers on a real photograph (user-supplied or named) or uses zine vocabulary: 纸刊 · zine · 拾景 · 拼贴 · poster · 抽象记忆面板 · photo-abstract · "把这张照片做成页面" · "this photo". A photographic/poetic brief that finesse-ui routes here lands on this skill as the complete implementation. If a finesse-ui craft flow is also loaded, follow this skill for the page's design (the register replaces finesse's soul + hero-engine pair) and finesse for the shared craft floor / blacklist / a11y full lists.
version: 1.0.0
user-invocable: true
argument-hint: "[拼贴|蒸馏|photo-abstract] [photo or topic]"
license: personal, non-commercial — see LICENSE
---

# Zine UI — 拾景纸刊 (Gathered Scenes)

**The paper-material register for photographic / poetic briefs.** Design MEMORIALIZES the real: the photo is the factual anchor, the fuel for distillation, or the anchor **plus** a derived abstract panel; the paper material language is the substrate. No hero engine, no grain/vignette display-type spectacle — the material system *is* the spectacle.

> **Inherited constraints** (from finesse-ui, declared not copied — full lists in finesse-ui's `references/design-dna.md` §1 and `references/anti-cheap.md` if that skill is also loaded):
> - **Universal craft floor:** tinted neutrals (no pure `#fff`/`#000`), translucent/hairline borders, tinted shadows, WCAG AA contrast floors.
> - **Cheapness blacklist:** no em-dash flourishes, gradient text, AI-purple glow, eyebrow-everywhere, identical card grids, fake-precise numbers, default-category palettes (beige+brass for craft), unexamined default fonts.
> - **Color lock:** one high-purity print color carries the page (applied harder here — it is load-bearing structure, not a badge).
> - **a11y gates:** WCAG AA (the paper may be aged, the text may not be illegible), reduced-motion terminal state, visible focus, ≥44px touch targets.

**Origin & license.** Distilled from 拾景纸刊 (Gathered Scenes Zine) by Zeejay0 (github.com/Zeejay0/gathered-scenes-zine-skill); the photo-abstract path from `photo-abstract-editorial` (Codex skill, 2026-08-09). **Personal, non-commercial use only** — see LICENSE; keep attribution in shared output ("Visual language: 拾景纸刊 by @Zeejay0").

---

## 0. Pick the path first (ask once if unclear)

Decision rule: *"keep a place (拼贴), keep a feeling (蒸馏), or keep the image and echo it (photo-abstract)?"*

- **实景拼贴 · Gathered Scenes** — the photo stays as the real anchor; abstract shapes + one high-purity color + torn fiber edges extend outward from it. Choose when the scene's identity is the point (a place, a moment, documentary value).
- **影像蒸馏 · Scene Distillation** — the photo never appears. Extract semantic core → emotional tension → visual metaphor, then rebuild in paper. Choose when the emotion outranks the pixels.
- **抽象记忆面板 · Photo Abstract** — the photo stays as the **principal section** and a **derived abstract memory panel** reconstructs its spatial/tonal/color relations as a sparse motif below it, with one poetic English title (2–5 words) on the panel. The diptych. Compact rules: photo never redrawn/filtered/extended (proportional scaling or slight crop only); panel on uniform ivory (`#F3F0E8` family, zero texture/gradient/grain), every mark tracing to a visual fact in the photo (1 primary mark family + ≤2 supporting); proportion adaptive (≈38–52% photo for wide, 55–68% for tall) — never a mechanical 50/50; title grounded in visible facts, restrained editorial serif, panel only, decided once and rendered exactly. Depth: `references/photo-abstract.md`. Method chain: `DECONSTRUCT → SELECTIVE PRESERVATION → ABSTRACT/DISTILL → RECONSTRUCT`.

## 1. The five principles (纸刊五则), in web terms

1. **真景为锚 · the real anchors** — one real photographic element is the factual base; every other element extends it. A photo dropped in as decoration is a bug, not this register.
2. **插画成场 · illustration extends, never traces** — vector shapes, halftone fields, line work continue the space the photo hasn't finished saying; they never redraw its outlines.
3. **色彩成结构 · color is structure** — one high-purity print color carries balance, direction, and visual weight; at most one small distant counterpoint block.
4. **纸面会呼吸 · the paper breathes** — paper-white negative space is load-bearing; compress information density into few clear shapes (uniform halftone / line fields), not detail.
5. **边界有触感 · edges have feel** — torn-paper edges, grain, dry ink, print error are the material language (ragged `clip-path`, static grain, halftone dots, one misregistration moment).

## 2. The five stages (观察 → 取舍 → 转译 → 编排 → 成页)

1. **观察** — name the core subject, spatial relations, direction, weight, quiet zones; one sentence for what the scene is.
2. **取舍** — keep the minimum that makes the scene stand; write the keep / compress / discard list; density compresses into printed fields.
3. **转译** — silhouette, path, light, emotion → paper shapes + color structure (sky, city, roof share one blue; a coat becomes deep blue, boots light purple).
4. **编排** — photography + illustration + text + edge + white form **one viewing path** — entry → traverse → exit, declared in one line.
5. **成页** — one flat, restrained, tactile, standalone page; runs the inherited blacklist + pre-flight + the zine pre-flight (`references/zine-register.md` §7).

## 3. Output contract (deliver all three layers, always)

1. **素材清单** — the scene inventory: the anchor, the shapes / fields / copy it yields.
2. **结构化草稿** — 封面语 (cover line), 分栏 (band/column structure), 短文案 (short editorial copy), 视觉提示 (per-element visual prompts).
3. **下一步编辑建议** — executable next steps.

Pin down the brief's inputs first: topic, style, page/section count, optional audience / tone / keywords.

## 4. Dials

SOUL 8–10 · **SPECTACLE 2–4** (paper craft over fireworks — no hero engine) · DENSITY 3–6.

## 5. Interactive vs autonomous

Same split as finesse-ui §0.B: if a user is present, state a one-line Design Read (path + material choices) and **stop** for confirmation before generating; if autonomous, record the decision and proceed. Pin the path (拼贴/蒸馏/photo-abstract) before touching code — a misroute costs a full rebuild.

## References

| File | When to load |
|------|--------------|
| `references/zine-register.md` | The register's depth: inputs/outputs, material recipes, the 成页 pre-flight — load when building, and before delivery |
| `references/photo-abstract.md` | Brief routed to the **photo-abstract** path — method chain, abstraction grading, mark system, adaptive proportion, color/title rules, web translation, photo-abstract pre-flight |

## 6. Before saying done

Run the zine pre-flight (`references/zine-register.md` §7) + the inherited blacklist + a11y gates. Output keeps attribution ("Visual language: 拾景纸刊 by @Zeejay0") in shared work.
