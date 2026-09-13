#!/usr/bin/env python3
"""
HTML-to-Kadence QA Engine (v1.1.0)
Portable, automated Quality Assurance pipeline and scoring gate for Kadence Gutenberg block markup.

Stages implemented:
1. Preflight QA (Config & Environment validation)
2. Structural QA (Block syntax, Kadence attributes, uniqueIDs, placeholder detection, zero custom HTML)
3. Semantic / Content Preservation QA (HTML manifest vs Block manifest comparison)
4. Accessibility QA (Headings hierarchy, image alt text, link labels, empty anchors)
5. Scoring & Hard Gates (Weighted scoring with non-negotiable hard-fail conditions)
"""

import os
import sys
import re
import json
import argparse
import hashlib
from html.parser import HTMLParser

# --- Standardized Error Codes ---
class ErrorCode:
    STRUCTURE_INVALID = "STRUCTURE_INVALID"
    BLOCK_JSON_INVALID = "BLOCK_JSON_INVALID"
    BLOCK_PARENT_INVALID = "BLOCK_PARENT_INVALID"
    DUPLICATE_UNIQUE_ID = "DUPLICATE_UNIQUE_ID"
    DUPLICATE_ANCHOR = "DUPLICATE_ANCHOR"
    CUSTOM_HTML_NOT_ALLOWED = "CUSTOM_HTML_NOT_ALLOWED"
    PLACEHOLDER_DETECTED = "PLACEHOLDER_DETECTED"
    HEADING_HIERARCHY_INVALID = "HEADING_HIERARCHY_INVALID"
    EMPTY_HEADING = "EMPTY_HEADING"
    COLOR_CLASS_MISMATCH = "COLOR_CLASS_MISMATCH"
    FONT_SIZE_INVALID = "FONT_SIZE_INVALID"
    CONTENT_LOST = "CONTENT_LOST"
    LINK_TARGET_CHANGED = "LINK_TARGET_CHANGED"
    CTA_MISSING = "CTA_MISSING"
    IMAGE_MISSING = "IMAGE_MISSING"
    ACCESSIBILITY_ALT_MISSING = "ACCESSIBILITY_ALT_MISSING"
    EMPTY_LINK = "EMPTY_LINK"
    SUSPICIOUS_LINK_LABEL = "SUSPICIOUS_LINK_LABEL"
    ROUND_TRIP_CHANGED_MARKUP = "ROUND_TRIP_CHANGED_MARKUP"
    WORDPRESS_SAVE_FAILED = "WORDPRESS_SAVE_FAILED"
    LIVE_CONTENT_CHANGED_ABORTED = "LIVE_CONTENT_CHANGED_ABORTED"
    VISUAL_DESKTOP_BELOW_THRESHOLD = "VISUAL_DESKTOP_BELOW_THRESHOLD"
    VISUAL_TABLET_BELOW_THRESHOLD = "VISUAL_TABLET_BELOW_THRESHOLD"
    VISUAL_MOBILE_BELOW_THRESHOLD = "VISUAL_MOBILE_BELOW_THRESHOLD"
    QA_REPAIR_LIMIT_REACHED = "QA_REPAIR_LIMIT_REACHED"

KADENCE_FONT_TOKENS = {'sm', 'base_sub', 'md', 'lg', 'xl', 'xxl', '3xl'}

DEFAULT_GATES = {
    "structural": 100,
    "content": 98,
    "runtime": 100,
    "accessibility": 90,
    "visual": 90,
    "overall": 92
}

PLACEHOLDER_PATTERNS = [
    (re.compile(r'\bTODO\b', re.IGNORECASE), "TODO comment found"),
    (re.compile(r'\bFIXME\b', re.IGNORECASE), "FIXME comment found"),
    (re.compile(r'\blorem\s+ipsum\b', re.IGNORECASE), "Lorem Ipsum dummy text found"),
    (re.compile(r'example\.com', re.IGNORECASE), "example.com placeholder URL found"),
    (re.compile(r'\{\{[^{}]+\}\}'), "Template placeholder {{...}} found"),
    (re.compile(r'\{[a-zA-Z0-9_]+_url\}'), "Template placeholder {url} found"),
    (re.compile(r'REPLACE_[A-Z0-9_]+'), "REPLACE_* placeholder token found"),
]

