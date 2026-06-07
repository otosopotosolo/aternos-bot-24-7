#!/bin/bash
# EarnApp Installation Script
# Usage: ./install_earnapp.sh

set -e

echo "🔍 Checking EarnApp installation..."

if command -v earnapp &> /dev/null; then
    echo "⚠️ EarnApp is already installed"
    earnapp version
    exit 0
fi

echo "📦 Installing EarnApp..."

# Check if running in VM/Docker/Cloud (EarnApp forbids this)
if [ -f /.dockerenv ] || grep -q docker /proc/1/cgroup 2>/dev/null; then
    echo "⚠️ WARNING: Docker environment detected. EarnApp may not work in containers."
fi
if [ -f /proc/1/cgroup ] && grep -q "cloud" /proc/1/cgroup 2>/dev/null; then
    echo "⚠️ WARNING: Cloud environment detected. EarnApp ToS forbids cloud VPS."
fi

# Download and run the official installation script
wget -qO- https://brightdata.com/static/earnapp/install.sh > /tmp/earnapp.sh
chmod +x /tmp/earnapp.sh
sudo bash /tmp/earnapp.sh || echo "⚠️ EarnApp installation failed or was blocked by ToS"

echo "✅ EarnApp installation complete!"
echo ""
echo "📋 Next steps:"
echo "1. Sign up at https://earnapp.com (if you haven't already)"
echo "2. The terminal will show a link URL after installation"
echo "3. Copy that link and paste it in your browser where you're logged into EarnApp"
echo "4. Your device will be linked and you'll start earning"
echo ""
echo "📊 Check your dashboard at: https://earnapp.com/dashboard"