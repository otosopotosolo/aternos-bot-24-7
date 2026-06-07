#!/usr/bin/env python3
"""
SARAhack Report Tracker
ติดตามสถานะ reports ที่ส่งไปแล้ว
"""

import argparse
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List

TRACKING_FILE = "reports/tracking/reports.json"

class ReportTracker:
    def __init__(self):
        self.tracking_file = Path(TRACKING_FILE)
        self.tracking_file.parent.mkdir(parents=True, exist_ok=True)
        self.reports = self.load_reports()
    
    def load_reports(self) -> List[Dict]:
        """Load reports from JSON file"""
        if self.tracking_file.exists():
            with open(self.tracking_file, 'r') as f:
                return json.load(f)
        return []
    
    def save_reports(self):
        """Save reports to JSON file"""
        with open(self.tracking_file, 'w') as f:
            json.dump(self.reports, f, indent=2)
    
    def add_report(self, platform: str, program: str, vuln_type: str, 
                   severity: str, report_file: str, status: str = "pending"):
        """Add a new report to tracking"""
        report = {
            "id": len(self.reports) + 1,
            "platform": platform,
            "program": program,
            "vulnerability": vuln_type,
            "severity": severity,
            "status": status,
            "report_file": report_file,
            "date_submitted": datetime.now().strftime("%Y-%m-%d"),
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "notes": ""
        }
        self.reports.append(report)
        self.save_reports()
        print(f"[+] Added report #{report['id']}: {program} ({platform})")
    
    def update_status(self, report_id: int, new_status: str, notes: str = ""):
        """Update report status"""
        for report in self.reports:
            if report['id'] == report_id:
                report['status'] = new_status
                report['last_updated'] = datetime.now().strftime("%Y-%m-%d")
                if notes:
                    report['notes'] = notes
                self.save_reports()
                print(f"[+] Updated report #{report_id} to '{new_status}'")
                return
        print(f"[-] Report #{report_id} not found")
    
    def list_reports(self, status_filter: Optional[str] = None):
        """List all reports, optionally filtered by status"""
        if not self.reports:
            print("No reports tracked yet.")
            return
        
        # Header
        print("\n" + "=" * 80)
        print(f"{'ID':<4} {'Platform':<10} {'Program':<15} {'Vuln':<12} {'Severity':<8} {'Status':<12} {'Submitted':<12}")
        print("=" * 80)
        
        for report in self.reports:
            if status_filter and report['status'] != status_filter:
                continue
            
            print(
                f"{report['id']:<4} "
                f"{report['platform']:<10} "
                f"{report['program']:<15} "
                f"{report['vulnerability']:<12} "
                f"{report['severity']:<8} "
                f"{report['status']:<12} "
                f"{report['date_submitted']:<12}"
            )
        
        print("=" * 80)
        
        # Stats
        total = len(self.reports)
        pending = len([r for r in self.reports if r['status'] == 'pending'])
        resolved = len([r for r in self.reports if r['status'] == 'resolved'])
        duplicate = len([r for r in self.reports if r['status'] == 'duplicate'])
        
        print(f"\nStats: {total} total | {pending} pending | {resolved} resolved | {duplicate} duplicate")
    
    def get_pending(self):
        """Get all pending reports"""
        return [r for r in self.reports if r['status'] == 'pending']
    
    def stats(self):
        """Show statistics"""
        if not self.reports:
            print("No reports tracked yet.")
            return
        
        total = len(self.reports)
        
        # By platform
        platforms = {}
        for r in self.reports:
            platforms[r['platform']] = platforms.get(r['platform'], 0) + 1
        
        # By severity
        severities = {}
        for r in self.reports:
            severities[r['severity']] = severities.get(r['severity'], 0) + 1
        
        # By status
        statuses = {}
        for r in self.reports:
            statuses[r['status']] = statuses.get(r['status'], 0) + 1
        
        print("\n" + "=" * 50)
        print("  SARAhack Report Statistics")
        print("=" * 50)
        
        print(f"\nTotal Reports: {total}")
        
        print("\nBy Platform:")
        for p, c in platforms.items():
            print(f"  - {p}: {c}")
        
        print("\nBy Severity:")
        for s, c in severities.items():
            print(f"  - {s}: {c}")
        
        print("\nBy Status:")
        for st, c in statuses.items():
            print(f"  - {st}: {c}")
        
        print("\n" + "=" * 50)

def main():
    parser = argparse.ArgumentParser(description="SARAhack Report Tracker")
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Add report
    add_parser = subparsers.add_parser('add', help='Add a new report')
    add_parser.add_argument('--platform', required=True, help='Platform (hackerone/bugcrowd)')
    add_parser.add_argument('--program', required=True, help='Program name')
    add_parser.add_argument('--vuln', required=True, help='Vulnerability type')
    add_parser.add_argument('--severity', required=True, help='Severity (HIGH/MEDIUM/LOW/INFO)')
    add_parser.add_argument('--file', required=True, help='Report file path')
    
    # Update status
    update_parser = subparsers.add_parser('update', help='Update report status')
    update_parser.add_argument('--id', type=int, required=True, help='Report ID')
    update_parser.add_argument('--status', required=True, help='New status')
    update_parser.add_argument('--notes', default='', help='Notes')
    
    # List reports
    list_parser = subparsers.add_parser('list', help='List reports')
    list_parser.add_argument('--status', help='Filter by status')
    
    # Stats
    subparsers.add_parser('stats', help='Show statistics')
    
    args = parser.parse_args()
    
    tracker = ReportTracker()
    
    if args.command == 'add':
        tracker.add_report(
            args.platform,
            args.program,
            args.vuln,
            args.severity,
            args.file
        )
    elif args.command == 'update':
        tracker.update_status(args.id, args.status, args.notes)
    elif args.command == 'list':
        tracker.list_reports(args.status)
    elif args.command == 'stats':
        tracker.stats()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()