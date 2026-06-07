# Bug Bounty Targets - 2026

**Research Date:** 2026-06-06
**Sources:** HackerOne, Bugcrowd, Web Research, security.txt

---

## 📧 Email-Based Programs (Direct Email Submission)

### Programs with Monetary Rewards

| Program | Email | Scope | Est. Payout |
|---------|-------|-------|-------------|
| **Proton** | security@proton.me | proton.me, protonmail.com, protonvpn.com | $500-2000 |
| **Intel** | secure@intel.com | intel.com, intel.co.jp (CPU, firmware, software) | $500-10000 |
| **Honeycomb** | security@honeycomb.io | honeycomb.io, API endpoints | $100-500 |
| **atmail** | security@atmail.com | atmail.com, email server software | $100-500 |

> ⚠️ **หมายเหตุ:** Line/Yahoo Japan อาจไม่จ่าย bounty สำหรับ email submissions - ควรตรวจสอบ policy ล่าสุดก่อนส่ง
| **Meta** | Via HackerOne เท่านั้น (facebook.com/bugbounty) | facebook, instagram, whatsapp | $500-15000 |
| **Google VRP** | bughunter.google.com | google.com, chrome, android | $100-31337 |

### VDP (No Reward) - Good for Practice

| Program | Email | Scope |
|---------|-------|-------|
| **Various organizations** | Check security.txt | Any public scope |
| **GoDaddy** | Via HackerOne เท่านั้น (godaddy on H1) | godaddy.com, domain services | $500-1000 |

> 📌 **เคล็ดลับ:** ใช้เครื่องมือต่างๆ หา security.txt:
> ```bash
> # ดึง security.txt จากหลาย domains
> for d in proton.me intel.com shopify.com; do
>   curl -s "https://$d/.well-known/security.txt" | grep -i "contact\|email"
> done
> ```

---

## 🔄 Auto-Submit via freebuff (Cloudflare Bypass)

### HackerOne Programs

| Program | Scope | Est. Payout | Status |
|---------|-------|-------------|--------|
| **Stripe** | *.stripe.com, *.stripe.network | $500-2500 | 🔄 Pending |
| **Discord** | *.discord.com, *.discordapp.com | $500-2000 | 🔄 Pending |
| **Polygon** | polygon.technology, matic.network | $500-1500 | 🔄 Pending |
| **Avalanche** | avax.network, avax.com | $500-1500 | 🔄 Pending |
| **Twilio** | twilio.com, sendgrid.com | $500-1500 | 🔄 Pending |
| **GitLab** | *.gitlab.com | $500-2000 | 🔄 Pending |
| **PayPal** | *.paypal.com, *.paypalobjects.com | $500-2500 | 🎯 Target |
| **Uber** | *.uber.com, *.ubercab.com | $500-1500 | 🎯 Target |
| **Shopify** | *.shopify.com, *.myshopify.com | $500-1500 | 🎯 Target |
| **Spotify** | *.spotify.com | $500-1500 | 🎯 Target |
| **Dropbox** | *.dropbox.com | $500-2000 | 🎯 Target |
| **Coinbase** | *.coinbase.com | $500-3000 | 🎯 Target |
| **Yahoo/Verizon** | *.yahoo.com, *.aol.com | $500-2000 | 🎯 Target |
| **Nintendo** | *.nintendo.net, *.nintendo.co.jp | $500-1500 | 🎯 Target |
| **Salesforce** | *.salesforce.com | $500-2000 | 🎯 Target |

### Bugcrowd Programs

| Program | Scope | Est. Payout | Status |
|---------|-------|-------------|--------|
| **Salesforce** | *.salesforce.com | $500-2000 | 🎯 Target |

---

## 🛠️ How to Submit

### Email Submission (Proton, Intel, etc.)

> ⚠️ **สำคัญ:** หลาย programs ต้องการ PGP encryption สำหรับ email reports

