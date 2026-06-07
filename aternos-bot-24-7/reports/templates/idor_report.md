# Insecure Direct Object Reference (IDOR) Bug Report

## Report Template

**Platform:** [HackerOne/Bugcrowd/Intigriti]
**Program:** `[PROGRAM_NAME]`
**Vulnerability:** Insecure Direct Object Reference (IDOR)
**Severity:** HIGH / MEDIUM / LOW
**Report Date:** YYYY-MM-DD
**Target URL:** `https://api.target.com/v1/[resource]`
**CWE:** CWE-639: Authorization Bypass Through User-Controlled Key

---

## Summary

An Insecure Direct Object Reference (IDOR) vulnerability was discovered in `[TARGET_ENDPOINT]`, allowing an attacker to access or modify resources belonging to other users by manipulating object identifiers (IDs, UUIDs, etc.).

**Attack Scenario:** As a low-privileged user, I can access other users' resources by simply changing the ID in the URL or API request:
- View private user profiles
- Access/download other users' files
- Modify other users' settings/data
- Access billing/invoice information

---

## Description

[Describe the vulnerability and how it was discovered]

The affected endpoint exposes direct references to internal objects (such as database IDs, file names, or document IDs) without proper authorization checks.

---

## Steps to Reproduce

1. Login as user A (attacker account)
2. Navigate to [affected page/endpoint]
3. Identify parameter that controls resource access [e.g., ?id=, ?user_id=, ?account=]
4. Change the parameter value to another user's identifier
5. Observe that you can now access/modify the other user's data

---

## PoC (Proof of Concept)

```bash
# As user A, access own data
curl -b "session=USER_A_COOKIE" \\
     "https://target.com/api/profile?id=12345"

# Response shows: {"id": "12345", "name": "User A", "email": "usera@example.com"}

# Change to user B's ID
curl -b "session=USER_A_COOKIE" \\
     "https://target.com/api/profile?id=12346"

# Response shows: {"id": "12346", "name": "User B", "email": "userb@example.com"}

# CONFIRMED: User A can read User B's data!
```

**Video PoC:** [Link to video if available]

---

## Impact

- **Data Confidentiality Breach** - Access other users' sensitive data
- **Data Modification** - Modify other users' data
- **Account Takeover** - In severe cases, modify password/email
- **Financial Impact** - Access payment/billing information

**Severity Justification:**
- Allows horizontal privilege escalation
- Exposes personally identifiable information (PII)
- No special privileges required
- Affects all users of the platform

---

## Affected Endpoints

| Endpoint | Parameter | Access Type |
|----------|-----------|-------------|
| /api/profile | id | Read |
| /api/settings | user_id | Read/Write |
| /api/invoices | invoice_id | Read |

---

## Remediation

1. **Implement proper authorization:**
```python
@require_auth
@require_resource_owner
def get_resource(resource_id):
    # Verify user owns the resource before returning
    resource = db.get(resource_id)
    if resource.user_id != current_user.id:
        abort(403)  # Forbidden
    return resource
```

2. **Use indirect references:**
```python
# Instead of exposing DB IDs, use random non-guessable IDs
resource_id = generate_secure_token()  # e.g., UUID or JWT
```

3. **Add access control checks at every level:**
```python
# Verify session matches resource owner
if session.user_id != resource.owner_id:
    raise UnauthorizedError()
```

---

## References

- [OWASP IDOR](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/05-Authorization_Testing/04-Testing_for_Insecure_Direct_Object_References)
- [PortSwigger IDOR](https://portswigger.net/web-security/access-control/idor)
- [IDOR Prevention Cheatsheet](https://cheatsheetseries.owasp.org/cheatsheets/Insecure_Direct_Object_Reference_Prevention_Cheat_Sheet.html)

---

## Timeline

- **Date Discovered:** [YYYY-MM-DD]
- **Date Reported:** [YYYY-MM-DD]
- **Date Acknowledged:** [YYYY-MM-DD]
- **Date Fixed:** [YYYY-MM-DD]

---

**Reporter:** [Your Name/HANDLE]
**Platform:** [HackerOne/Bugcrowd Profile]