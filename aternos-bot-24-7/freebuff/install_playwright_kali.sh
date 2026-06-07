#!/bin/bash
# SARAhack - Playwright & Chromium Installation Script for Kali Linux
# Run this script on your Kali machine to set up browser automation

set -e

echo "=========================================="
echo "🎯 Playwright + Chromium Setup for Kali"
echo "=========================================="
echo ""

# Colors for output
RED='\u001b[31m'
GREEN='\u001b[32m'
YELLOW='\u001b[33m'
BLUE='\u001b[34m'
NC='\u001b[0m' # No Color

log_info() { echo -e "${BLUE}[*]${NC} $1"; }
log_success() { echo -e "${GREEN}[✓]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[!]${NC} $1"; }
log_error() { echo -e "${RED}[✗]${NC} $1"; }

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    log_warn "Running as root - will use --no-sandbox for Chromium"
else
    log_warn "Not running as root. You may need to enter sudo password."
fi

echo ""
log_info "Step 1: Updating apt package list..."
sudo apt update -y
log_success "Package list updated"

echo ""
log_info "Step 2: Installing system dependencies for Chromium..."
# Note: NOT installing chromium-sandbox - Playwright handles sandboxing itself
sudo apt install -y --no-install-recommends \n    chromium \n    chromium-driver \n    libayatana-appindicator3-1 \n    libnss3 \n    libxss1 \n    libasound2 \n    libatk-bridge2.0-0 \n    libatk1.0-0 \n    libcups2 \n    libdrm2 \n    libgbm1 \n    libgtk-3-0 \n    libnspr4 \n    libpango-1.0-0 \n    libxcomposite1 \n    libxdamage1 \n    libxrandr2 \n    xdg-utils \n    fonts-liberation \n    libappindicator3-1 \n    x11-utils \n    xvfb \n    libxcb1 \n    libxcb-render0 \n    libxcb-shm0 \n    libxcb-icccm4 \n    libxcb-image0 \n    libxcb-keysyms0 \n    libxcb-randr0 \n    libxcb-shape0 \n    libxcb-sync1 \n    libxcb-xfixes0 \n    libxcb-xinerama0 \n    libxcb-dri3-0 \n    libx11-6 \n    libglib2.0-0 \n    libdbus-1-3
log_success "System dependencies installed"

echo ""
log_info "Step 3: Verifying Chromium installation..."
if command -v chromium &> /dev/null; then
    CHROMIUM_VERSION=$(chromium --version 2>/dev/null || chromium-browser --version 2>/dev/null)
    log_success "Chromium installed: $CHROMIUM_VERSION"
elif command -v chromium-browser &> /dev/null; then
    CHROMIUM_VERSION=$(chromium-browser --version)
    log_success "Chromium installed: $CHROMIUM_VERSION"
else
    log_error "Chromium not found after installation"
    log_info "Trying to install chromium-browser instead..."
    sudo apt install -y chromium-browser
    if command -v chromium-browser &> /dev/null; then
        log_success "Chromium-browser installed"
    else
        log_error "Chromium installation failed"
        exit 1
    fi
fi

echo ""
log_info "Step 4: Installing Python Playwright..."
pip3 install playwright --break-system-packages 2>/dev/null || pip3 install playwright
log_success "Python Playwright installed"

echo ""
log_info "Step 5: Downloading Chromium browser for Playwright..."
python3 -m playwright install chromium
log_success "Playwright Chromium downloaded"

echo ""
log_info "Step 6: Installing Playwright system dependencies..."
if python3 -m playwright install-deps chromium 2>&1 | tee /tmp/playwright_deps.log; then
    log_success "Playwright dependencies installed"
else
    log_warn "Some Playwright dependencies failed to install"
    log_info "Check /tmp/playwright_deps.log for details"
    log_info "Continuing anyway - may still work..."
fi

echo ""
log_info "Step 7: Testing Playwright with Chromium (headless mode)..."
python3 << 'PYEOF'
try:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        # Use --no-sandbox for root user
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
        )
        page = browser.new_page()
        
        # Test basic navigation
        page.goto("https://example.com", timeout=30000)
        title = page.title()
        
        # Test headless rendering
        page.set_content("<html><body><h1>Test Headless</h1></body></html>")
        content = page.content()
        
        browser.close()
        
        if "Test Headless" in content:
            print("[✓] Playwright + Chromium headless mode works!")
            print(f"    Page title: {title}")
        else:
            print("[✗] Content test failed")
            exit(1)
            
except Exception as e:
    print(f"[✗] Test failed: {e}")
    print("[!] Common issues:")
    print("    - Run as root with --no-sandbox")
    print("    - Check if Chromium is installed: chromium --version")
    print("    - Try: python3 -m playwright install chromium")
    exit(1)
PYEOF

if [ $? -eq 0 ]; then
    log_success "Playwright automation ready!"
else
    log_error "Playwright test failed"
    exit 1
fi

echo ""
log_info "Step 8: Testing the HackerOne submitter script..."
if [ -f "/home/runner/workspace/freebuff/playwright_h1_submitter.py" ]; then
    python3 /home/runner/workspace/freebuff/playwright_h1_submitter.py --test
    if [ $? -eq 0 ]; then
        log_success "HackerOne submitter script works!"
    else
        log_warn "Submitter script test failed - may need adjustments"
    fi
else
    log_warn "Submitter script not found at expected path"
fi

echo ""
echo "=========================================="
echo "✅ Installation Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Set HackerOne credentials:"
echo "     export HACKERONE_EMAIL=\"${HACKERONE_EMAIL}\""
echo "     export HACKERONE_PASSWORD=\")a9By=*D#6/w9T\""
echo ""
echo "  2. List pending reports:"
echo "     python3 /home/runner/workspace/freebuff/playwright_h1_submitter.py --list"
echo ""
echo "  3. Submit a specific report (e.g., #4 - Shopify):"
echo "     python3 /home/runner/workspace/freebuff/playwright_h1_submitter.py --submit 4"
echo ""
echo "  4. Submit all pending HackerOne reports:"
echo "     python3 /home/runner/workspace/freebuff/playwright_h1_submitter.py --submit-all"
echo ""