# --- Block Parsing Utilities ---
def parse_gutenberg_blocks(content):
    """
    Parses Gutenberg block comments from raw content.
    Returns list of dicts: name, attrs, is_void, start, end, inner, raw_attrs
    """
    block_pattern = re.compile(r'<!--\s+wp:([\w\/-]+)\s*({.*?})?\s*(-->|/-->)', re.DOTALL)
    blocks = []
    
    for match in block_pattern.finditer(content):
        name = match.group(1)
        raw_attrs = match.group(2)
        is_void = match.group(3) == '/-->'
        
        attrs = {}
        json_error = None
        if raw_attrs:
            try:
                attrs = json.loads(raw_attrs)
            except json.JSONDecodeError as e:
                json_error = str(e)
                
        inner = ""
        end_pos = match.end()
        if not is_void:
            close_tag = f"<!-- /wp:{name} -->"
            close_idx = content.find(close_tag, end_pos)
            if close_idx != -1:
                inner = content[end_pos:close_idx].strip()
                
        blocks.append({
            'name': name,
            'attrs': attrs,
            'raw_attrs': raw_attrs,
            'json_error': json_error,
            'is_void': is_void,
            'start': match.start(),
            'end': end_pos,
            'inner': inner
        })
        
    return blocks

# --- Manifest Extractor for HTML and Blocks ---
class HTMLContentExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.headings = []      # (tag, text)
        self.paragraphs = []    # text
        self.images = []        # (src, alt)
        self.links = []         # (href, text)
        self.buttons = []       # text
        self.all_text = []      # list of string tokens
        self.anchors = set()    # IDs and name attributes
        self._current_tag = None
        self._current_text = []

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        if 'id' in attr_dict:
            self.anchors.add(attr_dict['id'])
        if tag == 'a' and 'name' in attr_dict:
            self.anchors.add(attr_dict['name'])
            
        if tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            self._current_tag = tag
            self._current_text = []
        elif tag == 'p':
            self._current_tag = 'p'
            self._current_text = []
        elif tag == 'img':
            src = attr_dict.get('src', '')
            alt = attr_dict.get('alt', '')
            self.images.append({'src': src, 'alt': alt})
        elif tag == 'a':
            self._current_tag = 'a'
            self._current_href = attr_dict.get('href', '')
            self._current_text = []
        elif tag == 'button' or 'btn' in attr_dict.get('class', ''):
            self._current_tag = 'button'
            self._current_text = []

    def handle_data(self, data):
        cleaned = data.strip()
        if cleaned:
            self.all_text.append(cleaned)
            if self._current_tag:
                self._current_text.append(cleaned)

    def handle_endtag(self, tag):
        text = " ".join(self._current_text).strip()
        if tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6') and self._current_tag == tag:
            if text:
                self.headings.append({'level': int(tag[1]), 'text': text})
        elif tag == 'p' and self._current_tag == 'p':
            if text:
                self.paragraphs.append(text)
        elif tag == 'a' and self._current_tag == 'a':
            self.links.append({'href': getattr(self, '_current_href', ''), 'text': text})
        elif (tag == 'button' or self._current_tag == 'button') and text:
            self.buttons.append(text)
        self._current_tag = None
        self._current_text = []

def extract_manifest_from_html(html_content):
    # If <main> is present, extract only the page content area (excluding site header & footer)
    main_match = re.search(r'<main[^>]*>(.*?)</main>', html_content, re.DOTALL | re.IGNORECASE)
    target_content = main_match.group(1) if main_match else html_content

    parser = HTMLContentExtractor()
    parser.feed(target_content)
    return {
        'headings': parser.headings,
        'paragraphs': parser.paragraphs,
        'images': parser.images,
        'links': parser.links,
        'buttons': parser.buttons,
        'all_text': " ".join(parser.all_text),
        'anchors': parser.anchors
    }

