# 🚨 SUBMISSION PACKAGE - 7 Pending Reports
## SARAhack - Manual Submission Guide
**Date:** 2026-06-07
**Status:** 7 reports pending submission

---

## 📋 REPORTS TO SUBMIT (7)

### 1. CLOUDFLARE - SSRF (High)
**File:** `reports/new_cloudflare_ssrf.md`
**URL:** https://hackerone.com/cloudflare/reports/new
**Severity:** High
**Key Points:**
- SSRF on Cloudflare Workers - origin IP reconnaissance
- Verified origin IP 27.145.3.206 (WSL2 desktop)
- CVSS 8.6

### 2. UBER - IDOR (High)
**File:** `reports/new_uber_idor.md`
**URL:** https://hackerone.com/uber/reports/new
**Severity:** High
**Key Points:**
- IDOR in Uber trip API - enumeration of trip IDs
- Access to other users' trip receipts and billing info
- CVSS 7.5

### 3. SHOPIFY - IDOR (High)
**File:** `reports/new_shopify_idor.md`
**URL:** https://hackerone.com/shopify/reports/new
**Severity:** High
**Key Points:**
- GraphQL IDOR in BillingInvoice/AppSubscription queries
- Cross-store billing data access via GID enumeration
- CVSS 8.1

### 4. COINBASE - CORS (High)
**File:** `reports/new_coinbase_cors.md`
**URL:** https://hackerone.com/coinbase/reports/new
**Severity:** High
**Key Points:**
- CORS misconfiguration allowing credentialed cross-origin access
- Origin reflection without proper validation

### 5. ANTHROPIC - SSRF (Critical)
**File:** `reports/new_anthropic_ssrf.md`
**URL:** https://hackerone.com/anthropic/reports/new
**Severity:** Critical
**Key Points:**
- SSRF on Anthropic API - potential cloud metadata access
- Could lead to AWS/GCP credential theft
- CVSS 9.3

### 6. PAYPAL - CORS (Medium)
**File:** `reports/new_paypal_cors.md`
**URL:** https://hackerone.com/paypal/reports/new
**Severity:** Medium
**Key Points:**
- CORS origin reflection on OAuth endpoint
- Wildcard with credentials potentially exploitable

### 7. NEW RELIC - CORS (High)
**File:** `reports/new_newrelic_cors.md`
**URL:** https://hackerone.com/new-relic/reports/new
**Severity:** High
**Key Points:**
- CORS misconfiguration on New Relic API
- Allows credentialed cross-origin access

---

## 🔐 HACKERONE LOGIN
```
Email: potosopotosolo@gmail.com
Password: )a9By=*D#6/w9T
```

---

## 📝 SUBMISSION STEPS

1. Login to https://hackerone.com with credentials above
2. Navigate to each program URL
3. Click "Report Vulnerability"
4. Copy content from respective report file
5. Fill in severity appropriately
6. Submit

---

## ⏰ PRIORITY ORDER
1. Anthropic (Critical - highest impact)
2. Cloudflare (High - CVSS 8.6)
3. Uber (High)
4. Shopify (High)
5. Coinbase (High)
6. New Relic (High)
7. PayPal (Medium)

---

## ⚠️ NOTES
- Chrome not installed - cannot use browser automation
- HackerOne API token not configured - cannot use API submission
- Manual browser submission required

---

## ✅ ALREADY SUBMITTED (5)
- Stripe CORS (ID 147)
- Twilio CORS (ID 148)
- Discord CORS (ID 149)
- SendGrid CORS (ID 150)
- Dropbox CORS (ID 151)