# Skill: QA Reviewer

**Tier:** Core | **Steps:** 13–16

## Purpose

Orchestrate quality gates before deliver/publish.

## Checklist

- [ ] Markup validation checklist passed
- [ ] Responsive attributes on key blocks
- [ ] Heading hierarchy (one h1, logical order)
- [ ] Alt text on images
- [ ] No placeholder media IDs
- [ ] Tokens from design system, not raw HTML hex
- [ ] `learnings` from project.yaml applied

## Supporting agents (invoke as needed)

- `responsive-optimizer`, `accessibility-reviewer`, `seo-reviewer`, `performance-reviewer`

## Output

**QA Sign-off** — PASS / FAIL with remediation list. FAIL blocks publish.
