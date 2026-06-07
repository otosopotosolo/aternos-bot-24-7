#!/bin/bash
# SARAhack - Run Browser Automation via Docker
# Usage: ./run_browser_submit.sh --submit 24

set -e

# Colors - fixed ANSI escape codes
RED='\033[31m'
GREEN='\033[32m'
YELLOW='\033[33m'
NC='\033[0m'

echo -e "${GREEN}=== SARAhack Browser Automation (Docker) ===${NC}"

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo -e "${RED}ERROR: Docker not found${NC}"
    exit 1
fi

# Check if Docker daemon is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}ERROR: Docker daemon is not running${NC}"
    exit 1
fi

# Parse arguments
REPORT_ID=""
COMMAND="--list"

while [[ $# -gt 0 ]]; do
    case $1 in
        --submit)
            REPORT_ID=$2
            COMMAND="--submit $REPORT_ID"
            shift 2
            ;;
        --submit-all)
            COMMAND="--submit-all"
            shift
            ;;
        --test)
            COMMAND="--test"
            shift
            ;;
        *)
            shift
            ;;
    esac
done

# Build Docker image
echo -e "${YELLOW}[*] Building Docker image...${NC}"
docker build -f freebuff/Dockerfile.playwright -t sarahack-playwright . --no-cache

# Run automation
echo -e "${YELLOW}[*] Running Playwright automation...${NC}"
docker run --rm \\
    -e HACKERONE_EMAIL=${HACKERONE_EMAIL} \\
    -e HACKERONE_PASSWORD='#)a9By=*D#6/w9T' \\
    -e CHROME_BIN=/usr/bin/google-chrome \\
    -e PLAYWRIGHT_CHROMIUM_ARGS='--no-sandbox --disable-setuid-sandbox --disable-dev-shm-usage' \\
    -v $(pwd)/reports:/app/reports \\
    -v $(pwd)/freebuff:/app/freebuff \\
    sarahack-playwright python3 playwright_h1_submitter.py $COMMAND

echo -e "${GREEN}[*] Done!${NC}"