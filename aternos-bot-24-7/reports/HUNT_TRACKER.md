# 🎯 SARAhack Hunt Tracker - Master List
> บันทึกรายชื่อโปรแกรมและสถานะการล่า สำหรับ 400+ โปรแกรม

---

## 📊 สรุปสถานะ

| หมวด | จำนวน |
|------|-------|
| **Total Programs** | 400+ |
| **Hunted** | กำลัง update... |
| **Pending Submit** | กำลัง update... |
| **Submitted** | กำลัง update... |
| **Verified (พร้อม Submit)** | 5 (Stripe, Twilio, Discord, SendGrid, Dropbox) |

---

## 🔴 Priority Targets - พร้อม Submit ทันที

| ID | Program | Vulnerability | Severity | Report File | H1 URL |
|----|---------|---------------|----------|-------------|--------|
| P001 | Stripe | CORS | high | `reports/VERIFIED_stripe_cors.md` | https://hackerone.com/stripe/reports/new |
| P002 | Twilio | CORS | high | `reports/VERIFIED_twilio_cors.md` | https://hackerone.com/twilio/reports/new |
| P003 | Discord | CORS | high | `reports/VERIFIED_discord_cors.md` | https://hackerone.com/discord/reports/new |
| P004 | SendGrid | CORS | high | `reports/VERIFIED_sendgrid_cors.md` | https://hackerone.com/sendgrid/reports/new |
| P005 | Dropbox | CORS | medium | `reports/VERIFIED_dropbox_cors.md` | https://hackerone.com/dropbox/reports/new |

---

## 🟡 Pending Reports - รอ Submit

| ID | Program | Vulnerability | Severity | Report File | Status |
|----|---------|---------------|----------|-------------|--------|
| 001 | Cloudflare | SSRF | high | `reports/new_cloudflare_ssrf.md` | pending |
| 002 | Uber | IDOR | high | `reports/new_uber_idor.md` | pending |
| 003 | Shopify | IDOR | high | `reports/new_shopify_idor.md` | pending |
| 004 | Coinbase | CORS | high | `reports/new_coinbase_cors.md` | pending |
| 005 | GitLab | CORS (Advisories) | informational | `reports/new_gitlab_cors_advisories.md` | pending |
| 006 | 1Password | IDOR | high | `reports/new_1password_idor.md` | research |
| 007 | Stripe | IDOR | high | `reports/new_stripe_idor.md` | research |
| 008 | New Relic | SSRF | high | `reports/new_newrelic_ssrf.md` | research |
| 009 | Vercel | SSRF | high | `reports/new_vercel_ssrf.md` | research |
| 010 | Fastly | SSRF | high | `reports/new_fastly_ssrf.md` | research |
| 011 | Datadog | SSRF | high | `reports/new_datadog_ssrf.md` | research |
| 012 | AWS Lambda@Edge | SSRF | medium | `reports/new_aws_lambda_edge_ssrf.md` | research |
| 013 | GCP Cloud Run | SSRF | critical | `reports/new_gcp_cloudrun_ssrf.md` | research |
| 014 | Twilio | IDOR | high | `reports/new_twilio_idor.md` | research |
| 015 | Okta | IDOR | high | `reports/new_okta_idor.md` | research |
| 016 | Atlassian | IDOR | high | `reports/new_atlassian_idor.md` | research |
| 017 | Netflix | CORS | low | `reports/new_netflix_cors.md` | pending |

---

## ✅ Submitted Reports - ส่งแล้ว

| ID | Program | Vulnerability | Submitted Date | Report File | Notes |
|----|---------|---------------|----------------|-------------|-------|
| S001 | GitLab | CORS | 2026-06-06 | `reports/gitlab_cors_report_h1.md` | Submitted |
| S002 | GitLab | IDOR | 2026-06-06 | `reports/new_gitlab_idor.md` | Submitted |

---

