# CORS Misconfiguration Bug Report - GitLab Advisories

**Platform:** HackerOne  
**Program:** GitLab  
**Severity:** Informational  
**Report Date:** 2026-06-06  

---

## Summary

A Cross-Origin Resource Sharing (CORS) misconfiguration was discovered on `advisories.gitlab.com`, returning `Access-Control-Allow-Origin: *` headers without proper origin validation. While this specific configuration (static wildcard without credentials) has limited exploitability, it represents a policy violation and potential information disclosure vector.

---

## Description

During a systematic CORS scan of GitLab's bug bounty scope, the subdomain `advisories.gitlab.com` was found to return unrestricted CORS headers:

```
access-control-allow-origin: *
vary: Origin
```

The `advisories.gitlab.com` subdomain hosts the GitLab Security Advisory Database - a collection of security vulnerability information affecting GitLab products.

**8 subdomains found with CORS issues:**
1. `advisories.gitlab.com` - Security advisory database (PRIORITY)
2. `internal.gitlab.com` - Internal tools
3. `developer.gitlab.com` - Developer portal
4. `schemas.runway.gitlab.com` - Schema definitions
5. `slippers.gitlab.com` - Unknown purpose
6. `metrics.gitlab.com` - Metrics endpoints
7. `cx-plan.gitlab.com` - CX planning tool
8. `infra-roadmap.gitlab.com` - Infrastructure docs

---

## Steps to Reproduce

1. Send HTTP request to `advisories.gitlab.com` with arbitrary Origin:

```bash
curl -i -X GET "https://advisories.gitlab.com" \\
  -H "Origin: https://attacker-controlled-site.com"
```

2. Observe response headers:

```
HTTP/1.1 200 OK
server: nginx
access-control-allow-origin: *
vary: Origin
cache-control: max-age=600
content-type: text/html
```

3. Test from browser with JavaScript to confirm browser behavior

---

## PoC (Proof of Concept)

```bash
# Multiple Origin values all return wildcard
$ curl -i -X GET "https://advisories.gitlab.com" -H "Origin: https://evil.com"

HTTP/1.1 200 OK
access-control-allow-origin: *
vary: Origin

$ curl -i -X GET "https://advisories.gitlab.com" -H "Origin: null"

HTTP/1.1 200 OK
access-control-allow-origin: *
vary: Origin

$ curl -i -X GET "https://advisories.gitlab.com" -H "Origin: https://facebook.com"

HTTP/1.1 200 OK
access-control-allow-origin: *
vary: Origin
```

**Note:** No `Access-Control-Allow-Credentials: true` header is present, limiting exploitability.

---

## Impact

**Limited Exploitability (Informational):**

1. **No credential reflection:** Static `*` means browsers won't send cookies/authentication
2. **Read access limited:** Cannot read response due to CORS specification
3. **Static content only:** advisories.gitlab.com contains public security data

**Potential Scenarios:**

1. **Information Disclosure:** Security advisory data could be accessed by malicious third parties
2. **Policy Violation:** GitLab's own security posture may require origin restrictions
3. **Precedent Setting:** Demonstrates CORS misconfiguration pattern across multiple subdomains

**Why Submit (Informational):**
- GitLab may have compliance requirements for origin restrictions
- The `vary: Origin` header suggests dynamic origin handling capability
- Demonstrates reconnaissance findings for the program
- Could be combined with other vulnerabilities for impact

---

## Affected Endpoints

| Subdomain | CORS Header | Data Type | Priority |
|-----------|-------------|-----------|----------|
| `advisories.gitlab.com` | `access-control-allow-origin: *` | Security advisories | HIGH |
| `internal.gitlab.com` | `access-control-allow-origin: *` | Internal tools | LOW (likely OOS) |
| `developer.gitlab.com` | `access-control-allow-origin: *` | Dev portal | MEDIUM |
| `schemas.runway.gitlab.com` | `access-control-allow-origin: *` | Schemas | LOW |
| `metrics.gitlab.com` | `access-control-allow-origin: *` | Metrics | MEDIUM |
| `cx-plan.gitlab.com` | `access-control-allow-origin: *` | Planning tool | LOW |
| `infra-roadmap.gitlab.com` | `access-control-allow-origin: *` | Infra docs | LOW |

**Recommendation:** Focus on `advisories.gitlab.com` only, as other subdomains may be out of scope.

---

## Remediation

### 1. Restrict Allowed Origins

```nginx
# Nginx configuration
location / {
    if ($http_origin ~* ^https://(www\/)?.gitlab.com$) {
        add_header 'Access-Control-Allow-Origin' $http_origin;
        add_header 'Access-Control-Allow-Credentials' 'true';
        add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS';
        add_header 'Access-Control-Allow-Headers' 'Content-Type';
    }
}
```

### 2. Use Origin Allowlist in Application Code

```python
ALLOWED_ORIGINS = [
    'https://gitlab.com',
    'https://www.gitlab.com',
    'https://about.gitlab.com',
    'https://docs.gitlab.com'
]

@app.after_request
def add_cors_headers(response):
    origin = request.headers.get('Origin')
    if origin in ALLOWED_ORIGINS:
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response
```

### 3. Remove CORS Headers If Not Needed

```nginx
# If cross-origin access is not required, remove headers entirely
location / {
    # No CORS headers added
}
```

---

## References

- [OWASP CORS Security Cheatsheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
- [MDN CORS Documentation](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [GitLab HackerOne Program](https://hackerone.com/gitlab)
- [PortSwigger CORS](https://portswigger.net/web-security/cors)

---

## Timeline

- **Date Discovered:** 2026-06-06
- **Date Reported:** 2026-06-06
- **Date Acknowledged:** [Pending]
- **Date Fixed:** [Pending]

---

**Reporter:** SARAhack
**Platform:** HackerOne
**Program:** GitLab
**Hunting Method:** Subdomain enumeration + CORS header scanning with amass + curl