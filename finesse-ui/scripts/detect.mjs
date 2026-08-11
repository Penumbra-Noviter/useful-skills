#!/usr/bin/env node
// finesse — local slop / spectacle detector.
// No network, no deps. Scans HTML/CSS/JS files for cheapness tells, the
// finesse-specific "spectacle claimed but not shown" failure, and the
// regex-detectable micro-motion block list (references/motion.md §8).
//
// Usage:
//   node detect.mjs [--json] [--strict] <file ...>
//   node detect.mjs --json skills/finesse-ui/examples/*.html
//
// Exit code: 0 by default — ALWAYS, even when P0 findings exist. Findings are
// DATA carried in the report (the JSON `p0` count), not a tool failure. A
// non-zero exit reads to an agent as "this tool is broken" and it abandons the
// tool entirely, falling back to eyeballing — so the default path never does
// that. Pass --strict to make a P0 finding block with exit 1 (for CI / git
// hooks / humans who want a hard gate). The `audit` command (references/audit.md)
// consumes the --json output and decides for itself; it does not need exit codes.

import { readFileSync } from 'node:fs';
import { basename } from 'node:path';

const args = process.argv.slice(2);
const asJson = args.includes('--json');
const strict = args.includes('--strict');
const files = args.filter((a) => a !== '--json' && a !== '--strict');

// What the regex layer canNOT see. A clean run means "no regex-detectable slop",
// NOT "this page is good" — these taste/structure/runtime tells need a human eye
// (or the Playwright runtime pass in preflight.md §C). Surfaced in every report so
// a green result never reads as license to skip the visual audit.
const NOT_COVERED = [
  'default-category aesthetic (the vibe, not just token names — beige+brass craft, AI purple-glow)',
  'div-based fake screenshots / fake dashboards',
  'identical / generic card grids (icon + title + text × N)',
  'zero imagery on an image-implied brief (food / hotel / fashion / travel)',
  'glassmorphism / AI-purple-glow used as decoration',
  'layout-family repetition (§5) and whether the soul is actually distinct',
  'whether the engine RENDERS real pixels (needs the Playwright runtime pass, not a grep)',
  'easing *choice* context — ease-in-out on a hover vs an entrance (the pattern is fine, the situation decides)',
  'durations >300ms, keyframes on rapidly-triggered elements, exit-path asymmetry (motion.md §4/§5)',
  'transform-origin: center on a popover — regex cannot know it is not a modal (motion.md §3)',
];

if (files.length === 0) {
  // Guidance, not an error. Never teach the agent to abandon the tool.
  const note = 'usage: node detect.mjs [--json] [--strict] <file ...>';
  if (asJson) console.log(JSON.stringify({ p0: 0, files: [], notCovered: NOT_COVERED, note }, null, 2));
  else console.log(note);
  process.exit(0);
}

// ---- helpers ---------------------------------------------------------------

// Find 1-based line number of a regex match index.
function lineOf(text, index) {
  let line = 1;
  for (let i = 0; i < index && i < text.length; i++) if (text[i] === '\n') line++;
  return line;
}

// Collect every match of a global regex as {line, text}.
function matches(text, re) {
  const out = [];
  let m;
  const r = new RegExp(re.source, re.flags.includes('g') ? re.flags : re.flags + 'g');
  while ((m = r.exec(text)) !== null) {
    out.push({ line: lineOf(text, m.index), text: m[0].slice(0, 80).replace(/\s+/g, ' ').trim() });
    if (m.index === r.lastIndex) r.lastIndex++; // zero-width guard
  }
  return out;
}

