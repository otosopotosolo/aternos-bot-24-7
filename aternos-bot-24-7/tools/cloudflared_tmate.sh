#!/bin/bash
#
# SARAhack - Cloudflared Tunnel + Tmate Automation
# Uses cloudflared access with service token authentication
#

set -e

# Configuration
SEGFAULT_HOST="8lgm.segfault.net"
SERVICE_TOKEN_ID="eS6fytCGPu74pDmMNxAKcszLc"
SERVICE_TOKEN_SECRET="EUwteWtAugwWBPqCIUWcuVGq"

# Colors
GREEN='\uff1b[32m'
YELLOW='\uff1b[33m'
RED='\uff1b[31m'
NC='\uff1b[0m'

log_info() { echo -e "${GREEN}[*] $1${NC}"; }
log_warn() { echo -e "${YELLOW}[!] $1${NC}"; }
log_error() { echo -e "${RED}[x] $1${NC}"; }

# Check if cloudflared is available
check_cloudflared() {
    if [[ -x /tmp/cloudflared ]]; then
        log_info "cloudflared found: $(/tmp/cloudflared --version)"
        return 0
    fi
    
    log_info "Installing cloudflared..."
    curl -sL https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o /tmp/cloudflared
    chmod +x /tmp/cloudflared
    log_info "cloudflared installed"
}

# Test cloudflared tunnel connection
test_tunnel() {
    log_info "Testing cloudflared tunnel to $SEGFAULT_HOST..."
    
    check_cloudflared
    
    # Use service token authentication
    log_info "Authenticating with service token..."
    
    # Try with service token flags
    /tmp/cloudflared access ssh --hostname "$SEGFAULT_HOST" --service-token-id "$SERVICE_TOKEN_ID" --service-token-secret "$SERVICE_TOKEN_SECRET" "echo 'Tunnel connected!' && uptime 2>&1 | head -3" 2>&1
}

# Execute command via cloudflared tunnel
# cloudflared access ssh creates a TCP proxy, we then SSH through it
exec_via_tunnel() {
    local cmd="$1"
    log_info "Executing via cloudflared tunnel: $cmd"
    
    # Method: Start cloudflared tunnel in background, then SSH through it
    local tunnel_port=2022
    
    # Kill any existing tunnel on this port
    pkill -f "cloudflared.*--destination" 2>/dev/null || true
    
    # Start cloudflared tunnel in background
    log_info "Starting cloudflared tunnel..."
    nohup /tmp/cloudflared access ssh \
        --hostname "$SEGFAULT_HOST" \
        --service-token-id "$SERVICE_TOKEN_ID" \
        --service-token-secret "$SERVICE_TOKEN_SECRET" \
        --url "localhost:$tunnel_port" \
        > /tmp/cloudflared.log 2>&1 &
    
    local tunnel_pid=$!
    sleep 5
    
    # Check if tunnel started
    if ! kill -0 $tunnel_pid 2>/dev/null; then
        log_error "Cloudflared tunnel failed to start"
        cat /tmp/cloudflared.log
        return 1
    fi
    
    # SSH through the tunnel
    log_info "SSH through tunnel..."
    ssh -o "StrictHostKeyChecking=no" \
        -o "ConnectTimeout=10" \
        -p $tunnel_port \
        root@localhost "$cmd" 2>&1
    
    # Cleanup
    kill $tunnel_pid 2>/dev/null || true
}

# Setup tmate on segfault server
setup_tmate() {
    log_info "Setting up tmate on segfault server..."
    
    # First check what's available
    exec_via_tunnel "which tmate tmux python3 node 2>/dev/null || echo 'Checking installed packages...'; uname -a"
}

# Send command to tmate session
tmate_send() {
    local session="${1:-0}"
    local cmd="$2"
    log_info "Sending to tmate session $session: $cmd"
    
    exec_via_tunnel "tmux send-keys -t $session '$cmd' Enter"
}

# Run freebuff via tunnel
run_freebuff() {
    local prompt="$1"
    local timeout="${2:-120}"
    
    log_info "Running freebuff via cloudflared tunnel..."
    log_info "Prompt: ${prompt:0:100}..."
    
    # Create a temp script to avoid escaping issues
    local temp_script=$(mktemp)
    cat > "$temp_script" << 'SCRIPT'
#!/bin/bash
export PATH=$PATH:/usr/local/bin:/usr/bin
freebuff "SCRIPT_PLACEHOLDER"
SCRIPT

    # Replace placeholder
    sed -i "s|SCRIPT_PLACEHOLDER|${prompt//\"/\\\"}|g" "$temp_script"
    
    # Execute via tunnel
    exec_via_tunnel "bash /tmp/tmate_send.sh" 2>&1
    
    rm -f "$temp_script"
}

# Submit report via freebuff
submit_report() {
    local program="$1"
    local report_file="$2"
    
    log_info "Submitting $program report via freebuff..."
    
    # Load report content
    if [[ ! -f "$report_file" ]]; then
        report_file="reports/drafts/draft_${program}_cors.md"
    fi
    
    if [[ ! -f "$report_file" ]]; then
        log_error "Report not found: $report_file"
        return 1
    fi
    
    # Extract info from report
    local title=$(grep -m1 "^# " "$report_file" | sed 's/^# //' || echo "$program CORS")
    
    # Build prompt
    local prompt="Navigate to https://hackerone.com/$program/reports/new
Login with potsopotosolo@gmail.com and password )a9By=*D#6/w9T
Fill and submit bug report:
- Title: $title
- Severity: HIGH
- Description: CORS misconfiguration found allowing cross-origin access with credentials

Take screenshot and confirm success."
    
    run_freebuff "$prompt" 300
}

# Main
case "$1" in
    test)
        test_tunnel
        ;;
    setup)
        setup_tmate
        ;;
    exec)
        if [[ -z "$2" ]]; then
            echo "Usage: $0 exec \"command\""
            exit 1
        fi
        exec_via_tunnel "$2"
        ;;
    tmate-send)
        if [[ -z "$3" ]]; then
            echo "Usage: $0 tmate-send <session> <command>"
            exit 1
        fi
        tmate_send "$2" "$3"
        ;;
    freebuff)
        if [[ -z "$2" ]]; then
            echo "Usage: $0 freebuff \"prompt\" [timeout]"
            exit 1
        fi
        run_freebuff "$2" "${3:-120}"
        ;;
    submit)
        if [[ -z "$2" || -z "$3" ]]; then
            echo "Usage: $0 submit <program> <report_file>"
            exit 1
        fi
        submit_report "$2" "$3"
        ;;
    help|--help)
        cat << EOF
${GREEN}SARAhack - Cloudflared Tunnel + Tmate Automation${NC}

Usage:
  $0 test              - Test cloudflared tunnel connection
  $0 setup             - Setup tmate on segfault server
  $0 exec <cmd>        - Execute command via tunnel
  $0 tmate-send <s> <c> - Send command to tmate session
  $0 freebuff <prompt> - Run freebuff command via tunnel
  $0 submit <prog> <f> - Submit report via freebuff

Examples:
  $0 test
  $0 exec "freebuff --version"
  $0 freebuff "navigate to hackerone.com" 180
  $0 submit rollbar reports/drafts/draft_rollbar_cors.md
EOF
        ;;
    *)
        $0 help
        ;;
esac