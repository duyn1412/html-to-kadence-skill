# HTML → Kadence Skill

Portable agent skill: convert HTML mockups into **native Kadence / Gutenberg**
blocks for WordPress.

Works with **Cursor**, **Antigravity**, Claude Code, Codex, and any agent that
can follow a markdown skill file.

## Quick start

1. Install — see [INSTALL.md](INSTALL.md)
2. Bootstrap a WP project: `bash scripts/init-project.sh`
3. Tell the agent: *Convert this HTML using the html-to-kadence skill*

Entrypoint for agents: **[SKILL.md](SKILL.md)** · **[AGENTS.md](AGENTS.md)**

## What’s inside

```
html-to-kadence-skill/
├── SKILL.md                      # Orchestrator (entry)
├── AGENTS.md                     # Cross-agent contract
├── INSTALL.md                    # Cursor / Antigravity / others
├── reference.md                  # 17-step pipeline + mapping
├── bootstrap.md                  # New project setup
├── extending.md                  # Learn & extend
├── project-config.template.yaml
├── scripts/
│   ├── init-project.sh
│   ├── link-skill.sh
│   └── install-validator-plugin.sh
├── wordpress-plugin/
│   └── kadence-ai-validator/     # REST validate endpoint (optional)
├── docs/
│   └── kadence-ai-validate-endpoint.md
└── template/                     # Copied into project .cursor/
    ├── rules/
    ├── skills/                   # 5 core agents
    ├── docs/
    └── workflows/
```

## Optional: validate plugin

Install into WordPress, then activate **Kadence AI Validator**:

```bash
bash scripts/install-validator-plugin.sh /path/to/wp-content/plugins
```

Endpoint: `POST /wp-json/kadence-ai/v1/validate` — see [docs/kadence-ai-validate-endpoint.md](docs/kadence-ai-validate-endpoint.md).

## Architecture

| Layer | Where | Purpose |
|-------|-------|---------|
| **Framework** (this repo) | skill folder | Generic pipeline, validation, agents |
| **Project overlay** | `.cursor/html-to-kadence/project.yaml` | Page IDs, tokens, learnings |

## Non-negotiables

- Native Kadence blocks (not Custom HTML dumps)
- Clone from a live reference page — don’t invent structure
- Validate before publish; never auto-publish
- Page-update safety: fetch live content before overwrite
- Credentials stay in `.credentials/` (never committed)

## Version

1.0.2 — includes `kadence-ai-validator` WordPress plugin (2026-09-13)  
Originally extracted from a production Coast Residences Kadence build (2026-07).

## License

MIT
