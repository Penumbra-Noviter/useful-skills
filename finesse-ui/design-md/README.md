# design-md — Brand Lock Library

`design-md/` holds the locked design sources for `match <brand>` briefs and "make it look like X" requests — one folder per brand, each carrying its `DESIGN.md` (the locked palette / type / spacing / radius / components). When a brief names a brand here, that file **overrides** finesse's §4 soul and §5 palette picks; everything else (register, dials, engine, skeleton, blacklist, a11y, pre-flight) still runs.

**Entry point: `INDEX.md`** — the routing table (brand → folder → default register → voice). Read it before touching any brand folder; the merge contract lives in `../references/design-md.md`; the routing rules in SKILL.md's *Locked design systems* block and §0.A's brand-library paragraph.

## Provenance

- **Source:** [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md) — a curated collection of DESIGN.md analysis files extracted from real products.
- **Format:** each `DESIGN.md` follows the [Google Stitch DESIGN.md spec](https://stitch.withgoogle.com/docs/design-md/specification/) with extended sections: visual theme, color palette + roles, type hierarchy, component stylings, layout principles, depth/elevation, do's & don'ts, responsive behavior, agent prompt guide.
- **Local copy:** a snapshot subset of the upstream collection. When the upstream updates and the new brands earn their place, re-sync via `../references/domain-integration.md` (corpus-update variant — the overlap gate applies), then update this note with the sync date.

## Quality baseline (sampled 2026-08-10)

12 brands sampled (linear.app · stripe · vercel · claude · supabase · notion · apple · figma · binance · airbnb + outliers kraken / vodafone): **no low-quality locks found.** Every sample carries semantic color roles (primary/ink/canvas/surface/hairline), concrete values (radii, weights, tracking, shadow rgba), and discipline statements ("never decoratively"). Zero empty-phrase hits across the whole library. Thin files (e.g. kraken, 125 lines) are the older prose format, not truncation; few-hex files (e.g. vodafone, 6) reflect genuinely monochrome brands. **Low-quality signals to check when sampling new brands:** adjectives without hex/values · color lists without role assignments · missing major Stitch sections · description contradicting the INDEX row.

## License

The DESIGN.md files carry the upstream MIT license, provided "as is" without warranty; the tokens represent publicly visible CSS values, and no ownership of any site's visual identity is claimed. Keep this note when redistributing.
