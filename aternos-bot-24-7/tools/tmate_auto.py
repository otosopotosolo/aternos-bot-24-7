#!/usr/bin/env python3
"""
SARAhack - Tmate Session Automation using PTY
Uses Python's pty module to automate interactive tmate sessions for freebuff

Usage:
    python3 tools/tmate_auto.py connect
    python3 tools/tmate_auto.py send "freebuff --version"
    python3 tools/tmate_auto.py freebuff "navigate to hackerone.com"
    python3 tools/tmate_auto.py submit --program rollbar --report reports/drafts/draft_rollbar_cors.md
"""

import os
import sys
import time
import subprocess
import argparse
import signal
from pathlib import Path

# Configuration from ssh_temp.env
TMATE_HOST = "lon1.tmate.io"
TMATE_USER = "eS6fytCGPu74pDmMNxAKcszLc"
SECRET = "EUwteWtAugwWBPqCIUWcuVGq"

# Reports directory
REPORTS_DIR = Path(__file__).parent.parent / "reports"
DRAFTS_DIR = REPORTS_DIR / "drafts"


class TmateAutomator:
    """Automate tmate sessions using PTY for real interactive terminal"""
    
    def __init__(self):
        self.process = None
        self.output_buffer = ""
        
    def connect(self, timeout=30):
        """Connect to tmate session with PTY"""
        print("[*] Connecting to tmate session...")
        
        # Build SSH command with SECRET
        ssh_cmd = [
            "ssh",
            "-o", "StrictHostKeyChecking=no",
            "-o", "ServerAliveInterval=60",
            "-o", "ServerAliveCountMax=5",
            "-o", "SetEnv", f"SECRET={SECRET}",
            "-tt",  # Force pseudo-terminal
            f"{TMATE_USER}@{TMATE_HOST}"
        ]
        
        print(f"[*] Running: {' '.join(ssh_cmd)}")
        
        # Use PTY for interactive session
        self.process = subprocess.Popen(
            ssh_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            universal_newlines=True
        )
        
        # Wait for connection
        time.sleep(timeout)
        
        return self.process.poll() is None
    
    def send_command(self, command, wait=5):
        """Send command to tmate session and wait for response"""
        if not self.process or self.process.poll() is not None:
            print("[!] Not connected to tmate session")
            return None
        
        print(f"[*] Sending: {command}")
        
        # Send command with newline
        self.process.stdin.write(command + "\n")
        self.process.stdin.flush()
        
        # Wait for response
        time.sleep(wait)
        
        # Read output
        try:
            # Read whatever is available
            output = ""
            if self.process.stdout:
                import select
                while True:
                    ready, _, _ = select.select([self.process.stdout], [], [], 0.1)
                    if ready:
                        char = self.process.stdout.read(1)
                        if char:
                            output += char
                        else:
                            break
                    else:
                        break
            return output
        except:
            return ""
    
    def send_freebuff(self, prompt, timeout=300):
        """Send task to freebuff via tmate session"""
        print(f"[*] Sending to freebuff: {prompt[:50]}...")
        
        # Escape prompt for shell
        escaped_prompt = prompt.replace('"', '\\"').replace('$', '\\$').replace('`', '\\`')
        
        # Create freebuff command
        cmd = f'freebuff "{escaped_prompt}"'
        
        # Send command
        self.send_command(cmd, wait=10)
        
        # Wait for freebuff to process
        print(f"[*] Waiting {timeout}s for freebuff response...")
        time.sleep(timeout)
        
        # Collect output
        output = self.collect_output()
        
        return output
    
    def collect_output(self, max_lines=100):
        """Collect output from the session"""
        output = []
        try:
            import select
            if self.process.stdout:
                while len(output) < max_lines:
                    ready, _, _ = select.select([self.process.stdout], [], [], 0.5)
                    if ready:
                        line = self.process.stdout.readline()
                        if line:
                            output.append(line)
                        else:
                            break
                    else:
                        break
        except:
            pass
        return '\n'.join(output)
    
    def close(self):
        """Close the tmate session"""
        if self.process:
            print("[*] Closing tmate session...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except:
                self.process.kill()


def test_connection():
    """Test tmate connection"""
    print("[*] Testing tmate connection...")
    automator = TmateAutomator()
    
    if automator.connect(timeout=15):
        print("[+] Connected to tmate!")
        
        # Send test command
        output = automator.send_command("echo 'Hello from tmate!'", wait=3)
        print(f"Output: {output[:200] if output else 'No output'}")
        
        # Check for freebuff
        output = automator.send_command("which freebuff 2>/dev/null || echo 'freebuff not found'", wait=3)
        print(f"freebuff check: {output[:200] if output else 'No output'}")
        
        automator.close()
        return True
    else:
        print("[!] Failed to connect to tmate")
        return False


def submit_report(program, report_file):
    """Submit report using freebuff via tmate"""
    print(f"[*] Submitting {program} report via freebuff...")
    
    # Load report
    report_path = Path(report_file)
    if not report_path.exists():
        report_path = DRAFTS_DIR / Path(report_file).name
    
    if not report_path.exists():
        print(f"[!] Report not found: {report_file}")
        return False
    
    with open(report_path, 'r') as f:
        report_content = f.read()
    
    # Parse report
    lines = report_content.split('\n')
    title = None
    description = []
    
    for line in lines:
        if not title and line.startswith('# '):
            title = line[2:].strip()
        elif line.startswith('## ') or line.startswith('**'):
            continue
        elif line.strip():
            description.append(line)
    
    if not title:
        title = f"{program.upper()} - CORS Misconfiguration"
    
    # Build freebuff prompt
    prompt = f'''Navigate to https://hackerone.com/{program}/reports/new
Login with email potsopotosolo@gmail.com and password )a9By=*D#6/w9T
Fill the bug report:
- Title: {title}
- Severity: HIGH
- Description: {" ".join(description[:20])}...

Submit the report and confirm success.'''
    
    # Connect and send
    automator = TmateAutomator()
    
    if not automator.connect(timeout=20):
        print("[!] Failed to connect to tmate")
        return False
    
    # Send to freebuff
    output = automator.send_freebuff(prompt, timeout=180)
    
    automator.close()
    
    print(f"[*] Response: {output[:500] if output else 'No response'}")
    
    return "success" in output.lower() or "submitted" in output.lower()


def main():
    parser = argparse.ArgumentParser(description="SARAhack - Tmate Session Automation")
    parser.add_argument('command', choices=['connect', 'send', 'freebuff', 'submit', 'test'])
    parser.add_argument('--program', help='Program name')
    parser.add_argument('--report', help='Report file path')
    parser.add_argument('--timeout', type=int, default=180, help='Timeout for freebuff')
    
    args = parser.parse_args()
    
    if args.command == 'test':
        test_connection()
    elif args.command == 'connect':
        automator = TmateAutomator()
        if automator.connect():
            print("[+] Connected! Press Ctrl+C to exit")
            try:
                while True:
                    cmd = input("tmate> ")
                    if cmd.lower() in ['exit', 'quit']:
                        break
                    output = automator.send_command(cmd)
                    print(output)
            except KeyboardInterrupt:
                pass
            automator.close()
        else:
            print("[!] Connection failed")
    elif args.command == 'send':
        if len(sys.argv) < 3:
            print("Usage: tmate_auto.py send <command>")
            return
        automator = TmateAutomator()
        if automator.connect():
            output = automator.send_command(sys.argv[2])
            print(output)
            automator.close()
    elif args.command == 'freebuff':
        if len(sys.argv) < 3:
            print("Usage: tmate_auto.py freebuff <prompt>")
            return
        automator = TmateAutomator()
        if automator.connect():
            output = automator.send_freebuff(sys.argv[2], timeout=args.timeout)
            print(output)
            automator.close()
    elif args.command == 'submit':
        if not args.program or not args.report:
            print("[!] Usage: tmate_auto.py submit --program <name> --report <file>")
            return
        success = submit_report(args.program, args.report)
        if success:
            print("[+] Report submitted successfully!")
        else:
            print("[!] Report submission failed")


if __name__ == "__main__":
    main()