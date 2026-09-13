# Kadence AI Validator (WordPress Plugin)

Server-side validation for the HTML→Kadence pipeline. Runs on **WordPress**, not in the agent.

## What it does

- `POST /wp-json/kadence-ai/v1/validate` — validate block markup before publish
- `GET /wp-json/kadence-ai/v1/validate` — health check

Checks: `parse_blocks()`, block.json schema, Kadence rules (`uniqueID`, fontSize, overlay, inner HTML), `do_blocks()` render.

## Install

From this skill repo (or a clone):

```bash
# Auto-detect wp-content/plugins under cwd, or pass path:
bash scripts/install-validator-plugin.sh /path/to/wp-content/plugins
```

Or copy manually:

```bash
cp -R wordpress-plugin/kadence-ai-validator /path/to/wp-content/plugins/
```

Then **WP Admin → Plugins → Kadence AI Validator → Activate**.

## Configure pipeline

In `.cursor/html-to-kadence/project.yaml`:

```yaml
rest:
  validate_endpoint: /kadence-ai/v1/validate
```

Example call:

```python
api("POST", "/kadence-ai/v1/validate", {"content": markup, "strict": False})
```

**Gate:** `success: true` required before REST publish.

## Auth

- Application password (same as other REST calls)
- Capability: `edit_posts`
- Full browser User-Agent if host uses Cloudflare (WP Engine)

## Full API reference

See [docs/kadence-ai-validate-endpoint.md](../../docs/kadence-ai-validate-endpoint.md)

## Extend rules

Edit `includes/class-kadence-rules.php` for project-specific checks.
