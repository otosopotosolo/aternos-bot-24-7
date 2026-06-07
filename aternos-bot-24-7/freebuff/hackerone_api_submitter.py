#!/usr/bin/env python3
"""
HackerOne API Automated Bug Bounty Report Submitter

Usage:
    python3 hackerone_api_submitter.py --report 2
    python3 hackerone_api_submitter.py --report 2 --dry-run
    python3 hackerone_api_submitter.py --all
    python3 hackerone_api_submitter.py --list

Environment Variables:
    H1_API_IDENTIFIER - Your HackerOne API Identifier
    H1_API_TOKEN - Your HackerOne API Token
"""

import os
import sys
import json
import argparse
import requests
from pathlib import Path
from base64 import b64encode

# Configuration
H1_API_BASE_URL = "https://api.hackerone.com/v1"
H1_API_REPORTS_ENDPOINT = f"{H1_API_BASE_URL}/hackers/reports"
REPORTS_DIR = Path(__file__).parent.parent / "reports"
TRACKER_FILE = Path(__file__).parent.parent / "reports" / "tracking" / "reports.json"

# Program slugs mapping (HackerOne URL slugs)
PROGRAM_SLUGS = {
    "cloudflare": "cloudflare",
    "uber": "uber",
    "shopify": "shopify", 
    "coinbase": "coinbase",
    "gitlab": "gitlab",
    "reddit": "reddit",
    "doordash": "doordash",
    "anthropic": "anthropic"
}

# Severity mapping (HackerOne API values)
SEVERITY_MAP = {
    "critical": "critical",
    "high": "high",
    "medium": "medium",
    "low": "low",
    "informational": "informational",
    "p4": "medium",
    "p3": "medium",
    "p2": "high",
    "p1": "critical"
}

# CWE weakness IDs for common vulnerability types
# Note: Verify CWE IDs match actual vulnerability classifications
CWE_MAP = {
    "ssrf": 918,      # Server-Side Request Forgery
    "idor": 639,      # Insecure Direct Object Reference
    "cors": 346,      # Origin Confusion (CORS misconfiguration)
    "xss": 79,        # Cross-site Scripting
    "sql": 89,        # SQL Injection
    "rce": 94         # Code Injection
}

def get_auth_headers():
    """Get authentication headers for HackerOne API."""
    api_id = os.environ.get("H1_API_IDENTIFIER")
    api_token = os.environ.get("H1_API_TOKEN")
    
    if not api_id or not api_token:
        raise ValueError(
            "Missing HackerOne API credentials. "
            "Set H1_API_IDENTIFIER and H1_API_TOKEN environment variables."
        )
    
    credentials = f"{api_id}:{api_token}"
    encoded = b64encode(credentials.encode()).decode()
    return {
        "Authorization": f"Basic {encoded}",
        "Content-Type": "application/json"
    }

def load_tracker():
    """Load the reports tracker JSON."""
    with open(TRACKER_FILE, 'r') as f:
        return json.load(f)

def load_report_file(report_path):
    """Load a report markdown file and extract content."""
    # Handle path - remove 'reports/' prefix if present since REPORTS_DIR already points there
    clean_path = report_path.replace("reports/", "").replace("reports\\", "")
    full_path = REPORTS_DIR / clean_path
    
    with open(full_path, 'r') as f:
        content = f.read()
    
    # Parse markdown to extract sections
    lines = content.split('\n')
    title = None
    severity = None
    description = []
    in_description = False
    description_started = False
    
    for i, line in enumerate(lines):
        if line.startswith('**Title:**') or (line.startswith('# ') and not title):
            title = line.replace('**Title:**', '').replace('# ', '').strip()
        elif line.startswith('**Severity:**'):
            severity = line.replace('**Severity:**', '').strip().lower()
        elif line.startswith('## Summary') or line.startswith('## Description'):
            in_description = True
            description_started = True
        elif line.startswith('## ') and in_description and description_started:
            # Stop at next section (Impact, Steps to Reproduce, etc.)
            in_description = False
        elif in_description:
            description.append(line)
    
    # If description is still empty, try to collect content from beginning after title
    if not description:
        desc_content = []
        capture = False
        for line in lines:
            if line.startswith('---') and not capture:
                capture = True
                continue
            if line.startswith('## ') and capture:
                break
            if capture and line.strip():
                desc_content.append(line)
        if desc_content:
            description = desc_content
    
    # Fallback title extraction
    if not title:
        for line in lines:
            if line.startswith('**Platform:**'):
                break
            if line.startswith('# '):
                title = line.replace('# ', '').strip()
                break
    
    # Fallback severity
    if not severity:
        severity = "medium"
    
    # Extract impact section if present
    impact = []
    in_impact = False
    for line in lines:
        if line.startswith('## Impact'):
            in_impact = True
            continue
        elif line.startswith('## ') and in_impact:
            in_impact = False
        elif in_impact:
            impact.append(line)
    
    return {
        "title": title or "Untitled Report",
        "severity": severity,  # Return raw severity, mapping happens in submit_report
        "description": '\n'.join(description).strip(),
        "impact": '\n'.join(impact).strip(),
        "full_content": content
    }

