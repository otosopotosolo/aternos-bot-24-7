#!/bin/bash
# ============================================
# Remote Scanning Script - สแกนผ่าน Segfault.net Kali
# ============================================

set -e

# Configuration
SERVER="root@8lgm.segfault.net"
SECRET="NhjQPlbFLARQXwmSPVNeAJgz"
PASSWORD="${FREEBUFF_PASSWORD:-segfault}"
CODEBUFF_KEY="${CODEBUFF_POSTHOG_API_KEY:-be0e3e50-e07c-434d-98d0-85d6c59d615c}"

# Colors (ANSI escape codes)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

usage() {
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  status                 - ตรวจสอบ remote server"
    echo "  scan [program]         - รัน mass_scanner บน remote (default: shopify)"
    echo "  nmap <target> [ports]  - รัน nmap บน remote"
    echo "  masscan <target> [ports] - รัน masscan บน remote"
    echo "  curl-test <url>        - ทดสอบ CORS ด้วย curl"
    echo "  deploy                 - deploy ไปยัง tmate session"
    echo "  clean                  - ลบ traces ออกจาก remote (OPSEC!)"
    echo ""
    echo "Options:"
    echo "  --limit N              - จำกัดจำนวน targets (default: 50)"
    echo "  --verbose              - แสดงรายละเอียด"
    echo ""
    echo "Examples:"
    echo "  $0 status"
    echo "  $0 scan shopify --limit 100"
    echo "  $0 nmap api.stripe.com -p 1-1000"
    echo "  $0 masscan 1.2.3.0/24 -p80,443"
    echo "  $0 clean"
}

# Helper function for SSH with sshpass
do_ssh() {
    sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=30 -o "SetEnv SECRET=$SECRET" "$SERVER" "$@"
}

# Auto-deploy freebuff to remote Kali (tar pipeline)
auto_deploy() {
    echo -e "${YELLOW}[*] Auto-deploying freebuff to remote Kali...${NC}"
    tar czf - freebuff | sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no -o "SetEnv SECRET=$SECRET" "$SERVER" "mkdir -p /root/workspace && rm -rf /root/workspace/freebuff && tar xzf - -C /root/workspace" 2>&1
    echo -e "${GREEN}[*] Deploy complete!${NC}"
}

cmd_status() {
    echo -e "${GREEN}[*] ตรวจสอบ remote Kali...${NC}"
    do_ssh "echo connected && whoami && uptime | head -1 && echo '---Tools---' && which masscan nmap curl python3 node 2>/dev/null | head -10"
}

cmd_deploy() {
    echo -e "${GREEN}[*] Deploy ไปยัง tmate session...${NC}"
    do_ssh "export CODEBUFF_POSTHOG_API_KEY='$CODEBUFF_KEY' && echo 'Connected to Kali' && if command -v tmate >/dev/null 2>&1; then tmate -S /tmp/tmate.sock new-session -d -s main 2>/dev/null || true; tmate -S /tmp/tmate.sock display -p '#{session_name}'; else echo 'tmate not found'; fi"
}

cmd_scan() {
    local program="${1:-shopify}"
    local limit="${LIMIT:-50}"
    local verbose_flag=""
    local program_arg=""

    if [ -n "$VERBOSE" ]; then
        verbose_flag="--verbose"
    fi

    # ถ้าไม่ใส่ program หรือใส่ "all" จะ scan ทั้งหมด (ไม่ pass --program)
    if [ -n "$program" ] && [ "$program" != "all" ]; then
        program_arg="--program=$program"
    fi

    # Auto-deploy freebuff ก่อน scan (ถ้ายังไม่มีบน remote)
    auto_deploy

    if [ -n "$program_arg" ]; then
        echo -e "${GREEN}[*] รัน mass_scanner บน remote Kali (program: $program, limit: $limit)${NC}"
    else
        echo -e "${GREEN}[*] รัน mass_scanner บน remote Kali (scan ALL programs, limit: $limit)${NC}"
    fi

    do_ssh "mkdir -p /root/workspace/freebuff && cd /root/workspace/freebuff && npm install --silent 2>/dev/null || true && export CODEBUFF_POSTHOG_API_KEY='$CODEBUFF_KEY' && node mass_scanner.js $program_arg --limit=$limit $verbose_flag"
}

