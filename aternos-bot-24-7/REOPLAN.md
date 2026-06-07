# SARAhack - Project Re-Plan

**Created:** 2026-06-06
**Status:** PLANNING PHASE

---

## 🎯 เป้าหมายโปรเจค

สร้าง **Bug Bounty Auto-Submit System** ที่ทำงานร่วมกับ freebuff AI เพื่อ:
1. ค้นหาช่องโหว่และ targets ใหม่ๆ
2. รวบรวมความรู้จากแหล่งต่างๆ (Pentest Book, CVE, etc.)
3. สร้างและ submit reports อัตโนมัติ
4. ติดตามผลและจัดการ rewards

## ⚠️ Critical Blocker: Cloudflare Bypass

**ปัญหา:** HackerOne/Bugcrowd ใช้ Cloudflare Turnstile บล็อก bot ทุกครั้ง

**วิธีแก้:** ใช้ freebuff AI ที่มี **browser-use capability** ควบคุม browser จริงๆ ไม่ใช่ automation tool

```bash
# freebuff ทำงานบน server 8lgm.segfault.net
# สามารถ:
# 1. Control real Chrome browser
# 2. Bypass Cloudflare detection
# 3. Submit forms อัตโนมัติ

freebuff "Login to HackerOne and submit CORS report for Stripe"
```

---

## 📋 Phase 1: หน่วยจู่โจม - Intelligence Gathering (Week 1-2)

### 1.1 Server Setup บน 8lgm.segfault.net
```bash
# SSH ไป server
ssh -o "SetEnv SECRET=JEpUOZPOVhCTwdhQInbJTtNA" root@8lgm.segfault.net

# เช็ค specs
uptime && free -h && df -h

# ติดตั้ง tools ที่จำเป็น
./tools/setup_lab.sh
```

### 1.2 GitHub Reconnaissance

**GitHub Token Authentication:**
```bash
export GITHUB_TOKEN="[REDACTED_TOKEN]"
```

**GitHub Recon Script:**
```bash
# วิเคราะห์ organization
python3 freebuff/github_recon.py --org github --limit 100

# วิเคราะห์ user
python3 freebuff/github_recon.py --user potsopotosolo

# ค้นหาด้วย dorks
python3 freebuff/github_recon.py --dorks "aws api key"

# ค้นหา code ที่เฉพาะเจาะจง
python3 freebuff/github_recon.py --search "org:github filename:.env"

# เช็ค rate limit
python3 freebuff/github_recon.py --check-limit
```

**GitHub Dorking Patterns:**
| Dork | ใช้หา |
|------|-------|
| `filename:.env api_key` | Leaked API keys |
| `extension:pem private` | Private keys |
| `extension:sql mysql` | SQL dumps with credentials |
| `filename:config password` | Config files with passwords |
| `org:target aws secret` | AWS credentials in target org |
| `language:python password` | Python files with passwords |

### 1.3 เครื่องมือ Lab

### 1.1 เครื่องมือ Lab Setup
```
sarahack/
├── tools/
│   ├── recon/           # Reconnaissance tools
│   │   ├── amass/       # Subdomain enumeration
│   │   ├── subfinder/   # Passive subdomain discovery
│   │   ├── nmap/        # Port scanning
│   │   └── ffuf/        # Web fuzzing
│   ├── web/             # Web testing tools
│   │   ├── burp/        # Burp Suite configs
│   │   ├── sqlmap/      # SQL injection
│   │   └── nuclei/      # Vulnerability scanner
│   ├── cloud/           # Cloud security tools
│   │   └── cloud_enum/  # Multi-cloud enumeration
│   └── mobile/          # Mobile testing
│       └── apktool/     # APK analysis
```

### 1.2 ติดตั้งเครื่องมือ
```bash
# Install all tools
./setup_lab.sh

# ติดตั้ง:
# - amass, subfinder, assetfinder
# - nmap, masscan
# - ffuf, dirb, gobuster
# - sqlmap, commix
# - nuclei, nucy
# - subjack, nuclei-templates
# - httpx, naabu
```

### 1.3 สร้าง Wordlists
- Bug Bounty wordlists
- Subdomain wordlists
- Parameter wordlists
- Payload wordlists

---

## 📋 Phase 2: Target Discovery (สัปดาห์ที่ 2-3)

### 2.1 แหล่งรวบรวม Targets ใหม่
```bash
# Automatic target discovery
./scripts/find_targets.sh

# แหล่งข้อมูล:
# - https://github.com/arkadiyt/bounty-targets-data
# - https://hunter.io
# - https://securitytrails.com
# - https://chaos.projectdiscovery.io
```

### 2.2 ติดตาม New Programs
```bash
# HackerOne new programs
# Bugcrowd new programs
# Intigriti new programs
# OpenBugBounty
```

---

## 📋 Phase 3: Vulnerability Research (สัปดาห์ที่ 3-4)

### 3.1 ศึกษาช่องโหว่ใหม่ๆ 2026
```bash
# Fetch latest CVEs
./scripts/fetch_cves.sh

# Sources:
# - cve.mitre.org
# - nvd.nist.gov
# - exploit-db.com
# - github.com/advisories
```

