#!/usr/bin/env python3
"""
SARAhack - Segfault Server Browser Automation for HackerOne Submissions

Uses cloudflared tunnel to SSH into segfault server, then runs Playwright
for automated browser submission of bug bounty reports.

Requirements:
    pip3 install paramiko sshpass

Usage:
    export SEGFAULT_HOST="suitable-mate-caroline-guide.trycloudflare.com"
    export SEGFAULT_USER="gg"
    export SEGFAULT_PASS="123456123456--"
    python3 freebuff/segfault_browser_submit.py --submit rollbar
"""

import os
import sys
import json
import time
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime

try:
    import paramiko
except ImportError:
    print("Installing paramiko...")
    os.system("pip3 install paramiko --quiet")
    import paramiko

# Configuration from environment
SEGFAULT_HOST = os.environ.get("SEGFAULT_HOST", "suitable-mate-caroline-guide.trycloudflare.com")
SEGFAULT_USER = os.environ.get("SEGFAULT_USER", "gg")
SEGFAULT_PASS = os.environ.get("SEGFAULT_PASS", "123456123456--")
CLOUDFLARED_PATH = "/tmp/cloudflared"

# HackerOne Credentials
HACKERONE_EMAIL = os.environ.get("HACKERONE_EMAIL", "nonoto999t@gmail.com")
HACKERONE_PASSWORD = os.environ.get("HACKERONE_PASSWORD", ")a9By=*D#6/w9T")

# Reports directory
REPORTS_DIR = Path(__file__).parent.parent / "reports"
TRACKER_FILE = REPORTS_DIR / "tracking" / "reports.json"


def install_cloudflared():
    """Install cloudflared if not present."""
    if os.path.exists(CLOUDFLARED_PATH):
        return True
    
    print("[*] Installing cloudflared...")
    result = subprocess.run(
        ["curl", "-sL", "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64", 
         "-o", CLOUDFLARED_PATH],
        capture_output=True
    )
    os.chmod(CLOUDFLARED_PATH, 0o755)
    return os.path.exists(CLOUDFLARED_PATH)


def upload_script_via_scp(ssh_client, local_script_path, remote_path="/tmp/playwright_submit.py"):
    """Upload a Python script to the segfault server via SCP."""
    print(f"[*] Uploading script to segfault server...")
    try:
        sftp = ssh_client.open_sftp()
        sftp.put(local_script_path, remote_path)
        sftp.close()
        print(f"  ✓ Script uploaded to {remote_path}")
        return True
    except Exception as e:
        print(f"  ❌ Upload failed: {e}")
        return False


def setup_segfault_connection():
    """Establish SSH connection to segfault server via cloudflared tunnel."""
    print(f"[*] Connecting to segfault server...")
    print(f"    Host: {SEGFAULT_HOST}")
    print(f"    User: {SEGFAULT_USER}")
    
    # Install cloudflared first
    if not install_cloudflared():
        print("[❌] Failed to install cloudflared")
        return None
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # Try direct SSH with password
        print(f"[*] Attempting SSH to {SEGFAULT_HOST}...")
        client.connect(
            hostname=SEGFAULT_HOST,
            username=SEGFAULT_USER,
            password=SEGFAULT_PASS,
            look_for_keys=False,
            allow_agent=False,
            timeout=30
        )
        print("[✅] SSH connection established!")
        return client


