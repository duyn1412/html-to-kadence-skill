# HTML → Kadence QA Pipeline (v1.1.0)

> **Philosophy**: *QA is a gate, not a report.* A conversion is never complete merely because valid-looking block markup was generated. A conversion is complete only when all mandatory QA gates pass. Never silently ignore, downgrade, or hide QA failures.

---

## 1. The 9-Stage QA Pipeline

```
  ┌─────────────────────────────────────────────────────────────┐
  │ 1. Preflight QA (Source HTML & Environment Sanity)          │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
  ┌──────────────────────────────▼──────────────────────────────┐
  │ 2. Structural QA (Gutenberg & Kadence Block Integrity)       │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
  ┌──────────────────────────────▼──────────────────────────────┐
  │ 3. Semantic / Content Preservation QA (Source vs Blocks)    │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
  ┌──────────────────────────────▼──────────────────────────────┐
  │ 4. Accessibility QA (A11y, Headings, Alt Text, Links)       │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
  ┌──────────────────────────────▼──────────────────────────────┐
  │ 5. WordPress Runtime & Serialization QA (Round-trip check)  │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
  ┌──────────────────────────────▼──────────────────────────────┐
  │ 6. Frontend QA (Asset Loading, Rendered HTML)               │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
  ┌──────────────────────────────▼──────────────────────────────┐
  │ 7. Responsive Visual QA (1440px / 768px / 390px Viewports)  │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
  ┌──────────────────────────────▼──────────────────────────────┐
  │ 8. Regression QA (Fixtures & Pass-Rate Invariance)          │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
  ┌──────────────────────────────▼──────────────────────────────┐
  │ 9. Final Gate: PASS → Ready to publish                      │
  │               FAIL → Auto-repair loop (max 3 rounds)        │
  └─────────────────────────────────────────────────────────────┘
```

### Stage 1: Preflight QA
- **Scope**: Source HTML mockup and target environment.
- **Checks**:
  - Source HTML is well-formed (tags close properly, document hierarchy is sensible).
  - Scope isolation: if `<main>` or container tags exist, separate page body from site header/footer.
  - Media & asset verification: image paths or external URLs are reachable or cataloged for replacement.
  - Design token extraction: CSS variables or theme palette mappings are discovered.

### Stage 2: Structural QA
- **Scope**: Generated Gutenberg block comments and Kadence JSON schemas.
- **Checks**:
  - Comment balance: `<!-- wp:... -->` opening tags match closing `<!-- /wp:... -->` plus self-closing `<!-- wp:... /-->`.
  - Strict JSON syntax: All block attributes parse without trailing commas, unquoted keys, or escaping errors.
  - Zero Custom HTML: `core/html` or raw non-block HTML outside container blocks is rejected unless explicitly allowed via `--allow-custom-html`.
  - Unique IDs: `uniqueID` is present on all Kadence blocks and strictly unique across the document.
  - Anchor uniqueness: HTML `id` attributes and anchors are unique.
  - Required Kadence classes: `kt-adv-heading{id}`, `data-kb-block="kb-adv-heading{id}"`, `has-theme-palette-N-color`.
  - Numeric font sizes: `fontSize` arrays must contain numeric px values or valid Kadence size tokens (`sm`, `md`, `lg`, etc.), not arbitrary text.
  - Placeholder detection: Zero tolerance for `TODO`, `FIXME`, `example.com`, `lorem ipsum`, `{{...}}`, `REPLACE_*`, `href="#"`.

### Stage 3: Semantic & Content Preservation QA
- **Scope**: Source HTML content manifest vs Block markup content manifest.
- **Targets**:
  - **Headings**: 100% preservation of text content and hierarchy intent.
  - **Buttons & CTAs**: 100% preservation of button text and click actions.
  - **Link Destinations**: 100% preservation of target `href` URLs.
  - **Images**: 100% preservation of visual media references.
  - **Body Text Tokens**: Minimum 98% word-token preservation (accounting for whitespace/formatting differences).
  - **Reading Order**: Sequential ordering of major sections must match source.

