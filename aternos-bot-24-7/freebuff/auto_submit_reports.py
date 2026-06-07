#!/usr/bin/env python3
"""
SARAhack - Automated Freebuff Report Submission (v2)

This script automates submission of bug bounty reports via freebuff.
Uses invoke_shell() for proper PTY interaction with freebuff's AI model.

Usage:
    python3 auto_submit_reports.py [--dry-run] [--report N] [--all]

Environment:
    FREEBuff_API_TOKEN or CODEBUFF_POSTHOG_API_KEY - Freebuff token  
    SERVER_HOST - SSH host (default: lon1.tmate.io - tmate session)
"""

import os
import sys
import time
import argparse
from pathlib import Path

try:
    import paramiko
except ImportError:
    print("Installing paramiko...")
    os.system("pip3 install paramiko --quiet")
    import paramiko

# Configuration from environment or defaults
# Use tmate session for permanent connection
SERVER_HOST = os.environ.get("TMATE_HOST", "lon1.tmate.io")
SERVER_USER = os.environ.get("TMATE_USER", "eS6fytCGPu74pDmMNxAKcszLc")
SSH_KEY_FILE = os.environ.get("SSH_KEY_FILE", os.path.expanduser("~/.ssh/id_ed25519"))
FREEBuff_TOKEN = os.environ.get("CODEBUFF_POSTHOG_API_KEY", "be0e3e50-e07c-434d-98d0-85d6c59d615c")
FREEBuff_EMAIL = os.environ.get("HACKERONE_EMAIL", "potosopotosolo@gmail.com")

# DEV MODE - Unlimited timeout (no API stacking on timeout)
# Enable with: export FREEBUFF_DEV_MODE=true
DEV_MODE = os.environ.get("FREEBUFF_DEV_MODE", "false").strip().lower() in ("true", "1", "yes", "on")
DEV_TIMEOUT = float('inf')  # Unlimited timeout - prevents API stacking on session timeout

# Reports ready for submission (from tracker)
REPORTS_READY = [
    {
        "id": 2,
        "program": "Cloudflare",
        "platform": "HackerOne", 
        "vuln": "SSRF",
        "severity": "HIGH",
        "local_file": "reports/new_cloudflare_ssrf.md",
        "server_file": "/tmp/cloudflare_ssrf.md",
        "prompt": "Login to HackerOne and submit the Cloudflare SSRF report to the Cloudflare program. Use the report content from /tmp/cloudflare_ssrf.md"
    },
    {
        "id": 3,
        "program": "Uber",
        "platform": "HackerOne",
        "vuln": "IDOR", 
        "severity": "HIGH",
        "local_file": "reports/new_uber_idor.md",
        "server_file": "/tmp/new_uber_idor.md",
        "prompt": "Login to HackerOne and submit the Uber IDOR report to the Uber program. Use the report content from /tmp/new_uber_idor.md"
    },
    {
        "id": 4,
        "program": "Shopify",
        "platform": "HackerOne",
        "vuln": "IDOR",
        "severity": "HIGH",
        "local_file": "reports/new_shopify_idor.md",
        "server_file": "/tmp/new_shopify_idor.md", 
        "prompt": "Login to HackerOne and submit the Shopify IDOR report to the Shopify program. Use the report content from /tmp/new_shopify_idor.md"
    },
    {
        "id": 5,
        "program": "Coinbase",
        "platform": "HackerOne",
        "vuln": "CORS",
        "severity": "HIGH",
        "local_file": "reports/new_coinbase_cors.md",
        "server_file": "/tmp/new_coinbase_cors.md",
        "prompt": "Login to HackerOne and submit the Coinbase CORS report to the Coinbase program. Use the report content from /tmp/new_coinbase_cors.md"
    },
    {
        "id": 6,
        "program": "GitLab",
        "platform": "HackerOne",
        "vuln": "IDOR",
        "severity": "HIGH",
        "local_file": "reports/new_gitlab_idor.md",
        "server_file": "/tmp/new_gitlab_idor.md",
        "prompt": "Login to HackerOne and submit the GitLab IDOR report to the GitLab program. Use the report content from /tmp/new_gitlab_idor.md"
    },
    {
        "id": 8,
        "program": "GitLab",
        "platform": "HackerOne",
        "vuln": "CORS",
        "severity": "Informational",
        "local_file": "reports/new_gitlab_cors_advisories.md",
        "server_file": "/tmp/new_gitlab_cors_advisories.md",
        "prompt": "Login to HackerOne and submit the GitLab CORS report to the GitLab program. Use the report content from /tmp/new_gitlab_cors_advisories.md"
    }
]

