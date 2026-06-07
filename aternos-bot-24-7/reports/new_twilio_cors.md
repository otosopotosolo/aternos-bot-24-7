# TWILIO CORS Vulnerability Report

## Summary

| Field | Value |
|-------|-------|
| **Vulnerability Type** | CORS |
| **Severity** | high |
| **Program** | twilio |
| **Platform** | hackerone |
| **Bounty Range** | $500-$2,000 |
| **Date Found** | 2026-06-07 |
| **Report ID** | NEW-1780862125531 |

## Vulnerability Details

**Tested Endpoint:** 
https://api.twilio.com/2010-04-01/Accounts

**HTTP Status:** 200

**CORS Headers Received:**
```json
{
  "access-control-allow-credentials": "true",
  "access-control-allow-origin": "https://evil-test.com",
  "access-control-allow-methods": "POST,GET,DELETE,OPTIONS",
  "access-control-allow-headers": "Authorization"
}
```