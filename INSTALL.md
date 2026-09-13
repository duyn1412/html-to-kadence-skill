# Install — HTML → Kadence Skill

Portable skill for any agent that can read markdown skill files
(Cursor, Antigravity, Claude Code, Codex, Windsurf, etc.).

## Cursor

### Personal skill (all projects)

```bash
git clone https://github.com/duyn1412/html-to-kadence-skill.git \
  ~/.cursor/skills/html-to-kadence
```

Or symlink:

```bash
git clone https://github.com/duyn1412/html-to-kadence-skill.git ~/src/html-to-kadence-skill
ln -s ~/src/html-to-kadence-skill ~/.cursor/skills/html-to-kadence
```

Cursor discovers `SKILL.md` automatically. Invoke:

```
Convert this HTML to Kadence blocks using the html-to-kadence skill.
```

### Per-project bootstrap

```bash
cd /path/to/wordpress-project
bash ~/.cursor/skills/html-to-kadence/scripts/init-project.sh
# edit .html-to-kadence/project.yaml (or .cursor/html-to-kadence/project.yaml)
```

## Antigravity / other agents

Copy or clone into the agent’s skills / rules / knowledge folder, then
point the agent at `SKILL.md` as the entrypoint.

### Option A — Clone into agent skills dir

```bash
# Adjust path to your Antigravity / agent skills folder
git clone https://github.com/duyn1412/html-to-kadence-skill.git \
  ~/.antigravity/skills/html-to-kadence
```

Tell the agent:

> Use the skill at `~/.antigravity/skills/html-to-kadence/SKILL.md`
> to convert HTML into native Kadence Gutenberg blocks.

### Option B — Vendor into the WordPress project

```bash
cd /path/to/wordpress-project
git clone https://github.com/duyn1412/html-to-kadence-skill.git .agents/html-to-kadence
bash .agents/html-to-kadence/scripts/init-project.sh
```

Then in your agent instruction / AGENTS.md:

```markdown
## HTML → Kadence
Read `.agents/html-to-kadence/SKILL.md` first.
Project overlay: `.html-to-kadence/project.yaml (or .cursor/html-to-kadence/project.yaml)`
```

### Option C — One-shot (no install)

Paste or `@`-reference the raw GitHub URL to `SKILL.md` and ask the agent
to follow it for the conversion.

Raw entrypoint:

```
https://raw.githubusercontent.com/duyn1412/html-to-kadence-skill/main/SKILL.md
```

## What every agent must load

1. **`SKILL.md`** — orchestrator (always first)
2. **`reference.md`** — pipeline + mapping defaults
3. Project overlay **`.html-to-kadence/project.yaml (or .cursor/html-to-kadence/project.yaml)`** if present
4. Agent skills under `template/skills/` (or project `.cursor/skills/`)

## Optional — Kadence AI Validator plugin

Server-side block validation used by the pipeline gate before publish.

```bash
bash scripts/install-validator-plugin.sh /path/to/wp-content/plugins
# WP Admin → Plugins → Activate Kadence AI Validator
```

Then in `.html-to-kadence/project.yaml (or .cursor/html-to-kadence/project.yaml)`:

```yaml
rest:
  validate_endpoint: /kadence-ai/v1/validate
```

API: [docs/kadence-ai-validate-endpoint.md](docs/kadence-ai-validate-endpoint.md)

## Credentials (never commit)

```
WP_API_BASE=https://example.com/wp-json
WP_API_USER=YourUser
WP_APP_PASSWORD=xxxx xxxx xxxx xxxx
```

Store in `.credentials/wordpress-api.env` and gitignore it.

## Verify

Convert a single hero section. Expect:

- Native `<!-- wp:kadence/... -->` markup (not Custom HTML)
- Palette tokens, not raw hex
- Validation checklist passed before any publish
