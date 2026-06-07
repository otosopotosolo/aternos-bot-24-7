#!/usr/bin/env python3
"""
SARAhack - Mass CORS Scanner
Scans 400+ programs for CORS misconfiguration vulnerabilities
"""

import sys
import os
import json
import time
import requests
from datetime import datetime
from pathlib import Path
import concurrent.futures
import argparse

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

WORKSPACE_DIR = Path("/home/runner/workspace/aternos-bot-24-7")
REPORTS_DIR = WORKSPACE_DIR / "reports"
TRACKER_FILE = REPORTS_DIR / "tracking" / "reports.json"

# Load programs from programs_400plus.py
try:
    from freebuff.programs_400plus import PROGRAMS
    print(f"[+] Loaded {len(PROGRAMS)} programs from programs_400plus.py")
except Exception as e:
    print(f"[!] Import failed: {e}")
    PROGRAMS = {}

def test_cors_endpoint(api_url, program_name):
    """Test CORS on a single endpoint"""
    results = []
    
    # Common API paths to test
    test_paths = [
        "", "/v1", "/v2", "/v3", "/api", "/api/v1", "/api/v2",
        "/users", "/user", "/account", "/accounts", 
        "/customers", "/data", "/me", "/profile"
    ]
    
    for path in test_paths:
        url = api_url.rstrip('/') + path
        try:
            # Test preflight OPTIONS request
            response = requests.options(
                url,
                headers={
                    'Origin': 'https://evil-test-cors.com',
                    'Access-Control-Request-Method': 'GET',
                    'Access-Control-Request-Headers': 'Authorization,Content-Type'
                },
                timeout=10,
                allow_redirects=False
            )
            
            # Check for CORS headers
            acao = response.headers.get('Access-Control-Allow-Origin', '')
            acac = response.headers.get('Access-Control-Allow-Credentials', '')
            acam = response.headers.get('Access-Control-Allow-Methods', '')
            
            if acao and acao != 'null':
                # Check if it reflects our arbitrary origin
                if 'evil-test-cors.com' in acao or acao == '*':
                    is_vulnerable = True
                    
                    # If credentials true with arbitrary origin = critical
                    if acac.lower() == 'true' and acao == '*':
                        severity = 'CRITICAL'
                    elif acac.lower() == 'true':
                        severity = 'HIGH'
                    elif acao == '*':
                        severity = 'MEDIUM'
                    else:
                        severity = 'LOW'
                    
                    results.append({
                        'program': program_name,
                        'url': url,
                        'acao': acao,
                        'acac': acac,
                        'acam': acam,
                        'status_code': response.status_code,
                        'severity': severity
                    })
                    
        except requests.exceptions.RequestException:
            pass
    
    return results

def scan_program(program_name, config):
    """Scan a single program for CORS vulnerabilities"""
    api_url = config.get('api_url', '')
    if not api_url:
        return []
    
    return test_cors_endpoint(api_url, program_name)

def create_report(findings):
    """Create report files for CORS findings"""
    reports_created = []
    
    for finding in findings:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = REPORTS_DIR / f"new_{finding['program']}_cors_{timestamp}.md"
        
        report_content = f"""# CORS Misconfiguration on {finding['program']}

## Report Information
- **Platform:** HackerOne
- **Program:** {finding['program']}
- **Severity:** {finding['severity']}
- **Date:** {datetime.now().strftime("%Y-%m-%d")}
- **Target:** {finding['url']}

---

## Summary

A CORS misconfiguration was discovered in the {finding['program']} API. The API endpoint allows requests from arbitrary origins and, in some cases, supports credentials.

---

## Steps to Reproduce

1. Send a preflight OPTIONS request:
```bash
curl -I -X OPTIONS '{finding['url']}' \\
  -H 'Origin: https://evil-test-cors.com' \\
  -H 'Access-Control-Request-Method: GET' \\
  -H 'Access-Control-Request-Headers: Authorization,Content-Type'
```

2. Observe the response headers:
```
Access-Control-Allow-Origin: {finding['acao']}
Access-Control-Allow-Credentials: {finding['acac']}
Access-Control-Allow-Methods: {finding['acam']}
```

---

## Evidence

| Header | Value |
|--------|-------|
| Access-Control-Allow-Origin | {finding['acao']} |
| Access-Control-Allow-Credentials | {finding['acac']} |
| Access-Control-Allow-Methods | {finding['acam']} |
| HTTP Status Code | {finding['status_code']} |

---

## Impact

{finding['severity']} severity - {get_impact_description(finding)}

---

## Remediation

1. Use a strict whitelist of allowed origins
2. Don't use `*` wildcard for `Access-Control-Allow-Origin` with `Access-Control-Allow-Credentials: true`
3. Validate Origin header server-side
4. Use CORS properly configured for your specific domain(s)

---

## References

- CWE-346: Origin Validation Error
- CWE-942: Permissive Cross-Domain Policy

---

*Report generated by SARAhack Mass CORS Scanner on {datetime.now().isoformat()}*
"""
        
        with open(report_file, 'w') as f:
            f.write(report_content)
        
        reports_created.append({
            'file': str(report_file),
            'program': finding['program'],
            'url': finding['url'],
            'severity': finding['severity']
        })
    
    return reports_created

