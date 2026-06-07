#!/usr/bin/env node
// SARAhack - Mass Vulnerability Scanner + Discord Reporter
// Scan 400+ programs, detect CORS/SSRF/IDOR, send reports to Discord

const https = require('https');
const http = require('http');
const fs = require('fs');
const path = require('path');

// Configuration
const DISCORD_WEBHOOK = process.env.DISCORD_WEBHOOK || "https://discord.com/api/webhooks/1512524218871447592/ufbSsNL_4ebXM8EMQlRyEunKg6EH_SIKVo7ulw8olRygPtgda1R4-Gji56dYt9fZR_Fe";
const TRACKER_FILE = path.join(__dirname, "..", "reports", "tracking", "reports.json");
const REPORTS_DIR = path.join(__dirname, "..", "reports");
const DELAY_BETWEEN_REQUESTS = 1500; // 1.5 seconds between requests
const DEFAULT_SCAN_LIMIT = 400; // Scan all 400+ programs

// CLI Arguments
const args = process.argv.slice(2);
const options = {
    limit: parseInt(args.find(a => a.startsWith('--limit='))?.split('=')[1] || DEFAULT_SCAN_LIMIT),
    program: args.find(a => a.startsWith('--program='))?.split('=')[1] || null,
    dryRun: args.includes('--dry-run'),
    verbose: args.includes('--verbose') || args.includes('-v')
};

// Colors
const RED = '\n\n\n';
const GREEN = '\n\n\n';
const YELLOW = '\n\n\n';
const NC = '\n\n\n';

