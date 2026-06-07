#!/bin/bash
# SARAhack Manual Submit Fallback
# เมื่อ auto-submit ล้มเหลว ใช้วิธีนี้

set -e

echo "=========================================="
echo "  SARAhack Manual Submit Helper"
echo "=========================================="

# Colors
RED='\u001b[31m'
GREEN='\u001b[32m'
YELLOW='\u001b[33m'
NC='\u001b[0m'

log_success() { echo -e "${GREEN}[+]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[!]${NC} $1"; }
log_error() { echo -e "${RED}[-]${NC} $1"; }

# Parse arguments
PLATFORM=""
PROGRAM=""
FILE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --platform)
            PLATFORM="$2"
            shift 2
            ;;
        --program)
            PROGRAM="$2"
            shift 2
            ;;
        --file)
            FILE="$2"
            shift 2
            ;;
        *)
            log_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

if [ -z "$PLATFORM" ] || [ -z "$PROGRAM" ] || [ -z "$FILE" ]; then
    echo "Usage: $0 --platform <hackerone|bugcrowd> --program <name> --file <report.md>"
    exit 1
fi

echo "[*] Platform: $PLATFORM"
echo "[*] Program: $PROGRAM"
echo "[*] Report: $FILE"

# Check if file exists
if [ ! -f "$FILE" ]; then
    log_error "Report file not found: $FILE"
    exit 1
fi

# Display report content
echo ""
echo "[*] Report content preview:"
echo "=========================================="
head -30 "$FILE"
echo "..."
echo "=========================================="

# Open browser based on platform
echo ""
log_success "Instructions:"
echo ""

if [ "$PLATFORM" == "hackerone" ]; then
    echo "1. Open: https://hackerone.com/$PROGRAM/reports/new"
    echo "2. Login with: ${HACKERONE_EMAIL}"
    echo "3. Copy content from: $FILE"
    echo "4. Fill form and submit"
elif [ "$PLATFORM" == "bugcrowd" ]; then
    echo "1. Open: https://bugcrowd.com/$PROGRAM/submit"
    echo "2. Login with your credentials"
    echo "3. Copy content from: $FILE"
    echo "4. Fill form and submit"
fi

echo ""
log_warn "Don't forget to update tracker after submission:"
echo "   python3 tools/tracker.py add --platform $PLATFORM --program $PROGRAM --vuln CORS --severity HIGH --file $FILE"

# Option to open browser directly
read -p "Open browser now? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    if command -v xdg-open &> /dev/null; then
        if [ "$PLATFORM" == "hackerone" ]; then
            xdg-open "https://hackerone.com/$PROGRAM/reports/new"
        else
            xdg-open "https://bugcrowd.com/$PROGRAM/submit"
        fi
    elif command -v open &> /dev/null; then
        if [ "$PLATFORM" == "hackerone" ]; then
            open "https://hackerone.com/$PROGRAM/reports/new"
        else
            open "https://bugcrowd.com/$PROGRAM/submit"
        fi
    fi
fi

log_success "Good luck with your submission!"