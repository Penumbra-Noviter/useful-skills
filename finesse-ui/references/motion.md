# Micro-Motion — The Interaction Layer

> **When loaded by a command:** `animate` on an interactive element (button, dropdown, toast, drawer, drag) — the micro-interaction layer, motion only. Don't touch palette / layout / copy.
>
> **Not for:** the hero / spectacle moment (that's `hero-engines.md`), 3D effects (`3d-effects.md`), chart draw-ins (`chart-crafting.md` §6). This file is the *interaction* layer — the motion between clicks, not the showpiece.
>
> **Product register** (`product-ui.md` §0.4): these recipes + the three load moves are the whole of "feedback only". **Brand register**: everything that isn't the hero engine.

The decision framework, value tables, and recipes are distilled from Emil Kowalski's animation philosophy ([animations.dev](https://animations.dev) / `emilkowalski/skills`, MIT) and translated to vanilla JS. [Attribution & license at the bottom.](#license)

---

## 0. The Gate — should this animate at all?

| Frequency | Decision |
| --- | --- |
| 100+ times/day (keyboard shortcuts, command palette, ⌘K) | **No animation. Ever.** Stop here. |
| Tens of times/day (hover, list navigation, frequent toggles) | Near-imperceptible only — fast and subtle, or nothing |
| Occasional (modals, drawers, toasts, dropdowns) | Standard animation |
| Rare / first-time (onboarding, success, celebration) | The delight budget lives here |

**Keyboard-initiated actions are a disqualifier, not a judgment call.** Raycast has no open/close animation — correct for something opened hundreds of times a day.

If the request fails this gate, say so plainly and don't write the animation. Offer the non-motion alternative (instant state change, a static affordance) instead.

## 1. The Purpose — name it or don't build it

Before writing motion, name the purpose in one of these words:

- **Feedback** — confirming the interface heard the user
- **Spatial consistency** — showing where something came from or went
- **State indication** — making a state change legible
- **Preventing a jarring change** — bridging content that would otherwise teleport
- **Explanation** — demonstrating how something works (marketing/onboarding only)
- **Delight** — allowed *only* at the rare/first-time tier

Can't name it? Don't build it. "It looks cool" on a frequently-seen element is a reason to stop.

Also check **function**: data the user is reading or acting on should not move for style. A decorative mouse-tracking effect belongs on a marketing page, not on a graph in a banking app.

## 2. Pick the Tool — cheapest that works

Walk down; stop at the first that fits.

| Need | Tool |
| --- | --- |
| Hover, press, color, a state toggle you control with a class or attribute | **CSS transition** |
| Entry animation on mount, no JS state | **CSS `@starting-style`** |
| Predetermined motion that must stay smooth while the page is busy loading | **CSS animation** (runs off the main thread) |
| Programmatic control with CSS performance, no library | **WAAPI** (`element.animate()`) |
| Springs, layout animations, exit animations, gesture-driven values | **Motion** (`motion.dev` standalone — framework-free) |

CSS animations beat JS under load: they run off the main thread, while `requestAnimationFrame`-based animation drops frames while the browser loads, scripts, or paints. Use CSS for predetermined motion, JS for dynamic and interruptible motion.

If the task needs a *component* rather than an animation — a dropdown, a dialog, a command menu — build the component first (focus management, dismissal, a11y), then apply these recipes to it. Don't animate a `<div>` pretending to be a menu.

## 3. The Properties

- **`transform` and `opacity` only.** They skip layout and paint and run on the GPU. `width`/`height`/`margin`/`padding`/`top`/`left` trigger all three. (`clip-path` is the sanctioned fourth — see the hold-to-confirm and tab recipes. `height` is tolerated only for accordions, where there's no transform equivalent.)
- **Never `scale(0)`.** Start from `scale(0.9–0.97)` + `opacity: 0`. Nothing in the real world appears from nothing.
- **`transform-origin` at the trigger** for popovers, dropdowns, menus, tooltips. **Modals are exempt** — they're not anchored to a trigger, so they stay centered.
- **Percentages in `translate()`** are relative to the element's own size — `translateY(100%)` moves by its own height whatever the content. Prefer over hardcoded pixels.
- **Never drive a child's transform from a CSS variable on the parent** — it recalculates styles for every child. Set `transform` on the element directly.

## 4. Easing & Duration — or a Spring

**Easing**, in decision order:

| Situation | Easing |
| --- | --- |
| Entering or exiting | `ease-out` |
| Moving / morphing on screen | `ease-in-out` |
| Hover / color change | `ease` |
| Constant motion (marquee, progress) | `linear` |
| Default | `ease-out` |

**Never `ease-in` on UI.** It starts slow, delaying the exact moment the user is watching. `ease-out` at 200ms *feels* faster than `ease-in` at 200ms.

Built-in CSS easings are too weak. Define strong custom tokens once on `:root` — and **extend the codebase's tokens, don't fork them** (finesse's own reveal curve `cubic-bezier(.16,1,.3,1)` is already a valid strong ease-out):

```css
--ease-out: cubic-bezier(0.23, 1, 0.32, 1);        /* strong ease-out for UI */
--ease-in-out: cubic-bezier(0.77, 0, 0.175, 1);    /* strong ease-in-out for on-screen movement */
--ease-drawer: cubic-bezier(0.32, 0.72, 0, 1);     /* iOS-like drawer curve (Ionic) */
```

Need a curve that isn't here? Take it from [easing.dev](https://easing.dev/) — don't hand-roll one.

**Duration:**

| Element | Duration |
| --- | --- |
| Button press feedback | 100–160ms |
| Tooltips, small popovers | 125–200ms |
| Dropdowns, selects | 150–250ms |
| Modals, drawers | 200–500ms |
| Marketing / explanatory | Can be longer |

**UI animations stay under 300ms.** A 180ms dropdown feels more responsive than a 400ms one.

**Reach for a spring instead** when the motion is drag with momentum, an element that should feel alive, a gesture the user can interrupt or reverse, or decorative mouse-tracking:

```js
{ type: "spring", duration: 0.5, bounce: 0.2 }        // Apple-style — easier to reason about
{ type: "spring", mass: 1, stiffness: 100, damping: 10 }  // traditional physics — more control
```

Keep bounce at 0.1–0.3, and avoid bounce in most UI — reserve it for drag-to-dismiss and playful interactions. Apple's mapping: critically damped (`damping 1.0`, `response 0.3–0.4`) for most UI; under-damped (`damping ~0.8`) only when the gesture itself carried momentum — overshoot on a card you flicked feels right, overshoot on a menu that faded in feels wrong.

## 5. Interruption & Exit

- **Transitions, not keyframes, for anything triggered rapidly** — toasts, toggles, anything a user can fire twice in a second. Transitions retarget from the current value; keyframes restart from zero.
- **Springs for gestures**, because they carry velocity through an interruption.
- **Exit the way it entered.** A toast that slides in from the bottom leaves through the bottom. Symmetric paths are what make swipe-to-dismiss feel obvious.
- **Asymmetric timing where the user is deciding.** Slow on the deliberate phase (a hold-to-confirm press: 2s linear), snappy on the system response (release: 200ms ease-out).

## 6. Reduced Motion & Pointer Gating

Ships with the animation, every time. Use finesse's capability probe (`SKILL.md` §9) for JS:

```js
const RM = matchMedia('(prefers-reduced-motion: reduce)').matches;
const FINE = matchMedia('(hover: hover) and (pointer: fine)').matches;
```

```css
@media (prefers-reduced-motion: reduce) {
  .element { transition: opacity 200ms ease; } /* keep opacity/color, drop transform-based motion */
}
@media (hover: hover) and (pointer: fine) {
  .element:hover { transform: scale(1.04); } /* touch fires false hovers on tap */
}
```

Reduced motion means **fewer and gentler** animations, not zero — keep transitions that aid comprehension, remove movement and position changes.

---

## 7. Recipes (vanilla)

### Button press — any pressable element

```css
.button { transition: transform 160ms var(--ease-out); }
.button:active { transform: scale(0.97); }
```

`scale()` scales children too — the label and icons come along, which is what makes it read as a physical press. No hover gating needed: `:active` is a real press on touch. Gate any `:hover` styling separately.

### Dropdown, popover, menu, select

Scales out of its trigger, not out of thin air:

```css
.popover {
  transform-origin: var(--transform-origin); /* set from the trigger's position in JS */
  transition: opacity 200ms var(--ease-out), transform 200ms var(--ease-out);
}
.popover[data-closed] { opacity: 0; transform: scale(0.95); }
```

The `transform-origin` is the whole point — the panel should look like it came out of the thing you clicked. Compute it from `trigger.getBoundingClientRect()`.

### Tooltip

Same shape as a popover, faster, plus the detail most implementations miss:

```css
.tooltip {
  transform-origin: var(--transform-origin);
  transition: transform 125ms var(--ease-out), opacity 125ms var(--ease-out);
}
.tooltip[data-closed] { opacity: 0; transform: scale(0.97); }
/* Once one tooltip is open, neighbours open instantly */
.tooltip[data-instant] { transition-duration: 0ms; }
```

The initial delay prevents accidental activation; after that, skipping both the delay and the animation makes the whole toolbar feel faster.

### Modal — the one popover that stays centered

```css
.modal {
  transform-origin: center; /* exempt — not anchored to a trigger */
  transition: opacity 250ms var(--ease-out), transform 250ms var(--ease-out);
}
.modal[data-closed] { opacity: 0; transform: scale(0.96); }
.backdrop { transition: opacity 250ms var(--ease-out); }
```

Animate the backdrop's opacity alongside so they read as one surface.

### Drawer / sheet

```css
.drawer { transform: translateY(0); transition: transform 500ms var(--ease-drawer); }
.drawer[data-closed] { transform: translateY(100%); }
```

`translateY(100%)` — works regardless of drawer height. Add drag and it becomes a gesture problem — see **Drag to dismiss**.

### Toast

```css
.toast {
  opacity: 1;
  transform: translateY(0);
  transition: opacity 400ms ease, transform 400ms ease;
}
.toast[data-closing] { opacity: 0; transform: translateY(100%); }
```

Entry without JS: `@starting-style` (baseline 2024+ browsers):

```css
@starting-style { .toast { opacity: 0; transform: translateY(100%); } }
```

Fallback for older browsers: append the node, then flip a class inside `requestAnimationFrame`. Exit always needs a little JS: add `[data-closing]`, listen for `transitionend`, remove the node.

`ease` rather than `ease-out`, slightly slower than typical UI: Sonner reads as elegant partly because its motion is tuned to the component's personality rather than to the generic UI budget. When toasts stack and the list reflows, the opacity/height pair has no formula — adjust until it feels right, then check it again the next day.

### Accordion / collapse

```css
.content { overflow: hidden; transition: height 200ms var(--ease-out), opacity 200ms var(--ease-out); }
```

Keep it short — this is one of the few animations that costs layout on every frame. Measure the content height in JS rather than animating to `auto`.

### Stagger a group entrance

For a list or grid the user sees occasionally — never for a list they scroll past all day:

```css
.item { opacity: 0; transform: translateY(8px); animation: fadeIn 300ms var(--ease-out) forwards; }
.item:nth-child(2) { animation-delay: 50ms; }
.item:nth-child(3) { animation-delay: 100ms; }
.item:nth-child(4) { animation-delay: 150ms; }
@keyframes fadeIn { to { opacity: 1; transform: translateY(0); } }
```

30–80ms between items. Stagger is decorative — it must never block interaction while it plays.

### Hold to confirm

For destructive actions where a plain click is too easy to fire by accident:

```css
.overlay { clip-path: inset(0 100% 0 0); transition: clip-path 200ms var(--ease-out); } /* release: snappy */
.button:active .overlay { clip-path: inset(0 0 0 0); transition: clip-path 2s linear; } /* press: deliberate */
.button:active { transform: scale(0.97); }
```

`linear` is correct here — the fill is a progress indicator, and progress shouldn't ease.

### Tab indicator with a color transition

Timing individual color transitions across a tab list never quite lands. Clip instead: duplicate the tab list, style the copy as the active state, clip it so only the active tab shows, animate the clip on change. Text and background change together, in perfect sync, because they're one element being revealed rather than two colors being interpolated:

```css
.tabs-active-copy { clip-path: inset(0 60% 0 20%); transition: clip-path 250ms var(--ease-in-out); }
```

### Scroll reveal

Marketing surfaces only. Don't do this to functional UI a user visits daily:

```css
.reveal { clip-path: inset(0 0 100% 0); transition: clip-path 600ms var(--ease-in-out); }
.reveal[data-visible] { clip-path: inset(0 0 0 0); }
```

Trigger with `IntersectionObserver` (`{ once: true, rootMargin: "-100px" }`). Fire it once — re-animating on every scroll-by is an interface fighting its reader.

### Drag to dismiss

The gesture recipe. Springs, not durations, because the user can reverse mid-motion:

```js
el.addEventListener('pointerdown', (e) => {
  if (isDragging) return;                    // multi-touch protection — no finger-switch jumps
  isDragging = true;
  el.setPointerCapture(e.pointerId);         // drag continues outside the element
  startY = e.clientY; startTime = performance.now();
});
el.addEventListener('pointermove', (e) => {
  if (!isDragging) return;
  const d = e.clientY - startY;
  el.style.transform = `translateY(${d > 0 ? rubberband(d, el.offsetHeight) : d}px)`; // damping past the boundary
  lastD = d; lastT = performance.now();
});
el.addEventListener('pointerup', () => {
  isDragging = false;
  const v = Math.abs(lastD) / (lastT - startTime);             // px per ms
  if (Math.abs(lastD) >= THRESHOLD || v > 0.11) dismiss();     // a flick dismisses regardless of distance
  else el.style.transform = '';                                // spring back
});
function rubberband(overshoot, dimension, constant = 0.55) {
  return (overshoot * dimension * constant) / (dimension + constant * Math.abs(overshoot));
}
```

Set transform on the dragged element directly — driving it through a CSS variable on the parent recalcs styles for every child. For a true spring settle that carries the release velocity, use `motion`'s standalone `animate()`; a CSS transition snap-back is adequate for most toasts/sheets.

### Masking a crossfade that won't settle

When two states overlap visibly during a transition and no amount of easing or duration tuning fixes it, blur the seam:

```css
.content { transition: filter 200ms ease, opacity 200ms ease; }
.content.transitioning { filter: blur(2px); opacity: 0.7; }
```

Without blur the eye reads two distinct objects swapping; blur blends them into one perceived transformation. Keep it under 20px — heavy blur is expensive, especially in Safari.

### Programmatic, without a library

When the motion needs JS control but not a dependency, WAAPI gives CSS-grade performance — hardware-accelerated, interruptible, zero bundle cost:

```js
el.animate(
  [{ clipPath: 'inset(0 0 100% 0)' }, { clipPath: 'inset(0 0 0 0)' }],
  { duration: 1000, fill: 'forwards', easing: 'cubic-bezier(0.77, 0, 0.175, 1)' }
);
```

---

## 8. Never Ship

Self-check before you finish. Each of these is a block in `audit` (Scan 2.B):

| Never | Instead |
| --- | --- |
| `transition: all` | Name the exact properties |
| `scale(0)` entrance | `scale(0.95)` + `opacity: 0` |
| `ease-in` on a UI element | `ease-out` or a strong custom curve |
| Built-in `ease-out` on a deliberate animation | `cubic-bezier(0.23, 1, 0.32, 1)` (or the codebase's strong token) |
| Animation on a keyboard shortcut or 100+/day action | No animation |
| UI duration over 300ms with no reason | 150–250ms |
| `transform-origin: center` on a trigger-anchored popover | origin at the trigger (modals exempt) |
| Keyframes on toasts, toggles, rapidly-triggered elements | CSS transitions |
| Animating `width`/`height`/`margin`/`padding`/`top`/`left` | `transform` / `opacity` |
| Ungated `:hover` motion | `@media (hover: hover) and (pointer: fine)` |
| Missing reduced-motion handling | Gentler variant, not zero |
| Everything entering at once | 30–80ms stagger |
| Exit path ≠ entry path | Symmetric paths |

## 9. When Feel Can't Be Settled From Code

Some results depend on feel you can't judge from code — a crossfade, a spring's bounce, the opacity/height balance in an entering list. Say so instead of guessing, and point at the check: play it at 2–5× duration or in the DevTools animation inspector, step it frame by frame, test gestures on a real device, and look again the next day with fresh eyes.

---

<a name="license"></a>
## License

The decision framework, value tables, and recipes in this file are distilled and adapted from [`emilkowalski/skills`](https://github.com/emilkowalski/skills) (the animations.dev skill suite), translated from React idioms to vanilla JS:

MIT License — Copyright (c) 2026 Emil Kowalski

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
