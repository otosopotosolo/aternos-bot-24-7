# 🏴‍☠️ SARAhack Bug Bounty Hunting Guide
## ตั้งแต่มือใหม่ → โปร (Easy → Hard → $$$)

---

## 🎯 Overview

ระบบ Bug Bounty Hunting แบบลำดับขั้น:
- **Level 1 (Easy):** $50-$500 - หาได้เลยไม่ต้องมีประสบการณ์
- **Level 2 (Medium):** $500-$5,000 - ต้องมีความรู้พื้นฐาน
- **Level 3 (Hard):** $5,000-$100,000+ - ต้องมีความเชี่ยวชาญ

---

## 🚀 Level 1: เริ่มต้นง่าย (Easy Wins)

### 🎯 เป้าหมาย: Public Programs, Low-Hanging Fruit

**Bug Types ที่หาได้ง่าย:**
1. **CORS Misconfiguration** - หาได้ใน 5 นาที
2. **Open Redirect** - ง่ายมาก
3. **Information Disclosure** - ดูยังไม่เห็นก็หาได้เลย
4. **Broken Link Hijacking** - ง่ายๆ
5. **SPF/DKIM/DMARC Issues** - Email security

### 🔍Recon แบบเร็ว

```bash
# หา CORS ด้วย python3
python3 freebuff/github_recon.py --dorks "Access-Control-Allow-Origin"

# หา open redirect
ffuf -w wordlists/seclists/Discovery/Web-Content/quick-testing-list.txt -u "https://target.com/FUZZhttps://google.com"

# หา exposed .git
gobuster dir -u https://target.com -w wordlists/seclists/Discovery/Web-Content/quick-testing-list.txt -x .git,.git/config

# หา exposed configs
gobuster dir -u https://target.com -w wordlists/seclists/Discovery/Web-Content/quick-testing-list.txt -x .env,.env.local,config.php,settings.py
```

### 🎯 Target Programs (ง่ายที่สุด)

| Program | Platform | เหตุผลที่ง่าย |
|---------|----------|-------------|
| **GitHub** | HackerOne | Public repos เยอะมาก |
| **Private Programs** ที่ไม่ค่อยมีคนเล่น | HackerOne/Bugcrowd | หาได้ง่ายกว่า |
| **VDP (Disclosure)** | หลาย Platform | ไม่มีจำกัดเวลา |

### 📝 วิธีเลือกโปรที่ดี (Easy Target)

| เกณฑ์ | ทำไมดี |
|-------|--------|
| **จำนวน researchers น้อย** | โอกาส duplicate ต่ำ |
| **Scope กว้าง** | มีพื้นที่หาเยอะกว่า |
| **Bounty range สูง** | คุ้มค่าเวลามากกว่า |
| **ไม่ค่อยมีคนเล่น** | ยังมี low-hanging fruit |

### 📝 Report Template (CORS)

```markdown
# CORS Misconfiguration Report

## Summary
พบ CORS misconfiguration บน target.com ที่อนุญาต cross-origin requests จากทุก domain

## Steps to Reproduce
1. ไปที่ https://target.com/api/user
2. ส่ง request พร้อม Origin: https://evil.com
3. Response มี Access-Control-Allow-Origin: *

## Impact
- ขโมยข้อมูล users ที่ login อยู่
- ดู private information
- ใช้เป็น proxy หา internal systems

## Remediation
- กำหนด Origin ที่อนุญาตเฉพาะ
- ใช้ Access-Control-Allow-Credentials: true เฉพาะเมื่อจำเป็น
```

---

## 🔥 Level 2: ระดับกลาง (Medium)

### 🎯 เป้าหมาย: Auth Vulnerabilities, Business Logic

**Bug Types ที่ต้องมีความรู้:**
1. **IDOR** - ดูของคนอื่นได้
2. **SSRF** - เข้าถึง internal systems
3. **Race Condition** - ทำ transaction พร้อมกันได้เงิน
4. **GraphQL Issues** - Introspection, IDOR in queries
5. **JWT Issues** - Algorithm confusion, none alg

### 🔍Recon แบบละเอียด

