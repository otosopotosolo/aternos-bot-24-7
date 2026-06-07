#!/bin/bash
# SARAhack Lab Setup Script
# ติดตั้งเครื่องมือ pentesting ทั้งหมดสำหรับ Bug Bounty Hunting

set -e

echo "=========================================="
echo "  SARAhack Lab Setup"
echo "=========================================="

# ตรวจสอบ OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "[+] Linux detected"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "[+] macOS detected"
else
    echo "[-] Unsupported OS: $OSTYPE"
    exit 1
fi

# Colors
RED='\u001b[31m'
GREEN='\u001b[32m'
YELLOW='\u001b[33m'
NC='\u001b[0m' # No Color

log_success() { echo -e "${GREEN}[+]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[!]${NC} $1"; }
log_error() { echo -e "${RED}[-]${NC} $1"; }

# สร้างโครงสร้างโฟลเดอร์
echo ""
echo "[*] Creating directory structure..."
mkdir -p tools/recon tools/web tools/cloud tools/mobile
mkdir -p scripts reports/drafts reports/submitted reports/tracking
mkdir -p config/credentials knowledge/vulnerabilities knowledge/poc
mkdir -p wordlists
log_success "Directory structure created"

# Update system
echo ""
echo "[*] Updating system packages..."
if command -v apt-get &> /dev/null; then
    sudo apt-get update && sudo apt-get upgrade -y
elif command -v yum &> /dev/null; then
    sudo yum update -y
elif command -v brew &> /dev/null; then
    brew update
fi
log_success "System updated"

# Install Python packages
echo ""
echo "[*] Installing Python packages..."
pip3 install --break-system-packages requests beautifulsoup4 playwright selenium
pip3 install --break-system-packages argparse yaml colorama
log_success "Python packages installed"

# Install Go (ถ้ายังไม่มี)
if ! command -v go &> /dev/null; then
    echo ""
    echo "[*] Installing Go..."
    wget -q https://go.dev/dl/go1.21.0.linux-amd64.tar.gz
    sudo tar -C /usr/local -xzf go1.21.0.linux-amd64.tar.gz
    rm go1.21.0.linux-amd64.tar.gz
    export GOROOT=/usr/local/go
    export GOPATH=$HOME/go
    export PATH=$PATH:/usr/local/go/bin:$GOPATH/bin
    log_success "Go installed"
fi

# Persist GOPATH for Go tools
export GOROOT=/usr/local/go
export GOPATH=$HOME/go
export PATH=$PATH:/usr/local/go/bin:$GOPATH/bin:$HOME/go/bin

# Add to .bashrc for persistence
echo 'export GOROOT=/usr/local/go' >> ~/.bashrc
echo 'export GOPATH=$HOME/go' >> ~/.bashrc
echo 'export PATH=$PATH:/usr/local/go/bin:$GOPATH/bin:$HOME/go/bin' >> ~/.bashrc
log_success "Go environment persisted to ~/.bashrc"

# Install Recon Tools
echo ""
echo "[*] Installing Recon tools..."

# amass
if ! command -v amass &> /dev/null; then
    go install -v github.com/owasp-amass/amass/v3@latest
    log_success "amass installed"
fi

# subfinder
if ! command -v subfinder &> /dev/null; then
    go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
    log_success "subfinder installed"
fi

# assetfinder
if ! command -v assetfinder &> /dev/null; then
    go install -v github.com/tomnomnom/assetfinder@latest
    log_success "assetfinder installed"
fi

# httpx
if ! command -v httpx &> /dev/null; then
    go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
    log_success "httpx installed"
fi

# naabu
if ! command -v naabu &> /dev/null; then
    go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest
    log_success "naabu installed"
fi

# nuclei
if ! command -v nuclei &> /dev/null; then
    go install -v github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest
    log_success "nuclei installed"
fi

# Install Web Tools
echo ""
echo "[*] Installing Web tools..."

# ffuf
if ! command -v ffuf &> /dev/null; then
    go install -v github.com/ffuf/ffuf@latest
    log_success "ffuf installed"
fi

# sqlmap
if ! command -v sqlmap &> /dev/null; then
    git clone --depth 1 https://github.com/sqlmapproject/sqlmap.git ~/tools/sqlmap
    log_success "sqlmap installed"
fi

# dirb
if ! command -v dirb &> /dev/null; then
    sudo apt-get install -y dirb
    log_success "dirb installed"
fi

# gobuster
if ! command -v gobuster &> /dev/null; then
    go install -v github.com/OJ/gobuster/v3@latest
    log_success "gobuster installed"
fi

# Install Cloud Tools
echo ""
echo "[*] Installing Cloud tools..."

# cloud_enum
if [ ! -d "~/tools/cloud_enum" ]; then
    git clone --depth 1 https://github.com/initstring/cloud_enum.git ~/tools/cloud_enum
    log_success "cloud_enum installed"
fi

# Install Nmap
if ! command -v nmap &> /dev/null; then
    sudo apt-get install -y nmap
    log_success "nmap installed"
fi

# Install Kali-style Penetration Testing Tools
echo ""
echo "[*] Installing Kali-style Pentesting Tools..."

