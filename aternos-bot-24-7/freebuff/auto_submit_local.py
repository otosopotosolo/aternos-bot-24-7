#!/usr/bin/env python3
"""
SARAhack - Local Freebuff Auto-Submit System
Uses freebuff directly on local machine to submit reports to HackerOne

Usage:
    python3 freebuff/auto_submit_local.py test
    python3 freebuff/auto_submit_local.py submit --report 147
    python3 freebuff/auto_submit_local.py submit --all
    python3 freebuff/auto_submit_local.py list

Environment Variables:
    CODEBUFF_POSTHOG_API_KEY - Freebuff API key
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
    """Get configuration from environment"""
    load_env()
    
    api_key = os.environ.get("CODEBUFF_POSTHOG_API_KEY")
    if not api_key:
        raise ValueError("CODEBUFF_POSTHOG_API_KEY not set")
    
    h1_email = os.environ.get("HACKERONE_EMAIL", "potosopotosolo@gmail.com")
    h1_password = os.environ.get("HACKERONE_PASSWORD", "")
    if not h1_password:
        raise ValueError("HACKERONE_PASSWORD not set")
    
    return {
        "api_key": api_key,
        "h1_email": h1_email,
        "h1_password": h1_password,
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
    seen = {}
    
    for r in tracker:
        if r["status"] == "pending" and r.get("report_file", "").startswith("reports/VERIFIED_"):
            key = (r["program"], r["vulnerability"])
            if key not in seen:
                seen[key] = r
                verified.append(r)
    
    return verified

def test_freebuff():
    """Test if freebuff is available and working"""
    print("[*] Testing freebuff...")
    
    try:
        result = subprocess.run(
            ["freebuff", "--version"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            print(f"[+] freebuff is available: {result.stdout.strip()}")
            return True
        else:
            print(f"[-] freebuff error: {result.stderr}")
            return False
    except FileNotFoundError:
        print("[-] freebuff not found in PATH")
        return False
    except Exception as e:
        print(f"[-] Error: {e}")
        return False

def build_prompt(report, content, cfg):
    """Build the freebuff prompt"""
    program = report["program"].lower()
    
    prompt = f"""Use browser-use to complete the following task:

1. Navigate to: https://hackerone.com/{program}/reports/new
2. If not logged in, login with:
   - Email: {cfg['h1_email']}
   - Password: {cfg['h1_password']}
3. Submit a new vulnerability report with these details:

**Title:** {report['program']} - {report['vulnerability']} Misconfiguration

**Severity:** {report['severity']}

**Vulnerability Details:**
{content[:3000]}

**Steps to Reproduce:**
1. Navigate to the target API endpoint
2. Send a cross-origin request with appropriate headers
3. Observe that the response includes Access-Control-Allow-Origin reflecting the request origin
4. This allows cross-origin access to sensitive data

**Impact:**
An attacker can steal sensitive data from {report['program']} by making cross-origin requests from a malicious page.

**Remediation:**
Properly configure CORS headers to only allow trusted origins. Do not use arbitrary origin reflection with credentials.

