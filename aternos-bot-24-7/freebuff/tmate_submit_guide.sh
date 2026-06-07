#!/bin/bash
# SARAhack - Tmate + Freebuff Interactive Guide
# Run this script inside your tmate session

echo "=========================================="
echo "SARAhack - Freebuff Report Submission"
echo "=========================================="
echo ""

# Check if we have freebuff
if ! command -v freebuff &> /dev/null; then
    echo "[!] Freebuff not found. Installing..."
    npm install -g freebuff
fi

echo "[*] Freebuff version:"
freebuff --version 2>&1 || echo "Interactive mode only"

echo ""
echo "=========================================="
echo "Available Reports to Submit:"
echo "=========================================="
echo "1. Cloudflare SSRF (high)"
echo "2. Uber IDOR (high)"
echo "3. Shopify IDOR (high)"
echo "4. Coinbase CORS (high)"
echo "5. GitLab IDOR (high)"
echo "6. DoorDash SSRF (high)"
echo "7. GitLab CORS - advisories (informational)"
echo ""

# Set token
# Freebuff/Codebuff Token
export CODEBUFF_POSTHOG_API_KEY="be0e3e50-e07c-434d-98d0-85d6c59d615c"

# HackerOne Credentials (password auth - no API token needed)
export HACKERONE_EMAIL="${HACKERONE_EMAIL}"
export HACKERONE_PASSWORD=")a9By=*D#6/w9T"

# Optional: If you have API token instead
export H1_API_IDENTIFIER="nonoto999t@gmail.com"
export H1_API_TOKEN=""

# Minimax M2.7 Model Configuration
export AI_MODEL="minimax/minimax-m2.7"
export CODEBUFF_MODEL="minimax-m2.7"

# SSH to tmate session
ssh eS6fytCGPu74pDmMNxAKcszLc@lon1.tmate.io

echo "[*] Starting freebuff..."
echo "[*] When freebuff is ready, use commands like:"
echo ""
echo "--- To submit Cloudflare SSRF report ---"
echo 'Login to HackerOne and submit the SSRF report for Cloudflare from /tmp/cloudflare_ssrf.md'
echo ""
echo "--- To check freebuff status ---"
echo 'What version are you?'
echo ""
echo "=========================================="
echo ""

# Open freebuff
freebuff