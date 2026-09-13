# HTML → Kadence AI Framework (Project Instance)

Project-local framework. Generic rules live in `~/.cursor/skills/html-to-kadence/`.

## Layout

```
.cursor/
├── html-to-kadence/project.yaml   # Project config + learnings
├── rules/                         # Orchestrator rule
├── skills/                        # Agent skills (override/extend)
├── docs/                          # Validation, mapping quick ref
└── workflows/                     # Pipeline steps
docs/
└── kadence-html-mapping.md        # Full HTML→block mapping
```

## Five core agents

| Agent | Skill | Role |
|-------|-------|------|
| Kadence Architect | `kadence-architect` | Theme, blocks, child theme |
| HTML Analyzer | `html-analyzer` | Parse HTML → sections |
| Block Composer | `kadence-block-composer` | Generate block markup |
| QA Reviewer | `qa-reviewer` | Quality gates |
| REST Publisher | `rest-publisher` | Read/write WordPress |

## Invoke

> Convert this HTML to Kadence blocks using the html-to-kadence skill.

## Update & extend

1. Append failures to `project.yaml` → `learnings`
2. Add agents in `project.yaml` → `agents.supporting`
3. See `~/.cursor/skills/html-to-kadence/extending.md`