### 3.2 สร้าง Custom Exploits
```bash
# Nuclei templates สำหรับช่องโหว่ใหม่
./scripts/update_nuclei.sh

# Bug Bounty specific templates
nuclei -t custom-templates/ -l targets.txt
```

### 3.3 CORS Research
- หา CORS misconfiguration ใหม่ๆ
- สร้าง report template สำหรับ CORS
- Bypass techniques สำหรับ Cloudflare

---

## 📋 Phase 4: Report Generation (สัปดาห์ที่ 4-5)

### 4.1 ระบบสร้าง Report
```python
# Auto-generate report from findings
python3 tools/report_generator.py --type cors --target stripe
```

### 4.2 Report Templates
```
reports/
├── templates/
│   ├── cors_report.md
│   ├── ssrf_report.md
│   ├── idor_report.md
│   └── xss_report.md
├── drafts/
│   └── target_name_date.md
└── submitted/
    └── status_tracking.md
```

### 4.3 เพิ่มความรู้จาก Pentest Book
- อัพเดทเทคนิคใหม่ๆ จาก pentest-book.com
- บันทึกไว้ใน knowledge-base.md

---

## 📋 Phase 5: Auto-Submit System (สัปดาห์ที่ 5-6)

### 5.1 Freebuff AI Integration
```bash
# ใช้ freebuff สำหรับ browser automation
# สร้าง script ที่ใช้ freebuff ช่วย submit

freebuff "Submit this CORS report to HackerOne Stripe program"
freebuff "Bypass Cloudflare and login to Bugcrowd"
```

### 5.2 Browser Automation
```python
# Playwright/Selenium scripts
# ใช้ freebuff browser-use capability

# Workflow:
# 1. Login to platform via freebuff
# 2. Navigate to report form
# 3. Fill form automatically
# 4. Submit report
```

### 5.3 Manual Fallback
```bash
# เมื่อ auto-submit ล้มเหลว
# ใช้วิธี manual หรือ freebuff

# Commands:
./manual_submit.sh --platform hackerone --program stripe
```

---

## 📋 Phase 6: Tracking & Management (Ongoing)

### 6.1 Report Tracking System
```bash
# ติดตามสถานะ reports
python3 tools/tracker.py --list

# Dashboard:
# - Pending reports
# - Awaiting response
# - Rewarded/Resolved
# - Duplicate/Informative
```

### 6.2 Database
```yaml
# reports_database.yml
reports:
  - id: 1
    platform: hackerone
    program: stripe
    vulnerability: CORS
    severity: HIGH
    status: pending
    date_submitted: 2026-06-01
    last_updated: 2026-06-06
```

### 6.3 Notifications
```bash
# Discord notifications
# แจ้งเตือนเมื่อ:
# - Report ได้รับ response
# - ได้รับ reward
# - Status เปลี่ยน
```

---

## 🏗️ โครงสร้างโปรเจค (Final)

```
sarahack/
├── SARAhack.md           # Main documentation (this file)
├── REOPLAN.md            # แผนการพัฒนา
├── pentest-book.md       # ความรู้จาก Pentest Book
├── README.md             # Project overview
│
├── tools/                # เครื่องมือทั้งหมด
│   ├── setup_lab.sh      # ติดตั้ง lab
│   ├── recon/            # Reconnaissance
│   ├── web/              # Web testing
│   ├── cloud/            # Cloud security
│   └── tracker.py        # Report tracker
│
├── scripts/              # Scripts อัตโนมัติ
│   ├── find_targets.sh   # หา targets ใหม่
│   ├── fetch_cves.sh     # Fetch CVEs
│   ├── auto_submit.py    # Auto-submit reports
│   └── manual_submit.sh  # Manual fallback
│
├── reports/              # Reports ทั้งหมด
│   ├── templates/        # Report templates
│   ├── drafts/           # Draft reports
│   ├── submitted/        # ส่งแล้ว
│   └── tracking/         # ติดตามสถานะ
│
├── config/               # Configuration
│   ├── credentials/      # เก็บ credentials (gitignore)
│   ├── platforms.yml     # Platform configs
│   └── programs.yml      # Bug bounty programs
│
├── knowledge/            # ฐานความรู้
│   ├── vulnerabilities/  # ข้อมูลช่องโหว่
│   ├── techniques/       # เทคนิคการโจมตี
│   └── poc/              # Proof of concepts
│
└── freebuff/             # freebuff AI integration
    ├── sarahack_freebuff.sh
    └── freebuff_bounty.py
```

---

## 🧠 Freebuff Browser Automation Strategy

### วิธีใช้ freebuff สำหรับ Bypass Cloudflare:

**Step 1: เริ่ม session บน server**
```bash
ssh -o "SetEnv SECRET=JEpUOZPOVhCTwdhQInbJTtNA" root@8lgm.segfault.net
freebuff login
```

**Step 2: สั่งงาน freebuff**
```
freebuff "Use browser to:
1. Open https://hackerone.com/stripe/reports/new
2. Login with Potosopotosolo@gmail.com
3. Fill form with CORS vulnerability report
4. Submit the report"
```

