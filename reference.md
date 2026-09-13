# HTML → Kadence — Reference

Generic pipeline, block mapping, and validation rules. Project-specific values
come from `.cursor/html-to-kadence/project.yaml`.

---

## Pipeline (17 steps)

### Phase 1 — Context (1–7)

| Step | Action | Output |
|------|--------|--------|
| 1–4 | Read Kadence theme, blocks, pro, child theme | Stack versions |
| 5 | Read `theme.json` + Customizer palette | Token slugs |
| 6 | Read project rules | Conventions |
| 7 | REST read: pages, elements, media | Live snapshot |

### Phase 2 — Design intelligence (8–10)

| Step | Action | Output |
|------|--------|--------|
| 8 | Extract design system from live site | Design System Manifest |
| 9 | Analyze HTML | HTML Analysis Document |
| 10 | Match reusable patterns | Reuse Report |

### Phase 3 — Composition (11–12)

| Step | Action | Output |
|------|--------|--------|
| 11 | Map components → blocks | Mapping table |
| 12 | Generate Gutenberg markup | Block Markup |
| 12b | Server validate (if endpoint exists) | Validation JSON |

### Phase 4 — QA (13–16)

Responsive, accessibility, SEO, performance — QA Reviewer hub merges reports.

### Phase 5 — Publish (17)

**Only if user explicitly requests.** Default: deliver markup only.

---

## Block hierarchy

```
<section>  →  kadence/rowlayout  (align: full)
  <div>      →  kadence/column
    content  →  leaf block
```

## Core mapping

| HTML | Kadence block | Notes |
|------|---------------|-------|
| `<section>` | `rowlayout` | `align: full`, `bgColor`, `anchor` |
| layout `<div>` | `column` | child of row only |
| `<h1>`–`<h6>` | `advancedheading` | `level`, display font from project.yaml |
| `<p>` | `advancedheading` | `htmlTag: "p"`, body font |
| `<img>` | `image` or `advancedgallery` | real media `id` + URL |
| `<button>` / `.btn` | `advancedbtn` | clone from reference page |
| `<form>` | `advanced-form` (CPT) or embed | avoid Custom HTML |
| FAQ / accordion | `accordion` | `faqSchema: true` when appropriate |
| `<hr>` | `spacer` | `dividerEnable: true` |

Full site mapping: `docs/kadence-html-mapping.md` (per project).

---

## Composition rules (generic)

1. **Clone reference markup** — fetch `clone_source_page_id` from project.yaml
2. **Regenerate uniqueIDs** — `{targetPageId}_{8hex}`; match CSS classes + `data-kb-block`
3. **Replace only** — text, media IDs/URLs, uniqueIDs; keep structure
4. **Palette tokens** — use `paletteN` + `colorClass: theme-paletteN` together
5. **fontSize** — numeric px arrays `[40,"",28]` — not preset strings like `"4xl"`
6. **Row overlay** — hex in `overlay` attribute when needed
7. **Multi-column rows** — include `"columns": 2` (or 3)
8. **No nested rowlayout** inside columns
9. **Advanced Heading** — inner HTML must match `save()` output (class + data-kb-block)
10. **Zero Custom HTML** unless no Kadence equivalent and exception documented

---

## Validation checklist (pre-publish)

- [ ] Cloned from live reference page, not invented from docs alone
- [ ] All `uniqueID` values use target page prefix consistently
- [ ] `kt-adv-heading{uniqueID}` + `data-kb-block="kb-adv-heading{uniqueID}"` present
- [ ] Palette colors: both `color` and `colorClass` + matching HTML classes
- [ ] Real media IDs (no `REPLACE_*` placeholders)
- [ ] `markBorderStyles` boilerplate on headings (copy from reference)
- [ ] Row defaults: `kbVersion: 2`, column width attrs from reference
- [ ] REST validate endpoint returns `success: true` (if available)
- [ ] Gutenberg editor: no "invalid block" warnings

---

## Agent artifacts (contracts)

| Agent | Output document |
|-------|-----------------|
| Kadence Architect | Stack Context Brief |
| Design System Extractor | Design System Manifest |
| HTML Analyzer | HTML Analysis Document (JSON) |
| Pattern Finder | Reuse Report |
| Block Composer | Block Markup + Mapping Table |
| QA Reviewer | QA Sign-off |
| REST Publisher | Publish Report |

Pass documents sequentially; QA hub may request re-patch from Composer.

---

## HTML Analysis Document (schema)

```json
{
  "sections": [{
    "index": 1,
    "tag": "section",
    "pattern_hint": "hero|two-column|faq|cta|form",
    "children": [{"tag": "h1", "level": 1, "text": "..."}],
    "token_hints": {"bg": "palette2"}
  }],
  "heading_outline": ["h1: Title"],
  "forms": [],
  "warnings": []
}
```

---

## REST patterns

```bash
# Read page for cloning
GET /wp/v2/pages/{id}?context=edit

# Publish (opt-in)
PUT /wp/v2/pages/{id}
Body: { "content": "<!-- wp:kadence/...", "status": "draft" }

# Validate (if custom endpoint)
POST /kadence-ai/v1/validate
Body: { "content": "..." }
```

Credentials: `.credentials/wordpress-api.env` — never commit.
