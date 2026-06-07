# CORS Misconfiguration Bug Report

## Report Template

**Platform:** [HackerOne/Bugcrowd]
**Program:** [Program Name]
**Severity:** [HIGH/MEDIUM/LOW]
**Report Date:** [YYYY-MM-DD]

---

## Summary

A Cross-Origin Resource Sharing (CORS) misconfiguration was discovered in [target endpoint], allowing unauthorized cross-origin access to sensitive data.

---

## Description

[Describe the vulnerability and how it was discovered]

The affected endpoint improperly implements CORS headers, allowing arbitrary origins to access resources.

---

## Steps to Reproduce

1. Navigate to [affected URL]
2. Send a request with `Origin: https://attacker.com` header
3. Observe the response includes `Access-Control-Allow-Origin: *` or the attacker's origin
4. The response allows credentials (`Access-Control-Allow-Credentials: true`)

---

## PoC (Proof of Concept)

```bash
# Request
curl -i -X GET "https://target.com/api/endpoint" -H "Origin: https://evil.com" -H "Cookie: session=..."

# Expected Response Headers
HTTP/1.1 200 OK
Access-Control-Allow-Origin: https://evil.com
Access-Control-Allow-Credentials: true
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
Content-Type: application/json

# This allows the attacker's site to:
# - Read sensitive data via AJAX
# - Perform actions on behalf of the user
# - Access user-specific endpoints
```

---

## Impact

- **Confidentiality:** Attackers can read sensitive user data
- **Integrity:** Attackers may perform actions on behalf of authenticated users
- **Authentication Bypass:** Session cookies may be exposed

**Severity Justification:**
- Allows cross-origin access to sensitive API endpoints
- Can lead to data theft of user information
- Affects all users of the application

---

## Remediation

1. Validate the `Origin` header against an allowlist of permitted origins
2. Do not use `Access-Control-Allow-Origin: *` with `Access-Control-Allow-Credentials: true`
3. Implement proper CORS policy:

```python
# Example fix (Python/Flask)
ALLOWED_ORIGINS = ['https://legitimate-site.com', 'https://www.legitimate-site.com']

@app.after_request
def set_cors_headers(response):
    origin = request.headers.get('Origin')
    if origin in ALLOWED_ORIGINS:
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response
```

---

## References

- [OWASP CORS Security Cheatsheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
- [MDN CORS Documentation](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [CVE-Example](https://cve.mitre.org) (if applicable)

---

## Timeline

- **Date Discovered:** [YYYY-MM-DD]
- **Date Reported:** [YYYY-MM-DD]
- **Date Acknowledged:** [YYYY-MM-DD]
- **Date Fixed:** [YYYY-MM-DD]

---

**Reporter:** [Your Name/HANDLE]
**Platform:** [HackerOne/Bugcrowd Profile]