def get_cwe_for_vuln(vulnerability_type):
    """Get CWE ID for vulnerability type."""
    vuln_lower = vulnerability_type.lower()
    return CWE_MAP.get(vuln_lower, 0)  # 0 = unknown/unclassified


def submit_report(program_slug, report_data, vulnerability_type=None, dry_run=False):
    """Submit a report to HackerOne via API."""
    url = H1_API_REPORTS_ENDPOINT
    
    # Apply severity mapping (report_data["severity"] is already mapped from load_report_file)
    severity = report_data["severity"]  # Already mapped, use directly
    
    # Get CWE for vulnerability type (passed from tracker)
    cwe_id = get_cwe_for_vuln(vulnerability_type or "")
    
    # Build attributes per HackerOne API spec
    attributes = {
        "team_handle": program_slug,  # Program identifier (slug)
        "title": report_data["title"],
        "vulnerability_information": report_data["description"],
        "severity_rating": severity,
    }
    
    # Add impact if available
    if report_data.get("impact"):
        attributes["impact"] = report_data["impact"]
    
    # Add weakness if CWE found
    if cwe_id > 0:
        attributes["weakness_id"] = cwe_id
    
    payload = {
        "data": {
            "type": "report",
            "attributes": attributes
        }
    }
    
    if dry_run:
        print(f"[DRY RUN] Would submit to {program_slug}:")
        print(f"  Title: {report_data['title']}")
        print(f"  Severity: {report_data['severity']}")
        print(f"  Description (first 200 chars): {report_data['description'][:200]}...")
        return {"success": True, "dry_run": True}
    
    response = requests.post(
        url,
        headers=get_auth_headers(),
        json=payload,
        timeout=30
    )
    
    if response.status_code in [200, 201]:
        return {"success": True, "response": response.json()}
    else:
        return {
            "success": False, 
            "error": f"HTTP {response.status_code}: {response.text}",
            "status_code": response.status_code
        }

def submit_report_full(program_slug, report_file, dry_run=False, vulnerability_type=None):
    """Submit a complete report file to HackerOne."""
    report_path = f"reports/{report_file.replace('reports/', '')}"
    
    print(f"\n{'[DRY RUN] ' if dry_run else ''}Processing: {report_file}")
    
    # Load and parse report
    report_data = load_report_file(report_path)
    
    # Validate required fields
    if not report_data["title"] or report_data["title"] == "Untitled Report":
        print(f"  WARNING: Could not extract title from report file")
    if not report_data["description"]:
        print(f"  WARNING: Could not extract description from report file")
    
    print(f"  Title: {report_data['title']}")
    print(f"  Severity: {SEVERITY_MAP.get(report_data['severity'], report_data['severity'])}")
    
    # Submit
    result = submit_report(program_slug, report_data, vulnerability_type=vulnerability_type, dry_run=dry_run)
    
    if result.get("dry_run"):
        print(f"  Status: Would submit successfully (dry run)")
    elif result.get("success"):
        print(f"  Status: Submitted successfully!")
        if "response" in result:
            report_id = result["response"].get("data", {}).get("id", "unknown")
            print(f"  Report ID: {report_id}")
    else:
        print(f"  Status: FAILED - {result.get('error', 'Unknown error')}")
    
    return result

