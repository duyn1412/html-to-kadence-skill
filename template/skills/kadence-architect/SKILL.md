# Skill: Kadence Architect

**Tier:** Core | **Steps:** 1–6

## Purpose

Establish Kadence stack context before conversion.

## Workflow

1. Read `.cursor/html-to-kadence/project.yaml`
2. Verify paths: `theme.parent`, `theme.child`, `kadence-blocks*`
3. Read `theme.json`, child `functions.php`, project rules
4. Emit **Stack Context Brief**

## Output

```markdown
## Stack Context Brief
- Theme: {parent} + {child}
- Content width: {theme.content_width}
- Clone source page: {pages.clone_source}
- Fonts: {design_system.fonts}
- Validate endpoint: {rest.validate_endpoint}
```

## Rules

- Read `project.yaml` → `learnings` first
- Never assume block availability — inventory from plugins
- Document header/footer strategy (Element CPT vs in-page rows)
