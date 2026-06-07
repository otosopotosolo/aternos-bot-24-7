#!/bin/bash
#
# SARAhack - Tmate Session Automation using pure Bash
# Uses bash's built-in /dev/tcp and here-documents to automate tmate sessions
#
# Usage:
#   ./tmate_bash_auto.sh test
#   ./tmate_bash_auto.sh send "echo test"
#   ./tmate_bash_auto.sh freebuff "navigate to hackerone.com"
#   ./tmate_bash_auto.sh submit rollbar reports/drafts/draft_rollbar_cors.md
#

set -e

# Configuration
TMATE_HOST="lon1.tmate.io"
TMATE_USER="eS6fytCGPu74pDmMNxAKcszLc"
SECRET="EUwteWtAugwWBPqCIUWcuVGq"
TIMEOUT=60

# Colors
RED='\n\uff1b[31m'
GREEN='\n\uff1b[32m'
YELLOW='\n\uff1b[33m'
NC='\uff1b[0m'

log_info() { echo -e "${GREEN}[*] $1${NC}"; }
log_warn() { echo -e "${YELLOW}[!] $1${NC}"; }
log_error() { echo -e "${RED}[x] $1${NC}"; }

# Test SSH connection
test_connection() {
    log_info "Testing SSH connection to tmate..."
    
    # Use expect-like approach with expect library if available
    if command -v expect &>/dev/null; then
        expect -c "
            spawn ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=60 -tt $TMATE_USER@$TMATE_HOST
            set timeout 30
            expect {
                \"Last login:\" { send \"echo Connection OK\\r\"; exp_continue }
                \"password:\" { send \"$SECRET\\r\"; exp_continue }
                timeout { puts \"TIMEOUT\"; exit 1 }
            }
            expect eof
        "
        return $?
    fi
    
    # Fallback: direct SSH with timeout
    log_warn "expect not found, trying direct SSH..."
    timeout $TIMEOUT ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=60 -tt $TMATE_USER@$TMATE_HOST "echo 'Connected'; exit" 2>&1 || {
        log_error "SSH connection failed"
        return 1
    }
}

# Send command to tmate
send_command() {
    local cmd="$1"
    log_info "Sending: $cmd"
    
    if command -v expect &>/dev/null; then
        expect -c "
            spawn ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=60 -tt $TMATE_USER@$TMATE_HOST
            set timeout 30
            expect {
                \"Last login:\" { send \"$cmd\\r\" }
                \"password:\" { send \"$SECRET\\r\"; exp_continue }
                timeout { puts \"TIMEOUT\" }
            }
            expect eof
        " 2>&1
    else
        timeout $TIMEOUT ssh -o StrictHostKeyChecking=no -tt $TMATE_USER@$TMATE_HOST "$cmd" 2>&1 || true
    fi
}

# Send to freebuff
send_freebuff() {
    local prompt="$1"
    local wait_time="${2:-120}"
    log_info "Sending to freebuff (timeout: ${wait_time}s)..."
    
    # Escape prompt for shell
    local escaped_prompt=$(echo "$prompt" | sed 's/"/\\"/g' | sed 's/\"/\\"/g')
    
    if command -v expect &>/dev/null; then
        expect -c "
            spawn ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=60 -tt $TMATE_USER@$TMATE_HOST
            set timeout $wait_time
            
            expect {
                \"Last login:\" { 
                    send \"freebuff \\\"$escaped_prompt\\\"\\r\"
                }
                \"password:\" { 
                    send \"$SECRET\\r\"
                    exp_continue 
                }
                timeout { 
                    puts \"TIMEOUT\"
                    exit 1
                }
            }
            
            expect eof
        " 2>&1
    else
        log_warn "expect not available, cannot run freebuff"
        return 1
    fi
}

# Submit report via freebuff
submit_report() {
    local program="$1"
    local report_file="$2"
    
    log_info "Submitting $program report via freebuff..."
    
    if [[ ! -f "$report_file" ]]; then
        report_file="reports/drafts/draft_${program}_cors.md"
    fi
    
    if [[ ! -f "$report_file" ]]; then
        log_error "Report file not found: $report_file"
        return 1
    fi
    
    # Extract title from report
    local title=$(grep -m1 "^# " "$report_file" | sed 's/^# //' || echo "$program - CORS Misconfiguration")
    
    # Build prompt
    local prompt="Navigate to https://hackerone.com/$program/reports/new
Login with email potsopotosolo@gmail.com and password )a9By=*D#6/w9T
Submit a bug report with:
- Title: $title
- Severity: HIGH
- Description: CORS misconfiguration found in $program API allowing credentials to be sent to unauthorized origins. An attacker can steal sensitive data by making cross-origin requests from a malicious page.

Take screenshot after submission and confirm success."
    
    send_freebuff "$prompt" 300
}

# Main
case "$1" in
    test)
        test_connection
        ;;
    send)
        if [[ -z "$2" ]]; then
            echo "Usage: $0 send \"command\""
            exit 1
        fi
        send_command "$2"
        ;;
    freebuff)
        if [[ -z "$2" ]]; then
            echo "Usage: $0 freebuff \"prompt\""
            exit 1
        fi
        send_freebuff "$2" "${3:-120}"
        ;;
    submit)
        if [[ -z "$2" || -z "$3" ]]; then
            echo "Usage: $0 submit <program> <report_file>"
            exit 1
        fi
        submit_report "$2" "$3"
        ;;
    list)
        log_info "Draft reports:"
        ls -1 reports/drafts/draft_*_cors.md 2>/dev/null | head -20
        ;;
    *)
        echo "Usage: $0 <command> [args]"
        echo ""
        echo "Commands:"
        echo "  test              - Test tmate SSH connection"
        echo "  send \"cmd\"        - Send command to tmate"
        echo "  freebuff \"prompt\" - Send prompt to freebuff (optional timeout in seconds)"
        echo "  submit <prog> <f> - Submit report via freebuff"
        echo "  list              - List draft reports"
        echo ""
        echo "Examples:"
        echo "  $0 test"
        echo "  $0 send \"freebuff --version\""
        echo "  $0 freebuff \"navigate to hackerone.com\" 180"
        echo "  $0 submit rollbar reports/drafts/draft_rollbar_cors.md"
        exit 1
        ;;
esac