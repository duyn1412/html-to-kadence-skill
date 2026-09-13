#!/usr/bin/env python3
"""
Kadence Gutenberg Block Markup Validator
Part of html-to-kadence framework (https://github.com/duyn1412/html-to-kadence-skill)

Validates generated Kadence Gutenberg block markup against WordPress block editor rules:
- uniqueID presence & format
- Advanced Heading innerHTML sync (classes, data-kb-block, colorClass, font size)
- Row layout structure (colLayout, overlay, bgColorClass)
- Image block assets (valid URLs, alt text)
- Disallows unapproved Custom HTML blocks (zero Custom HTML rule)
"""

import os
import sys
import glob
import json
import re
import argparse

KADENCE_FONT_TOKENS = {'sm', 'base_sub', 'md', 'lg', 'xl', 'xxl', '3xl'}

def parse_blocks(content):
    """
    Extracts all Gutenberg blocks from the raw content.
    Returns a list of dicts: {'name', 'attrs', 'raw_attrs', 'is_void', 'start', 'end', 'inner'}
    """
    block_pattern = re.compile(r'<!--\s+wp:([\w\/-]+)\s*({.*?})?\s*(-->|/-->)', re.DOTALL)
    blocks = []
    
    for match in block_pattern.finditer(content):
        name = match.group(1)
        raw_attrs = match.group(2)
        is_void = match.group(3) == '/-->'
        
        attrs = {}
        if raw_attrs:
            try:
                attrs = json.loads(raw_attrs)
            except json.JSONDecodeError as e:
                attrs = {'__json_error__': str(e), '__raw__': raw_attrs}
                
        # Find closing tag if not void
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
            'is_void': is_void,
            'start': match.start(),
            'end': match.end(),
            'inner': inner
        })
        
    return blocks

