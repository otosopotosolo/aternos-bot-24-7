# ✅ SARAhack Hunting Checklist
> รายการตรวจสอบสำหรับการล่า Bug Bounty ประจำวัน

---

## 🎯 Daily Hunting Checklist

### ก่อนเริ่มล่า (ทุกครั้ง)

- [ ] **Sync Repository**
  ```bash
  cd /home/runner/workspace
  git pull origin main
  ```

- [ ] **ตรวจสอบ Reports ที่รอ Submit**
  ```bash
  cat reports/SUBMISSION_QUEUE.md
  ls -la reports/VERIFIED_*.md
  ```

- [ ] **ตรวจสอบ Server Status**
  ```bash
  # SSH ไป server
  ssh root@8lgm.segfault.net
  # หรือผ่าน tmate
  ssh eS6fytCGPu74pDmMNxAKcszLc@lon1.tmate.io
  ```

---

### 🔴 Priority 1: Submit Verified Reports (ทำทันที)

- [ ] **Submit Stripe CORS**
  ```bash
  freebuff "Submit Stripe CORS report"
  ```
  - File: `reports/VERIFIED_stripe_cors.md`
  - URL: https://hackerone.com/stripe/reports/new

- [ ] **Submit Twilio CORS**
  ```bash
  freebuff "Submit Twilio CORS report"
  ```
  - File: `reports/VERIFIED_twilio_cors.md`
  - URL: https://hackerone.com/twilio/reports/new

- [ ] **Submit Discord CORS**
  ```bash
  freebuff "Submit Discord CORS report"
  ```
  - File: `reports/VERIFIED_discord_cors.md`
  - URL: https://hackerone.com/discord/reports/new

- [ ] **Submit SendGrid CORS**
  ```bash
  freebuff "Submit SendGrid CORS report"
  ```
  - File: `reports/VERIFIED_sendgrid_cors.md`
  - URL: https://hackerone.com/sendgrid/reports/new

- [ ] **Submit Dropbox CORS**
  ```bash
  freebuff "Submit Dropbox CORS report"
  ```
  - File: `reports/VERIFIED_dropbox_cors.md`
  - URL: https://hackerone.com/dropbox/reports/new

---

### 🟡 Priority 2: Scan New Targets

- [ ] **Run Mass Scanner บน High-Value Targets**
  ```bash
  node freebuff/mass_scanner.js --program=netflix --limit=10
  node freebuff/mass_scanner.js --program=klarna --limit=10
  node freebuff/mass_scanner.js --program=cognition --limit=10
  node freebuff/mass_scanner.js --program=supabase --limit=10
  node freebuff/mass_scanner.js --program=1password --limit=10
  ```

- [ ] **หา Programs ใหม่**
  ```bash
  ./scripts/find_targets.sh
  cat reports/drafts/targets_20260607.md
  ```

- [ ] **Test Manual CORS บน Targets ใหม่**
  ```bash
  # Supabase
  curl -s -X OPTIONS 'https://supabase.com/auth/v1/signup' -H 'Origin: https://evil-test.com' -H 'Access-Control-Request-Method: POST' -i
  
  # 1Password
  curl -s -X OPTIONS 'https://connect.1password.com/v1/vaults' -H 'Origin: https://evil-test.com' -i
  
  # Klarna
  curl -s -X OPTIONS 'https://checkout.klarna.com/v1/sessions' -H 'Origin: https://evil-test.com' -i
  ```

---

### 🔵 Priority 3: Research Pending Reports

- [ ] **Research 1Password IDOR**
  ```bash
  cat reports/new_1password_idor.md
  # หา API endpoints ที่ vulnerable
  ```

- [ ] **Research Stripe IDOR**
  ```bash
  cat reports/new_stripe_idor.md
  # หา acquired companies ที่อาจมี vulnerability
  ```

- [ ] **Research New Relic SSRF**
  ```bash
  cat reports/new_newrelic_ssrf.md
  # หา webhook endpoints ที่ vulnerable
  ```

---

### 📊 End of Day Checklist

- [ ] **Update Tracking**
  ```bash
  # อัพเดท reports/tracking/reports.json
  # อัพเดท reports/HUNT_TRACKER.md
  # อัพเดท reports/SUBMISSION_QUEUE.md
  ```

- [ ] **Commit Changes**
  ```bash
  git add reports/
  git commit -m "Update reports - $(date +%Y-%m-%d)"
  git push
  ```

- [ ] **ตรวจสอบ Discord Notifications**
  ```bash
  cat freebuff/discord_notifier.py
  # ส่ง summary ไป Discord
  ```

---

## 🔧 Server Recovery Checklist (เมื่อ Server ดับ)

