#!/bin/bash
# SARAhack - Complete Setup for tmate Session
# Run this script on your tmate session after connecting
# SSH: eS6fytCGPu74pDmMNxAKcszLc@lon1.tmate.io

set -e

echo "=========================================="
echo "SARAhack - tmate Session Setup"
echo "=========================================="
echo ""

# Step 1: Load tokenlogin environment
echo "[*] Step 1: Loading tokenlogin configuration..."
if [ -f "$HOME/workspace/freebuff/tokenlogin.env" ]; then
    source "$HOME/workspace/freebuff/tokenlogin.env"
    echo "[+] Tokenlogin loaded"
else
    echo "[!] Warning: tokenlogin.env not found"
fi

# Step 2: Install freebuff if not present
echo ""
echo "[*] Step 2: Checking freebuff installation..."
if ! command -v freebuff &> /dev/null; then
    echo "[*] Installing freebuff..."
    npm install -g freebuff
    echo "[+] Freebuff installed"
else
    echo "[+] Freebuff already installed: $(which freebuff)"
fi

# Step 3: Install Python dependencies
echo ""
echo "[*] Step 3: Installing Python dependencies..."
pip3 install paramiko requests bs4 colorama termcolor --quiet
echo "[+] Python dependencies installed"

# Step 4: Configure Minimax M2.7 model
echo ""
echo "[*] Step 4: Configuring Minimax M2.7 model..."
export AI_MODEL="minimax/minimax-m2.7"
export CODEBUFF_MODEL="minimax-m2.7"
echo "[+] Minimax M2.7 configured"

# Step 5: Verify everything
echo ""
echo "[*] Step 5: Verifying installation..."
echo "    - freebuff: $(which freebuff || echo 'not found')"
echo "    - python3: $(which python3)"
echo "    - paramiko: $(python3 -c 'import paramiko; print(paramiko.__version__)' 2>/dev/null || echo 'not installed')"
echo "    - AI Model: $AI_MODEL"
echo ""

echo "[+] Setup complete!"
echo ""
echo "=========================================="
echo "Available Commands:"
echo "=========================================="
echo "1. freebuff login"
echo "2. freebuff submit 'your report content'"
echo "3. python3 auto_submit_reports.py --all"
echo ""
echo "To use Minimax M2.7 model:"
echo "    export AI_MODEL=\"minimax/minimax-m2.7\""
echo "=========================================="