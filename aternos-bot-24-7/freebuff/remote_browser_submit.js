/**
 * Remote Browser Automation for Freebuff HackerOne Submission
 * 
 * Uses Browserless.io or similar remote browser service
 * to avoid system dependency issues in Replit
 * 
 * Usage:
 *   BROWSERLESS_TOKEN=your_token node remote_browser_submit.js submit <report_path>
 *   node remote_browser_submit.js test
 */

const playwright = require('playwright');

// Configuration
const BROWSERLESS_TOKEN = process.env.BROWSERLESS_TOKEN || '';
if (!BROWSERLESS_TOKEN) {
  throw new Error('BROWSERLESS_TOKEN environment variable is required\nUsage: BROWSERLESS_TOKEN=your_token node remote_browser_submit.js test');
}
const BROWSERLESS_WS = `wss://chrome.browserless.io?token=${BROWSERLESS_TOKEN}`;
const FREE_URL = process.env.FREE_URL || 'https://freebuff.com';

// Alternative endpoints
const ALT_ENDPOINTS = [
  'wss://chrome.browserless.io',
  'wss://brd.browserless.io',
];

// Stealth evasion settings
const STEALTH_SETTINGS = {
  headless: true,
  ignoreHTTPSErrors: true,
  viewport: { width: 1920, height: 1080 },
  userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
};

/**
 * Apply stealth evasion to page
 */
async function applyStealth(page) {
  await page.evaluateOnNewDocument(() => {
    // Remove webdriver property
    Object.defineProperty(navigator, 'webdriver', { get: () => false });
    
    // Mock chrome object
    window.chrome = {
      runtime: {},
      csi: () => {},
      loadTimes: () => {},
    };
    
    // Mock permissions
    const originalQuery = window.navigator.permissions.query;
    window.navigator.permissions.query = (parameters) => (
      parameters.name === 'notifications' ?
        Promise.resolve({ state: Notification.permission }) :
        originalQuery(parameters)
    );
  });
  
  // Additional stealth via CDP
  await page.addInitScript(() => {
    // Spoof automation flags
    Object.defineProperty(navigator, 'plugins', {
      get: () => [1, 2, 3, 4, 5],
    });
    Object.defineProperty(navigator, 'languages', {
      get: () => ['en-US', 'en', 'en-GB'],
    });
  });
}

/**
 * Connect to remote browser
 */
async function connectToRemoteBrowser() {
  console.log('[~] Connecting to remote browser...');
  
  // Token validation happens at module load time
  
  try {
    const browser = await playwright.chromium.connectOverCDP(BROWSERLESS_WS);
    console.log('[+] Connected to remote browser!');
    return browser;
  } catch (error) {
    console.error('[-] Failed to connect:', error.message);
    throw error;
  }
}

/**
 * Test connection to freebuff
 */
async function testConnection() {
  console.log('[~] Testing freebuff connection...');
  
  let browser;
  let success = false;
  
  try {
    browser = await connectToRemoteBrowser();
    const context = await browser.newContext(STEALTH_SETTINGS);
    const page = await context.newPage();
    
    await applyStealth(page);
    
    console.log('[~] Navigating to freebuff.com...');
    await page.goto(FREE_URL, { waitUntil: 'networkidle', timeout: 30000 });
    
    const title = await page.title();
    console.log('[+] Page title:', title);
    
    // Check for Cloudflare challenge
    const cfChallenge = await page.$('[data-translate="challenge_headline"]');
    if (cfChallenge) {
      console.log('[!] Cloudflare challenge detected, waiting...');
      await page.waitForTimeout(10000);
    }
    
    // Check if logged in
    const loginBtn = await page.$('a[href*="login"], button:has-text("Login"), button:has-text("Sign in")');
    if (loginBtn) {
      console.log('[i] User appears to be logged out');
    } else {
      console.log('[+] User appears to be logged in!');
    }
    
    success = true;
    
    await context.close();
  } catch (error) {
    console.error('[-] Test failed:', error.message);
  } finally {
    if (browser) await browser.close();
  }
  
  return success;
}

/**
 * Submit report via freebuff
 */