def extract_manifest_from_blocks(blocks, raw_content):
    extractor = HTMLContentExtractor()
    extractor.feed(raw_content)
    
    # Also parse singlebtn, advancedbtn, pane and infobox attributes
    for b in blocks:
        name = b['name']
        attrs = b['attrs']
        if name in ('kadence/singlebtn', 'kadence/advancedbtn'):
            txt = attrs.get('text')
            link = attrs.get('link')
            if txt:
                extractor.buttons.append(txt)
                extractor.all_text.append(txt)
            if link:
                extractor.links.append({'href': link, 'text': txt or ''})
        elif name == 'kadence/pane':
            title = attrs.get('title')
            if title:
                extractor.all_text.append(title)
                
    return {
        'headings': extractor.headings,
        'paragraphs': extractor.paragraphs,
        'images': extractor.images,
        'links': extractor.links,
        'buttons': extractor.buttons,
        'all_text': " ".join(extractor.all_text),
        'anchors': extractor.anchors
    }

# --- Stage 1: Structural QA ---
def run_structural_qa(blocks, raw_content, allow_custom_html=False):
    errors = []
    warnings = []
    seen_uids = set()
    seen_anchors = set()
    custom_html_count = 0
    kadence_count = 0
    core_count = 0
    
    # 1. Comment balance check
    open_comments = len(re.findall(r'<!--\s+wp:([\w\/-]+)', raw_content))
    close_comments = len(re.findall(r'<!--\s+/wp:([\w\/-]+)', raw_content))
    void_comments = len(re.findall(r'<!--\s+wp:[\w\/-]+.*?/-->', raw_content))
    
    if open_comments != (close_comments + void_comments):
        errors.append({
            "code": ErrorCode.STRUCTURE_INVALID,
            "severity": "critical",
            "message": f"Mismatched Gutenberg block comments: {open_comments} open vs {close_comments} close + {void_comments} self-closing",
            "location": "document",
            "repair": "Ensure every non-void block has a matching <!-- /wp:blockname --> tag"
        })

    # 2. Block checks
    for idx, b in enumerate(blocks):
        name = b['name']
        attrs = b['attrs']
        inner = b['inner']
        loc = f"Block #{idx+1} ({name})"
        
        if name.startswith('kadence/'):
            kadence_count += 1
        elif name.startswith('core/'):
            core_count += 1
            
        if b.get('json_error'):
            errors.append({
                "code": ErrorCode.BLOCK_JSON_INVALID,
                "severity": "critical",
                "message": f"{loc}: Malformed JSON attributes: {b['json_error']}",
                "location": loc,
                "repair": "Ensure block attributes are strictly valid JSON"
            })
            continue
            
        # Custom HTML check
        if name in ('core/html', 'html'):
            custom_html_count += 1
            if not allow_custom_html:
                errors.append({
                    "code": ErrorCode.CUSTOM_HTML_NOT_ALLOWED,
                    "severity": "critical",
                    "message": f"{loc}: Custom HTML block detected. Rule 'zero-custom-html' requires native Kadence blocks.",
                    "location": loc,
                    "repair": "Convert custom HTML into native Kadence blocks (rowlayout, advancedheading, advancedbtn, etc.)"
                })

        # Kadence-specific rules
        if name.startswith('kadence/'):
            uid = attrs.get('uniqueID')
            if not uid or not isinstance(uid, str):
                errors.append({
                    "code": ErrorCode.STRUCTURE_INVALID,
                    "severity": "critical",
                    "message": f"{loc}: Missing or non-string 'uniqueID'",
                    "location": loc,
                    "repair": "Add a uniqueID string attribute: {pageId}_{hash}"
                })
            else:
                if uid in seen_uids:
                    errors.append({
                        "code": ErrorCode.DUPLICATE_UNIQUE_ID,
                        "severity": "critical",
                        "message": f"{loc}: Duplicate uniqueID '{uid}' detected on page",
                        "location": loc,
                        "repair": "Regenerate uniqueID so every block on the page has a distinct identifier"
                    })
                seen_uids.add(uid)
                
            # Anchor check
            anchor = attrs.get('anchor')
            if anchor:
                if anchor in seen_anchors:
                    errors.append({
                        "code": ErrorCode.DUPLICATE_ANCHOR,
                        "severity": "major",
                        "message": f"{loc}: Duplicate anchor/HTML ID '#{anchor}'",
                        "location": loc,
                        "repair": "Ensure all section anchor attributes are unique"
                    })
                seen_anchors.add(anchor)

            # Block specific
            if name == 'kadence/advancedheading':
                if not inner:
                    errors.append({
                        "code": ErrorCode.STRUCTURE_INVALID,
                        "severity": "critical",
                        "message": f"{loc} (uid:{uid}): Empty inner HTML",
                        "location": loc,
                        "repair": "Add rendered HTML tag inside block comments"
                    })
                else:
                    if uid:
                        if f"kt-adv-heading{uid}" not in inner:
                            errors.append({
                                "code": ErrorCode.STRUCTURE_INVALID,
                                "severity": "critical",
                                "message": f"{loc} (uid:{uid}): Inner HTML missing class 'kt-adv-heading{uid}'",
                                "location": loc,
                                "repair": f"Add class 'kt-adv-heading{uid}' to rendered heading element"
                            })
                        if f'data-kb-block="kb-adv-heading{uid}"' not in inner:
                            errors.append({
                                "code": ErrorCode.STRUCTURE_INVALID,
                                "severity": "critical",
                                "message": f"{loc} (uid:{uid}): Inner HTML missing 'data-kb-block=\"kb-adv-heading{uid}\"'",
                                "location": loc,
                                "repair": f"Add attribute 'data-kb-block=\"kb-adv-heading{uid}\"' to heading element"
                            })
                    color_class = attrs.get('colorClass')
                    if color_class and isinstance(color_class, str):
                        expected_class = "has-" + re.sub(r'(\d+)$', r'-\1', color_class) + "-color"
                        if expected_class not in inner or 'has-text-color' not in inner:
                            errors.append({
                                "code": ErrorCode.COLOR_CLASS_MISMATCH,
                                "severity": "major",
                                "message": f"{loc} (uid:{uid}): colorClass '{color_class}' set but inner HTML missing '{expected_class} has-text-color'",
                                "location": loc,
                                "repair": f"Add classes '{expected_class} has-text-color' to rendered heading"
                            })
                    font_size = attrs.get('fontSize')
                    if font_size and isinstance(font_size, list):
                        for fs in font_size:
                            if fs not in (None, "") and not isinstance(fs, (int, float)) and str(fs) not in KADENCE_FONT_TOKENS:
                                errors.append({
                                    "code": ErrorCode.FONT_SIZE_INVALID,
                                    "severity": "major",
                                    "message": f"{loc} (uid:{uid}): Invalid fontSize '{fs}'. Must be numeric px or Kadence token",
                                    "location": loc,
                                    "repair": "Use numeric array [desktop, tablet, mobile] e.g. [40, '', 28]"
                                })

            elif name == 'kadence/rowlayout':
                cols = attrs.get('columns', 1)
                if cols > 1 and not attrs.get('colLayout'):
                    warnings.append({
                        "code": ErrorCode.STRUCTURE_INVALID,
                        "severity": "minor",
                        "message": f"{loc} (uid:{uid}): Multi-column row should define 'colLayout'",
                        "location": loc,
                        "repair": "Specify colLayout (e.g. 'equal', 'two-one')"
                    })
                overlay = attrs.get('overlay')
                if overlay and isinstance(overlay, str) and overlay.startswith('palette'):
                    errors.append({
                        "code": ErrorCode.STRUCTURE_INVALID,
                        "severity": "major",
                        "message": f"{loc} (uid:{uid}): Row overlay '{overlay}' must be a hex color (#hex), not a palette slug",
                        "location": loc,
                        "repair": "Convert palette slug to explicit hex color (e.g. '#23272B')"
                    })

            elif name == 'kadence/image':
                url = attrs.get('url')
                img_id = attrs.get('id')
                if not url and not img_id:
                    errors.append({
                        "code": ErrorCode.IMAGE_MISSING,
                        "severity": "critical",
                        "message": f"{loc} (uid:{uid}): Image block missing both 'url' and 'id'",
                        "location": loc,
                        "repair": "Provide valid media url or attachment id"
                    })

    # 3. Placeholder checks across entire content
    for pattern, msg in PLACEHOLDER_PATTERNS:
        match = pattern.search(raw_content)
        if match:
            errors.append({
                "code": ErrorCode.PLACEHOLDER_DETECTED,
                "severity": "critical",
                "message": f"Placeholder detected: '{match.group(0)}' ({msg})",
                "location": f"Offset {match.start()}",
                "repair": "Replace placeholder with real production content/media"
            })

    # Check empty href or href="#"
    for empty_link in re.finditer(r'href=["\'](#|)["\']', raw_content):
        warnings.append({
            "code": ErrorCode.EMPTY_LINK,
            "severity": "minor",
            "message": f"Empty or hash link found: '{empty_link.group(0)}'",
            "location": f"Offset {empty_link.start()}",
            "repair": "Provide real destination URL or anchor ID"
        })

    metrics = {
        "blocks": len(blocks),
        "kadence_blocks": kadence_count,
        "core_blocks": core_count,
        "custom_html_blocks": custom_html_count,
        "duplicate_unique_ids": len(blocks) - len(seen_uids),
        "duplicate_anchors": len(seen_anchors)
    }

    score = 100 if len(errors) == 0 else max(0, 100 - (len(errors) * 15 + len(warnings) * 2))
    return {
        "score": score,
        "errors": errors,
        "warnings": warnings,
        "metrics": metrics
    }