class FreebuffSession:
    """Interactive freebuff session using PTY via invoke_shell()"""
    
    def __init__(self, ssh_client):
        self.ssh = ssh_client
        self.channel = None
        self.output_buffer = ""
        
    def open(self):
        """Open interactive PTY session"""
        transport = self.ssh.get_transport()
        self.channel = transport.open_session()
        self.channel.setblocking(0)
        self.channel.get_pty(width=200, height=80)
        self.channel.invoke_shell()
        time.sleep(1)
        self._collect_output(timeout=5)
        
    def close(self):
        """Close the session"""
        if self.channel:
            self.channel.close()
            
    def _collect_output(self, timeout=10):
        """Collect output from the channel"""
        output = []
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.channel.recv_ready():
                data = self.channel.recv(4096).decode('utf-8', errors='ignore')
                output.append(data)
            time.sleep(0.2)
        
        self.output_buffer += ''.join(output)
        return ''.join(output)
    
    def send(self, cmd, wait_time=2):
        """Send command and wait"""
        self.channel.send(cmd + "\n")
        time.sleep(wait_time)
        
    def send_and_wait_response(self, cmd, wait_time=60, poll_interval=2):
        """Send command and wait for response
        
        DEV MODE: When FREEBUFF_DEV_MODE=true, uses unlimited timeout to prevent
        API stacking when session times out mid-command. The loop keeps polling
        until no more data is received (channel closes or timeout).
        """
        self.output_buffer = ""
        self.send(cmd, wait_time=wait_time)
        
        # Poll for response
        output = []
        start_time = time.time()
        
        # Use unlimited timeout in DEV_MODE to prevent API stacking on timeout
        effective_timeout = DEV_TIMEOUT if DEV_MODE else wait_time
        
        while True:
            elapsed = time.time() - start_time
            # Check timeout (skip check if DEV_MODE / infinite timeout)
            if not DEV_MODE and elapsed >= effective_timeout:
                break
            
            if self.channel.recv_ready():
                data = self.channel.recv(4096).decode('utf-8', errors='ignore')
                output.append(data)
                start_time = time.time()  # Reset on activity
        else:
            # No data received - check if we should exit
            if not DEV_MODE and elapsed >= poll_interval * 2:
                # In normal mode, exit if no activity for 2x poll_interval
                break
            elif DEV_MODE:
                # In DEV_MODE: exit only if channel likely closed (60s no activity AND no pending data)
                if elapsed > 60 and not self.channel.recv_ready():
                    break
            time.sleep(poll_interval)
        
        result = ''.join(output)
        self.output_buffer = result
        return result
    
    def is_ready(self):
        """Check if freebuff is ready for input"""
        self._collect_output(timeout=2)
        # Look for prompt indicators that appear at end of freebuff output
        # Freebuff typically shows '>' or '>>>' when ready
        ready_patterns = ['>>>', '>> ', '\n> ', 'freebuff>']
        for pattern in ready_patterns:
            if pattern in self.output_buffer:
                return True
        # Also check for common ready phrases
        ready_phrases = ['what would you like', 'what can i help', 'enter your']
        return any(phrase in self.output_buffer.lower()[-500:] for phrase in ready_phrases)
    
    def get_full_output(self):
        """Get all buffered output"""
        output = self._collect_output(timeout=3)
        # Limit buffer size to prevent memory issues
        self.output_buffer = self.output_buffer[-10000:]
        return output


def copy_reports_to_server(ssh_client):
    """Copy all report files to the server"""
    print("[*] Copying reports to server...")
    
    script_dir = Path(__file__).parent.parent
    sftp = ssh_client.open_sftp()
    
    for report in REPORTS_READY:
        local_file = script_dir / report["local_file"]
        if local_file.exists():
            print(f"  - {local_file.name}...")
            sftp.put(str(local_file), report["server_file"])
        else:
            print(f"  [!] Missing: {local_file}")
    
    sftp.close()
    print("[+] Reports copied")