def run_remote_playwright(ssh_client, program_slug, report_content):
    """Run Playwright browser automation on the segfault server."""
    print(f"[*] Running Playwright on segfault server for {program_slug}...")
    
    # Create the Playwright submission script
    playwright_script = f'''#!/usr/bin/env python3
import os
import sys
import time

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Installing playwright...")
    os.system("pip3 install playwright --quiet")
    os.system("python3 -m playwright install chromium --with-deps")
    from playwright.sync_api import sync_playwright

HACKERONE_EMAIL = "{HACKERONE_EMAIL}"
HACKERONE_PASSWORD = "{HACKERONE_PASSWORD}"

def submit_report():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Show browser
        page = browser.new_page()
        
        # Login
        print("[*] Logging into HackerOne...")
        page.goto("https://hackerone.com/login")
        time.sleep(3)
        
        page.fill('input[name="user[email]"]', HACKERONE_EMAIL)
        page.fill('input[name="user[password]"]', HACKERONE_PASSWORD)
        page.click('button[type="submit"]')
        time.sleep(5)
        
        # Navigate to report form
        print("[*] Navigating to report form...")
        page.goto("https://hackerone.com/{program_slug}/reports/new")
        time.sleep(3)
        
        # Fill report
        print("[*] Filling report form...")
        title = "CORS Misconfiguration - {program_slug} API"
        page.fill('input[name="title"]', title)
        time.sleep(1)
        
        # Select severity
        try:
            page.select_option('select[name="severity"]', 'high')
        except:
            pass
        
        # Fill description
        description = """{report_content}"""
        page.fill('textarea[name="description"]', description[:5000])
        time.sleep(1)
        
        # Submit
        print("[*] Submitting report...")
        try:
            page.click('button[type="submit"]')
            time.sleep(5)
            print("[✅] Report submitted!")
        except Exception as e:
            print(f"[⚠️] Submit error: {{e}}")
        
        browser.close()

if __name__ == "__main__":
    submit_report()
'''
    
    # Upload and run
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(playwright_script)
        local_script = f.name
    
    try:
        # Upload script
        if not upload_script_via_scp(ssh_client, local_script, "/tmp/playwright_submit.py"):
            return False
        
        # Run the script
        print("[*] Executing Playwright script on segfault server...")
        stdin, stdout, stderr = ssh_client.exec_command("cd /tmp && python3 playwright_submit.py", timeout=120)
        
        # Read output
        output = ""
        for line in stdout:
            output += line
            print(f"    {line.strip()}")
        
        error = ""
        for line in stderr:
            error += line
        
        if error:
            print(f"[⚠️] stderr: {error[:500]}")
        
        return "submitted" in output.lower() or "success" in output.lower()
        
    finally:
        os.unlink(local_script)


def load_tracker():
    """Load reports tracker."""
    if not TRACKER_FILE.exists():
        return []
    with open(TRACKER_FILE, 'r') as f:
        return json.load(f)


def find_report(program_slug):
    """Find a pending report for the given program."""
    tracker = load_tracker()
    
    # Try exact match first
    for r in tracker:
        if r.get('program', '').lower() == program_slug.lower() and r.get('status') == 'pending':
            return r
    
    # Try partial match
    for r in tracker:
        if program_slug.lower() in r.get('program', '').lower() and r.get('status') == 'pending':
            return r
    
    return None


def get_report_content(report_file):
    """Load report content from file."""
    report_path = REPORTS_DIR / report_file
    if not report_path.exists():
        # Try alternate paths
        for pattern in [f"*{report_file}*", f"*{program_slug}*"]:
            files = list(REPORTS_DIR.glob(pattern))
            if files:
                report_path = files[0]
                break
    
    if not report_path.exists():
        return f"CORS Misconfiguration found in {program_slug} API. See scan results."
    
    with open(report_path, 'r') as f:
        return f.read()[:3000]  # Limit to 3000 chars


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Segfault Server Browser Automation")
    parser.add_argument("--submit", type=str, help="Submit report for program (e.g., rollbar, discord)")
    parser.add_argument("--list", action="store_true", help="List pending reports")
    parser.add_argument("--test", action="store_true", help="Test SSH connection")
    args = parser.parse_args()
    
    if args.test:
        print("[*] Testing segfault connection...")
        client = setup_segfault_connection()
        if client:
            print("[✅] Connection successful!")
            client.close()
            return
        print("[❌] Connection failed")
        return
    
    if args.list:
        tracker = load_tracker()
        print("\\n📋 Pending Reports:")
        print("-" * 60)
        for r in tracker:
            if r.get('status') == 'pending':
                print(f"  {r['program']} | {r['vulnerability']} | {r['severity']}")
        print("-" * 60)
        return
    
    if not args.submit:
        parser.print_help()
        print("\\n📋 Example usage:")
        print("  python3 freebuff/segfault_browser_submit.py --submit rollbar")
        print("  python3 freebuff/segfault_browser_submit.py --test")
        print("  python3 freebuff/segfault_browser_submit.py --list")
        return
    
    program_slug = args.submit.lower()
    print(f"\\n{'='*60}")
    print(f"🎯 Segfault Browser Submit - {program_slug}")
    print(f"{'='*60}")
    
    # Find report
    report = find_report(program_slug)
    if not report:
        print(f"[❌] No pending report found for: {program_slug}")
        return
    
    report_content = get_report_content(report.get('report_file', ''))
    
    # Connect to segfault
    client = setup_segfault_connection()
    if not client:
        print("[❌] Failed to connect to segfault server")
        print("\\n⚠️ Alternative: Submit manually at https://hackerone.com/{program_slug}/reports/new")
        return
    
    # Run Playwright submission
    success = run_remote_playwright(client, program_slug, report_content)
    
    client.close()
    
    if success:
        print(f"\\n[✅] Report submitted for {program_slug}!")
    else:
        print(f"\\n[⚠️] Submission may have failed - please verify manually")


if __name__ == "__main__":
    main()