# Zine Register — 拾景纸刊 · Gathered Scenes

The **zine register**: a brand-register treatment for photographic / poetic briefs. The trigger is a **real photograph** (user-provided or named) or explicit zine vocabulary (纸刊 · zine · 拼贴 · poster · "把这张照片做成页面"). The photo is the factual anchor — or the fuel for distillation — and the **paper material language** is the substrate. Route at the zine-ui SKILL.md §0; the compact rules live there; this file is the depth.

> **Origin & license.** Distilled from 拾景纸刊 (Gathered Scenes Zine) by Zeejay0 (github.com/Zeejay0/gathered-scenes-zine-skill). Original license: **personal, non-commercial use only**; commercial use requires the author's written permission. Keep attribution in shared output ("Visual language: 拾景纸刊 by @Zeejay0"). The distilled chapter is NOT covered by finesse-ui's MIT terms for redistribution — personal use only.
>
> Inherits the **substrate** (universal craft floor), the **cheapness blacklist**, and the a11y gates — see the *Inherited constraints* section of the zine-ui SKILL.md. The register replaces the brand-register soul + hero-engine pair, not the craft floor.

---

## 0. Inputs & output contract (official spec)

- **Inputs:** topic (主题), style (风格), page / length constraints (页数或长度约束) — plus optional audience, tone, keywords. For a web build, page-count maps to sections/bands, and style maps to the two paths + material choices.
- **Outputs — always deliver all three layers:**
  1. **素材清单 (scene inventory)** — what the scene yields: the anchor element, the shapes / fields it transcribes into, the copy it suggests.
  2. **结构化草稿 (structured draft)** — 封面语 (cover line) · 分栏 (band/column structure) · 短文案 (short editorial copy) · 视觉提示 (per-element visual prompts).
  3. **下一步编辑建议 (executable next steps)** — the 2–3 highest-value edits to refine next, mapped per the zine-ui iteration guidance.

---

## 1. Two paths — decide before building

| | 实景拼贴 · Gathered Scenes | 影像蒸馏 · Scene Distillation |
|---|---|---|
| **Photo's role** | Stays in the piece as the real visual anchor | Never appears; only a semantic/emotional source |
| **When** | The scene's identity is the point (a place, a moment, documentary value, recognition) | The emotion / idea outranks the pixels |
| **Conversion** | Photography + abstract shapes + single high-purity color + torn fiber edges extend **outward** from the photo | Extract semantic core → emotional tension → visual metaphor, then rebuild in paper |
| **Result** | Real but restrained paper-collage page | Expression-first minimal illustrated page |

Decision rule: *"Is this page trying to keep a place, or keep a feeling?"* — place → 拼贴, feeling → 蒸馏. When unsure, ask once.

## 2. The five principles → web translations

1. **真景为锚 (the real anchors)** — one real photographic element is the factual base; every other element extends it. On the web: the actual photo (per `asset-sourcing.md` — real imagery, not placeholders) occupies a fixed, load-bearing slot; nothing decorative competes with it.
2. **插画成场 (illustration extends, never traces)** — vector shapes, halftone fields, and line work continue the space the photo hasn't finished saying. Never redraw the photo's outlines; continue its color fields and directions.
3. **色彩成结构 (color is structure)** — one high-purity print color carries balance, direction, and visual weight: halftone fields, a trajectory line, a distant block. This is the inherited color lock applied harder — the accent is a load-bearing member, not a badge. At most **one** small distant counterpoint block (see §4 回点).
4. **纸面会呼吸 (the paper breathes)** — paper-white negative space is load-bearing; complex information compresses into few clear shapes (uniform halftone / line fields) instead of detail. Generous margins, one idea per band.
5. **边界有触感 (edges have feel)** — torn paper, fiber, dry ink, and print error are the material language (recipes in §5 below).

## 3. The five stages — with checklists

1. **观察 · Observe** — name the core subject, the spatial relations, direction, weight, and quiet zones. Write one sentence for what the scene is.
2. **取舍 · Keep / Discard** — keep the minimum that makes the scene still stand; remove unrelated detail; compress density into printed fields. Write the **keep / compress / discard** list explicitly — it is the design's skeleton.
3. **转译 · Transcribe** — turn silhouette, path, light, and emotion into paper shapes and color structure (city density → a blue halftone field; a coat → deep blue, boots → light purple).
4. **编排 · Orchestrate** — photography + illustration + text + edge + white form **one clear viewing path**: entry → traverse → exit. Declare it in one line and assign every element a stage.
5. **成页 · Finish** — one flat, restrained, tactile, standalone page. Runs the inherited blacklist + pre-flight + the zine pre-flight (§7 below).

