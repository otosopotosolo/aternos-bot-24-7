#!/usr/bin/env python3
"""
SARAhack - Improved HackerOne Browser Automation
Uses freebuff with real Chrome to bypass Cloudflare protection

Usage:
    python3 h1_auto_submit.py test-connection
    python3 h1_auto_submit.py submit --program rollbar --report reports/new_rollbar_cors.md
    python3 h1_auto_submit.py test-bypass
"""

import os
import sys
import json
import time
import argparse
import subprocess
import base64
from pathlib import Path
from datetime import datetime

# SSH Configuration for freebuff server
FREEFF_HOST = "lon1.tmate.io"
FREEFF_USER = "eS6fytCGPu74pDmMNxAKcszLc"
SSH_KEY = os.environ.get("SSH_KEY_FILE", os.path.expanduser("~/.ssh/id_ed25519"))
# SECRET for cloudflared tunnel authentication
SECRET = "EUwteWtAugwWBPqCIUWcuVGq"

# HackerOne Credentials
HACKERONE_EMAIL = os.environ.get("HACKERONE_EMAIL", "potosopotosolo@gmail.com")
HACKERONE_PASSWORD = os.environ.get("HACKERONE_PASSWORD", ")a9By=*D#6/w9T")

# DEV MODE - Unlimited timeout (no API stacking on timeout)
# Enable with: export FREEBUFF_DEV_MODE=true
DEV_MODE = os.environ.get("FREEBUFF_DEV_MODE", "false").strip().lower() in ("true", "1", "yes", "on")
DEV_TIMEOUT = float('inf')  # Unlimited timeout - prevents API stacking on session timeout

# Reports directory
REPORTS_DIR = Path(__file__).parent.parent / "reports"
DRAFTS_DIR = REPORTS_DIR / "drafts"

# Program URLs
PROGRAM_URLS = {
    "rollbar": "https://hackerone.com/rollbar/reports/new",
    "stripe": "https://hackerone.com/stripe/reports/new",
    "discord": "https://hackerone.com/discord/reports/new",
    "github": "https://hackerone.com/github/reports/new",
    "gitlab": "https://hackerone.com/gitlab/reports/new",
    "sendgrid": "https://hackerone.com/sendgrid/reports/new",
    "twilio": "https://hackerone.com/twilio/reports/new",
    "shopify": "https://hackerone.com/shopify/reports/new",
    "uber": "https://hackerone.com/uber/reports/new",
    "cloudflare": "https://hackerone.com/cloudflare/reports/new",
    "bitbucket": "https://hackerone.com/bitbucket/reports/new",
    "atlassian": "https://hackerone.com/atlassian/reports/new",
    "automattic": "https://hackerone.com/automattic/reports/new",
    "mailgun": "https://hackerone.com/mailgun/reports/new",
    "newrelic": "https://hackerone.com/newrelic/reports/new",
    "travis": "https://hackerone.com/travis-ci/reports/new",
    "spotify": "https://hackerone.com/spotify/reports/new",
    "slack": "https://hackerone.com/slack/reports/new",
    "figma": "https://hackerone.com/figma/reports/new",
    "pipedrive": "https://hackerone.com/pipedrive/reports/new",
    "cdn77": "https://hackerone.com/cdn77/reports/new",
    "victorops": "https://hackerone.com/victorops/reports/new",
    "clickup": "https://hackerone.com/clickup/reports/new",
}

def ssh_command(cmd, timeout=120):
    """Execute command via SSH to freebuff server
    
    DEV MODE: Uses unlimited timeout to prevent API stacking when
    session times out mid-command.
    """
    # Check if SSH key exists, if not try without it
    ssh_key_arg = []
    if os.path.exists(SSH_KEY):
        ssh_key_arg = ["-i", SSH_KEY]
    
    ssh_cmd = [
        "ssh", "-o", "StrictHostKeyChecking=no",
        "-o", "ConnectTimeout=30",
        "-o", "SetEnv", f"SECRET={SECRET}",
    ] + ssh_key_arg + [
        f"{FREEFF_USER}@{FREEFF_HOST}", cmd
    ]
    
    # Use unlimited timeout in DEV_MODE
    effective_timeout = DEV_TIMEOUT if DEV_MODE else timeout
    
    try:
        result = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=effective_timeout)
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, "SSH timeout"
    except Exception as e:
        return False, str(e)

