# Kadence AI Validate Endpoint

Server-side block validation via **kadence-ai-validator** WordPress plugin.

## Plugin source (this skill repo)

| Item | Value |
|------|-------|
| Package path | `wordpress-plugin/kadence-ai-validator/` |
| Install script | `scripts/install-validator-plugin.sh` |
| Deploy path | `{wp_content}/plugins/kadence-ai-validator/` |
| Slug | `kadence-ai-validator` |
| Activate | WP Admin → Plugins → **Kadence AI Validator** |

## Endpoints

| Method | URL | Purpose |
|--------|-----|---------|
| `GET` | `/wp-json/kadence-ai/v1/validate` | Health check + Kadence block count |
| `POST` | `/wp-json/kadence-ai/v1/validate` | Validate block markup |

**Auth:** Application password, capability `edit_posts`

**User-Agent:** Full browser UA if host uses Cloudflare (WP Engine)

Configure in `project.yaml`:

```yaml
rest:
  validate_endpoint: /kadence-ai/v1/validate
```

## POST body

```json
{
  "content": "<!-- wp:kadence/rowlayout ...",
  "strict": false
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `content` | Yes | Raw Gutenberg block markup (`post_content`) |
| `strict` | No | If `true`, warnings become errors |

## Response (422 on failure)

```json
{
  "success": false,
  "block_count": 24,
  "errors": [
    {
      "block": "kadence/advancedheading",
      "message": "fontSize preset string \"4xl\" is invalid — use numeric px e.g. [40,\"\",28]",
      "path": "blocks[2].innerBlocks[0]",
      "attribute": "fontSize"
    }
  ],
  "warnings": [],
  "plugin_version": "1.1.0",
  "validated_at": "2026-07-03T03:00:00+00:00"
}
```

## What it checks

1. `parse_blocks()` — unrecoverable / empty blocks
2. Block registered in `WP_Block_Type_Registry`
3. Attributes vs `block.json` schema
4. Kadence rules — `uniqueID`, placeholder media, fontSize presets, overlay, inner HTML
5. `do_blocks()` render — PHP warnings/errors captured

## Pipeline integration

```
Block Composer → POST validate → QA Reviewer → REST publish (opt-in)
```

**Gate:** `success: true` before Step 17 publish. On failure, return errors to Block Composer.

## HTTP codes

| Code | Meaning |
|------|---------|
| 200 | Validation passed |
| 422 | Validation failed |
| 401 | Auth failed |
| 403 | Missing `edit_posts` |
| 404 | Plugin not active |

## Extend

Project-specific rules: edit `includes/class-kadence-rules.php` in the plugin.
Universal rules: contribute back to framework submodule + tag release.
