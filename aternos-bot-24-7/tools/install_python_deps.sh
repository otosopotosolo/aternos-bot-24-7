#!/bin/bash
# SARAhack - Python & Dependencies Installer
# Run this script on the server (8lgm.segfault.net or tmate session)
# Usage: chmod +x install_python_deps.sh && ./install_python_deps.sh

set -e

echo "=========================================="
echo "  SARAhack - Python Dependencies Installer"
echo "=========================================="

# Colors
RED='\u001b[31m'
GREEN='\u001b[32m'
YELLOW='\u001b[33m'
NC='\u001b[0m'

log_success() { echo -e "${GREEN}[+]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[!]${NC} $1"; }
log_error() { echo -e "${RED}[-]${NC} $1"; }

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    log_warn "Not running as root. Using sudo..."
    SUDO=sudo
else
    SUDO=""
fi

# Step 1: Update package list
echo ""
log_success "Updating package list..."
$SUDO apt update

# Step 2: Install Python 3 and pip
echo ""
log_success "Installing Python 3 and pip..."
$SUDO apt install -y python3 python3-pip python3-venv

# Verify Python installation
PYTHON_VERSION=$(python3 --version)
log_success "Python installed: $PYTHON_VERSION"

# Step 3: Upgrade pip
echo ""
log_success "Upgrading pip..."
python3 -m pip --upgrade pip

# Step 4: Install core dependencies
echo ""
log_success "Installing core Python packages..."

python3 -m pip install --break-system-packages:
    requests
    selenium
    webdriver-manager
    playwright
    Pillow
    beautifulsoup4
    lxml
    html5lib

# Step 5: Install Playwright browsers
echo ""
log_success "Installing Playwright Chromium browser..."
python3 -m playwright install chromium

# Step 6: Create virtual environment (optional but recommended)
echo ""
log_success "Creating Python virtual environment..."
python3 -m venv ~/.venv/sarahack
source ~/.venv/sarahack/bin/activate

# Install packages in venv as well
pip install --quiet requests selenium webdriver-manager playwright beautifulsoup4 lxml

log_success "Virtual environment created at ~/.venv/sarahack"

# Step 7: Install additional tools
echo ""
log_success "Installing additional system tools..."
$SUDO apt install -y curl wget git jq httpie nmap masscan ffuf sqlmap python3-nmap

# Step 8: Verify installations
echo ""
echo "=========================================="
log_success "Verifying installations..."
echo "=========================================="

echo "Python version:"
python3 --version

echo ""
echo "Python packages:"
pip list | grep -E "requests|selenium|playwright|beautifulsoup4"

echo ""
echo "Playwright browsers:"
playwright show-trace --version 2>/dev/null || echo "Playwright CLI available"

# Step 9: Create convenient aliases
echo ""
log_success "Creating convenient aliases..."

# Add to .bashrc
cat >> ~/.bashrc << 'EOF'

# SARAhack aliases
alias saravenv='source ~/.venv/sarahack/bin/activate'
alias sara-py='python3 -m pip'
alias sara-playwright='playwright'

# Quick test
test-python() {
    python3 -c "import requests; print('requests OK')"
    python3 -c "import selenium; print('selenium OK')"
    playwright --version
}
EOF

log_success "Aliases added to ~/.bashrc"

# Final message
echo ""
echo "=========================================="
echo -e "${GREEN}[+]${NC} Installation complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Activate virtual environment: source ~/.venv/sarahack/bin/activate"
echo "  2. Or use aliases: saravenv"
echo "  3. Test Python packages: python3 -c 'import requests; print(\"OK\")'"
echo ""
echo "To use HackerOne API submitter:"
echo "  export H1_API_IDENTIFIER='your_api_id'"
echo "  export H1_API_TOKEN='your_api_token'"
echo ""