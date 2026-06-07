#!/usr/bin/env python3
"""
SARAhack - Submit reports via freebuff
Freebuff is an interactive AI tool - this script handles multi-turn conversation
"""

import os
import sys
import time
import signal
import socket

TMATE_HOST = "lon1.tmate.io"
TMATE_USER = "eS6fytCGPu74pDmMNxAKcszLc"
SSH_KEY_FILE = os.path.expanduser("~/.ssh/id_ed25519")

def signal_handler(sig, frame):
    print("\n[!] Interrupted.")
    sys.exit(0)

def submit_report_via_freebuff(report_path: str, platform: str = "hackerone", program: str = "cloudflare") -> tuple[bool, str]:
    """Submit a report using freebuff - handles AI responses, not shell prompts"""
    import paramiko
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # Connect using SSH key
        client.connect(
            hostname=TMATE_HOST,
            username=TMATE_USER,
            key_filename=SSH_KEY_FILE,
            look_for_keys=False,
            allow_agent=False,
            compress=False,  # Disable compression for tmate compatibility
            timeout=30
        )
        
        # Use invoke_shell for true PTY
        channel = client.invoke_shell()
        channel.settimeout(5)  # Short timeout for recv iterations
        
        # No SECRET needed for tmate
        time.sleep(0.5)
        
        # Send freebuff login command
        channel.send('freebuff login\n')
        time.sleep(8)  # Wait for freebuff to initialize (can take time)
        
        # Read login response
        output = ''
        for _ in range(20):  # Read for up to 20 iterations
            try:
                data = channel.recv(4096).decode('utf-8', errors='ignore')
                if data:
                    output += data
                    time.sleep(1)
                else:
                    time.sleep(1)
            except socket.timeout:
                time.sleep(1)
        
        print(f"[DEBUG] Login response:\n{output[:2000]}")
        
        # Check if freebuff is ready (look for any prompt or ready signal)
        # freebuff typically shows something like "What can I help you with?" or similar
        
        # Now send the report submission prompt
        submit_prompt = f"""Login to HackerOne and submit a bug bounty report for {program} program. 
The report content is in the file: {report_path}
Read the report content from that file and use it to submit to the {program} bug bounty program on {platform}.

If you need to login to {platform}, use the credentials provided during the freebuff session.
Focus on submitting the report - do not browse the web or do research."""

        # Send in parts if too long
        channel.send(submit_prompt[:500] + '\n')
        time.sleep(3)
        
        # Send remainder
        if len(submit_prompt) > 500:
            channel.send(submit_prompt[500:] + '\n')
        
        # Wait for freebuff to process (longer wait for AI response)
        time.sleep(15)
        
        # Collect response
        output = ''
        for _ in range(30):  # Read for up to 30 iterations
            try:
                data = channel.recv(4096).decode('utf-8', errors='ignore')
                if data:
                    output += data
                    time.sleep(1)
                else:
                    time.sleep(1)
            except socket.timeout:
                break  # Timeout means no more data coming
        
        channel.close()
        client.close()
        
        return (True, output)
        
    except Exception as e:
        return (False, str(e))

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 freebuff_submit.py <report_path> [platform] [program]")
        print("Example: python3 freebuff_submit.py /tmp/cloudflare_ssrf.md hackerone cloudflare")
        sys.exit(1)
    
    report_path = sys.argv[1]
    platform = sys.argv[2] if len(sys.argv) > 2 else "hackerone"
    program = sys.argv[3] if len(sys.argv) > 3 else "cloudflare"
    
    print(f"[*] Connecting to {TMATE_HOST} (tmate session)...")
    print(f"[*] Submitting report: {report_path}")
    print(f"[*] Platform: {platform}, Program: {program}")
    
    success, output = submit_report_via_freebuff(report_path, platform, program)
    
    print("\n" + "="*60)
    if success:
        print("[+] Freebuff session completed")
    else:
        print("[-] Freebuff session failed")
    print("="*60)
    print("\nOutput:")
    print(output[:8000] if len(output) > 8000 else output)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    main()