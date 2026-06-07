#!/bin/bash
# ============================================================
# SARAhack - Manual Submission Script (for tmate session)
# ============================================================
# This script runs INSIDE the tmate terminal session.
# SSH to tmate first, then run this script.
#
# Commands to run before this script:
#   export CODEBUFF_POSTHOG_API_KEY='be0e3e50-e07c-434d-98d0-85d6c59d615c'
#   export HACKERONE_EMAIL='${HACKERONE_EMAIL}'
#   export HACKERONE_PASSWORD=')a9By=*D#6/w9T'
#   freebuff login
# ============================================================

set -e

echo "============================================================"
echo "SARAhack - Manual Report Submission"
echo "============================================================"

# Check environment
if [ -z "$CODEBUFF_POSTHOG_API_KEY" ]; then
    echo "[ERROR] CODEBUFF_POSTHOG_API_KEY not set"
    echo "Run: export CODEBUFF_POSTHOG_API_KEY='be0e3e50-e07c-434d-98d0-85d6c59d615c'"
    exit 1
fi

# Verify freebuff is installed
if ! command -v freebuff &> /dev/null; then
    echo "[ERROR] freebuff not found. Is it installed?"
    exit 1
fi

# Reports to submit (path relative to script directory)
REPORTS=(
    "reports/new_cloudflare_ssrf.md:Cloudflare:SSRF"
    "reports/new_uber_idor.md:Uber:IDOR"
    "reports/new_shopify_idor.md:Shopify:IDOR"
    "reports/new_coinbase_cors.md:Coinbase:CORS"
    "reports/new_gitlab_idor.md:GitLab:IDOR"
    "reports/new_gitlab_cors_advisories.md:GitLab:CORS"
)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo ""
echo "Reports ready for submission:"
for i in "${!REPORTS[@]}"; do
    IFS=':' read -r file program vuln <<< "${REPORTS[$i]}"
    full_path="$SCRIPT_DIR/$file"
    if [ -f "$full_path" ]; then
        echo "  [$((i+1))] $program - $vuln ✓"
    else
        echo "  [$((i+1))] $program - $vuln ✗ (missing)"
    fi
done

echo ""
read -p "Submit all reports? [Y/n]: " confirm
confirm="${confirm:-Y}"

if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

# Submit each report via freebuff
for report_spec in "${REPORTS[@]}"; do
    IFS=':' read -r local_file program vuln <<< "$report_spec"
    
    echo ""
    echo "============================================================"
    echo "[*] Submitting: $program $vuln"
    echo "============================================================"
    
    # Create prompt for freebuff
    full_path="$SCRIPT_DIR/$local_file"
    prompt="Submit a bug bounty report for $vuln vulnerability to the $program program on HackerOne. Use the report content from $full_path"
    
    # Send to freebuff using heredoc for TTY input
    freebuff <<PROMPT
Submit a bug bounty report for $vuln vulnerability to the $program program on HackerOne. Use the report content from $full_path
PROMPT
    if [ $? -eq 0 ]; then
        echo "[+] $program $vuln submitted!"
    else
        echo "[ERROR] $program $vuln failed"
    fi
    
    # Wait between submissions
    echo "[*] Waiting 45 seconds before next submission..."
    sleep 45
done

echo ""
echo "============================================================"
echo "[+] SUBMISSION COMPLETE"
echo "============================================================"