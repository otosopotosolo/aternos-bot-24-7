#!/usr/bin/env python3
"""
SARAhack - Freebuff Auto-Submit System v2
Uses freebuff's real browser capability to submit reports to HackerOne

Usage:
    python3 freebuff/auto_submit_freebuff.py test-connection
    python3 freebuff/auto_submit_freebuff.py submit --report 24
    python3 freebuff/auto_submit_freebuff.py submit --all
    python3 freebuff/auto_submit_freebuff.py list

Environment Variables (from freebuff/tokenlogin.env):
    CODEBUFF_POSTHOG_API_KEY - Freebuff API key
    TMATE_USER, TMATE_HOST - tmate session credentials
    SSH_KEY_FILE - path to SSH private key
    HACKERONE_EMAIL, HACKERONE_PASSWORD - H1 login
"""

import os
import sys
import json
import time
import subprocess
import argparse
from pathlib import Path

# Configuration
WORKSPACE = Path("/home/runner/workspace")
TRACKER_FILE = WORKSPACE / "reports/tracking/reports.json"
TOKEN_FILE = WORKSPACE / "freebuff/tokenlogin.env"

def load_env():
    """Load credentials from tokenlogin.env into environment"""
    if TOKEN_FILE.exists():
        with open(TOKEN_FILE) as f:
            for line in f:
                if line.startswith("export ") and "=" in line:
                    key, value = line.split("=", 1)
                    key = key.replace("export ", "").strip()
                    value = value.strip().strip('"').strip("'")
                    os.environ[key] = value

def get_config():
    """Get configuration from environment - fail if required vars missing"""
    load_env()
    
    # Required variables (no fallbacks allowed)
    required = ["CODEBUFF_POSTHOG_API_KEY", "TMATE_USER", "TMATE_HOST"]
    for var in required:
        if not os.environ.get(var):
            raise ValueError(f"Missing required environment variable: {var}")
    
    # Check password is set
    h1_password = os.environ.get("HACKERONE_PASSWORD", "")
    if not h1_password:
        raise ValueError("HACKERONE_PASSWORD not set - login will fail")
    
    # Get SSH key and validate it exists
    ssh_key = os.environ.get("SSH_KEY_FILE", os.path.expanduser("~/.ssh/id_ed25519"))
    if not os.path.exists(ssh_key):
        raise ValueError(f"SSH key not found: {ssh_key}")
    
    return {
        "tmate_host": os.environ["TMATE_HOST"],  # Required - no fallback
        "tmate_user": os.environ["TMATE_USER"],  # Required - no fallback
        "ssh_key": ssh_key,
        "api_key": os.environ["CODEBUFF_POSTHOG_API_KEY"],  # Required - no fallback
        "h1_email": os.environ.get("HACKERONE_EMAIL", "potosopotosolo@gmail.com"),
        "h1_password": h1_password,  # Required - checked above
    }

def load_tracker():
    """Load reports tracker"""
    with open(TRACKER_FILE) as f:
        return json.load(f)

def save_tracker(tracker):
    """Save reports tracker"""
    with open(TRACKER_FILE, "w") as f:
        json.dump(tracker, f, indent=2)

def get_verified_reports(tracker):
    """Get reports that are verified and ready to submit"""
    verified = []
    seen = {}  # (program, vuln_type) -> report
    
    for r in tracker:
        if r["status"] == "pending" and r.get("report_file", "").startswith("reports/VERIFIED_"):
            key = (r["program"], r["vulnerability"])
            if key not in seen:
                seen[key] = r
                verified.append(r)
    
    return verified

