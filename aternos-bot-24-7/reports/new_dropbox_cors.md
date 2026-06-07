# DROPBOX CORS Vulnerability Report

## Summary

| Field | Value |
|-------|-------|
| **Vulnerability Type** | CORS |
| **Severity** | medium |
| **Program** | dropbox |
| **Platform** | hackerone |
| **Bounty Range** | $500-$2,000 |
| **Date Found** | 2026-06-07 |
| **Report ID** | NEW-1780862209248 |

## Vulnerability Details

**Tested Endpoint:** 
https://api.dropboxapi.com/2/users/get_current_account

**HTTP Status:** 200

**CORS Headers Received:**
```json
{
  "access-control-allow-origin": "https://evil-test.com",
  "access-control-allow-methods": "GET,POST",
  "access-control-allow-headers": "Authorization,Cache-Control,Content-Type,If-Modified-Since,If-None-Match,Range,Dropbox-API-Arg,Dropbox-API-Select-User,Dropbox-API-User-Locale,Dropbox-API-Select-Admin,Dropbox-API-Path-Root,X-Dropbox-Backend,X-Dropbox-Validation,X-Dropbox-Destination,X-Dropbox-User-Agent,X-Dropbox-Force-Request-Tracing,X-Dropbox-Is-ESV,X-Dropbox-ESV-View-Name,Accept,Accept-Language,Content-Language,Origin,Referer,Traceparent,x-coding-agent-use-staging,x-grpc-web,x-user-agent,grpc-timeout,x-grpc-web-client,x-grpc-web-client-timeout",
  "access-control-max-age": "600",
  "access-control-expose-headers": "Accept-Ranges,Content-Range,ETag,Dropbox-API-Result,X-Dropbox-Request-Id,X-Dropbox-Trace-Id,grpc-status,grpc-message,grpc-encoding,grpc-accept-encoding,grpc-status-details-bin,trailer"
}
```