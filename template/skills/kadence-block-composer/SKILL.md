# Skill: Kadence Block Composer

**Tier:** Core | **Steps:** 11–12

## Purpose

Generate native Kadence block markup by cloning reference page structure.

## Inputs

- HTML Analysis Document
- Design System Manifest
- `GET /wp/v2/pages/{pages.clone_source}?context=edit`
- `docs/kadence-html-mapping.md`
- `project.yaml` → `learnings`

## Outputs

1. Block Markup (raw post_content)
2. Mapping Table
3. Clone source map

## Rules

1. **Clone, don't invent** — copy JSON + inner HTML from clone_source
2. Regenerate uniqueIDs per `conversion.unique_id_format`
3. Replace only: text, media IDs/URLs, uniqueIDs
4. Run `.cursor/docs/kadence-markup-validation.md` checklist
5. Zero Custom HTML unless `conversion.allow_custom_html: true` + documented exception

## Workflow

1. Fetch clone_source page raw content
2. Match each HTML section to closest reference row
3. Clone, regenerate IDs, replace content
4. Validate → hand off to QA
