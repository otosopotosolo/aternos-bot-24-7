#!/bin/bash
# SARAhack Freebuff Integration Script
# สคริปต์สำหรับทำงานกับ freebuff AI

set -e

echo "=========================================="
echo "  SARAhack - Freebuff AI Integration"
echo "=========================================="

# Server configuration (tmate)
TMATE_HOST="lon1.tmate.io"
TMATE_USER="eS6fytCGPu74pDmMNxAKcszLc"
SSH_KEY_FILE="$HOME/.ssh/id_ed25519"

# Password authentication (optional - set password or leave empty)
USE_PASSWORD=false
TMATE_PASSWORD=""

# Colors
RED='\u001b[31m'
GREEN='\u001b[32m'
YELLOW='\u001b[33m'
NC='\u001b[0m'

log_success() { echo -e "${GREEN}[+]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[!]${NC} $1"; }
log_error() { echo -e "${RED}[-]${NC} $1"; }

# Check if sshpass is available
check_sshpass() {
    if command -v sshpass &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# Function to SSH and run freebuff command
run_freebuff() {
    local command="$1"
    local description="$2"
    
    echo ""
    log_success "$description"
    echo "[*] Running: $command"
    
    if [ "$USE_PASSWORD" = true ] && [ -n "$TMATE_PASSWORD" ]; then
        # Use password authentication with sshpass
        if check_sshpass; then
            sshpass -p "$TMATE_PASSWORD" ssh -o "StrictHostKeyChecking=no" -o "Compression=no" $TMATE_USER@$TMATE_HOST "$command"
        else
            log_warn "sshpass not installed. Installing..."
            sudo apt-get update && sudo apt-get install -y sshpass
            sshpass -p "$TMATE_PASSWORD" ssh -o "StrictHostKeyChecking=no" -o "Compression=no" $TMATE_USER@$TMATE_HOST "$command"
        fi
    else
        # Use SSH key authentication
        if [ -f "$SSH_KEY_FILE" ]; then
            ssh -o "StrictHostKeyChecking=no" -o "Compression=no" -i $SSH_KEY_FILE $TMATE_USER@$TMATE_HOST "$command"
        else
            log_error "SSH key not found at $SSH_KEY_FILE"
            log_error "Please either:"
            log_error "  1. Create SSH key: ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519"
            log_error "  2. Set USE_PASSWORD=true and TMATE_PASSWORD in this script"
            exit 1
        fi
    fi
}

# Interactive password prompt
get_password() {
    if [ "$USE_PASSWORD" = true ] && [ -z "$TMATE_PASSWORD" ]; then
        read -s -p "Enter SSH password for $TMATE_USER@$TMATE_HOST: " TMATE_PASSWORD
        echo ""
    fi
}

# Function to test SSH connection
test_connection() {
    echo ""
    log_success "Testing connection to $TMATE_USER@$TMATE_HOST..."
    
    if [ "$USE_PASSWORD" = true ] && [ -n "$TMATE_PASSWORD" ]; then
        if check_sshpass; then
            sshpass -p "$TMATE_PASSWORD" ssh -o "StrictHostKeyChecking=no" -o "ConnectTimeout=10" $TMATE_USER@$TMATE_HOST "echo 'Connection OK' && whoami && pwd"
        else
            log_warn "sshpass not installed. Installing..."
            sudo apt-get update && sudo apt-get install -y sshpass 2>/dev/null || true
            sshpass -p "$TMATE_PASSWORD" ssh -o "StrictHostKeyChecking=no" -o "ConnectTimeout=10" $TMATE_USER@$TMATE_HOST "echo 'Connection OK' && whoami && pwd"
        fi
    else
        ssh -o "StrictHostKeyChecking=no" -o "ConnectTimeout=10" -i $SSH_KEY_FILE $TMATE_USER@$TMATE_HOST "echo 'Connection OK' && whoami && pwd"
    fi
    
    if [ $? -eq 0 ]; then
        log_success "Connection successful!"
    else
        log_error "Connection failed!"
    fi
}

# Menu
show_menu() {
    echo ""
    echo "=========================================="
    echo "  SARAhack Freebuff Commands"
    echo "=========================================="
    echo ""
    echo "1. Test SSH connection"
    echo "2. Login to freebuff"
    echo "3. Submit report to HackerOne"
    echo "4. Submit report to Bugcrowd"
    echo "5. Find new bug bounty targets"
    echo "6. Research CORS vulnerabilities"
    echo "7. Test Cloudflare bypass"
    echo "8. Custom command"
    echo "9. Configure password authentication"
    echo "10. Exit"
    echo ""
}

# Main loop
while true; do
    show_menu
    read -p "Select option (1-10): " choice
    
    case $choice in
        1)
            get_password
            test_connection
            ;;
        2)
            get_password
            run_freebuff "freebuff login" "Logging into freebuff"
            ;;
        3)
            get_password
            read -p "Program name: " program
            read -p "Report file: " report_file
            run_freebuff "freebuff 'Submit CORS report to HackerOne $program using file $report_file'" "Submitting to HackerOne"
            ;;
        4)
            get_password
            read -p "Program name: " program
            read -p "Report file: " report_file
            run_freebuff "freebuff 'Submit bug report to Bugcrowd $program using file $report_file'" "Submitting to Bugcrowd"
            ;;
        5)
            get_password
            run_freebuff 'freebuff "Find new bug bounty programs with CORS vulnerabilities on HackerOne and Bugcrowd"' "Finding new targets"
            ;;
        6)
            get_password
            read -p "Target domain: " target
            run_freebuff "freebuff 'Research CORS misconfiguration on $target and provide POC'" "Researching CORS"
            ;;
        7)
            get_password
            run_freebuff 'freebuff "Test browser automation on https://hackerone.com and bypass Cloudflare Turnstile"' "Testing Cloudflare bypass"
            ;;
        8)
            get_password
            read -p "Enter custom command: " cmd
            run_freebuff "freebuff '$cmd'" "Running custom command"
            ;;
        9)
            echo ""
            echo "=========================================="
            echo "  Password Authentication Configuration"
            echo "=========================================="
            read -s -p "Enter SSH password (leave empty to cancel): " new_password
            echo ""
            if [ -n "$new_password" ]; then
                USE_PASSWORD=true
                TMATE_PASSWORD="$new_password"
                log_success "Password authentication enabled!"
            else
                USE_PASSWORD=false
                TMATE_PASSWORD=""
                log_warn "Password authentication disabled."
            fi
            ;;
        10)
            log_success "Goodbye!"
            exit 0
            ;;
        *)
            log_error "Invalid option"
            ;;
    esac
done