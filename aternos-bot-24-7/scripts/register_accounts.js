const { chromium } = require('playwright');

const EMAIL = 'potosopotosolo@gmail.com';
const PASSWORD = 'TempPass123!@#';

async function registerHoneygain() {
  console.log('🔍 Starting Honeygain registration...');
  const browser = await chromium.launch({ 
    headless: true,
    executablePath: '/home/runner/workspace/.cache/ms-playwright/chromium-1223/chrome-linux64/chrome'
  });
  const page = await browser.newPage();
  
  try {
    await page.goto('https://dashboard.honeygain.com/', { timeout: 30000 });
    console.log('✅ Page loaded');
    
    // Check if already logged in or redirect to signup
    await page.waitForTimeout(2000);
    
    const title = await page.title();
    console.log('📄 Page title:', title);
    
    // Try to find signup link
    const signupLink = await page.$('a[href*="signup"], a[href*="register"]');
    if (signupLink) {
      await signupLink.click();
      await page.waitForTimeout(1000);
    }
    
    // Take screenshot for reference
    console.log('📸 Current URL:', page.url());
    console.log('⚠️ Manual registration may be required at:', page.url());
    
  } catch (error) {
    console.log('❌ Error:', error.message);
  } finally {
    await browser.close();
  }
}

async function registerEarnApp() {
  console.log('\n🔍 Starting EarnApp registration...');
  // EarnApp requires Google signup mostly
  console.log('📋 EarnApp signup URL: https://earnapp.com/');
}

async function registerPawns() {
  console.log('\n🔍 Starting Pawns.app registration...');
  console.log('📋 Pawns.app signup URL: https://pawns.app/');
}

async function main() {
  console.log('🚀 Starting registration process for passive income platforms...\n');
  
  await registerHoneygain();
  await registerEarnApp();
  await registerPawns();
  
  console.log('\n📋 Summary:');
  console.log('These platforms require human verification (CAPTCHA) during signup.');
  console.log('Please register manually using your device at:');
  console.log('- Honeygain: https://dashboard.honeygain.com/');
  console.log('- EarnApp: https://earnapp.com/');
  console.log('- Pawns.app: https://pawns.app/');
  console.log('\nUse email: ' + EMAIL);
}

main().catch(console.error);