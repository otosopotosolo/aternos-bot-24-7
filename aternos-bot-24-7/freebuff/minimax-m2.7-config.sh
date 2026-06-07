#!/bin/bash
# SARAhack - Minimax M2.7 Model Configuration
# This script configures the AI model to use Minimax M2.7

echo "=========================================="
echo "SARAhack - Minimax M2.7 Configuration"
echo "=========================================="
echo ""

# Set Minimax M2.7 as the AI model
export AI_MODEL="minimax/minimax-m2.7"
export CODEBUFF_MODEL="minimax-m2.7"

# Freebuff Configuration
export CODEBUFF_POSTHOG_API_KEY="be0e3e50-e07c-434d-98d0-85d6c59d615c"
export CODEBUFF_POSTHOG_HOST="https://posthog.codebuff.com"

# HackerOne Credentials (password auth)
export HACKERONE_EMAIL="${HACKERONE_EMAIL}"
export HACKERONE_PASSWORD=")a9By=*D#6/w9T"

# Python path
export PYTHONPATH="$HOME/workspace:$PYTHONPATH"

echo "[*] Model Configuration:"
echo "    AI_MODEL: $AI_MODEL"
echo "    CODEBUFF_MODEL: $CODEBUFF_MODEL"
echo ""

echo "[*] Testing freebuff with Minimax M2.7..."
freebuff --model minimax-m2.7 --version 2>&1 || echo "freebuff interactive mode"

echo ""
echo "[+] Minimax M2.7 configured successfully!"
echo "    Add to ~/.bashrc for persistence:"
echo "    source $HOME/workspace/freebuff/minimax-m2.7-config.sh"