```bash
# Subdomain enumeration
amass enum -passive -d target.com -o subdomains.txt
subfinder -d target.com -o subdomains.txt
assetfinder target.com | tee subdomains.txt

# ตรวจสอบ subdomains
cat subdomains.txt | httpx -title -tech-detect -silent | tee alive.txt

# หา IDOR
# 1. ดู request/response ของ user A
# 2. เปลี่ยน user ID เป็น user B
# 3. ถ้าได้ข้อมูล = IDOR

# หา SSRF
ffuf -w wordlists/seclists/Discovery/Web-Content/burp-param-names.txt -u "https://target.com/api/fetch?url=FUZZ" -mr "localhost" -s

# หา GraphQL
# 1. ไปที่ /graphql หรือ /api/graphql
# 2. ส่ง {__schema{types{name}}}
# 3. หา sensitive queries
```

### 🎯 Target Programs (Medium)

| Program | Platform | ประเภท |
|---------|----------|--------|
| **Shopify** | HackerOne | E-commerce, APIs |
| **Coinbase** | HackerOne | Crypto, High bounty |
| **Uber** | HackerOne | Transport, Many features |

### 📝 Report Template (IDOR)

```markdown
# IDOR Report - User Profile Access

## Summary
พบ IDOR บน /api/profile/{id} ที่สามารถดู profile ของ users อื่นได้โดยไม่ต้อง authorized

## Steps to Reproduce
1. Login ในชื่อ user A
2. ไปที่ /api/profile/12345 (12345 = user B's ID)
3. ได้รับ user B's private data

## Impact
- เข้าถึง private information ของ users ทั้งหมด
- ใช้ในการ scale attacks

## Evidence
[Attach screenshots และ Burp request/response]
```

---

## 💎 Level 3: ระดับสูง (Hard - High Bounty)

### 🎯 เป้าหมาย: Critical Infrastructure, 0-day

**Bug Types ที่ต้องเชี่ยวชาญ:**
1. **Remote Code Execution (RCE)** - Command injection, Deserialization
2. **Authentication Bypass** - OAuth, SAML, MFA bypass
3. **SQL Injection** - Blind, Time-based, Union
4. **Server-Side XSS** - Stored XSS, PDF generation
5. **Insecure Deserialization** - Java, Python, PHP

### 🔍Advanced Recon

```bash
# Nmap full scan
nmap -sV -sC -p- target.com -oN full_scan.txt

# หา vulnerabilities ด้วย nuclei
nuclei -l alive.txt -t ~/nuclei-templates/ -o nuclei_results.txt

# หา SQL injection
sqlmap -r request.txt --batch --level=5 --risk=3

# หา XSS (Stored)
# 1. หา input fields ที่ถูกเก็บและแสดงผล
# 2. ลอง <script>alert(1)</script>
# 3. ตรวจสอบทุก endpoints

# หา SSRF ขั้นสูง
# Target: https://target.com/api/pdf?url=http://169.254.169.254/latest/meta-data/
```

### 🎯 Target Programs (Hard - ได้เงินเยอะ)

| Program | Platform | Bounty Range |
|---------|----------|--------------|
| **Stripe** | HackerOne | $1,000-$50,000 |
| **Google** | VRP | $100-$$100,000+ |
| **Apple** | VRP | $$$$-$$$$$ |
| **Microsoft** | VRP | $500-$250,000 |

### 📝 Report Template (RCE)

```markdown
# Remote Code Execution Report

## Summary
พบ RCE บน target.com ผ่าน command injection ใน parameter q

## Steps to Reproduce
1. ไปที่ https://target.com/search
2. กรอก: `; cat /etc/passwd`
3. System executes command

## Impact
- Full server compromise
- Access to sensitive data
- Pivot to internal systems

## Proof of Concept
[Include command output, screenshot]
```

---

## 🛠️ Kali Tools Setup

### ติดตั้งเครื่องมือทั้งหมด

```bash
# Reconnaissance
sudo apt-get install -y amass nmap masscan

# Web Testing
sudo apt-get install -y sqlmap nikto dirb

# Password Attacks
sudo apt-get install -y hydra john hashcat

# Exploitation
sudo apt-get install -y metasploit-framework

# Misc
sudo apt-get install -y curl wget git jq
```

### คำสั่งใช้งานเครื่องมือ

#### Burp Suite (Web Testing) - สำคัญที่สุด!
```bash
# ติดตั้ง (ต้องมี Java)
sudo apt-get install -y burpsuite

# หรือดาวน์โหลดจาก portswigger.com
# ตั้งค่า Proxy ใน browser
# จับ requests และวิเคราะห์

# วิธี export request สำหรับ sqlmap:
# 1. คลิกขวาที่ request ใน Proxy tab
# 2. เลือก "Copy as cURL"
# 3. ใช้ sqlmap --curl"..." หรือ
# 4. หรือ คลิกขวา → "Save item" แล้วใช้ sqlmap -r request.txt
```