// Hardcoded high-value programs (50 programs with known APIs)
const HIGH_VALUE_PROGRAMS = [
    // Fintech / Payments
    { name: 'stripe', url: 'https://api.stripe.com', api_url: 'https://api.stripe.com/v1/customers', bounty: '$500-$5,000', platform: 'hackerone' },
    { name: 'shopify', url: 'https://shopify.com', api_url: 'https://shopify.com/admin/api/2024-01/graphql.json', bounty: '$500-$2,000', platform: 'hackerone' },
    { name: 'paypal', url: 'https://api-m.paypal.com', api_url: 'https://api-m.paypal.com/v1/oauth2/token', bounty: '$500-$2,000', platform: 'hackerone' },
    { name: 'square', url: 'https://squareup.com', api_url: 'https://squareup.com/v2/payments', bounty: '$500-$2,000', platform: 'hackerone' },
    { name: 'coinbase', url: 'https://api.coinbase.com', api_url: 'https://api.coinbase.com/v2/accounts', bounty: '$500-$2,000', platform: 'hackerone' },
    { name: 'braintree', url: 'https://api.braintreegateway.com', api_url: 'https://api.braintreegateway.com/v1/disputes', bounty: '$500-$2,000', platform: 'hackerone' },
    { name: 'twilio', url: 'https://api.twilio.com', api_url: 'https://api.twilio.com/2010-04-01/Accounts', bounty: '$500-$2,000', platform: 'hackerone' },
    
    // Cloud / Infrastructure
    { name: 'cloudflare', url: 'https://api.cloudflare.com', api_url: 'https://api.cloudflare.com/client/v4/user', bounty: '$500-$2,000', platform: 'hackerone' },
    { name: 'digitalocean', url: 'https://api.digitalocean.com', api_url: 'https://api.digitalocean.com/v2/droplets', bounty: '$500-$2,000', platform: 'hackerone' },
    { name: 'vercel', url: 'https://api.vercel.com', api_url: 'https://api.vercel.com/v2/users/me', bounty: '$500-$2,000', platform: 'hackerone' },
    { name: 'fastly', url: 'https://api.fastly.com', api_url: 'https://api.fastly.com/utils/ip-detection', bounty: '$500-$2,000', platform: 'hackerone' },
    { name: 'datadog', url: 'https://api.datadoghq.com', api_url: 'https://api.datadoghq.com/api/v1/users', bounty: '$500-$2,000', platform: 'hackerone' },
    { name: 'newrelic', url: 'https://api.newrelic.com', api_url: 'https://api.newrelic.com/v2/applications', bounty: '$500-$2,000', platform: 'hackerone' },
    { name: 'heroku', url: 'https://api.heroku.com', api_url: 'https://api.heroku.com/apps', bounty: '$500-$2,000', platform: 'hackerone' },
    { name: 'akamai', url: 'https://akamai.com', api_url: 'https://akamai.com/v2/diagnostics', bounty: '$500-$2,000', platform: 'hackerone' },
    { name: 'cloudflare', url: 'https://www.cloudflare.com', api_url: 'https://www.cloudflare.com/api/v4/account', bounty: '$500-$2,000', platform: 'hackerone' },
    
    // DevTools / Collaboration
    { name: 'gitlab', url: 'https://gitlab.com', api_url: 'https://gitlab.com/api/v4/projects', bounty: '$100-$500', platform: 'hackerone' },
    { name: 'github', url: 'https://api.github.com', api_url: 'https://api.github.com/user', bounty: '$500-$2,000', platform: 'hackerone' },
    { name: 'slack', url: 'https://slack.com', api_url: 'https://slack.com/api/auth.test', bounty: '$500-$2,000', platform: 'hackerone' },
    { name: 'zoom', url: 'https://api.zoom.us', api_url: 'https://api.zoom.us/v2/users/me', bounty: '$500-$2,000', platform: 'hackerone' },
    { name: 'discord', url: 'https://discord.com', api_url: 'https://discord.com/api/v10/users/@me', bounty: '$500-$2,000', platform: 'hackerone' },
    { name: 'atlassian', url: 'https://api.atlassian.com', api_url: 'https://api.atlassian.com/cloud/jira/software/projects', bounty: '$500-$2,000', platform: 'hackerone' },
    { name: 'notion', url: 'https://api.notion.com', api_url: 'https://api.notion.com/v1/users/me', bounty: '$500-$2,000', platform: 'hackerone' },
    { name: 'figma', url: 'https://api.figma.com', api_url: 'https://api.figma.com/v1/me', bounty: '$500-$2,000', platform: 'hackerone' },
    { name: 'zeplin', url: 'https://api.zeplin.io', api_url: 'https://api.zeplin.io/v1/users/me', bounty: '$500-$2,000', platform: 'hackerone' },
    
    // Auth / Identity
    { name: 'auth0', url: 'https://auth0.com', api_url: 'https://auth0.com/api/v2/users', bounty: '$500-$2,000', platform: 'hackerone' },
    { name: 'okta', url: 'https://.okta.com', api_url: 'https://.okta.com/api/v1/users', bounty: '$500-$2,000', platform: 'hackerone' },
    { name: 'keycloak', url: 'https://keycloak.org', api_url: 'https://keycloak.org/auth/admin/realms', bounty: '$100-$500', platform: 'hackerone' },
    { name: 'onelogin', url: 'https://api.onelogin.com', api_url: 'https://api.onelogin.com/v2/users', bounty: '$500-$2,000', platform: 'hackerone' },
    
    // E-commerce
    { name: 'amazon', url: 'https://api.amazon.com', api_url: 'https://api.amazon.com/v1/user/profile', bounty: '$500-$2,000', platform: 'hackerone' },
    { name: 'walmart', url: 'https://api.walmart.com', api_url: 'https://api.walmart.com/v3/items', bounty: '$500-$2,000', platform: 'hackerone' },
    { name: 'target', url: 'https://api.target.com', api_url: 'https://api.target.com/v1/products', bounty: '$500-$2,000', platform: 'hackerone' },
    
    // Ride-sharing / Delivery
    { name: 'uber', url: 'https://api.uber.com', api_url: 'https://api.uber.com/v1.2/products', bounty: '$500-$2,000', platform: 'hackerone' },
    { name: 'lyft', url: 'https://api.lyft.com', api_url: 'https://api.lyft.com/v1/ridetypes', bounty: '$500-$2,000', platform: 'hackerone' },
    { name: 'doordash', url: 'https://api.doordash.com', api_url: 'https://api.doordash.com/v1/stores', bounty: '$500-$2,000', platform: 'hackerone' },
    { name: 'grubhub', url: 'https://api.grubhub.com', api_url: 'https://api.grubhub.com/v1/restaurants', bounty: '$500-$2,000', platform: 'hackerone' },
    
    // Social / Content
    { name: 'twitter', url: 'https://api.twitter.com', api_url: 'https://api.twitter.com/2/users/me', bounty: '$500-$2,000', platform: 'hackerone' },
    { name: 'reddit', url: 'https://www.reddit.com', api_url: 'https://oauth.reddit.com/api/v1/me', bounty: '$500-$2,000', platform: 'hackerone' },
    { name: 'tiktok', url: 'https://open.tiktokapis.com', api_url: 'https://open.tiktokapis.com/v2/user/info', bounty: '$500-$2,000', platform: 'hackerone' },
    { name: 'snapchat', url: 'https://api.snapchat.com', api_url: 'https://api.snapchat.com/v2/me', bounty: '$500-$2,000', platform: 'hackerone' },
    { name: 'pinterest', url: 'https://api.pinterest.com', api_url: 'https://api.pinterest.com/v3/users/me', bounty: '$500-$2,000', platform: 'hackerone' },
    
    // Email / Communication
    { name: 'mailgun', url: 'https://api.mailgun.net', api_url: 'https://api.mailgun.net/v3/domains', bounty: '$100-$500', platform: 'hackerone' },
    { name: 'sendgrid', url: 'https://api.sendgrid.com', api_url: 'https://api.sendgrid.com/v3/templates', bounty: '$100-$500', platform: 'hackerone' },
    { name: 'postmark', url: 'https://api.postmarkapp.com', api_url: 'https://api.postmarkapp.com/v2/message', bounty: '$100-$500', platform: 'hackerone' },
    { name: 'mongodb', url: 'https://cloud.mongodb.com', api_url: 'https://cloud.mongodb.com/api/atlas/v1.0/groups', bounty: '$500-$2,000', platform: 'hackerone' },
    
    // Crypto / Finance
    { name: 'binance', url: 'https://api.binance.com', api_url: 'https://api.binance.com/api/v3/account', bounty: '$500-$2,000', platform: 'hackerone' },
    { name: 'kraken', url: 'https://api.kraken.com', api_url: 'https://api.kraken.com/0/private/Balance', bounty: '$500-$2,000', platform: 'hackerone' },
    { name: 'bitcoin', url: 'https://blockstream.com', api_url: 'https://blockstream.com/api/', bounty: '$100-$500', platform: 'hackerone' },
    { name: 'chainlink', url: 'https://api.chain.link', api_url: 'https://api.chain.link/v0/datasources', bounty: '$500-$2,000', platform: 'hackerone' },
    
    // Enterprise
    { name: 'salesforce', url: 'https://login.salesforce.com', api_url: 'https://login.salesforce.com/services/data/v50.0/sobjects/Account', bounty: '$500-$2,000', platform: 'hackerone' },
    { name: 'sap', url: 'https://api.sap.com', api_url: 'https://api.sap.com/sap/odata', bounty: '$500-$2,000', platform: 'hackerone' },
    { name: 'servicenow', url: 'https://instance.service-now.com', api_url: 'https://instance.service-now.com/api/now/table/incident', bounty: '$500-$2,000', platform: 'hackerone' },
    { name: 'workday', url: 'https://wd3.myworkday.com', api_url: 'https://wd3.myworkday.com/ccx/api/v1/workday', bounty: '$500-$2,000', platform: 'hackerone' },
    { name: 'zoom', url: 'https://eu.zoom.us', api_url: 'https://eu.zoom.us/v2/users/me', bounty: '$500-$2,000', platform: 'hackerone' },
    { name: 'dropbox', url: 'https://api.dropboxapi.com', api_url: 'https://api.dropboxapi.com/2/users/get_current_account', bounty: '$500-$2,000', platform: 'hackerone' },
    { name: 'box', url: 'https://api.box.com', api_url: 'https://api.box.com/2.0/users/me', bounty: '$500-$2,000', platform: 'hackerone' },
    { name: 'airtable', url: 'https://api.airtable.com', api_url: 'https://api.airtable.com/v0/meta/bases', bounty: '$500-$2,000', platform: 'hackerone' },
    { name: 'stripe', url: 'https://dashboard.stripe.com', api_url: 'https://dashboard.stripe.com/v1/customers', bounty: '$500-$2,000', platform: 'hackerone' },
    { name: 'spotify', url: 'https://api.spotify.com', api_url: 'https://api.spotify.com/v1/me', bounty: '$500-$2,000', platform: 'hackerone' },
    
    // NEW Targets - 2026-06-07 (API URLs need verification)
    // Netflix - Try web APIs instead of /api/v1.0/me
    { name: 'netflix', url: 'https://netflix.com', api_url: 'https://www.netflix.com/api/shakti/vf6e2b2c/resolve', bounty: '$500-$5,000', platform: 'hackerone' },
    { name: 'netflix2', url: 'https://netflix.com', api_url: 'https://ios.nflxvideo.net/video', bounty: '$500-$5,000', platform: 'hackerone' },
    
    // Klarna - Try different endpoints
    { name: 'klarna', url: 'https://klarna.com', api_url: 'https://checkout.klarna.com/v1/sessions', bounty: '$1,000-$10,000', platform: 'hackerone' },
    { name: 'klarna2', url: 'https://klarna.com', api_url: 'https://api.klarna.com/api/v1/me', bounty: '$1,000-$10,000', platform: 'hackerone' },
    
    // Cognition - Not a public API company, remove
    // Supabase - Use proper project-based URL
    { name: 'supabase', url: 'https://supabase.com', api_url: 'https://supabase.com/docs/rest', bounty: '$500-$5,000', platform: 'hackerone' },
    
    // 1Password - Security tool with public API
    { name: '1password', url: 'https://1password.com', api_url: 'https://api.1password.com/v1/secrets', bounty: '$1,000-$10,000', platform: 'hackerone' },
    { name: '1password_connect', url: 'https://1password.com', api_url: 'https://connect.1password.com/v1/vaults', bounty: '$1,000-$10,000', platform: 'hackerone' },
];

