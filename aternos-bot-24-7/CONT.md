# CONT.md - คู่มือการตั้งค่าและกู้คืนโปรเจค

> ⚠️ **WARNING: คู่มือนี้มี Credentials อยู่ - ห้าม commit ขึ้น git!**
> หลังจากตั้งค่าเสร็จ ให้เก็บไฟล์นี้ไว้ในที่ปลอดภัย หรือใช้ `.gitignore`

## 🎯 ภาพรวม

CONT.md เอาไว้ใช้สำหรับ **เริ่มต้นโปรเจคใหม่บนเครื่องอื่น** หรือ **กู้คืนเมื่อไฟดับ** โดยมีทุกอย่างที่ต้องรู้รวมอยู่ที่นี่:

- 🔐 Credentials และ API Keys
- 🔧 วิธีติดตั้ง Dependencies
- 🤖 Tools ที่ใช้ (freebuff, OpenClaw, SARAhack)
- 📋 Workflows การทำงาน
- 🛠️ Scripts สำคัญ
- ⚡ วิธีแก้ปัญหาเบื้องต้น

---

## 🔐 Credentials (สำคัญมาก!)

### HackerOne Account
```
Email: YOUR_H1_EMAIL@gmail.com
Password: YOUR_H1_PASSWORD
API Identifier: YOUR_H1_API_IDENTIFIER@gmail.com
API Token: (ต้องไปสร้างที่ https://hackerone.com/settings/api_credentials)
```

### Discord Webhook (HOOKtoME)
```
URL: https://discord.com/api/webhooks/YOUR_DISCORD_WEBHOOK_ID/YOUR_DISCORD_WEBHOOK_TOKEN
```

### Telegram Bot
```
Bot Name: @YOUR_BOT_NAME_bot_bot
Token: YOUR_TELEGRAM_BOT_TOKEN
```

### tmate Session (สำหรับ freebuff remote)
```
Host: lon1.tmate.io
User: YOUR_TMATE_USER
```

### PostHog API Key (Codebuff/freebuff)
```
Key: YOUR_POSTHOG_API_KEY
```

---

## 🔧 การติดตั้ง Dependencies (ครั้งแรกบนเครื่องใหม่)

### 1. Node.js 22 (Required for OpenClaw)
```bash
# ถ้าใช้ nvm
nvm install 22
nvm use 22

# หรือใช้ nix store (ใน Replit)
export PATH="/nix/store/s97a21afj6aw098a25gs3j7ias7wzanm-nodejs-22.22.0-wrapped/bin:$PATH"
```

### 2. Python Dependencies
```bash
cd /home/runner/workspace
./tools/install_python_deps.sh
```

### 3. Node Packages (npm global)
```bash
npm install -g openclaw@latest --ignore-scripts
npm install -g freebuff
```

---

## 🤖 Tools ที่ใช้

### 1. freebuff (v0.0.103+)
**AI Coding Agent** - ใช้สำหรับ browser automation และ bug bounty tasks

```bash
# ติดตั้ง
npm install -g freebuff

# ใช้งาน
freebuff "submit CORS report for Stripe to HackerOne"

# Login
freebuff login
```

**Path:** `/home/runner/workspace/.config/npm/node_global/bin/freebuff`

---

### 2. OpenClaw (v2026.6.1+)
**Autonomous AI Agent Framework** - ใช้สำหรับ orchestration และ automation

```bash
# ติดตั้ง
npm install -g openclaw@latest --ignore-scripts

# Wrapper script (ใช้ Node 22)
cat > /home/runner/workspace/openclaw.sh << 'EOF'
#!/bin/bash
export PATH="/nix/store/s97a21afj6aw098a25gs3j7ias7wzanm-nodejs-22.22.0-wrapped/bin:$PATH"
exec /nix/store/s97a21afj6aw098a25gs3j7ias7wzanm-nodejs-22.22.0-wrapped/bin/node /home/runner/workspace/.config/npm/node_global/lib/node_modules/openclaw/dist/index.js "$@"
EOF
chmod +x /home/runner/workspace/openclaw.sh

# Version check
/home/runner/workspace/openclaw.sh --version
```

**Config Location:** `/home/runner/.openclaw/openclaw.json`