```bash
# ตรวจสอบ tools ที่มีใน server
which swaks mutt sendemail 2>/dev/null || echo "Need to install"

# วิธีที่ 1: ใช้ swaks (simple SMTP tester)
swaks -to security@proton.me -from researcher@gmail.com \
  --header "Subject: [Security] Bug Report" \
  --body "$(cat reports/gitlab_cors_report_h1.md)"

# วิธีที่ 2: ใช้ mutt (email client)
mutt -s "[Security] CORS Misconfiguration" \
    -a reports/gitlab_cors_report_h1.md \
    -- security@proton.me < /dev/null

# วิธีที่ 3: ใช้ sendemail (ติดตั้งก่อน: apt install sendemail)
sendemail -f researcher@gmail.com -t security@proton.me \
    -u "[Security] Bug Report" -m "Report content here"
```

> 📌 **PGP Encryption:** Intel และ Proton อาจต้องการ PGP encrypted reports
> ตรวจสอบ security.txt ของแต่ละ program ก่อนส่ง

### Auto-Submit via freebuff (HackerOne/Bugcrowd)

> 🔧 **หมายเหตุ:** ต้อง test connection ก่อนใช้งาน

```bash
# Test connection
python3 freebuff/freebuff_bounty.py test-connection

# Test Cloudflare bypass
python3 freebuff/freebuff_bounty.py test-bypass --url https://hackerone.com

# Submit report
python3 freebuff/freebuff_bounty.py submit --platform hackerone --program gitlab --file reports/gitlab_cors_report_h1.md

# หา targets ใหม่ (ถ้าต้องการ)
python3 freebuff/freebuff_bounty.py find --keyword CORS
```

---

## 🎯 Recommended Priority Order

### HIGH Priority (High payout, accessible scope)

1. **Stripe** (HackerOne) - $500-2500, large API scope
2. **Coinbase** (HackerOne) - $500-3000, crypto focus
3. **PayPal** (HackerOne) - $500-2500, financial data
4. **Proton** (Email) - $500-2000, email-based (easy submit)
5. **Google VRP** (Independent) - $100-31337, wide scope
6. **Stellar SDF** (HackerOne) - $2000-25000, Crypto, IDOR
7. **TikTok** (HackerOne) - $500-2500, social media API
8. **Fastly** (HackerOne) - $2500-20000, Cloud Infra, SSRF

### MEDIUM Priority

9. **Discord** (HackerOne) - $500-2000, API targets
10. **Shopify** (HackerOne) - $500-1500, e-commerce APIs
11. **Intel** (Email) - $500-10000, firmware/hardware
12. **Meta/Facebook** (HackerOne) - $500-15000, social media
13. **HashiCorp** (HackerOne) - $2000-15000, Cloud Infra, SSRF
14. **Hugging Face** (HackerOne) - $2000-10000, AI/ML, Model security
15. **Yahoo** (Intigriti) - $500-2000, large scope

### LOW Priority (Good for practice)

16. **GitLab** (HackerOne) - Informational (public data)
17. **Dropbox** (HackerOne) - $500-2000
18. **Uber** (HackerOne) - $500-1500
19. **Tencent** (Bugcrowd) - $500-1500, tech/social
20. **Revolut** (Intigriti) - $2000-10000, Fintech, IDOR
21. **Unity** (HackerOne) - $2000-15000, Gaming API
22. **PagerDuty** (Bugcrowd) - $2000-15000, SaaS, IDOR/SSRF
23. **Grafana Labs** (Intigriti) - SaaS/API, infrastructure

---

## 💡 YesWeHack Programs (NEW!)

| Program | Platform | Scope | Bounty |
|---------|----------|-------|--------|
| **Orange** | YesWeHack | Telecom, API, IoT | $500-15,000 |
| **Keycloak** | YesWeHack | Identity (IAM), Auth APIs | $300-8,000 |
| **TeamViewer** | YesWeHack | Remote Access, IoT | $1,000-20,000 |
| **Ledger** | YesWeHack | Crypto Hardware, Embedded | $1,000-50,000 |
| **Withings** | YesWeHack | IoT, Health devices | $500-10,000 |

---

## 🚀 NEW Programs (June 2026)