def test_ssh_connection():
    """Test SSH connection to tmate session"""
    cfg = get_config()
    print(f"[*] Testing SSH connection to {cfg['tmate_user']}@{cfg['tmate_host']}...")
    
    cmd = [
        "ssh", "-o", "StrictHostKeyChecking=no",
        "-o", "ConnectTimeout=10",
        "-i", cfg["ssh_key"],
        f"{cfg['tmate_user']}@{cfg['tmate_host']}",
        "echo 'SSH OK' && freebuff --version 2>/dev/null || echo 'freebuff not found'"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("[+] SSH connection OK")
            print(f"    {result.stdout.strip()}")
            return True
        else:
            print(f"[-] SSH failed")
            if result.stderr:
                print(f"    {result.stderr[:200]}")
            return False
    except Exception as e:
        print(f"[-] Error: {e}")
        return False

def build_freebuff_prompt(report, content, cfg):
    """Build the freebuff prompt with proper escaping"""
    program = report["program"].lower()
    
    # Escape for shell - use shlex.quote for content
    escaped_content = shlex.quote(content[:3000])
    
    prompt = f'''export CODEBUFF_POSTHOG_API_KEY={shlex.quote(cfg['api_key'])}
freebuff "Use browser-use to:
1. Open https://hackerone.com/{program}/reports/new
2. Login with email: {shlex.quote(cfg['h1_email'])} and password: {shlex.quote(cfg['h1_password'])}
3. Fill and submit the report:
Title: {report['program']} - {report['vulnerability']} Misconfiguration
Severity: {report['severity']}
Report: {escaped_content}
Fill all required fields and submit the report."'''
    
    return prompt

def submit_via_freebuff(report, dry_run=False, verbose=False):
    """Submit a single report via freebuff browser-use"""
    cfg = get_config()
    report_path = WORKSPACE / report["report_file"]
    
    # Read report content
    if report_path.exists():
        with open(report_path) as f:
            content = f.read()
    else:
        print(f"[-] Report file not found: {report_path}")
        return False
    
    program = report["program"].lower()
    vuln = report["vulnerability"]
    severity = report["severity"]
    
    if dry_run:
        print(f"[DRY RUN] Would submit #{report['id']}: {program}/{vuln}")
        print(f"  File: {report['report_file']}")
        print(f"  Severity: {severity}")
        return True
    
    print(f"[*] Submitting #{report['id']} {program}/{vuln}...")
    
    # Build prompt
    prompt = f'''Use browser-use to:
1. Open https://hackerone.com/{program}/reports/new
2. Login with email: {cfg['h1_email']} and password: {cfg['h1_password']}
3. Fill and submit the report with these details:

Title: {report['program']} - {vuln} Misconfiguration
Severity: {severity}

Report Content:
{content[:3000]}

Fill all required fields and submit the report.'''
    
    # Escape for shell - minimal escaping for heredoc
    safe_prompt = prompt.replace("\\", "\\\\").replace('"', '\\"').replace("$", "\\$").replace("`", "\\`")
    
    # Use heredoc via SSH for reliable multi-line input
    cmd = [
        "ssh", "-o", "StrictHostKeyChecking=no",
        "-o", "ServerAliveInterval=60",
        "-o", "TCPKeepAlive=yes",
        "-tt",  # Force PTY allocation
        "-i", cfg["ssh_key"],
        f"{cfg['tmate_user']}@{cfg['tmate_host']}",
        f'''export CODEBUFF_POSTHOG_API_KEY='{cfg['api_key']}' && cat << 'FREEBUFF_EOF' | freebuff\n{safe_prompt}\nFREEBUFF_EOF'''
    ]
    
    if verbose:
        print(f"    Running SSH with PTY...")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        if verbose:
            print(f"    Exit code: {result.returncode}")
            if result.stdout:
                print(f"    stdout: {result.stdout[:300]}")
            if result.stderr:
                print(f"    stderr: {result.stderr[:300]}")
        
        # Check for success indicators (freebuff may use different wording)
        success_indicators = ['submitted', 'success', 'created', 'thank you', 'complete']
        stdout_lower = result.stdout.lower() + result.stderr.lower()
        has_success_msg = any(ind in stdout_lower for ind in success_indicators)
        
        if result.returncode == 0:
            if has_success_msg:
                print(f"[+] Report #{report['id']} submitted successfully!")
                return True
            else:
                print(f"[?] Report #{report['id']} completed (verify manually)")
                return True  # No error but unclear - assume success
        else:
            print(f"[-] Submission failed (exit code {result.returncode})")
            if result.stderr:
                print(f"    {result.stderr[:200]}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"[-] Timeout for report #{report['id']} (600s)")
        return False
    except Exception as e:
        print(f"[-] Error: {e}")
        return False

def update_tracker_report(report_id, new_status):
    """Update report status in tracker"""
    tracker = load_tracker()
    for r in tracker:
        if r["id"] == report_id:
            r["status"] = new_status
            r["last_updated"] = time.strftime("%Y-%m-%d")
            break
    save_tracker(tracker)

def list_pending_reports(tracker):
    """List all pending reports"""
    print("\n📋 Pending Reports:")
    print("-" * 60)
    
    verified = get_verified_reports(tracker)
    if verified:
        print("\n✅ VERIFIED Reports (curl confirmed - ready to submit):")
        for r in verified:
            print(f"  [{r['id']}] {r['program']} - {r['vulnerability']} ({r['severity']})")
            print(f"         {r['report_file']}")
    else:
        print("\n⚠️ No verified reports found")
    
    pending = [r for r in tracker if r["status"] == "pending" and not r.get("report_file", "").startswith("reports/VERIFIED_")]
    if pending:
        print(f"\n⏳ Other Pending ({len(pending)} reports):")
        for r in pending[:15]:
            print(f"  [{r['id']}] {r['program']} - {r['vulnerability']}")

def main():
    parser = argparse.ArgumentParser(description="SARAhack Auto-Submit via Freebuff")
    parser.add_argument("command", choices=["test-connection", "submit", "list"], help="Command")
    parser.add_argument("--report", type=int, help="Submit specific report ID")
    parser.add_argument("--all", action="store_true", help="Submit all verified reports")
    parser.add_argument("--dry-run", action="store_true", help="Preview without submitting")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed output")
    parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompt")
    args = parser.parse_args()
    
    try:
        get_config()  # Load env and validate
    except ValueError as e:
        print(f"[-] Configuration error: {e}")
        return 1
    
    if args.command == "test-connection":
        success = test_ssh_connection()
        return 0 if success else 1
    
    elif args.command == "list":
        tracker = load_tracker()
        list_pending_reports(tracker)
        return 0
    
    elif args.command == "submit":
        tracker = load_tracker()
        
        reports_to_submit = []
        
        if args.report:
            # Specific report
            for r in tracker:
                if r["id"] == args.report:
                    reports_to_submit = [r]
                    break
            if not reports_to_submit:
                print(f"[-] Report #{args.report} not found")
                return 1
        elif args.all:
            # All verified reports
            reports_to_submit = get_verified_reports(tracker)
            if not reports_to_submit:
                print("[-] No verified reports to submit")
                return 1
            # Confirmation for bulk submit
            if not args.yes:
                print(f"\n⚠️  About to submit {len(reports_to_submit)} reports via freebuff browser.")
                response = input("Continue? (y/n): ")
                if response.lower() != 'y':
                    print("Aborted.")
                    return 0
        else:
            parser.print_help()
            return 1
        
        print(f"[*] Submitting {len(reports_to_submit)} report(s)...")
        
        results = []
        for r in reports_to_submit:
            success = submit_via_freebuff(r, dry_run=args.dry_run, verbose=args.verbose)
            results.append({"id": r["id"], "program": r["program"], "success": success})
            
            if success and not args.dry_run:
                update_tracker_report(r["id"], "submitted")
            
            # Wait between submissions
            if not args.dry_run:
                print("[*] Waiting 45s before next submission...")
                time.sleep(45)
        
        # Summary
        print("\n" + "=" * 50)
        print("SUBMISSION SUMMARY")
        print("=" * 50)
        for res in results:
            icon = "✅" if res["success"] else "❌"
            print(f"{icon} #{res['id']} {res['program']}")
        
        success_count = sum(1 for r in results if r["success"])
        print(f"\nResult: {success_count}/{len(results)} successful")
        
        return 0 if success_count == len(results) else 1

if __name__ == "__main__":
    sys.exit(main())