#!/bin/bash
# SARAhack - Auto send pending reports to Discord
# ส่ง report .md files ไป Discord เพื่อให้ user copy ไป submit เอง

DISCORD_WEBHOOK="https://discord.com/api/webhooks/1512524218871447592/ufbSsNL_4ebXM8EMQlRyEunKg6EH_SIKVo7ulw8olRygPtgda1R4-Gji56dYt9fZR_Fe"
TRACKER_FILE="reports/tracking/reports.json"

usage() {
    echo "SARAhack - Discord Report Sender"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --list        แสดง reports ที่รอส่ง"
    echo "  --all         ส่งทุก report ที่ pending ไป Discord"
    echo "  --id N        ส่งเฉพาะ report ID N"
    echo "  --help        แสดง help"
    echo ""
    echo "Examples:"
    echo "  $0 --list                    # ดู reports ที่รอส่ง"
    echo "  $0 --all                     # ส่งทุก report ไป Discord"
    echo "  $0 --id 24                   # ส่งแค่ report ID 24"
}

list_reports() {
    echo "=== Reports ที่รอส่งไป Discord ==="
    echo ""
    
    node -e "
const fs = require('fs');
const data = JSON.parse(fs.readFileSync('${TRACKER_FILE}', 'utf8'));
const pending = data.filter(r => r.status === 'pending' || r.status === 'new');

if (pending.length === 0) {
    console.log('ไม่มี report ที่รอส่ง');
} else {
    pending.forEach(r => {
        console.log('ID ' + r.id + ': ' + r.program.toUpperCase() + ' | ' + r.vulnerability + ' | ' + r.severity + ' | ' + r.report_file);
    });
    console.log('');
    console.log('Total: ' + pending.length + ' reports');
}
"
}

send_to_discord() {
    local id="$1"
    local program="$2"
    local vuln="$3"
    local severity="$4"
    local file="$5"
    
    # สีตาม severity
    case "$severity" in
        critical) color=15158332 ;;
        high) color=15105570 ;;
        medium) color=16776960 ;;
        low) color=3066993 ;;
        informational) color=7506394 ;;
        *) color=0 ;;
    esac
    
    # อ่าน report content
    local content=""
    if [ -f "$file" ]; then
        content=$(head -60 "$file" | grep -A10 "## Summary" | head -15 | tr '\n' ' ' | cut -c1-600)
    else
        content="Report file not found: $file"
    fi
    
    # สร้าง JSON payload
    local payload=$(cat <<JSONPAYLOAD
{
    "username": "SARAhack Reports",
    "embeds": [{
        "title": "📋 Report #$id: $program - $vuln",
        "color": $color,
        "fields": [
            {"name": "Severity", "value": "$severity", "inline": true},
            {"name": "Program", "value": "$program", "inline": true},
            {"name": "Vuln Type", "value": "$vuln", "inline": true}
        ],
        "description": "${content}...\n\n📁 File: \\`$file\\`\n\n🔗 Submit: https://hackerone.com/$program/reports/new",
        "footer": {"text": "SARAhack v1.0 - กด Submit เองที่ browser | #$id"}
    }]
}
JSONPAYLOAD
)
    
    # ส่งไป Discord
    curl -s -X POST "$DISCORD_WEBHOOK" -H "Content-Type: application/json" -d "$payload" > /dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        echo "[✓] Report #$id ($program $vuln) ส่งแล้ว!"
        return 0
    else
        echo "[✗] Report #$id ส่งไม่ได้"
        return 1
    fi
}

send_all() {
    echo "=== กำลังส่ง Reports ไป Discord ==="
    echo ""
    
    local count=0
    local success=0
    
    # อ่าน pending reports และส่งทีละตัว
    node -e "
const fs = require('fs');
const data = JSON.parse(fs.readFileSync('${TRACKER_FILE}', 'utf8'));
const pending = data.filter(r => r.status === 'pending' || r.status === 'new');

pending.forEach((r, i) => {
    console.log(r.id + '|' + r.program + '|' + r.vulnerability + '|' + r.severity + '|' + r.report_file);
});
" | while IFS='|' read -r id program vuln severity file; do
        
        send_to_discord "$id" "$program" "$vuln" "$severity" "$file"
        count=$((count + 1))
        sleep 2  # delay ระหว่าง report
        
    done
    
    echo ""
    echo "=== เสร็จสิ้น! ส่ง $count reports ไป Discord ==="
}

send_single() {
    local target_id="$1"
    
    echo "[*] กำลังส่ง Report #$target_id..."
    
    # หา report จาก tracker
    local result=$(node -e "
const fs = require('fs');
const data = JSON.parse(fs.readFileSync('${TRACKER_FILE}', 'utf8'));
const r = data.find(x => x.id === ${target_id});
if (r) {
    console.log(r.id + '|' + r.program + '|' + r.vulnerability + '|' + r.severity + '|' + r.report_file);
} else {
    console.log('NOT_FOUND');
}
")
    
    if [ "$result" = "NOT_FOUND" ]; then
        echo "[✗] Report #$target_id ไม่พบใน tracker"
        exit 1
    fi
    
    IFS='|' read -r id program vuln severity file <<< "$result"
    
    send_to_discord "$id" "$program" "$vuln" "$severity" "$file"
}

# Main
case "${1:-}" in
    --list|-l)
        list_reports
        ;;
    --all|-a)
        send_all
        ;;
    --id|-i)
        if [ -z "$2" ]; then
            echo "[✗] ต้องระบุ report ID"
            echo "Usage: $0 --id 24"
            exit 1
        fi
        send_single "$2"
        ;;
    --help|-h)
        usage
        ;;
    *)
        usage
        echo ""
        echo "ตัวอย่าง:"
        echo "  $0 --list          # ดู reports ที่รอ"
        echo "  $0 --all           # ส่งทุก report ไป Discord"
        echo "  $0 --id 24         # ส่งแค่ report ID 24"
        ;;
esac