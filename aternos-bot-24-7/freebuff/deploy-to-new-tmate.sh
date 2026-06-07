#!/bin/bash
# ============================================================
# SARAhack - Complete Deploy to New Tmate Session
# ============================================================
# New session: eS6fytCGPu74pDmMNxAKcszLc@lon1.tmate.io
# SSH Key: ~/.ssh/id_ed25519

set -e

echo "============================================================"
echo "SARAhack - Deploy to New Tmate Session"
echo "============================================================"
echo ""

# Variables
TMATE_HOST="lon1.tmate.io"
TMATE_USER="eS6fytCGPu74pDmMNxAKcszLc"
SSH_KEY="$HOME/.ssh/id_ed25519"
PACKAGE_URL="https://tmpfiles.org/wnwCK7dmiD9T/sarahack-v10-final.tar"

echo "[*] Target: $TMATE_USER@$TMATE_HOST"
echo "[*] SSH Key: $SSH_KEY"
echo ""

# Check if SSH key exists
if [ ! -f "$SSH_KEY" ]; then
    echo "[!] SSH key not found: $SSH_KEY"
    exit 1
fi

# Test SSH connection
echo "[1/4] Testing SSH connection..."
if ! ssh -o StrictHostKeyChecking=no -o ConnectTimeout=15 -i "$SSH_KEY" "$TMATE_USER@$TMATE_HOST" 'echo "SSH OK" && whoami && uptime' 2>&1 | head -10; then
    echo "[!] SSH connection failed"
    echo "[*] Make sure the tmate session is active"
    exit 1
fi
echo "[+] SSH connection OK"
echo ""

# Create directories and download package
echo "[2/4] Setting up workspace..."
ssh -o StrictHostKeyChecking=no -o ConnectTimeout=30 -i "$SSH_KEY" "$TMATE_USER@$TMATE_HOST" << 'ENDSSH'
mkdir -p ~/workspace
cd ~/workspace

# Create freebuff directory
mkdir -p freebuff

# Download package
echo "[*] Downloading sarahack-v5.tar..."
curl -L -o sarahack-v10-final.tar https://tmpfiles.org/wnwCK7dmiD9T/sarahack-v10-final.tar

if [ -s sarahack-v5.tar ]; then
    echo "[+] Package downloaded ($(du -h sarahack-v5.tar | cut -f1))"
    
    # Extract
    tar xf sarahack-v5.tar
    echo "[+] Package extracted"
    
    # Move files to correct location
    if [ -d freebuff ]; then
        echo "[+] freebuff directory exists"
    fi
    
    # List files
    echo "[*] Files in ~/workspace:"
    ls -la
    
    echo "[*] Files in ~/workspace/freebuff:"
    ls -la freebuff/ 2>/dev/null || echo "No freebuff folder"
else
    echo "[!] Download failed"
fi
ENDSSH
echo ""

# Setup environment
echo "[3/4] Setting up environment variables..."
ssh -o StrictHostKeyChecking=no -o ConnectTimeout=30 -i "$SSH_KEY" "$TMATE_USER@$TMATE_HOST" << 'ENDSSH'
cd ~/workspace

# Create .env file with all credentials
cat > ~/.env << 'ENVEOF'
# SARAhack Configuration
export TMATE_HOST="lon1.tmate.io"
export TMATE_USER="eS6fytCGPu74pDmMNxAKcszLc"
export SSH_KEY_FILE="$HOME/.ssh/id_ed25519"

# Freebuff Token
export CODEBUFF_POSTHOG_API_KEY="be0e3e50-e07c-434d-98d0-85d6c59d615c"

# HackerOne Credentials
export HACKERONE_EMAIL="${HACKERONE_EMAIL}"
export HACKERONE_PASSWORD=")a9By=*D#6/w9T"

# AI Model - Minimax M2.7
export AI_MODEL="minimax/minimax-m2.7"
export CODEBUFF_MODEL="minimax-m2.7"

# Paths
export PATH="$HOME/.local/bin:$HOME/go/bin:$PATH"
export PYTHONPATH="$HOME/workspace:$PYTHONPATH"
ENVEOF

echo "[+] Environment saved to ~/.env"
cat ~/.env
ENDSSH
echo ""

# Verify setup
echo "[4/4] Verifying installation..."
ssh -o StrictHostKeyChecking=no -o ConnectTimeout=30 -i "$SSH_KEY" "$TMATE_USER@$TMATE_HOST" << 'ENDSSH'
cd ~/workspace

echo "[*] Checking freebuff..."
which freebuff && freebuff --version 2>&1 | head -3 || echo "freebuff not installed - run: npm install -g freebuff"

echo ""
echo "[*] Checking node..."
which node && node --version 2>&1 || echo "node not installed"

echo ""
echo "[*] Report files available:"
ls -la reports/*.md 2>/dev/null | head -10 || echo "No reports folder"

echo ""
echo "[*] Python scripts:"
ls -la freebuff/*.py 2>/dev/null | head -10 || echo "No python scripts"
ENDSSH
echo ""

echo "============================================================"
echo "[+] DEPLOYMENT COMPLETE!"
echo "============================================================"
echo ""
echo "Next steps - SSH into tmate session and run:"
echo ""
echo "  1. source ~/.env"
echo "  2. freebuff login"
echo "  3. cd ~/workspace/freebuff"
echo "  4. bash run-submission-manual.sh"
echo ""
echo "To SSH manually:"
echo "  ssh -i ~/.ssh/id_ed25519 eS6fytCGPu74pDmMNxAKcszLc@lon1.tmate.io"
echo ""