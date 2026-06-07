#!/bin/bash
# Honeygain Installation Script (Docker-based)
# Usage: ./install_honeygain.sh <email> <password> [device_name]

set -e

EMAIL="${1:-}"
PASSWORD="${2:-}"
DEVICE_NAME="${3:-linux-server}"

if [ -z "$EMAIL" ] || [ -z "$PASSWORD" ]; then
    echo "Usage: $0 <email> <password> [device_name]"
    echo "Example: $0 your@email.com yourpassword my-server"
    exit 1
fi

echo "🔍 Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first:"
    echo "   sudo apt update && sudo apt install docker.io"
    exit 1
fi

echo "✅ Docker found"

echo "🚀 Starting Honeygain container..."
docker run -d --name honeygain-client \\
    -tou-accept \\
    -email "$EMAIL" \\
    -pass "$PASSWORD" \\
    -device "$DEVICE_NAME" \\
    honeygain/honeygain

echo "✅ Honeygain is installed and running!"
echo "📊 Check your dashboard at: https://dashboard.honeygain.com/"
echo "📱 Device '$DEVICE_NAME' should appear within a few minutes"