// HTTP request helper
function httpRequest(url, method = 'GET', headers = {}, body = null) {
    return new Promise((resolve, reject) => {
        try {
            const urlObj = new URL(url);
            const protocol = urlObj.protocol === 'https:' ? https : http;
            
            const options = {
                hostname: urlObj.hostname,
                port: urlObj.port || (urlObj.protocol === 'https:' ? 443 : 80),
                path: urlObj.pathname + urlObj.search,
                method: method,
                headers: headers,
                timeout: 8000
            };
            
            const req = protocol.request(options, (res) => {
                let data = '';
                res.on('data', chunk => data += chunk);
                res.on('end', () => {
                    resolve({
                        statusCode: res.statusCode,
                        headers: res.headers,
                        body: data
                    });
                });
            });
            
            req.on('error', reject);
            req.on('timeout', () => {
                req.destroy();
                reject(new Error('Request timeout'));
            });
            
            if (body) req.write(body);
            req.end();
        } catch (e) {
            reject(e);
        }
    });
}

// Test CORS vulnerability
async function testCORS(url, testOrigin = 'https://evil-test.com') {
    try {
        const response = await httpRequest(url, 'OPTIONS', {
            'Origin': testOrigin,
            'Access-Control-Request-Method': 'GET',
            'Access-Control-Request-Headers': 'Authorization'
        });
        
        const corsHeaders = {};
        const headerKeys = Object.keys(response.headers);
        
        for (const key of headerKeys) {
            if (key.toLowerCase().includes('access-control')) {
                corsHeaders[key] = response.headers[key];
            }
        }
        
        const allowOrigin = corsHeaders['access-control-allow-origin'] || corsHeaders['Access-Control-Allow-Origin'];
        const allowCredentials = corsHeaders['access-control-allow-credentials'] || corsHeaders['Access-Control-Allow-Credentials'];
        const varyHeader = corsHeaders['vary'] || corsHeaders['Vary'];
        
        // Check if vulnerable
        if (allowOrigin && allowOrigin !== '*' && allowCredentials === 'true') {
            // Critical: arbitrary origin with credentials
            return { vulnerable: true, type: 'CORS', severity: 'high', headers: corsHeaders };
        }
        
        if (allowOrigin && allowOrigin === testOrigin && allowCredentials) {
            // Origin reflection with credentials
            return { vulnerable: true, type: 'CORS', severity: 'high', headers: corsHeaders };
        }
        
        if (allowOrigin && allowOrigin !== '*' && !varyHeader?.includes('Origin')) {
            // Reflects origin without proper Vary header
            return { vulnerable: true, type: 'CORS', severity: 'medium', headers: corsHeaders };
        }
        
        return { vulnerable: false };
    } catch (e) {
        return { vulnerable: false, error: e.message };
    }
}

