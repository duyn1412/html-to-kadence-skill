# HTML → Kadence Skill (v1.1.0)

[![HTML-to-Kadence CI](https://github.com/duyn1412/html-to-kadence-skill/actions/workflows/test.yml/badge.svg)](https://github.com/duyn1412/html-to-kadence-skill/actions/workflows/test.yml)

Portable agent skill: convert HTML mockups into **native Kadence / Gutenberg** blocks for WordPress with a rigorous, automated **9-stage Quality Assurance (QA) Engine**.

Works with **Cursor**, **Antigravity**, Claude Code, Codex, and any AI agent that follows markdown skill files.

---

## Core Principle

```
Analyze ──► Convert ──► QA Engine ──► PASS? ──► [Ready to publish]
                            │
                          [FAIL]
                            │
                            ▼
                        Diagnose
                            │
                            ▼
              Repair smallest affected scope
                            │
                            ▼
                     Re-run QA Engine (max 3 rounds)
```

> **Important Rule**: **QA IS A GATE, NOT A REPORT.**  
> A conversion is never complete merely because valid-looking block markup was generated. A conversion is complete only when all mandatory QA gates pass. Never silently ignore, downgrade, or hide QA failures.

---

## Quick start

1. **Install** — see [INSTALL.md](INSTALL.md)
2. **Bootstrap a WP project**:
   ```bash
   bash scripts/init-project.sh
   ```
3. **Run Regression Tests**:
   ```bash
   python3 scripts/run-tests.py
   ```
4. **Tell the agent**:
   > *Convert this HTML using the html-to-kadence skill*

Entrypoint for agents: **[SKILL.md](SKILL.md)** · **[AGENTS.md](AGENTS.md)**

---

## Repository Structure

```
html-to-kadence-skill/
├── SKILL.md                      # Primary orchestrator & entrypoint
├── AGENTS.md                     # Cross-agent contract & roles
├── INSTALL.md                    # Installation for Cursor, Antigravity, etc.
├── reference.md                  # Detailed block mapping & conversion pipeline
├── bootstrap.md                  # New project bootstrap guide
├── extending.md                  # Extending agents, rules, and mappings
├── project-config.template.yaml  # v1.1.0 config template
├── scripts/
│   ├── qa-engine.py              # Zero-dependency 9-stage QA engine & scoring
│   ├── validate-blocks.py        # Fast block validation wrapper
│   ├── run-tests.py              # Regression test suite runner
│   ├── init-project.sh           # Project initializer (tool-neutral)
│   ├── link-skill.sh             # Agent symlink helper
│   └── install-validator-plugin.sh
├── tests/
│   └── fixtures/                 # 8 PASS & intentional FAIL fixtures
├── docs/
│   ├── qa-pipeline.md            # 9 QA stages, scoring model & error codes
│   ├── wordpress-safety.md       # Optimistic concurrency & round-trip safety
│   ├── kadence-compatibility.md  # Block slug vs UI names & version matrix
│   └── kadence-ai-validate-endpoint.md
├── wordpress-plugin/
│   └── kadence-ai-validator/     # Optional WP REST API validation plugin (v1.1.0)
└── template/                     # Scaffolding copied to user projects
    ├── docs/
    ├── rules/
    ├── skills/
    └── workflows/
```

---

## The 9-Stage QA Pipeline

The automated QA engine enforces strict quality criteria across 9 distinct stages:

1. **Preflight QA**: Source HTML integrity, scope isolation (`<main>`), media reachability.
2. **Structural QA**: Gutenberg comment balance, valid JSON attributes, zero Custom HTML, unique IDs, no duplicate anchors, placeholder detection (`TODO`, `example.com`, `href="#"`).
3. **Semantic / Content Preservation QA**: 100% headings, 100% CTAs, 100% link URLs, 100% images, $\ge 98\%$ text token preservation.
4. **Accessibility QA**: Single `h1`, no skipped heading levels, image `alt` text, accessible button/link names.
5. **WordPress Runtime QA**: Round-trip serialization invariance (`PUT` -> `GET raw` equivalence check).
6. **Frontend QA**: Clean PHP execution via `do_blocks()`, zero render notices.
7. **Responsive Visual QA**: Desktop (1440px), Tablet (768px), Mobile (390px) fidelity checks.
8. **Regression QA**: Automated fixture testing ensuring pass rate invariance.
9. **Final QA Gate**: Non-negotiable hard gate: Structural must be 100, Content $\ge 98$, zero critical errors.

Detailed documentation: **[docs/qa-pipeline.md](docs/qa-pipeline.md)**

---

## Tool-Neutral Portability

The framework does not depend on `.cursor/`. It supports clean, tool-neutral project layouts:

1. `--config <path>` (explicit CLI flag)
2. `.html-to-kadence/project.yaml` (primary canonical location)
3. `.cursor/html-to-kadence/project.yaml` (legacy Cursor fallback)
4. Built-in defaults

---

## Safe WordPress Updates & Concurrency

- **Optimistic Concurrency**: Fetch page state before conversion; verify `content_sha256` immediately prior to writing. Abort with `LIVE_CONTENT_CHANGED_ABORTED` on conflict.
- **Draft-First Policy**: All automated mutations default to `draft`.
- **Local Snapshots**: Automatic backup of `post_content` to `.backups/` before any update.

Detailed documentation: **[docs/wordpress-safety.md](docs/wordpress-safety.md)**

---

## Running Automated QA & Tests

Run the full regression test suite locally:
```bash
python3 scripts/run-tests.py
```

Run QA engine directly against generated blocks:
```bash
# Basic structural + semantic validation
python3 scripts/qa-engine.py path/to/blocks.txt --html path/to/source.html

# Machine-readable JSON output
python3 scripts/qa-engine.py path/to/blocks.txt --html path/to/source.html --json
```

---

## Version History

- **v1.1.0** (2026-09-13):
  - Comprehensive 9-stage QA engine (`scripts/qa-engine.py`) with hard gating & automated diagnostic repair loop.
  - Regression test suite with 8 PASS and intentional FAIL test fixtures.
  - Tool-neutral portability (`.html-to-kadence/` primary, `.cursor/` fallback).
  - Optimistic concurrency control & round-trip serialization safety (`docs/wordpress-safety.md`).
  - Kadence Blocks UI terminology & compatibility matrix (`docs/kadence-compatibility.md`).
  - GitHub Actions CI workflow for script syntax & regression tests.
  - Bumped validator plugin to v1.1.0 with standardized error reporting.
- **v1.0.2** (2026-09-13): Initial `kadence-ai-validator` WordPress plugin.
- **v1.0.0** (2026-07): Initial extraction from production Coast Residences build.

## License

MIT
