# Skill: HTML Analyzer

**Tier:** Core | **Step:** 9

## Purpose

Parse HTML into structured section tree for block mapping.

## Output: HTML Analysis Document

JSON with `sections[]`, `heading_outline`, `forms`, `warnings`.

Each section: `pattern_hint` (hero, two-column, faq, cta, form), `children`, `token_hints`.

## Rules

- Analyze only — do not propose blocks
- Map inline hex to nearest palette token from `project.yaml` when confident
- Flag Custom HTML triggers (scripts, embeds)

## Workflow

1. Split top-level sections
2. Walk children (max depth 6)
3. Build heading outline
4. Emit JSON document
