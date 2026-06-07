#!/usr/bin/env python3
"""
SARAhack Auto-Submit Script
ใช้ freebuff AI สำหรับ submit reports อัตโนมัติ

Usage:
    python3 auto_submit.py --platform hackerone --program stripe --report reports/drafts/stripe_cors.md
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

# Server configuration
SERVER = "8lgm.segfault.net"
SECRET = "JEpUOZPOVhCTwdhQInbJTtNA"

def ssh_to_server(command: str) -> tuple[bool, str]:
    """Execute command on remote server via SSH"""
    ssh_cmd = [
        "ssh",
        "-o", "SetEnv=SECRET=" + SECRET,
        "-o", "StrictHostKeyChecking=no",
        f"root@{SERVER}",
        command
    ]
    
    try:
        result = subprocess.run(
            ssh_cmd,
            capture_output=True,
            text=True,
            timeout=120
        )
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, "SSH command timed out"
    except Exception as e:
        return False, str(e)

def submit_via_freebuff(platform: str, program: str, report_content: str) -> bool:
    """Submit report using freebuff AI"""
    
    # Escape report content for safe SSH transfer
    report_escaped = report_content.replace('"', '\\"').replace('$', '\\$').replace('`', '\\`')
    
    # Prepare freebuff command using heredoc over SSH
    ssh_cmd = [
        "ssh",
        "-o", "SetEnv=SECRET=" + SECRET,
        "-o", "StrictHostKeyChecking=no",
        f"root@{SERVER}"
    ]
    
    # Use heredoc to safely transfer script
    heredoc = f'''cat << 'FREEBUFF_EOF' > /tmp/freebuff_submit.sh
#!/bin/bash
freebuff "Login to {platform}, navigate to {program} program, and submit this CORS report: {report_escaped[:1500]}..."
FREEBUFF_EOF
bash /tmp/freebuff_submit.sh'''
    
    try:
        result = subprocess.run(
            ssh_cmd,
            input=heredoc,
            capture_output=True,
            text=True,
            timeout=180
        )
        return result.returncode == 0
    except Exception as e:
        print(f"[-] SSH error: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="SARAhack Auto-Submit")
    parser.add_argument('--platform', required=True, help='Platform: hackerone, bugcrowd')
    parser.add_argument('--program', required=True, help='Bug bounty program name')
    parser.add_argument('--report', required=True, help='Path to report file (.md)')
    parser.add_argument('--test', action='store_true', help='Test connection only')
    
    args = parser.parse_args()
    
    print(f"Platform: {args.platform}")
    print(f"Program: {args.program}")
    
    if args.test:
        print("[*] Testing server connection...")
        success, output = ssh_to_server("echo OK")
        if success:
            print("[+] Server connection OK")
            print(f"   Output: {output.strip()}")
        else:
            print("[-] Server connection failed")
            print(f"   Error: {output}")
        return
    
    # Read report file
    report_path = Path(args.report)
    if not report_path.exists():
        print(f"[-] Report file not found: {args.report}")
        return
    
    with open(report_path, 'r') as f:
        report_content = f.read()
    
    print(f"[*] Report loaded: {len(report_content)} characters")
    print("[*] Submitting via freebuff AI...")
    
    success = submit_via_freebuff(args.platform, args.program, report_content)
    
    if success:
        print("[+] Report submitted successfully!")
    else:
        print("[-] Failed to submit via freebuff")
        print("[*] Try manual submission:")
        print(f"    python3 scripts/manual_submit.sh --platform {args.platform} --program {args.program} --file {args.report}")

if __name__ == "__main__":
    main()