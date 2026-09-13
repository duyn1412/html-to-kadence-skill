# Skill: QA Reviewer

**Tier:** Core | **Steps:** 13–16 | **Mandatory Quality Gate**

## Purpose

Orchestrate rigorous, structured quality gates after block composition and before delivery/publishing.
**No conversion deliverable or publish is approved without a formal QA Sign-off Report.**

---

## The 5 Quality Gates

Every conversion must pass all 5 gates. If any gate fails, reject the markup back to `kadence-block-composer` for remediation.

### Gate 1: Block Markup & Syntax Integrity (Automated)

Run the automated validator script:
```bash
python3 scripts/validate-blocks.py kadence-blocks/
```
Or with custom validator endpoint if configured.

**Pass Criteria:**
- [ ] Script exits with code `0` (Zero errors).
- [ ] Every block has a unique, non-empty string `uniqueID` in `{pageId}_{hash}` format.
- [ ] Advanced Heading inner HTML contains `kt-adv-heading{uniqueID}` and `data-kb-block="kb-adv-heading{uniqueID}"`.
- [ ] Color classes match inner HTML: `colorClass: "theme-paletteN"` → `class="... has-theme-palette-N-color has-text-color"`.
- [ ] Font sizes use numeric px arrays `[desktop, tablet, mobile]` or valid Kadence tokens (`sm`, `md`, `lg`, `xl`, etc.). Never invented strings.
- [ ] Multi-column rows define `colLayout` and valid `columns` count.
- [ ] Row overlays use hex color (`#hex`), never raw palette slugs.
- [ ] All image blocks have valid asset URLs/IDs (zero `REPLACE_*` placeholders).
- [ ] Zero Custom HTML blocks (`core/html`) unless explicitly approved in `project.yaml`.

---

### Gate 2: Content & Visual Fidelity (1:1 with HTML Mockup)

Compare the generated blocks/pages against the original HTML mockup:

- [ ] **Text & Copy:** 100% of headings, body copy, labels, badge texts, buttons, and microcopy match the original HTML exactly.
- [ ] **Design Tokens:** All colors map directly to `palette1`–`palette9` defined in `project.yaml`. No untracked ad-hoc hex values in block attributes.
- [ ] **Media Assets:** All images, icons, and diagrams from the mockup are uploaded to WordPress media and rendered.
- [ ] **Components & Interactive:** Accordions, button groups, grids, cards, and spacers match the mockup's intended hierarchy and layout.

---

### Gate 3: Responsive Behavior & Mobile Optimization

- [ ] **Grid Collapse:** Multi-column rows collapse cleanly to single-column or specified tablet layout on smaller screens (`tabletLayout: "row"`, `colLayout: "equal"`).
- [ ] **Font Scaling:** Headings have appropriate mobile/tablet sizes defined via `fontSize: [desktop, tablet, mobile]` to avoid overflow.
- [ ] **Touch Targets:** All buttons and interactive links have at least 44×44px clickable area on mobile.
- [ ] **Padding & Gutters:** Row layouts use responsive padding (reduced top/bottom margins on mobile) to avoid excessive dead whitespace.

---

### Gate 4: Accessibility (A11y) & SEO Semantic Structure

- [ ] **Heading Hierarchy:** Exactly one `<h1>` per page. Subsections follow sequential heading hierarchy (`h2` → `h3`), with no skipped levels.
- [ ] **Image Alt Attributes:** Meaningful `alt` text on informative images; decorative images have empty `alt=""`.
- [ ] **Color Contrast:** Text against background meets WCAG AA standards (minimum 4.5:1 for normal text, 3:1 for large text).
- [ ] **Semantic Markup:** Descriptive button and link labels (no ambiguous "click here").

---

### Gate 5: Live Site Verification (Post-Publish / Staging)

When blocks are published to WordPress staging/production:

- [ ] **HTTP 200:** All published page URLs return HTTP status 200 OK.
- [ ] **Layout & Template:** Default theme `entry-title` and redundant container padding are disabled on custom full-width landing pages (`_kad_post_title: "hide"`, `_kad_post_content_style: "fullwidth"`).
- [ ] **Clean Rendering:** No raw Gutenberg block comments (`<!-- wp:... -->`) or unrendered shortcodes visible in browser DOM.
- [ ] **Network & Console:** Zero 404 errors for images, stylesheets, or scripts in the browser console / Network tab.
- [ ] **Navigation:** Primary header menu links point to correct page IDs or permalinks, active state highlights correctly.

---

## Required QA Output: QA Sign-off Report

The QA Reviewer must output this structured report at the end of Phase 4:

```markdown
### QA Sign-off Report: [Project Name]

| Gate | Focus Area | Status | Notes / Remediation |
|---|---|---|---|
| **Gate 1** | Block Markup Integrity | ✅ PASS / ❌ FAIL | Zero syntax errors, valid uniqueIDs |
| **Gate 2** | Content & Visual Fidelity | ✅ PASS / ❌ FAIL | 100% copy match, tokens aligned |
| **Gate 3** | Responsive Behavior | ✅ PASS / ❌ FAIL | Mobile font scaling and grid collapse verified |
| **Gate 4** | A11y & SEO Hierarchy | ✅ PASS / ❌ FAIL | Single h1, valid heading sequence, alt tags present |
| **Gate 5** | Live Site Verification | ✅ PASS / ❌ FAIL | HTTP 200, clean frontend render, no 404 assets |

**Final Decision:** ✅ APPROVED FOR PUBLISH / 🛑 BLOCKED (Requires fix)
```
