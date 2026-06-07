# SENDGRID CORS Vulnerability Report

## Summary

| Field | Value |
|-------|-------|
| **Vulnerability Type** | CORS |
| **Severity** | high |
| **Program** | sendgrid |
| **Platform** | hackerone |
| **Bounty Range** | $100-$500 |
| **Date Found** | 2026-06-07 |
| **Report ID** | NEW-1780862190588 |

## Vulnerability Details

**Tested Endpoint:** 
https://api.sendgrid.com/v3/templates

**HTTP Status:** 200

**CORS Headers Received:**
```json
{
  "access-control-allow-methods": "HEAD, GET, PUT, POST, DELETE, OPTIONS, PATCH",
  "access-control-max-age": "21600",
  "access-control-expose-headers": "Link, Location",
  "access-control-allow-origin": "https://evil-test.com",
  "access-control-allow-credentials": "true",
  "access-control-allow-headers": "AUTHORIZATION, Content-Type, On-behalf-of, x-sg-elas-acl, X-Recaptcha, X-Request-Source, Browser-Fingerprint"
}
```