# Install sqlmap
git clone --depth 1 https://github.com/sqlmapproject/sqlmap.git ~/tools/sqlmap 2>/dev/null || echo "sqlmap already exists"
ln -sf ~/tools/sqlmap/sqlmap.py /usr/local/bin/sqlmap
log_success "sqlmap installed"

# Install nikto
if ! command -v nikto &> /dev/null; then
    git clone --depth 1 https://github.com/sullo/nikto.git ~/tools/nikto 2>/dev/null || echo "nikto already exists"
    ln -sf ~/tools/nikto/program/nikto.pl /usr/local/bin/nikto
    log_success "nikto installed"
fi

# Install hydra (password attacks)
if ! command -v hydra &> /dev/null; then
    sudo apt-get install -y hydra
    log_success "hydra installed"
fi

# Install john the ripper
if ! command -v john &> /dev/null; then
    sudo apt-get install -y john
    log_success "john installed"
fi

# Install masscan
if ! command -v masscan &> /dev/null; then
    sudo apt-get install -y masscan
    log_success "masscan installed"
fi

# Install whatweb (web fingerprinting)
if ! command -v whatweb &> /dev/null; then
    sudo apt-get install -y whatweb
    log_success "whatweb installed"
fi

# Install wpscan (WordPress scanner)
if ! command -v wpscan &> /dev/null; then
    gem install wpscan
    log_success "wpscan installed"
fi

# Install seclists (comprehensive wordlists)
if [ ! -d "~/tools/seclists" ]; then
    git clone --depth 1 https://github.com/danielmiessler/SecLists.git ~/tools/seclists
    ln -sf ~/tools/seclists wordlists/seclists
    log_success "SecLists installed"
fi

# Install wordlists
echo ""
echo "[*] Downloading wordlists..."

# SecLists
if [ ! -d "~/tools/seclists" ]; then
    git clone --depth 1 https://github.com/danielmiessler/SecLists.git ~/tools/seclists
    ln -sf ~/tools/seclists wordlists/seclists
    log_success "SecLists installed"
fi

# Install sshpass for automated SSH
echo ""
echo "[*] Installing sshpass..."
if ! command -v sshpass &> /dev/null; then
    sudo apt-get install -y sshpass
    log_success "sshpass installed"
fi

# Install jq for JSON parsing
echo ""
echo "[*] Installing jq..."
if ! command -v jq &> /dev/null; then
    sudo apt-get install -y jq
    log_success "jq installed"
fi

# Setup config files
echo ""
echo "[*] Creating config files..."

# platforms.yml
cat > config/platforms.yml << 'EOF'
platforms:
  hackerone:
    name: "HackerOne"
    api_url: "https://api.hackerone.com/v1"
    web_url: "https://hackerone.com"
    credentials:
      - env: H1_EMAIL
      - env: H1_PASSWORD
  
  bugcrowd:
    name: "Bugcrowd"
    api_url: "https://bugcrowd.com/api/v2"
    web_url: "https://bugcrowd.com"
    credentials:
      - env: BC_EMAIL
      - env: BC_PASSWORD
EOF

# programs.yml
cat > config/programs.yml << 'EOF'
# Bug Bounty Programs to hunt
programs:
  high_priority:
    - name: "Stripe"
      platform: hackerone
      scope: ["*.stripe.com", "*.stripe.network"]
      bounty: true
    
    - name: "Discord"
      platform: hackerone
      scope: ["*.discord.com", "*.discordapp.com"]
      bounty: true
    
    - name: "Uber"
      platform: hackerone
      scope: ["*.uber.com", "*.uberinternal.com"]
      bounty: true
  
  medium_priority:
    - name: "Shopify"
      platform: hackerone
      scope: ["*.shopify.com"]
      bounty: true
    
    - name: "Coinbase"
      platform: hackerone
      scope: ["*.coinbase.com"]
      bounty: true
EOF

# Create credentials template
cat > config/credentials/.env.example << 'EOF'
# HackerOne
H1_EMAIL=${HACKERONE_EMAIL}
H1_PASSWORD=#)a9By=*D#6/w9T

# Bugcrowd
BC_EMAIL=your@email.com
BC_PASSWORD=your_password

# freebuff Server
FREEBUFF_SERVER=8lgm.segfault.net
FREEBUFF_SECRET=JEpUOZPOVhCTwdhQInbJTtNA

# Discord Webhook (สำหรับ notifications)
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
EOF

log_success "Config files created"

# Final summary
echo ""
echo "=========================================="
echo -e "${GREEN}[+] Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "Tools installed:"
echo "  - amass, subfinder, assetfinder (recon)"
echo "  - httpx, naabu, nuclei (scanning)"
echo "  - ffuf, sqlmap, gobuster (web)"
echo "  - nmap (port scanning)"
echo ""
echo "Next steps:"
echo "  1. cp config/credentials/.env.example config/credentials/.env"
echo "  2. แก้ไข credentials ในไฟล์ .env"
echo "  3. ./scripts/find_targets.sh"
echo ""
echo "=========================================="