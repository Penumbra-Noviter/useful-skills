# Stack & Architecture Defaults — SKILL.md §3

The default implementation layer for finesse builds. **Load before writing components — the hard rules below are mandatory.** Unless the Design Read picks a real design system (SKILL.md §2.A) or the build target is a non-React stack (vanilla HTML, Vue, Svelte — adjust accordingly).

## 1. Stack
- **Framework:** React or Next.js. Default to Server Components (RSC).
  - **RSC SAFETY:** Global state works ONLY in Client Components. In Next.js, wrap providers in a `"use client"` component.
  - **INTERACTIVITY ISOLATION:** Any component using Motion, scroll listeners, or pointer physics MUST be an isolated leaf with `'use client'` at the top. Server Components render static layouts only.
- **Styling:** **Tailwind v4** (default). Tailwind v3 only if the existing project demands it.
  - For v4: do NOT use the `tailwindcss` plugin in `postcss.config.js`. Use `@tailwindcss/postcss` or the Vite plugin.
- **Animation:** **Motion** (the library formerly known as Framer Motion). Import from `motion/react` (`import { motion } from "motion/react"`). The `framer-motion` package still works as a legacy alias — prefer `motion/react` in new code.
- **Fonts:** Always use `next/font` (Next.js) or self-host with `@font-face` + `font-display: swap`. Never link Google Fonts via `<link>` in production.

## 2. State
- Local `useState` / `useReducer` for isolated UI.
- Global state ONLY for deep prop-drilling avoidance — Zustand, Jotai, or React context.
- **[HARD RULE] NEVER use `useState` to track continuous values driven by user input** (mouse position, scroll progress, pointer physics, magnetic hover). Use Motion's `useMotionValue` / `useTransform` / `useScroll`. `useState` re-renders the React tree on every change and collapses on mobile.

## 3. Icons
- **Allowed libraries (priority order):** `@phosphor-icons/react`, `hugeicons-react`, `@radix-ui/react-icons`, `@tabler/icons-react`.
- **Discouraged:** `lucide-react`. Acceptable only when the user explicitly asks for it or the project already depends on it.
- **[HARD RULE] NEVER hand-roll SVG icons.** If a glyph is missing, install a second library or compose from primitives — do not draw icon paths from scratch.
- **One family per project.** Do not mix Phosphor with Lucide in the same component tree.
- **Standardize `strokeWidth` globally** (e.g. `1.5` or `2.0`).

## 4. Emoji Policy
Discouraged by default in code, markup, and visible text. Replace symbols with icon-library glyphs. **Override:** allow emojis only when the user explicitly asks for a playful / chat-style / social-native vibe — and even then use them sparingly with intent.

## 5. Responsiveness & Layout Mechanics
- Standardize breakpoints (`sm 640`, `md 768`, `lg 1024`, `xl 1280`, `2xl 1536`).
- Contain page layouts using `max-w-[1400px] mx-auto` or `max-w-7xl`.
- **[HARD RULE] Viewport Stability:** NEVER use `h-screen` for full-height Hero sections. ALWAYS use `min-h-[100dvh]` to prevent layout jumping on mobile (iOS Safari address bar).
- **[HARD RULE] Grid over Flex-Math:** NEVER use complex flexbox percentage math (`w-[calc(33%-1rem)]`). ALWAYS use CSS Grid (`grid grid-cols-1 md:grid-cols-3 gap-6`).

## 6. Dependency Verification
**[HARD RULE]** Before importing ANY 3rd-party library, check `package.json`. If the package is missing, output the install command first. **Never** assume a library exists.
