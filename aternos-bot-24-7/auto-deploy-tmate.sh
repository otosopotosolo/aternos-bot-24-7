#!/bin/bash
# =============================================================================
# AUTO-DEPLOY SCRIPT FOR TMATE SESSION
# =============================================================================
# SSH: eS6fytCGPu74pDmMNxAKcszLc@lon1.tmate.io
# 
# Usage: 
#   1. SSH to tmate: ssh eS6fytCGPu74pDmMNxAKcszLc@lon1.tmate.io
#   2. Copy/paste this script or run line by line
#   3. Or download and run: 
#      curl -L -o deploy.tar https://tmpfiles.org/wmw2KoTPwxYj/deploy.tar
#      tar xf deploy.tar && chmod +x auto-deploy-tmate.sh && ./auto-deploy-tmate.sh
# =============================================================================

# Configuration
WORKSPACE_URL="https://tmpfiles.org/wvwMKNHv2dZO/workspace.tar"
TOOLS_URL="https://tmpfiles.org/wHwCKZHDEY2h/tools.tar"

# Colors (simple printf style)
GREEN='\n\uff1b[32m'
YELLOW='\n\uff1b[33m'
BLUE='\n\uff1b[34m'
RED='\n\uff1b[31m'
NC='\uff1b[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  TMATE AUTO-DEPLOY SCRIPT${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# =============================================================================
# STEP 1: System Info
# =============================================================================
echo -e "${GREEN}[1/7] System Information${NC}"
echo "  Hostname: $(hostname)"
echo "  OS: $(uname -s) $(uname -r)"
echo "  User: $(whoami)"
echo "  Date: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# =============================================================================
# STEP 2: Create Workspace
# =============================================================================
echo -e "${GREEN}[2/7] Creating workspace directory...${NC}"
mkdir -p ~/workspace
cd ~/workspace
echo "  Working directory: $(pwd)"
echo ""

# =============================================================================
# STEP 3: Download & Extract Project
# =============================================================================
echo -e "${GREEN}[3/7] Downloading project files...${NC}"

if curl -L -o workspace.tar "${WORKSPACE_URL}" 2>/dev/null; then
    echo "  Download complete!"
    tar xf workspace.tar 2>/dev/null && echo "  Extract complete!" || echo "  Extract failed!"
    ls -la | head -10
else
    echo -e "  ${RED}Download failed!${NC}"
fi
echo ""

# =============================================================================
# STEP 4: Download & Extract Tools
# =============================================================================
echo -e "${GREEN}[4/7] Downloading tools package...${NC}"

if curl -L -o tools.tar "${TOOLS_URL}" 2>/dev/null; then
    echo "  Tools download complete!"
    tar xf tools.tar 2>/dev/null && echo "  Tools extract complete!" || echo "  Tools extract failed!"
else
    echo -e "  ${YELLOW}Tools download skipped${NC}"
fi
echo ""

# =============================================================================
# STEP 5: Make Scripts Executable
# =============================================================================
echo -e "${GREEN}[5/7] Preparing scripts...${NC}"

if [ -f ~/workspace/tools/install-tools.sh ]; then
    chmod +x ~/workspace/tools/install-tools.sh
    echo "  install-tools.sh ready"
fi

if [ -f ~/workspace/auto-deploy-tmate.sh ]; then
    chmod +x ~/workspace/auto-deploy-tmate.sh
    echo "  auto-deploy-tmate.sh ready"
fi
echo ""

# =============================================================================
# STEP 6: Install Tools
# =============================================================================
echo -e "${GREEN}[6/7] Installing penetration testing tools...${NC}"
echo "  Updating package list..."
sudo apt update -qq 2>/dev/null || true

echo "  Installing tools (nmap, sqlmap, nikto, gobuster, etc.)..."
sudo apt install -y nmap sqlmap nikto dirb masscan gobuster git python3-pip curl wget 2>/dev/null || true

echo "  Installing Python packages..."
pip3 install requests bs4 paramiko colorama termcolor 2>/dev/null || true

# Install Go if not present
if ! command -v go &> /dev/null; then
    echo "  Installing Go..."
    curl -sL https://go.dev/dl/go1.22.0.linux-amd64.tar.gz | sudo tar -C /usr/local -xzf - 2>/dev/null || true
    export PATH=$PATH:/usr/local/go/bin
fi

# Install Go-based tools
if command -v go &> /dev/null; then
    echo "  Installing Amass, Subfinder, Nuclei..."
    GOBIN=/usr/local/bin go install -v github.com/owasp-amass/amass/v3/...@latest 2>/dev/null || true
    GOBIN=/usr/local/bin go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest 2>/dev/null || true
    GOBIN=/usr/local/bin go install -v github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest 2>/dev/null || true
fi

echo ""

# =============================================================================
# STEP 7: Verify Installation
# =============================================================================
echo -e "${GREEN}[7/7] Verifying installation...${NC}"
echo ""

echo "  Tools Status:"
command -v nmap > /dev/null && echo -e "    [OK] nmap" || echo -e "    [FAIL] nmap"
command -v sqlmap > /dev/null && echo -e "    [OK] sqlmap" || echo -e "    [FAIL] sqlmap"
command -v gobuster > /dev/null && echo -e "    [OK] gobuster" || echo -e "    [FAIL] gobuster"
command -v nikto > /dev/null && echo -e "    [OK] nikto" || echo -e "    [FAIL] nikto"
command -v masscan > /dev/null && echo -e "    [OK] masscan" || echo -e "    [FAIL] masscan"
command -v dirb > /dev/null && echo -e "    [OK] dirb" || echo -e "    [FAIL] dirb"
command -v amass > /dev/null && echo -e "    [OK] amass" || echo -e "    [FAIL] amass"
command -v subfinder > /dev/null && echo -e "    [OK] subfinder" || echo -e "    [FAIL] subfinder"
command -v nuclei > /dev/null && echo -e "    [OK] nuclei" || echo -e "    [FAIL] nuclei"

echo ""
echo "  Python packages:"
pip3 show requests > /dev/null 2>&1 && echo -e "    [OK] requests" || echo -e "    [FAIL] requests"
pip3 show bs4 > /dev/null 2>&1 && echo -e "    [OK] beautifulsoup4" || echo -e "    [FAIL] beautifulsoup4"
pip3 show paramiko > /dev/null 2>&1 && echo -e "    [OK] paramiko" || echo -e "    [FAIL] paramiko"

echo ""
echo "  Workspace contents:"
ls -la ~/workspace/ | head -15

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}  DEPLOYMENT COMPLETE!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Quick start:"
echo "  cd ~/workspace"
echo "  nmap -V                          # Check nmap"
echo "  sqlmap --version                 # Check sqlmap"
echo "  gobuster --help                  # Check gobuster"
echo "  ls -la tools/                    # See all tools"
echo ""