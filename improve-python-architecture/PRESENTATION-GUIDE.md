# Presentation Guide

The architectural review renders as a self-contained HTML file in the OS temp directory, named `python-arch-review-<timestamp>.html`. Tailwind and Mermaid come from CDNs — no build step.

## Required Sections

Every candidate card (one `<article>` element) has exactly these sections:

| # | Section | Content |
|---|---------|---------|
| 1 | **Files** | Affected packages and modules, `font-mono text-sm` list |
| 2 | **Problem** | One sentence: the current friction |
| 3 | **Solution** | One sentence: what changes |
| 4 | **Benefits** | Bullets (≤6 words each) in architecture vocabulary — _protocol shrinks_, _locality restored_, _seam justified_ |
| 5 | **Python Analysis** | Friction signals found; import graph; Protocol/ABC usage; `__all__` state |
| 6 | **Before / After** | Side-by-side visual diagram |
| 7 | **Badge** | `Strong` / `Worth exploring` / `Speculative` |

## Diagram Patterns

Use Mermaid `flowchart` for dependency and call-flow changes. Use hand-built `<div>` + inline SVG for editorial visuals — mass diagrams, cross-sections, collapse animations. Mix them.

### Before — module is a pass-through

```html
<div class="rounded border border-slate-200 bg-white p-4">
  <pre class="mermaid">
    flowchart LR
      A[client] --> B[package.__init__]
      B --> C[parser]
      B --> D[formatter]
      B --> E[sender]
      classDef shallow stroke:#d97706,stroke-width:2px;
      class B shallow
  </pre>
</div>
```

### After — module is deep

```html
<div class="rounded border border-slate-200 bg-white p-4">
  <pre class="mermaid">
    flowchart LR
      A[client] --> B[package.report]
      subgraph internal
        C[parser] --> D[formatter]
      end
      B --> internal
      classDef deep fill:#0f172a,stroke:#0ea5e9,color:#fff;
      class B deep
  </pre>
</div>
```

### Cross-section — before/after depth comparison

Use horizontal bands (`h-12 border-l-4`) to show layers a call passes through. Before: six thin bands, each doing nothing. After: one thick band, labelled with the consolidated responsibility.

### Mass diagram — protocol surface vs implementation

Two rectangles per module — interface surface area vs implementation. Before: rectangles nearly equal height (shallow). After: interface rectangle short, implementation rectangle tall (deep).

## Scaffold

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <title>Python Architecture Review — {{repo_name}}</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script type="module">
    import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";
    mermaid.initialize({ startOnLoad: true, theme: "neutral", securityLevel: "loose" });
  </script>
  <style>
    .seam { stroke-dasharray: 4 4; }
    .leak { stroke: #dc2626; }
  </style>
</head>
<body class="bg-stone-50 text-slate-900 font-sans">
  <main class="max-w-5xl mx-auto px-6 py-12 space-y-12">
    <header><!-- repo name, date, legend --></header>
    <section id="candidates" class="space-y-10"><!-- one article per candidate --></section>
    <section id="top-recommendation"><!-- which to tackle first and why --></section>
  </main>
</body>
</html>
```

## Style

- Lean editorial. Generous whitespace. Serif optional for headings (`font-serif` with stone/slate).
- Colour sparingly: one accent (indigo or emerald) + red for leakage + amber for warnings.
- Keep diagrams ~320px tall for comfortable side-by-side view.
- Module labels: `text-xs uppercase tracking-wider`.
- The only scripts: Tailwind CDN + Mermaid ESM import. No app code, no interactivity beyond Mermaid rendering.

## Top Recommendation Section

One larger card. Candidate name, one sentence on why, anchor link to its card.