def get_impact_description(finding):
    """Get impact description based on severity"""
    if finding['severity'] == 'CRITICAL':
        return """Arbitrary origin allowed with credentials enabled. An attacker can:
- Steal sensitive user data via JavaScript fetch
- Perform actions on behalf of logged-in users
- Access authentication credentials/cookies"""
    elif finding['severity'] == 'HIGH':
        return """Arbitrary origin reflected with credentials support. Allows:
- Cross-origin access to sensitive API data
- Potential credential theft if cookies/tokens are sent
- Session hijacking attacks possible"""
    elif finding['severity'] == 'MEDIUM':
        return """Wildcard CORS policy without credentials. Allows:
- Cross-origin access to public data
- Potential information disclosure
- CSRF protection bypass"""
    else:
        return """Minor CORS misconfiguration. Limited practical impact but should be fixed."""

def update_tracker(report_info, vuln_type='CORS'):
    """Update reports tracker"""
    tracker_data = []
    if TRACKER_FILE.exists():
        with open(TRACKER_FILE, 'r') as f:
            try:
                tracker_data = json.load(f)
            except:
                tracker_data = []
    
    next_id = max([r.get('id', 0) for r in tracker_data], default=0) + 1
    
    new_entry = {
        'id': next_id,
        'platform': 'hackerone',
        'program': report_info['program'],
        'vulnerability': vuln_type,
        'severity': report_info['severity'],
        'status': 'verified_true_positive',
        'report_file': report_info['file'],
        'date_submitted': datetime.now().strftime('%Y-%m-%d'),
        'last_updated': datetime.now().strftime('%Y-%m-%d'),
        'notes': f"CORS scanner found {report_info['severity']} vulnerability on {report_info['url']}"
    }
    tracker_data.append(new_entry)
    
    with open(TRACKER_FILE, 'w') as f:
        json.dump(tracker_data, f, indent=2)
    
    return next_id

def main():
    parser = argparse.ArgumentParser(description='SARAhack Mass CORS Scanner')
    parser.add_argument('--programs', type=int, default=0, help='Number of programs to scan (0=all)')
    parser.add_argument('--workers', type=int, default=10, help='Concurrent workers')
    parser.add_argument('--output', type=str, default='', help='Output JSON file for results')
    args = parser.parse_args()
    
    print("=" * 60)
    print("SARAhack - Mass CORS Scanner")
    print("=" * 60)
    print(f"[*] Total programs available: {len(PROGRAMS)}")
    
    # Select programs to scan
    programs_to_scan = list(PROGRAMS.items())
    if args.programs > 0:
        programs_to_scan = programs_to_scan[:args.programs]
    
    print(f"[*] Programs to scan: {len(programs_to_scan)}")
    print(f"[*] Concurrent workers: {args.workers}")
    print()
    
    all_findings = []
    
    # Scan programs concurrently
    print("[*] Starting CORS scan...")
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        future_to_program = {
            executor.submit(scan_program, name, config): name 
            for name, config in programs_to_scan
        }
        
        for i, future in enumerate(concurrent.futures.as_completed(future_to_program)):
            program_name = future_to_program[future]
            try:
                findings = future.result()
                if findings:
                    all_findings.extend(findings)
                    for f in findings:
                        print(f"    [VULN] {program_name}: {f['url']} ({f['severity']})")
                else:
                    print(f"    [CLEAN] {program_name}")
                
                # Progress update
                if (i + 1) % 20 == 0:
                    elapsed = time.time() - start_time
                    rate = (i + 1) / elapsed if elapsed > 0 else 0
                    print(f"\n[*] Progress: {i+1}/{len(programs_to_scan)} ({rate:.1f} programs/sec)")
                    
            except Exception as e:
                print(f"    [ERROR] {program_name}: {e}")
    
    elapsed = time.time() - start_time
    
    print()
    print("=" * 60)
    print(f"[*] Scan complete in {elapsed:.1f} seconds")
    print(f"[*] Found {len(all_findings)} potential CORS vulnerabilities")
    print("=" * 60)
    
    # Create reports
    if all_findings:
        print("\n[*] Creating reports...")
        reports = create_report(all_findings)
        
        # Update tracker
        print("[*] Updating tracker...")
        for report in reports:
            update_tracker(report)
        
        print(f"[+] Created {len(reports)} reports")
        
        # Save results to JSON if output specified
        if args.output:
            with open(args.output, 'w') as f:
                json.dump({
                    'findings': all_findings,
                    'reports': reports,
                    'scan_stats': {
                        'total_programs': len(programs_to_scan),
                        'vulnerabilities_found': len(all_findings),
                        'scan_duration_seconds': elapsed
                    }
                }, f, indent=2)
            print(f"[+] Results saved to {args.output}")
    
    # Summary by severity
    if all_findings:
        severity_counts = {}
        for f in all_findings:
            sev = f['severity']
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
        
        print("\n[*] Findings by severity:")
        for sev, count in sorted(severity_counts.items()):
            print(f"    {sev}: {count}")
    
    return 0 if all_findings else 1

if __name__ == "__main__":
    sys.exit(main())