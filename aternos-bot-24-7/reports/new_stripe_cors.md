# STRIPE CORS Vulnerability Report

## Summary

| Field | Value |
|-------|-------|
| **Vulnerability Type** | CORS |
| **Severity** | high |
| **Program** | stripe |
| **Platform** | hackerone |
| **Bounty Range** | $500-$5,000 |
| **Date Found** | 2026-06-07 |
| **Report ID** | NEW-1780862115787 |

## Vulnerability Details

**Tested Endpoint:** 
https://api.stripe.com/v1/customers

**HTTP Status:** 200

**CORS Headers Received:**
```json
{
  "access-control-allow-credentials": "true",
  "access-control-allow-headers": "Authorization",
  "access-control-allow-methods": "GET, HEAD, PUT, PATCH, POST, DELETE",
  "access-control-allow-origin": "https://evil-test.com",
  "access-control-expose-headers": "Request-Id, Stripe-Manage-Version, Stripe-Should-Retry, X-Stripe-External-Auth-Required, X-Stripe-Privileged-Session-Required",
  "access-control-max-age": "300"
}
```