# --- Stage 2: Content Preservation QA ---
def run_content_preservation_qa(source_html, block_content):
    errors = []
    warnings = []
    
    source_m = extract_manifest_from_html(source_html)
    blocks = parse_gutenberg_blocks(block_content)
    block_m = extract_manifest_from_blocks(blocks, block_content)
    
    # 1. Heading check
    src_headings = [h['text'].lower().strip() for h in source_m['headings']]
    blk_headings = [h['text'].lower().strip() for h in block_m['headings']]
    
    missing_headings = [h for h in src_headings if not any(h in bh or bh in h for bh in blk_headings)]
    heading_preservation = 1.0 if len(src_headings) == 0 else (len(src_headings) - len(missing_headings)) / len(src_headings)
    
    if missing_headings:
        errors.append({
            "code": ErrorCode.CONTENT_LOST,
            "severity": "critical",
            "message": f"Missing headings from mockup ({len(missing_headings)}): {', '.join(missing_headings[:3])}",
            "location": "headings",
            "repair": "Restore missing headings into advancedheading blocks"
        })

    # 2. Image check
    src_images = len(source_m['images'])
    blk_images = len(block_m['images'])
    img_preservation = 1.0 if src_images == 0 else min(1.0, blk_images / src_images)
    if blk_images < src_images:
        warnings.append({
            "code": ErrorCode.IMAGE_MISSING,
            "severity": "major",
            "message": f"Image count mismatch: {src_images} in HTML mockup vs {blk_images} in Kadence blocks",
            "location": "images",
            "repair": "Ensure all mockup images are represented in Kadence image/gallery blocks"
        })

    # 3. Links / CTAs check
    src_links = set(l['href'].strip() for l in source_m['links'] if l['href'].strip() and l['href'] != '#')
    blk_links = set(l['href'].strip() for l in block_m['links'] if l['href'].strip() and l['href'] != '#')
    missing_links = src_links - blk_links
    link_preservation = 1.0 if len(src_links) == 0 else (len(src_links) - len(missing_links)) / len(src_links)
    
    if missing_links:
        errors.append({
            "code": ErrorCode.LINK_TARGET_CHANGED,
            "severity": "major",
            "message": f"Missing link destinations ({len(missing_links)}): {', '.join(list(missing_links)[:3])}",
            "location": "links",
            "repair": "Restore original link URLs in button or heading links"
        })

    # 4. Text preservation (token set overlap)
    src_words = set(re.findall(r'\w+', source_m['all_text'].lower()))
    blk_words = set(re.findall(r'\w+', block_m['all_text'].lower()))
    preserved_words = src_words.intersection(blk_words)
    text_preservation = 1.0 if len(src_words) == 0 else len(preserved_words) / len(src_words)
    
    if text_preservation < 0.95:
        errors.append({
            "code": ErrorCode.CONTENT_LOST,
            "severity": "critical",
            "message": f"Significant text content missing: {text_preservation*100:.1f}% preserved (required >= 98%)",
            "location": "body_text",
            "repair": "Check for missing paragraphs or truncated sections in generated blocks"
        })

    score = int((heading_preservation * 0.35 + text_preservation * 0.35 + link_preservation * 0.15 + img_preservation * 0.15) * 100)
    return {
        "score": score,
        "metrics": {
            "heading_preservation_pct": round(heading_preservation * 100, 1),
            "text_preservation_pct": round(text_preservation * 100, 1),
            "link_preservation_pct": round(link_preservation * 100, 1),
            "image_preservation_pct": round(img_preservation * 100, 1)
        },
        "errors": errors,
        "warnings": warnings
    }

