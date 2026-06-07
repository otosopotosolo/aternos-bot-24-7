#!/bin/bash
# SARAhack - HackerOne Auto-Submit via freebuff
# Usage: bash submit_hackerone.sh

set -e

# Colors
RED='\n\ue001[31m'
GREEN='\ue001[32m'
YELLOW='\ue001[33m'
BLUE='\ue001[34m'
NC='\ue001[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  SARAhack - HackerOne Report Submit${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Reports to submit (pending from reports.json)
declare -a REPORTS=(
  "reports/new_cloudflare_ssrf.md:Cloudflare:SSRF:HIGH"
  "reports/new_uber_idor.md:Uber:IDOR:HIGH"
  "reports/new_shopify_idor.md:Shopify:IDOR:HIGH"
  "reports/new_coinbase_cors.md:Coinbase:CORS:HIGH"
  "reports/new_gitlab_idor.md:GitLab:IDOR:MEDIUM"
)

echo -e "${YELLOW}Reports to submit:${NC}"
for i in "${!REPORTS[@]}"; do
  IFS=':' read -r file program vuln severity <<< "${REPORTS[$i]}"
  echo "  $((i+1)). $program - $vuln ($severity)"
done
echo ""

echo -e "${GREEN}[1] Connecting to freebuff server...${NC}"
echo "SSH: ssh -o \"SetEnv SECRET=JEpUOZPOVhCTwdhQInbJTtNA\" root@8lgm.segfault.net"
echo "Password: segfault"
echo ""
echo "Then run these commands in freebuff:"
echo ""
echo "=========================================="
echo ""

for i in "${!REPORTS[@]}"; do
  IFS=':' read -r file program vuln severity <<< "${REPORTS[$i]}"
  
  echo -e "${GREEN}[$((i+2))] Submit ${program} ${vuln} Report:${NC}"
  echo "----------------------------------------"echo "Command: Use browser automation to submit a bug bounty report to HackerOne"
  echo ""
  echo "Details for freebuff:"
  echo "  - Platform: HackerOne"
  echo "  - Program: $program"
  echo "  - Vulnerability: $vuln"
  echo "  - Severity: $severity"
  echo "  - Report file: $file"
  echo ""
  echo "Prompt for freebuff:"
  echo "  \"Login to HackerOne at https://hackerone.com using your HackerOne credentials,"
  echo "   then navigate to the $program bug bounty program and submit a new report."
  echo "   Use the contents from the file $file as the report description."
  echo "   Then navigate to the $program bug bounty program and submit a new report."
  echo "   Use the contents from the file $file as the report description.\""
  echo ""
  echo "=========================================="
  echo ""
done

echo -e "${GREEN}[DONE] Instructions displayed above${NC}"
echo ""
echo "After submitting all reports, update reports.json:"
echo "  - Change status from 'pending' to 'submitted'"
echo "  - Add date_submitted"
echo ""
echo "Or run: python3 tools/tracker.py update --all --status submitted"