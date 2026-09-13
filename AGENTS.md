# AGENTS.md — HTML → Kadence Framework (v1.1.0)

This repository is a **portable agent skill**. Any AI coding agent (Cursor, Antigravity, Claude Code, Codex) should treat `SKILL.md` as the primary entrypoint.

## Entrypoint

Read and follow: [`SKILL.md`](./SKILL.md)

## Core Philosophy

```
Analyze ──► Convert ──► QA Engine ──► PASS? ──► [Ready to publish]
                            │
                          [FAIL]
                            │
                            ▼
     Diagnose ──► Repair smallest scope ──► Re-run QA (max 3)
```

> **Non-Negotiable**: **QA IS A GATE, NOT A REPORT.**  
> Never mark a conversion as complete or deliver markup without running and passing all mandatory QA gates. Never silently ignore or downgrade QA errors.

## Hard Rules

1. **Native Kadence Blocks Only**: No `core/html` or raw Custom HTML dumps.
2. **Zero Placeholder Tolerance**: Never leave `TODO`, `FIXME`, `example.com`, `lorem ipsum`, or `href="#"` in generated blocks.
3. **Mandatory QA Gate**: Run `python3 scripts/qa-engine.py`; require Structural = 100, Content $\ge 98$, and zero critical errors.
4. **Targeted Repair**: When QA fails, repair the smallest affected block scope. Do not regenerate the entire page.
5. **Never Auto-Publish**: Deliver block markup and formal QA sign-off report unless the user explicitly requests publish.
6. **Optimistic Concurrency & Safety**: Always `GET` live content first. Abort with `LIVE_CONTENT_CHANGED_ABORTED` if live content changed prior to write.
7. **Credentials Isolation**: Never commit `.credentials/` or API passwords.

## Suggested Load Order for Agents

1. [`SKILL.md`](./SKILL.md) — Orchestration & workflow entrypoint
2. Project Configuration: Check `.html-to-kadence/project.yaml` (primary) or `.cursor/html-to-kadence/project.yaml` (legacy fallback)
3. [`docs/qa-pipeline.md`](./docs/qa-pipeline.md) — The 9 QA stages, scoring rules, and error codes
4. [`docs/wordpress-safety.md`](./docs/wordpress-safety.md) — Optimistic concurrency and round-trip validation
5. [`docs/kadence-compatibility.md`](./docs/kadence-compatibility.md) — Block slug vs editor UI terminology mapping
6. [`reference.md`](./reference.md) — Pipeline details and block mapping reference

## Installation

See [`INSTALL.md`](./INSTALL.md) for setup across Cursor, Antigravity, Claude Code, and other agent platforms.
