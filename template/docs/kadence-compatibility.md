# Kadence Blocks Compatibility & Terminology Guide (v1.1.0)

This guide documents the relationship between internal Gutenberg block slugs, modern Kadence block UI terminology in the editor, supported plugin versions, and theme compatibility.

---

## 1. Block Slug vs Gutenberg UI Name Mapping

Kadence Blocks has evolved its user-facing editor labels across major releases. To avoid confusion where modern UI names differ from historical block slugs, reference this canonical mapping:

| Internal Block Slug | Current Editor UI Name | Former UI Name | Primary Purpose / Notes |
|:---|:---|:---|:---|
| `kadence/advancedheading` | **Text (Adv)** | Advanced Heading | Headings (h1–h6), paragraphs, subheadings with typography & palette controls |
| `kadence/rowlayout` | **Row Layout** | Row Layout | Flexbox & CSS grid layout container; supports multi-column layouts |
| `kadence/column` | **Section / Column** | Column | Child container inside Row Layout; handles inner padding and borders |
| `kadence/advancedbtn` | **Advanced Buttons** | Advanced Buttons | Wrapper container for button clusters and alignment |
| `kadence/singlebtn` | **Single Button** | Button | Individual button with label, URL, icon, and hover states |
| `kadence/infobox` | **Info Box** | Info Box | Media-card pattern with icon/image, heading, text, and link |
| `kadence/accordion` | **Accordion** | Accordion | Collapsible FAQ container; manages active pane states |
| `kadence/pane` | **Accordion Pane** | Accordion Pane | Single collapsible drawer within an Accordion block |
| `kadence/tabs` | **Tabs** | Tabs | Tabbed content container (horizontal/vertical) |
| `kadence/tab` | **Tab** | Tab | Individual content panel inside a Tabs container |
| `kadence/image` | **Advanced Image** | Advanced Image | Responsive image with ratio preservation, lightbox, and filters |
| `kadence/icon` | **Icon** | Icon | SVG icon display with size, color, and background controls |
| `kadence/iconlist` | **Icon List** | Icon List | Unordered list with customizable bullet icons |
| `kadence/spacer` | **Spacer / Divider** | Spacer/Divider | Responsive vertical spacing or stylized visual divider line |
| `kadence/testimonials`| **Testimonials** | Testimonials | Testimonial slider or grid layout container |
| `kadence/form` | **Form** | Form | Contact or lead-generation form (free/pro) |

> **Note for AI Agents**: Never invent block slugs. Even though the UI says "Text (Adv)", the underlying Gutenberg block slug in `post_content` is strictly `kadence/advancedheading`.

---

## 2. Version Compatibility Matrix

| Component | Tested Version Range | Status | Key Considerations |
|:---|:---|:---:|:---|
| **WordPress Core** | 6.2 – 6.7+ | ✅ Supported | Full support for Gutenberg block grammar and REST API v2 |
| **Kadence Blocks (Free)** | 3.2.0 – 3.4.x | ✅ Supported | Primary target. Requires `kbVersion: 2` attribute on Row & Column |
| **Kadence Blocks (Legacy)**| 3.0.0 – 3.1.x | ⚠️ Caution | Legacy flex styles; avoid older container attributes |
| **Kadence Blocks Pro** | 2.1.0 – 2.4.x | ✅ Supported | Enables query loops, dynamic content, and advanced modal blocks |
| **Kadence Blocks 4.x** | *Roadmap* | 🔍 Planned | Will be tested upon official beta release |

---

## 3. Deprecated Blocks & Migration Guide

| Deprecated Block | Current Native Replacement | Reason / Migration Path |
|:---|:---|:---|
| `kadence/row-layout` (hyphenated) | `kadence/rowlayout` (unhyphenated) | Slug standardized in Kadence v3.0+. Old slug causes block invalidation. |
| `core/columns` | `kadence/rowlayout` | Kadence row layouts provide fine-grained responsive controls and global palette integration. |
| `core/heading` / `core/paragraph` | `kadence/advancedheading` | Standardize on Advanced Heading for consistent palette variable binding. |
| `core/button` | `kadence/advancedbtn` + `kadence/singlebtn` | Native Kadence buttons support theme hover states and theme button radius tokens. |

---

## 4. Theme Compatibility

### Kadence Theme (Native)
- Full integration with Customizer Global Palette (`theme-palette1` through `theme-palette9`).
- Content width managed via `content_width` token (default `1290px`).
- Inherits typography variables directly from Customizer.

### Third-Party Themes (Astra, GeneratePress, Twenty Twenty-Four)
- Kadence Blocks operates independently of the active theme.
- Global palette CSS classes (`has-theme-palette-N-color`) may require CSS fallback variable definitions in child theme `style.css` if the theme does not supply standard Kadence palette variables.