def main():
    parser = argparse.ArgumentParser(
        description="HackerOne API Automated Bug Bounty Report Submitter"
    )
    parser.add_argument("--report", type=int, help="Submit specific report by ID")
    parser.add_argument("--program", type=str, help="Filter by program name")
    parser.add_argument("--all", action="store_true", help="Submit all pending reports")
    parser.add_argument("--list", action="store_true", help="List all reports")
    parser.add_argument("--dry-run", action="store_true", help="Preview without submitting")
    parser.add_argument("--yes", action="store_true", help="Skip confirmation prompt")
    
    args = parser.parse_args()
    
    # Load tracker
    tracker = load_tracker()
    
    # List mode
    if args.list:
        print("Available Reports:")
        print("-" * 60)
        for report in tracker:
            status_icon = "✅" if report["status"] == "submitted" else "❌" if "closed" in report["status"] else "⏳"
            print(f"{status_icon} #{report['id']} | {report['program']} | {report['vulnerability']} | {report['severity']} | {report['status']}")
        return
    
    # Determine which reports to submit
    reports_to_submit = []
    
    if args.all:
        reports_to_submit = [
            r for r in tracker 
            if r["status"] == "pending" and r["platform"] == "hackerone"
        ]
    elif args.report:
        reports_to_submit = [
            r for r in tracker if r["id"] == args.report
        ]
    elif args.program:
        reports_to_submit = [
            r for r in tracker 
            if r["program"].lower() == args.program.lower() and r["status"] == "pending"
        ]
    else:
        parser.print_help()
        print("\nExamples:")
        print("  python3 hackerone_api_submitter.py --list")
        print("  python3 hackerone_api_submitter.py --report 2")
        print("  python3 hackerone_api_submitter.py --all")
        print("  python3 hackerone_api_submitter.py --program cloudflare")
        print("  python3 hackerone_api_submitter.py --report 2 --dry-run")
        return
    
    if not reports_to_submit:
        print("No reports to submit. Use --list to see available reports.")
        return
    
    # Check for API credentials before submission
    if not args.dry_run:
        try:
            get_auth_headers()
        except ValueError as e:
            print(f"ERROR: {e}")
            print("\nTo set credentials:")
            print("  export H1_API_IDENTIFIER='your_identifier'")
            print("  export H1_API_TOKEN='your_token'")
            sys.exit(1)
        
        # Confirmation prompt (skip with --yes flag)
        if not args.yes:
            print(f"\n⚠️  About to submit {len(reports_to_submit)} report(s) to HackerOne.")
            response = input("Continue? (y/n): ")
            if response.lower() != 'y':
                print("Aborted.")
                return
    
    print(f"\n{'='*60}")
    print(f"HackerOne Report Submitter {'(DRY RUN)' if args.dry_run else ''}")
    print(f"{'='*60}")
    
    results = []
    for report in reports_to_submit:
        program_slug = PROGRAM_SLUGS.get(report["program"].lower())
        
        if not program_slug:
            print(f"\n⚠️  No program slug found for: {report['program']}")
            results.append({
                "id": report["id"],
                "program": report["program"],
                "success": False,
                "error": "Unknown program slug"
            })
            continue
        
        result = submit_report_full(
            program_slug, 
            report["report_file"], 
            args.dry_run,
            vulnerability_type=report.get("vulnerability", "")  # Pass vulnerability for CWE lookup
        )
        
        results.append({
            "id": report["id"],
            "program": report["program"],
            **result
        })
        
        # Rate limiting - wait between submissions (5 seconds to avoid rate limits)
        if not args.dry_run:
            import time
            time.sleep(5)
    
    # Summary
    print(f"\n{'='*60}")
    print("SUBMISSION SUMMARY")
    print(f"{'='*60}")
    
    success_count = sum(1 for r in results if r.get("success"))
    fail_count = len(results) - success_count
    
    for r in results:
        status = "✅" if r.get("success") else "❌"
        print(f"{status} #{r['id']} {r['program']}: {'Success' if r.get('success') else r.get('error', 'Failed')}")
    
    print(f"\nTotal: {len(results)} | Success: {success_count} | Failed: {fail_count}")
    
    if fail_count > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()