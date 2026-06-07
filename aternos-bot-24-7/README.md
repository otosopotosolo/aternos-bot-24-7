# SARAhack - Bug Bounty Auto-Submit System

**Version:** 2.0 (Re-planned)
**Purpose:** Automated Bug Bounty Report Submission with AI Assistance

---

## 🎯 Overview

SARAhack เป็นระบบอัตโนมัติสำหรับ submit bug bounty reports ไปยัง HackerOne และ Bugcrowd โดยใช้ freebuff AI ช่วย bypass Cloudflare protection

## ✨ Features

- **Auto-Submit Reports** - ส่ง reports อัตโนมัติผ่าน freebuff AI
- **Target Discovery** - หา bug bounty programs ใหม่ๆ
- **Vulnerability Research** - ติดตาม CVEs และช่องโหว่ใหม่
- **Report Tracking** - ติดตามสถานะ reports ทั้งหมด
- **Pentest Knowledge Base** - ความรู้จาก Pentest Book

## 🛠️ Quick Start

### 1. Setup Lab

```bash
# Clone/Copy project to server 8lgm.segfault.net
# Then run:
chmod +x tools/setup_lab.sh
./tools/setup_lab.sh
```

### 2. Configure Credentials

```bash
# Copy example env file
cp config/credentials/.env.example config/credentials/.env

# Edit with your credentials
nano config/credentials/.env
```

### 3. Find Targets

```bash
./scripts/find_targets.sh
```

### 4. Submit Report

```bash
# Via freebuff AI
python3 scripts/auto_submit.py --platform hackerone --program stripe --report reports/drafts/stripe_cors.md

# Manual fallback
python3 scripts/manual_submit.sh --platform hackerone --program stripe --file reports/drafts/stripe_cors.md
```

## 📁 Project Structure

```
sarahack/
├── SARAhack.md              # Main documentation (original)
├── REOPLAN.md               # Development plan
├── pentest-book.md          # Pentesting knowledge base
├── README.md                # This file
│
├── tools/                   # Tools & scripts
│   ├── setup_lab.sh         # Lab setup
│   ├── tracker.py           # Report tracker
│   └── ...
│
├── scripts/                 # Automation scripts
│   ├── auto_submit.py       # Auto submit via freebuff
│   ├── manual_submit.sh     # Manual fallback
│   ├── find_targets.sh      # Find new programs
│   └── fetch_cves.sh        # Fetch latest CVEs
│
├── freebuff/                # Freebuff AI integration
│   ├── sarahack_freebuff.sh # Bash wrapper
│   └── freebuff_bounty.py   # Python wrapper
│
├── reports/                 # Reports management
│   ├── templates/           # Report templates
│   ├── drafts/              # Draft reports
│   ├── submitted/           # Submitted reports
│   └── tracking/            # Status tracking
│
├── config/                  # Configuration
│   ├── credentials/         # Credentials (gitignored)
│   ├── platforms.yml        # Platform configs
│   └── programs.yml         # Program list
│
└── knowledge/               # Knowledge base
    ├── vulnerabilities/     # Vulnerability research
    └── poc/                 # Proof of concepts
```

## 🚀 Usage

### Using freebuff AI

```bash
# SSH to server
ssh -o "SetEnv=SECRET=JEpUOZPOVhCTwdhQInbJTtNA" root@8lgm.segfault.net

# Login to freebuff
freebuff login

# Submit report
python3 freebuff/freebuff_bounty.py submit --platform hackerone --program stripe --file report.md

# Find targets
python3 freebuff/freebuff_bounty.py find --keyword CORS

# Research vulnerability
python3 freebuff/freebuff_bounty.py research --target stripe.com --type CORS
```

### Manual Commands

```bash
# Track report
python3 tools/tracker.py add --platform hackerone --program stripe --vuln CORS --severity HIGH --file report.md

# List reports
python3 tools/tracker.py list --status pending

# Show stats
python3 tools/tracker.py stats
```

## 📚 Documentation

- [SARAhack.md](SARAhack.md) - Original project documentation
- [REOPLAN.md](REOPLAN.md) - Full development plan
- [pentest-book.md](pentest-book.md) - Pentesting knowledge

## 🔧 Tools Required

- Python 3.8+
- Go 1.21+
- nmap
- amass, subfinder, assetfinder
- httpx, naabu, nuclei
- ffuf, sqlmap
- Burp Suite (optional)

## ⚠️ Known Issues

- **Cloudflare Turnstile** - Blocked by default, use freebuff browser automation
- **SSH Password** - Manual entry required (segfault)

## 📝 License

MIT License

## 🤝 Contributing

Pull requests welcome! Please read REOPLAN.md for development guidelines.