---

### 3. SARAhack
**Bug Bounty Auto-Submit System** - workflow สำหรับ scanning และ submitting

**อ่านเพิ่มเติม:** `SARAhack.md`

---

## 📁 โครงสร้างโปรเจค

```
/home/runner/workspace/
├── CONT.md                    # เอกสารนี้ (คู่มือตั้งค่าใหม่)
├── SARAhack.md                # Bug Bounty Auto-Submit System
├── REOPLAN.md                 # แผนการพัฒนา
├── HOOKtoME.json              # Credentials file
│
├── freebuff/                  # freebuff AI tools
│   ├── mass_scanner.js        # Scanner หา vulnerabilities
│   ├── send_to_discord_with_link.sh  # อัพโหลด + ส่ง Discord
│   ├── discord_report_sender.sh      # ส่ง Discord อย่างเดียว
│   ├── hackerone_api_submitter.py    # Submit ผ่าน API
│   ├── freebuff_bounty.py     # Bounty automation
│   ├── freebuff_interactive.py
│   ├── tokenlogin.env         # Credentials (gitignore!)
│   └── programs_400plus.py    # รายชื่อ 400+ programs
│
├── reports/                   # Reports ทั้งหมด
│   ├── VERIFIED_*.md          # Reports ที่ยืนยันแล้ว (curl จริง)
│   ├── new_*.md               # Reports ที่สร้างจาก scanner
│   ├── templates/             # Report templates
│   └── tracking/
│       └── reports.json       # Tracker สถานะ reports
│
├── tools/
│   ├── setup_lab.sh           # ติดตั้ง lab tools
│   ├── install_python_deps.sh # ติดตั้ง Python dependencies
│   ├── install_tools.sh
│   ├── ssh_auto.sh
│   └── tracker.py
│
├── scripts/
│   ├── find_targets.sh        # หา targets ใหม่
│   ├── fetch_cves.sh          # Fetch CVEs
│   ├── auto_submit.py
│   └── manual_submit.sh
│
├── .openclaw/                 # OpenClaw config
│   ├── openclaw.json
│   ├── agents/main/skills/
│   │   └── auto-hunter/       # Auto-hunter skill
│   │       ├── SKILL.md
│   │       ├── scan.sh
│   │       └── submit.sh
│   └── plugin-skills/
│
└── .config/
    ├── npm/node_global/bin/   # Global npm binaries
    └── docker/
```

---

## 📋 Workflows การทำงาน

### Workflow 1: SARAhack (Manual Scanning)

```bash
# 1. สแกน programs หา vulnerabilities
node freebuff/mass_scanner.js --limit=100 --verbose

# 2. ตรวจสอบด้วย curl
curl -s -X OPTIONS 'https://api.stripe.com/v1/customers' -H 'Origin: https://evil-test.com' -H 'Access-Control-Request-Method: GET' -i | grep -E 'access-control|HTTP'

# 3. สร้าง VERIFIED report ถ้าผ่าน

# 4. อัพโหลด + ส่ง Discord
./freebuff/send_to_discord_with_link.sh --all

# 5. ไปกดลิงค์ใน Discord → Submit ที่ HackerOne
```

### Workflow 2: freebuff (Interactive AI)

```bash
# 1. SSH ไป tmate session
ssh eS6fytCGPu74pDmMNxAKcszLc@lon1.tmate.io

# 2. รอ 30 วินาที แล้วตั้งค่า
export CODEBUFF_POSTHOG_API_KEY='be0e3e50-e07c-434d-98d0-85d6c59d615c'
freebuff

# 3. ถาม freebuff
freebuff "Submit Stripe CORS report to HackerOne"
freebuff "Find new CORS vulnerabilities in 50 programs"
```

### Workflow 3: OpenClaw (Autonomous Agent)

```bash
# 1. ตั้งค่า AI Provider (ต้องมี API key)
export OPENROUTER_API_KEY="sk-or-v1-..."
/home/runner/workspace/openclaw.sh config set models.provider openrouter

# 2. Start gateway
/home/runner/workspace/openclaw.sh gateway

# 3. ทดสอบ autonomous
/home/runner/workspace/openclaw.sh agent --message "scan 10 programs for bugs"

# 4. ส่ง message ผ่าน Telegram
/home/runner/workspace/openclaw.sh message send --channel telegram --target @Gagagaga888_bot_bot --message "Scan complete!"
```

