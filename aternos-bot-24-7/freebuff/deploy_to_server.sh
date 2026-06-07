#!/bin/bash
# SARAhack Deployment Script for segfault server
# Usage: ./deploy_to_server.sh

set -e

SERVER="root@8lgm.segfault.net"
SSH_OPTS="-o 'SetEnv SECRET=NdnaRgvpuNaehtqPvVbgTDJQ'"
FILES=("freebuff/target_scanner.py" "freebuff/discord_notifier.py" "freebuff/hackerone_api_submitter.py")

echo "=== SARAhack Deployment ==="

# Create base64 encoded versions to handle special characters
for file in "${FILES[@]}"; do
    if [[ -f "$file" ]]; then
        echo "[*] Encoding $file..."
        ENCODED=$(base64 -w 0 "$file")
        
        echo "[*] Copying to server..."
        ssh $SSH_OPTS "$SERVER" "mkdir -p /opt/sarahack/freebuff" 2>/dev/null || true
        
        # Create file on server via encoded transfer
        ssh $SSH_OPTS "$SERVER" "echo '$ENCODED' | base64 -d > /opt/sarahack/$file" 2>/dev/null
        
        echo "[✓] $file deployed"
    fi
done

echo ""
echo "=== Installation on Server ==="
ssh $SSH_OPTS "$SERVER" << 'ENDSSH'
cd /opt/sarahack

# Install Python dependencies
pip3 install requests --break-system-packages 2>/dev/null || true

# Install Go tools
go install github.com/projectdiscovery/nuclei/v3@latest 2>/dev/null || true
go install github.com/ffuf/ffuf@latest 2>/dev/null || true

# Install Playwright for browser automation
npm install -g playwright 2>/dev/null || true
npx playwright install chromium 2>/dev/null || true

# Update nuclei templates
nuclei -update-templates 2>/dev/null || true

# Set permissions
chmod +x freebuff/*.py

echo "[✓] Installation complete"
ENDSSH

echo ""
echo "=== Deployment Complete ==="
echo "Run on server:"
echo "  cd /opt/sarahack"
echo "  python3 freebuff/target_scanner.py"
echo ""
echo "Or SSH and run manually:"
echo "  ssh -o 'SetEnv SECRET=NdnaRgvpuNaehtqPvVbgTDJQ' root@8lgm.segfault.net"