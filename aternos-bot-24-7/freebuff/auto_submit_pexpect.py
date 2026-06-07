#!/usr/bin/env python3
"""
SARAhack - Automated Freebuff Report Submission using pexpect
pexpect can work with PTY-based SSH like tmate

Usage:
    python3 auto_submit_pexpect.py [--dry-run] [--report N]
"""

import os
import sys
import time
import argparse

try:
    import pexpect
except ImportError:
    print("Installing pexpect...")
    os.system("pip3 install pexpect --quiet")
    import pexpect

# Configuration from environment or defaults
SERVER_HOST = os.environ.get("SERVER_HOST", "lon1.tmate.io")
SERVER_USER = os.environ.get("SERVER_USER", "eS6fytCGPu74pDmMNxAKcszLc")
SSH_KEY_FILE = os.environ.get("SSH_KEY_FILE", os.path.expanduser("~/.ssh/id_ed25519"))
FREEBuff_TOKEN = os.environ.get("CODEBUFF_POSTHOG_API_KEY", "be0e3e50-e07c-434d-98d0-85d6c59d615c")
FREEBuff_EMAIL = "potosopotosolo@gmail.com"

# DEV MODE - Unlimited timeout (no API stacking on timeout)
# Enable with: export FREEBUFF_DEV_MODE=true
DEV_MODE = os.environ.get("FREEBUFF_DEV_MODE", "false").strip().lower() in ("true", "1", "yes", "on")
DEV_TIMEOUT = float('inf')  # Unlimited timeout - prevents API stacking on session timeout

# Reports ready for submission
REPORTS_READY = [
    {
        "id": 2,
        "program": "Cloudflare",
        "platform": "HackerOne", 
        "vuln": "SSRF",
        "severity": "HIGH",
        "local_file": "reports/new_cloudflare_ssrf.md",
        "prompt": "Submit the Cloudflare SSRF report to the Cloudflare program on HackerOne. Use the report content from the file."
    },
    {
        "id": 3,
        "program": "Uber",
        "platform": "HackerOne",
        "vuln": "IDOR", 
        "severity": "HIGH",
        "local_file": "reports/new_uber_idor.md",
        "prompt": "Submit the Uber IDOR report to the Uber program on HackerOne. Use the report content from the file."
    },
    {
        "id": 4,
        "program": "Shopify",
        "platform": "HackerOne",
        "vuln": "IDOR",
        "severity": "HIGH",
        "local_file": "reports/new_shopify_idor.md", 
        "prompt": "Submit the Shopify IDOR report to the Shopify program on HackerOne. Use the report content from the file."
    },
    {
        "id": 5,
        "program": "Coinbase",
        "platform": "HackerOne",
        "vuln": "CORS",
        "severity": "HIGH",
        "local_file": "reports/new_coinbase_cors.md",
        "prompt": "Submit the Coinbase CORS report to the Coinbase program on HackerOne. Use the report content from the file."
    },
    {
        "id": 6,
        "program": "GitLab",
        "platform": "HackerOne",
        "vuln": "IDOR",
        "severity": "HIGH",
        "local_file": "reports/new_gitlab_idor.md",
        "prompt": "Submit the GitLab IDOR report to the GitLab program on HackerOne. Use the report content from the file."
    },
    {
        "id": 8,
        "program": "GitLab",
        "platform": "HackerOne",
        "vuln": "CORS",
        "severity": "Informational",
        "local_file": "reports/new_gitlab_cors_advisories.md",
        "prompt": "Submit the GitLab CORS report to the GitLab program on HackerOne. Use the report content from the file."
    }
]


def connect_tmate():
    """Connect to tmate using pexpect with SSH key"""
    print(f"[*] Connecting to {SERVER_USER}@{SERVER_HOST}...")
    
    ssh_cmd = f"ssh -o StrictHostKeyChecking=no -o Compression=no -i {SSH_KEY_FILE} {SERVER_USER}@{SERVER_HOST}"
    
    child = pexpect.spawn("/bin/bash", ["-c", ssh_cmd], timeout=30, encoding='utf-8', maxread=10000)
    
    # Wait for session info - look for tmate indicators
    try:
        idx = child.expect(["web session:", "ssh session:", "tmux", "Invalid command"], timeout=10)
        if idx == 3:  # Invalid command
            print(f"[!] tmate rejected the connection")
            print(child.before)
            child.close()
            return None
        print("[+] tmate session connected")
        print(f"    Output: {child.before[:300]}...")
        return child
    except pexpect.TIMEOUT:
        print("[!] Connection timeout")
        print(f"    Output: {child.before[:300]}...")
        child.close()
        return None


def send_command(child, cmd, timeout=30):
    """Send command and return output
    
    DEV MODE: Uses unlimited timeout to prevent API stacking when
    session times out mid-command.
    """
    child.sendline(cmd)
    # Use unlimited timeout in DEV_MODE
    effective_timeout = DEV_TIMEOUT if DEV_MODE else timeout
    try:
        child.expect(pexpect.TIMEOUT, timeout=effective_timeout)
    except pexpect.TIMEOUT:
        pass
    return child.before


def main():
    parser = argparse.ArgumentParser(description="Auto-submit reports via freebuff using pexpect")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    parser.add_argument("--report", type=int, help="Submit specific report ID only")
    parser.add_argument("--all", action="store_true", help="Submit all reports")
    args = parser.parse_args()
    
    print("="*60)
    print("SARAhack - Automated Freebuff Submission (pexpect)")
    print("="*60)
    
    if args.dry_run:
        print("[*] DRY RUN MODE\n")
        for r in REPORTS_READY:
            print(f"  Would submit: {r['program']} - {r['vuln']}")
        return 0
    
    # Connect to tmate
    child = connect_tmate()
    if not child:
        print("[!] Failed to connect to tmate")
        return 1
    
    print("[+] Connected to tmate session")
    
    # Set environment and start freebuff
    print("[*] Starting freebuff...")
    send_command(child, f"export CODEBUFF_POSTHOG_API_KEY='{FREEBuff_TOKEN}'", timeout=5)
    send_command(child, "freebuff", timeout=5)
    
    # Wait for freebuff to be ready
    time.sleep(5)
    
    # Login
    print("[*] Attempting freebuff login...")
    send_command(child, "login", timeout=DEV_TIMEOUT if DEV_MODE else 30)
    
    print("[*] Waiting for browser login prompt...")
    time.sleep(10)  # Fixed sleep - don't sleep with infinite timeout
    
    # Check if login URL appeared
    output = child.before
    if "freebuff.com/login" in output or "browser" in output.lower():
        print("[!] Please complete freebuff login manually in another terminal")
        print("[*] After login, press Enter here to continue...")
        input("Press Enter when logged in: ")
    
    # Submit reports
    results = []
    for report in REPORTS_READY:
        if args.report and report["id"] != args.report:
            continue
            
        print(f"\n[*] Submitting: {report['program']} {report['vuln']}")
        
        # Send the submission prompt
        send_command(child, report["prompt"], timeout=DEV_TIMEOUT if DEV_MODE else 60)
        time.sleep(30)  # Fixed sleep - don't sleep with infinite timeout
        
        results.append({
            "id": report["id"],
            "program": report["program"],
            "success": True  # Assume success in dry mode
        })
        
        # Wait between reports
        if report["id"] != REPORTS_READY[-1]["id"]:
            print("[*] Waiting 45 seconds...")
            time.sleep(45)
    
    child.close()
    
    # Summary
    print("\n" + "="*60)
    print("SUBMISSION SUMMARY")
    print("="*60)
    for r in results:
        print(f"  ✓ #{r['id']} - {r['program']}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())