### ขั้นตอนการ Resume:

1. **SSH ไป Server ใหม่**
   ```bash
   ssh root@8lgm.segfault.net
   ```

2. **Clone หรือ Pull Repository**
   ```bash
   cd /home/runner/workspace
   git clone https://github.com/YOUR_REPO.git
   # หรือ
   git pull
   ```

3. **ตรวจสอบ Environment**
   ```bash
   cat freebuff/tokenlogin.env
   # ต้องมี:
   # HACKERONE_EMAIL=potosopotosolo@gmail.com
   # HACKERONE_PASSWORD=)a9By=*D#6/w9T
   ```

4. **ดู Reports ที่รอ Submit**
   ```bash
   cat reports/SUBMISSION_QUEUE.md
   ls -la reports/VERIFIED_*.md
   ```

5. **Submit Reports ที่พร้อม**
   ```bash
   freebuff "Submit 5 CORS reports: Stripe, Twilio, Discord, SendGrid, Dropbox"
   ```

6. **Sync กลับไป GitHub**
   ```bash
   git add reports/
   git commit -m "Submitted reports - $(date +%Y-%m-%d)"
   git push
   ```

---

## 🌐 Browser Auto-Submit ผ่าน SSH

เมื่อ server มี Chrome ติดตั้งและต้องการ submit อัตโนมัติผ่าน browser:

```bash
# บน server - รัน Playwright auto-submitter
python3 freebuff/playwright_h1_submitter.py --reports stripe,twilio,discord,sendgrid,dropbox

# หรือ submit ทีละตัว
python3 freebuff/playwright_h1_submitter.py --program stripe --vulnerability cors

# ดู help
python3 freebuff/playwright_h1_submitter.py --help
```

**หมายเหตุ:** 
- ต้องมี Chrome installed บน server ถึงจะทำงานได้
- ถ้าไม่มี Chrome ใช้วิธี manual copy-paste จาก reports/SUBMISSION_PACKAGE_CORS_5x.md

### วิธีการ Submit อื่นๆ:

| Method | คำสั่ง | หมายเหตุ |
|--------|--------|----------|
| **freebuff CLI** | `freebuff "Submit Stripe CORS"` | ต้องมี freebuff installed |
| **Playwright** | `python3 freebuff/playwright_h1_submitter.py --reports stripe` | ต้องมี Chrome |
| **Manual** | Copy จาก `reports/SUBMISSION_PACKAGE_CORS_5x.md` | ไม่ต้องใช้ script |
| **H1 API** | ใช้ `freebuff/hackerone_api_submitter.py` | ต้องมี H1_API_TOKEN |

---

## 📋 Quick Reference Commands

| Action | Command |
|--------|---------|
| **ดู pending reports** | `cat reports/SUBMISSION_QUEUE.md` |
| **ดู tracker** | `cat reports/HUNT_TRACKER.md` |
| **สแกน target ใหม่** | `node freebuff/mass_scanner.js --program=TARGET --limit=10` |
| **หา programs ใหม่** | `./scripts/find_targets.sh` |
| **submit ทั้งหมด** | `freebuff "Submit all pending CORS reports"` |
| **ดู tracking** | `cat reports/tracking/reports.json | jq length` |
| **browser auto-submit** | `python3 freebuff/playwright_h1_submitter.py --reports stripe` | ต้องมี Chrome |

---

## 🎯 Target Programs วันนี้

### High Priority (ทำก่อน):
1. ✅ Stripe - CORS (พร้อม submit)
2. ✅ Twilio - CORS (พร้อม submit)
3. ✅ Discord - CORS (พร้อม submit)
4. ✅ SendGrid - CORS (พร้อม submit)
5. ✅ Dropbox - CORS (พร้อม submit)

### Medium Priority:
6. 🔍 Supabase - Test หา actual project API
7. 🔍 1Password - Research IDOR vulnerability
8. 🔍 Klarna - Test CORS on checkout API
9. 🔍 Netflix - CORS found (low severity, optional submit)

### Low Priority (ถ้ามีเวลา):
10. 🔍 Shopify - IDOR research
11. 🔍 Cloudflare - SSRF research
12. 🔍 Uber - IDOR research

---

## 📊 Progress Tracking

| Metric | Value | Notes |
|--------|-------|-------|
| **Total Reports Ready** | 10 | Verified + Pending |
| **Verified (พร้อม submit)** | 5 | Stripe, Twilio, Discord, SendGrid, Dropbox |
| **Pending Research** | 12 | กำลังทำ |
| **Submitted Today** | 0 | ยังไม่ได้ submit |
| **Programs Scanned** | 15+ | Mass scanner results |

---

*Last updated: 2026-06-07*
*Generated by SARAhack*