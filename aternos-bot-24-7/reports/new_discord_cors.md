# DISCORD CORS Vulnerability Report

## Summary

| Field | Value |
|-------|-------|
| **Vulnerability Type** | CORS |
| **Severity** | high |
| **Program** | discord |
| **Platform** | hackerone |
| **Bounty Range** | $500-$2,000 |
| **Date Found** | 2026-06-07 |
| **Report ID** | NEW-1780862146681 |

## Vulnerability Details

**Tested Endpoint:** 
https://discord.com/api/v10/users/@me

**HTTP Status:** 200

**CORS Headers Received:**
```json
{
  "access-control-allow-origin": "https://evil-test.com",
  "access-control-allow-credentials": "true",
  "access-control-allow-methods": "POST, GET, PUT, PATCH, DELETE",
  "access-control-allow-headers": "Content-Type, Authorization, X-Audit-Log-Reason, X-Track, X-Super-Properties, X-Context-Properties, X-Failed-Requests, X-Fingerprint, X-RPC-Proxy, X-Discord-Locale, X-Discord-Original-MD5, X-Discord-Timezone, X-Debug-Options, x-client-trace-id, If-None-Match, X-Captcha-Key, X-Captcha-Rqtoken, X-Captcha-Session-Id, X-Discord-Resource-Optimization-Level, x-science-test, X-Discord-MFA-Authorization, Range, X-RateLimit-Precision, X-Discord-Features, X-Installation-Id"
}
```