### Workflow 4: API Submit (Automatic)

```bash
# 1. ตั้งค่า credentials
export H1_API_IDENTIFIER="nonoto999t@gmail.com"
export H1_API_TOKEN="your_api_token_here"

# 2. ดู reports ที่รอ
python3 freebuff/hackerone_api_submitter.py --list

# 3. Submit report
python3 freebuff/hackerone_api_submitter.py --report 2

# 4. Submit ทั้งหมด
python3 freebuff/hackerone_api_submitter.py --all
```

---

## 🛠️ Scripts สำคัญ

### freebuff/mass_scanner.js
สแกน programs หา vulnerabilities (CORS, SSRF, IDOR)
```bash
node freebuff/mass_scanner.js --limit=100 --verbose
node freebuff/mass_scanner.js --program=stripe
```

### freebuff/remote_scan.sh
SSH ไป segfault.net แล้ว scan บน remote Kali (ไม่หนักเครื่องเรา)
```bash
# ตรวจสอบ remote Kali
./freebuff/remote_scan.sh status

# สแกน program
./freebuff/remote_scan.sh scan stripe --limit 50 --verbose

# รัน nmap/masscan บน remote
./freebuff/remote_scan.sh nmap api.stripe.com -p 1-1000
./freebuff/remote_scan.sh masscan 1.2.3.0/24 -p80,443

# ทดสอบ CORS ด้วย curl บน remote
./freebuff/remote_scan.sh curl-test https://api.stripe.com

# ⚠️ สำคัญ: หลัง scan เสร็จต้อง clean up!
./freebuff/remote_scan.sh clean
```

**SSH Credentials:**
- Server: root@8lgm.segfault.net
- Password: segfault
- SECRET: NhjQPlbFLARQXwmSPVNeAJgz

### freebuff/remote_scan.sh
SSH ไป segfault.net แล้ว scan บน remote Kali (ไม่หนักเครื่องเรา)
```bash
# ตรวจสอบ remote Kali
./freebuff/remote_scan.sh status

# สแกน program
./freebuff/remote_scan.sh scan stripe --limit 50 --verbose

# รัน nmap/masscan บน remote
./freebuff/remote_scan.sh nmap api.stripe.com -p 1-1000
./freebuff/remote_scan.sh masscan 1.2.3.0/24 -p80,443

# ทดสอบ CORS ด้วย curl บน remote
./freebuff/remote_scan.sh curl-test https://api.stripe.com

# ⚠️ สำคัญ: หลัง scan เสร็จต้อง clean up!
./freebuff/remote_scan.sh clean
```

**SSH Credentials:**
- Server: root@8lgm.segfault.net
- Password: segfault
- SECRET: NhjQPlbFLARQXwmSPVNeAJgz

### freebuff/send_to_discord_with_link.sh
อัพโหลด report ไป tmpfiles.org แล้วส่ง Discord
```bash
./freebuff/send_to_discord_with_link.sh --all      # ทั้งหมด
./freebuff/send_to_discord_with_link.sh --id 24    # เฉพาะ ID
./freebuff/send_to_discord_with_link.sh --list     # ดูรายการ
```

### freebuff/discord_report_sender.sh
ส่ง Discord อย่างเดียว (ไม่อัพโหลด)
```bash
./freebuff/discord_report_sender.sh --all
./freebuff/discord_report_sender.sh --list
./freebuff/discord_report_sender.sh --id 24
```

### freebuff/hackerone_api_submitter.py
Submit reports ผ่าน HackerOne API
```bash
export H1_API_IDENTIFIER="nonoto999t@gmail.com"
export H1_API_TOKEN="your_token"
python3 freebuff/hackerone_api_submitter.py --list
python3 freebuff/hackerone_api_submitter.py --report 2
python3 freebuff/hackerone_api_submitter.py --all
```

---

## 🔐 OpenClaw Configuration

