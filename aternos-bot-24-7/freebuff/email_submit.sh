#!/bin/bash
# SARAhack - Email Report Submission via SMTP (curl)
# Works with Gmail SMTP using SSL/TLS

set -e

# Configuration
SMTP_HOST="${SMTP_HOST:-smtp.gmail.com}"
SMTP_PORT="${SMTP_PORT:-465}"
SMTP_USER="${SMTP_USER:-${HACKERONE_EMAIL}}"
SMTP_PASS="${SMTP_PASS:-#)a9By=*D#6/w9T}"
FROM_EMAIL="${FROM_EMAIL:-${HACKERONE_EMAIL}}"

# Report to submit (passed as argument)
PROGRAM="${1:-stripe}"
TO_EMAIL="${2:-security@stripe.com}"
REPORT_FILE="${3:-}"

usage() {
    echo "Usage: $0 <program> [to_email] [report_file]"
    echo ""
    echo "Examples:"
    echo "  $0 stripe security@stripe.com reports/new_stripe_cors.md"
    echo "  $0 shopify security@shopify.com reports/new_shopify_idor.md"
    echo ""
    echo "Environment variables:"
    echo "  SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS"
    echo ""
    echo "Note: Default port is 465 (implicit SSL/TLS)"
    echo "      For port 587 (STARTTLS), use: SMTP_PORT=587 SMTP_SECURITY=starttls ./email_submit.sh ..."
}

send_email_report() {
    local to_email="$1"
    local subject="$2"
    local body="$3"
    
    echo "[*] Sending email to $to_email..."
    
    # Create temporary file for email content
    EMAIL_FILE=$(mktemp)
    
    cat > "$EMAIL_FILE" << EOMAIL
From: $FROM_EMAIL
To: $to_email
Subject: $subject
Content-Type: text/plain; charset=utf-8

$body
EOMAIL

    # Determine security protocol based on port
    if [ "$SMTP_PORT" = "465" ]; then
        # Port 465 uses implicit SSL/TLS from start
        SMTP_URL="smtps://$SMTP_HOST:$SMTP_PORT"
    else
        # Port 587 uses STARTTLS upgrade
        SMTP_URL="smtp://$SMTP_HOST:$SMTP_PORT"
    fi
    
    echo "[*] Connecting to $SMTP_URL"
    
    # Send via curl SMTP
    # For smtps:// (port 465): SSL from start
    # For smtp:// (port 587): use --starttls
    if [ "$SMTP_PORT" = "465" ]; then
        response=$(curl -s --max-time 60 "$SMTP_URL" -u "$SMTP_USER:$SMTP_PASS" --mail-from "$FROM_EMAIL" --mail-rcpt "$to_email" --upload-file "$EMAIL_FILE" 2>&1)
    else
        response=$(curl -s --max-time 60 "$SMTP_URL" -u "$SMTP_USER:$SMTP_PASS" --mail-from "$FROM_EMAIL" --mail-rcpt "$to_email" --upload-file "$EMAIL_FILE" --starttls 2>&1)
    fi
    
    exit_code=$?
    
    # Clean up
    rm -f "$EMAIL_FILE"
    
    # Check response
    if [ $exit_code -eq 0 ]; then
        echo "[+] Email sent successfully!"
        return 0
    else
        echo "[-] Failed to send email (exit code: $exit_code)"
        echo "[-] Response: $response"
        return 1
    fi
}

# Main
if [ "$PROGRAM" == "--help" ] || [ "$PROGRAM" == "-h" ]; then
    usage
    exit 0
fi

if [ -z "$REPORT_FILE" ]; then
    echo "[-] Error: Report file is required"
    usage
    exit 1
fi

if [ ! -f "$REPORT_FILE" ]; then
    echo "[-] Error: Report file not found: $REPORT_FILE"
    exit 1
fi

# Read report content
REPORT_CONTENT=$(cat "$REPORT_FILE")

# Create email subject based on report
SUBJECT="[Bug Bounty Report] $PROGRAM vulnerability report"

echo "[*] Email Report Submission"
echo "  Program: $PROGRAM"
echo "  To: $TO_EMAIL"
echo "  Report: $REPORT_FILE"
echo ""

# Send email
if send_email_report "$TO_EMAIL" "$SUBJECT" "$REPORT_CONTENT"; then
    echo ""
    echo "[+] SUCCESS! Report submitted via email"
else
    echo ""
    echo "[-] FAILED to send email"
    exit 1
fi