async function submitReport(reportPath) {
  console.log('[~] Submitting report:', reportPath);
  
  const fs = require('fs');
  
  if (!fs.existsSync(reportPath)) {
    console.error('[-] Report not found:', reportPath);
    return false;
  }
  
  const reportContent = fs.readFileSync(reportPath, 'utf8');
  
  // Extract title from markdown (first # heading)
  const titleMatch = reportContent.match(/^#\s+(.+)$/m);
  const title = titleMatch ? titleMatch[1].trim() : 'Untitled Report';
  
  // Extract severity from report
  let severity = 'medium';
  if (reportContent.includes('**Severity:**') || reportContent.includes('Severity:')) {
    const sevMatch = reportContent.match(/\b(critical|high|medium|low)\b/i);
    if (sevMatch) severity = sevMatch[1].toLowerCase();
  }
  
  let browser;
  
  try {
    browser = await connectToRemoteBrowser();
    const context = await browser.newContext(STEALTH_SETTINGS);
    const page = await context.newPage();
    
    await applyStealth(page);
    
    console.log('[~] Navigating to freebuff...');
    await page.goto(FREE_URL, { waitUntil: 'networkidle', timeout: 30000 });
    
    // Wait for any Cloudflare challenge
    // Wait for Cloudflare challenge to resolve (can take 15+ seconds)
    await page.waitForTimeout(15000);
    
    // Navigate to submit page (adjust selector based on actual site)
    console.log('[~] Looking for submit interface...');
    
    // Try to find and click submit button
    const submitBtn = await page.$('a[href*="submit"], button:has-text("Submit"), button:has-text("New Report")');
    if (submitBtn) {
      await submitBtn.click();
      await page.waitForTimeout(2000);
    }
    
    // Fill in report details
    console.log('[~] Filling report form...');
    
    const titleInput = await page.$('input[name*="title"], input[name*="name"], textarea[name*="title"]');
    if (titleInput) {
      await titleInput.fill(title);
      console.log('[+] Filled title:', title);
    }
    
    // Fill description (full report content)
    const descInput = await page.$('textarea[name*="description"], textarea[name*="report"], textarea[name*="details"]');
    if (descInput) {
      await descInput.fill(reportContent);
      console.log('[+] Filled description');
    }
    
    // Select severity if available
    const sevInput = await page.$('select[name*="severity"], select[name*="priority"]');
    if (sevInput) {
      await sevInput.selectOption(severity);
      console.log('[+] Selected severity:', severity);
    }
    
    // Submit
    const submitButton = await page.$('button[type="submit"], button:has-text("Submit"), button:has-text("Send")');
    if (submitButton) {
      await submitButton.click();
      await page.waitForTimeout(3000);
      console.log('[+] Report submitted!');
    }
    
    await context.close();
    return true;
    
  } catch (error) {
    console.error('[-] Submission failed:', error.message);
    return false;
  } finally {
    if (browser) await browser.close();
  }
}

/**
 * Main CLI
 */
async function main() {
  const args = process.argv.slice(2);
  const command = args[0] || 'test';
  
  console.log('=== Freebuff Remote Browser Automation ===');
  console.log('Browser:', BROWSERLESS_WS ? 'Remote (Browserless)' : 'Local');
  console.log('');
  
  switch (command) {
    case 'test':
      await testConnection();
      break;
      
    case 'submit':
      const reportPath = args[1];
      if (!reportPath) {
        console.error('Usage: node remote_browser_submit.js submit <report_path>');
        process.exit(1);
      }
      await submitReport(reportPath);
      break;
      
    case 'batch':
      const reportsDir = args[1] || './reports/drafts';
      const fs = require('fs');
      const files = fs.readdirSync(reportsDir).filter(f => f.endsWith('.md'));
      console.log(`[i] Found ${files.length} reports to submit`);
      for (const file of files) {
        await submitReport(`${reportsDir}/${file}`);
        await new Promise(r => setTimeout(r, 2000)); // Rate limit
      }
      break;
      
    default:
      console.log('Commands:');
      console.log('  test              - Test connection to freebuff');
      console.log('  submit <path>     - Submit a single report');
      console.log('  batch <dir>       - Submit all reports in directory');
      console.log('');
      console.log('Environment variables:');
      console.log('  BROWSERLESS_TOKEN - Your Browserless.io API token');
      console.log('  FREE_URL          - Freebuff URL (default: https://freebuff.com)');
  }
}

main().catch(console.error);