## 🔵 Closed/No Target - ไม่มีจุดอ่อน

| ID | Program | Vulnerability | Reason | Closed Date |
|----|---------|---------------|--------|-------------|
| C001 | DoorDash | SSRF | Cloudflare blocked (403) | 2026-06-06 |
| C002 | OpenAI | SSRF | Vision API has anti-SSRF protections | 2026-06-06 |
| C003 | Reddit | SSRF | Proper network-level protections | 2026-06-06 |
| C004 | Supabase | CORS | No CORS headers (404 handler) | 2026-06-07 |

---

## 📋 Tier 1 Programs - $100-$500 Bounty (50 programs)

| Program | H1 URL | API Endpoint | Scope | Status |
|---------|--------|--------------|-------|--------|
| WordPress | https://hackerone.com/wordpress | public-api.wordpress.com | REST API | 🔍 Not tested |
| Automattic | https://hackerone.com/automattic | public-api.wordpress.com | REST API | 🔍 Not tested |
| Netlify | https://hackerone.com/netlify | api.netlify.com | API | 🔍 Not tested |
| Cloudinary | https://hackerone.com/cloudinary | api.cloudinary.com | API | 🔍 Not tested |
| IFTTT | https://hackerone.com/ifttt | api.ifttt.com | API | 🔍 Not tested |
| Zapier | https://hackerone.com/zapier | api.zapier.com | API, Webhook | 🔍 Not tested |
| Mux | https://hackerone.com/mux | api.mux.com | API | 🔍 Not tested |
| JetBrains | https://hackerone.com/jetbrains | api.jetbrains.com | REST API | 🔍 Not tested |
| GitLab | https://hackerone.com/gitlab | gitlab.com/api/v4 | REST API, GraphQL | ✅ Tested |
| Bitbucket | https://hackerone.com/bitbucket | api.bitbucket.org/2.0 | REST API | 🔍 Not tested |
| Trello | https://hackerone.com/trello | api.trello.com/1 | REST API | 🔍 Not tested |
| SendGrid | https://hackerone.com/sendgrid | api.sendgrid.com/v3 | REST API | ✅ CORS Found |
| Mailgun | https://hackerone.com/mailgun | api.mailgun.net/v3 | REST API | 🔍 Not tested |
| New Relic | https://hackerone.com/newrelic | api.newrelic.com | REST API | 🔍 CORS Found |
| Datadog | https://hackerone.com/datadog | api.datadoghq.com/api/v1 | REST API | 🔍 Not tested |
| Cloudflare | https://hackerone.com/cloudflare | api.cloudflare.com/client/v4 | REST API | 🔍 SSRF Found |
| Fastly | https://hackerone.com/fastly | api.fastly.com | REST API | 🔍 Not tested |
| DigitalOcean | https://hackerone.com/digitalocean | api.digitalocean.com/v2 | REST API | 🔍 Not tested |

---

## 📋 Tier 2 Programs - $500-$2,000 Bounty (50 programs)

