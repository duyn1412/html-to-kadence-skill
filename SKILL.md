---
name: html-to-kadence
description: >-
  Converts HTML mockups into native Kadence/Gutenberg block markup for WordPress.
  Orchestrates a 9-stage QA-gated conversion pipeline (preflight, structural, content
  preservation, a11y, runtime, responsive visual, regression, and auto-repair).
  Use when converting HTML to Kadence blocks, building pages from design files,
  generating wp:kadence block comments, or running automated QA validation.
---

# HTML → Kadence Framework (v1.1.0)

Portable orchestrator for converting HTML into native Kadence blocks with automated **Quality Assurance (QA) Gates**. Works in any WordPress + Kadence project via **project overlay** (`.html-to-kadence/` or `.cursor/html-to-kadence/`).

## Quick start

1. **Check project overlay** — read `.html-to-kadence/project.yaml` (or `.cursor/html-to-kadence/project.yaml`)
2. **If missing** — run bootstrap: see [bootstrap.md](bootstrap.md)
3. **Run pipeline** — follow [reference.md](reference.md) § Pipeline with automated QA gating
4. **Deliver** — block markup + QA Sign-off Report (publish only if user explicitly requests)

## Project vs Framework Layers

| Layer | Location | What it holds |
|---|---|---|
| **Framework** (this skill) | skill folder | Generic pipeline, Kadence rules, QA Engine |
| **Project overlay** (primary) | `.html-to-kadence/` | Tokens, clone page IDs, fonts, QA settings, learnings |
| **Project overlay** (legacy) | `.cursor/html-to-kadence/` | Backward-compatible Cursor configuration location |
| **Project skills** | `.cursor/skills/` or `skills/` | Project-tuned agent skills (optional) |
| **Project docs** | `docs/kadence-html-mapping.md` | Full HTML→block mapping for this site |

**Configuration Resolution Order:**
1. `--config <path>` (explicit CLI flag)
2. `.html-to-kadence/project.yaml` (primary canonical location)
3. `.cursor/html-to-kadence/project.yaml` (legacy Cursor fallback)
4. Built-in defaults

## Operational Modes

- **analyze-only**: Inspect source HTML mockup, extract content manifest, generate section tree. No blocks generated, no WP calls.
- **offline-compose**: Generate Kadence blocks using conservative known patterns without live WP connection. Run structural & content QA.
- **clone-assisted**: Fetch live patterns from `clone_source` page on WordPress, clone structure, populate content, run full QA.
- **publish**: Complete all mandatory QA gates (Structural 100, Content $\ge 98$), run optimistic concurrency verification, update WordPress via REST API, verify round-trip serialization.

## When User Says "Convert This HTML"

```
Task Progress:
- [ ] 1. Load project.yaml (precedence: .html-to-kadence/ -> .cursor/ -> default)
- [ ] 2. Preflight QA: Parse source HTML into content manifest (headings, CTAs, links, text)
- [ ] 3. Pattern Finder: Match section layouts from clone_source reference page
- [ ] 4. Block Composer: Compose native Kadence block markup (zero placeholders)
- [ ] 5. Automated QA Engine: Run `python3 scripts/qa-engine.py` (Stage 2-4 validation)
- [ ] 6. Repair Loop: If QA fails, diagnose root cause and repair smallest affected scope (max 3 rounds)
- [ ] 7. WordPress Runtime & Safety (if publishing): Check concurrency hash, round-trip serialization
- [ ] 8. Deliver: Block markup + Formal QA Sign-off Report (+ publish only if requested)
```

## Non-Negotiables (All Projects)

1. **QA IS A GATE, NOT A REPORT**: Never deliver or publish markup that fails mandatory QA gates.
2. **Native Kadence Blocks Only**: Never dump raw or custom HTML into `core/html` blocks.
3. **Zero Placeholder Content**: Zero tolerance for `TODO`, `FIXME`, `example.com`, `lorem ipsum`, `{{...}}`, or `href="#"`.
4. **Mandatory Automated QA**: Run `python3 scripts/qa-engine.py` requiring Structural = 100, Content $\ge 98$.
5. **Targeted Auto-Repair**: Fix only the smallest affected scope when QA fails; never regenerate the whole page blindly.
6. **Never Auto-Publish**: Deliver block markup and QA report unless user explicitly commands publish.
7. **Optimistic Concurrency**: Always `GET` live content first. Abort with `LIVE_CONTENT_CHANGED_ABORTED` on conflict.

## Documentation Index (Progressive Disclosure)

- **[docs/qa-pipeline.md](docs/qa-pipeline.md)**: Detailed 9 QA stages, scoring formulas, hard gates, and error code directory.
- **[docs/wordpress-safety.md](docs/wordpress-safety.md)**: Concurrency control, local backups, round-trip validation, and rollback.
- **[docs/kadence-compatibility.md](docs/kadence-compatibility.md)**: Block slugs vs editor UI terminology, compatibility matrix.
- **[reference.md](reference.md)**: Detailed step-by-step conversion pipeline and HTML-to-block mapping guide.
- **[bootstrap.md](bootstrap.md)**: Bootstrapping new WordPress projects.

## Outputs

1. **Block Markup**: Clean `post_content` string with `<!-- wp:kadence/... -->` blocks.
2. **QA Sign-off Report**: Machine-readable and human-readable score table across Structural, Content, A11y, and Runtime.
3. **Publish Report**: Only generated when user explicitly requested publishing to WordPress.