**Step 3: Monitor ผลลัพธ์**
```bash
# freebuff จะควบคุม browser จริงๆ
# ไม่ถูก detect เพราะเป็น real browser session
```

### ข้อดีของ freebuff:
- ✅ ใช้ real Chrome browser (ไม่ใช่ automation)
- ✅ หลบ Cloudflare Turnstile ได้
- ✅ ฟรี ไม่ต้องเสียเงิน
- ✅ มี web research ในตัว

### ข้อจำกัด:
- ⚠️ ต้อง SSH ไป server ทุกครั้ง
- ⚠️ ต้องพิมพ์ password เอง (segfault)
- ⚠️ Session อาจหมดอายุ

---

## ⚠️ Risk Assessment & Contingency

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| freebuff unavailable | MEDIUM | HIGH | ใช้ manual submission |
| Server down | LOW | HIGH | ใช้ local environment |
| Cloudflare detect | HIGH | MEDIUM | ใช้ freebuff real browser |
| Report duplicate | MEDIUM | LOW | ตรวจสอบก่อน submit |
| Credentials leak | LOW | CRITICAL | เก็บใน .env ที่ encrypt |

---

## 📅 Timeline (Realistic)

```
sarahack/
├── SARAhack.md           # Main documentation
├── REOPLAN.md            # แผนการพัฒนา
├── pentest-book.md       # ความรู้จาก Pentest Book
├── README.md             # Project overview
│
├── tools/                # เครื่องมือทั้งหมด
│   ├── setup_lab.sh      # ติดตั้ง lab
│   ├── recon/            # Reconnaissance
│   ├── web/              # Web testing
│   ├── cloud/            # Cloud security
│   └── tracker.py        # Report tracker
│
├── scripts/              # Scripts อัตโนมัติ
│   ├── find_targets.sh   # หา targets ใหม่
│   ├── fetch_cves.sh     # Fetch CVEs
│   ├── auto_submit.py    # Auto-submit reports
│   └── manual_submit.sh  # Manual fallback
│
├── reports/              # Reports ทั้งหมด
│   ├── templates/        # Report templates
│   ├── drafts/           # Draft reports
│   ├── submitted/        # ส่งแล้ว
│   └── tracking/         # ติดตามสถานะ
│
├── config/               # Configuration
│   ├── credentials/      # เก็บ credentials (gitignore)
│   ├── platforms.yml     # Platform configs
│   └── programs.yml      # Bug bounty programs
│
├── knowledge/            # ฐานความรู้
│   ├── vulnerabilities/  # ข้อมูลช่องโหว่
│   ├── techniques/       # เทคนิคการโจมตี
│   └── poc/              # Proof of concepts
│
└── freebuff/             # freebuff AI integration
    ├── sarahack_freebuff.sh
    └── freebuff_bounty.py
```

---

## 📅 Timeline (Realistic)

| Week | Phase | Tasks | Deliverable |
|------|-------|-------|-------------|
| 1 | Phase 1 | Setup lab, install tools | Working environment |
| 2 | Phase 2 | Target discovery | 50+ programs in scope |
| 3-4 | Phase 3 | Vulnerability research | New CVE reports ready |
| 4-5 | Phase 4 | Report generation | 10+ draft reports |
| 5-6 | Phase 5 | Freebuff integration | Auto-submit working |
| Ongoing | Phase 6 | Tracking & rewards | Database of all reports |

---

## 🎯 Success Metrics

- [ ] ติดตั้ง tools ครบบน 8lgm.segfault.net
- [ ] หา targets ใหม่ 50+ programs
- [ ] Submit reports 20+ / สัปดาห์
- [ ] สร้าง report ใหม่ๆ จาก CVE ใหม่
- [ ] ติดตาม reports ทั้งหมดได้
- [ ] ได้รับ reward 5+ reports

---

## 🚨 Priority Tasks (Immediate)

1. **ติดตั้ง Lab** - `chmod +x tools/setup_lab.sh && ./tools/setup_lab.sh`
2. **ศึกษา Pentest Book** - ดึงเทคนิคใหม่ๆ เพิ่มลงใน knowledge/
3. **อัพเดท SARAhack.md** - โครงสร้างใหม่ตามแผนนี้
4. **สร้าง Report Templates** - สำหรับ CORS, SSRF, IDOR
5. **เชื่อมต่อ freebuff** - ทดสอบ browser automation

---

## 💡 Next Steps

1. **Phase 1 เริ่มเลย** - SSH ไป server แล้วรัน setup_lab.sh
2. **ดึงข้อมูลจาก Pentest Book** - เพิ่มลงใน knowledge/vulnerabilities/
3. **หา targets ใหม่** - รัน `./scripts/find_targets.sh`
4. **สร้าง auto-submit script** - ใช้ freebuff ช่วย
5. **Track reports** - ใช้ `tools/tracker.py`

---

**หมายเหตุ:** ทุก phase สามารถทำขนานกันได้ เมื่อ team capacity พร้อม