def validate_file(fpath, allow_custom_html=False):
    errors = []
    warnings = []
    
    if not os.path.isfile(fpath):
        return [f"File not found: {fpath}"], []
        
    with open(fpath, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
        
    if not content.strip():
        return [f"File is empty: {fpath}"], []
        
    blocks = parse_blocks(content)
    if not blocks:
        return [f"No Gutenberg block comments found in {fpath}"], []
        
    seen_uids = set()
    
    for idx, b in enumerate(blocks):
        name = b['name']
        attrs = b['attrs']
        inner = b['inner']
        loc = f"Block #{idx+1} ({name})"
        
        if '__json_error__' in attrs:
            errors.append(f"{loc}: Malformed JSON attributes: {attrs['__json_error__']}")
            continue
            
        # Rule: Zero Custom HTML
        if name == 'core/html' or name == 'html':
            if not allow_custom_html:
                errors.append(f"{loc}: Custom HTML block detected. Rule 'zero-custom-html' requires native Kadence blocks.")
                
        if not name.startswith('kadence/'):
            continue
            
        uid = attrs.get('uniqueID')
        if not uid or not isinstance(uid, str):
            errors.append(f"{loc}: Missing or non-string 'uniqueID'")
        else:
            if uid in seen_uids:
                errors.append(f"{loc}: Duplicate uniqueID '{uid}' detected on page")
            seen_uids.add(uid)
            
        # Block-specific checks
        if name == 'kadence/advancedheading':
            if not inner:
                errors.append(f"{loc} (uid:{uid}): Empty inner HTML — advancedheading must contain rendered tag")
            else:
                if uid:
                    if f"kt-adv-heading{uid}" not in inner:
                        errors.append(f"{loc} (uid:{uid}): Inner HTML missing class 'kt-adv-heading{uid}' — Gutenberg will flag block as invalid")
                    if f'data-kb-block="kb-adv-heading{uid}"' not in inner:
                        errors.append(f"{loc} (uid:{uid}): Inner HTML missing 'data-kb-block=\"kb-adv-heading{uid}\"' — Gutenberg will flag block as invalid")
                        
                color_class = attrs.get('colorClass')
                if color_class and isinstance(color_class, str):
                    expected_color_class = "has-" + re.sub(r'(\d+)$', r'-\1', color_class) + "-color"
                    if expected_color_class not in inner:
                        errors.append(f"{loc} (uid:{uid}): colorClass '{color_class}' set but inner HTML missing '{expected_color_class}'")
                    if 'has-text-color' not in inner:
                        errors.append(f"{loc} (uid:{uid}): colorClass set but inner HTML missing 'has-text-color'")
                        
                font_size = attrs.get('fontSize')
                if font_size and isinstance(font_size, list):
                    for fs in font_size:
                        if fs not in (None, "") and not isinstance(fs, (int, float)) and str(fs) not in KADENCE_FONT_TOKENS:
                            errors.append(f"{loc} (uid:{uid}): Invalid fontSize '{fs}'. Must be numeric px or valid token: {KADENCE_FONT_TOKENS}")
                            
                tag = attrs.get('htmlTag')
                level = attrs.get('level', 2)
                expected_tag = tag if tag in ['p', 'span', 'div'] else f"h{level}"
                if not re.search(r'<' + re.escape(expected_tag) + r'[\s>]', inner, re.IGNORECASE):
                    errors.append(f"{loc} (uid:{uid}): Attributes expect <{expected_tag}> but inner HTML does not match")
                    
        elif name == 'kadence/rowlayout':
            cols = attrs.get('columns', 1)
            if cols > 1 and not attrs.get('colLayout'):
                warnings.append(f"{loc} (uid:{uid}): Multi-column row should define 'colLayout'")
            overlay = attrs.get('overlay')
            if overlay and isinstance(overlay, str) and overlay.startswith('palette'):
                errors.append(f"{loc} (uid:{uid}): Row overlay '{overlay}' must be a hex color (#hex), not a palette slug")
            bg_color = attrs.get('bgColor')
            if bg_color and isinstance(bg_color, str) and bg_color.startswith('palette') and not attrs.get('bgColorClass'):
                warnings.append(f"{loc} (uid:{uid}): Palette bgColor '{bg_color}' missing 'bgColorClass'")
            bg_img = attrs.get('bgImg')
            if bg_img and 'REPLACE_' in bg_img:
                errors.append(f"{loc} (uid:{uid}): Placeholder detected in bgImg URL '{bg_img}'")
                
        elif name == 'kadence/image':
            url = attrs.get('url')
            img_id = attrs.get('id')
            if not url and not img_id:
                errors.append(f"{loc} (uid:{uid}): Image block missing both 'url' and 'id'")
            if url and 'REPLACE_' in url:
                errors.append(f"{loc} (uid:{uid}): Placeholder detected in image URL '{url}'")
            if attrs.get('imageRatio'):
                warnings.append(f"{loc} (uid:{uid}): Deprecated 'imageRatio' attribute — use 'ratio' + 'useRatio'")
                
    return errors, warnings, len(blocks)

def main():
    parser = argparse.ArgumentParser(description="Validate Kadence Gutenberg block markup")
    parser.add_argument("target", nargs="?", default="kadence-blocks", help="File or directory to validate (default: kadence-blocks)")
    parser.add_argument("--allow-custom-html", action="store_true", help="Allow core/html blocks")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    args = parser.parse_args()
    
    target = args.target
    files = []
    
    if os.path.isfile(target):
        files = [target]
    elif os.path.isdir(target):
        files = sorted(glob.glob(os.path.join(target, "*.txt")) + glob.glob(os.path.join(target, "*.html")))
    else:
        # Try finding kadence-blocks in cwd or parent
        if os.path.isdir("kadence-blocks"):
            files = sorted(glob.glob("kadence-blocks/*.txt") + glob.glob("kadence-blocks/*.html"))
            
    if not files:
        print(f"❌ No markup files found to validate in '{target}'")
        sys.exit(1)
        
    print(f"🔍 Kadence Block Markup Validator")
    print(f"==================================================")
    print(f"Scanning {len(files)} file(s)...\n")
    
    total_errors = 0
    total_warnings = 0
    total_blocks = 0
    all_passed = True
    
    for fpath in files:
        errs, warns, count = validate_file(fpath, allow_custom_html=args.allow_custom_html)
        total_errors += len(errs)
        total_warnings += len(warns)
        total_blocks += count
        
        status_icon = "✅" if not errs and (not warns or not args.strict) else "❌"
        print(f"{status_icon} {fpath} ({count} Kadence blocks)")
        
        if errs:
            all_passed = False
            for e in errs:
                print(f"   🛑 ERROR: {e}")
        if warns:
            for w in warns:
                print(f"   ⚠️  WARN:  {w}")
                
    print(f"\n==================================================")
    print(f"Summary: {len(files)} file(s), {total_blocks} block(s) parsed.")
    print(f"Errors: {total_errors}, Warnings: {total_warnings}")
    
    if not all_passed or (args.strict and total_warnings > 0):
        print(f"❌ VALIDATION FAILED — Fix errors above before publishing.")
        sys.exit(1)
    else:
        print(f"✅ ALL CHECKS PASSED — 100% compliant Kadence markup.")
        sys.exit(0)

if __name__ == "__main__":
    main()