### Channels Setup
```bash
# Telegram
/home/runner/workspace/openclaw.sh channels add --channel telegram --token 8989539373:AAFFdmlnoUK7lVmzXNWeUu1YM4eMC-ZT3_Q --name Gagagaga888

# Discord
/home/runner/workspace/openclaw.sh channels add --channel discord --token https://discord.com/api/webhooks/1512524218871447592/ufbSsNL_4ebXM8EMQlRyEunKg6EH_SIKVo7ulw8olRygPtgda1R4-Gji56dYt9fZR_Fe --name HOOKtoME
```

### Gateway Configuration
```bash
/home/runner/workspace/openclaw.sh config set gateway.mode local
/home/runner/workspace/openclaw.sh config set commands.ownerAllowFrom '["*"]'
```

### Check Status
```bash
/home/runner/workspace/openclaw.sh channels list
/home/runner/workspace/openclaw.sh status
/home/runner/workspace/openclaw.sh doctor
```

---

## ⚡ วิธีแก้ปัญหาเบื้องต้น

### 1. Node.js Version Error
```
Error: Node.js v22.19+ is required (current: v16.13.1)
```
**วิธีแก้:**
```bash
# ใช้ wrapper script
/home/runner/workspace/openclaw.sh --version

# หรือ upgrade Node
nvm install 22 && nvm use 22
```

### 2. OpenClaw Gateway Not Running
```
Gateway at ws://127.0.0.1:18789 is unreachable
```
**วิธีแก้:**
```bash
/home/runner/workspace/openclaw.sh gateway install
/home/runner/workspace/openclaw.sh gateway start
```

### 3. H1_API_TOKEN Empty
```
Error: H1_API_TOKEN not set
```
**วิธีแก้:**
```bash
# ไปสร้าง API key ที่ https://hackerone.com/settings/api_credentials
export H1_API_IDENTIFIER="nonoto999t@gmail.com"
export H1_API_TOKEN="your_api_token_here"
```

### 4. Discord Webhook Fail
```bash
# ทดสอบ webhook
curl -X POST "https://discord.com/api/webhooks/1512524218871447592/ufbSsNL_4ebXM8EMQlRyEunKg6EH_SIKVo7ulw8olRygPtgda1R4-Gji56dYt9fZR_Fe" -d "content=Test"
```

### 5. freebuff Not Found
```bash
# ติดตั้งใหม่
npm install -g freebuff

# ตรวจสอบ path
which freebuff
/home/runner/workspace/.config/npm/node_global/bin/freebuff --version
```

---

## 🚀 Quick Start (เริ่มใช้งานเร็ว)

### ครั้งแรก: ติดตั้งทุกอย่าง
```bash
cd /home/runner/workspace

# 1. ติดตั้ง Python deps
./tools/install_python_deps.sh

# 2. ติดตั้ง Node packages
npm install -g openclaw@latest --ignore-scripts
npm install -g freebuff

# 3. สร้าง wrapper script
cat > openclaw.sh << 'EOF'
#!/bin/bash
export PATH="/nix/store/s97a21afj6aw098a25gs3j7ias7wzanm-nodejs-22.22.0-wrapped/bin:$PATH"
exec /nix/store/s97a21afj6aw098a25gs3j7ias7wzanm-nodejs-22.22.0-wrapped/bin/node /home/runner/workspace/.config/npm/node_global/lib/node_modules/openclaw/dist/index.js "$@"
EOF
chmod +x openclaw.sh

# 4. ตั้งค่า channels
./openclaw.sh channels add --channel telegram --token 8989539373:AAFFdmlnoUK7lVmzXNWeUu1YM4eMC-ZT3_Q --name Gagagaga888
./openclaw.sh channels add --channel discord --token https://discord.com/api/webhooks/1512524218871447592/ufbSsNL_4ebXM8EMQlRyEunKg6EH_SIKVo7ulw8olRygPtgda1R4-Gji56dYt9fZR_Fe --name HOOKtoME
```

### ทุกครั้ง: เริ่มทำงาน
```bash
# 1. สแกน vulnerabilities
node freebuff/mass_scanner.js --limit=50 --verbose

# 2. ตรวจสอบ report ด้วย curl

# 3. อัพโหลด + ส่ง Discord
./freebuff/send_to_discord_with_link.sh --all

# 4. Submit ด้วยตัวเองผ่านลิงค์ใน Discord
```

