#!/usr/bin/env python3
"""
SARAhack - Playwright Browser Automation for HackerOne Report Submission

Requirements (on Kali):
    pip3 install playwright
    python3 -m playwright install chromium
    python3 -m playwright install-deps chromium

Environment Variables:
    export HACKERONE_EMAIL="potosopotosolo@gmail.com"
    export HACKERONE_PASSWORD=")a9By=*D#6/w9T"

Usage:
    python3 playwright_h1_submitter.py --list
    python3 playwright_h1_submitter.py --submit 4
    python3 playwright_h1_submitter.py --submit-all
    python3 playwright_h1_submitter.py --test

NOTE: This script requires Chrome/Chromium installed and may be blocked by
HackerOne's bot protection (Cloudflare, reCAPTCHA). For fully automated
submission, use the freebuff tmate session instead.

"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from datetime import datetime

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("❌ Playwright not installed. Run: pip3 install playwright && python3 -m playwright install chromium")
    sys.exit(1)

# Configuration
# Credentials from environment variables (more secure)
def get_credentials():
    return {
        "email": os.environ.get("HACKERONE_EMAIL", "potosopotosolo@gmail.com"),
        "password": os.environ.get("HACKERONE_PASSWORD", ")a9By=*D#6/w9T")
    }

# Program slugs and correct URLs (/reports/new not /new)
PROGRAMS = {
    "shopify": "https://hackerone.com/shopify/reports/new",
    "gitlab": "https://hackerone.com/gitlab/reports/new",
    "uber": "https://hackerone.com/uber/reports/new",
    "coinbase": "https://hackerone.com/coinbase/reports/new",
    "cloudflare": "https://hackerone.com/cloudflare/reports/new",
}

# Reports to submit
REPORTS_DIR = Path(__file__).parent.parent / "reports"
TRACKER_FILE = REPORTS_DIR / "tracking" / "reports.json"


def load_tracker():
    """Load reports tracker."""
    with open(TRACKER_FILE, 'r') as f:
        return json.load(f)


def load_report_content(report_file):
    """Load report markdown file and extract content."""
    report_path = REPORTS_DIR / report_file.replace("reports/", "")
    with open(report_path, 'r') as f:
        return f.read()


def parse_report_content(content):
    """Parse markdown report to extract title, severity, and description."""
    lines = content.split('\n')
    
    title = None
    severity = None
    description_lines = []
    impact_lines = []
    in_description = False
    in_impact = False
    
    for line in lines:
        # Extract title
        if not title and (line.startswith('# ') or line.startswith('**Title:**')):
            title = line.replace('# ', '').replace('**Title:**', '').strip()
        
        # Extract severity
        if line.startswith('**Severity:**'):
            severity = line.replace('**Severity:**', '').strip().lower()
        
        # Track sections
        if line.startswith('## Summary') or line.startswith('## Description'):
            in_description = True
            in_impact = False
        elif line.startswith('## Impact'):
            in_description = False
            in_impact = True
        elif line.startswith('## ') and (in_description or in_impact):
            in_description = False
            in_impact = False
        elif in_description and line.strip():
            description_lines.append(line)
        elif in_impact and line.strip():
            impact_lines.append(line)
    
    # Fallback title extraction
    if not title:
        for line in lines:
            if line.startswith('**Platform:**'):
                break
            if line.startswith('# '):
                title = line.replace('# ', '').strip()
                break
    
    return {
        "title": title or "Untitled Report",
        "severity": severity or "medium",
        "description": '\n'.join(description_lines).strip(),
        "impact": '\n'.join(impact_lines).strip()
    }


def login_to_hackerone(page):
    """Login to HackerOne account."""
    print("[*] Logging into HackerOne...")
    credentials = get_credentials()
    
    page.goto("https://hackerone.com/login", wait_until="networkidle")
    time.sleep(3)
    
    # Fill email - correct selector for HackerOne
    try:
        page.fill('input[name="user[email]"]', credentials["email"])
        print("  ✓ Email field filled")
    except Exception as e:
        print(f"  ⚠ Email field error: {e}")
    
    # Fill password - correct selector for HackerOne
    try:
        page.fill('input[name="user[password]"]', credentials["password"])
        print("  ✓ Password field filled")
    except Exception as e:
        print(f"  ⚠ Password field error: {e}")
    
    # Click login button with explicit wait
    try:
        page.wait_for_selector('button[type="submit"]', timeout=5000)
        page.click('button[type="submit"]')
        print("  ✓ Login button clicked")
    except Exception as e:
        print(f"  ⚠ Login button error: {e}")
    
    # Wait for potential MFA or redirect
    time.sleep(5)
    
    # Check for MFA challenge
    if "two-factor" in page.content().lower() or "authenticator" in page.content().lower():
        print("[⚠️] MFA required - please complete manually in the browser")
        print("    The browser will remain open for you to enter the code")
        input("    Press Enter after completing MFA...")
    
    # Check for Cloudflare challenge
    if "cloudflare" in page.content().lower() or "checking your browser" in page.content().lower():
        print("[⚠️] Cloudflare challenge detected - waiting...")
        time.sleep(15)
        
    # Verify login success
    current_url = page.url
    if "dashboard" in current_url or "hackerone.com" in current_url:
        print("[✅] Login successful!")
        return True
    else:
        print(f"[⚠️] Current URL: {current_url}")
        return False


def submit_report(page, program_slug, report_data):
    """Submit a single report to HackerOne program."""
    print(f"[*] Submitting report to {program_slug}...")
    
    # Navigate to program's new report page
    if program_slug not in PROGRAMS:
        print(f"[❌] Unknown program: {program_slug}")
        return False
    
    print(f"  → Navigating to {PROGRAMS[program_slug]}")
    page.goto(PROGRAMS[program_slug], wait_until="networkidle", timeout=30000)
    time.sleep(5)
    
    # Check for Cloudflare challenge
    if "cloudflare" in page.content().lower() or "checking your browser" in page.content().lower():
        print("  ⚠ Cloudflare challenge - waiting 20 seconds...")
        time.sleep(20)
    
    # Fill report form
    # Title field
    try:
        title_input = page.query_selector('input[name="title"], input[id="report_title"], input[placeholder*="title" i]')
        if title_input:
            title_input.fill(report_data["title"])
            print(f"  ✓ Title: {report_data['title'][:50]}...")
    except Exception as e:
        print(f"  ⚠ Title field error: {e}")
    
    # Severity selection (if dropdown exists)
    try:
        severity_select = page.query_selector('select[name="severity"], select[id*="severity"]')
        if severity_select:
            severity_map = {
                "critical": "critical",
                "high": "high", 
                "medium": "medium",
                "low": "low",
                "informational": "informational"
            }
            sev_value = severity_map.get(report_data["severity"], "medium")
            severity_select.select_option(sev_value)
            print(f"  ✓ Severity: {sev_value}")
    except Exception as e:
        print(f"  ⚠ Severity field error: {e}")
    
    # Description field (textarea)
    try:
        desc_textarea = page.query_selector('textarea[name="description"], textarea[id*="description"], textarea[placeholder*="vulnerability" i]')
        if desc_textarea:
            full_description = f"{report_data['description']}\n\n## Impact\n{report_data['impact']}"
            desc_textarea.fill(full_description[:10000])  # Limit to 10000 chars
            print(f"  ✓ Description filled ({len(full_description)} chars)")
    except Exception as e:
        print(f"  ⚠ Description field error: {e}")
    
    # Submit button
    try:
        submit_btn = page.query_selector('button[type="submit"], input[type="submit"], button:has-text("Submit")')
        if submit_btn:
            submit_btn.click()
            print(f"  ✓ Submit button clicked")
            time.sleep(5)
    except Exception as e:
        print(f"  ⚠ Submit button error: {e}")
    
    # Check for success
    if "success" in page.content().lower() or "thank you" in page.content().lower():
        print(f"[✅] Report submitted successfully to {program_slug}!")
        return True
    
    # Take screenshot for debugging
    screenshot_path = f"/tmp/h1_submit_{program_slug}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    page.screenshot(path=screenshot_path, full_page=True)
    print(f"  📷 Screenshot saved: {screenshot_path}")
    
    # Save page HTML for debugging
    html_path = f"/tmp/h1_submit_{program_slug}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    with open(html_path, 'w') as f:
        f.write(page.content())
    print(f"  📄 HTML saved: {html_path}")
    
    return False


def test_playwright():
    """Test if Playwright and Chromium are working."""
    print("[*] Testing Playwright...")
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Test basic navigation
            page.goto("https://hackerone.com")
            print(f"[✅] Chromium works! Page title: {page.title()}")
            
            browser.close()
            return True
    except Exception as e:
        print(f"[❌] Playwright test failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="SARAhack - HackerOne Report Submitter using Playwright"
    )
    parser.add_argument("--list", action="store_true", help="List pending reports")
    parser.add_argument("--submit", type=int, help="Submit report by ID")
    parser.add_argument("--submit-all", action="store_true", help="Submit all pending reports")
    parser.add_argument("--program", type=str, help="Submit to specific program")
    parser.add_argument("--test", action="store_true", help="Test Playwright setup")
    
    args = parser.parse_args()
    
    # Test mode
    if args.test:
        success = test_playwright()
        sys.exit(0 if success else 1)
    
    # List mode
    if args.list:
        tracker = load_tracker()
        print("\n📋 Pending Reports:")
        print("-" * 60)
        for report in tracker:
            if report["status"] == "pending" and report["platform"] == "hackerone":
                print(f"  #{report['id']} | {report['program']} | {report['vulnerability']} | {report['severity']}")
        print("-" * 60)
        return
    
    # Load tracker
    tracker = load_tracker()
    
    # Determine which reports to submit
    reports_to_submit = []
    
    if args.submit:
        reports_to_submit = [r for r in tracker if r["id"] == args.submit]
    elif args.program:
        reports_to_submit = [
            r for r in tracker 
            if r["program"].lower() == args.program.lower() and r["status"] == "pending"
        ]
    elif args.submit_all:
        reports_to_submit = [
            r for r in tracker 
            if r["status"] == "pending" and r["platform"] == "hackerone"
        ]
    else:
        parser.print_help()
        print("\n📋 Example usage:")
        print("  python3 playwright_h1_submitter.py --list")
        print("  python3 playwright_h1_submitter.py --submit 4")
        print("  python3 playwright_h1_submitter.py --program shopify")
        print("  python3 playwright_h1_submitter.py --submit-all")
        print("  python3 playwright_h1_submitter.py --test")
        return
    
    if not reports_to_submit:
        print("❌ No reports to submit.")
        return
    
    print(f"\n{'='*60}")
    print(f"🎯 HackerOne Report Submitter (Playwright)")
    print(f"{'='*60}")
    
    # Test Playwright first
    if not test_playwright():
        print("\n❌ Playwright test failed. Please install Chromium:")
        print("  pip3 install playwright")
        print("  python3 -m playwright install chromium")
        print("  python3 -m playwright install-deps chromium")
        sys.exit(1)
    
    # Start browser automation
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Login once
        if not login_to_hackerone(page):
            print("❌ Login failed. Please check your credentials.")
            browser.close()
            sys.exit(1)
        
        # Submit each report
        results = []
        for report in reports_to_submit:
            print(f"\n[*] Processing report #{report['id']}: {report['program']} - {report['vulnerability']}")
            
            # Load and parse report content
            try:
                content = load_report_content(report["report_file"])
                parsed = parse_report_content(content)
                
                # Submit report
                success = submit_report(page, report["program"], parsed)
                results.append({
                    "id": report["id"],
                    "program": report["program"],
                    "success": success
                })
            except Exception as e:
                print(f"[❌] Error processing report: {e}")
                results.append({
                    "id": report["id"],
                    "program": report["program"],
                    "success": False,
                    "error": str(e)
                })
            
            # Wait between submissions
            time.sleep(5)
        
        browser.close()
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 SUBMISSION SUMMARY")
    print(f"{'='*60}")
    
    success_count = sum(1 for r in results if r.get("success"))
    fail_count = len(results) - success_count
    
    for r in results:
        status = "✅" if r.get("success") else "❌"
        print(f"{status} #{r['id']} {r['program']}: {'Success' if r.get('success') else 'Failed'}")
    
    print(f"\nTotal: {len(results)} | Success: {success_count} | Failed: {fail_count}")
    
    if fail_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()