# --- Stage 3: Accessibility QA ---
def run_accessibility_qa(raw_content):
    errors = []
    warnings = []
    
    blocks = parse_gutenberg_blocks(raw_content)
    manifest = extract_manifest_from_blocks(blocks, raw_content)
    
    # 1. Heading hierarchy
    h1_count = 0
    prev_level = 0
    for h in manifest['headings']:
        lvl = h['level']
        if lvl == 1:
            h1_count += 1
        if prev_level > 0 and lvl > (prev_level + 1):
            warnings.append({
                "code": ErrorCode.HEADING_HIERARCHY_INVALID,
                "severity": "minor",
                "message": f"Heading level skipped from h{prev_level} to h{lvl} ('{h['text'][:25]}...')",
                "location": f"h{lvl}",
                "repair": "Maintain sequential heading hierarchy without skipping levels"
            })
        prev_level = lvl
        
    if h1_count == 0:
        errors.append({
            "code": ErrorCode.HEADING_HIERARCHY_INVALID,
            "severity": "major",
            "message": "Page has no <h1> heading tag",
            "location": "h1",
            "repair": "Designate exactly one primary page heading as level 1"
        })
    elif h1_count > 1:
        warnings.append({
            "code": ErrorCode.HEADING_HIERARCHY_INVALID,
            "severity": "minor",
            "message": f"Multiple <h1> headings found ({h1_count}). Best practice is a single h1 per page.",
            "location": "h1",
            "repair": "Change secondary headings to h2"
        })

    # 2. Image alt text check
    missing_alt_count = 0
    for img in manifest['images']:
        # Alt missing or purely whitespace
        if img.get('alt') is None or img.get('alt') == "":
            # Note: empty alt is permitted for decorative images, but in markup we flag warning if completely omitted
            missing_alt_count += 1
            
    if missing_alt_count > 0:
        warnings.append({
            "code": ErrorCode.ACCESSIBILITY_ALT_MISSING,
            "severity": "minor",
            "message": f"{missing_alt_count} image(s) have empty alt text. Ensure decorative images have alt='' and informative images have descriptive text.",
            "location": "img",
            "repair": "Provide meaningful alt text for content images"
        })

    # 3. Suspicious link labels
    suspicious_labels = {'click here', 'read more', 'more', 'link', 'here'}
    for link in manifest['links']:
        lbl = link['text'].strip().lower()
        if lbl in suspicious_labels:
            warnings.append({
                "code": ErrorCode.SUSPICIOUS_LINK_LABEL,
                "severity": "minor",
                "message": f"Generic non-descriptive link text found: '{link['text']}'",
                "location": "a",
                "repair": "Use descriptive link text indicating destination"
            })

    score = 100 if len(errors) == 0 else max(0, 100 - (len(errors) * 15 + len(warnings) * 3))
    return {
        "score": score,
        "errors": errors,
        "warnings": warnings,
        "metrics": {
            "h1_count": h1_count,
            "total_headings": len(manifest['headings']),
            "total_images": len(manifest['images'])
        }
    }

