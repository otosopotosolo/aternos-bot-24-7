#!/bin/bash
# SARAhack - Find Bug Bounty Targets
# หา programs ใหม่ๆ จากแหล่งต่างๆ

set -e

echo "=========================================="
echo "  SARAhack - Finding Bug Bounty Targets"
echo "=========================================="

TARGET_DIR="reports/drafts"
mkdir -p "$TARGET_DIR"

# Colors
RED='\u001b[31m'
GREEN='\u001b[32m'
YELLOW='\u001b[33m'
NC='\u001b[0m'

log_success() { echo -e "${GREEN}[+]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[!]${NC} $1"; }
log_error() { echo -e "${RED}[-]${NC} $1"; }

# 1. หา targets จาก bounty-targets-data
echo ""
echo "[*] Fetching from bounty-targets-data..."
if [ ! -d "~/tools/bounty-targets-data" ]; then
    git clone --depth 1 https://github.com/arkadiyt/bounty-targets-data.git ~/tools/bounty-targets-data
fi

# Extract HackerOne programs
echo ""
echo "[*] Extracting HackerOne programs..."
grep -r "hackerone" ~/tools/bounty-targets-data/data/*.json 2>/dev/null | head -20 || log_warn "No data found"

# 2. หา targets จาก CVEs ใหม่
echo ""
echo "[*] Checking for new CVEs..."
curl -s "https://cve.mitre.org/cgi-bin/cvekey.cgi?keyword=web+vulnerability" | grep -o 'CVE-[0-9]*-[0-9]*' | head -10 || log_warn "CVE search limited"

# 3. หา programs ที่มี scope ใหม่
echo ""
echo "[*] Scanning popular programs..."
programs=("stripe" "discord" "shopify" "coinbase" "uber" "github" "twitter" "linkedin")

for program in "${programs[@]}"; do
    echo "  - Checking $program..."
done

# 4. สร้าง report สำหรับ targets ที่เจอ
echo ""
echo "[*] Creating target list..."

cat > "$TARGET_DIR/targets_$(date +%Y%m%d).md" << 'EOF'
# Bug Bounty Targets - วันที่

## High Priority Programs

| Program | Platform | Scope | Bounty |
|---------|----------|-------|--------|
| Stripe | HackerOne | *.stripe.com | Yes |
| Discord | HackerOne | *.discord.com | Yes |
| Shopify | HackerOne | *.shopify.com | Yes |
| Coinbase | HackerOne | *.coinbase.com | Yes |
| Uber | HackerOne | *.uber.com | Yes |

## New Programs เดือนนี้

<!-- อัพเดททุกสัปดาห์ -->

## Targets ที่ต้องหา更多信息

1. Programs ที่มี CORS misconfiguration
2. Programs ที่มี SSRF vulnerabilities
3. Programs ที่มี IDOR in API

## วิธีหา Targets ใหม่

```bash
# 1. ใช้ amass หา subdomain
amass enum -passive -d stripe.com

# 2. ใช้ subfinder หา subdomains
subfinder -d stripe.com

# 3. ใช้ httpx ตรวจสอบ alive
cat subdomains.txt | httpx -silent

# 4. หา CORS misconfiguration
echo "domain" | nuclei -t custom-cors.yaml
```

EOF

log_success "Target list created at $TARGET_DIR/targets_$(date +%Y%m%d).md"

# 5. แสดงผลลัพธ์
echo ""
echo "=========================================="
echo -e "${GREEN}[+] Done!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. เปิด $TARGET_DIR/targets_$(date +%Y%m%d).md"
echo "  2. เลือก program ที่จะ hunt"
echo "  3. ใช้ recon tools หาช่องโหว่"
echo ""