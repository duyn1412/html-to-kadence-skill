#!/usr/bin/env python3
"""
HTML-to-Kadence Regression Test Runner (v1.1.0)
Validates QA Engine against PASS and intentional FAIL test fixtures.
"""

import os
import sys
import glob
import json
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
FIXTURES_DIR = os.path.join(REPO_ROOT, "tests", "fixtures")
QA_ENGINE = os.path.join(SCRIPT_DIR, "qa-engine.py")

def run_fixture_test(fixture_path):
    name = os.path.basename(fixture_path)
    expected_file = os.path.join(fixture_path, "expected.json")
    blocks_file = os.path.join(fixture_path, "blocks.txt")
    html_file = os.path.join(fixture_path, "input.html")
    
    if not os.path.isfile(expected_file) or not os.path.isfile(blocks_file):
        return None, f"Missing expected.json or blocks.txt in {name}"
        
    with open(expected_file, 'r', encoding='utf-8') as f:
        expected = json.load(f)
        
    cmd = [sys.executable, QA_ENGINE, blocks_file, "--json"]
    if os.path.isfile(html_file):
        cmd.extend(["--html", html_file])
        
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    try:
        actual = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return False, f"Invalid JSON output from qa-engine: {proc.stdout} {proc.stderr}"
        
    expected_status = expected.get("status")
    actual_status = actual.get("status")
    
    if expected_status != actual_status:
        return False, f"Status mismatch: expected '{expected_status}', got '{actual_status}'"
        
    expected_errors = expected.get("expected_errors", [])
    actual_error_codes = [e.get("code") for e in actual.get("errors", [])]
    
    for exp_err in expected_errors:
        if exp_err not in actual_error_codes:
            return False, f"Expected error code '{exp_err}' not found in actual errors: {actual_error_codes}"
            
    return True, "OK"

def main():
    fixtures = sorted(glob.glob(os.path.join(FIXTURES_DIR, "*")))
    if not fixtures:
        print(f"No fixtures found in {FIXTURES_DIR}")
        sys.exit(1)
        
    print(f"🧪 Running HTML-to-Kadence Regression Suite (v1.1.0)")
    print(f"==================================================")
    print(f"Found {len(fixtures)} test fixture(s)...\n")
    
    passed = 0
    failed = 0
    
    for f in fixtures:
        if not os.path.isdir(f):
            continue
        fname = os.path.basename(f)
        success, msg = run_fixture_test(f)
        if success:
            print(f"✅ PASS: {fname}")
            passed += 1
        else:
            print(f"❌ FAIL: {fname} — {msg}")
            failed += 1
            
    print(f"\n==================================================")
    print(f"Results: {passed} passed, {failed} failed out of {len(fixtures)} tests.")
    
    if failed > 0:
        print(f"❌ Test suite FAILED")
        sys.exit(1)
    else:
        print(f"🎉 All regression tests PASSED!")
        sys.exit(0)

if __name__ == "__main__":
    main()