def ssh_command_with_stdin(cmd, stdin_data, timeout=120):
    """Execute command via SSH with stdin (for base64 encoded prompts)
    
    DEV MODE: Uses unlimited timeout to prevent API stacking when
    session times out mid-command.
    """
    ssh_key_arg = []
    if os.path.exists(SSH_KEY):
        ssh_key_arg = ["-i", SSH_KEY]
    
    ssh_cmd = [
        "ssh", "-o", "StrictHostKeyChecking=no",
        "-o", "ConnectTimeout=30",
        "-o", "SetEnv", f"SECRET={SECRET}",
    ] + ssh_key_arg + [
        f"{FREEFF_USER}@{FREEFF_HOST}"
    ]
    
    # Use unlimited timeout in DEV_MODE
    effective_timeout = DEV_TIMEOUT if DEV_MODE else timeout
    
    try:
        result = subprocess.run(ssh_cmd, input=stdin_data, capture_output=True, text=True, timeout=effective_timeout)
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, "SSH timeout"
    except Exception as e:
        return False, str(e)

def load_report_content(report_file):
    """Load report from file"""
    report_path = Path(report_file)
    if not report_path.exists():
        # Try reports directory
        report_path = REPORTS_DIR / Path(report_file).name
    if not report_path.exists():
        # Try drafts directory
        report_path = DRAFTS_DIR / Path(report_file).name
    
    if not report_path.exists():
        return None
    
    with open(report_path, 'r') as f:
        return f.read()

def parse_report_for_h1(content):
    """Parse report content for HackerOne submission"""
    lines = content.split('\n')
    
    title = None
    severity = None
    description_lines = []
    impact_lines = []
    steps_lines = []
    current_section = None
    
    for line in lines:
        line_lower = line.lower()
        
        # Extract title
        if not title and line.startswith('# '):
            title = line[2:].strip()
        
        # Extract severity
        if 'severity' in line_lower and ':' in line:
            severity = line.split(':')[-1].strip().lower()
        
        # Track sections
        if line.startswith('## Summary') or line.startswith('## Description'):
            current_section = 'description'
        elif line.startswith('## Steps to Reproduce'):
            current_section = 'steps'
        elif line.startswith('## Impact'):
            current_section = 'impact'
        elif line.startswith('## '):
            current_section = None
        elif current_section == 'description' and line.strip():
            description_lines.append(line)
        elif current_section == 'steps' and line.strip():
            steps_lines.append(line)
        elif current_section == 'impact' and line.strip():
            impact_lines.append(line)
    
    # Build structured description
    description = '\n'.join(description_lines)
    if steps_lines:
        description += '\n\n## Steps to Reproduce\n' + '\n'.join(steps_lines)
    if impact_lines:
        description += '\n\n## Impact\n' + '\n'.join(impact_lines)
    
    return {
        'title': title or 'CORS Misconfiguration',
        'severity': severity or 'high',
        'description': description[:8000]  # Limit length
    }

def build_freebuff_prompt(program, report_data):
    """Build prompt for freebuff browser-use"""
    
    url = PROGRAM_URLS.get(program.lower(), f"https://hackerone.com/{program}/reports/new")
    
    prompt = f"""Use browser-use to complete this HackerOne report submission:

1. Navigate to: {url}

2. If not logged in, login with:
   - Email: {HACKERONE_EMAIL}
   - Password: {HACKERONE_PASSWORD}

3. If you encounter Cloudflare challenge, wait for it to complete automatically.

4. Fill the report form:
   - Title: {report_data['title']}
   - Severity: {report_data['severity']}
   - Description: 
{report_data['description']}

5. Look for these fields:
   - Title field: input[name="title"] or input[id="report_title"]
   - Severity: select[name="severity"] or dropdown
   - Description: textarea[name="description"]

6. After filling, click the Submit button.

7. Take a screenshot and confirm if submission was successful.

Return a summary of what happened."""

    return prompt

def test_connection():
    """Test SSH connection to freebuff server"""
    print("[*] Testing SSH connection to freebuff...")
    timeout = DEV_TIMEOUT if DEV_MODE else 30
    success, output = ssh_command("echo 'Connection OK' && uptime && which freebuff 2>/dev/null || echo 'freebuff not in PATH'", timeout=timeout)
    
    if success:
        print("[✅] Connected to freebuff server!")
        print(output[:500])
        return True
    else:
        print(f"[❌] Connection failed: {output}")
        return False

