# Domain Integration — Ingesting a Design Repo / Corpus into finesse

For when the user drops a design repository or corpus (a shipped admin, a component library, a themed page collection) and asks to integrate it into finesse — or when adding the next specialized domain. Read this **before touching the skill's structure**. The protocol's job: take in the repo's value while the skill's structure (SKILL.md router, references table, examples index, version discipline) stays exactly as it is — the slots stay, only the entries change.

---

## 0. The one rule

The skill is a **rules corpus + a lift corpus**. A repo enters it as:

- **distilled rules** → `references/*.md` (patterns, measured in paragraphs, not files), and/or
- **lift material** → `examples/EXAMPLES.md` entries (pointers + "what to study" lists, not copies).

**Never as itself.** The repo's files stay outside the skill directory; the skill records the canonical path. Volume discipline: a 12k-line repo's whole integration ≈ 100 lines of rules + 1 index entry. If the distilled product approaches the source's volume, the distillation has failed.

---

## 1. Classify — the gate

| Repo's nature | Where it lands |
|---|---|
| **New register** — passes the zine test: its own substrate (what the page is made of), its own trigger vocabulary, its own pre-flight, its own output contract | **Standalone skill** — extraction with an *inheritance declaration* ("inherits craft floor + blacklist + a11y gates"), never a copy of them; SKILL.md §11 shows the stub pattern |
| **Large implementation corpus inside an existing register** (>2k lines / multi-file / a component system) | **Distill rules into references + path-referenced corpus entry** in EXAMPLES.md (the `shadcn-admin` case: `admin-console.md` + the component-system corpus section) |
| **Small pattern set** (a few hundred lines, one page's worth) | Patch the relevant reference directly |
| **Cross-cutting layer** (motion / 3D / palettes) | Patch `motion.md` / `3d-effects.md` / `product-palettes.md` |
| **Pure routing note** — says nothing the register map doesn't already know | **Don't integrate.** Reject explicitly with the reason |

The zine test decides skill vs corpus: *does this domain have its own substrate, triggers, pre-flight, and output contract?* A dashboard template answers no on all four — it implements the product register, so it's material, not a domain. 纸刊 answers yes on all four — it's a register, so it got a register's home.

---

## 1.5 The Overlap Gate — is this already covered?

The classify gate answers *what kind of thing* the repo is. A second gate answers *do we already have it* — before any distillation, so effort isn't spent rediscovering rules that exist. **The skill already carries a coverage registry; the gate is how you read it without reading everything:**

1. **SKILL.md references table** — the "When to load" column is one line of coverage declaration per reference. Match the repo's domain keywords and page-morphology words against it.
2. **EXAMPLES.md index + "Not in corpus"** — the lift-corpus registry: which morphologies have shipped examples, and which are declared absent.
3. **The target reference's header** — its `Covers / Adjacent / Does-not-cover` declaration (new references carry one; older ones may not — read the first 10 lines instead).

**Three signals, measured against these sources:**

- **Route hit** — how many of the repo's trigger words / page-job words (read / manage / commit, shell types) hit existing "When to load" descriptions.
- **Morphology hit** — does the repo's page morphology (or its role in one) already have a home reference?
- **Distill-draft overlap** — sketch the distilled rule list first, then count how many items already exist in the target reference.

**The four verdicts:**

| Overlap | Signal | Verdict |
|---|---|---|
| **High** — same direction, same morphology, draft items >~80% already present | route hits almost all | **Reject** with the reason, or take only the diff items as a patch — never a parallel reference that says the same thing |
| **Medium** — same direction, different morphology / depth | partial hits | **Merge** — write only the diff; if the existing reference is already full, open a new reference (the `admin-console.md` pattern) |
| **Low** — fills a real gap | no hits | Full distill → wire pipeline |
| **Corpus-level overlap** — the lift corpus already has the same kind of material | index match | **Add a what-to-study index entry**, don't add files |

Rejection is a first-class outcome. A repo that duplicates `product-ui.md` §2's table rules adds a second authority for the same rule — which is how drift starts. Saying "already covered, here's what it adds" is a complete, correct integration.

---

## 2. Locate

*Runs for repos the overlap gate (§1.5) accepted — a rejection skips this.*

1. **Map the repo to the register** — SKILL.md §0.A's register → reference map. Which register does it serve (brand / product / zine / commerce)? Read, manage, or operate?
2. **Name the gap** — the integration is justified by what the repo adds, not by its existence. If the overlap gate already measured the draft at 90% overlap, the distilled output is the remaining 10% and the corpus entry may be the whole value.
3. **Record the repo facts** — source, license (MIT keeps attribution; non-commercial gets its own note like the zine chapter), stack, volume, key file paths, version. The EXAMPLES.md entry needs these.

---

## 3. Distill — the handoff core

- **Draft the rule list first** — it is the overlap gate's third signal (§1.5); the accepted draft is then the distillation's skeleton.
- **Rules as paragraphs** — into references goes the *pattern* ("a faceted filter shows each option's live count"), not the *implementation* ("`getFacetedUniqueValues()`"). The reference layer must outlive the repo's library choices.
- **Library choices don't inherit** — components, icon families, animation libs re-route through `stack-defaults.md` (e.g. the corpus ships lucide; the rule layer says "follow the icon family lock"). A distilled reference that hardcodes the source's stack is a fork, not a distillation.
- **Blacklist filter** — the repo's own slop is not inherited. Run the distilled rules through `anti-cheap.md` and cut (fake metrics, default-category palette, banned fonts) before they land. Say what was cut in the entry.
- **Lift material as pointers** — large repos stay in place; EXAMPLES.md records the canonical path + a per-file "what to study" table. A repo of 272 files becomes one table row.
- **License line** — every new reference / corpus entry states source + attribution duty ("MIT © Sat Naing — keep attribution when copying code").

---

## 4. Wire — fill the existing slots, never add new structure

1. **SKILL.md references table**: +1 row — the reference's name + "when to load" in the table's existing voice. (admin-console.md → "data-grid-heavy consoles… load on top of `workflow-ui.md`"; domain-integration.md → "a design repo is dropped in and the user asks to integrate it".)
2. **EXAMPLES.md**: +1 entry / section, with the what-to-study table.
3. **Routing prose**: the one sentence in SKILL.md §0.A (and/or the How-to-use step) that the new material extends — a clause, not a paragraph.
4. **Cross-references**: a one-line pointer in the reference the new file stacks on (`workflow-ui.md` pointing at `admin-console.md`), matching how `chart-crafting.md` points at `dataviz.md`.
5. **Version + sync**: bump SKILL.md `version:` (0.16.0 → 0.17.0 → …), and sync **every deployed copy** (the `.zcode/skills/finesse-ui` deployment) — the copies are byte-identical today; keep them that way. The repo is the single source; deployment is a copy, never an edit target.

---

## 5. Guard

- **Consistency**: the new rules contradict nothing in `anti-cheap.md`, `dials.md`, or the color lock.
- **Lazy-load discipline**: a new reference loads only when routed to — it must not be required reading for pages that don't need it.
- **Coverage declarations**: every new reference carries a `Covers / Adjacent / Does-not-cover` header block (see `admin-console.md`), consistent with its references-table row — so the next overlap gate reads declarations, not full files. Older references may lack one; read their first 10 lines instead. Don't mass-backfill.
- **Corpus slop statement**: vendored corpus entries are `detect.mjs`-clean; path-referenced ones state "not scanned, no slop-cleanliness promise".
- **Structural audit**: references table rows ↔ `references/` files 1:1; cross-reference paths resolve; version matches across copies.

---

## 6. The two handoff directions

- **Write side (repo → skill)** — steps 1–5 above. The handoff artifact is rules paragraphs + an index entry; the repo's volume never enters the skill. Efficient handoff = the entry tells the reader exactly where the value is, so nobody re-reads 12k lines to find the three patterns.
- **Read side (skill → build)** — the EXAMPLES.md what-to-study table is the handoff device: "open these files, study these patterns, lift these ideas, vendor nothing, attribute this". A brief that routes to the new material reads the distilled reference first, then the corpus entry, then the repo — in that order, and only as far as the entry points.
