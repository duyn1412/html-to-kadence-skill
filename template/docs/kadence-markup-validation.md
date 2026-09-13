# Kadence Markup Validation & Quality Assurance Guide

**Mandatory Quality Check** before delivering markup or publishing to WordPress.
This document defines the validation procedures and common Gutenberg validation pitfalls.

---

## 1. Automated Validation Procedure

Run the validation script against generated block files:

```bash
# Validate specific directory
python3 scripts/validate-blocks.py kadence-blocks/

# Validate with strict warning checks
python3 scripts/validate-blocks.py kadence-blocks/ --strict
```

If the WordPress validation REST endpoint is installed (`kadence-ai-validator` plugin):
```bash
curl -X POST "https://your-site.com/wp-json/kadence-ai/v1/validate" \
  -H "Content-Type: application/json" \
  -d '{"content": "<!-- wp:kadence/..."}'
```

---

## 2. Core Block Validation Rules

### `uniqueID`
- **Format:** `{pageId}_{6hex}-{2hex}` or `{pageId}_{8hex}` (e.g. `14_3dabfd-46`).
- **Requirement:** Must be a non-empty string and unique across the entire post.
- **CSS Binding:** Block class and `data-kb-block` attributes in inner HTML must match the uniqueID exactly.

### `kadence/advancedheading`
Gutenberg will invalidate the block if inner HTML does not match the block's `save()` output:
- **Inner Tag:** Tag must match attribute: `htmlTag: "p"` → `<p>`, `level: 1` → `<h1>`, `level: 2` → `<h2>`.
- **Classes Required:** `kt-adv-heading{uniqueID} wp-block-kadence-advancedheading`.
- **Attribute Required:** `data-kb-block="kb-adv-heading{uniqueID}"`.
- **Palette Binding:** If `colorClass: "theme-paletteN"` is set in attributes, inner HTML **must** contain:
  `has-theme-palette-N-color has-text-color` (notice the hyphen between `palette` and `N`).
- **Font Size:** Must be an array of numbers `[desktop, tablet, mobile]` e.g. `[48, "", 32]` or Kadence tokens (`sm`, `md`, `lg`, `xl`, `xxl`, `3xl`). Never use raw strings like `"4xl"`.
- **Link Attribute:** If `link` attribute is set, inner HTML must contain the `<a>` tag.

### `kadence/rowlayout`
- **Multi-column:** When `"columns": 2` or more, `"colLayout"` is mandatory (e.g. `"equal"`, `"two-one"`).
- **Overlay:** Must use hex color (e.g. `"#1c1917"`). Do not use palette slugs (e.g. `"palette1"`).
- **Background Color:** If `bgColor` is a palette slug (`"palette1"`), `"bgColorClass": "theme-palette1"` must also be set.
- **Version:** Include `"kbVersion": 2` and `"align": "full"`.

### `kadence/image`
- Must have valid `url` or `id`.
- Zero `REPLACE_*` placeholders allowed.

---

## 3. Common Failures & Quick Fixes

| Symptom | Root Cause | Fix |
|---|---|---|
| "This block contains unexpected or invalid content" | Inner HTML doesn't match `uniqueID` or tag in block attributes | Ensure inner tag matches `level`/`htmlTag`, and classes include `kt-adv-heading{uid}` |
| Text color doesn't show in frontend / editor | Missing `colorClass` or inner HTML class mismatch | Set both `colorClass: "theme-paletteN"` and inner HTML `has-theme-palette-N-color has-text-color` |
| Block appears unstyled or default serif font | Font size or weight passed as invalid string | Use numeric px array `[40, "", 28]` and proper font family token |
| Row overlay transparent or wrong color | Overlay attribute using palette slug instead of hex | Change `"overlay": "palette3"` to `"overlay": "#23272B"` |
| Layout squished inside small container | Missing fullwidth post layout meta | Set postmeta `_kad_post_content_style: "fullwidth"` |
| Extra page title showing above custom hero | Kadence page title bar active | Set postmeta `_kad_post_title: "hide"` |
