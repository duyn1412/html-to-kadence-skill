# AGENTS.md — HTML → Kadence

This repository is a **portable agent skill**. Any coding agent should treat
`SKILL.md` as the single entrypoint.

## Entrypoint

Read and follow: [`SKILL.md`](./SKILL.md)

## When to use

User asks to:

- Convert HTML / mockups / design files into WordPress Kadence blocks
- Generate `<!-- wp:kadence/... -->` Gutenberg markup
- Bootstrap an HTML→Kadence workflow in a new WP project

## Hard rules

1. Native Kadence blocks only — no Custom HTML unless documented exception
2. Clone structure from the project’s reference page — do not invent layouts
3. Validate markup before publish
4. Never auto-publish — deliver markup unless the user explicitly asks to publish
5. Before overwriting an existing page: `GET` live content first (page-update safety)
6. Never commit `.credentials/` or API passwords

## Suggested load order

1. `SKILL.md`
2. `reference.md`
3. Project `.cursor/html-to-kadence/project.yaml` (if exists)
4. Relevant `template/skills/*/SKILL.md` (or project overrides in `.cursor/skills/`)
5. `template/docs/kadence-markup-validation.md` before finalizing markup

## Install

See [`INSTALL.md`](./INSTALL.md) for Cursor, Antigravity, and other agents.