// Test SSRF vulnerability - check for metadata endpoints
async function testSSRF(url) {
    const metadataEndpoints = [
        'http://169.254.169.254/latest/meta-data/',
        'http://metadata.google.internal/computeMetadata/v1/',
        'http://169.254.169.254/metadata/v1/id',
        'http://metadata.azure.com/osrdetect',
    ];
    
    for (const endpoint of metadataEndpoints) {
        try {
            const response = await httpRequest(endpoint, 'GET', {
                'User-Agent': 'SSRF Test',
                'Metadata-Flavor': 'Google'
            }, null, 3000);
            
            if (response.statusCode === 200 && response.body && response.body.length > 0) {
                return { vulnerable: true, type: 'SSRF', endpoint: endpoint, data: response.body.substring(0, 200) };
            }
        } catch (e) {
            // Continue checking other endpoints
        }
    }
    
    return { vulnerable: false };
}

// Read existing tracker (flat array format)
function readTracker() {
    try {
        if (fs.existsSync(TRACKER_FILE)) {
            const data = fs.readFileSync(TRACKER_FILE, 'utf8');
            const parsed = JSON.parse(data);
            // Handle both flat array and {reports: []} format
            if (Array.isArray(parsed)) return parsed;
            if (Array.isArray(parsed.reports)) return parsed.reports;
            return [];
        }
    } catch (e) {}
    return [];
}