---

## 📊 Report Status Tracking

```bash
# ดูสถานะ reports ทั้งหมด
cat reports/tracking/reports.json | node -e "
const fs = require('fs');
const data = JSON.parse(fs.readFileSync('/dev/stdin','utf8'));
const counts = {pending:0, verified:0, submitted:0};
data.forEach(r => { if(counts[r.status]!==undefined) counts[r.status]++; });
console.log('Reports:', JSON.stringify(counts, null, 2));
"

# สถานะที่เป็นไปได้:
# - pending: รอส่ง
# - verified: ยืนยันแล้วด้วย curl
# - submitted: ส่งไป HackerOne แล้ว
# - closed_duplicate, closed_no_target, etc.
```

---

## 🎯 Severity Rules (CORS Testing)

| ผลลัพธ์ | Severity | สถานะ |
|---------|----------|--------|
| `allow-origin: arbitrary` + `credentials: true` | **HIGH** | ✅ Vulnerable |
| `allow-origin: arbitrary` + ไม่มี `credentials` | **MEDIUM** | ✅ Vulnerable |
| `allow-origin: *` (wildcard) | - | ❌ Not Vulnerable |
| HTTP Error / 404 / 500 | - | ❌ Not Vulnerable |

---

## 🔑 API Keys ที่ต้องมี

| Service | Key Type | หาที่ไหน |
|---------|----------|----------|
| HackerOne | API Token | https://hackerone.com/settings/api_credentials |
| OpenRouter | API Key | https://openrouter.ai/keys (free tier available) |
| Claude/OpenAI | API Key | ตาม provider ที่ใช้ |

---

## 📝 Notes สำคัญ

1. **tmpfiles.org** รองรับแค่ .txt เท่านั้น - script จะแปลง .md → .txt อัตโนมัติ
2. **ทุก report ต้องผ่าน curl verification** ก่อนส่ง
3. **Discord links ต้องเป็น format `[text](url)`** ใน description ถึงจะ clickable
4. **freebuff ต้อง SSH ไป tmate** ถึงจะทำงานได้
5. **OpenClaw ต้องการ Node 22+** ถึงจะรันได้

---

## 🔄 Recovery Checklist (กู้คืนเมื่อไฟดับ)

- [ ] Clone repo: `git clone <your-repo-url>`
- [ ] ติดตั้ง Node.js 22+ (ใช้ nvm หรือ download จาก nodejs.org)
- [ ] ติดตั้ง Python dependencies: `./tools/install_python_deps.sh`
- [ ] ติดตั้ง npm packages: `npm install -g openclaw@latest --ignore-scripts freebuff`
- [ ] Restore `freebuff/tokenlogin.env` จาก backup
- [ ] ตั้งค่า environment variables:
  ```bash
  export H1_API_IDENTIFIER="YOUR_H1_API_IDENTIFIER"
  export H1_API_TOKEN="YOUR_H1_API_TOKEN"
  export CODEBUFF_POSTHOG_API_KEY='YOUR_POSTHOG_KEY'
  ```
- [ ] Restore reports จาก backup:
  ```bash
  # Backup ทุกครั้งก่อนไฟดับ
  tar -czf reports-backup.tar.gz reports/
  # Restore
  tar -xzf reports-backup.tar.gz
  ```
- [ ] Restore OpenClaw config จาก backup: `/home/runner/.openclaw/`
- [ ] Run `openclaw.sh doctor --fix`

---

### Backup ที่ต้องทำเป็นประจำ:
```bash
# 1. Reports และ tracking
tar -czf reports-backup.tar.gz reports/

# 2. OpenClaw config
tar -czf openclaw-backup.tar.gz ~/.openclaw/

# 3. Credentials (เก็บไว้ในที่ปลอดภัย)
cp freebuff/tokenlogin.env ~/secure-backup/
```

### ไฟล์ที่ควร .gitignore:
```
freebuff/tokenlogin.env
CONT.md
.openclaw/
reports/tracking/reports.json
*.backup
*.tar.gz
```

---

*Last Updated: 2026-06-07 03:00 UTC*
*CONT.md v1.0 - Setup & Recovery Guide*