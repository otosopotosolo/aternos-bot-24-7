#!/bin/bash
# Pawns.app Installation Script
# Usage: ./install_pawns.sh <email> <password>

set -e

EMAIL="${1:-}"
PASSWORD="${2:-}"

if [ -z "$EMAIL" ] || [ -z "$PASSWORD" ]; then
    echo "Usage: $0 <email> <password>"
    echo "Example: $0 your@email.com yourpassword"
    exit 1
fi

echo "🔍 Checking Pawns.app installation..."

if command -v pawns-cli &> /dev/null; then
    echo "⚠️ Pawns CLI is already installed"
    pawns-cli --version
    exit 0
fi

# Detect architecture
ARCH=$(uname -m)
if [ "$ARCH" = "x86_64" ]; then
    ARCH_NAME="amd64"
elif [ "$ARCH" = "aarch64" ] || [ "$ARCH" = "arm64" ]; then
    ARCH_NAME="arm64"
else
    ARCH_NAME="amd64"
fi

echo "📦 Downloading Pawns.app CLI for $ARCH_NAME..."

# Download the latest version
curl -sL "https://dashboard.pawns.app/api/cli/download/linux-$ARCH_NAME" -o /tmp/pawns-cli
chmod +x /tmp/pawns-cli

echo "🚀 Starting Pawns.app with credentials..."
/tmp/pawns-cli -email="$EMAIL" -password="$PASSWORD" &

echo "✅ Pawns.app is starting!"
echo "📊 Check your dashboard at: https://dashboard.pawns.app/"
echo "📱 Your device should appear within a few minutes after setup"