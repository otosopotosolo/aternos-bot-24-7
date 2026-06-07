#!/usr/bin/env python3
"""
Discord Notifier for Bug Bounty Reports
Sends findings to Discord webhook after each hunt completion
"""

import os
import sys
import json
import requests
from datetime import datetime
from pathlib import Path

# Discord webhook - loaded from environment for security
DISCORD_WEBHOOK_URL = os.environ.get(
    "DISCORD_WEBHOOK_URL",
    "https://discord.com/api/webhooks/1512524218871447592/ufbSsNL_4ebXM8EMQlRyEunKg6EH_SIKVo7ulw8olRygPtgda1R4-Gji56dYt9fZR_Fe"
)

def send_discord_embed(title, description, color=0x00ff00, fields=None, footer=None):
    """Send embedded message to Discord"""
    embed = {
        "title": title,
        "description": description,
        "color": color,
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    if fields:
        embed["fields"] = fields
    
    if footer:
        embed["footer"] = {"text": footer}
    
    payload = {
        "embeds": [embed],
        "username": "SARAhack Bot"
    }
    
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        if response.status_code == 204:
            print(f"[✓] Discord notification sent: {title}")
            return True
        else:
            print(f"[✗] Discord notification failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"[✗] Discord error: {e}")
        return False

def notify_finding(program, vulnerability_type, severity, bounty_range, description, poc=None):
    """Send finding notification to Discord"""
    
    # Color based on severity
    severity_colors = {
        "critical": 0xff0000,
        "high": 0xff8800,
        "medium": 0xffff00,
        "low": 0x00ff00,
        "informational": 0x888888
    }
    color = severity_colors.get(severity.lower(), 0x00ff00)
    
    fields = [
        {"name": "Program", "value": program, "inline": True},
        {"name": "Vulnerability", "value": vulnerability_type, "inline": True},
        {"name": "Severity", "value": severity.upper(), "inline": True},
        {"name": "Bounty Range", "value": bounty_range, "inline": True},
    ]
    
    if poc:
        fields.append({"name": "PoC", "value": poc[:1024], "inline": False})
    
    footer_text = f"SARAhack Auto-Hunter | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    return send_discord_embed(
        title=f"🐛 New Finding: {vulnerability_type} on {program}",
        description=description[:2048],
        color=color,
        fields=fields,
        footer=footer_text
    )

def notify_hunt_start(program, target_url, tools):
    """Notify hunt started"""
    fields = [
        {"name": "Target", "value": target_url, "inline": False},
        {"name": "Tools", "value": tools, "inline": False},
    ]
    return send_discord_embed(
        title=f"🔍 Hunt Started: {program}",
        description=f"Starting vulnerability assessment on {program}",
        color=0x0088ff,
        fields=fields,
        footer="SARAhack Auto-Hunter"
    )

def notify_hunt_complete(program, vulnerabilities_found, time_spent):
    """Notify hunt completed"""
    fields = [
        {"name": "Findings", "value": str(vulnerabilities_found), "inline": True},
        {"name": "Time Spent", "value": time_spent, "inline": True},
    ]
    return send_discord_embed(
        title=f"✅ Hunt Complete: {program}",
        description=f"Assessment completed. Found {vulnerabilities_found} potential vulnerabilities.",
        color=0x00ff00,
        fields=fields,
        footer="SARAhack Auto-Hunter"
    )

def notify_report_submitted(program, report_id, submission_method):
    """Notify report submitted"""
    fields = [
        {"name": "Submission Method", "value": submission_method, "inline": True},
        {"name": "Report ID", "value": str(report_id), "inline": True},
    ]
    return send_discord_embed(
        title=f"📤 Report Submitted: {program}",
        description=f"Bug report successfully submitted to {program}",
        color=0x00ff00,
        fields=fields,
        footer="SARAhack Auto-Hunter"
    )

if __name__ == "__main__":
    # Test notification
    notify_finding(
        program="Test Program",
        vulnerability_type="SSRF",
        severity="high",
        bounty_range="$500 - $5,000",
        description="Server-side request forgery found in API endpoint allowing metadata access"
    )