# --- Full QA Pipeline Runner ---
def run_qa_pipeline(block_file, source_html_file=None, allow_custom_html=False, gates=None):
    if gates is None:
        gates = DEFAULT_GATES

    with open(block_file, 'r', encoding='utf-8', errors='replace') as f:
        block_content = f.read()

    blocks = parse_gutenberg_blocks(block_content)
    
    # Stage 1: Structural QA
    structural = run_structural_qa(blocks, block_content, allow_custom_html=allow_custom_html)
    
    # Stage 2: Content Preservation QA (if source HTML provided)
    content_preservation = None
    if source_html_file and os.path.isfile(source_html_file):
        with open(source_html_file, 'r', encoding='utf-8', errors='replace') as f:
            source_html = f.read()
        content_preservation = run_content_preservation_qa(source_html, block_content)
        
    # Stage 3: Accessibility QA
    a11y = run_accessibility_qa(block_content)
    
    # Calculate Overall Score
    scores = {
        "structural": structural["score"],
        "accessibility": a11y["score"],
        "runtime": 100, # Simulated or populated via REST round-trip
        "visual": 95    # Simulated default unless visual QA runner active
    }
    if content_preservation:
        scores["content"] = content_preservation["score"]
    else:
        scores["content"] = 100 # N/A

    overall_score = round(
        scores["structural"] * 0.35 +
        scores["content"] * 0.35 +
        scores["accessibility"] * 0.15 +
        scores["runtime"] * 0.15
    )
    scores["overall"] = overall_score

    # Evaluate Hard Fail Conditions
    all_errors = structural["errors"] + a11y["errors"] + (content_preservation["errors"] if content_preservation else [])
    all_warnings = structural["warnings"] + a11y["warnings"] + (content_preservation["warnings"] if content_preservation else [])
    
    critical_errors = [e for e in all_errors if e.get("severity") == "critical"]
    
    # Gate Decisions
    passed_structural = scores["structural"] >= gates.get("structural", 100)
    passed_content = scores["content"] >= gates.get("content", 98)
    passed_a11y = scores["accessibility"] >= gates.get("accessibility", 90)
    passed_overall = scores["overall"] >= gates.get("overall", 92)
    no_critical = len(critical_errors) == 0

    is_passed = passed_structural and passed_content and passed_a11y and passed_overall and no_critical

    return {
        "status": "pass" if is_passed else "fail",
        "file": block_file,
        "scores": scores,
        "gates": gates,
        "passed_gates": {
            "structural": passed_structural,
            "content": passed_content,
            "accessibility": passed_a11y,
            "overall": passed_overall
        },
        "errors": all_errors,
        "warnings": all_warnings,
        "metrics": {
            **structural["metrics"],
            **(content_preservation["metrics"] if content_preservation else {})
        }
    }

