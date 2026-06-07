# 🎯 DoorDash API - Hunting Target Checklist
# Platform: HackerOne
# Program: DoorDash
# Date: 2026-06-06
# Status: HUNTING TARGET (Not a confirmed vulnerability!)

---

## ⚠️ IMPORTANT: This is NOT a vulnerability report!

This is a hunting target checklist. You must:
1. Actually test the API to find real vulnerabilities
2. Document real API requests/responses as proof
3. Only submit a report if you confirm a real vulnerability exists

---

## Research Findings

### DoorDash API Information
| Item | Details |
|------|---------|
| **API Portal** | https://developer.doordash.com/ |
| **Marketplace API** | https://openapi.doordash.com/marketplace |
| **Authentication** | JWT (developer_id, key_id, secret) |
| **HackerOne** | https://hackerone.com/doordash |

### Important Notes
- DoorDash APIs are for **partner/merchant integration**, not public developers
- You likely need to be an authorized DoorDash partner to get API credentials
- Automated scanning is **forbidden** by DoorDash policy

---

## Pre-Testing Checklist

### Step 1: Check HackerOne Scope
```bash
# IMPORTANT: Before ANY testing
# 1. Go to https://hackerone.com/doordash
# 2. Read the Scope section carefully
# 3. Verify which domains/APIs are in scope
# 4. Only test assets listed in scope!
```

### Step 2: Get API Access (if possible)
```bash
# DoorDash APIs require partnership - not public access
# Options:
# 1. Apply to be a DoorDash partner developer
# 2. Check if DoorDash has a public sandbox
# 3. Look for any public DoorDash API endpoints
```

### Step 3: Find Testing Endpoints
```bash
# If you get API access, look for:
# - /store/{store_id}/orders - Store order data
# - /driver/{driver_id}/deliveries - Driver delivery data
# - /merchant/{merchant_id}/analytics - Business analytics
```

---

## IDOR Testing Methodology

### If you get API access:

```bash
# 1. Authenticate and get your own data first
curl -X GET 'https://openapi.doordash.com/marketplace/v1/stores/YOUR_STORE_ID' \\
  -H 'Authorization: Bearer YOUR_JWT_TOKEN'

# Document your store ID and the response

# 2. Enumerate other store IDs
# Try different store IDs to see if you can access other merchants' data

# 3. Check for authorization
# If you get data for stores you don't own = IDOR CONFIRMED!
```

### IDOR Signs to Look For:
- Sequential or predictable IDs (e.g., store_id=123, 124, 125)
- No ownership validation in API responses
- Different data returned when changing ID parameters
- Missing `403 Forbidden` for unauthorized access

---

## Alternative Targets (Easier to Test)

If DoorDash API is not accessible, consider these easier targets:

| Target | Why Easier |
|--------|------------|
| **Uber** | Already has report template (SUBMISSION_PACKAGE_uber_idor.md) |
| **Shopify** | Already has report template (SUBMISSION_PACKAGE_shopify_idor.md) |
| **GitLab** | Already has report template (SUBMISSION_PACKAGE_gitlab_idor.md) |

---

## Next Steps on Kali

```bash
# Option 1: Submit existing confirmed reports
# Shopify, GitLab, Uber IDOR reports are ready for submission!

# Option 2: Find DoorDash API access
# Apply at https://developer.doordash.com/
# If approved, test for IDOR using the methodology above

# Option 3: Hunt new targets
# Look for other programs with public APIs
# Check https://hackerone.com/programs for new VDPs
```

---

## References
- DoorDash HackerOne: https://hackerone.com/doordash
- DoorDash Developer: https://developer.doordash.com/
- OWASP IDOR: https://owasp.org/www-project-api-security/