#!/bin/bash
# SARAhack - Daily Scheduled Scanner Setup
# Run this script on the segfault server to set up automatic daily hunting

# Don't exit on error - we want to complete as much as possible
set +e

echo "=========================================="
echo "SARAhack - Daily Scanner Setup"
echo "=========================================="

# Configuration
WORKSPACE_DIR="/home/runner/workspace"
SCANNER_DIR="$WORKSPACE_DIR/freebuff"
LOG_DIR="/var/log/sarahack"
CRON_LOG="$LOG_DIR/cron.log"

# Colors (removed - cron won't render these properly)
# Simple text instead
INFO="[*]"
OK="[✓]"
WARN="[!]"
ERROR="[✗]"

# Create directories
echo "$INFO Creating directories..."
mkdir -p "$WORKSPACE_DIR/freebuff"
mkdir -p "$WORKSPACE_DIR/reports/tracking"
mkdir -p "$LOG_DIR"

# Check Python
echo "$INFO Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "$WARN Python3 not found. Installing..."
    apt update && apt install -y python3 python3-pip
fi

python3 --version

# Install requests if needed
echo "$INFO Installing dependencies..."
pip3 install requests --break-system-packages 2>/dev/null || true

# Create scanner wrapper with logging
echo "$INFO Creating scanner wrapper..."

cat > "$SCANNER_DIR/run_scanner.sh" << 'SCRIPT'
#!/bin/bash
# SARAhack Scanner Wrapper with Logging

LOG_FILE="/var/log/sarahack/scanner_$(date +%Y%m%d_%H%M%S).log"
ERROR_LOG="/var/log/sarahack/errors_$(date +%Y%m%d).log"
WORKSPACE_DIR="/home/runner/workspace"

# Discord notification function
send_discord() {
    local message="$1"
    local webhook="${DISCORD_WEBHOOK_URL:-https://discord.com/api/webhooks/1512524218871447592/ufbSsNL_4ebXM8EMQlRyEunKg6EH_SIKVo7ulw8olRygPtgda1R4-Gji56dYt9fZR_Fe}"
    
    curl -s -X POST "$webhook" -H "Content-Type: application/json" -d "{\"content\":\"$message\"}" 2>/dev/null || true
}

# Start
echo "========================================" >> "$LOG_FILE"
echo "SARAhack Scanner Started: $(date)" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

send_discord "🔍 SARAhack Daily Scan Starting..."

cd "$WORKSPACE_DIR"

# Run scanner with all output logged
python3 freebuff/target_scanner.py >> "$LOG_FILE" 2>&1

# Check result
if [ $? -eq 0 ]; then
    echo "Scan completed successfully at $(date)" >> "$LOG_FILE"
    send_discord "✅ SARAhack Daily Scan Complete!"
else
    echo "Scan failed at $(date)" >> "$LOG_FILE"
    echo "Check logs at $LOG_FILE" >> "$ERROR_LOG"
    send_discord "❌ SARAhack Daily Scan Failed!"
fi

echo "========================================" >> "$LOG_FILE"
echo "Scan Finished: $(date)" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"
SCRIPT

chmod +x "$SCANNER_DIR/run_scanner.sh"
echo "$OK Scanner wrapper created"

# Setup Cron Job
echo "$INFO Setting up cron job..."

# Create crontab entry
CRON_ENTRY="0 2 * * * $SCANNER_DIR/run_scanner.sh >> $CRON_LOG 2>&1"

# Check if cron exists
if command -v cron &> /dev/null; then
    # Remove ONLY the specific sarahack line, not anything with "run_scanner"
    crontab -l 2>/dev/null | grep -v "/run_scanner.sh" | grep -v "sarahack-scanner" > /tmp/crontab_temp
    echo "$CRON_ENTRY" >> /tmp/crontab_temp
    crontab /tmp/crontab_temp
    rm /tmp/crontab_temp
    echo "$OK Cron job added - runs daily at 2:00 AM"
elif command -v systemd &> /dev/null; then
    # Create systemd service instead
    cat > /etc/systemd/system/sarahack-scanner.service << 'SYSTEMD'
[Unit]
Description=SARAhack Daily Bug Bounty Scanner
After=network.target

[Service]
Type=oneshot
ExecStart=/home/runner/workspace/freebuff/run_scanner.sh
User=root
StandardOutput=append:/var/log/sarahack/systemd.log
StandardError=append:/var/log/sarahack/errors.log

[Install]
WantedBy=multi-user.target
SYSTEMD

    # Create timer for daily execution
    cat > /etc/systemd/system/sarahack-scanner.timer << 'TIMER'
[Unit]
Description=SARAhack Daily Scanner Timer
After=network.target

[Timer]
OnCalendar=*-*-* 02:00:00
Persistent=true

[Install]
WantedBy=timers.target
TIMER

    systemctl daemon-reload
    systemctl enable sarahack-scanner.timer
    systemctl start sarahack-scanner.timer
    echo "$OK Systemd timer created - runs daily at 2:00 AM"
else
    echo "$WARN No cron or systemd found. Manual setup required."
    echo "Add this to your crontab (crontab -e):"
    echo "$CRON_ENTRY"
fi

# Show status
# Add log cleanup (keep last 7 days)
echo "$INFO Setting up log rotation..."
cat > /etc/logrotate.d/sarahack << 'LOGROTATE'
/var/log/sarahack/*.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
}
LOGROTATE
echo "$OK Log rotation set up (keep 7 days)"

# Show status
echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "Schedule: Daily at 2:00 AM server time"
echo "Log file: $CRON_LOG"
echo "Scanner log: /var/log/sarahack/scanner_*.log"
echo ""
echo "To check status:"
echo "  - Cron: crontab -l | grep run_scanner"
echo "  - Systemd: systemctl status sarahack-scanner.timer"
echo ""
echo "To run manually:"
echo "  $SCANNER_DIR/run_scanner.sh"
echo ""