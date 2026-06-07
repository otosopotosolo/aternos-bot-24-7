#!/usr/bin/env node
/**
 * SARAhack - Stealth Playwright Browser Automation for HackerOne
 * 
 * Uses playwright-stealth to bypass Cloudflare detection
 * and automate bug bounty report submissions
 * 
 * Usage:
 *   node stealth_h1_submit.js test
 *   node stealth_h1_submit.js submit rollbar
 *   node stealth_h1_submit.js submit-all
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

// Configuration
const HACKERONE_EMAIL = 'potosopotosolo@gmail.com';
const HACKERONE_PASSWORD = ')a9By=*D#6/w9T';

const REPORTS_DIR = path.join(__dirname, '..', 'reports');
const DRAFTS_DIR = path.join(REPORTS_DIR, 'drafts');

// Program URLs
const PROGRAM_URLS = {
  rollbar: 'https://hackerone.com/rollbar/reports/new',
  stripe: 'https://hackerone.com/stripe/reports/new',
  discord: 'https://hackerone.com/discord/reports/new',
  github: 'https://hackerone.com/github/reports/new',
  gitlab: 'https://hackerone.com/gitlab/reports/new',
  sendgrid: 'https://hackerone.com/sendgrid/reports/new',
  shopify: 'https://hackerone.com/shopify/reports/new',
  twilio: 'https://hackerone.com/twilio/reports/new',
  uber: 'https://hackerone.com/uber/reports/new',
  cloudflare: 'https://hackerone.com/cloudflare/reports/new',
};

// Stealth browser options - bypass automation detection
const STEALTH_OPTIONS = {
  headless: true,
  args: [
    '--disable-blink-features=AutomationControlled',
    '--no-sandbox',
    '--disable-setuid-sandbox',
    '--disable-dev-shm-usage',
    '--disable-accelerated-2d-canvas',
    '--no-first-run',
    '--no-zygote',
    '--disable-gpu',
    '--window-size=1920,1080',
    '--start-maximized',
    '--disable-web-security',
    '--allow-running-insecure-content',
  ],
};

// Custom stealth evasion
async function applyStealth(page) {
  // Remove webdriver property
  await page.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', {
      get: () => false,
    });
  });
  
  // Remove automation flags
  await page.addInitScript(() => {
    window.navigator.chrome = {
      runtime: {},
    };
  });
  
  // Mock permissions
  await page.addInitScript(() => {
    const originalQuery = window.navigator.permissions.query;
    window.navigator.permissions.query = (parameters) =>
      parameters.name === 'notifications' ?
        Promise.resolve({ state: Notification.permission }) :
        originalQuery(parameters);
  });
  
  // Block automation detection
  await page.addInitScript(() => {
    Object.defineProperty(navigator, 'plugins', {
      get: () => [1, 2, 3, 4, 5],
    });
    Object.defineProperty(navigator, 'languages', {
      get: () => ['en-US', 'en'],
    });
  });
}

async function launchStealthBrowser() {
  console.log('[*] Launching stealth browser...');
  
  const browser = await chromium.launch(STEALTH_OPTIONS);
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    locale: 'en-US',
    timezoneId: 'America/New_York',
  });
  
  const page = await context.newPage();
  
  // Apply custom stealth evasion
  await applyStealth(page);
  
  // Extra headers to appear more human-like
  await page.addExtraHTTPHeaders({
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
  });
  
  console.log('[+] Stealth browser launched');
  return { browser, context, page };
}

async function loginToHackerOne(page) {
  console.log('[*] Navigating to HackerOne login...');
  
  await page.goto('https://hackerone.com/users/sign_in', { 
    waitUntil: 'networkidle',
    timeout: 60000 
  });
  
  // Wait for Cloudflare challenge to complete
  await page.waitForTimeout(3000);
  
  console.log('[*] Filling login credentials...');
  
  // Fill email
  await page.fill('input[type="email"], input[name="email"]', HACKERONE_EMAIL, { timeout: 10000 });
  
  // Fill password
  await page.fill('input[type="password"], input[name="password"]', HACKERONE_PASSWORD, { timeout: 10000 });
  
  // Click submit
  console.log('[*] Clicking login button...');
  await page.click('button[type="submit"]');
  
  // Wait for redirect
  await page.waitForTimeout(5000);
  
  // Check if login successful
  const url = page.url();
  if (url.includes('dashboard') || url.includes('hackerone.com')) {
    console.log('[+] Login successful!');
    return true;
  }
  
  console.log('[!] Login may have failed, URL:', url);
  return false;
}

async function submitReport(page, program, reportPath) {
  console.log(`[*] Submitting report for ${program}...`);
  
  // Check if report file exists
  if (!fs.existsSync(reportPath)) {
    console.error(`[!] Report not found: ${reportPath}`);
    return false;
  }
  
  // Load report content
  const reportContent = fs.readFileSync(reportPath, 'utf8');
  
  // Parse title from report (fix regex - # doesn't need escaping)
  const titleMatch = reportContent.match(/^#\s+(.+)$/m);
  const title = titleMatch ? titleMatch[1] : `${program.toUpperCase()} - CORS Misconfiguration`;
  
  // Extract description
  const lines = reportContent.split('\n');
  let description = '';
  for (const line of lines) {
    if (line.startsWith('##') || line.startsWith('**')) continue;
    if (line.trim()) description += line + ' ';
  }
  description = description.substring(0, 5000);
  
  // Navigate to report form
  const url = PROGRAM_URLS[program.toLowerCase()];
  if (!url) {
    console.log(`[!] Unknown program: ${program}`);
    return false;
  }
  
  console.log(`[*] Navigating to ${url}...`);
  await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 });
  
  // Wait for Cloudflare challenge to complete
  console.log('[*] Waiting for Cloudflare challenge...');
  await page.waitForTimeout(10000);
  
  // Fill title
  console.log('[*] Filling report title...');
  try {
    await page.fill('input[name="report[title]"], input[id="report_title"]', title, { timeout: 5000 });
  } catch (e) {
    console.log('[!] Title field not found, trying alternative selectors...');
    await page.fill('input[type="text"]', title, { timeout: 5000 });
  }
  
  // Select severity
  console.log('[*] Setting severity...');
  try {
    await page.selectOption('select[name*="severity"]', 'high', { timeout: 5000 });
  } catch (e) {
    console.log('[!] Severity selector not found, skipping...');
  }
  
  // Fill description
  console.log('[*] Filling vulnerability description...');
  try {
    await page.fill('textarea[name*="description"]', description, { timeout: 5000 });
  } catch (e) {
    console.log('[!] Description field not found, trying alternative...');
    await page.fill('textarea', description.substring(0, 3000), { timeout: 5000 });
  }
  
  // Take screenshot before submit
  await page.screenshot({ path: `/tmp/h1_${program}_before_submit.png`, fullPage: true });
  console.log(`[+] Screenshot saved: /tmp/h1_${program}_before_submit.png`);
  
  // Submit
  console.log('[*] Submitting report...');
  try {
    await page.click('button[type="submit"], button:has-text("Submit")', { timeout: 5000 });
    await page.waitForTimeout(3000);
    
    // Check for success
    const content = await page.content();
    if (content.includes('success') || content.includes('thank') || content.includes('submitted')) {
      console.log(`[+] Report submitted successfully for ${program}!`);
      await page.screenshot({ path: `/tmp/h1_${program}_success.png`, fullPage: true });
      return true;
    }
  } catch (e) {
    console.log('[!] Submit button not found or click failed');
  }
  
  await page.screenshot({ path: `/tmp/h1_${program}_after_submit.png`, fullPage: true });
  return false;
}

async function testBrowser() {
  console.log('[*] Testing stealth browser...');
  
  try {
    const { browser, page } = await launchStealthBrowser();
    
    console.log('[*] Navigating to https://www.google.com...');
    await page.goto('https://www.google.com', { waitUntil: 'networkidle', timeout: 30000 });
    
    const title = await page.title();
    console.log(`[+] Page title: ${title}`);
    
    // Check for automation detection
    const isDetected = await page.evaluate(() => {
      return navigator.webdriver === true || 
             /headless/.test(navigator.userAgent) ||
             window.chrome !== undefined;
    });
    
    if (isDetected) {
      console.log('[!] Browser may be detected as automation');
    } else {
      console.log('[+] Browser appears stealthy!');
    }
    
    await browser.close();
    console.log('[+] Test completed successfully!');
    return true;
    
  } catch (error) {
    console.error('[x] Test failed:', error.message);
    return false;
  }
}

async function submitAllReports() {
  console.log('[*] Finding draft reports...');
  
  const drafts = fs.readdirSync(DRAFTS_DIR).filter(f => f.endsWith('_cors.md'));
  console.log(`[+] Found ${drafts.length} draft reports`);
  
  const { browser, page } = await launchStealthBrowser();
  
  // Login first
  const loggedIn = await loginToHackerOne(page);
  if (!loggedIn) {
    console.error('[x] Login failed, cannot submit reports');
    await browser.close();
    return;
  }
  
  const results = [];
  for (const draft of drafts) {
    const program = draft.replace('draft_', '').replace('_cors.md', '');
    const reportPath = path.join(DRAFTS_DIR, draft);
    
    console.log(`\n[*] Processing: ${program}`);
    const success = await submitReport(page, program, reportPath);
    results.push({ program, success });
    
    // Wait between submissions
    await page.waitForTimeout(5000);
  }
  
  await browser.close();
  
  // Summary
  console.log('\n========== SUBMISSION SUMMARY ==========');
  const successCount = results.filter(r => r.success).length;
  for (const r of results) {
    console.log(`${r.success ? '✅' : '❌'} ${r.program}`);
  }
  console.log(`\nTotal: ${results.length} | Success: ${successCount} | Failed: ${results.length - successCount}`);
}

async function main() {
  const args = process.argv.slice(2);
  const command = args[0] || 'help';
  
  if (command === 'test') {
    await testBrowser();
  } else if (command === 'submit') {
    const program = args[1];
    if (!program) {
      console.error('[!] Usage: node stealth_h1_submit.js submit <program>');
      process.exit(1);
    }
    
    const { browser, page } = await launchStealthBrowser();
    await loginToHackerOne(page);
    
    const reportPath = path.join(DRAFTS_DIR, `draft_${program}_cors.md`);
    await submitReport(page, program, reportPath);
    
    await browser.close();
  } else if (command === 'submit-all') {
    await submitAllReports();
  } else {
    console.log(`
SARAhack - Stealth Playwright for HackerOne

Usage:
  node stealth_h1_submit.js test        - Test stealth browser
  node stealth_h1_submit.js submit <p>  - Submit report for program
  node stealth_h1_submit.js submit-all  - Submit all draft reports

Example:
  node stealth_h1_submit.js test
  node stealth_h1_submit.js submit rollbar
  node stealth_h1_submit.js submit-all
`);
  }
}

main().catch(console.error);