// Remove comment bodies (HTML, CSS-block, JS-line) so copy-rules don't fire on
// notes/labels inside comments. Replace with same-length whitespace to keep line
// numbers stable.
function stripComments(text) {
  return text
    .replace(/<!--[\s\S]*?-->/g, (m) => m.replace(/[^\n]/g, ' '))
    .replace(/\/\*[\s\S]*?\*\//g, (m) => m.replace(/[^\n]/g, ' '))
    .replace(/(^|[^:])\/\/[^\n]*/g, (m, p1) => p1 + m.slice(p1.length).replace(/./g, ' '));
}

// ---- generic slop rules ----------------------------------------------------
// Each rule: {id, severity, label, fix, find(text) -> [{line,text}]}

const RULES = [
  {
    id: 'gradient-text',
    severity: 'P1',
    label: 'Gradient text (background-clip:text + gradient)',
    fix: 'typeset / soul',
    find: (t) => {
      // a block that has background-clip:text near a linear/radial-gradient
      const out = [];
      const re = /-?webkit-background-clip\s*:\s*text|background-clip\s*:\s*text/gi;
      let m;
      while ((m = re.exec(t)) !== null) {
        const window = t.slice(Math.max(0, m.index - 240), m.index + 240);
        if (/(linear|radial|conic)-gradient/i.test(window)) {
          out.push({ line: lineOf(t, m.index), text: m[0] });
        }
      }
      return out;
    },
  },
  {
    id: 'side-stripe',
    severity: 'P1',
    label: 'Side-stripe border (border-left/right > 1px as colored accent)',
    fix: 'redesign',
    find: (t) =>
      matches(t, /border-(left|right)\s*:\s*(?:[2-9]|\d{2,})px[^;]*/gi).filter(
        (h) => !/transparent/i.test(h.text)
      ),
  },
  {
    id: 'em-dash',
    severity: 'P2',
    label: 'Em-dash / "--" as a prose flourish (kinetic pause / dramatic aside)',
    fix: 'clarify',
    // Only flag the real tell: an em-dash between two lowercase prose words
    // ("workflow — seamlessly"). Skip structured labels where it's a legitimate
    // separator: number—label ("001 — ENGINE"), CAPS—CAPS ("NEXT — ISSUE 08"),
    // role—name bylines, and CJK labels. Also catch literal " -- " in prose.
    // Scan comment-stripped copy so notes/CSS don't fire.
    find: (t) => matches(stripComments(t), /[a-z]{2,}\s*—\s*[a-z]{2,}|[a-z]{2,}\s--\s[a-z]{2,}/g),
  },
  {
    id: 'numbered-scaffold',
    severity: 'P2',
    label: 'Numbered section scaffolding (01 · / 02 · / 03 ·)',
    fix: 'redesign',
    find: (t) => matches(t, /\b0[1-9]\s*[·.\-/]\s*[A-Z][a-z]/g),
  },
  {
    id: 'default-palette-token',
    severity: 'P2',
    label: 'Default-category palette token name (--cream/--sand/--paper…)',
    fix: 'soul',
    find: (t) =>
      matches(t, /--(cream|sand|paper|parchment|bone|flour|linen|wheat|biscuit|ivory)\b/gi),
  },
  {
    id: 'pure-bw',
    severity: 'P2',
    label: 'Pure #fff / #000 (untinted neutral)',
    fix: 'soul',
    find: (t) => matches(t, /#fff(?:fff)?\b|#000(?:000)?\b/gi),
  },
  {
    id: 'hard-333-border',
    severity: 'P2',
    label: 'Hard #333-ish border instead of translucent',
    fix: 'soul',
    find: (t) => matches(t, /border[^;{]*:\s*[^;]*#(?:333|444|222|ccc|ddd)\b[^;]*/gi),
  },
  {
    id: 'fake-precise-number',
    severity: 'P2',
    label: 'Fake-precise metric (e.g. 4.1×, 92.7%) — verify it has a source',
    fix: 'clarify',
    find: (t) => matches(t, />\s*\d{1,3}\.\d+\s*(?:×|x|%)\s*</g),
  },
];

// ---- motion layer rules (motion.md §8) -------------------------------------
// The regex-detectable subset of the micro-motion block list. The context-
// judgment items (durations >300ms, keyframes on rapid triggers, transform-
// origin — modals are exempt, exit symmetry) stay in audit.md Scan 2.B by eye.

const MOTION_RULES = [
  {
    id: 'ease-in',
    severity: 'P0',
    label: '`ease-in` on UI — delays the moment the user watches; use ease-out or a strong custom curve',
    fix: 'animate',
    // `ease-in` and `easeIn` are the tell; `ease-in-out` / `easeInOut` is a
    // legitimate on-screen-movement curve and must not fire. Comments stripped
    // so notes like "/* try ease-in */" don't count.
    find: (t) => matches(stripComments(t), /ease-?in(?!-?out)/gi),
  },
  {
    id: 'scale-0',
    severity: 'P0',
    label: '`scale(0)` transform — nothing appears from nothing; start from scale(0.9–0.97) + opacity:0',
    fix: 'animate',
    find: (t) => {
      // Only flag scale(0) inside a transform context (±120 chars), so math,
      // SVG attributes, and non-animated uses don't fire. `scaleY(0)` (bars
      // growing from a baseline) is a different pattern and never matches.
      const out = [];
      const re = /scale\(\s*0\s*\)/gi;
      const text = stripComments(t);
      let m;
      while ((m = re.exec(text)) !== null) {
        const win = text.slice(Math.max(0, m.index - 120), m.index + 120);
        if (/transform|gsap\.to|\banimate\(/.test(win)) {
          out.push({ line: lineOf(text, m.index), text: m[0] });
        }
        if (m.index === re.lastIndex) re.lastIndex++;
      }
      return out;
    },
  },
  {
    id: 'transition-all',
    severity: 'P0',
    label: '`transition: all` — animates unintended properties off-GPU; name the exact properties',
    fix: 'animate',
    find: (t) => matches(stripComments(t), /transition(?:-property)?\s*:\s*all\b/gi),
  },
];

// =============================================================================
// Impeccable-ported rules.
// Derived from pbakaus/impeccable (github.com/pbakaus/impeccable),
// cli/engine/rules/checks.mjs + cli/engine/shared/{constants,color,fonts}.mjs,
// licensed under the Apache License 2.0 (https://www.apache.org/licenses/LICENSE-2.0).
//
// Port: upstream runs on a DOM (computed styles, layout). This port runs on
// raw HTML/CSS text with no DOM, no deps. Faithful where it ports; deliberate
// simplifications (each noted inline): color parsing handles hex/rgb/named
// only — oklch()/lch()/color-mix() resolve as "unknown" and are SKIPPED rather
// than guessed, matching upstream's no-false-positive philosophy. Rules that
// fundamentally need computed styles / layout are NOT executed here — they are
// inventoried in IMPECCABLE_RULES with port:'runtime' and surface in
// NOT_COVERED (they need the Playwright pass, preflight.md §C).
// All 59 upstream rule ids are accounted for in IMPECCABLE_RULES below.
// =============================================================================

const OVERUSED_FONTS = new Set([
  'inter', 'roboto', 'open sans', 'lato', 'montserrat', 'arial', 'helvetica',
  'fraunces', 'instrument sans', 'instrument serif',
  'geist', 'geist sans', 'geist mono', 'mona sans',
  'plus jakarta sans', 'space grotesk', 'recoleta',
]);
const GENERIC_FONTS = new Set([
  'serif', 'sans-serif', 'monospace', 'cursive', 'fantasy', 'system-ui',
  'ui-serif', 'ui-sans-serif', 'ui-monospace', 'ui-rounded',
  '-apple-system', 'blinkmacsystemfont', 'segoe ui',
]);
const EM_DASH_FLOOR = 8;
const EM_DASH_CHARS_PER_DASH = 500;
const CSS_NAMED_COLORS = {
  black: { r: 0, g: 0, b: 0 }, white: { r: 255, g: 255, b: 255 }, silver: { r: 192, g: 192, b: 192 },
  gray: { r: 128, g: 128, b: 128 }, grey: { r: 128, g: 128, b: 128 }, red: { r: 255, g: 0, b: 0 },
  maroon: { r: 128, g: 0, b: 0 }, yellow: { r: 255, g: 255, b: 0 }, olive: { r: 128, g: 128, b: 0 },
  lime: { r: 0, g: 255, b: 0 }, green: { r: 0, g: 128, b: 0 }, aqua: { r: 0, g: 255, b: 255 },
  cyan: { r: 0, g: 255, b: 255 }, teal: { r: 0, g: 128, b: 128 }, blue: { r: 0, g: 0, b: 255 },
  navy: { r: 0, g: 0, b: 128 }, fuchsia: { r: 255, g: 0, b: 255 }, magenta: { r: 255, g: 0, b: 255 },
  purple: { r: 128, g: 0, b: 128 }, orange: { r: 255, g: 165, b: 0 }, gold: { r: 255, g: 215, b: 0 },
  coral: { r: 255, g: 127, b: 80 }, crimson: { r: 220, g: 20, b: 60 }, indigo: { r: 75, g: 0, b: 130 },
  violet: { r: 238, g: 130, b: 238 }, pink: { r: 255, g: 192, b: 203 }, salmon: { r: 250, g: 128, b: 114 },
  brown: { r: 165, g: 42, b: 42 }, tan: { r: 210, g: 180, b: 140 }, beige: { r: 245, g: 245, b: 220 },
  honeydew: { r: 240, g: 255, b: 240 }, azure: { r: 240, g: 255, b: 255 }, ivory: { r: 255, g: 255, b: 240 },
  lavender: { r: 230, g: 230, b: 250 }, mintcream: { r: 245, g: 255, b: 250 }, snow: { r: 255, g: 250, b: 250 },
  whitesmoke: { r: 245, g: 245, b: 245 }, gainsboro: { r: 220, g: 220, b: 220 }, darkslategray: { r: 47, g: 79, b: 79 },
  dimgray: { r: 105, g: 105, b: 105 }, slategray: { r: 112, g: 128, b: 144 }, lightgray: { r: 211, g: 211, b: 211 },
  darkred: { r: 139, g: 0, b: 0 }, firebrick: { r: 178, g: 34, b: 34 }, orangered: { r: 255, g: 69, b: 0 },
  darkorange: { r: 255, g: 140, b: 0 }, goldenrod: { r: 218, g: 165, b: 32 }, darkgoldenrod: { r: 184, g: 134, b: 11 },
  darkgreen: { r: 0, g: 100, b: 0 }, forestgreen: { r: 34, g: 139, b: 34 }, seagreen: { r: 46, g: 139, b: 87 },
  springgreen: { r: 0, g: 255, b: 127 }, turquoise: { r: 64, g: 224, b: 208 }, dodgerblue: { r: 30, g: 144, b: 255 },
  royalblue: { r: 65, g: 105, b: 225 }, midnightblue: { r: 25, g: 25, b: 112 }, darkslateblue: { r: 72, g: 61, b: 139 },
  mediumpurple: { r: 147, g: 112, b: 219 }, darkorchid: { r: 153, g: 50, b: 204 }, deeppink: { r: 255, g: 20, b: 147 },
  hotpink: { r: 255, g: 105, b: 180 }, tomato: { r: 255, g: 99, b: 71 }, chocolate: { r: 210, g: 105, b: 30 },
  saddlebrown: { r: 139, g: 69, b: 19 }, peru: { r: 205, g: 133, b: 63 }, burlywood: { r: 222, g: 184, b: 135 },
};

// Upstream: shared/color.mjs — subset used by the glow/halo/stripe scanners.
function relativeLuminance({ r, g, b }) {
  const [rs, gs, bs] = [r / 255, g / 255, b / 255].map((c) =>
    c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4
  );
  return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
}
function hasChroma(c, threshold = 30) {
  return !!c && Math.max(c.r, c.g, c.b) - Math.min(c.r, c.g, c.b) >= threshold;
}
function colorToHex(c) {
  return '#' + [c.r, c.g, c.b].map((v) => v.toString(16).padStart(2, '0')).join('');
}
// Simplified parseAnyColor: hex (#3/#4/#6/#8), rgb()/rgba(), named colors.
// oklch()/lch()/hsl()/color-mix() → null ("don't guess") — upstream parses
// these fully; ported simplification, see the section header.
function parseAnyColor(s) {
  if (!s || typeof s !== 'string') return null;
  const str = s.trim();
  if (str === 'transparent' || str === 'currentcolor' || str === 'inherit') return null;
  let m = str.match(/rgba?\(\s*(\d+(?:\.\d+)?)\s*[, ]\s*(\d+(?:\.\d+)?)\s*[, ]\s*(\d+(?:\.\d+)?)(?:\s*[,/]\s*([\d.]+))?\s*\)/i);
  if (m) return { r: Math.round(+m[1]), g: Math.round(+m[2]), b: Math.round(+m[3]), a: m[4] !== undefined ? +m[4] : 1 };
  m = str.match(/^#([0-9a-f]{3,8})$/i);
  if (m) {
    const h = m[1];
    if (h.length === 3 || h.length === 4) {
      return { r: parseInt(h[0] + h[0], 16), g: parseInt(h[1] + h[1], 16), b: parseInt(h[2] + h[2], 16), a: h.length === 4 ? parseInt(h[3] + h[3], 16) / 255 : 1 };
    }
    return { r: parseInt(h.slice(0, 2), 16), g: parseInt(h.slice(2, 4), 16), b: parseInt(h.slice(4, 6), 16), a: h.length === 8 ? parseInt(h.slice(6, 8), 16) / 255 : 1 };
  }
  const named = CSS_NAMED_COLORS[str.toLowerCase()];
  return named ? { ...named, a: 1 } : null;
}

// Upstream: checks.mjs collectCssCustomProps / resolveVarRefs (first-decl wins,
// single-level var() resolution, depth-capped).
function collectCssCustomProps(content) {
  const map = new Map();
  const re = /(--[\w-]+)\s*:\s*([^;{}]+)/g;
  let m;
  while ((m = re.exec(content)) !== null) if (!map.has(m[1])) map.set(m[1], m[2].trim());
  return map;
}
function resolveVarRefs(raw, customPropMap, depth = 0) {
  if (typeof raw !== 'string' || !raw.includes('var(') || depth > 8) return raw;
  return raw.replace(/var\(\s*(--[a-zA-Z0-9_-]+)\s*(?:,\s*([^)]+))?\)/g, (_m, name, fallback) => {
    const v = customPropMap.get(name);
    return v != null ? resolveVarRefs(v, customPropMap, depth + 1) : fallback ? resolveVarRefs(fallback.trim(), customPropMap, depth + 1) : _m;
  });
}
// Upstream: CSS_RULE_BLOCK_SOURCE + parseCssDeclBlock + cssLengthToPx + isZeroOffset.
const CSS_RULE_BLOCK_SOURCE = String.raw`([^{};]+)\{([^{}]*)\}`;
function parseCssDeclBlock(block) {
  const decls = new Map();
  for (const part of String(block || '').split(';')) {
    const idx = part.indexOf(':');
    if (idx <= 0) continue;
    const prop = part.slice(0, idx).trim().toLowerCase();
    const value = part.slice(idx + 1).replace(/\s*!important\s*$/i, '').trim();
    if (prop && value) decls.set(prop, value);
  }
  return decls;
}
function cssLengthToPx(value) {
  const m = String(value || '').trim().match(/^(-?[\d.]+)(px|rem|em)$/i);
  if (!m) return null;
  const n = parseFloat(m[1]);
  return m[2].toLowerCase() === 'px' ? n : n * 16;
}
function isZeroOffset(value) {
  return value != null && /^-?0(?:px|%|rem|em)?$/.test(String(value).trim());
}
function splitTopLevelCommas(str) {
  const parts = [];
  let depth = 0, start = 0;
  for (let i = 0; i < str.length; i++) {
    const ch = str[i];
    if (ch === '(') depth++;
    else if (ch === ')') depth = Math.max(0, depth - 1);
    else if (ch === ',' && depth === 0) { parts.push(str.slice(start, i).trim()); start = i + 1; }
  }
  const tail = str.slice(start).trim();
  if (tail) parts.push(tail);
  return parts;
}
// Upstream: checks.mjs findShadowColor / extractShadowLengths.
function findShadowColor(layer) {
  const fn = layer.match(/(?:rgba?|hsla?|hwb|oklch|oklab|lch|lab|color)\([^)]*\)/i);
  if (fn) return { color: parseAnyColor(fn[0]), start: fn.index, end: fn.index + fn[0].length };
  const hex = layer.match(/#[0-9a-fA-F]{3,8}\b/);
  if (hex) return { color: parseAnyColor(hex[0]), start: hex.index, end: hex.index + hex[0].length };
  const wordRe = /[a-zA-Z][a-zA-Z]*/g;
  let m;
  while ((m = wordRe.exec(layer)) !== null) {
    const named = CSS_NAMED_COLORS[m[0].toLowerCase()];
    if (named) return { color: { ...named, a: 1 }, start: m.index, end: m.index + m[0].length };
  }
  return null;
}
function extractShadowLengths(layer, colorStart, colorEnd) {
  const stripped = colorStart != null ? layer.slice(0, colorStart) + ' ' + layer.slice(colorEnd) : layer;
  const vals = [];
  const re = /(-?\d*\.?\d+)(px|rem|em)?/g;
  let m;
  while ((m = re.exec(stripped)) !== null) {
    let v = parseFloat(m[1]);
    if (m[2] === 'rem' || m[2] === 'em') v *= 16;
    vals.push(v);
  }
  return vals;
}

// Upstream: checks.mjs cssTextHasDarkRootBg — dark literal / Tailwind dark bg /
// ROOT-scoped background resolving (via var()) to a dark color.
function cssTextHasDarkRootBg(content, customProps) {
  const darkBgRe = /background(?:-color)?\s*:\s*(?:#(?:0[0-9a-f]|1[0-9a-f]|2[0-3])[0-9a-f]{4}\b|#(?:0|1)[0-9a-f]{2}\b|rgb\(\s*(\d{1,2})\s*,\s*(\d{1,2})\s*,\s*(\d{1,2})\s*\))/i;
  if (darkBgRe.test(content) || /\bbg-(?:gray|slate|zinc|neutral|stone)-(?:9\d{2}|800)\b/.test(content)) return true;
  const rootScopes = [];
  const blockRe = /(?:^|[}\s,;>])(?:body|html|:root)\s*(?:,[^{]*)?\{([^}]*)\}/gi;
  let sm;
  while ((sm = blockRe.exec(content)) !== null) rootScopes.push(sm[1]);
  const inlineBody = content.match(/<body[^>]*\bstyle\s*=\s*"([^"]*)"/i);
  if (inlineBody) rootScopes.push(inlineBody[1]);
  for (const scope of rootScopes) {
    const bgRe = /background(?:-color)?\s*:\s*([^;{}]+)/gi;
    let bm;
    while ((bm = bgRe.exec(scope)) !== null) {
      const c = parseAnyColor(resolveVarRefs(bm[1].trim(), customProps));
      if (c && (c.a ?? 1) > 0.5 && relativeLuminance(c) < 0.1) return true;
    }
  }
  return false;
}

// Upstream: scanCssTextForGlow — zero-offset chromatic halo (any bg) and
// chromatic blurred shadow on a dark page. One finding per declaration.
function scanCssTextForGlow(content) {
  const customProps = collectCssCustomProps(content);
  const hasDarkBg = cssTextHasDarkRootBg(content, customProps);
  const results = [];
  const shadowRe = /\b(box-shadow|text-shadow)\s*:\s*([^;{}]+)/gi;
  let m;
  while ((m = shadowRe.exec(content)) !== null) {
    const prop = m[1].toLowerCase();
    const value = resolveVarRefs(m[2].trim(), customProps);
    for (const layer of value.split(/,(?![^(]*\))/)) {
      const colorInfo = findShadowColor(layer);
      if (!colorInfo || !colorInfo.color || !hasChroma(colorInfo.color, 30)) continue;
      const vals = extractShadowLengths(layer, colorInfo.start, colorInfo.end);
      if (vals.length < 3 || vals[2] <= 4) continue;
      const zeroOffset = vals[0] === 0 && vals[1] === 0;
      if (!zeroOffset && !hasDarkBg) continue;
      results.push({
        index: m.index,
        snippet: zeroOffset ? `Zero-offset ${prop} glow (${colorToHex(colorInfo.color)})` : `Colored ${prop} glow (${colorToHex(colorInfo.color)}) on dark page`,
      });
      break;
    }
  }
  return results;
}

// Upstream: scanCssTextForRadialHalo — radial-gradient halo fading to
// transparent on a dark page (px-stop dot/texture patterns exempt).
function scanCssTextForRadialHalo(content) {
  const customProps = collectCssCustomProps(content);
  if (!cssTextHasDarkRootBg(content, customProps)) return [];
  const findings = [];
  const seen = new Set();
  const declRe = /background(?:-image)?\s*:\s*([^;{}]+)/gi;
  const colorTokenRe = /(?:rgba?|hsla?|oklch|oklab|lab|lch|hwb|color-mix)\([^)]*(?:\([^)]*\))?[^)]*\)|#[0-9a-f]{3,8}\b|\btransparent\b/i;
  let m;
  while ((m = declRe.exec(content)) !== null) {
    const value = resolveVarRefs(m[1].trim(), customProps);
    if (/url\s*\(/i.test(value)) continue;
    const gradRe = /(repeating-)?radial-gradient\(/gi;
    let g;
    while ((g = gradRe.exec(value)) !== null) {
      if (g[1]) continue;
      let depth = 0, end = -1;
      const open = value.indexOf('(', g.index);
      for (let i = open; i < value.length; i++) {
        if (value[i] === '(') depth++;
        else if (value[i] === ')') { depth--; if (depth === 0) { end = i; break; } }
      }
      if (end < 0) break;
      const args = splitTopLevelCommas(value.slice(open + 1, end));
      if (args.length < 2) continue;
      const stops = args.filter((a) => colorTokenRe.test(a));
      if (stops.length < 2) continue;
      if (stops.some((s) => { const pm = s.match(/(-?[\d.]+)px\b/); return pm && Math.abs(parseFloat(pm[1])) <= 24; })) continue;
      const first = stops[0].match(colorTokenRe);
      const last = stops[stops.length - 1].match(colorTokenRe);
      if (!first || !last) continue;
      const lastColor = /^transparent$/i.test(last[0]) ? { r: 0, g: 0, b: 0, a: 0 } : parseAnyColor(last[0]);
      if (!lastColor || (lastColor.a ?? 1) > 0.05) continue;
      const firstColor = /^transparent$/i.test(first[0]) ? null : parseAnyColor(first[0]);
      if (!firstColor || (firstColor.a ?? 1) < 0.7) continue;
      const spread = Math.max(firstColor.r, firstColor.g, firstColor.b) - Math.min(firstColor.r, firstColor.g, firstColor.b);
      if (spread < 24) continue;
      const snippet = `radial-gradient halo (${colorToHex(firstColor)} → transparent) on dark page`;
      if (seen.has(snippet)) continue;
      seen.add(snippet);
      findings.push({ index: m.index, snippet });
    }
  }
  return findings;
}

// Upstream: scanCssTextForGridBackground — hairline linear-gradient grid/line
// fields tiled by a fixed px cell (the "codex grid" tell). Both signals must
// co-occur in one declaration block.
function scanCssTextForGridBackground(content) {
  const hairlineRe = /\b\d{1,3}px\s*,\s*transparent\s+\d{1,3}px/gi;
  const invertedHairlineRe = /transparent\s+calc\(100%\s*-\s*\d{1,3}px\)/gi;
  const sizeDeclPxRe = /background-size\s*:[^;{}"']*\b\d{1,3}px\b/i;
  const sizeDeclPxPairRe = /background-size\s*:[^;{}"']*\b\d{1,3}px\s+\d{1,3}px/i;
  const shorthandPxAnyRe = /\/\s*\d{1,3}px\b/;
  const shorthandPxPairRe = /\/\s*\d{1,3}px\s+\d{1,3}px/;
  const bgDeclRe = /\bbackground(?:-image)?\s*:\s*([^;{}"']*)/gi;
  const blockRe = /\{([^{}]*)\}|style\s*=\s*"([^"]*)"|style\s*=\s*'([^']*)'/gi;
  const findings = [];
  let blk;
  while ((blk = blockRe.exec(content)) !== null) {
    const block = blk[1] || blk[2] || blk[3] || '';
    let hairlineCount = 0;
    let bgJoined = '';
    let bm;
    bgDeclRe.lastIndex = 0;
    while ((bm = bgDeclRe.exec(block)) !== null) {
      hairlineCount += (bm[1].match(hairlineRe) || []).length;
      hairlineCount += (bm[1].match(invertedHairlineRe) || []).length;
      bgJoined += `${bm[1]};`;
    }
    if (hairlineCount === 0) continue;
    const hasPxCell = sizeDeclPxRe.test(block) || shorthandPxAnyRe.test(bgJoined);
    const hasPxPairCell = sizeDeclPxPairRe.test(block) || shorthandPxPairRe.test(bgJoined);
    if ((hairlineCount >= 2 && hasPxCell) || hasPxPairCell) {
      findings.push({ index: blk.index, snippet: 'hairline gradient grid/line field (codex-grid background)' });
      break;
    }
  }
  return findings;
}

// Upstream: scanCssTextForPseudoStripe + scanCssTextForInsetStripe — the
// side-tab accent stripe drawn as an absolutely-positioned ::before/::after
// bar or a single-edge inset box-shadow (element border checks can't see them).
function scanCssTextForPseudoStripe(rawContent) {
  const content = String(rawContent || '').replace(/\/\*[\s\S]*?\*\//g, (block) => block.replace(/[^\n]/g, ' '));
  const customProps = collectCssCustomProps(content);
  const findings = [];
  const seen = new Set();
  const ruleRe = new RegExp(CSS_RULE_BLOCK_SOURCE, 'g');
  let m;
  while ((m = ruleRe.exec(content)) !== null) {
    const selector = m[1].trim();
    if (!/::?(?:before|after)\b/i.test(selector)) continue;
    if (/\b(?:blockquote|pre|code|nav|hr)\b/i.test(selector)) continue;
    const decls = parseCssDeclBlock(m[2]);
    const position = decls.get('position');
    if (position !== 'absolute' && position !== 'fixed') continue;
    const widthPx = cssLengthToPx(resolveVarRefs(decls.get('width') || decls.get('inline-size') || '', customProps));
    const heightPx = cssLengthToPx(resolveVarRefs(decls.get('height') || decls.get('block-size') || '', customProps));
    const verticalCandidate = widthPx != null && widthPx >= 3 && widthPx <= 12;
    const horizontalCandidate =
      heightPx != null && heightPx >= 3 && heightPx <= 12 &&
      !/(?:^|[\s>+~,(])(?:a|button|summary|tr|td|th|table|li)(?![\w-])/i.test(selector) &&
      !/\[aria-selected\s*[*^$|~]?=\s*["']?true/i.test(selector) &&
      !/\[aria-current(?!\s*[*^$|~]?=\s*["']?false)/i.test(selector) &&
      !/(?:^|[\s._[-])(?:active|current|selected|btn[\w-]*|button[\w-]*|link[\w-]*)(?![\w])/i.test(selector) &&
      !/:(?:hover|focus|focus-visible|focus-within|active|checked)\b/i.test(selector);
    if (!verticalCandidate && !horizontalCandidate) continue;
    const offsets = { top: decls.get('top'), right: decls.get('right'), bottom: decls.get('bottom'), left: decls.get('left') };
    const inset = decls.get('inset');
    if (inset) {
      const p = inset.split(/\s+/);
      const [t, r, b, l] = p.length === 1 ? [p[0], p[0], p[0], p[0]] : p.length === 2 ? [p[0], p[1], p[0], p[1]] : p.length === 3 ? [p[0], p[1], p[2], p[1]] : p;
      if (offsets.top == null) offsets.top = t;
      if (offsets.right == null) offsets.right = r;
      if (offsets.bottom == null) offsets.bottom = b;
      if (offsets.left == null) offsets.left = l;
    }
    if (offsets.left == null) offsets.left = decls.get('inset-inline-start');
    if (offsets.right == null) offsets.right = decls.get('inset-inline-end');
    const heightValue = String(resolveVarRefs(decls.get('height') || decls.get('block-size') || '', customProps)).trim();
    const widthValue = String(resolveVarRefs(decls.get('width') || decls.get('inline-size') || '', customProps)).trim();
    let edge = null;
    let thicknessPx = null;
    if (verticalCandidate) {
      const topPx = cssLengthToPx(resolveVarRefs(String(offsets.top ?? ''), customProps));
      const bottomPx = cssLengthToPx(resolveVarRefs(String(offsets.bottom ?? ''), customProps));
      const fullHeight = (isZeroOffset(offsets.top) && isZeroOffset(offsets.bottom)) || /^100(?:\.0*)?%$/.test(heightValue) ||
        (topPx != null && bottomPx != null && topPx >= 0 && topPx <= 20 && bottomPx >= 0 && bottomPx <= 20);
      if (fullHeight) {
        edge = isZeroOffset(offsets.left) ? 'left' : isZeroOffset(offsets.right) ? 'right' : null;
        thicknessPx = widthPx;
      }
    }
    if (!edge && horizontalCandidate) {
      const fullWidth = (isZeroOffset(offsets.left) && isZeroOffset(offsets.right)) || /^100(?:\.0*)?%$/.test(widthValue);
      if (fullWidth) {
        edge = isZeroOffset(offsets.top) ? 'top' : isZeroOffset(offsets.bottom) ? 'bottom' : null;
        thicknessPx = heightPx;
      }
    }
    if (!edge) continue;
    const bg = String(resolveVarRefs(decls.get('background-color') || decls.get('background') || '', customProps)).trim();
    if (!bg || /^(?:none|transparent|inherit|initial|unset|currentcolor)$/i.test(bg)) continue;
    const colorToken = bg.match(/(?:rgba?|hsla?|oklch|oklab|lab|lch|hwb)\([^)]*\)|#[0-9a-f]{3,8}\b/i);
    const parsed = parseAnyColor(colorToken ? colorToken[0] : bg);
    if (parsed) {
      if ((parsed.a ?? 1) < 0.1) continue;
      if (Math.max(parsed.r, parsed.g, parsed.b) - Math.min(parsed.r, parsed.g, parsed.b) < 30) continue;
    } else if (/^(?:white|black|gray|grey|silver)$/i.test(bg)) {
      continue;
    }
    if (seen.has(selector)) continue;
    seen.add(selector);
    findings.push({ index: m.index, snippet: `${selector} — absolute ${thicknessPx}px pseudo-element stripe (${edge}: 0)` });
  }
  return findings;
}
function scanCssTextForInsetStripe(content) {
  const customProps = collectCssCustomProps(content);
  const findings = [];
  const seen = new Set();
  const ruleRe = new RegExp(CSS_RULE_BLOCK_SOURCE, 'g');
  let m;
  while ((m = ruleRe.exec(content)) !== null) {
    const selector = m[1].trim();
    if (/:(?:hover|focus|focus-visible|focus-within|active|checked|target)\b/i.test(selector)) continue;
    if (/\[aria-selected\s*[*^$|~]?=\s*["']?true/i.test(selector)) continue;
    if (/\[aria-current(?!\s*[*^$|~]?=\s*["']?false)/i.test(selector)) continue;
    if (/(?:^|[\s._[-])(?:active|current|selected)(?![\w])/i.test(selector)) continue;
    if (/(?:^|[\s>+~,(])(?:button|hr|tr|td|th|table|blockquote|pre|code)(?![\w-])/i.test(selector)) continue;
    const decls = parseCssDeclBlock(m[2]);
    const shadow = decls.get('box-shadow');
    if (!shadow || !/\binset\b/i.test(shadow)) continue;
    const declaredWidth = cssLengthToPx(resolveVarRefs(decls.get('width') || decls.get('inline-size') || '', customProps));
    if (declaredWidth != null && declaredWidth <= 40) continue;
    const value = resolveVarRefs(shadow, customProps);
    for (const layer of value.split(/,(?![^(]*\))/)) {
      if (!/\binset\b/i.test(layer)) continue;
      const colorInfo = findShadowColor(layer);
      if (!colorInfo || !colorInfo.color) continue;
      const c = colorInfo.color;
      if ((c.a ?? 1) < 0.1) continue;
      if (Math.max(c.r, c.g, c.b) - Math.min(c.r, c.g, c.b) < 30) continue;
      const vals = extractShadowLengths(layer, colorInfo.start, colorInfo.end);
      const x = vals[0] || 0, y = vals[1] || 0, blur = vals[2] || 0, sp = vals[3] || 0;
      if (blur !== 0 || sp !== 0) continue;
      const ax = Math.abs(x), ay = Math.abs(y);
      const isStripe = (ax >= 3 && ax <= 12 && ay === 0) || (ay >= 3 && ay <= 12 && ax === 0);
      if (!isStripe) continue;
      if (seen.has(selector)) break;
      seen.add(selector);
      const edge = ay === 0 ? (x > 0 ? 'left' : 'right') : (y > 0 ? 'top' : 'bottom');
      findings.push({ index: m.index, snippet: `${selector} — inset box-shadow ${ay === 0 ? ax : ay}px stripe (${edge})` });
      break;
    }
  }
  return findings;
}

// Upstream: collectMarqueeKeyframes + scanCssTextForMarquee (X-travel >= 20%,
// infinite animation bound to a marquee keyframe) + collectPulseKeyframes
// (opacity / box-shadow / scale keyframes) for the pulsing-dot rule.
function collectMarqueeKeyframes(content) {
  const names = new Set();
  const re = /@(?:-webkit-)?keyframes\s+([\w-]+)\s*\{/g;
  let m;
  while ((m = re.exec(content)) !== null) {
    let depth = 1;
    let i = re.lastIndex;
    while (i < content.length && depth > 0) {
      const ch = content.charCodeAt(i);
      if (ch === 0x7b) depth++;
      else if (ch === 0x7d) depth--;
      i++;
    }
    const body = content.slice(re.lastIndex, Math.max(re.lastIndex, i - 1));
    re.lastIndex = i;
    const pct = [];
    const xRe = /\btranslate(?:X|3d)?\(\s*(-?[\d.]+)%/gi;
    let xm;
    while ((xm = xRe.exec(body)) !== null) pct.push(parseFloat(xm[1]));
    if (pct.length === 0) continue;
    if (pct.length === 1 && /\bscale\(|\bopacity\s*:/i.test(body)) continue;
    const travelPct = pct.length > 1 ? Math.max(...pct) - Math.min(...pct) : Math.abs(pct[0]);
    if (travelPct >= 20) names.add(m[1]);
  }
  return names;
}
const ANIMATION_VALUE_KEYWORDS = new Set([
  'ease', 'ease-in', 'ease-out', 'ease-in-out', 'linear', 'infinite', 'alternate',
  'alternate-reverse', 'normal', 'reverse', 'none', 'forwards', 'backwards', 'both',
  'running', 'paused', 'step-start', 'step-end', 'inherit', 'initial', 'unset',
]);
function infiniteAnimationNames(decls) {
  const out = [];
  const shorthand = decls.get('animation');
  if (shorthand) {
    for (const layer of shorthand.split(/,(?![^(]*\))/)) {
      if (!/\binfinite\b/i.test(layer)) continue;
      const name = layer.split(/\s+/).find((t) => /^[a-zA-Z_-][\w-]*$/.test(t) && !ANIMATION_VALUE_KEYWORDS.has(t.toLowerCase()));
      if (name) out.push(name);
    }
  }
  const nameDecl = decls.get('animation-name');
  if (nameDecl && /\binfinite\b/i.test(decls.get('animation-iteration-count') || '')) {
    for (const raw of nameDecl.split(',')) {
      const t = raw.trim();
      if (t && t.toLowerCase() !== 'none') out.push(t);
    }
  }
  return out;
}
function scanCssTextForMarquee(content) {
  const findings = [];
  if (/<marquee\b/i.test(content)) findings.push({ index: 0, snippet: '<marquee> element' });
  const marqueeKeyframes = collectMarqueeKeyframes(content);
  if (marqueeKeyframes.size === 0) return findings;
  const seen = new Set();
  const ruleRe = new RegExp(CSS_RULE_BLOCK_SOURCE, 'g');
  let m;
  while ((m = ruleRe.exec(content)) !== null) {
    const selector = m[1].trim();
    const decls = parseCssDeclBlock(m[2]);
    for (const name of infiniteAnimationNames(decls)) {
      if (!marqueeKeyframes.has(name)) continue;
      const key = `${selector} ${name}`;
      if (seen.has(key)) continue;
      seen.add(key);
      findings.push({ index: m.index, snippet: `${selector} — infinite horizontal loop animation "${name}"` });
    }
  }
  return findings;
}
function scanCssTextForPulse(content) {
  const map = new Map();
  const re = /@(?:-webkit-)?keyframes\s+([\w-]+)\s*\{/g;
  let m;
  while ((m = re.exec(content)) !== null) {
    let depth = 1;
    let i = re.lastIndex;
    while (i < content.length && depth > 0) {
      const ch = content.charCodeAt(i);
      if (ch === 0x7b) depth++;
      else if (ch === 0x7d) depth--;
      i++;
    }
    const body = content.slice(re.lastIndex, Math.max(re.lastIndex, i - 1));
    const pulses = /\bopacity\s*:/i.test(body) || /\bbox-shadow\s*:/i.test(body) || /\btransform\s*:[^;{}]*\bscale/i.test(body);
    if (!map.has(m[1]) || pulses) map.set(m[1], pulses);
    re.lastIndex = i;
  }
  const findings = [];
  const seen = new Set();
  const ruleRe = new RegExp(CSS_RULE_BLOCK_SOURCE, 'g');
  while ((m = ruleRe.exec(content)) !== null) {
    const selector = m[1].trim();
    const decls = parseCssDeclBlock(m[2]);
    for (const name of infiniteAnimationNames(decls)) {
      if (map.get(name) !== true) continue;
      const key = `${selector} ${name}`;
      if (seen.has(key)) continue;
      seen.add(key);
      findings.push({ index: m.index, snippet: `${selector} — infinite pulse animation "${name}"` });
    }
  }
  return findings;
}

// Upstream: checkEmDashOveruse — density gate (floor 8 dashes AND >= 1 dash
// per 500 chars of body text), unlike finesse's presence-based em-dash rule.
// Ported difference: upstream counts rendered body text (innerText); here the
// comment-, script- and style-stripped source text stands in for it so code,
// CSS custom properties (--var) and comments don't inflate the count.
function stripNonCopy(text) {
  return stripComments(String(text || ''))
    .replace(/<script[\s\S]*?<\/script>/gi, (m) => m.replace(/[^\n]/g, ' '))
    .replace(/<style[\s\S]*?<\/style>/gi, (m) => m.replace(/[^\n]/g, ' '));
}
function checkEmDashOveruse(text) {
  const body = stripNonCopy(text).replace(/\s+/g, ' ');
  let count = 0;
  let first = -1;
  const re = /[—]|--(?=\S)/g;
  let m;
  while ((m = re.exec(body)) !== null) {
    if (first < 0) first = m.index;
    count++;
  }
  if (count < EM_DASH_FLOOR) return [];
  if (body.length > count * EM_DASH_CHARS_PER_DASH) return [];
  return [{ index: first < 0 ? 0 : first, snippet: `${count} em-dashes in body text (density ≥ 1/500 chars)` }];
}

// Upstream: shared/fonts.mjs extractGoogleFontFamilies + OVERUSED_FONTS.
const GOOGLE_FONTS_URL_RE = /fonts\.googleapis\.com\/css2?\?[^"'\s)<>]*/gi;
function extractGoogleFontFamilies(text) {
  const families = [];
  GOOGLE_FONTS_URL_RE.lastIndex = 0;
  let urlMatch;
  while ((urlMatch = GOOGLE_FONTS_URL_RE.exec(text)) !== null) {
    const url = urlMatch[0];
    const queryStart = url.indexOf('?');
    if (queryStart === -1) continue;
    const params = new URLSearchParams(url.slice(queryStart + 1).replace(/&amp;/g, '&'));
    for (const value of params.getAll('family')) {
      for (const part of String(value || '').split('|')) {
        const fam = part.split(':')[0].trim().toLowerCase();
        if (fam) families.push(fam);
      }
    }
  }
  return families;
}

// Upstream: checks.mjs theater-slop-phrase — "X theater" framing copy.
const THEATER_RE = /\b(\w+)\s+theater\b/gi;

// Upstream: checks.mjs isEmojiOnlyText (emoji-only text nodes — icon-tile
// ancestor of the emoji policy, SKILL.md §3.D). Static approximation: a text
// node whose content is only emoji + whitespace. Range narrowed vs upstream:
// pictograph emoji (\u{1F000}–\u{1FAFF} incl. flags/modifiers) only — the
// upstream \u{2600}–\u{27BF} band (weather symbols + dingbats) is typographic
// ornament (✦ ★ ◆ …), not emoji, and over-fires as a standalone rule.
const EMOJI_ONLY_RE = />([\s\u{1F000}-\u{1FAFF}\u{FE0F}\u{200D}\u{1F3FB}-\u{1F3FF}]+)</gu;
const EMOJI_CHAR_RE = /[\u{1F000}-\u{1FAFF}\u{FE0F}\u{200D}\u{1F3FB}-\u{1F3FF}]/u;
function scanEmojiOnlyText(text) {
  const hits = [];
  EMOJI_ONLY_RE.lastIndex = 0;
  let m;
  while ((m = EMOJI_ONLY_RE.exec(text)) !== null) {
    if (EMOJI_CHAR_RE.test(m[1])) {
      hits.push({ index: m.index, snippet: `emoji-only text node "${m[1].trim().slice(0, 20)}"` });
    }
    if (m.index === EMOJI_ONLY_RE.lastIndex) EMOJI_ONLY_RE.lastIndex++;
  }
  return hits;
}

// The impeccable rule inventory: all 59 upstream rule ids, with the port
// status of each. `runtime` rules need computed styles / layout / a live
// browser and are NOT executed here — they surface in NOT_COVERED and the
// agent runs them via the Playwright pass (preflight.md §C).
const IMPECCABLE_RULES = [
  // Ported to static scanning (executed below):
  { id: 'em-dash-overuse', name: 'Em-dash overuse', port: 'ported' },
  { id: 'overused-font', name: 'Overused font (Google Fonts)', port: 'ported' },
  { id: 'codex-grid-background', name: 'Codex hairline grid background', port: 'ported' },
  { id: 'dark-glow', name: 'Chromatic glow (zero-offset halo / dark-page glow)', port: 'ported' },
  { id: 'radial-halo', name: 'Radial-gradient halo on dark page', port: 'ported' },
  { id: 'side-tab', name: 'Side-tab accent stripe (CSS pseudo-element / inset-shadow variant)', port: 'ported' },
  { id: 'marquee', name: 'Marquee / infinite horizontal loop — finesse allows exactly one per page (count 1 is fine)', port: 'ported' },
  { id: 'pulsing-dot', name: 'Pulsing status dot', port: 'ported' },
  { id: 'theater-slop-phrase', name: '"X theater" framing copy', port: 'ported' },
  { id: 'emoji-only-text', name: 'Emoji-only text node', port: 'ported' },
  { id: 'gradient-text', name: 'Gradient text', port: 'ported' }, // finesse's own rule covers it
  { id: 'numbered-section-labels', name: 'Numbered section labels', port: 'ported' }, // finesse's numbered-scaffold covers it
  { id: 'em-dash', name: 'Em-dash flourish', port: 'ported' }, // finesse's em-dash rule covers it
  // Runtime-only (DOM / computed styles / layout / live browser):
  { id: 'border-accent-on-rounded', name: 'Border accent on rounded element', port: 'runtime', note: 'needs computed border width + radius' },
  { id: 'flat-type-hierarchy', name: 'Flat type hierarchy', port: 'runtime', note: 'needs rendered font sizes across headings' },
  { id: 'ai-color-palette', name: 'AI color palette', port: 'runtime', note: 'needs computed effective background colors' },
  { id: 'cream-palette', name: 'Cream / beige palette', port: 'runtime', note: 'needs computed page background' },
  { id: 'nested-cards', name: 'Nested cards', port: 'runtime', note: 'needs DOM nesting + computed surfaces' },
  { id: 'monotonous-spacing', name: 'Monotonous spacing', port: 'runtime', note: 'needs layout metrics' },
  { id: 'bounce-easing', name: 'Bounce / elastic easing', port: 'runtime', note: 'needs computed animation-timing-function' },
  { id: 'blinking-cursor', name: 'Decorative blinking cursor', port: 'runtime', note: 'needs rendered caret/typing animation' },
  { id: 'shape-assembled-illustration', name: 'Shape-assembled illustration', port: 'runtime', note: 'visual judgement' },
  { id: 'radial-spotlight-glow', name: 'Radial spotlight glow', port: 'runtime', note: 'layout-dependent variant of dark-glow' },
  { id: 'icon-tile-stack', name: 'Icon tile stack', port: 'runtime', note: 'needs DOM shape + computed geometry' },
  { id: 'italic-serif-display', name: 'Italic serif display', port: 'runtime', note: 'needs resolved font stacks' },
  { id: 'hero-eyebrow-chip', name: 'Hero eyebrow chip', port: 'runtime', note: 'needs rendered hero composition' },
  { id: 'kicker-above-heading', name: 'Kicker above heading', port: 'runtime', note: 'needs DOM heading context' },
  { id: 'marketing-buzzword', name: 'Marketing buzzword', port: 'runtime', note: 'copy judgement — finesse anti-cheap.md has the family list' },
  { id: 'aphoristic-cadence', name: 'Aphoristic cadence', port: 'runtime', note: 'copy judgement' },
  { id: 'oversized-h1', name: 'Oversized h1', port: 'runtime', note: 'needs computed px size vs viewport' },
  { id: 'broken-image', name: 'Broken image', port: 'runtime', note: 'needs a live browser' },
  { id: 'script-error', name: 'Script error', port: 'runtime', note: 'needs a live browser' },
  { id: 'content-hidden-at-rest', name: 'Content hidden at rest', port: 'runtime', note: 'needs rendered visibility' },
  { id: 'edge-flush-cards', name: 'Edge-flush cards', port: 'runtime', note: 'needs layout metrics' },
  { id: 'text-occlusion', name: 'Text occlusion', port: 'runtime', note: 'needs rendered overlap' },
  { id: 'first-viewport-column-overflow', name: 'First-viewport column overflow', port: 'runtime', note: 'needs layout metrics' },
  { id: 'gray-on-color', name: 'Gray text on color', port: 'runtime', note: 'needs computed colors' },
  { id: 'low-contrast', name: 'Low contrast', port: 'runtime', note: 'needs computed colors' },
  { id: 'layout-transition', name: 'Layout transition', port: 'runtime', note: 'needs computed animation on layout props' },
  { id: 'line-length', name: 'Line length', port: 'runtime', note: 'needs rendered measure' },
  { id: 'cramped-padding', name: 'Cramped padding', port: 'runtime', note: 'needs computed padding' },
  { id: 'body-text-viewport-edge', name: 'Body text bleeding to viewport edge', port: 'runtime', note: 'needs layout metrics' },
  { id: 'tight-leading', name: 'Tight line-height', port: 'runtime', note: 'needs computed line-height/font-size' },
  { id: 'skipped-heading', name: 'Skipped heading level', port: 'runtime', note: 'needs DOM heading order' },
  { id: 'heading-rhythm', name: 'Heading rhythm', port: 'runtime', note: 'needs rendered heading sizes' },
  { id: 'justified-text', name: 'Justified text without hyphens', port: 'runtime', note: 'needs computed text-align' },
  { id: 'tiny-text', name: 'Tiny body text', port: 'runtime', note: 'needs computed font size' },
  { id: 'undersized-ui-text', name: 'Undersized functional text', port: 'runtime', note: 'needs computed font size' },
  { id: 'all-caps-body', name: 'All-caps body text', port: 'runtime', note: 'needs rendered text length' },
  { id: 'wide-tracking', name: 'Wide letter-spacing on body', port: 'runtime', note: 'needs computed letter-spacing' },
  { id: 'text-overflow', name: 'Text overflow', port: 'runtime', note: 'needs rendered overflow' },
  { id: 'repeated-container-text', name: 'Repeated container text', port: 'runtime', note: 'needs DOM text comparison' },
  { id: 'clipped-overflow-container', name: 'Clipped overflow container', port: 'runtime', note: 'needs rendered overflow' },
  { id: 'design-system-font', name: 'Design-system font drift', port: 'runtime', note: 'needs DESIGN.md tokens' },
  { id: 'design-system-color', name: 'Design-system color drift', port: 'runtime', note: 'needs DESIGN.md tokens' },
  { id: 'design-system-radius', name: 'Design-system radius drift', port: 'runtime', note: 'needs DESIGN.md tokens' },
  { id: 'design-system-font-size', name: 'Design-system font-size drift', port: 'runtime', note: 'needs DESIGN.md tokens' },
  { id: 'gpt-thin-border-wide-shadow', name: 'GPT thin-border wide-shadow', port: 'runtime', note: 'needs computed border/shadow' },
  { id: 'repeating-stripes-gradient', name: 'Repeating stripes gradient', port: 'runtime', note: 'needs computed background' },
  { id: 'image-hover-transform', name: 'Image hover transform', port: 'runtime', note: 'needs rendered hover state' },
];
const IMPECCABLE_RUNTIME = IMPECCABLE_RULES.filter((r) => r.port === 'runtime');

// The static rules wired into the run loop (id → find() returning [{index, snippet}]).
const IMPECCABLE_STATIC_CHECKS = {
  'em-dash-overuse': (t) => checkEmDashOveruse(t),
  'overused-font': (t) => {
    const used = extractGoogleFontFamilies(t);
    const hits = [];
    for (const fam of used) {
      if (OVERUSED_FONTS.has(fam) && !GENERIC_FONTS.has(fam)) {
        hits.push({ index: 0, snippet: `Google Font "${fam}" — overused monoculture face` });
      }
    }
    return hits;
  },
  'codex-grid-background': (t) => scanCssTextForGridBackground(t),
  'dark-glow': (t) => scanCssTextForGlow(t),
  'radial-halo': (t) => scanCssTextForRadialHalo(t),
  'side-tab': (t) => [...scanCssTextForPseudoStripe(t), ...scanCssTextForInsetStripe(t)],
  'marquee': (t) => scanCssTextForMarquee(t),
  'pulsing-dot': (t) => scanCssTextForPulse(t),
  'theater-slop-phrase': (t) => {
    const hits = [];
    let m;
    const body = stripComments(t);
    THEATER_RE.lastIndex = 0;
    while ((m = THEATER_RE.exec(body)) !== null) {
      hits.push({ index: m.index, snippet: `"${m[0].trim()}" — "X theater" framing copy` });
      if (m.index === THEATER_RE.lastIndex) THEATER_RE.lastIndex++;
    }
    return hits;
  },
  'emoji-only-text': (t) => scanEmojiOnlyText(stripComments(t)),
};

// ---- finesse-specific: spectacle claimed vs shown --------------------------
// Look for a stated SPECTACLE value (in comments / Design Read / data-attr).
function spectacleCheck(text) {
  const claim = text.match(/SPECTACLE\s*[=:]\s*(\d{1,2})/i);
  if (!claim) return null;
  const value = parseInt(claim[1], 10);
  const line = lineOf(text, claim.index);
  // Evidence of a real engine.
  const enginePatterns = [
    /\bthree(?:\.min)?\.js\b|\bTHREE\b|from\s+['"]three['"]/,
    /\bgetContext\(\s*['"](?:webgl2?|2d)['"]/,
    /\bgsap\b|ScrollTrigger/,
    /requestAnimationFrame/,
    /\bnew\s+OffscreenCanvas\b/,
    /animation-timeline\s*:/i,
  ];
  const hasEngine = enginePatterns.some((re) => re.test(text));
  if (value >= 7 && !hasEngine) {
    return {
      id: 'spectacle-not-shown',
      severity: 'P0',
      label: `SPECTACLE ${value} claimed but no engine found (three/canvas/gsap/rAF/CSS-timeline)`,
      fix: 'animate / bolder',
      hits: [{ line, text: `claimed SPECTACLE=${value}` }],
    };
  }
  return null;
}

// Reduced-motion fallback presence. Only continuous/scroll-driven motion gates a
// P0 — rAF loops, gsap/ScrollTrigger, or @keyframes (which often run infinitely).
// A bare hover `transition:` or one-shot `animation:` does NOT require the media
// query, so it must not trigger a false P0.
function reducedMotionCheck(text) {
  const hasContinuousMotion =
    /requestAnimationFrame|gsap|ScrollTrigger|@keyframes|animation-timeline\s*:/.test(text);
  const hasFallback = /prefers-reduced-motion/.test(text);
  if (hasContinuousMotion && !hasFallback) {
    return {
      id: 'no-reduced-motion',
      severity: 'P0',
      label: 'Continuous motion (rAF/gsap/@keyframes) but no prefers-reduced-motion fallback',
      fix: 'animate',
      hits: [{ line: 0, text: 'no @media (prefers-reduced-motion)' }],
    };
  }
  return null;
}

// Eyebrow density: count tiny-uppercase-tracked labels vs sections.
function eyebrowCheck(text) {
  const eyebrows = (text.match(/letter-spacing\s*:\s*0?\.[12]\d*em/gi) || []).length;
  const uppercases = (text.match(/text-transform\s*:\s*uppercase/gi) || []).length;
  const sections = (text.match(/<section\b/gi) || []).length || 1;
  const eyebrowish = Math.min(eyebrows, uppercases);
  if (eyebrowish > Math.ceil(sections / 3) && eyebrowish >= 3) {
    return {
      id: 'eyebrow-overuse',
      severity: 'P1',
      label: `Likely eyebrow on most sections (~${eyebrowish} vs ${sections} sections)`,
      fix: 'typeset',
      hits: [{ line: 0, text: `${eyebrowish} uppercase+tracked labels` }],
    };
  }
  return null;
}

// ---- run -------------------------------------------------------------------

const report = [];
let p0Count = 0;

for (const file of files) {
  let text;
  try {
    text = readFileSync(file, 'utf8');
  } catch (e) {
    report.push({ file, error: String(e.message || e), findings: [] });
    continue;
  }

  const findings = [];
  for (const rule of [...RULES, ...MOTION_RULES]) {
    const hits = rule.find(text);
    if (hits.length) {
      findings.push({ id: rule.id, severity: rule.severity, label: rule.label, fix: rule.fix, count: hits.length, hits: hits.slice(0, 8) });
    }
  }
  // Impeccable-ported static rules (Apache-2.0 derived, see the section above).
  for (const [id, find] of Object.entries(IMPECCABLE_STATIC_CHECKS)) {
    const hits = find(text).map((h) => ({ line: lineOf(text, h.index), text: h.snippet }));
    if (hits.length) {
      findings.push({
        id,
        severity: id === 'side-tab' ? 'P1' : 'P2',
        label: (IMPECCABLE_RULES.find((r) => r.id === id) || {}).name || id,
        fix: 'redesign / audit',
        count: hits.length,
        hits: hits.slice(0, 8),
      });
    }
  }
  for (const fn of [spectacleCheck, reducedMotionCheck, eyebrowCheck]) {
    const f = fn(text);
    if (f) findings.push({ ...f, count: f.hits.length });
  }

  findings.sort((a, b) => severityRank(a.severity) - severityRank(b.severity));
  p0Count += findings.filter((f) => f.severity === 'P0').length;
  report.push({ file, findings });
}

function severityRank(s) {
  return { P0: 0, P1: 1, P2: 2 }[s] ?? 3;
}

// The full not-covered list: the by-eye items plus the impeccable rules that
// need a DOM / live browser (IMPECCABLE_RULES with port:'runtime').
function allNotCovered() {
  return [
    ...NOT_COVERED,
    ...IMPECCABLE_RUNTIME.map((r) => `[impeccable·runtime] ${r.name}${r.note ? ` — ${r.note}` : ''}`),
  ];
}

// ---- output ----------------------------------------------------------------

if (asJson) {
  console.log(JSON.stringify({ p0: p0Count, files: report, notCovered: allNotCovered() }, null, 2));
} else {
  for (const { file, findings, error } of report) {
    const name = basename(file);
    if (error) {
      console.log(`\n✗ ${name} — read error: ${error}`);
      continue;
    }
    if (!findings.length) {
      console.log(`\n✓ ${name} — no regex-detectable slop (visual audit still required)`);
      continue;
    }
    console.log(`\n● ${name} — ${findings.length} finding(s)`);
    for (const f of findings) {
      const where = f.hits.map((h) => (h.line ? `L${h.line}` : '')).filter(Boolean).join(', ');
      console.log(`  [${f.severity}] ${f.label}${f.count > 1 ? ` ×${f.count}` : ''}${where ? `  (${where})` : ''}`);
      console.log(`        → fix with \`${f.fix}\``);
    }
  }
  console.log(`\n${p0Count ? `✗ ${p0Count} P0 finding(s) — ships broken` : '✓ no P0 findings'}`);
  console.log(`\nRegex layer only — still needs a human/Playwright pass for:`);
  for (const c of allNotCovered()) console.log(`  · ${c}`);
}

// See the exit-code note at the top: default is always 0 so the agent never reads
// a finding as a tool malfunction. Only --strict turns a P0 into a blocking exit.
process.exit(strict && p0Count ? 1 : 0);
