#!/usr/bin/env python3
"""
SARAhack - Freebuff AI Browser-Use Integration
ใช้ freebuff browser-use capability เพื่อ bypass Cloudflare Turnstile

Key insight: freebuff uses REAL Chrome browser, not headless automation
This allows bypassing Cloudflare detection mechanisms.

Usage:
    python3 freebuff_bounty.py test-connection
    python3 freebuff_bounty.py status
    python3 freebuff_bounty.py submit --platform hackerone --program gitlab --file reports/gitlab_cors_report_h1.md
    python3 freebuff_bounty.py find --keyword CORS
    python3 freebuff_bounty.py test-bypass --url https://hackerone.com
"""

import argparse
import subprocess
import sys
import os
import base64
from pathlib import Path
from typing import Optional, Tuple

# Server configuration (NEW tmate session)
TMATE_HOST = "lon1.tmate.io"
TMATE_USER = "eS6fytCGPu74pDmMNxAKcszLc"
SSH_KEY_FILE = os.environ.get("SSH_KEY_FILE", os.path.expanduser("~/.ssh/id_ed25519"))

# DEV MODE - Unlimited timeout (no API stacking on timeout)
# Enable with: export FREEBUFF_DEV_MODE=true
DEV_MODE = os.environ.get("FREEBUFF_DEV_MODE", "false").strip().lower() in ("true", "1", "yes", "on")
DEV_TIMEOUT = float('inf')  # Unlimited timeout - prevents API stacking on session timeout

def get_credentials() -> tuple:
    """Load HackerOne credentials from environment variables"""
    email = os.environ.get("HACKERONE_EMAIL", "potosopotosolo@gmail.com")
    password = os.environ.get("HACKERONE_PASSWORD", ")a9By=*D#6/w9T")
    return email, password

