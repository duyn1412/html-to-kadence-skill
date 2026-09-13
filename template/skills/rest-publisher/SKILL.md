# Skill: REST Publisher

**Tier:** Core | **Steps:** 7 (read), 17 (write)

## Purpose

Read/write WordPress via REST API.

## Read (always)

- Pages `context=edit`, elements, media, settings
- Credentials: `project.yaml` → `rest.credentials_file`

## Write (opt-in only)

- User must explicitly request publish
- Default status: `project.yaml` → `conversion.default_publish_status`
- **GET current content first** — detect manual edits before PUT
- Validate via `rest.validate_endpoint` if configured

## Output

Publish Report with endpoint, status, URL, timestamp.

## Rules

- Never hardcode credentials
- Never delete without confirmation
- Abort publish if validate returns `success: false`
