# HTML → Kadence Conversion Pipeline

Follow these steps in order. Condense when context already loaded in-session.

## Phase 1 — Context (1–7)

Load `project.yaml`, discover theme stack, read project rules, REST snapshot.

**Gate:** Stack Context Brief confirmed before Phase 2.

## Phase 2 — Design intelligence (8–10)

Extract design system, analyze HTML, find reusable patterns from `clone_source`.

**Gate:** HTML Analysis Document required before mapping.

## Phase 3 — Composition (11–12)

Map to blocks, generate markup by **cloning** reference page structure.

**Gate 12b:** REST validate `success: true` if endpoint configured.

## Phase 4 — QA (13–16)

QA Reviewer runs responsive, a11y, SEO, performance checks.

**Gate:** QA sign-off before publish.

## Phase 5 — Publish (17)

Only if user explicitly requests. Default status: `draft`.

---

Generic reference: `~/.cursor/skills/html-to-kadence/reference.md`
Extend pipeline: `~/.cursor/skills/html-to-kadence/extending.md`