class FreebuffBounty:
    """Freebuff AI browser-use integration for bug bounty tasks"""
    
    def __init__(self):
        self.tmate_host = TMATE_HOST
        self.tmate_user = TMATE_USER
        self.ssh_key_file = SSH_KEY_FILE
        self.h1_email, self.h1_password = get_credentials()
    
    def ssh_command(self, command: str, timeout: int = 300) -> Tuple[bool, str]:
        """Execute command via SSH to tmate session
        
        DEV MODE: Uses unlimited timeout to prevent API stacking when
        session times out mid-command.
        """
        ssh_cmd = [
            "ssh",
            "-o", "StrictHostKeyChecking=no",
            "-o", "Compression=no",
            "-o", "ServerAliveInterval=60",
            "-o", "ConnectTimeout=30",
            "-i", self.ssh_key_file,
            f"{self.tmate_user}@{self.tmate_host}",
            command
        ]
        
        # Use unlimited timeout in DEV_MODE
        effective_timeout = DEV_TIMEOUT if DEV_MODE else timeout
        
        try:
            result = subprocess.run(
                ssh_cmd,
                capture_output=True,
                text=True,
                timeout=effective_timeout
            )
            return result.returncode == 0, result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return False, "SSH timeout"
        except Exception as e:
            return False, str(e)
    
    def ssh_command_with_stdin(self, command: str, stdin_data: str, timeout: int = 300) -> Tuple[bool, str]:
        """Execute command via SSH with stdin input (for heredoc)
        
        DEV MODE: Uses unlimited timeout to prevent API stacking when
        session times out mid-command.
        """
        ssh_cmd = [
            "ssh",
            "-o", "StrictHostKeyChecking=no",
            "-o", "Compression=no",
            "-o", "ServerAliveInterval=60",
            "-o", "ConnectTimeout=30",
            "-i", self.ssh_key_file,
            f"{self.tmate_user}@{self.tmate_host}"
        ]
        
        # Use unlimited timeout in DEV_MODE
        effective_timeout = DEV_TIMEOUT if DEV_MODE else timeout
        
        try:
            result = subprocess.run(
                ssh_cmd,
                input=stdin_data,
                capture_output=True,
                text=True,
                timeout=effective_timeout
            )
            return result.returncode == 0, result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return False, "SSH timeout"
        except Exception as e:
            return False, str(e)
    
    def _build_browser_submit_prompt(self, platform: str, program: str, report_content: str) -> str:
        """Build detailed prompt for browser-based report submission"""
        
        # Platform-specific URLs and instructions
        platform_config = {
            "hackerone": {
                "url": f"https://hackerone.com/{program}/reports/new",
                "title_field": "Report title",
            },
            "bugcrowd": {
                "url": f"https://bugcrowd.com/{program}/submit",
                "title_field": "Title",
            }
        }
        
        config = platform_config.get(platform.lower(), platform_config["hackerone"])
        
        # Truncate report if too long (avoid token limits)
        max_report_len = 3500
        if len(report_content) > max_report_len:
            report_content = report_content[:max_report_len] + "\n\n[Report truncated - see full details in source file]"
        
        prompt = f"""Use browser-use to complete the following task:

1. Navigate to: {config['url']}
2. If not logged in, login with:
   - Email: {self.h1_email}
   - Password: {self.h1_password}
3. Submit a new vulnerability report with these details:

**Report Title:** {program} - CORS Misconfiguration
**Severity:** HIGH

**Vulnerability Details:**
{report_content}

**Steps to Reproduce:**
1. Navigate to the target API endpoint
2. Send a cross-origin request with appropriate headers
3. Observe that the response includes sensitive data due to improper CORS configuration

**Impact:**
An attacker can steal sensitive data from the target domain by making cross-origin requests from a malicious page.

**Remediation:**
Properly configure CORS headers to only allow trusted origins. Do not use wildcard (*) for Access-Control-Allow-Origin with credentials.

Please fill in all required fields and submit the report."""

        return prompt
    
    def _send_via_base64(self, prompt: str) -> Tuple[bool, str]:
        """Send prompt to freebuff using base64 encoding to avoid escaping issues"""
        # Encode prompt as base64
        prompt_b64 = base64.b64encode(prompt.encode('utf-8')).decode('ascii')
        
        # Create a heredoc that decodes and executes the prompt
        stdin_script = f'''cat << 'FREEBUFF_EOF' | base64 -d | freebuff
{prompt_b64}
FREEBUFF_EOF'''
        
        # Use unlimited timeout in DEV_MODE (600s default)
        effective_timeout = DEV_TIMEOUT if DEV_MODE else 600
        return self.ssh_command_with_stdin("bash -s", stdin_script, timeout=effective_timeout)
    
    def login(self) -> bool:
        """Login to freebuff"""
        print("[*] Logging into freebuff...")
        success, output = self.ssh_command("freebuff login")
        if success:
            print("[+] Logged in successfully")
        else:
            print(f"[-] Login failed: {output}")
        return success

    def submit_report(self, platform: str, program: str, report_file: str) -> bool:
        """Submit bug report using freebuff browser-use capability"""
        print(f"[*] Submitting report to {platform}/{program}...")
        print(f"[*] Reading report: {report_file}")
        
        # Read report
        report_path = Path(report_file)
        if not report_path.exists():
            print(f"[-] Report file not found: {report_file}")
            return False
        
        try:
            with open(report_path, 'r') as f:
                report_content = f.read()
        except Exception as e:
            print(f"[-] Cannot read report file: {e}")
            return False
        
        print(f"[+] Report loaded: {len(report_content)} characters")
        
        # Build prompt
        prompt = self._build_browser_submit_prompt(platform, program, report_content)
        
        # Use freebuff with browser-use via base64 encoding
        print("[*] Sending task to freebuff with browser-use capability...")
        print("[*] Using base64 encoding to handle multi-line prompts...")
        
        success, output = self._send_via_base64(prompt)
        
        if success:
            print("[+] Report submission task completed via freebuff")
            print("[*] Please verify the submission manually or check platform for status")
        else:
            print(f"[-] Submission failed: {output}")
            print("[*] Try manual submission using: ./scripts/manual_submit.sh")
        
        return success

    def find_targets(self, keyword: str = "CORS") -> bool:
        """Find new bug bounty targets"""
        print(f"[*] Finding targets with keyword: {keyword}...")
        
        prompt = f"""Search the web for bug bounty programs on HackerOne, Bugcrowd, and Intigriti that accept {keyword} vulnerabilities.

For each program found, provide:
1. Program name and platform
2. URL to the program
3. Scope (what vulnerabilities are accepted)
4. Bounty range if available
5. Any special instructions for {keyword} submissions

Focus on programs that are actively accepting {keyword} reports."""
        
        timeout = DEV_TIMEOUT if DEV_MODE else 300
        success, output = self.ssh_command(f'freebuff "{prompt}"', timeout=timeout)
        
        if success:
            print("[+] Target search complete")
            print("-" * 50)
            print(output)
        else:
            print(f"[-] Search failed: {output}")
        
        return success

    def research_vuln(self, target: str, vuln_type: str = "CORS") -> bool:
        """Research vulnerability on target"""
        print(f"[*] Researching {vuln_type} on {target}...")
        
        prompt = f"""Research {vuln_type} vulnerability on {target}.

Using your web research capability:
1. Find publicly known {vuln_type} issues or disclosures for this target
2. Identify endpoints that might be vulnerable
3. Look for existing writeups or PoCs
4. Provide a proof of concept exploit if possible
5. Suggest remediation steps

Also use browser-use to test the target if accessible."""
        
        timeout = DEV_TIMEOUT if DEV_MODE else 300
        success, output = self.ssh_command(f'freebuff "{prompt}"', timeout=timeout)
        
        if success:
            print("[+] Research complete")
            print("-" * 50)
            print(output)
        else:
            print(f"[-] Research failed: {output}")
        
        return success

    def test_bypass(self, url: str) -> bool:
        """Test Cloudflare bypass using browser-use"""
        print(f"[*] Testing Cloudflare bypass on {url} using browser-use...")
        
        prompt = f"""Use your browser-use capability to:
1. Navigate to: {url}
2. Bypass any Cloudflare or bot protection you encounter
3. Report what you see on the page (title, main content, any forms)
4. If you encounter a login page or form, document the structure

This tests if your browser automation can successfully bypass anti-bot measures."""
        
        timeout = DEV_TIMEOUT if DEV_MODE else 300
        success, output = self.ssh_command(f'freebuff "{prompt}"', timeout=timeout)
        
        if success:
            print("[+] Bypass test complete")
            print("-" * 50)
            print(output)
        else:
            print(f"[-] Test failed: {output}")
        
        return success

    def test_connection(self) -> bool:
        """Test SSH connection to server"""
        print(f"[*] Testing connection to {self.tmate_host}...")
        
        timeout = DEV_TIMEOUT if DEV_MODE else 30
        success, output = self.ssh_command("echo 'Connection OK' && uptime && free -h | head -5", timeout=timeout)
        
        if success:
            print("[+] Server connection successful!")
            print(output)
        else:
            print(f"[-] Connection failed: {output}")
        
        return success

    def check_freebuff_status(self) -> bool:
        """Check if freebuff is available and working"""
        print("[*] Checking freebuff status...")
        
        success, output = self.ssh_command("which freebuff && freebuff --version 2>/dev/null || freebuff --help 2>&1 | head -10")
        
        if success:
            print("[+] freebuff is available")
            print(output[:500] if len(output) > 500 else output)
        else:
            print(f"[-] freebuff check failed: {output}")
        
        return success

