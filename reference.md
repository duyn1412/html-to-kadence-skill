# HTML → Kadence — Reference (v1.1.0)

Generic pipeline, block mapping, and validation rules. Project-specific values
come from `.html-to-kadence/project.yaml` (or `.cursor/html-to-kadence/project.yaml`).

---

## Pipeline (17 steps)

### Phase 1 — Context (1–7)

| Step | Action | Output |
|------|--------|--------|
| 1–4 | Read Kadence theme, blocks, pro, child theme | Stack versions |
| 5 | Read `theme.json` + Customizer palette | Token slugs |
| 6 | Read project rules & configuration | Conventions |
| 7 | REST read: pages, elements, media | Live snapshot |

### Phase 2 — Design intelligence (8–10)

| Step | Action | Output |
|------|--------|--------|
| 8 | Extract design system from live site | Design System Manifest |
| 9 | Analyze HTML & derive content manifest | HTML Analysis Document |
| 10 | Match reusable patterns | Reuse Report |

### Phase 3 — Composition (11–12)

| Step | Action | Output |
|------|--------|--------|
| 11 | Map components → blocks | Mapping table |
| 12 | Generate Gutenberg markup | Block Markup |
| 12b | Server validate (if endpoint exists) | Validation JSON |

### Phase 4 — Quality Assurance & Gating (13–16)

The QA Engine runs a 9-stage evaluation with mandatory hard gating:
- **Structural QA**: Comment balance, JSON syntax, Kadence attributes, zero Custom HTML, unique IDs, zero placeholders.
- **Content Preservation QA**: 100% headings, 100% CTAs, 100% links, 100% images, $\ge 98\%$ text tokens.
- **Accessibility QA**: Single H1, proper heading order, image alt text, accessible links.
- **WordPress Runtime QA**: Round-trip serialization invariance (`PUT` -> `GET raw`).
- **Visual QA**: Desktop (1440px), Tablet (768px), Mobile (390px) responsive fidelity.
- **Auto-repair loop**: If gates fail, isolate defect to smallest block scope, apply patch, and re-run QA (max 3 rounds).

Detailed documentation: **[docs/qa-pipeline.md](docs/qa-pipeline.md)**

### Phase 5 — Safe Publish (17)

**Only if user explicitly requests.** Default: deliver markup only.
- Optimistic concurrency: verify live `sha256` hash before write. Abort on `LIVE_CONTENT_CHANGED_ABORTED`.
- Save local backup snapshot to `.backups/pages/`.
- Default status: `draft`.

Detailed documentation: **[docs/wordpress-safety.md](docs/wordpress-safety.md)**

---

## Block hierarchy

```
<section>  →  kadence/rowlayout  (align: full)
  <div>      →  kadence/column
    content  →  leaf block
```

## Core mapping

| HTML | Kadence block | UI Name | Notes |
|------|---------------|---------|-------|
| `<section>` | `rowlayout` | Row Layout | `align: full`, `bgColor`, `anchor` |
| layout `<div>` | `column` | Section / Column | child of row only |
| `<h1>`–`<h6>` | `advancedheading` | Text (Adv) | `level`, display font from project.yaml |
| `<p>` | `advancedheading` | Text (Adv) | `htmlTag: "p"`, body font |
| `<img>` | `image` | Advanced Image | real media `id` + URL |
| `<button>` / `.btn` | `advancedbtn` + `singlebtn` | Advanced Buttons | clone from reference page |
| `<form>` | `advanced-form` | Form | avoid Custom HTML |
| FAQ / accordion | `accordion` + `pane` | Accordion | `faqSchema: true` when appropriate |
| `<hr>` | `spacer` | Spacer / Divider | `dividerEnable: true` |

Full site mapping: `docs/kadence-html-mapping.md` (per project).
Terminology mapping: `docs/kadence-compatibility.md`.

---

## Composition rules (generic)

1. **Clone reference markup** — fetch `clone_source_page_id` from project.yaml
2. **Regenerate uniqueIDs** — `{targetPageId}_{8hex}`; match CSS classes + `data-kb-block`
3. **Replace only** — text, media IDs/URLs, uniqueIDs; keep structure
4. **Palette tokens** — use `paletteN` + `colorClass: theme-paletteN` together
5. **fontSize** — numeric px arrays `[40,"",28]` — not preset strings like `"4xl"`
6. **Row overlay** — hex in `overlay` attribute when needed
7. **Multi-column rows** — include `"columns": 2` (or 3) and `colLayout`
8. **No nested rowlayout** inside columns
9. **Advanced Heading** — inner HTML must match `save()` output (`kt-adv-heading{id}` + `data-kb-block`)
10. **Zero Custom HTML** unless no Kadence equivalent and exception documented
11. **Zero Placeholders** — no `TODO`, `FIXME`, `example.com`, `lorem ipsum`, or `href="#"`

---

## Validation checklist (pre-publish)

- [ ] Run `python3 scripts/qa-engine.py <blocks_file> --html <source_html>`: Exit code 0 (PASS)
- [ ] Structural score = 100/100
- [ ] Content preservation score $\ge 98/100$
- [ ] Accessibility score $\ge 90/100$
- [ ] All `uniqueID` values strictly unique
- [ ] `kt-adv-heading{uniqueID}` + `data-kb-block="kb-adv-heading{uniqueID}"` present
- [ ] Palette colors: both `color` and `colorClass` + matching HTML classes
- [ ] Real media IDs (no `REPLACE_*` placeholders)
- [ ] REST validate endpoint returns `success: true` (if available)
- [ ] Gutenberg editor: zero "invalid block" warnings

---

## Agent artifacts (contracts)

| Agent | Output document |
|-------|-----------------|
| Kadence Architect | Stack Context Brief |
| Design System Extractor | Design System Manifest |
| HTML Analyzer | HTML Analysis Document (JSON) |
| Pattern Finder | Reuse Report |
| Block Composer | Block Markup + Mapping Table |
| QA Reviewer | Formal QA Sign-off Report |
| REST Publisher | Publish Report |

Pass documents sequentially; QA Reviewer triggers targeted re-patch if gates fail.

---

## REST patterns

```bash
# Read page for cloning / concurrency check
GET /wp/v2/pages/{id}?context=edit

# Publish (opt-in only, draft status)
PUT /wp/v2/pages/{id}
Body: { "content": "<!-- wp:kadence/...", "status": "draft" }

# Validate (if custom endpoint)
POST /kadence-ai/v1/validate
Body: { "content": "..." }
```

Credentials: `.credentials/wordpress-api.env` — never commit.