def test_freebuff_browser():
    """Test freebuff browser capability"""
    print("[*] Testing freebuff browser-use...")
    
    test_prompt = """Use browser-use to:
1. Navigate to https://www.google.com
2. Take a screenshot
3. Return the page title

This tests if browser automation is working."""
    
    timeout = DEV_TIMEOUT if DEV_MODE else 120
    success, output = ssh_command(f'freebuff "{test_prompt}"', timeout=timeout)
    
    if success:
        print("[✅] Freebuff browser is working!")
        print(output[:300])
        return True
    else:
        print(f"[❌] Freebuff browser test failed: {output}")
        return False

def send_via_base64(prompt):
    """Send prompt to freebuff using base64 encoding to avoid escaping issues"""
    import base64
    prompt_b64 = base64.b64encode(prompt.encode('utf-8')).decode('ascii')
    
    stdin_script = f'''cat << 'FREEBUFF_EOF' | base64 -d | freebuff
{prompt_b64}
FREEBUFF_EOF'''
    
    # Use unlimited timeout in DEV_MODE (600s default)
    timeout = DEV_TIMEOUT if DEV_MODE else 600
    return ssh_command_with_stdin("bash -s", stdin_script, timeout=timeout)

def submit_report(program, report_file):
    """Submit report using freebuff browser-use"""
    print(f"[*] Submitting {program} report via freebuff...")
    
    # Load report
    content = load_report_content(report_file)
    if not content:
        print(f"[❌] Report file not found: {report_file}")
        return False
    
    # Parse report
    report_data = parse_report_for_h1(content)
    print(f"[+] Report loaded: {report_data['title']}")
    print(f"    Severity: {report_data['severity']}")
    print(f"    Description: {len(report_data['description'])} chars")
    
    # Build prompt
    prompt = build_freebuff_prompt(program, report_data)
    
    # Send to freebuff via base64
    print("[*] Sending to freebuff browser-use (via base64)...")
    success, output = send_via_base64(prompt)
    
    if success:
        print("[✅] Report submission completed!")
        print(output[:500] if len(output) > 500 else output)
        return True
    else:
        print(f"[❌] Submission failed: {output}")
        return False

def submit_all_drafts():
    """Submit all draft reports"""
    print("[*] Finding draft reports to submit...")
    
    drafts = list(DRAFTS_DIR.glob("draft_*_cors.md"))
    print(f"[+] Found {len(drafts)} draft reports")
    
    results = []
    for draft in drafts:
        program = draft.stem.replace("draft_", "").replace("_cors", "")
        print(f"\n[*] Processing: {program}")
        
        success = submit_report(program, str(draft))
        results.append({
            'program': program,
            'success': success,
            'file': str(draft)
        })
        
        # Wait between submissions
        time.sleep(10)
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 SUBMISSION SUMMARY")
    print(f"{'='*60}")
    
    success_count = sum(1 for r in results if r['success'])
    for r in results:
        status = "✅" if r['success'] else "❌"
        print(f"{status} {r['program']}")
    
    print(f"\nTotal: {len(results)} | Success: {success_count} | Failed: {len(results) - success_count}")
    
    return success_count > 0

def main():
    parser = argparse.ArgumentParser(description="SARAhack - HackerOne Auto Submit via Freebuff")
    parser.add_argument('command', choices=['test-connection', 'test-browser', 'submit', 'submit-all', 'list'])
    parser.add_argument('--program', help='Program name (e.g., rollbar)')
    parser.add_argument('--report', help='Report file path')
    
    args = parser.parse_args()
    
    if args.command == 'test-connection':
        test_connection()
    elif args.command == 'test-browser':
        test_freebuff_browser()
    elif args.command == 'submit':
        if not args.program or not args.report:
            print("[❌] Usage: submit --program <name> --report <file>")
            return
        submit_report(args.program, args.report)
    elif args.command == 'submit-all':
        submit_all_drafts()
    elif args.command == 'list':
        drafts = list(DRAFTS_DIR.glob("draft_*_cors.md"))
        print(f"\n📋 Draft Reports ({len(drafts)}):")
        for d in drafts:
            program = d.stem.replace("draft_", "").replace("_cors", "")
            print(f"  - {program}: {d.name}")

if __name__ == "__main__":
    main()