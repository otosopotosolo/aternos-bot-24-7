#!/bin/bash
# ============================================================
# SARAhack - Deploy to New Tmate Session
# ============================================================
# New session: eS6fytCGPu74pDmMNxAKcszLc@lon1.tmate.io

set -e

echo "============================================================"
echo "SARAhack - Deploy to New Tmate Session"
echo "============================================================"
echo ""

# Variables
TMATE_HOST="lon1.tmate.io"
TMATE_USER="eS6fytCGPu74pDmMNxAKcszLc"
SSH_KEY="$HOME/.ssh/id_ed25519"
TOKEN="be0e3e50-e07c-434d-98d0-85d6c59d615c"
H1_EMAIL="${HACKERONE_EMAIL}"
H1_PASS=")a9By=*D#6/w9T"

echo "[*] Target: $TMATE_USER@$TMATE_HOST"
echo "[*] SSH Key: $SSH_KEY"
echo ""

# Test SSH connection
echo "[1/5] Testing SSH connection..."
if ! ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 -i "$SSH_KEY" "$TMATE_USER@$TMATE_HOST" 'echo "SSH OK" && whoami' 2>&1 | head -5; then
    echo "[!] SSH connection failed"
    exit 1
fi
echo "[+] SSH connection OK"
echo ""

# Create workspace directory
echo "[2/5] Creating workspace directory..."
ssh -o StrictHostKeyChecking=no -i "$SSH_KEY" "$TMATE_USER@$TMATE_HOST" 'mkdir -p ~/workspace/freebuff && ls -la ~/workspace/' 2>&1
echo ""

# Upload deployment package
echo "[3/5] Uploading deployment package..."
PACKAGE_URL="https://tmpfiles.org/wKw2KIT24Xzj/freebuff-v4.tar"
ssh -o StrictHostKeyChecking=no -i "$SSH_KEY" "$TMATE_USER@$TMATE_HOST" << 'ENDSSH'
mkdir -p ~/workspace/freebuff
cd ~/workspace/freebuff
echo "[*] Downloading package..."
curl -L -o freebuff-v4.tar https://tmpfiles.org/wKw2KIT24Xzj/freebuff-v4.tar
if [ -s freebuff-v4.tar ]; then
    echo "[+] Package downloaded"
    tar xf freebuff-v4.tar
    echo "[+] Package extracted"
    ls -la
else
    echo "[!] Download failed"
fi
ENDSSH
echo ""

# Setup environment variables
echo "[4/5] Setting up environment variables..."
ssh -o StrictHostKeyChecking=no -i "$SSH_KEY" "$TMATE_USER@$TMATE_HOST" << 'ENDSSH'
cd ~/workspace/freebuff

# Set environment variables
export CODEBUFF_POSTHOG_API_KEY="be0e3e50-e07c-434d-98d0-85d6c59d615c"
export HACKERONE_EMAIL="${HACKERONE_EMAIL}"
export HACKERONE_PASSWORD=")a9By=*D#6/w9T"
export AI_MODEL="minimax/minimax-m2.7"

# Save to .env file
cat > ~/.env << 'ENVEOF'
export CODEBUFF_POSTHOG_API_KEY="be0e3e50-e07c-434d-98d0-85d6c59d615c"
export HACKERONE_EMAIL="${HACKERONE_EMAIL}"
export HACKERONE_PASSWORD=")a9By=*D#6/w9T"
export AI_MODEL="minimax/minimax-m2.7"
export TMATE_HOST="lon1.tmate.io"
export TMATE_USER="eS6fytCGPu74pDmMNxAKcszLc"
ENVEOF

echo "[+] Environment saved to ~/.env"
cat ~/.env
ENDSSH
echo ""

# Verify installation
echo "[5/5] Verifying installation..."
ssh -o StrictHostKeyChecking=no -i "$SSH_KEY" "$TMATE_USER@$TMATE_HOST" << 'ENDSSH'
cd ~/workspace/freebuff
echo "[*] Checking freebuff..."
which freebuff && freebuff --version || echo "freebuff not installed - will install"
echo ""
echo "[*] Listing files..."
ls -la freebuff/
ENDSSH
echo ""

echo "============================================================"
echo "[+] DEPLOYMENT COMPLETE!"
echo "============================================================"
echo ""
echo "Next steps on the tmate session:"
echo "1. source ~/.env"
echo "2. freebuff login"
echo "3. cd ~/workspace/freebuff"
echo "4. bash run-submission-manual.sh"
echo ""