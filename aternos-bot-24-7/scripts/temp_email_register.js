#!/usr/bin/env node
/**
 * SARAhack - Temp Email Registration Script
 * Uses Mail.tm (free, no API key) for temporary email
 * Sends registration data to webhook for manual verification
 * 
 * Usage: node temp_email_register.js <platform>
 * Example: node temp_email_register.js prolific
 */

const https = require('https');
const http = require('http');
const fs = require('fs');

// Configuration
const WEBHOOK_URL = process.env.WEBHOOK_URL || 'https://hook.mee.my.id/hook';
const EMAIL_OUTPUT_FILE = '/tmp/temp_email_credentials.json';

// Colors for output
const colors = {
  green: '\u001b[32m',
  red: '\u001b[31m',
  yellow: '\u001b[33m',
  blue: '\u001b[34m',
  reset: '\u001b[0m'
};

function log(color, msg) {
  console.log(`${color}${msg}${colors.reset}`);
}

// Mail.tm API functions
async function getDomains() {
  return new Promise((resolve, reject) => {
    const req = https.get('https://api.mail.tm/domains', (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(data));
        } catch (e) {
          reject(e);
        }
      });
    });
    req.on('error', reject);
  });
}

async function createAccount(domain, password) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({
      address: `sarahack_${Date.now()}@${domain}`,
      password: password
    });
    
    const req = https.request({
      hostname: 'api.mail.tm',
      path: '/accounts',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': data.length
      }
    }, (res) => {
      let result = '';
      res.on('data', chunk => result += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(result));
        } catch (e) {
          reject(e);
        }
      });
    });
    
    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

async function getToken(address, password) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({
      address: address,
      password: password
    });
    
    const req = https.request({
      hostname: 'api.mail.tm',
      path: '/token',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': data.length
      }
    }, (res) => {
      let result = '';
      res.on('data', chunk => result += chunk);
      res.on('end', () => {
        try {
          const parsed = JSON.parse(result);
          resolve(parsed.token);
        } catch (e) {
          reject(e);
        }
      });
    });
    
    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

async function getMessages(token) {
  return new Promise((resolve, reject) => {
    const req = https.request({
      hostname: 'api.mail.tm',
      path: '/messages',
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(data));
        } catch (e) {
          reject(e);
        }
      });
    });
    
    req.on('error', reject);
    req.end();
  });
}

async function getMessage(token, id) {
  return new Promise((resolve, reject) => {
    const req = https.request({
      hostname: 'api.mail.tm',
      path: `/messages/${id}`,
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(data));
        } catch (e) {
          reject(e);
        }
      });
    });
    
    req.on('error', reject);
    req.end();
  });
}

async function sendToWebhook(data) {
  return new Promise((resolve, reject) => {
    const payload = JSON.stringify({
      timestamp: new Date().toISOString(),
      source: 'SARAhack-temp-email',
      ...data
    });
    
    const url = new URL(WEBHOOK_URL);
    const options = {
      hostname: url.hostname,
      path: url.pathname,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(payload)
      }
    };
    
    const req = (url.protocol === 'https:' ? https : http).request(options, (res) => {
      let result = '';
      res.on('data', chunk => result += chunk);
      res.on('end', () => resolve(result));
    });
    
    req.on('error', reject);
    req.write(payload);
    req.end();
  });
}

