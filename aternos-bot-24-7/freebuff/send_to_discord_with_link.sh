#!/bin/bash
# SARAhack - Upload report to tmpfiles.org and send link to Discord
# ส่ง report ไป Discord พร้อมลิงค์ download

DISCORD_WEBHOOK="https://discord.com/api/webhooks/1512524218871447592/ufbSsNL_4ebXM8EMQlRyEunKg6EH_SIKVo7ulw8olRygPtgda1R4-Gji56dYt9fZR_Fe"
TRACKER_FILE="reports/tracking/reports.json"

usage() {
    echo "SARAhack - Upload & Send to Discord"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --all         อัพโหลดทั้งหมดและส่งลิงค์ไป Discord"
    echo "  --id N        อัพโหลดเฉพาะ report ID N"
    echo "  --list        แสดง reports ที่รอส่ง"
    echo ""
    echo "Examples:"
    echo "  $0 --all                     # อัพโหลดทั้งหมด + ส่ง Discord"
    echo "  $0 --id 24                   # อัพโหลด ID 24 + ส่ง Discord"
}

# อัพโหลดไป tmpfiles.org
upload_to_tmpfiles() {
    local file="$1"
    local filename=$(basename "$file")
    
    if [ ! -f "$file" ]; then
        echo "File not found: $file"
        return 1
    fi
    
    # Copy เป็น .txt (tmpfiles.org รองรับ)
    local txt_file="/tmp/sarahack_${filename}.txt"
    cp "$file" "$txt_file"
    
    # อัพโหลด
    local result=$(curl -s --max-time 60 -F "file=@${txt_file}" "https://tmpfiles.org/api/v1/upload")
    local url=$(echo "$result" | node -e "
        try {
            const d = JSON.parse(require('fs').readFileSync('/dev/stdin', 'utf8'));
            console.log(d.status === 'success' ? d.data.url : 'FAILED');
        } catch(e) {
            console.log('FAILED');
        }
    ")
    
    # ลบ temp file
    rm -f "$txt_file"
    
    echo "$url"
}

# ส่งไป Discord พร้อมลิงค์
send_to_discord() {
    local id="$1"
    local program="$2"
    local vuln="$3"
    local severity="$4"
    local file="$5"
    local download_url="$6"
    
    # สีตาม severity
    case "$severity" in
        critical) color=15158332 ;;
        high) color=15105570 ;;
        medium) color=16776960 ;;
        low) color=3066993 ;;
        informational) color=7506394 ;;
        *) color=0 ;;
    esac
    
    # สร้าง JSON payload พร้อมลิงค์ clickable ใน description
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
        "description": "🎯 **Download Report:** [$program $vuln]($download_url)\n\n📁 **Submit:** https://hackerone.com/$program/reports/new",
        "footer": {"text": "SARAhack v1.0 | #$id | Permanent link"}
    }]
}
JSONPAYLOAD
)
    
    # ส่งไป Discord
    curl -s -X POST "$DISCORD_WEBHOOK" -H "Content-Type: application/json" -d "$payload" > /dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        echo "[✓] Report #$id - Uploaded & Sent! URL: $download_url"
        return 0
    else
        echo "[✗] Report #$id - Failed to send"
        return 1
    fi
}

send_all() {
    echo "=== กำลังอัพโหลด & ส่ง Reports ไป Discord ==="
    echo ""
    
    local count=0
    local success=0
    local failed=0
    
    node -e "
const fs = require('fs');
const data = JSON.parse(fs.readFileSync('${TRACKER_FILE}', 'utf8'));
const pending = data.filter(r => r.status === 'pending' || r.status === 'new');

pending.forEach((r, i) => {
    console.log(r.id + '|' + r.program + '|' + r.vulnerability + '|' + r.severity + '|' + r.report_file);
});
" | while IFS='|' read -r id program vuln severity file; do
        
        echo "[$count] Processing: $program - $vuln"
        
        # อัพโหลดก่อน
        local url=$(upload_to_tmpfiles "$file")
        
        if [ "$url" != "FAILED" ] && [ -n "$url" ]; then
            # ส่งไป Discord พร้อมลิงค์
            send_to_discord "$id" "$program" "$vuln" "$severity" "$file" "$url"
            success=$((success + 1))
        else
            echo "[✗] Report #$id - Upload failed"
            failed=$((failed + 1))
        fi
        
        count=$((count + 1))
        sleep 3
        
    done
    
    echo ""
    echo "=== เสร็จสิ้น! ส่งสำเร็จ: $success | ล้มเหลว: $failed ==="
}

send_single() {
    local target_id="$1"
    
    echo "[*] Processing Report #$target_id..."
    
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
    
    echo "Uploading: $file"
    local url=$(upload_to_tmpfiles "$file")
    
    if [ "$url" != "FAILED" ] && [ -n "$url" ]; then
        send_to_discord "$id" "$program" "$vuln" "$severity" "$file" "$url"
    else
        echo "[✗] Upload failed"
        exit 1
    fi
}

list_reports() {
    echo "=== Reports ที่รออัพโหลด & ส่ง ==="
    echo ""
    node -e "
const fs = require('fs');
const data = JSON.parse(fs.readFileSync('${TRACKER_FILE}', 'utf8'));
const pending = data.filter(r => r.status === 'pending' || r.status === 'new');
pending.forEach(r => {
    console.log('ID ' + r.id + ': ' + r.program.toUpperCase() + ' | ' + r.vulnerability + ' | ' + r.severity);
});
console.log('');
console.log('Total: ' + pending.length + ' reports');
"
}

case "${1:-}" in
    --all|-a)
        send_all
        ;;
    --id|-i)
        if [ -z "$2" ]; then
            echo "[✗] ต้องระบุ report ID"
            exit 1
        fi
        send_single "$2"
        ;;
    --list|-l)
        list_reports
        ;;
    *)
        usage
        ;;
esac