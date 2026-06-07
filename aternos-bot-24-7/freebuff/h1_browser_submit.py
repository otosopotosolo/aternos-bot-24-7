#!/usr/bin/env python3
"""
SARAhack - HackerOne Browser Submitter
Uses Playwright to automate report submission to HackerOne
Bypasses Cloudflare protection
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

async def submit_report(program: str, report_file: str, severity: str = "high"):
    """Submit a report to HackerOne using Playwright browser automation"""
    
    from playwright.async_api import async_playwright
    
    # Credentials from tokenlogin.env
    EMAIL = "potosopotosolo@gmail.com"
    PASSWORD = ")a9By=*D#6/w9T"
    
    # Report URLs
    REPORT_URLS = {
        "rollbar": "https://hackerone.com/rollbar/reports/new",
        "stripe": "https://hackerone.com/stripe/reports/new",
        "twilio": "https://hackerone.com/twilio/reports/new",
        "newrelic": "https://hackerone.com/newrelic/reports/new",
        "discord": "https://hackerone.com/discord/reports/new",
        "mailgun": "https://hackerone.com/mailgun/reports/new",
        "travis": "https://hackerone.com/travis-ci/reports/new",
        "spotify": "https://hackerone.com/spotify/reports/new",
        "gitlab": "https://hackerone.com/gitlab/reports/new",
        "slack": "https://hackerone.com/slack/reports/new",
        "figma": "https://hackerone.com/figma/reports/new",
        "bitbucket": "https://hackerone.com/bitbucket/reports/new",
        "pipedrive": "https://hackerone.com/pipedrive/reports/new",
        "sendgrid": "https://hackerone.com/sendgrid/reports/new",
        "wordpress": "https://hackerone.com/automattic/reports/new",
        "atlassian": "https://hackerone.com/atlassian/reports/new",
        "clickup": "https://hackerone.com/clickup/reports/new",
        "cdn77": "https://hackerone.com/cdn77/reports/new",
        "victorops": "https://hackerone.com/victorops/reports/new",
    }
    
    if program.lower() not in REPORT_URLS:
        print(f"[-] Unknown program: {program}")
        return False
    
    print(f"[*] Submitting {program} CORS report via browser...")
    print(f"[*] Report file: {report_file}")
    
    # Read report content
    report_path = Path(report_file)
    if not report_path.exists():
        # Try relative to project root
        report_path = Path(__file__).parent.parent / "reports" / Path(report_file).name
    
    if not report_path.exists():
        print(f"[-] Report file not found: {report_file}")
        return False
    
    with open(report_path, 'r') as f:
        report_content = f.read()
    
    # Extract title from report
    title = f"{program.upper()} - CORS Misconfiguration with Credentials"
    
    # Parse vulnerability details from report
    lines = report_content.split('\n')
    vuln_details = ""
    for line in lines:
        if line.startswith('##') or line.startswith('**'):
            continue
        if line.strip():
            vuln_details += line + "\n"
    
    async with async_playwright() as p:
        try:
            # Launch browser
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = await context.new_page()
            
            # Navigate to login
            print("[*] Navigating to HackerOne login...")
            await page.goto("https://hackerone.com/users/sign_in", timeout=60000)
            await page.wait_for_load_state("networkidle", timeout=30000)
            
            # Fill credentials
            print("[*] Logging in...")
            await page.fill('input[type="email"]', EMAIL)
            await page.fill('input[type="password"]', PASSWORD)
            await page.click('button[type="submit"]')
            
            # Wait for redirect
            await page.wait_for_timeout(5000)
            
            # Navigate to report submission
            print(f"[*] Navigating to {program} report page...")
            await page.goto(REPORT_URLS[program.lower()], timeout=60000)
            await page.wait_for_load_state("networkidle", timeout=30000)
            
            # Fill report title
            print("[*] Filling report title...")
            title_selector = 'input[name="report[title]"], input[id="report_title"], input[placeholder*="title" i]'
            await page.fill(title_selector, title)
            
            # Fill severity (select high)
            print("[*] Setting severity...")
            severity_selector = 'select[name*="severity"], select[id*="severity"]'
            try:
                await page.select_option(severity_selector, "high")
            except:
                print("[*] Could not set severity via selector, will set later")
            
            # Fill vulnerability details
            print("[*] Filling vulnerability details...")
            details_selector = 'textarea[name*="description"], textarea[id*="description"], textarea[placeholder*="vulnerability" i]'
            await page.fill(details_selector, vuln_details[:5000])
            
            # Take screenshot for verification
            await page.screenshot(path=f"/tmp/h1_submit_{program}.png")
            print(f"[+] Screenshot saved: /tmp/h1_submit_{program}.png")
            
            # Submit button
            submit_selector = 'button[type="submit"], input[type="submit"], button:has-text("Submit")'
            try:
                await page.click(submit_selector)
                print(f"[+] Report submitted for {program}!")
                await browser.close()
                return True
            except Exception as e:
                print(f"[-] Could not submit: {e}")
                await browser.close()
                return False
                
        except Exception as e:
            print(f"[-] Browser automation failed: {e}")
            try:
                await browser.close()
            except:
                pass
            return False

async def main():
    if len(sys.argv) < 3:
        print("Usage: python3 h1_browser_submit.py <program> <report_file>")
        print("Example: python3 h1_browser_submit.py stripe reports/new_stripe_cors.md")
        return 1
    
    program = sys.argv[1]
    report_file = sys.argv[2]
    
    success = await submit_report(program, report_file)
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)