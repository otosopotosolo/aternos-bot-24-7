# NEWRELIC CORS Vulnerability Report

## Summary

| Field | Value |
|-------|-------|
| **Vulnerability Type** | CORS |
| **Severity** | high |
| **Program** | newrelic |
| **Platform** | hackerone |
| **Bounty Range** | $500-$2,000 |
| **Date Found** | 2026-06-07 |
| **Report ID** | NEW-1780862135362 |

## Vulnerability Details

**Tested Endpoint:** 
https://api.newrelic.com/v2/applications

**HTTP Status:** 200

**CORS Headers Received:**
```json
{
  "access-control-allow-origin": "https://evil-test.com",
  "access-control-allow-methods": "DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT",
  "access-control-allow-headers": "x-requested-with, Content-Type, If-Modified-Since, If-None-Match, x-api-key, NewRelic-api-key, api-key",
  "access-control-expose-headers": "ETag, Link",
  "access-control-allow-credentials": "true"
}
```