### AI/ML Sector
| Program | Platform | Scope | Bounty |
|---------|----------|-------|--------|
| **Hugging Face** | HackerOne | huggingface.co, spaces, models | $2,000-10,000 |
| **Mistral AI** | HackerOne (VDP) | mistral.ai, API | VDP |

### Cloud Infrastructure
| Program | Platform | Scope | Bounty |
|---------|----------|-------|--------|
| **HashiCorp** | HackerOne | hashicorp.com, Consul, Vault, Terraform | $2,000-15,000 |
| **Fastly** | HackerOne | fastly.net, Edge computing | $2,500-20,000 |
| **PagerDuty** | Bugcrowd | pagerduty.com, API | $2,000-15,000 |
| **Grafana Labs** | Intigriti | grafana.com, Loki, Prometheus | $1,000-5,000 |

### Crypto/Web3
| Program | Platform | Scope | Bounty |
|---------|----------|-------|--------|
| **Stellar SDF** | HackerOne | stellar.org, API, network | $2,000-25,000 |
| **Chainlink** | Immunefi | chain.link, smart contracts | $5,000-100,000+ |
| **Solana** | Immunefi | solana.com, protocol/nodes | $5,000-100,000+ |

### Fintech
| Program | Platform | Scope | Bounty |
|---------|----------|-------|--------|
| **Revolut** | Intigriti | revolut.com, mobile API | $2,000-10,000 |

### Gaming
| Program | Platform | Scope | Bounty |
|---------|----------|-------|--------|
| **Unity** | HackerOne | unity.com, gaming platform API | $2,000-15,000 |
| **Valve** | HackerOne | Steam, gaming platform | $500-20,000 |

### Automotive/IoT
| Program | Platform | Scope | Bounty |
|---------|----------|-------|--------|
| **Tesla** | Bugcrowd | Automotive, IoT, Embedded | $1,000-100,000 |
| **Garmin** | Bugcrowd | Wearables, Mobile | $500-10,000 |
| **Cisco** | Bugcrowd | Network, IoT, Embedded | $1,000-25,000 |
| **Canonical** | HackerOne | Ubuntu Core, IoT | $300-5,000 |

### OAuth/Auth Focus
| Program | Platform | Scope | Bounty |
|---------|----------|-------|--------|
| **Okta** | Bugcrowd | Identity, OAuth, API | $500-15,000 |
| **Auth0** | Bugcrowd | Auth APIs, Identity | $500-10,000 |
| **Keycloak** | YesWeHack | Identity (IAM), Auth APIs | $300-8,000 |

### GraphQL Focus
| Program | Platform | Scope | Bounty |
|---------|----------|-------|--------|
| **GitHub** | HackerOne | API, Auth, GraphQL | $600-30,000 |
| **Shopify** | HackerOne | API, GraphQL, IDOR | $500-50,000 |

---

## 🔍 Finding New Targets

### 1. security.txt Discovery
```bash
# Check security.txt for new targets
for domain in "proton.me" "intel.com" "shopify.com"; do
  curl -s "https://$domain/.well-known/security.txt" 2>/dev/null | grep -i "contact"
done

# Mass check with hakrevdns or masscan
```

### 2. Platform Search
```bash
# Find programs via freebuff
python3 freebuff/freebuff_bounty.py find --keyword CORS
python3 freebuff/freebuff_bounty.py find --keyword SSRF
python3 freebuff/freebuff_bounty.py find --keyword IDOR
```

### 3. HackerOne/Bugcrowd API
```bash
# Monitor new programs (via web scraping)
# Use freebuff for research
```

---

## 📊 Submission Status

| Program | Platform | Vulnerability | Severity | Status |
|---------|----------|--------------|----------|--------|
| GitLab | HackerOne | CORS | Informational | 📋 Pending |
| Stripe | HackerOne | CORS | HIGH | ✅ Submitted (33 total) |
| Discord | HackerOne | CORS | HIGH | ✅ Submitted |

---

**Last Updated:** 2026-06-06

> ⚠️ **ตรวจสอบ Policy ล่าสุด:** Program policies เปลี่ยนบ่อย ควร verify ก่อน submit เสมอ