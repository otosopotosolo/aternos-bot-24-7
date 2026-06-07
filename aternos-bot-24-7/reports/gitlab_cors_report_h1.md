# CORS Misconfiguration Bug Report - GitLab

**Platform:** HackerOne  
**Program:** gitlab.com  
**Severity:** Informational  
**Report Date:** 2026-06-06  

---

## Summary

A Cross-Origin Resource Sharing (CORS) misconfiguration was discovered on `advisories.gitlab.com`, a public GitLab subdomain that hosts the GitLab Advisory Database (GLAD). The endpoint returns `Access-Control-Allow-Origin: *` header without proper origin restrictions.

---

## Description

During a security assessment of GitLab's public infrastructure, the `advisories.gitlab.com` subdomain was found to have overly permissive CORS headers. The server returns `Access-Control-Allow-Origin: *` alongside `Vary: Origin`, suggesting the server may dynamically handle origin validation.

---

## Steps to Reproduce

1. Navigate to `https://advisories.gitlab.com`
2. Send a GET request with an arbitrary Origin header:
```bash
curl -i -X GET "https://advisories.gitlab.com" -H "Origin: https://evil.com"
```

**Response Headers:**
```
HTTP/2 200
access-control-allow-origin: *
vary: Origin
cache-control: max-age=600
content-type: text/html
date: Sat, 06 Jun 2026 03:28:26 GMT
```

3. Test with different arbitrary origins - response consistently returns `*`:
```bash
curl -i -X GET "https://advisories.gitlab.com" -H "Origin: https://myevil123456.com"
# Response: access-control-allow-origin: *

curl -i -X GET "https://advisories.gitlab.com" -H "Origin: https://attacker.xyz"
# Response: access-control-allow-origin: *
```

---

## PoC (Proof of Concept)

```bash
# Test 1 - Basic CORS check
curl -i https://advisories.gitlab.com -H "Origin: https://evil.com" 2>/dev/null | grep -i access-control

# Test 2 - With credentials header
curl -i https://advisories.gitlab.com -H "Origin: https://evil.com" -H "Cookie: session=test" 2>/dev/null | grep -i access-control

# Test 3 - Verify vary header
curl -i https://advisories.gitlab.com -H "Origin: https://test.com" 2>/dev/null | grep -E "(access-control|vary)"
```

**Results:**
- `access-control-allow-origin: *` - Always wildcard
- `vary: Origin` - Present, indicating dynamic origin handling
- `access-control-allow-credentials: true` - **NOT present** (verified)

---

## Impact

**Why Informational Severity:**

The `advisories.gitlab.com` endpoint is a **publicly accessible** page containing security advisories that are intentionally meant to be visible to everyone. The data is already accessible without authentication via direct browsing.

While `access-control-allow-origin: *` is technically a CORS misconfiguration:
- **No credentials can be stolen** - Browsers block cookies when the server returns wildcard `*` origins
- **No authenticated data exposed** - The advisory data is public by design
- **Server consistently returns `*`** - The `Vary: Origin` header is present for caching purposes, not to dynamically reflect origins

**Reported per OWASP CORS best practices guidance** which recommends against using wildcard `*` on any endpoint, even public ones, to maintain good security hygiene.

---

## Additional Findings (Out of Scope)

The following GitLab subdomains also exhibit similar CORS configuration but are likely **out of scope** for the bug bounty program:

| Subdomain | CORS Header | Notes |
|-----------|-------------|-------|
| internal.gitlab.com | `*` | Likely internal-only, out of scope |
| developer.gitlab.com | `*` | Developer portal, may be out of scope |
| metrics.gitlab.com | `*` | Internal monitoring, out of scope |
| schemas.runway.gitlab.com | `*` | Internal tooling, out of scope |
| slippers.gitlab.com | `*` | Internal service, out of scope |
| cx-plan.gitlab.com | `*` | Internal planning tool, out of scope |
| infra-roadmap.gitlab.com | `*` | Internal infrastructure docs, out of scope |

**Only `advisories.gitlab.com` is included in this report** as the only likely in-scope endpoint with CORS misconfiguration.

---

## Remediation

If GitLab intends to restrict CORS to only GitLab-owned origins:

1. Replace wildcard `*` with explicit gitlab.com origins
2. Only enable `Access-Control-Allow-Credentials: true` with specific origins

**Example Fix (nginx):**
```nginx
location / {
    # Restrict to gitlab.com domains only
    if ($http_origin ~* ^https://[a-z-]+\.gitlab\.com$) {
        add_header 'Access-Control-Allow-Origin' "$http_origin" always;
        add_header 'Access-Control-Allow-Credentials' 'true' always;
    }
}
```

**Note:** If public access to advisories is intentional (it likely is for the security community), keeping `*` may be acceptable since no sensitive data is being exposed. The `Vary: Origin` header suggests the server is aware of origin handling but chose to use wildcard for this public endpoint.

---

## References

- [OWASP CORS Security Cheatsheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
- [MDN CORS Documentation](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [PortSwigger CORS Guide](https://portswigger.net/web-security/cors)

---

## Timeline

- **Date Discovered:** 2026-06-06
- **Date Reported:** 2026-06-06

---

**Reporter:** SARAhack Automation  
**Platform:** HackerOne  
**Programs Scanned:** GitLab, Spotify, PayPal, Yahoo, Salesforce, Nintendo, Coinbase (43,000+ subdomains total)