#### Nmap (Port Scanning)
```bash
# Quick scan
nmap -sV target.com

# Full port scan
nmap -sV -sC -p- -T4 target.com -oN scan.txt

# UDP scan
nmap -sU target.com -oN udp_scan.txt

# Aggressive scan with scripts
nmap -sV -sC --script=vuln target.com
```

#### SQLMap (SQL Injection)
```bash
# Basic test
sqlmap -u "https://target.com/?id=1" --batch

# Advanced with POST data
sqlmap -u "https://target.com/search" --data="q=test" --batch

# Full database dump
sqlmap -u "https://target.com/?id=1" --batch --dump
```

#### FFUF (Web Fuzzing)
```bash
# Directory fuzzing
ffuf -w wordlist.txt -u "https://target.com/FUZZ"

# Parameter fuzzing
ffuf -w params.txt -u "https://target.com/api?q=FUZZ"

# Subdomain enumeration
ffuf -w subdomains.txt -u "https://FUZZ.target.com"
```

#### Nuclei (Vulnerability Scanner)
```bash
# Scan with templates
nuclei -u https://target.com -t nuclei-templates/

# Scan list of URLs
nuclei -l urls.txt -t nuclei-templates/

# Custom template
nuclei -u https://target.com -t custom-templates/
```

---

## 📊 Bug Bounty Workflow

### 1. หาเป้าหมาย
```bash
# ดู programs ใหม่ๆ
python3 scripts/find_targets.sh

# หา public programs
curl -s "https://raw.githubusercontent.com/arkadiyt/bounty-targets-data/master/data/programs_hackerone.json" | jq '.[] | select(.name) | {name, platform}'
```

### 2. Recon
```bash
# Subdomain enumeration
amass enum -passive -d target.com -o subdomains.txt
subfinder -d target.com -o subdomains.txt

# ตรวจสอบ alive
cat subdomains.txt | httpx -silent | tee alive.txt

# Technology detection
cat alive.txt | httpx -tech-detect
```

### 3. วิเคราะห์
```bash
# ดูทุก endpoints
ffuf -w wordlists/seclists/Discovery/Web-Content/raft-large-words.txt -u "https://target/FUZZ" -mc 200,204,301,302,307,401,403

# หา parameters
ffuf -w wordlists/seclists/Discovery/Web-Content/burp-param-names.txt -u "https://target.com/path?FUZZ=value" -fc 400

# ทดสอบ vulns
nuclei -l alive.txt -t nuclei-templates/cves/
```

### 4. หา Bugs
```bash
# CORS
python3 freebuff/github_recon.py --search "org:target Access-Control"

# IDOR - ด้วยมือ
# 1. ดู requests ใน Burp
# 2. เปลี่ยน IDs
# 3. ตรวจสอบ responses

# XSS
# 1. หา input fields
# 2. ลอง <img src=x onerror=alert(1)>
# 3. ตรวจสอบ reflection
```

### 5. เขียน Report
```bash
# ใช้ template
cp reports/templates/cors_report.md reports/drafts/draft_$(date +%Y%m%d)_target.md

# Submit ผ่าน freebuff
freebuff "Submit this bug report to HackerOne for target program"
```

---

## 💰 Bug Bounty Tips

### เพิ่มโอกาสได้รับ Reward

1. **หาโปรใหม่ๆ** - ยังไม่มีคนเล่น = ยังไม่มี duplicate
2. **P4-P5 bugs** - ง่ายและเยอะ แม้จะได้น้อยแต่ได้เร็ว
3. **หาใน scope เล็กๆ** - มีโอกาส duplicate น้อยกว่า
4. **ส่ง report ดีๆ** - มี steps to reproduce, impact, evidence ครบ

### ผิดดีต้องทำอย่างไร

| สิ่งที่ทำ | ผลลัพธ์ |
|---------|---------|
| ลอง exploit production | 🚫 Duplicate / Wontfix |
| ใช้ automated tools เยอะๆ | 🚫 Rate limit / Ban |
| หาแต่ไม่ส่ง report | ❌ เสียเวลา |
| ส่ง report ไม่ครบ | ⚠️ NIT |

