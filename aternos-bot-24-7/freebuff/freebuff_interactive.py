#!/usr/bin/env python3
"""
SARAhack - Interactive SSH to freebuff using Paramiko + Screen
Creates a persistent PTY session for freebuff browser automation
"""

import sys
import time
import signal
import os
import socket
from pathlib import Path

# Server configuration (NEW tmate session)
TMATE_HOST = "lon1.tmate.io"
TMATE_USER = "eS6fytCGPu74pDmMNxAKcszLc"
SSH_KEY_FILE = os.path.expanduser("~/.ssh/id_ed25519")

def signal_handler(sig, frame):
    print("\n[!] Interrupted. Cleaning up...")
    sys.exit(0)

def run_freebuff_command(cmd: str, timeout: int = 60) -> tuple[bool, str]:
    """Run a command via SSH with PTY using paramiko invoke_shell"""
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
        channel.settimeout(timeout)
        
        # No SECRET needed for tmate
        time.sleep(0.5)  # Wait for connection
        
        # Send command
        channel.send(cmd + '\n')
        time.sleep(2)
        
        # Read output
        output = ''
        while True:
            try:
                data = channel.recv(4096).decode('utf-8', errors='ignore')
                if not data:
                    break
                output += data
                if 'root@' in output or '$' in output:
                    # Shell prompt - command done
                    if 'freebuff' not in cmd or output.count('\n') > 50:
                        break
            except socket.timeout:
                break
        
        channel.close()
        client.close()
        
        return (True, output)
        
    except Exception as e:
        return (False, str(e))

def send_to_screen(session_name: str, cmd: str) -> bool:
    """Send command to a screen session"""
    success, output = run_freebuff_command(f'screen -S {session_name} -X stuff "{cmd}\\n"')
    return success

def create_screen_session(session_name: str) -> bool:
    """Create a detached screen session"""
    success, output = run_freebuff_command(f'screen -dmS {session_name}')
    return success

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 freebuff_interactive.py <command>")
        print("Example: python3 freebuff_interactive.py 'freebuff login'")
        sys.exit(1)
    
    cmd = " ".join(sys.argv[1:])
    
    print(f"[*] Connecting to {SERVER}...")
    print(f"[*] Executing: {cmd}")
    
    success, output = run_freebuff_command(cmd, timeout=120)
    
    print("\n" + "="*50)
    if success:
        print("[+] Command executed successfully")
    else:
        print("[-] Command failed")
    print("="*50)
    print("\nOutput:")
    print(output[:5000] if len(output) > 5000 else output)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    main()