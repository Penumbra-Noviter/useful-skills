# Pre-Flight Check

Run before saying "done." Merges the substrate check, the cheapness scan, the spectacle verification, and the accessibility gates. Failing any **hard rule** is shipping broken work — fix before delivery. Soft rules are judgment calls; if you skip one, say why.

---

## A. Direction & Soul (hard)

- [ ] **Design Read** was committed (industry · soul · register · SPECTACLE · engine).
- [ ] **Anti-default named** — the lazy aesthetic for this brief was identified and beaten.
- [ ] **One soul, one accent, locked** across every section. No drift, no second accent unless duotone-by-design.
- [ ] **Theme locked** — no warm-paper section inside a dark page (unless deliberate one-time switch).
- [ ] Page matches its **register** (brand = bold/spectacle; if it's really product-UI, finesse is the wrong tool).

## B. Premium Substrate (hard)

- [ ] **Grain** layer present (`opacity .02–.05`).
- [ ] **No pure `#fff`/`#000`**; neutrals tinted toward brand hue.
- [ ] **Translucent borders** only; no hard `#333` lines; shadows hue-tinted (not pure black on light bg).
- [ ] **Display type tension** — `clamp()` size, negative tracking, line-height .86–.95, weight contrast against light body.
- [ ] **Layered z-index** depth (engine · grain · vignette · content).

## C. Spectacle (hard if SPECTACLE ≥ 7)

- [ ] **Spectacle shown, not claimed** — a real working engine exists.
- [ ] **60fps on a mid-range device** (not the dev machine). Below 50fps → simplified.
- [ ] **Canvas DPR-adapted** (retina not blurry).
- [ ] **Progressive enhancement** — page is complete and readable with the engine removed.
- [ ] **`prefers-reduced-motion`** freezes the engine to a still frame / static hero.
- [ ] **Motivated motion** — every animation has a one-sentence reason. ≤1 marquee.

### Verifying spectacle — don't trust your own claim, prove it

A page that *claims* SPECTACLE 8 but ships a white hero is broken, not plain. Verify in two passes:

1. **Static (always):** run the detector — it greps for a real engine and the reduced-motion fallback, and fails on "claimed-not-shown":
   ```bash
   node skills/finesse-ui/scripts/detect.mjs --json <target>
   ```
   A `P0 spectacle-not-shown` or `P0 no-reduced-motion` in the output (`p0 > 0`) is a hard fail — fix before shipping. The script always exits 0 (findings live in the JSON); add `--strict` if you want it to block with a non-zero exit in a git hook / CI. If the script isn't present, fall back to the by-hand checks above — don't treat its absence as a pass.
2. **Runtime (when a browser is available):** the grep only proves the *code* exists, not that it *renders*. Open the page and confirm real pixels:
   - Use the Playwright MCP tools (`browser_navigate` → `browser_take_screenshot`) to load the page and screenshot the hero.
   - Confirm the engine drew something — **not** a white screen, not a flat background-color fill. If the hero is blank, the engine errored; check `browser_console_messages` for the throw.
   - Reload with reduced motion (emulate `prefers-reduced-motion: reduce`) and confirm a composed static frame still shows — never a blank or frozen-mid-animation hero.
   - If you cannot run a browser in this environment, say so explicitly and fall back to the static pass; don't silently claim runtime verification you didn't do.

## D. Layout Discipline (hard)

- [ ] **Hero fits the viewport** — headline ≤2 lines, subtext ≤20 words, CTA visible without scroll. Max 4 text elements (eyebrow OR brand strip, headline, subtext, CTAs).
- [ ] **Hero top padding** ≤ `pt-24` (≈6rem) at desktop. Hero content does not float halfway down the viewport.
- [ ] **Hero stack discipline** — no tiny tagline below CTAs, no trust micro-strip in hero, no feature bullet list, no social-proof avatar row. Those go to dedicated sections below.
- [ ] **"Used by / Trusted by" logo wall** lives UNDER the hero, never inside it.
- [ ] **Nav** single line, ≤80px tall.
- [ ] **Eyebrow count ≤ ceil(sections/3).** Hero counts as 1. Mechanical check: count instances of `uppercase tracking` small-caps labels above headlines.
- [ ] **≥4 layout families** on a long page; no family more than twice; ≤2 consecutive image+text zigzags.
- [ ] **Split-header ban** — no "left big headline + right small explainer paragraph" as a section header. Stack vertically.
- [ ] **Bento cell count** — N items = N cells, no empty tiles. Re-shape the grid, don't paste a blank tile.
- [ ] **Bento background diversity** — at least 2-3 cells have real visual variation (image, gradient, pattern), not all white-on-white text cards.
- [ ] **Mobile collapse** declared per multi-column section. No horizontal scroll at 375px. `min-h-dvh` over `100vh`.

## E. Cheapness Scan (hard)

- [ ] No em-dashes in copy. No div-based fake screenshots. No gradient-text/glass/AI-purple as default.
- [ ] No fake-precise numbers without a source. No banned beige+brass default palette.
- [ ] No identical card grids. No numbered `01·02·03` unless a real sequence.
- [ ] **Real imagery** where the brief implies it (food/hotel/fashion/travel/product); sourced per `asset-sourcing.md` (generate/stock/placeholder), not a silent gradient-blob substitute.
- [ ] Real SVG logos (not text wordmarks) on any "trusted by" wall.
- [ ] Fonts chosen with a reason — not a blind reach for Inter/Fraunces/Instrument Serif.
- [ ] No version labels in hero (`V0.6`, `BETA`, `INVITE-ONLY`) unless the brief is a launch.
- [ ] No section-numbering eyebrows (`00 / INDEX`, `001 · Capabilities`, `06 · how it works`).
- [ ] No decorative dots (zero by default, only for real semantic state).
- [ ] No `border-t` + `border-b` on every row of long lists / spec tables.
- [ ] No pills/labels overlaid on images (no `Plate · Brand`, no `Field notes - journal`).
- [ ] No photo-credit captions as decoration (`Field study no. 12 · Ines Caetano`).
- [ ] No version footers on marketing pages (`v1.4.2`, `Build 0048`).
- [ ] No micro-meta-sentences under eyebrows ("Each of these is a feature we ship today...").
- [ ] No decoration text strip at hero bottom (`BRAND. MOTION. SPATIAL.`).
- [ ] No floating top-right sub-text in section headings.
- [ ] No scoring/progress bars with filled background tracks as comparison visuals.
- [ ] No locale / city-name / time / weather strips unless brief is genuinely place-focused.
- [ ] No scroll cues (`Scroll`, `↓ scroll`, `Scroll to explore`).
- [ ] No generic step labels ("Stage 1 / Stage 2 / Stage 3"). Use verb-noun directly.

## F. Copy Self-Audit (hard)

- [ ] Re-read every visible string. No broken grammar, unclear referents, or AI-cute wordplay.
- [ ] One copy register per page. No mixing technical mono, editorial prose, and marketing punch in the same composition.
- [ ] Quotes ≤ 3 lines with full attribution (name + role + company, no em-dash).
- [ ] One label per CTA intent across nav/hero/footer.
- [ ] No generic step labels ("Stage 1 / Stage 2 / Stage 3", "Phase 01 / Phase 02").
- [ ] No marketing-buzzword family (`streamline · empower · unleash · seamless · elevate · revolutionize · next-gen`).
- [ ] No anecdotal placeholder formulas ("Quietly in use at", "From the field", "Field notes").

## G. Accessibility (hard)

- [ ] Contrast WCAG AA — body ≥4.5:1, large ≥3:1. Includes **buttons over photos** (scrim/stroke), placeholders, helper/error text, focus rings.
- [ ] Visible focus state on every interactive element; keyboard-reachable nav + CTAs.
- [ ] **Button text fits one line at desktop**; no wrapped CTAs. If a label wraps to 2+ lines, shorten the label or widen the button.
- [ ] **No duplicate CTA intent** — "Get in touch" + "Contact us" + "Let's talk" on one page = fail. One label per intent everywhere.
- [ ] Touch targets ≥44px. Form labels above inputs (never placeholder-as-label).
- [ ] **Reduced motion on every movement, micro-interactions included** (press scale, toasts, drawers, reveals) — gentler variant or static terminal state, never zero-motion for comprehension aids; hover motion gated behind `(hover:hover) and (pointer:fine)`. Micro-interaction values/recipes: `motion.md`.

## H. Performance (soft)

- [ ] Animate only `transform`/`opacity`. `will-change` sparingly.
- [ ] Heavy engines lazy-loaded. Responsive images (WebP/AVIF, `srcset`). CLS < 0.1.

---

### The four ship-tests (from overdrive thinking)

1. **wow** — would someone who hasn't seen it react?
2. **removal** — if you delete the engine, is the experience clearly worse?
3. **device** — still smooth on a phone / Chromebook?
4. **context** — does this spectacle actually serve *this* brand and audience, or is it showing off?

If "removal" or "context" fails, the spectacle is decoration, not finesse. Cut or rework it.

---

## I. Strategic Omissions (soft — but separate a prototype from a real deliverable)

These don't affect visual output but are what get noticed after launch:

- [ ] **Custom 404 page** — a framework default is not acceptable for a brand page.
- [ ] **Legal links** (Privacy Policy, Terms of Service) in the footer — required for any real launch.
- [ ] **Skip-to-content link** (`<a href="#main" class="sr-only focus:not-sr-only">`) for keyboard users — satisfies WCAG 2.4.1.
- [ ] **"Back" navigation** — every page is reachable from at least one other page. No dead ends in user flows.
- [ ] **No placeholder data left** ("Jane Doe", lorem ipsum, `email@example.com`) in shipped output.
- [ ] **Form validation wired** — client-side on blur, errors state cause + fix ("Password needs 8+ chars", not "Invalid").

---

## J. Self-Grading Loop (run last, before saying "done")

Generate 5 sharp questions about your specific output, then answer each with concrete evidence from the code/copy you wrote — not a generic "yes." If any answer reveals a failure, fix it before shipping.

**Template — fill in with your actual output:**

1. **Engine check:** "Did I ship a working `[engine type]`, or is there a gradient blob/placeholder where the hero should be?" → [evidence]
2. **Soul check:** "Is the soul I picked (`[persona name]`) actually visible in the palette, typeface, and motion — or did I drift back to a generic aesthetic?" → [evidence]
3. **HARD BAN sweep:** "Does the copy contain any em-dashes? Are there any eyebrow labels on more than 1-in-3 sections? Any fake numbers?" → [evidence]
4. **Substrate check:** "Did I apply grain, type tension (negative tracking + weight contrast), and translucent borders to every section — or just the hero?" → [evidence]
5. **Dial honesty:** "Is the page I built actually `SPECTACLE=[n]` and `DENSITY=[n]`, or did I under-deliver on what I committed to?" → [evidence]

**A "yes" with no evidence = unverified = fail.** Re-read the output, quote the specific line or value that proves it.

---

## K. Image & Visual Assets (hard)

- [ ] **Real images used** where the brief implies it — food, hotel, fashion, travel, product. Zero imagery on an image-implied brief is a bug, not minimalism.
- [ ] **Priority order respected:** image-gen tool first, then real stock photography (picsum/unsplash by specific ID), then explicit placeholder slots. Never silent gradient-blob substitutes.
- [ ] **No div-based fake screenshots** — no fake task lists, terminals, or dashboards built from styled divs as a hero preview.
- [ ] **No hand-rolled decorative SVG illustrations** as default. Icon libraries for icons; simple monogram for brand marks.
- [ ] **Logo wall = logos only** — no industry/category labels printed below logos. Real SVG logos (Simple Icons `cdn.simpleicons.org/{slug}` or devicon) or generated SVG monogram for invented brands.
- [ ] **No pills/labels/tags overlaid on images** — no `Brand · 02`, no `PLATE · BRAND`, no `Field notes - journal` on photos.
- [ ] **No photo-credit captions as decoration** — `Field study no. 12 · Ines Caetano`, `Plate 03 · House archive` under stock/Picsum images are banned. Photo credit only for a real photographer with permission.
- [ ] **Real company logos for social proof** — plain text wordmarks or `<span>Acme Co</span>` styled in a row are not acceptable. Generate a simple SVG monogram for invented brands.
- [ ] **Logos render in both light and dark mode** — white-on-dark, black-on-light, or single-color theme variable.

---

## L. Register Fit (hard) — last-line route backstop

The route was verified early (SKILL.md §0.F), but check it one final time before "done":

- [ ] **Job matches the reference it was built with:** a **read** page (monitor / analytics / tables — no commit path) was built with `product-ui.md`; an **operate** page (a primary action that commits — 保存 / 发布 / 提交 / 配置 / 上线) was built with `workflow-ui.md`; an **assistant** page (spine is a conversation or live agent run — prompt → watch → review/approve) was built with `ai-native-ui.md`. A settings page wearing a dashboard shell is a route failure, not a style preference.
- [ ] **Commerce pages routed per page job** (PDP leans brand / PLP leans product) per SKILL.md §0.A.
- [ ] **Zine pages picked a path and kept it** — 实景拼贴 has the real photo anchored; 影像蒸馏 has no stray photographic pixels (SKILL.md §11).
- [ ] **No cross-register masquerade** — no dashboard shell on a landing page, no hero engine on a product page, no workflow shell on a monitor page.
- [ ] Mismatch found? **Re-route now and rebuild the shell** — shipping a wrong-morphology page because the content is "almost right" is a hard fail.