### Stage 4: Accessibility QA
- **Scope**: HTML semantics and WCAG 2.1 AA baseline.
- **Checks**:
  - Exactly one `<h1>` per page.
  - No heading level skipping (e.g. `<h1>` immediately followed by `<h3>`).
  - All `<img>` and `kadence/image` elements must have meaningful `alt` attributes (or empty `alt=""` if purely decorative).
  - Links must have accessible names (no empty `<a>` tags or icon-only links without `aria-label`).
  - Non-generic CTA text (avoid ambiguous standalone labels like "click here").

### Stage 5: WordPress Runtime / Serialization QA
- **Scope**: WordPress REST API and Gutenberg block parser.
- **Checks**:
  - Round-trip serialization: POST/PUT content to WP REST API as `draft`, then GET `content.raw` and verify byte/AST equivalence.
  - Block parser stability: Ensure WordPress block parser does not trigger auto-recovery warnings ("This block contains unexpected or invalid content").
  - Optimistic concurrency: Verify `modified_gmt` or content hash before updating existing pages.

### Stage 6: Frontend QA
- **Scope**: Server-rendered HTML output via `do_blocks()`.
- **Checks**:
  - PHP warnings/errors: Zero PHP notices or warnings during block rendering.
  - Render non-empty: Rendered markup must produce valid, styled HTML elements.
  - Script & stylesheet enqueues: Kadence frontend CSS (`kt-blocks-css`) correctly loads required assets.

### Stage 7: Responsive Visual QA
- **Scope**: Multi-viewport visual fidelity comparison.
- **Breakpoints**:
  - Desktop: `1440px` (min threshold: 0.92)
  - Tablet: `768px` (min threshold: 0.90)
  - Mobile: `390px` (min threshold: 0.90)
- **Defect Severity**:
  - `Critical`: Missing section, horizontal overflow on mobile, broken overlapping containers.
  - `Major`: Wrong column count, broken responsive stacking, substantially wrong spacing.
  - `Minor`: Small padding mismatch (< 15px), modest line-height difference.
  - `Cosmetic`: Sub-pixel alignment differences (does not block gate).

### Stage 8: Regression QA
- **Scope**: Continuous validation against standardized test fixtures (`tests/fixtures/`).
- **Checks**:
  - Verified passing fixtures must continue to PASS.
  - Intentional failure fixtures must be caught with exact matching error codes.
  - Pass rate must not decrease after framework updates.

### Stage 9: Final QA Gate
- **Decision Engine**:
  - Evaluates weighted score and hard gating conditions.
  - Output: `PASS` (proceed to publish) or `FAIL` (enter repair loop or halt).

---

## 2. Scoring Model & Calculations

The QA Engine computes an overall score from four core categories:

$$\text{Overall Score} = (0.35 \times \text{Structural}) + (0.35 \times \text{Content}) + (0.15 \times \text{A11y}) + (0.15 \times \text{Runtime})$$

When Visual QA is run in an integration environment with browser capture:
$$\text{Overall Score} = (0.25 \times \text{Structural}) + (0.25 \times \text{Content}) + (0.15 \times \text{A11y}) + (0.15 \times \text{Runtime}) + (0.20 \times \text{Visual})$$

### Hard Gating Conditions (Non-negotiable)
The gate will **FAIL immediately**, regardless of overall weighted score, if any of the following occur:
1. **Structural Score < 100**: Any syntax error, comment mismatch, or invalid block JSON.
2. **Content Score < 98**: Any heading loss, CTA loss, or text token overlap below 98%.
3. **Runtime Score < 100**: WordPress serialization change or block recovery error.
4. **Any Critical Error**: Unresolved critical issues (such as `DUPLICATE_UNIQUE_ID`, `PLACEHOLDER_DETECTED`, `CUSTOM_HTML_NOT_ALLOWED`).
5. **A11y Score < 90**: Severe accessibility flaws (missing H1 or unlabeled images).

---

## 3. Directory of Standardized Error Codes