Please fill in all required fields and submit the report."""

    return prompt

def submit_via_freebuff(report, dry_run=False, verbose=False):
    """Submit a single report via freebuff browser-use"""
    cfg = get_config()
    report_path = WORKSPACE / report["report_file"]
    
    if report_path.exists():
        with open(report_path) as f:
            content = f.read()
    else:
        print(f"[-] Report file not found: {report_path}")
        return False
    
    program = report["program"].lower()
    vuln = report["vulnerability"]
    
    if dry_run:
        print(f"[DRY RUN] Would submit #{report['id']}: {program}/{vuln}")
        return True
    
    print(f"[*] Submitting #{report['id']} {program}/{vuln} via freebuff browser...")
    
    # Build prompt
    prompt = build_prompt(report, content, cfg)
    
    # Create prompt file in temp directory with secure permissions
    import tempfile
    import shutil
    temp_dir = tempfile.mkdtemp(prefix='freebuff_')
    prompt_file = Path(temp_dir) / "prompt.txt"
    script_file = Path(temp_dir) / "submit.sh"
    
    # Write prompt to file (no escaping issues)
    with open(prompt_file, "w") as f:
        f.write(prompt)
    
    # Create wrapper script that sources env and runs freebuff
    script_content = f'''#!/bin/bash
export CODEBUFF_POSTHOG_API_KEY="{cfg['api_key']}"
freebuff < "{prompt_file}"
'''
    with open(script_file, "w") as f:
        f.write(script_content)
    # chmod AFTER file is created
    script_file.chmod(0o700)
    
    if verbose:
        print(f"    Running freebuff with browser-use...")
    
    try:
        result = subprocess.run(
            ["bash", str(script_file)],
            capture_output=True, text=True, timeout=600
        )
        
        if verbose:
            print(f"    Exit code: {result.returncode}")
            if result.stdout:
                print(f"    stdout: {result.stdout[:500]}")
            if result.stderr:
                print(f"    stderr: {result.stderr[:500]}")
        
        # Check success
        success_indicators = ['submitted', 'success', 'created', 'thank you', 'complete']
        combined = (result.stdout + result.stderr).lower()
        has_success = any(ind in combined for ind in success_indicators)
        
        if result.returncode == 0 and has_success:
            print(f"[+] Report #{report['id']} submitted successfully!")
            return True
        elif result.returncode == 0:
            print(f"[?] Report #{report['id']} completed (verify manually)")
            return True
        else:
            print(f"[-] Submission failed (exit code {result.returncode})")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"[-] Timeout for report #{report['id']} (600s)")
        return False
    except Exception as e:
        print(f"[-] Error: {e}")
        return False
    finally:
        # Cleanup temp files
        if Path(temp_dir).exists():
            shutil.rmtree(temp_dir)

def list_pending_reports(tracker):
    """List all pending reports"""
    print("\n📋 Pending Reports:")
    print("-" * 60)
    
    verified = get_verified_reports(tracker)
    if verified:
        print("\n✅ VERIFIED Reports (ready to submit):")
        for r in verified:
            print(f"  [{r['id']}] {r['program']} - {r['vulnerability']} ({r['severity']})")
            print(f"         {r['report_file']}")
    else:
        print("\n⚠️ No verified reports found")
    
    pending = [r for r in tracker if r["status"] == "pending" and not r.get("report_file", "").startswith("reports/VERIFIED_")]
    if pending:
        print(f"\n⏳ Other Pending ({len(pending)} reports):")
        for r in pending[:10]:
            print(f"  [{r['id']}] {r['program']} - {r['vulnerability']}")

def update_tracker_report(report_id, new_status):
    """Update report status in tracker"""
    tracker = load_tracker()
    for r in tracker:
        if r["id"] == report_id:
            r["status"] = new_status
            r["last_updated"] = time.strftime("%Y-%m-%d")
            break
    save_tracker(tracker)

def main():
    parser = argparse.ArgumentParser(description="SARAhack Auto-Submit via Local Freebuff")
    parser.add_argument("command", choices=["test", "submit", "list"], help="Command")
    parser.add_argument("--report", type=int, help="Submit specific report ID")
    parser.add_argument("--all", action="store_true", help="Submit all verified reports")
    parser.add_argument("--dry-run", action="store_true", help="Preview without submitting")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed output")
    parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompt")
    args = parser.parse_args()
    
    try:
        get_config()
    except ValueError as e:
        print(f"[-] Configuration error: {e}")
        return 1
    
    if args.command == "test":
        success = test_freebuff()
        return 0 if success else 1
    
    elif args.command == "list":
        tracker = load_tracker()
        list_pending_reports(tracker)
        return 0
    
    elif args.command == "submit":
        tracker = load_tracker()
        
        reports_to_submit = []
        
        if args.report:
            for r in tracker:
                if r["id"] == args.report:
                    reports_to_submit = [r]
                    break
            if not reports_to_submit:
                print(f"[-] Report #{args.report} not found")
                return 1
        elif args.all:
            reports_to_submit = get_verified_reports(tracker)
            if not reports_to_submit:
                print("[-] No verified reports to submit")
                return 1
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
            
            if not args.dry_run:
                print("[*] Waiting 60s before next submission...")
                time.sleep(60)
        
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