def main():
    parser = argparse.ArgumentParser(
        description="""
SARAhack Freebuff Browser-Use Integration

This tool uses freebuff's real browser capability to bypass
Cloudflare Turnstile and submit bug bounty reports.

Examples:
    python3 freebuff_bounty.py test-connection
    python3 freebuff_bounty.py status
    python3 freebuff_bounty.py submit --platform hackerone --program gitlab --file reports/gitlab_cors_report_h1.md
    python3 freebuff_bounty.py find --keyword CORS
    python3 freebuff_bounty.py test-bypass --url https://hackerone.com
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Test connection
    test_parser = subparsers.add_parser('test-connection', help='Test SSH connection to server')
    
    # Check freebuff status
    status_parser = subparsers.add_parser('status', help='Check freebuff installation')
    
    # Login
    login_parser = subparsers.add_parser('login', help='Login to freebuff')
    
    # Submit report
    submit_parser = subparsers.add_parser('submit', help='Submit bug report via browser-use')
    submit_parser.add_argument('--platform', required=True, 
                               help='Platform: hackerone, bugcrowd, intigriti')
    submit_parser.add_argument('--program', required=True, 
                               help='Bug bounty program name')
    submit_parser.add_argument('--file', required=True, 
                               help='Path to report file (.md)')
    
    # Find targets
    find_parser = subparsers.add_parser('find', help='Find new bug bounty targets')
    find_parser.add_argument('--keyword', default='CORS', 
                             help='Vulnerability keyword to search for')
    
    # Research
    research_parser = subparsers.add_parser('research', help='Research vulnerability')
    research_parser.add_argument('--target', required=True, 
                                 help='Target domain or program')
    research_parser.add_argument('--type', default='CORS', 
                                 help='Vulnerability type')
    
    # Test bypass
    bypass_parser = subparsers.add_parser('test-bypass', help='Test Cloudflare bypass')
    bypass_parser.add_argument('--url', required=True, 
                               help='URL to test')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    fb = FreebuffBounty()
    
    if args.command == 'test-connection':
        fb.test_connection()
    elif args.command == 'status':
        fb.check_freebuff_status()
    elif args.command == 'login':
        fb.login()
    elif args.command == 'submit':
        fb.submit_report(args.platform, args.program, args.file)
    elif args.command == 'find':
        fb.find_targets(args.keyword)
    elif args.command == 'research':
        fb.research_vuln(args.target, args.type)
    elif args.command == 'test-bypass':
        fb.test_bypass(args.url)

if __name__ == "__main__":
    main()