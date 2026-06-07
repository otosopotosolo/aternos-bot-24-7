# SUBMISSION PACKAGE - Batch 3
# Date: 2026-06-07
# Total Reports: 9

---

## 🔐 HACKERONE LOGIN CREDENTIALS

```
Email: potosopotosolo@gmail.com
Password: )a9By=*D#6/w9T
```

**Login URL:** https://hackerone.com/login

---

## 📋 REPORTS TO SUBMIT (9 Reports)

### 1. Cloudflare SSRF
| Field | Value |
|-------|-------|
| **Program** | Cloudflare |
| **URL** | https://hackerone.com/cloudflare/reports/new |
| **Severity** | High |
| **File** | `reports/new_cloudflare_ssrf.md` |
| **Vulnerability** | Server-Side Request Forgery (SSRF) in Cloudflare Workers |
| **Key Points** | Origin IP reconnaissance, WAF bypass via SSRF, metadata access |

### 2. Uber IDOR
| Field | Value |
|-------|-------|
| **Program** | Uber |
| **URL** | https://hackerone.com/uber/reports/new |
| **Severity** | High |
| **File** | `reports/new_uber_idor.md` |
| **Vulnerability** | IDOR in Trip API - access other users' trips/receipts |
| **Key Points** | Trip ID enumeration, fuel card activation IDOR, document upload IDOR |

### 3. Shopify IDOR
| Field | Value |
|-------|-------|
| **Program** | Shopify |
| **URL** | https://hackerone.com/shopify/reports/new |
| **Severity** | High |
| **File** | `reports/new_shopify_idor.md` |
| **Vulnerability** | IDOR in GraphQL Admin API - cross-store billing access |
| **Key Points** | BillingInvoice/BillingDocument/AppSubscription ID enumeration |

### 4. Coinbase CORS
| Field | Value |
|-------|-------|
| **Program** | Coinbase |
| **URL** | https://hackerone.com/coinbase/reports/new |
| **Severity** | High |
| **File** | `reports/new_coinbase_cors.md` |
| **Vulnerability** | CORS Misconfiguration with credentialed cross-origin access |
| **Key Points** | Origin reflection with Access-Control-Allow-Credentials: true |

### 5. Stripe CORS (NEW - from mass scanner)
| Field | Value |
|-------|-------|
| **Program** | Stripe |
| **URL** | https://hackerone.com/stripe/reports/new |
| **Severity** | High |
| **File** | `reports/new_stripe_cors.md` |
| **Vulnerability** | CORS Misconfiguration |
| **Key Points** | Dynamic origin reflection, credentialed requests allowed |

### 6. Twilio CORS (NEW - from mass scanner)
| Field | Value |
|-------|-------|
| **Program** | Twilio |
| **URL** | https://hackerone.com/twilio/reports/new |
| **Severity** | High |
| **File** | `reports/new_twilio_cors.md` |
| **Vulnerability** | CORS Misconfiguration |
| **Key Points** | Origin reflection, credentialed cross-origin access |

### 7. Discord CORS (NEW - from mass scanner)
| Field | Value |
|-------|-------|
| **Program** | Discord |
| **URL** | https://hackerone.com/discord/reports/new |
| **Severity** | High |
| **File** | `reports/new_discord_cors.md` |
| **Vulnerability** | CORS Misconfiguration |
| **Key Points** | Origin reflection, credentialed cross-origin access |

### 8. SendGrid CORS (NEW - from mass scanner)
| Field | Value |
|-------|-------|
| **Program** | SendGrid |
| **URL** | https://hackerone.com/sendgrid/reports/new |
| **Severity** | High |
| **File** | `reports/new_sendgrid_cors.md` |
| **Vulnerability** | CORS Misconfiguration |
| **Key Points** | Origin reflection with credentials |

### 9. Dropbox CORS (NEW - from mass scanner)
| Field | Value |
|-------|-------|
| **Program** | Dropbox |
| **URL** | https://hackerone.com/dropbox/reports/new |
| **Severity** | Medium |
| **File** | `reports/new_dropbox_cors.md` |
| **Vulnerability** | CORS Misconfiguration |
| **Key Points** | Arbitrary origin reflection |

---

## 📝 SUBMISSION STEPS

### Step 1: Login to HackerOne
1. Go to https://hackerone.com/login
2. Enter email: `potosopotosolo@gmail.com`
3. Enter password: `)a9By=*D#6/w9T`

### Step 2: Submit Each Report
For each report:
1. Navigate to the program's submission URL
2. Copy content from the report file
3. Paste into the HackerOne report form
4. Submit

### Step 3: Update Tracking
After submitting each report, note the report ID from HackerOne URL.

---

## ⏱️ QUICK COPY - Report Titles

| # | Title |
|---|-------|
| 1 | **Cloudflare Workers SSRF - Origin IP Reconnaissance and WAF Bypass** |
| 2 | **Uber Trip API IDOR - Horizontal Privilege Escalation via Trip ID Enumeration** |
| 3 | **Shopify GraphQL Admin API IDOR - Cross-Store Billing Invoice Access** |
| 4 | **Coinbase API CORS Misconfiguration - Credentialed Cross-Origin Access** |
| 5 | **Stripe API CORS Misconfiguration - Dynamic Origin Reflection with Credentials** |
| 6 | **Twilio API CORS Misconfiguration - Credentialed Cross-Origin Access** |
| 7 | **Discord API CORS Misconfiguration - Credentialed Cross-Origin Access** |
| 8 | **SendGrid API CORS Misconfiguration - Origin Reflection with Credentials** |
| 9 | **Dropbox API CORS Misconfiguration - Arbitrary Origin Reflection** |

---

## 📊 SUBMISSION CHECKLIST

- [ ] Cloudflare SSRF - Submit
- [ ] Uber IDOR - Submit
- [ ] Shopify IDOR - Submit
- [ ] Coinbase CORS - Submit
- [ ] Stripe CORS - Submit
- [ ] Twilio CORS - Submit
- [ ] Discord CORS - Submit
- [ ] SendGrid CORS - Submit
- [ ] Dropbox CORS - Submit

---

## 📁 Report File Locations

```
reports/new_cloudflare_ssrf.md
reports/new_uber_idor.md
reports/new_shopify_idor.md
reports/new_coinbase_cors.md
reports/new_stripe_cors.md
reports/new_twilio_cors.md
reports/new_discord_cors.md
reports/new_sendgrid_cors.md
reports/new_dropbox_cors.md
```

---

**⚠️ Note:** Chrome/Playwright not available in current environment. Manual browser submission required.

**After submission:** Update `reports/tracking/reports.json` with status "submitted" and date_submitted.