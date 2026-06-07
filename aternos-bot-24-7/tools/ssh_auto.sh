#!/bin/bash
# SARAhack - SSH Automation Script
# ใช้ sshpass สำหรับ SSH ไป server โดยไม่ต้องพิมพ์ password

set -e

# ============== CONFIGURATION ==============
# Server Configuration
SERVER="${SSH_SERVER:-8lgm.segfault.net}"
SECRET="${SECRET:-JEpUOZPOVhCTwdhQInbJTtNA}"
PASSWORD="${SSH_PASSWORD:-segfault}"
SSH_OPTS="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ServerAliveInterval=60"

# Check dependencies
if ! command -v sshpass &> /dev/null; then
    echo "[-] sshpass is not installed. Please install it first:"
    echo "    nix-env -iA nixpkgs.sshpass"
    echo "    or: sudo apt install sshpass"
    exit 1
fi

# ============== COLORS ==============
RED='\u001b[31m'
GREEN='\u001b[32m'
YELLOW='\u001b[33m'
BLUE='\u001b[34m'
NC='\u001b[0m'

log_info() { echo -e "${BLUE}[*]${NC} $1"; }
log_success() { echo -e "${GREEN}[+]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[!]${NC} $1"; }
log_error() { echo -e "${RED}[-]${NC} $1"; }

# ============== SSH FUNCTIONS ==============

# SSH to server and run command
ssh_run() {
    local cmd="$1"
    local description="${2:-Running command}"
    
    log_info "$description"
    sshpass -p "$PASSWORD" ssh $SSH_OPTS -o "SetEnv=SECRET=$SECRET" "root@$SERVER" "$cmd" 2>/dev/null
}

# SCP file to server
scp_to_server() {
    local local_file="$1"
    local remote_path="$2"
    local description="${3:-Copying file}"
    
    log_info "$description"
    sshpass -p "$PASSWORD" scp $SSH_OPTS -o "SetEnv=SECRET=$SECRET" "$local_file" "root@$SERVER:$remote_path" 2>/dev/null
    log_success "Copied to $remote_path"
}

# SCP file from server
scp_from_server() {
    local remote_file="$1"
    local local_path="$2"
    local description="${3:-Downloading file}"
    
    log_info "$description"
    sshpass -p "$PASSWORD" scp $SSH_OPTS -o "SetEnv=SECRET=$SECRET" "root@$SERVER:$remote_file" "$local_path" 2>/dev/null
    log_success "Downloaded to $local_path"
}

# ============== COMMANDS ==============

# Test connection
test_connection() {
    echo "=========================================="
    echo "  SARAhack SSH Connection Test"
    echo "=========================================="
    
    log_info "Testing connection to $SERVER..."
    
    result=$(sshpass -p "$PASSWORD" ssh $SSH_OPTS -o "SetEnv=SECRET=$SECRET" "root@$SERVER" "echo OK" 2>/dev/null)
    
    if [ "$result" = "OK" ]; then
        log_success "Connection successful!"
        ssh_run "uptime && free -h" "Server status"
        return 0
    else
        log_error "Connection failed!"
        return 1
    fi
}

# Interactive SSH session
ssh_shell() {
    echo "=========================================="
    echo "  Opening SSH shell to $SERVER"
    echo "=========================================="
    echo "Type 'exit' to return"
    echo ""
    
    sshpass -p "$PASSWORD" ssh $SSH_OPTS -o "SetEnv=SECRET=$SECRET" "root@$SERVER"
}

# Run freebuff command
ssh_freebuff() {
    local command="$1"
    
    echo "=========================================="
    echo "  Running freebuff command"
    echo "=========================================="
    echo "Command: $command"
    echo ""
    
    ssh_run "freebuff '$command'" "Executing freebuff"
}