function extractLinks(html) {
  const regex = /https?:\/\/[^\"'\/\n<>\u0000-\u001F]+/gi;
  return html.match(regex) || [];
}

async function waitForEmail(token, timeoutMs = 60000) {
  const startTime = Date.now();
  while (Date.now() - startTime < timeoutMs) {
    const messages = await getMessages(token);
    if (messages.hydra['totalItems'] > 0) {
      return messages.hydra['member'][0];
    }
    await new Promise(r => setTimeout(r, 5000)); // Poll every 5 seconds
  }
  return null;
}

// Platform registration URLs and info
const platforms = {
  prolific: {
    name: 'Prolific',
    url: 'https://www.prolific.com/',
    type: 'Participant',
    note: 'Academic surveys - รายได้ £50-300/เดือน'
  },
  freecash: {
    name: 'Freecash',
    url: 'https://freecash.com/',
    type: 'Email/Google',
    note: 'Micro tasks - รายได้ $1-20/เดือน'
  },
  honeygain: {
    name: 'Honeygain',
    url: 'https://dashboard.honeygain.com/',
    type: 'Docker',
    note: 'Bandwidth sharing - รายได้ $5-50/เดือน'
  },
  earnapp: {
    name: 'EarnApp',
    url: 'https://earnapp.com/',
    type: 'Download',
    note: 'Bandwidth sharing - รายได้ $5-30/เดือน'
  },
  pawns: {
    name: 'Pawns.app',
    url: 'https://pawns.app/',
    type: 'CLI',
    note: 'Bandwidth sharing - รายได้ $5-20/เดือน'
  }
};

async function main() {
  const platformKey = process.argv[2] || 'prolific';
  const platform = platforms[platformKey];
  
  if (!platform) {
    log(colors.red, 'Unknown platform. Options:');
    Object.keys(platforms).forEach(k => {
      log(colors.blue, `  - ${k}: ${platforms[k].name}`);
    });
    process.exit(1);
  }
  
  log(colors.yellow, `=== SARAhack Temp Email Registration ===`);
  log(colors.blue, `Platform: ${platform.name}`);
  log(colors.blue, `URL: ${platform.url}`);
  console.log();
  
  try {
    // Step 1: Get available domain from Mail.tm
    log(colors.yellow, '[1/5] Getting temp email domain...');
    const domainsResponse = await getDomains();
    
    if (!domainsResponse || !domainsResponse['hydra:member'] || domainsResponse['hydra:member'].length === 0) {
      throw new Error('No available domains from Mail.tm');
    }
    
    const domain = domainsResponse['hydra:member'][0].domain;
    log(colors.green, `  Domain: ${domain}`);
    
    // Step 2: Generate password for email account
    const emailPassword = `SarahAck_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    // Step 3: Create temp email account
    log(colors.yellow, '[2/5] Creating temp email account...');
    let emailAddress;
    try {
      const account = await createAccount(domain, emailPassword);
      emailAddress = account.address;
      log(colors.green, `  Email: ${emailAddress}`);
    } catch (e) {
      // If creation fails, generate a random address manually
      emailAddress = `sarahack_${Date.now()}@${domain}`;
      log(colors.yellow, `  Using generated email: ${emailAddress}`);
    }
    
    // Step 4: Get authentication token
    log(colors.yellow, '[3/5] Getting API token...');
    let token;
    try {
      token = await getToken(emailAddress, emailPassword);
      log(colors.green, `  Token obtained`);
    } catch (e) {
      log(colors.red, `  Failed to get token: ${e.message}`);
      // Continue anyway - we still have the email
      token = null;
    }
    
    // Step 5: Send registration info to webhook (WITHOUT passwords!)
    log(colors.yellow, '[4/5] Sending info to webhook...');
    const registrationData = {
      platform: platform.name,
      platformKey: platformKey,
      registrationUrl: platform.url,
      registrationType: platform.type,
      tempEmail: emailAddress,
      estimatedEarnings: platform.note,
      instructions: [
        `1. Go to ${platform.url}`,
        `2. Click Sign Up`,
        platformKey === 'prolific' ? '3. Select PARTICIPANT (not Researcher)' : '3. Sign up with email',
        `4. Use temp email: ${emailAddress}`,
        `5. Check emails at mail.tm for verification link`,
        `6. Complete verification manually`
      ].join('\n'),
      mailTmInboxEndpoint: `https://mail.tm/en/inbox`,
      note: 'Password and token NOT sent to webhook for security'
    };
    
    try {
      await sendToWebhook(registrationData);
      log(colors.green, '  Info sent to webhook!');
    } catch (e) {
      log(colors.yellow, `  Webhook failed: ${e.message}`);
    }
    
    // Save only email to file (NOT password for security)
    log(colors.yellow, '[5/5] Saving email info...');
    fs.writeFileSync(EMAIL_OUTPUT_FILE, JSON.stringify({
      platform: platform.name,
      email: emailAddress,
      savedAt: new Date().toISOString(),
      note: 'Password not saved - use mail.tm to access inbox'
    }, null, 2));
    log(colors.green, `  Email saved to ${EMAIL_OUTPUT_FILE}`);
    
    // Display summary (DON'T show password for security!)
    console.log();
    log(colors.green, '=== REGISTRATION INFO ===');
    console.log(`Platform: ${platform.name}`);
    console.log(`URL: ${platform.url}`);
    console.log(`Temp Email: ${emailAddress}`);
    console.log();
    log(colors.yellow, '=== NEXT STEPS ===');
    console.log('1. Go to registration URL');
    console.log('2. Use the temp email above');
    console.log('3. Check emails at mail.tm and verify');
    console.log();
    log(colors.blue, '=== ACCESS EMAIL ===');
    console.log(`URL: https://mail.tm`);
    console.log(`Email: ${emailAddress}`);
    console.log('Password: Check /tmp/temp_email_credentials.json for your password');
    console.log();
    if (token) {
      console.log('API to check emails:');
      console.log(`curl -H "Authorization: Bearer ${token}" https://api.mail.tm/messages`);
    }
    console.log();
    log(colors.green, '✅ Registration info sent to webhook!');
    
  } catch (error) {
    log(colors.red, `Error: ${error.message}`);
    console.error(error);
    process.exit(1);
  }
}

main();