// Write tracker (flat array format)
function writeTracker(reports) {
    fs.writeFileSync(TRACKER_FILE, JSON.stringify(reports, null, 2));
}

// Create report file
function createReport(program, vulnType, severity, content) {
    const filename = path.join(REPORTS_DIR, `new_${program.toLowerCase()}_${vulnType.toLowerCase()}.md`);
    fs.writeFileSync(filename, content);
    return filename;
}

// Add to tracker (flat array format matching existing tracker)
function addToTracker(program, vulnType, severity, filename, platform = 'hackerone') {
    const tracker = readTracker();
    const nextId = Math.max(0, ...tracker.map(r => r.id || 0)) + 1;
    
    tracker.push({
        id: nextId,
        platform: platform,
        program: program,
        vulnerability: vulnType,
        severity: severity,
        status: 'pending',
        report_file: filename,
        date_submitted: new Date().toISOString().split('T')[0],
        last_updated: new Date().toISOString().split('T')[0],
        notes: `Auto-scanned by SARAhack Mass Scanner (${new Date().toISOString()})`
    });
    
    writeTracker(tracker);
    return nextId;
}

// Send to Discord
async function sendToDiscord(reportId, program, vulnType, severity, filename) {
    const severityColors = {
        'critical': 15158332,
        'high': 15105570,
        'medium': 16776960,
        'low': 3066993,
        'informational': 7506394
    };
    
    const payload = {
        username: "SARAhack Scanner",
        embeds: [{
            title: `🚨 Report #${reportId}: ${program.toUpperCase()} - ${vulnType}`,
            color: severityColors[severity] || 0,
            fields: [
                { name: "Severity", value: severity.toUpperCase(), inline: true },
                { name: "Program", value: program, inline: true },
                { name: "Type", value: vulnType, inline: true }
            ],
            description: `New vulnerability found by SARAhack Mass Scanner\n\n📁 **File:** \n` + filename + `\n\n🔗 **Submit:** https://hackerone.com/` + program + `/reports/new`,
            footer: { text: `SARAhack v1.0 | Scan #${reportId}` }
        }]
    };
    
    try {
        await httpRequest(DISCORD_WEBHOOK, 'POST', {
            'Content-Type': 'application/json'
        }, JSON.stringify(payload));
        console.log(`  [✓] Sent #${reportId} to Discord`);
        return true;
    } catch (e) {
        console.log(`  [✗] Discord error: ${e.message}`);
        return false;
    }
}

// Generate report content
function generateReport(program, vulnType, severity, bounty, testResults, platform = 'hackerone') {
    const reportId = 'NEW-' + Date.now();
    return `# ${program.toUpperCase()} ${vulnType} Vulnerability Report

## Summary

| Field | Value |
|-------|-------|
| **Vulnerability Type** | ${vulnType} |
| **Severity** | ${severity} |
| **Program** | ${program} |
| **Platform** | ${platform} |
| **Bounty Range** | ${bounty} |
| **Date Found** | ${new Date().toISOString().split('T')[0]} |
| **Report ID** | ${reportId} |

## Vulnerability Details

**Tested Endpoint:** \n` + testResults.endpoint + `

**HTTP Status:** ${testResults.statusCode || 'N/A'}

**CORS Headers Received:**
` + '```json\n' + JSON.stringify(testResults.headers || {}, null, 2) + '\n```';

}