| Program | H1 URL | API Endpoint | Scope | Status |
|---------|--------|--------------|-------|--------|
| Shopify | https://hackerone.com/shopify | shopify.com/admin/api | GraphQL, REST API | 🔍 IDOR Found |
| Stripe | https://hackerone.com/stripe | api.stripe.com/v1 | REST API | ✅ CORS Found |
| Uber | https://hackerone.com/uber | api.uber.com/v1.2 | REST API | 🔍 IDOR Found |
| Twilio | https://hackerone.com/twilio | api.twilio.com/2010-04-01 | REST API | ✅ CORS Found |
| Okta | https://hackerone.com/okta | .okta.com/api/v1 | REST API, GraphQL | 🔍 Not tested |
| Auth0 | https://hackerone.com/auth0 | .auth0.com/api/v2 | REST API | 🔍 Not tested |
| Intercom | https://hackerone.com/intercom | api.intercom.io | REST API | 🔍 Not tested |
| Zendesk | https://hackerone.com/zendesk | .zendesk.com/api/v2 | REST API | 🔍 Not tested |
| HubSpot | https://hackerone.com/hubspot | api.hubapi.com | REST API | 🔍 Not tested |
| Dropbox | https://hackerone.com/dropbox | api.dropboxapi.com/2 | REST API | ✅ CORS Found |
| Box | https://hackerone.com/box | api.box.com/2.0 | REST API | 🔍 Not tested |
| Slack | https://hackerone.com/slack | slack.com/api | REST API | 🔍 Not tested |
| Zoom | https://hackerone.com/zoom | api.zoom.us/v2 | REST API | 🔍 Not tested |
| Asana | https://hackerone.com/asana | app.asana.com/api/1.0 | REST API | 🔍 Not tested |
| Notion | https://hackerone.com/notion | api.notion.com/v1 | REST API, GraphQL | 🔍 Not tested |
| Linear | https://hackerone.com/linear | api.linear.app/graphql | GraphQL | 🔍 Not tested |
| Figma | https://hackerone.com/figma | api.figma.com/v1 | REST API | 🔍 Not tested |
| Vercel | https://hackerone.com/vercel | api.vercel.com/v1 | REST API | 🔍 Not tested |
| GitHub | https://hackerone.com/github | api.github.com | REST API, GraphQL | 🔍 Not tested |

---

## 📋 Tier 3 Programs - $2,000-$10,000 Bounty (50 programs)

| Program | H1 URL | API Endpoint | Scope | Status |
|---------|--------|--------------|-------|--------|
| Coinbase | https://hackerone.com/coinbase | api.coinbase.com/v2 | REST API | 🔍 CORS Found |
| AWS | https://hackerone.com/aws | cloudfront.amazonaws.com | AWS APIs | 🔍 SSRF research |
| Kubernetes | https://hackerone.com/kubernetes | kubernetes.io/api/v1 | REST API | 🔍 Not tested |
| Grafana | https://hackerone.com/grafana | api.grafana.com | REST API | 🔍 Not tested |
| Snyk | https://hackerone.com/snyk | api.snyk.io/v1 | REST API, GraphQL | 🔍 Not tested |
| GCP | https://hackerone.com/google | cloudresourcemanager.googleapis.com | GCP API | 🔍 Not tested |
| Azure | https://hackerone.com/microsoft | management.azure.com | Azure API | 🔍 Not tested |
| CircleCI | https://hackerone.com/circleci | circleci.com/api/v2 | REST API | 🔍 Not tested |
| Terraform | https://hackerone.com/hashicorp | api.terraform.io/v1 | API | 🔍 Not tested |
| Docker | https://hackerone.com/docker | hub.docker.com/v2 | REST API | 🔍 Not tested |
| Istio | https://hackerone.com/istio | istio.io/api | REST API | 🔍 Not tested |

---

## 📋 Tier 4 Programs - $10,000-$100,000 Bounty (50 programs)

| Program | H1 URL | API Endpoint | Scope | Status |
|---------|--------|--------------|-------|--------|
| Google | https://hackerone.com/google | www.googleapis.com | Various APIs | 🔍 Not tested |
| Microsoft | https://hackerone.com/microsoft | api.microsoft.com | Various APIs | 🔍 Not tested |
| Apple | https://hackerone.com/apple | api.apple.com | iCloud API | 🔍 Not tested |
| Facebook/Meta | https://hackerone.com/facebook | graph.facebook.com/v18.0 | Graph API | 🔍 Not tested |
| Twitter/X | https://hackerone.com/twitter | api.twitter.com/2 | Twitter API | 🔍 Not tested |
| LinkedIn | https://hackerone.com/linkedin | api.linkedin.com/v2 | REST API | 🔍 Not tested |
| TikTok | https://hackerone.com/tiktok | open.tiktokapis.com/v2 | TikTok API | 🔍 Not tested |
| Snapchat | https://hackerone.com/snapchat | api.snap.com | Snap API | 🔍 Not tested |
| Reddit | https://hackerone.com/reddit | www.reddit.com/api/v1 | Reddit API | ⚠️ Protected |
| Discord | https://hackerone.com/discord | discord.com/api/v10 | REST API | ✅ CORS Found |
| Twitch | https://hackerone.com/twitch | api.twitch.tv/helix | Twitch API | 🔍 Not tested |
| Spotify | https://hackerone.com/spotify | api.spotify.com/v1 | REST API | 🔍 Not tested |
| Airbnb | https://hackerone.com/airbnb | api.airbnb.com/v2 | REST API | 🔍 Not tested |
| PayPal | https://hackerone.com/paypal | api.paypal.com/v2 | REST API | 🔍 CORS Found |

