#!/bin/bash
#
# SARAhack - Correct Tmate Automation
#
# ปัญหา: tmate ไม่รองรับ remote command execution
# วิธีแก้: ต้องมี tmate session รันอยู่บน server แล้วใช้ send-keys
#
# Architecture:
# 1. ถ้ามี tmate session รันอยู่บน segfault server -> ใช้ cloudflared tunnel + tmate send-keys
# 2. ถ้าไม่มี -> ใช้วิธีอื่น เช่น direct SSH หรือ API
#

set -e

# Colors
RED='\uff1b[31m'
GREEN='\uff1b[32m'
YELLOW='\uff1b[33m'
BLUE='\uff1b[34m'
NC='\uff1b[0m'

log_info() { echo -e "${GREEN}[*] $1${NC}"; }
log_warn() { echo -e "${YELLOW}[!] $1${NC}"; }
log_error() { echo -e "${RED}[x] $1${NC}"; }

# Configuration
SEGFAULT_HOST="8lgm.segfault.net"
SECRET="EUwteWtAugwWBPqCIUWcuVGq"

# SSH to segfault server via cloudflared tunnel
ssh_segfault() {
    local cmd="$1"
    log_info "Connecting to segfault server via cloudflared..."
    
    # Method 1: Use cloudflared access
    ssh -o "StrictHostKeyChecking=no" -o "ConnectTimeout=30" -o "SetEnv SECRET=$SECRET" root@$SEGFAULT_HOST "$cmd" 2>&1
}

# Check if tmate is running on segfault
check_tmate_status() {
    log_info "Checking tmate status on segfault server..."
    
    ssh_segfault "tmux list-sessions 2>/dev/null || echo 'No tmux sessions'; pgrep -a tmate 2>/dev/null || echo 'tmate not running'" 2>&1
}

# Send command to existing tmate session
tmate_send_keys() {
    local session="${1:-0}"
    local cmd="$2"
    
    log_info "Sending to tmate session $session: $cmd"
    ssh_segfault "tmux send-keys -t $session '$cmd' Enter" 2>&1
}

# Start tmate on segfault server
start_tmate() {
    log_info "Starting tmate session on segfault server..."
    
    ssh_segfault "which tmate || (apt-get update && apt-get install -y tmate)" 2>&1
    
    # Start tmate in background
    ssh_segfault "tmux new-session -d -s sara 'tmate -S /tmp/tmate.sock' 2>&1" 2>&1
    
    # Wait for connection
    sleep 5
    
    # Get tmate session info
    local info=$(ssh_segfault "tmate -S /tmp/tmate.sock display -p '#{tmate_ssh}'" 2>&1)
    log_info "Tmate session info: $info"
}

# Test cloudflared tunnel connection
test_cloudflared() {
    log_info "Testing cloudflared tunnel to segfault server..."
    
    # Check if cloudflared is available
    if ! ssh_segfault "which cloudflared" 2>&1 | grep -q "cloudflared"; then
        log_warn "cloudflared not found, installing..."
        ssh_segfault "curl -sL https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o /usr/local/bin/cloudflared && chmod +x /usr/local/bin/cloudflared" 2>&1
    fi
    
    # Test connection
    local result=$(ssh_segfault "cloudflared --version" 2>&1)
    log_info "Cloudflared: $result"
}

# Submit report via direct HackerOne API (fallback)
submit_via_api() {
    local program="$1"
    local report_file="$2"
    
    log_info "Submitting $program via HackerOne API (fallback method)..."
    
    # This would use the HackerOne API directly
    # For now, just log the attempt
    log_warn "Direct API submission not yet implemented"
    log_info "Manual submission required at: https://hackerone.com/$program/reports/new"
}

# Main menu
show_help() {
    cat << EOF
${GREEN}SARAhack - Tmate Automation Guide${NC}

${YELLOW}ปัญหา: tmate ไม่รองรับ remote command execution${NC}
เมื่อ SSH ไปที่ tmate session จะได้ "Invalid command" เพราะ tmate เป็น
terminal sharing tool ไม่ใช่ SSH server

${GREEN}วิธีแก้ที่ถูกต้อง:${NC}
1. เชื่อมต่อ SSH ไปยัง segfault server (ที่มี tmate รันอยู่)
2. ใช้ 'tmux send-keys' เพื่อส่งคำสั่งไปยัง tmate session

${GREEN}Commands:${NC}
  test-cloudflared    - ทดสอบ cloudflared tunnel ไป segfault
  check-tmate         - ตรวจสอบ tmate status บน segfault
  start-tmate         - เริ่ม tmate session บน segfault
  send-keys <session> <cmd> - ส่ง command ไป tmate
  help                - แสดง help นี้

${GREEN}การใช้งาน:${NC}
  $0 test-cloudflared
  $0 check-tmate
  $0 send-keys 0 "freebuff --version"

${RED}หมายเหตุ:${NC}
  - ต้องมี cloudflared tunnel ไปยัง 8lgm.segfault.net
  - ต้องมี tmate/tmux session รันอยู่บน server
  - SECRET=EUwteWtAugwWBPqCIUWcuVGq ใช้สำหรับ cloudflared access
EOF
}

# Parse command
case "$1" in
    test-cloudflared)
        test_cloudflared
        ;;
    check-tmate)
        check_tmate_status
        ;;
    start-tmate)
        start_tmate
        ;;
    send-keys)
        if [[ -z "$3" ]]; then
            echo "Usage: $0 send-keys <session> <command>"
            exit 1
        fi
        tmate_send_keys "$2" "$3"
        ;;
    api|submit-api)
        if [[ -z "$2" || -z "$3" ]]; then
            echo "Usage: $0 api <program> <report_file>"
            exit 1
        fi
        submit_via_api "$2" "$3"
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        show_help
        ;;
esac