cmd_nmap() {
    local target="${1:-api.stripe.com}"
    local ports="${2:--p 1-1000}"

    echo -e "${GREEN}[*] รัน nmap บน remote Kali (target: $target)${NC}"
    do_ssh "nmap $target $ports -oX /tmp/nmap_scan.xml && echo 'Scan complete, results in /tmp/nmap_scan.xml'"
}

cmd_masscan() {
    local target="${1:-1.2.3.0/24}"
    local ports="${2:--p80,443}"

    echo -e "${GREEN}[*] รัน masscan บน remote Kali (target: $target)${NC}"
    do_ssh "masscan $target $ports --rate=10000 -oX /tmp/masscan_scan.xml && echo 'Scan complete, results in /tmp/masscan_scan.xml'"
}

cmd_curl_test() {
    local url="${1:-https://api.stripe.com}"

    echo -e "${GREEN}[*] ทดสอบ CORS ด้วย curl บน remote Kali (url: $url)${NC}"
    do_ssh "curl -sI -H 'Origin: https://evil.com' $url | grep -i 'access-control'"
}

cmd_clean() {
    echo -e "${YELLOW}[*] ลบ traces ออกจาก remote Kali (OPSEC)...${NC}"
    echo -e "${YELLOW}[!] กำลังลบ workspace, history, และ temp files...${NC}"
    # ใช้ do_ssh แต่ต้องใช้ && เพื่อไม่ให้ script หยุดถ้า command รันไม่ได้
    do_ssh "rm -rf /root/workspace /root/freebuff 2>/dev/null; rm -f ~/.bash_history ~/.zsh_history ~/.history 2>/dev/null; unset HISTFILE HISTSIZE HISTFILESIZE; (rm -rf /tmp/* 2>/dev/null || true); echo '=== OPSEC Clean Complete ==='; echo 'Checking /root/:'; ls -la /root/ 2>/dev/null || echo 'Clean!'"
}

# Parse command first
COMMAND="${1:-}"
shift || true

# Parse global options and collect remaining args (--limit, --verbose can be anywhere)
LIMIT="50"
VERBOSE=""
_remaining=""
_capture_next=false

for arg in "$@"; do
    if [[ "$_capture_next" == "true" ]]; then
        LIMIT="$arg"
        _capture_next=false
        continue
    fi
    case "$arg" in
        --limit)
            _capture_next=true
            ;;
        --limit=*)
            LIMIT="${arg#--limit=}"
            ;;
        --verbose|-v)
            VERBOSE="1"
            ;;
        --help|-h)
            usage
            exit 0
            ;;
        *)
            _remaining="$_remaining $arg"
            ;;
    esac
done

# Trim leading space and set remaining as positional args
_remaining="${_remaining# }"
set -- $_remaining

# Now $@ contains only command-specific args (program name, etc.)
case "$COMMAND" in
    status)
        VERBOSE=1 cmd_status
        ;;
    scan)
        cmd_scan "$@"
        ;;
    nmap)
        cmd_nmap "$@"
        ;;
    masscan)
        cmd_masscan "$@"
        ;;
    curl-test)
        cmd_curl_test "$@"
        ;;
    deploy)
        cmd_deploy
        ;;
    clean)
        cmd_clean
        ;;
    test)
        echo -e "${GREEN}[*] ทดสอบ SSH connection...${NC}"
        do_ssh "echo 'SSH OK!' && whoami"
        ;;
    "")
        usage
        ;;
    *)
        echo -e "${RED}[ERROR] Unknown command: $COMMAND${NC}"
        usage
        exit 1
        ;;
esac