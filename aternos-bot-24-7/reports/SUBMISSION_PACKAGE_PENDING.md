# 🚨 SUBMISSION PACKAGE - Pending Reports
## SARAhack - Manual Submission Guide
**Date:** 2026-06-07
**Status:** 6 reports pending submission

---

## 📋 REPORTS TO SUBMIT (6)

### 1. UBER - IDOR (High)
**File:** `reports/new_uber_idor.md`
**URL:** https://hackerone.com/uber/reports/new
**Severity:** High
**Key Points:**
- IDOR in Uber trip API - enumeration of trip IDs
- Access to other users' trip receipts and billing info
- CVSS 3.1: 7.5 (AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)

### 2. SHOPIFY - IDOR (High)
**File:** `reports/new_shopify_idor.md`
**URL:** https://hackerone.com/shopify/reports/new
**Severity:** High
**Key Points:**
- GraphQL IDOR in BillingInvoice/AppSubscription queries
- Cross-store billing data access via GID enumeration
- CVSS 3.1: 8.1 (AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)

### 3. COINBASE - CORS (High)
**File:** `reports/new_coinbase_cors.md`
**URL:** https://hackerone.com/coinbase/reports/new
**Severity:** High
**Key Points:**
- CORS misconfiguration allowing credentialed cross-origin access
- Origin reflection without proper validation

### 4. ANTHROPIC - SSRF (Critical)
**File:** `reports/new_anthropic_ssrf.md`
**URL:** https://hackerone.com/anthropic/reports/new
**Severity:** Critical
**Key Points:**
- SSRF on Anthropic API - potential cloud metadata access
- Could lead to AWS/GCP credential theft
- CVSS 9.3

### 5. PAYPAL - CORS (Medium)
**File:** `reports/new_paypal_cors.md`
**URL:** https://hackerone.com/paypal/reports/new
**Severity:** Medium
**Key Points:**
- CORS origin reflection on OAuth endpoint
- Wildcard with credentials potentially exploitable

### 6. NEW RELIC - CORS (High)
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

### For each report:
1. Login to HackerOne with credentials above
2. Navigate to program URL
3. Click "Report Vulnerability"
4. Copy content from report file
5. Fill in:
   - Title (from report)
   - Summary (from report)
   - Steps to reproduce (from report)
   - PoC (from report)
   - Impact (from report)
6. Set severity appropriately
7. Submit

---

## ⏰ PRIORITY ORDER
1. Anthropic (Critical - highest impact)
2. Uber (High)
3. Shopify (High)
4. Coinbase (High)
5. New Relic (High)
6. PayPal (Medium)

---

## ✅ AFTER SUBMISSION
Update tracking file:
```bash
# Change status from "pending" to "submitted"
# Add date_submitted and HackerOne report URL
```

---

## ⚠️ NOTES
- Chrome not installed - cannot use browser automation
- HackerOne API token not configured - cannot use API submission
- Manual browser submission required