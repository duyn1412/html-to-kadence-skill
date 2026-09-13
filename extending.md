# Extending the HTML → Kadence Framework

How to learn, update, and grow the framework per project without forking the core skill.

## Three extension mechanisms

### 1. Project overlay (`project.yaml`)

**Use for:** IDs, tokens, URLs, project-specific rules learned from failures.

```yaml
learnings:
  - id: unique-id-format
    date: 2026-07-10
    rule: "uniqueID must be {pageId}_{8hex}; match data-kb-block attribute"
    source: "About page v1 broken render"
```

After each failed or successful conversion, append a learning. Agents must read
`learnings` before composing markup.

### 2. Project skills (`.cursor/skills/`)

**Use for:** Agent behavior that differs from generic defaults.

Add or override a skill file — same name as framework agent:

```
.cursor/skills/kadence-block-composer/SKILL.md   # overrides generic composer rules
.cursor/skills/my-custom-carousel/SKILL.md     # new supporting agent
```

Register new agents in `project.yaml`:

```yaml
agents:
  supporting:
    - name: my-custom-carousel
      skill: .cursor/skills/my-custom-carousel/SKILL.md
      pipeline_step: "11b"
      invokes_when: "HTML contains .carousel or swiper class"
```

### 3. Project mapping doc (`docs/kadence-html-mapping.md`)

**Use for:** HTML element → Kadence block tables, site patterns, token values.

Keep the **full** mapping here (can be long). Framework `reference.md` stays generic.

## Adding a new supporting agent

1. Create `.cursor/skills/<agent-name>/SKILL.md` using this template:

```markdown
# Skill: <Agent Name>

**Tier:** Supporting
**Pipeline step:** <N or "on-demand">

## Purpose
<one sentence>

## Inputs
| Input | Required |
|-------|----------|

## Outputs
<artifact name and format>

## Rules
- ...

## Workflow
1. ...
```

2. Register in `project.yaml` → `agents.supporting`
3. Update `.cursor/docs/agent-communication.md` hub diagram
4. Add invocation note to QA Reviewer or Block Composer skill

## Updating after a conversion failure

**Post-mortem checklist:**

1. What broke? (frontend render | Gutenberg invalid block | wrong tokens)
2. Add `learning` entry to `project.yaml`
3. If repeatable → add rule to `kadence-markup-validation.md`
4. If site-specific → update `kadence-block-composer/SKILL.md`
5. If generic Kadence rule → propose update to `~/.cursor/skills/html-to-kadence/reference.md`

## Versioning

Track framework version in `project.yaml`:

```yaml
framework_version: "1.1.0"   # skill package version
project_overlay_version: "3" # increment when learnings/rules change
```

When pulling skill updates:

```bash
diff ~/.cursor/skills/html-to-kadence/reference.md <old-copy>
# Merge generic improvements into reference; keep project.yaml learnings
```

## Anti-patterns

- **Don't** hardcode page IDs in generic skill files — use `project.yaml`
- **Don't** duplicate full mapping in SKILL.md — link to `docs/kadence-html-mapping.md`
- **Don't** skip learnings — they're how the next conversion avoids the same bug
- **Don't** invent block JSON without cloning a live reference block

## Coast Residences as reference implementation

The Coast project (`coastresidences`) is the reference implementation:

- 11 agent skills in `.cursor/skills/`
- Full pipeline in `.cursor/workflows/html-to-kadence-pipeline.md`
- `docs/kadence-html-mapping.md` — production mapping
- Child theme validate endpoint pattern

Copy patterns from Coast; replace IDs/tokens via `project.yaml`.
