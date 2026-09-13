# HTML → Kadence Conversion Pipeline

Follow these steps in order. Condense when context already loaded in-session.

## Phase 1 — Context (Steps 1–7)
1. Load `.cursor/html-to-kadence/project.yaml`
2. Discover theme stack (Kadence theme, child theme, Kadence Blocks plugins)
3. Read project rules and design tokens
4. Snapshot live site (pages, media, menus via REST API)
**Gate 1:** Stack Context Brief confirmed before Phase 2.

## Phase 2 — Design Intelligence (Steps 8–10)
5. Extract design system & palette tokens (`palette1`–`palette9`, fonts, container width)
6. Analyze HTML files into component tree
7. Match reusable patterns from `clone_source` or pattern library
**Gate 2:** HTML Analysis Document required before block composition.

## Phase 3 — Composition (Steps 11–12)
8. Map HTML components to Kadence blocks
9. Generate native Gutenberg block markup (`kadence/rowlayout`, `advancedheading`, `image`, `accordion`, `advancedbtn`)
10. Save raw block markup into `kadence-blocks/*.txt`
**Gate 3:** Zero Custom HTML blocks (`core/html`) allowed without documented exception.

## Phase 4 — Validation & Rigorous QA (Steps 13–16) — MANDATORY
11. **Automated Block Validation:** Run `python3 scripts/validate-blocks.py kadence-blocks/` (0 errors required).
12. **Content & Visual Fidelity:** Verify 1:1 match with HTML mockup (text, images, components).
13. **Responsive Testing:** Check mobile/tablet grid collapse and font scaling.
14. **A11y & SEO:** Verify single `h1`, logical heading tree, image `alt` attributes.
15. **Generate QA Sign-off Report:** Must produce full 5-gate pass/fail table.
**Gate 4:** QA Sign-off PASS required before delivery or publish.

## Phase 5 — Publish & Live Verification (Step 17)
16. Publish pages via REST API only if user explicitly requests (or deliver markup).
17. Run live site verification (HTTP 200, postmeta layout, navigation menu links, zero console 404s).