## 4. Composition devices (from the archive)

- **Shared color structure** — sky, city, and roof share one blue field; space is unified by color, not by detail. One hue can own a whole region.
- **回点 (distant response)** — one small, high-purity warm block placed far from the subject creates a distant visual response: the snow piece's small warm red against blue-white; the wave piece's yellow trajectory crossing white toward a small distant form.
- **Trajectory as time** — a gesture becomes a line crossing blank space toward a small distant shape; the drawn line carries the time metaphor the photo couldn't.
- **The torn strip cuts and reconnects** — a torn band doesn't just border the piece; it can cut through space and reconnect it (the beige strip separating and re-joining sky and city).
- **Anchor suspended, edges extend** — the real photo sits near center; drawn elements (trees, water) cross its torn boundaries outward.
- **Viewing path, declared** — archive examples: *"先进入宽阔天空，再落向城市纹理，最后停在真实塔楼"*; *"从左侧淡树影进入，穿过桥上人群，再沿水面安静退出"*. Entry → traverse → exit; every element supports one stage.

## 5. Material recipes (CSS)

- **Torn paper edge** — `clip-path: polygon()` with 8–14 irregular points, 2–4px raggedness (values hand-jittered, never a symmetric zigzag — symmetry reads as CSS clip-art). Pair with a same-shape inset layer (`clip-path` + slightly offset, darker tint) for paper-stack thickness.
- **Halftone / screen-print field** — `background-image: radial-gradient(circle, <ink> 1px, transparent 1.5px); background-size: 4px 4px;` at low opacity for the "compressed density" fields; a coarser scale (6–8px) for the large printed regions. Optional second layer rotated 45° for a true screen tint.
- **Grain** — the inherited craft-floor SVG `feTurbulence` layer, opacity `.03–.06`; static (never animated), the paper's texture, not a video effect.
- **Aged-paper tint** — warm off-whites only (e.g. `#F2EDE3` family), tinted toward the print color per the §5 color lock; never pure `#fff` as a paper background.
- **Dry ink** — high-contrast ink text (tinted black, never `#000`); real ink texture when an asset exists, otherwise a solid serif / slab with letterpress feel. **Never a fake-handwritten webfont** — that is the register's #1 cheap tell.
- **Registration / print error** — duplicate a color layer with a `.5–1px` offset and `mix-blend-mode: multiply` (or a soft shadow) for a slight misregistration; one moment per page, not everywhere.
- **Paper layers** — stacked flat sections with visible edges (like stacked sheets), each with its own tint; depth comes from layer order + edge shadow, not from 3D.

## 6. Zine anti-cheap additions (in addition to the inherited blacklist)

- Symmetric / perfectly smooth "torn" edges → ragged irregular `clip-path`.
- Texture soup: full-page paper texture behind everything → texture lives at edges, bands, and fields only.
- Fake handwritten fonts posing as dry ink → real ink texture or a solid letterpress-style face.
- Low-contrast "artistic" type → the inherited WCAG AA floor still applies; the paper may be aged, the text may not be illegible.
- Fake collage: random floating clip-art shapes → every shape must trace back to a relation in the scene.
- A zine that forgets it's a page → it keeps nav, links, and scroll when it is a website; a poster is a one-pager, a site is not.
- Zero photography on a photo-led brief → that is the 拼贴 path failing; the anchor must actually be there.

## 7. Zine pre-flight (in addition to the inherited blacklist + pre-flight)

- [ ] **拼贴**: one real photo anchored, load-bearing, real imagery (never placeholder stock). **蒸馏**: photo fully absent — no stray photographic pixels.
- [ ] Keep / compress / discard list written; nothing that should have been compressed survived as detail.
- [ ] One high-purity print color locked; ≤ 1 distant counterpoint block; no second accent crept in.
- [ ] Viewing path declared (entry → traverse → exit) and every element assigned a stage.
- [ ] Torn edges ragged + irregular; grain static; no texture soup; no fake handwriting fonts; ≤ 1 registration-offset moment.
- [ ] Still passes the inherited substrate + blacklist and the a11y gates.

## 8. Dials

SOUL 8–10 (the register is a strong persona) · SPECTACLE 2–4 (paper craft over fireworks — no hero engine; the material system *is* the spectacle) · DENSITY 3–6 (paper breathes, but a zine can carry a dense spread).