# Setup project on server
ssh_setup_project() {
    echo "=========================================="
    echo "  Setting up SARAhack project on server"
    echo "=========================================="
    
    # Create directory structure
    ssh_run "mkdir -p sarahack/{tools,scripts,reports/{templates,drafts,submitted,tracking},config/credentials,knowledge/{vulnerabilities,poc},freebuff,wordlists}" "Creating directories"
    
    # Copy project files
    log_info "Copying project files..."
    
    scp_to_server "/home/runner/workspace/SARAhack.md" "/root/sarahack/" "Copying SARAhack.md"
    scp_to_server "/home/runner/workspace/REOPLAN.md" "/root/sarahack/" "Copying REOPLAN.md"
    scp_to_server "/home/runner/workspace/pentest-book.md" "/root/sarahack/" "Copying pentest-book.md"
    scp_to_server "/home/runner/workspace/tools/tracker.py" "/root/sarahack/tools/" "Copying tracker.py"
    scp_to_server "/home/runner/workspace/scripts/"*.sh "/root/sarahack/scripts/" "Copying scripts"
    scp_to_server "/home/runner/workspace/freebuff/"*.sh "/root/sarahack/freebuff/" "Copying freebuff scripts"
    scp_to_server "/home/runner/workspace/freebuff/"*.py "/root/sarahack/freebuff/" "Copying freebuff scripts"
    scp_to_server "/home/runner/workspace/reports/templates/"*.md "/root/sarahack/reports/templates/" "Copying report templates"
    
    log_success "Project files copied!"
    
    # Make scripts executable
    ssh_run "chmod +x /root/sarahack/tools/*.sh /root/sarahack/scripts/*.sh /root/sarahack/freebuff/*.sh 2>/dev/null; echo 'Permissions set'" "Setting permissions"
}

# Run reconnaissance
ssh_recon() {
    local target="$1"
    local wordlist="${2:-wordlists/seclists/discovery/dns/subdomains-top1million-5000.txt}"
    
    echo "=========================================="
    echo "  Running Recon on $target"
    echo "=========================================="
    
    ssh_run "export PATH=\\$PATH:\\$HOME/go/bin && amass enum -passive -d $target -o /tmp/amass_$target.txt 2>&1 | tail -5" "Running Amass"
    ssh_run "export PATH=\\$PATH:\\$HOME/go/bin && subfinder -d $target -silent -o /tmp/subfinder_$target.txt 2>&1 | tail -5" "Running Subfinder"
    ssh_run "cat /tmp/amass_$target.txt /tmp/subfinder_$target.txt 2>/dev/null | sort -u > /tmp/all_subdomains_$target.txt && wc -l /tmp/all_subdomains_$target.txt" "Combining results"
    
    log_success "Recon complete for $target"
    log_info "Results saved to /tmp/all_subdomains_$target.txt"
}

# ============== MENU ==============

show_menu() {
    echo ""
    echo "=========================================="
    echo "  SARAhack SSH Automation Menu"
    echo "=========================================="
    echo ""
    echo "  1. Test connection"
    echo "  2. Open SSH shell (interactive)"
    echo "  3. Setup project on server"
    echo "  4. Run freebuff command"
    echo "  5. Run reconnaissance on target"
    echo "  6. Copy file to server"
    echo "  7. Download file from server"
    echo "  8. Check server status"
    echo "  9. Exit"
    echo ""
}

# ============== MAIN ==============

if [ $# -gt 0 ]; then
    # Command line mode
    case "$1" in
        test)
            test_connection
            ;;
        shell)
            ssh_shell
            ;;
        setup)
            ssh_setup_project
            ;;
        freebuff)
            shift
            ssh_freebuff "$*"
            ;;
        recon)
            shift
            ssh_recon "$1" "$2"
            ;;
        status)
            ssh_run "uptime && free -h && df -h" "Server status"
            ;;
        *)
            echo "Usage: $0 {test|shell|setup|freebuff|recon|status} [args]"
            ;;
    esac
else
    # Interactive menu mode
    while true; do
        show_menu
        read -p "Select option (1-9): " choice
        
        case $choice in
            1) test_connection ;;
            2) ssh_shell ;;
            3) ssh_setup_project ;;
            4)
                read -p "Enter freebuff command: " cmd
                ssh_freebuff "$cmd"
                ;;
            5)
                read -p "Enter target domain: " target
                ssh_recon "$target"
                ;;
            6)
                read -p "Local file: " local_file
                read -p "Remote path: " remote_path
                if [ -f "$local_file" ]; then
                    scp_to_server "$local_file" "$remote_path" "Copying file"
                else
                    log_error "Local file not found: $local_file"
                fi
                ;;
            7)
                read -p "Remote file: " remote_file
                read -p "Local path: " local_path
                scp_from_server "$remote_file" "$local_path" "Downloading file"
                ;;
            8) ssh_run "uptime && free -h && df -h" "Server status" ;;
            9) log_success "Goodbye!"; exit 0 ;;
            *) log_error "Invalid option" ;;
        esac
        
        echo ""
        read -p "Press Enter to continue..."
    done
fi