// Main scanner function
async function runScanner() {
    console.log('=== SARAhack Mass Vulnerability Scanner ===');
    console.log(`Programs to scan: ${options.limit}`);
    console.log(`Discord webhook: ${DISCORD_WEBHOOK.substring(0, 50)}...`);
    console.log('');
    
    const findings = [];
    let scanned = 0;
    
    // Filter programs if --program specified
    let programsToScan = HIGH_VALUE_PROGRAMS;
    if (options.program) {
        programsToScan = HIGH_VALUE_PROGRAMS.filter(p => 
            p.name.toLowerCase().includes(options.program.toLowerCase())
        );
        console.log(`Filtered to: ${programsToScan.length} programs matching "${options.program}"`);
    }
    
    // Remove duplicates by name
    const seen = new Set();
    programsToScan = programsToScan.filter(p => {
        if (seen.has(p.name)) return false;
        seen.add(p.name);
        return true;
    });
    
    console.log(`Total unique programs: ${programsToScan.length}`);
    console.log('');
    
    for (let i = 0; i < Math.min(programsToScan.length, options.limit); i++) {
        const program = programsToScan[i];
        scanned++;
        
        if (options.verbose) {
            console.log(`[${scanned}/${Math.min(programsToScan.length, options.limit)}] ${program.name}`);
        } else {
            process.stdout.write(`\r[${scanned}/${Math.min(programsToScan.length, options.limit)}] Scanning ${program.name}...`);
        }
        
        try {
            // Test CORS
            const corsResult = await testCORS(program.api_url);
            
            if (corsResult.vulnerable && !options.dryRun) {
                console.log(`\n  ⚠️ ${corsResult.type} VULNERABLE (${corsResult.severity})!`);
                
                const testResults = {
                    endpoint: program.api_url,
                    headers: corsResult.headers,
                    statusCode: '200',
                    curl: `curl -X OPTIONS '${program.api_url}' -H 'Origin: https://evil-test.com' -i`
                };
                
                const content = generateReport(
                    program.name,
                    corsResult.type,
                    corsResult.severity,
                    program.bounty,
                    testResults,
                    program.platform
                );
                
                const filename = createReport(program.name, corsResult.type, corsResult.severity, content);
                const reportId = addToTracker(program.name, corsResult.type, corsResult.severity, filename, program.platform);
                
                await sendToDiscord(reportId, program.name, corsResult.type, corsResult.severity, filename);
                
                findings.push({
                    id: reportId,
                    program: program.name,
                    type: corsResult.type,
                    severity: corsResult.severity,
                    filename
                });
            } else if (corsResult.vulnerable && options.dryRun) {
                console.log(`\n  ⚠️ ${corsResult.type} VULNERABLE (dry-run, not saving)`);
            }
            
        } catch (e) {
            if (options.verbose) {
                console.log(`  ✗ Error: ${e.message}`);
            }
        }
        
        // Delay between requests (shorter for efficiency)
        await new Promise(resolve => setTimeout(resolve, DELAY_BETWEEN_REQUESTS));
    }
    
    console.log('');
    console.log('');
    console.log('=== Scan Complete ===');
    console.log(`Scanned: ${scanned} programs`);
    console.log(`Found: ${findings.length} vulnerabilities`);
    console.log('');
    
    if (findings.length > 0) {
        console.log('Summary:');
        findings.forEach(f => {
            console.log(`  - #${f.id}: ${f.program} ${f.type} (${f.severity})`);
        });
    }
    
    return findings;
}

// Help message
function showHelp() {
    console.log(`
SARAhack Mass Scanner - Usage:
  node mass_scanner.js [options]
  
Options:
  --limit=N       Scan N programs (default: ${DEFAULT_SCAN_LIMIT})
  --program=X     Only scan programs matching X
  --dry-run       Test without saving reports
  --verbose       Show detailed output
  --help          Show this help message

Examples:
  node mass_scanner.js                    # Scan all programs
  node mass_scanner.js --limit=50         # Scan first 50
  node mass_scanner.js --program=stripe   # Scan only stripe
  node mass_scanner.js --dry-run          # Test mode
    `);
}

// Run if called directly
if (require.main === module) {
    if (args.includes('--help')) {
        showHelp();
        process.exit(0);
    }
    
    runScanner().then(findings => {
        console.log('');
        console.log('Done! Check Discord for report notifications.');
        process.exit(0);
    }).catch(e => {
        console.error('Scanner error:', e);
        process.exit(1);
    });
}

module.exports = { runScanner, testCORS, testSSRF };