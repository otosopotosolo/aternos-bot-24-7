#!/usr/bin/env python3
"""
SARAhack - HackerOne Report Submit via Playwright
Uses server's chromium browser to bypass Cloudflare
"""

import argparse
import sys
import os
from pathlib import Path

def submit_report(platform: str, program: str, report_file: str, email: str, password: str):
    """Submit bug bounty report using Playwright"""
    
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("[-] Playwright not installed. Run: pip3 install playwright")
        return False
    
    report_path = Path(report_file)
    if not report_path.exists():
        print(f"[-] Report file not found: {report_file}")
        return False
    
    with open(report_path, 'r') as f:
        report_content = f.read()
    
    # Parse report for title
    lines = report_content.split('\n')
    title = f"{program} - Vulnerability Report"
    severity = "High"
    
    # Extract title from report if it has one
    for line in lines:
        if line.startswith('**Program:**'):
            program_name = line.split('**Program:**')[1].strip()
            title = f"{program_name} - Security Report"
        if line.startswith('**Severity:**'):
            severity = line.split('**Severity:**')[1].strip()
    
    print(f"[*] Platform: {platform}")
    print(f"[*] Program: {program}")
    print(f"[*] Report: {report_file}")
    print(f"[*] Title: {title}")
    print(f"[*] Severity: {severity}")
    
    with sync_playwright() as p:
        # Launch browser with anti-detection settings
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]
        )
        
        context = browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        page = context.new_page()
        
        # Navigate to login
        print("[*] Navigating to HackerOne...")
        page.goto("https://hackerone.com/users/sign_in")
        page.wait_for_load_state("networkidle")
        
        # Check if already logged in
        if page.url.endswith("/users/sign_in"):
            print("[*] Logging in...")
            page.fill('input[name="user[email]"]', email)
            page.fill('input[name="user[password]"]', password)
            page.click('button[type="submit"]')
            page.wait_for_load_state("networkidle")
            print("[+] Login submitted")
        
        # Navigate to program
        print(f"[*] Navigating to {program} program...")
        page.goto(f"https://hackerone.com/{program}/reports/new")
        page.wait_for_load_state("networkidle")
        
        # Wait for form to load
        page.wait_for_selector('textarea[name*="report"]', timeout=10000)
        
        # Fill in the report
        print("[*] Filling report form...")
        
        # Fill title using common HackerOne field patterns
        try:
            title_selector = page.query_selector('input[name*="title"], input[id*="title"], input[name*="subject"]')
            if title_selector:
                title_selector.fill(title)
                print("[+] Title filled")
        except Exception as e:
            print(f"[*] Title field: {e}")
        
        # Fill description using common patterns
        try:
            desc_selector = page.query_selector('textarea[name*="description"], textarea[name*="body"], textarea[id*="description"]')
            if desc_selector:
                desc_selector.fill(report_content[:8000])  # Limit to avoid truncation
                print("[+] Description filled")
        except Exception as e:
            print(f"[*] Description field: {e}")
        
        # Try to set severity
        try:
            severity_select = page.query_selector('select[name*="severity"], select[id*="severity"], select[name*="priority"]')
            if severity_select:
                severity_select.select_option(severity.lower())
                print("[+] Severity set")
        except Exception as e:
            print(f"[*] Severity selector: {e}")
        
        # Take screenshot for verification
        page.screenshot(path="/tmp/report_result.png")
        
        # Print current URL for debugging
        print(f"[*] Current URL: {page.url}")
        
        # Try to submit the form
        try:
            # Look for submit button
            submit_btn = page.query_selector('button[type="submit"], input[type="submit"], button:has-text("Submit")')
            if submit_btn:
                submit_btn.click()
                print("[+] Submit button clicked")
                page.wait_for_timeout(3000)
            else:
                print("[*] Submit button not found")
        except Exception as e:
            print(f"[*] Submit error: {e}")
        
        print("[*] Form submission attempted. Manual verification recommended.")
        print("[*] Check screenshot at /tmp/report_result.png")
        
        browser.close()
        
    return True


def main():
    parser = argparse.ArgumentParser(description="Submit bug bounty reports via Playwright")
    parser.add_argument('--platform', required=True, help='Platform: hackerone, bugcrowd')
    parser.add_argument('--program', required=True, help='Bug bounty program name')
    parser.add_argument('--file', required=True, help='Path to report file')
    parser.add_argument('--email', required=True, help='Email (or set HACKERONE_EMAIL env var)')
    parser.add_argument('--password', required=True, help='Password (or set HACKERONE_PASSWORD env var)')
    
    args = parser.parse_args()
    
    success = submit_report(args.platform, args.program, args.file, args.email, args.password)
    
    if success:
        print("[+] Report submission attempt completed")
        print("[*] Please verify manually on the platform")
        sys.exit(0)
    else:
        print("[-] Report submission failed")
        sys.exit(1)


if __name__ == "__main__":
    main()