---

## 🎓 Learning Path

### Week 1-2: Easy Wins
- [ ] หา CORS misconfig 2-3 ตัว
- [ ] หา Open Redirect 2-3 ตัว
- [ ] ส่ง report 3-5 ตัว (เริ่มจาก P5/P4)
- [ ] เรียนรู้ Burp Suite พื้นฐาน

### Week 3-4: Medium
- [ ] หา IDOR 1-2 ตัว
- [ ] หา SSRF 1-2 ตัว
- [ ] เข้าใจ GraphQL basics
- [ ] ส่ง report 2-3 ตัว

### Month 2: Hard
- [ ] หา SQL Injection 1-2 ตัว
- [ ] หา XSS stored 2-3 ตัว
- [ ] เริ่มหา RCE ใน lab
- [ ] ส่ง report 2-3 ตัว

### Month 3+: Expert
- [ ] หา critical bugs (IDOR high impact, RCE)
- [ ] ทำ write-up เพื่อโชว์ portfolio
- [ ] ได้ Hall of Fame
- [ ] เริ่ม target big bounty programs

---

## ⚠️ Rate Limit Warning

**สำคัญมาก!** อย่าใช้ automated tools ติดต่อกันโดยไม่มี delay:

```bash
# FFUF - เพิ่ม delay
ffuf -w wordlist.txt -u "https://target/FUZZ" -p 0.5

# Nuclei - เพิ่ม delay
nuclei -l urls.txt -delay 1s

# ถ้าโดน ban
# - IP จะถูก block
# - Account อาจถูก suspend
# - ต้องรอ 1-24 ชม กว่าจะ unblock
```

**การป้องกัน:**
1. ใช้ `-rate` parameter เพื่อจำกัด requests/second
2. ใช้ proxy หมุน IP ถ้าทำ recon เยอะๆ
3. ทำงานเป็น session สั้นๆ แทน session ยาว

---

## 🛠️ Kali Tools เพิ่มเติม

| Tool | ใช้งาน | คำสั่ง |
|------|--------|-------|
| **masscan** | Fast port scan | `masscan -p1-65535 10.0.0.0/24` |
| **nikto** | Web server scan | `nikto -h target.com` |
| **wpscan** | WordPress scanner | `wpscan --url https://target.com` |
| **hydra** | Password attacks | `hydra -l admin -P pass.txt ssh://target` |
| **john** | Hash cracking | `john --wordlist=pass.txt hash.txt` |
| **whatweb** | Web fingerprint | `whatweb target.com` |

## 📚 Resources

### Tools
- **Amass** - Subdomain enumeration
- **Subfinder** - Passive subdomain discovery
- **FFUF** - Web fuzzing
- **SQLMap** - SQL injection
- **Nuclei** - Vulnerability scanner
- **Nmap** - Port scanning
- **Burp Suite** - Web testing (ควรใช้ Pro)

### Learning
- **PentesterLab** - เรียน web hacking
- **PortSwigger** - Web Security Academy
- **HackerOne Reports** - ดู write-ups จากคนอื่น
- **CTF Writeups** - ฝึกหา bugs ใน labs

---

## 📊 Bug Bounty Platforms แนะนำ

| Platform | URL | หมายเหตุ |
|----------|-----|----------|
| **HackerOne** | https://hackerone.com | โปรใหญ่ที่สุด |
| **Bugcrowd** | https://bugcrowd.com | มีโปรหลากหลาย |
| **Intigriti** | https://intigriti.com | EU-focused |
| **OpenBugBounty** | https://openbugbounty.org | VDP ไม่มี bounty |
| **GitHub VRP** | https://bounty.github.com | Microsoft acquisition |

## 🚀 Quick Start Commands

```bash
# 1. หาโปรใหม่
./scripts/find_targets.sh

# 2. Recon
amass enum -passive -d target.com -o subdomains.txt
subfinder -d target.com | httpx -silent | tee alive.txt

# 3. Scan
nuclei -l alive.txt -t nuclei-templates/

# 4. หา CORS
python3 freebuff/github_recon.py --dorks "Access-Control-Allow-Origin"

# 5. ส่ง report
freebuff "Submit report to HackerOne"
```

---

**หมายเหตุ:** ทำ bug bounty ต้องอยู่ใน scope เท่านั้น และต้องมีสติ อย่าพยายาม exploit production system ที่ไม่ได้รับอนุญาต