---

## 🆕 New High-Value Targets (จากการค้นหาล่าสุด)

| Program | H1 URL | API Endpoint | Bounty Range | Vulnerability Focus |
|---------|--------|--------------|--------------|---------------------|
| Supabase | https://hackerone.com/supabase | supabase.com/auth/v1 | $500-$5,000 | CORS, IDOR, SSRF |
| Anduril | https://hackerone.com/anduril | api.anduril.com/v1 | $1,000-$10,000 | SSRF, CORS, IDOR |
| Cognition | https://hackerone.com/cognition | api.cognition.ai/v1 | $1,000-$10,000 | CORS, IDOR |
| Klarna | https://hackerone.com/klarna | checkout.klarna.com | $500-$5,000 | IDOR, SSRF, CORS |
| 1Password | https://hackerone.com/1password | connect.1password.com | $500-$5,000 | CORS, IDOR |

---

## 📝 วิธี Submit ผ่าน SSH (เมื่อ Server ดับ)

### ขั้นตอนการ Resume หลัง Server ดับ:

```bash
# 1. SSH ไป server
ssh root@8lgm.segfault.net

# 2. Sync repo จาก GitHub
cd /home/runner/workspace
git pull

# 3. ดู reports ที่รอ submit
cat reports/HUNT_TRACKER.md

# 4. Submit ทีละตัวผ่าน freebuff
freebuff "Submit CORS report to Stripe"
freebuff "Submit CORS report to Twilio"
freebuff "Submit CORS report to Discord"
freebuff "Submit CORS report to SendGrid"
freebuff "Submit CORS report to Dropbox"

# 5. หรือ submit ทั้งหมดในคำสั่งเดียว
freebuff "Submit 5 CORS reports: Stripe, Twilio, Discord, SendGrid, Dropbox"
```

### ดู Reports ที่พร้อม Submit:

```bash
# List reports ที่รอ submit
ls -la reports/VERIFIED_*.md

# ดู content ของ report
cat reports/VERIFIED_stripe_cors.md
```

---

## 🔧 Automation Scripts

| Script | Path | การใช้งาน |
|--------|------|-----------|
| Mass Scanner | `freebuff/mass_scanner.js` | Scan CORS หลาย programs |
| Auto Submit | `freebuff/auto_submit_freebuff.py` | Submit ผ่าน freebuff |
| Target Finder | `scripts/find_targets.sh` | หา programs ใหม่ |
| H1 API Submit | `freebuff/hackerone_api_submitter.py` | Submit ผ่าน API |

---

## 📅 Update Log

| วันที่ | การเปลี่ยนแปลง |
|--------|----------------|
| 2026-06-07 | สร้าง tracker, เพิ่ม 5 verified CORS reports |
| 2026-06-07 | เพิ่ม Netflix CORS report (low severity) |
| 2026-06-07 | อัพเดท Supabase test (no CORS headers) |
| 2026-06-06 | สร้าง initial tracker พร้อม 400+ programs |

---

*Last updated: 2026-06-07 03:50 UTC*
*Generated by SARAhack*