| Error Code | Severity | Description | Suggested Repair Action |
|:---|:---:|:---|:---|
| `STRUCTURE_INVALID` | Critical | Gutenberg block comments are mismatched or unbalanced. | Ensure every non-void block has a matching `<!-- /wp:blockname -->` closing comment. |
| `BLOCK_JSON_INVALID` | Critical | Block JSON attributes failed `json.loads()`. | Inspect JSON attributes for unescaped quotes, trailing commas, or invalid types. |
| `DUPLICATE_UNIQUE_ID` | Critical | The same `uniqueID` is used on multiple Kadence blocks. | Regenerate unique IDs using format `{pageId}_{randomHex}`. |
| `DUPLICATE_ANCHOR` | Critical | Duplicate HTML `id` attribute detected. | Ensure all section anchors and element IDs are unique across the page. |
| `CUSTOM_HTML_NOT_ALLOWED`| Critical | `core/html` block used without explicit override. | Replace custom HTML with native Kadence blocks (`rowlayout`, `advancedheading`, etc.). |
| `PLACEHOLDER_DETECTED` | Critical | Unresolved placeholder text (`TODO`, `example.com`, `href="#"`). | Replace placeholders with production content or valid destination URLs. |
| `CONTENT_LOST` | Critical | Headings, CTAs, or body text missing from output. | Review source HTML manifest and restore missing elements into block tree. |
| `LINK_TARGET_CHANGED` | Major | Link destination URL differs from source. | Restore exact `href` URL from source mockup. |
| `CTA_MISSING` | Critical | Call to action button from source HTML is absent in blocks. | Add `kadence/singlebtn` or `kadence/advancedbtn` with matching label and URL. |
| `IMAGE_MISSING` | Major | Image from source HTML is missing in blocks. | Add `kadence/image` or column background image. |
| `ACCESSIBILITY_H1_MISSING` | Critical | No H1 heading found on page. | Change primary section heading level to 1. |
| `ACCESSIBILITY_H1_MULTIPLE`| Major | Multiple H1 headings found on page. | Demote secondary hero headings to H2. |
| `ACCESSIBILITY_HEADING_SKIP`| Minor | Heading level skipped (e.g. H2 to H4). | Adjust heading levels to follow sequential hierarchy. |
| `ACCESSIBILITY_ALT_MISSING`| Major | Image element missing `alt` attribute. | Add descriptive alt text describing the image content. |
| `ROUND_TRIP_CHANGED_MARKUP`| Critical | WordPress modified or stripped block markup on save. | Check for invalid HTML inside block wrappers or unrecognized block attributes. |
| `WORDPRESS_SAVE_FAILED` | Critical | WP REST API returned an HTTP error on update. | Verify user authentication, application password permissions, and post ID. |
| `LIVE_CONTENT_CHANGED_ABORTED`| Critical | Optimistic concurrency conflict: live page was modified. | Fetch latest live page content, re-diff, and re-run conversion pipeline. |
| `VISUAL_DESKTOP_BELOW_THRESHOLD`| Major | Desktop visual rendering match below threshold (0.92). | Adjust column widths, typography font size, or padding. |
| `VISUAL_MOBILE_BELOW_THRESHOLD`| Critical | Mobile visual rendering match below threshold (0.90). | Check mobile column collapse order and responsive font sizes. |
| `QA_REPAIR_LIMIT_REACHED`| Critical | Auto-repair failed after maximum attempts (3 rounds). | Escalate to developer with targeted failure report; do not publish. |

---

## 4. The Automated Diagnostic & Repair Loop

When the QA engine reports errors, the pipeline enters a controlled diagnostic and repair cycle:

```
  ┌──────────────┐
  │ Run QA Engine│
  └──────┬───────┘
         │
    Is Status PASS? ────► [YES] ────► Proceed to Publish / Delivery
         │
       [NO]
         │
    Round <= 3? ────────► [NO]  ────► ABORT with QA_REPAIR_LIMIT_REACHED
         │
       [YES]
         │
  ┌──────▼──────────────────────────────────────────────────────┐
  │ 1. Isolate Defect: Target smallest affected block scope.     │
  │ 2. Apply Targeted Patch (Do NOT rewrite entire page).        │
  │ 3. Re-run QA Engine on repaired scope.                      │
  │ 4. Increment Round Counter (round = round + 1).             │
  └─────────────────────────────────────────────────────────────┘
```

### Golden Rule of Repair
**Repair the smallest affected scope.** If a single heading has a missing class or an image has a missing `alt` attribute, modify ONLY that block. Never discard and regenerate the entire page layout to fix localized QA defects.
