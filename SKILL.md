---
name: html-to-kadence
description: >-
  Converts HTML mockups into native Kadence/Gutenberg block markup for WordPress.
  Orchestrates a multi-agent pipeline (architect, analyzer, composer, QA, publisher).
  Use when converting HTML to Kadence blocks, building pages from design files,
  generating wp:kadence block comments, or setting up HTML-to-Kadence workflows
  in a new WordPress project.
---

# HTML → Kadence Framework

Portable orchestrator for converting HTML into native Kadence blocks. Works in any
WordPress + Kadence project via **project overlay** (`.cursor/html-to-kadence/`).

## Quick start

1. **Check project overlay** — read `.cursor/html-to-kadence/project.yaml` if it exists
2. **If missing** — run bootstrap: see [bootstrap.md](bootstrap.md)
3. **Run pipeline** — follow [reference.md](reference.md) § Pipeline (17 steps)
4. **Deliver** — block markup + conversion report (publish only if user asks)

## Project vs framework layers

| Layer | Location | What it holds |
|-------|----------|---------------|
| **Framework** (this skill) | `~/.cursor/skills/html-to-kadence/` | Generic pipeline, Kadence rules, validation |
| **Project overlay** | `.cursor/html-to-kadence/` | Tokens, clone page IDs, fonts, learnings |
| **Project skills** | `.cursor/skills/` | Project-tuned agent skills (optional) |
| **Project docs** | `docs/kadence-html-mapping.md` | Full HTML→block mapping for this site |

**Resolution order:** project overlay → project `.cursor/` → this skill's `reference.md`.

## When user says "convert this HTML"

```
Task Progress:
- [ ] 1. Load project.yaml + Stack Context Brief
- [ ] 2. HTML Analyzer → section tree
- [ ] 3. Pattern Finder → reuse matches from clone_source_page
- [ ] 4. Block Composer → clone live markup, replace content
- [ ] 5. Validate (checklist + optional REST endpoint)
- [ ] 6. QA (responsive, a11y, SEO, performance)
- [ ] 7. Deliver markup (+ publish only if requested)
```

## Core agents (read project skills if present)

| Agent | Project skill path | Role |
|-------|-------------------|------|
| Kadence Architect | `.cursor/skills/kadence-architect/SKILL.md` | Theme, blocks, child theme |
| HTML Analyzer | `.cursor/skills/html-analyzer/SKILL.md` | Parse HTML → section tree |
| Block Composer | `.cursor/skills/kadence-block-composer/SKILL.md` | Generate block markup |
| QA Reviewer | `.cursor/skills/qa-reviewer/SKILL.md` | Quality gates |
| REST Publisher | `.cursor/skills/rest-publisher/SKILL.md` | Read/write WordPress |

If project skills missing, use defaults in [reference.md](reference.md).

## Non-negotiables (all projects)

1. **Native Kadence blocks** — no Custom HTML unless documented exception
2. **Clone, don't invent** — copy structure from `clone_source_page` in project.yaml
3. **Validate before publish** — run markup checklist; use REST validate if available
4. **Never auto-publish** — deliver markup unless user explicitly requests publish
5. **Page update safety** — `GET` current content before any `PUT` that replaces `content`

## Outputs

1. **Block Markup** — raw `post_content` with `<!-- wp:kadence/... -->`
2. **Conversion Report** — mapping table, tokens, clone sources, QA summary
3. **Publish Report** — only when user requested publish

## Extend this framework

- New project: [bootstrap.md](bootstrap.md)
- Add agents / update mappings: [extending.md](extending.md)
- Block mapping reference: [reference.md](reference.md)
- Copy project template: `scripts/init-project.sh`

## Invoke

> Convert this HTML to Kadence blocks using the html-to-kadence skill.

Or: `@.cursor/workflows/html-to-kadence-pipeline.md` (after bootstrap).
