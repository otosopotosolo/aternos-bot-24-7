#!/bin/bash
# SARAhack - Fetch Latest CVEs
# ดึงช่องโหว่ใหม่ๆ จาก CVE database

set -e

echo "=========================================="
echo "  SARAhack - Fetching Latest CVEs"
echo "=========================================="

CVE_DIR="knowledge/vulnerabilities/cves"
mkdir -p "$CVE_DIR"

# Colors
RED='\u001b[31m'
GREEN='\u001b[32m'
YELLOW='\u001b[33m'
NC='\u001b[0m'

log_success() { echo -e "${GREEN}[+]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[!]${NC} $1"; }
log_error() { echo -e "${RED}[-]${NC} $1"; }

# 1. Fetch latest CVEs from NVD
echo ""
echo "[*] Fetching latest CVEs from NVD..."
curl -s "https://services.nvd.nist.gov/rest/json/cves/2.0/?resultsPerPage=10&pubStartDate=$(date -u +%Y-%m-%d)T00%3A00%3A00%3A000" | jq '.vulnerabilities[].cve' 2>/dev/null | head -50 || log_warn "NVD API rate limited"

# 2. Search for web vulnerabilities
echo ""
echo "[*] Searching for web-related CVEs..."
WEB_CVES=$(curl -s "https://cve.mitre.org/cgi-bin/cvekey.cgi?keyword=web+application" 2>/dev/null | grep -o 'CVE-[0-9]*-[0-9]*' | head -20 || echo "")

if [ -n "$WEB_CVES" ]; then
    echo "Found CVEs:"
    echo "$WEB_CVES"
else
    log_warn "Could not fetch CVEs from MITRE"
fi

# 3. Check Exploit-DB for new exploits
echo ""
echo "[*] Checking Exploit-DB..."
if command -v searchsploit &> /dev/null; then
    searchsploit --mirror | head -10 || log_warn "searchsploit not working"
else
    log_warn "searchsploit not installed"
fi

# 4. Check GitHub Advisories
echo ""
echo "[*] Checking GitHub Advisories..."
curl -s "https://api.github.com/advisories?per_page=10" 2>/dev/null | jq '.[].ghsa_id' || log_warn "GitHub API limited"

# 5. Save to file
echo ""
echo "[*] Saving CVE data..."

cat > "$CVE_DIR/cves_$(date +%Y%m%d).md" << EOF
# CVEs - วันที่ $(date +%Y-%m-%d)

## Web Application Vulnerabilities

### Latest CVEs

<!-- เพิ่ม CVE ที่นี่ -->

### Critical CVEs to Watch

| CVE | Description | Severity | CVSS |
|-----|-------------|----------|------|
| CVE-2026-xxxx | TBD | HIGH | 8.0+ |

## Zero-Day Disclosures

## Exploit-DB New Exploits

## Mitigation Recommendations

1. Update affected software immediately
2. Implement WAF rules for known attack patterns
3. Monitor for suspicious activity

EOF

log_success "CVE data saved to $CVE_DIR/cves_$(date +%Y%m%d).md"

# 6. Create nuclei template for new CVEs
echo ""
echo "[*] Creating nuclei template..."

cat > "$CVE_DIR/cve-template.yaml" << 'EOF'
id: CVE-XXXX-XXXX
info:
  name: CVE Description
  author: SARAhack
  severity: high
  description: Vulnerability description
  reference:
    - https://nvd.nist.gov/vuln/detail/CVE-XXXX-XXXX
  tags: cve,web

requests:
  - method: GET
    path:
      - "{{BaseURL}}"
    matchers:
      - type: word
        words:
          - "vulnerable-pattern"
EOF

log_success "Nuclei template created"

echo ""
echo "=========================================="
echo -e "${GREEN}[+] Done!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Review $CVE_DIR/cves_$(date +%Y%m%d).md"
echo "  2. Create POC for critical CVEs"
echo "  3. Test targets with nuclei"
echo ""