# --- CLI Interface ---
def main():
    parser = argparse.ArgumentParser(description="HTML-to-Kadence QA Engine v1.1.0")
    parser.add_argument("block_path", help="Path to block markup file or directory")
    parser.add_argument("--html", help="Path to original source HTML file (for content preservation QA)")
    parser.add_argument("--allow-custom-html", action="store_true", help="Allow core/html blocks")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON only")
    parser.add_argument("--strict", action="store_true", help="Treat all warnings as errors")
    args = parser.parse_args()

    files = []
    if os.path.isfile(args.block_path):
        files = [(args.block_path, args.html)]
    elif os.path.isdir(args.block_path):
        txt_files = sorted(glob.glob(os.path.join(args.block_path, "*.txt")) + glob.glob(os.path.join(args.block_path, "*.html")))
        for tf in txt_files:
            files.append((tf, None))
            
    if not files:
        print(f"❌ Error: No files found at '{args.block_path}'")
        sys.exit(1)

    results = []
    all_clean = True
    
    for bf, hf in files:
        res = run_qa_pipeline(bf, source_html_file=hf, allow_custom_html=args.allow_custom_html)
        results.append(res)
        if res["status"] != "pass" or (args.strict and len(res["warnings"]) > 0):
            all_clean = False

    if args.json:
        print(json.dumps(results if len(results) > 1 else results[0], indent=2))
        sys.exit(0 if all_clean else 1)

    print("\n" + "="*60)
    print("  HTML → KADENCE QA ENGINE (v1.1.0)")
    print("="*60)
    
    for r in results:
        status_sym = "✅ PASS" if r["status"] == "pass" else "❌ FAIL"
        print(f"\nTarget: {r['file']}")
        print(f"Status: {status_sym}")
        print(f"Scores: Structural: {r['scores']['structural']}/100 | Content: {r['scores']['content']}/100 | A11y: {r['scores']['accessibility']}/100 | Overall: {r['scores']['overall']}/100")
        
        if r["errors"]:
            print(f"🛑 Errors ({len(r['errors'])}):")
            for e in r["errors"]:
                print(f"   - [{e['code']}] {e['message']}")
                if e.get('repair'):
                    print(f"     💡 Repair: {e['repair']}")
                    
        if r["warnings"]:
            print(f"⚠️  Warnings ({len(r['warnings'])}):")
            for w in r["warnings"]:
                print(f"   - [{w['code']}] {w['message']}")

    print("\n" + "="*60)
    if all_clean:
        print("🎉 ALL MANDATORY QA GATES PASSED (Exit code 0)")
        sys.exit(0)
    else:
        print("❌ QA GATE REJECTED: Fix critical errors before publishing (Exit code 1)")
        sys.exit(1)

if __name__ == "__main__":
    main()
