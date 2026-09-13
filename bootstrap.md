# Bootstrap — New WordPress + Kadence Project

Use when starting HTML→Kadence conversion in a project that has no overlay yet.

## Prerequisites

- WordPress with Kadence theme + Kadence Blocks (Pro optional)
- Child theme recommended for custom CSS/PHP
- REST API access (application password)
- At least one **reference page** built correctly in Kadence (usually Home)

## Step 1 — Copy framework into project

From any machine with this skill installed:

```bash
# Run from WordPress project root
bash ~/.cursor/skills/html-to-kadence/scripts/init-project.sh
```

Or manually copy:

```
~/.cursor/skills/html-to-kadence/template/
  → <project>/.cursor/
```

## Step 2 — Create project overlay

```bash
cp ~/.cursor/skills/html-to-kadence/project-config.template.yaml \
   .cursor/html-to-kadence/project.yaml
```

Edit `project.yaml` — fill every `REQUIRED` field.

## Step 3 — Discover live design system

1. Fetch reference page: `GET /wp/v2/pages/{clone_source_page_id}?context=edit`
2. Extract palette slugs, fonts, button patterns from live markup
3. Document in `docs/kadence-html-mapping.md` (project root)
4. Add first **learning** to `project.yaml` → `learnings:` if you discover a rule

## Step 4 — Wire Cursor

Add to project `.cursor/rules/project.mdc` (or equivalent):

```markdown
## HTML → Kadence

For HTML conversion, use skill `html-to-kadence` and read:
1. `.cursor/html-to-kadence/project.yaml`
2. `.cursor/workflows/html-to-kadence-pipeline.md`
3. `docs/kadence-html-mapping.md`
```

## Step 5 — Verify

Convert a small HTML snippet (one hero section). Check:

- [ ] Blocks render on staging
- [ ] Gutenberg editor shows no "invalid block" errors
- [ ] Tokens match live design system (not raw HTML hex)

## Credentials

Store in `.credentials/wordpress-api.env` (gitignored):

```env
WP_BASE_URL=https://staging.example.com
WP_USER=api-user
WP_APP_PASSWORD=xxxx xxxx xxxx xxxx
```

Never commit credentials.

## Optional — Kadence AI Validator plugin

```bash
bash scripts/install-validator-plugin.sh /path/to/wp-content/plugins
# WP Admin → Plugins → Activate Kadence AI Validator
```

Document in `project.yaml`:

```yaml
rest:
  validate_endpoint: /kadence-ai/v1/validate
```

API: [docs/kadence-ai-validate-endpoint.md](docs/kadence-ai-validate-endpoint.md)
