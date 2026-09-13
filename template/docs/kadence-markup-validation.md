# Kadence Markup Validation

**Mandatory** before publish. Project learnings in `.cursor/html-to-kadence/project.yaml`
may add rules beyond this checklist.

## Workflow

1. Fetch `pages.clone_source` via REST: `GET /wp/v2/pages/{id}?context=edit`
2. Clone block structure — replace only uniqueIDs, text, media
3. Run checklist below
4. `POST` validate endpoint if configured in `project.yaml`

## uniqueID

- Format: `{pageId}_{8hex}` (from `conversion.unique_id_format`)
- CSS class + `data-kb-block` must match uniqueID

## Advanced Heading

Inner HTML must include:
- `class="kt-adv-heading{uniqueID} wp-block-kadence-advancedheading"`
- `data-kb-block="kb-adv-heading{uniqueID}"`
- Palette: `has-theme-palette-N-color has-text-color` when `colorClass` set

## Attributes

- `fontSize`: numeric px `[40,"",28]` — not `"4xl"`
- `color` + `colorClass` together for palette tokens
- Row `overlay`: hex when needed
- Multi-col: `"columns": 2` or `3`
- Copy `markBorderStyles` boilerplate from reference page

## Common failures

| Symptom | Cause |
|---------|-------|
| Unstyled frontend | Invented attributes |
| "Invalid block" in editor | Inner HTML ≠ block save() output |
| Wrong colors | Missing `colorClass` HTML classes |

Full generic rules: `~/.cursor/skills/html-to-kadence/reference.md`