def login_freebuff(session):
    """Login to freebuff with token and email"""
    print("[*] Logging in to freebuff...")
    
    # Start freebuff with login command
    response = session.send_and_wait_response(
        f"export CODEBUFF_POSTHOG_API_KEY='{FREEBuff_TOKEN}' && freebuff login",
        wait_time=DEV_TIMEOUT if DEV_MODE else 90,
        poll_interval=1  # Check every second for faster response
    )
    print(f"  Initial response: {response[:300]}...")
    
    # Check for email prompt or login completed
    response_lower = response.lower()
    if 'email' in response_lower or 'enter email' in response_lower:
        print("[*] Entering email...")
        response = session.send_and_wait_response(
            FREEBuff_EMAIL,
            wait_time=DEV_TIMEOUT if DEV_MODE else 60,
            poll_interval=1
        )
        print(f"  After email: {response[:300]}...")
    elif 'welcome' in response_lower or 'ready' in response_lower or 'logged in' in response_lower:
        print("[+] Login completed directly")
    
    # Wait for any "waiting" messages (free tier needs time)
    time.sleep(10)
    final_output = session.get_full_output()
    
    # Verify login success
    if any(x in final_output.lower() for x in ['welcome', 'ready', 'logged', 'freebuff']):
        print("[+] Login successful!")
        return True
    
    print("[!] Login verification unclear, proceeding anyway...")
    return True  # Continue anyway, submission will reveal issues


def submit_report(session, report, dry_run=False):
    """Submit a single report via freebuff"""
    print(f"\n{'='*60}")
    print(f"[*] Report #{report['id']}: {report['program']} {report['vuln']}")
    print(f"{'='*60}")
    
    if dry_run:
        print(f"[DRY RUN] Would submit: {report['prompt']}")
        return True
    
    if not session.is_ready():
        print("[!] Freebuff not ready, attempting to reconnect...")
        return False
    
    # Send submission prompt
    print("[*] Sending submission request...")
    response = session.send_and_wait_response(
        report["prompt"],
        wait_time=DEV_TIMEOUT if DEV_MODE else 120,
        poll_interval=2  # Check every 2 seconds
    )
    
    print(f"Response:\n{response[:1500]}...")
    
    # Check for success indicators
    success_indicators = [
        'submitted', 'success', 'report created',
        'thank you', 'confirmed', 'received',
        'created successfully', 'logged'
    ]
    
    success = any(ind in response.lower() for ind in success_indicators)
    
    if success:
        print(f"[+] Report #{report['id']} submitted successfully!")
    else:
        print(f"[!] Report #{report['id']} submission may have failed")
    
    return success


def main():
    parser = argparse.ArgumentParser(description="Auto-submit reports via freebuff")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    parser.add_argument("--report", type=int, help="Submit specific report ID only")
    parser.add_argument("--all", action="store_true", help="Submit all reports")
    parser.add_argument("--skip-copy", action="store_true", help="Skip copying reports to server")
    args = parser.parse_args()
    
    print("="*60)
    print("SARAhack - Automated Freebuff Submission v2")
    print("="*60)
    
    if args.dry_run:
        print("[*] DRY RUN MODE\n")
    
    # Connect to server
    print(f"[*] Connecting to {SERVER_HOST}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # Use SSH key authentication for tmate session
        ssh.connect(
            SERVER_HOST,
            username=SERVER_USER,
            key_filename=SSH_KEY_FILE,
            timeout=30,
            allow_agent=False,
            look_for_keys=False,
            compress=False  # Disable compression for tmate compatibility
        )
        print("[+] Connected to tmate session")
    except Exception as e:
        print(f"[!] Connection failed: {e}")
        return 1
    
    # Copy reports
    if not args.skip_copy and not args.dry_run:
        copy_reports_to_server(ssh)
    
    # Reports to submit
    reports_to_submit = REPORTS_READY
    if args.report:
        reports_to_submit = [r for r in REPORTS_READY if r["id"] == args.report]
        if not reports_to_submit:
            print(f"[!] Report #{args.report} not found")
            return 1
    
    # Open freebuff session
    session = FreebuffSession(ssh)
    
    try:
        print("[*] Opening PTY session...")
        session.open()
        print("[+] PTY session opened")
        
        # Login
        if not args.dry_run:
            if not login_freebuff(session):
                print("[!] Login failed")
                return 1
        
        # Submit reports
        results = []
        for report in reports_to_submit:
            success = submit_report(session, report, dry_run=args.dry_run)
            results.append({
                "id": report["id"],
                "program": report["program"],
                "success": success
            })
            
            if not args.dry_run and success:
                print("[*] Waiting 45 seconds before next submission...")
                time.sleep(45)
        
    finally:
        print("\n[*] Closing session...")
        session.close()
        ssh.close()
    
    # Summary
    print("\n" + "="*60)
    print("SUBMISSION SUMMARY")
    print("="*60)
    for r in results:
        status = "✅" if r["success"] else "❌"
        print(f"  {status} #{r['id']} - {r['program']}")
    
    successful = sum(1 for r in results if r["success"])
    print(f"\nResult: {successful}/{len(results)} submitted")
    
    return 0 if successful == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())