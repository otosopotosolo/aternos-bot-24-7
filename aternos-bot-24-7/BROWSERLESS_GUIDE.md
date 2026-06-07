# คู่มือการใช้งาน Browserless.io สำหรับ Browser Automation

## ภาพรวม

Browserless.io เป็นบริการ "Browser-as-a-Service" ที่ให้ remote Chrome browser ผ่าน WebSocket API ช่วยให้รัน browser automation ได้โดยไม่ต้องติดตั้ง Chrome บนเครื่อง local

## ขั้นตอนการสมัคร

### 1. สมัครบัญชี

1. ไปที่ https://www.browserless.io
2. คลิก "Sign Up" หรือ "Get Started"
3. กรอกข้อมูล: Email, Password
4. ยืนยัน email

### 2. รับ API Token

1. Login เข้า dashboard
2. ไปที่ Settings หรือ API Section
3. Copy API Token (จะเป็น string ยาวประมาณ 32+ characters)

**Token จะมีหน้าตาแบบนี้:**
```
browserless_fp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## Free Tier (เริ่มต้นฟรี)

- **หน่วยฟรี:** ~100 units/month
- **Concurrency:** 2 simultaneous sessions
- **เพียงพอสำหรับ:** ทดสอบและใช้งานเบื้องต้น

**หมายเหตุ:** แต่ละ page load ใช้ประมาณ 1-5 units ขึ้นอยู่กับความซับซ้อน

## การใช้งานกับ Playwright

### วิธีที่ 1: Playwright.connectOverCDP

```javascript
const { chromium } = require('playwright');

async function main() {
  const browser = await chromium.connectOverCDP(
    'wss://chrome.browserless.io?token=YOUR_API_TOKEN'
  );
  
  const page = await browser.newPage();
  await page.goto('https://example.com');
  
  const title = await page.title();
  console.log('Page title:', title);
  
  await browser.close();
}

main();
```

### วิธีที่ 2: playwright.connect (CDP directly)

```javascript
const { chromium } = require('playwright');

const browser = await chromium.connect(
  'wss://chrome.browserless.io?token=YOUR_API_TOKEN'
);
const page = await browser.newPage();
await page.goto('https://example.com');
await browser.close();
```

## การใช้งานกับ Puppeteer

```javascript
const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.connect({
    browserWSEndpoint: 'wss://chrome.browserless.io?token=YOUR_API_TOKEN'
  });
  
  const page = await browser.newPage();
  await page.goto('https://example.com');
  
  await browser.disconnect();
})();
```

## การรัน Script บน Replit

### ตั้งค่า Environment Variable

```bash
export BROWSERLESS_TOKEN=your_api_token_here
```

### รัน remote_browser_submit.js

```bash
cd /home/runner/workspace/aternos-bot-24-7/freebuff

# Test connection
BROWSERLESS_TOKEN=your_token node remote_browser_submit.js test

# Submit single report
BROWSERLESS_TOKEN=your_token node remote_browser_submit.js submit ../reports/drafts/draft_001_cors.md

# Batch submit
BROWSERLESS_TOKEN=your_token node remote_browser_submit.js batch ./reports/drafts
```

## ค่าใช้จ่ายและการจัดการ

| Plan | ราคา | Units/Month | Concurrency |
|------|------|-------------|-------------|
| Free | ฟรี | ~100 | 2 |
| Starter | ตรวจสอบเว็บไซต์ | 5,000 | 5 |
| Pro | ตรวจสอบเว็บไซต์ | 15,000 | 10 |

**เคล็ดลับ:** Monitor usage ที่ dashboard เพื่อไม่ให้เกิน limit

## Troubleshooting

### Error: "Authentication required"

- ตรวจสอบว่าใส่ token ถูกต้อง
- Token ต้องอยู่ในรูปแบบ: `?token=YOUR_TOKEN`

### Error: "Session limit reached"

- รอสักครู่แล้วลองใหม่
- หรือ upgrade plan เพื่อเพิ่ม concurrency

### Error: "Connection closed"

- ตรวจสอบ internet connection
- ลอง reconnect

## Alternatives (กรณี Browserless ไม่เหมาะ)

| Service | Website | Notes |
|---------|---------|-------|
| ScrapingBee | scrapingbee.com | Similar, 1000 free credits |
| ScrapingAnt | scrapingant.com | Cheap, reliable |
| Oxylabs | oxylabs.io | Enterprise grade |
| Browserstack | browserstack.com | Real devices |

## ข้อควรระวัง

⚠️ **เก็บ Token ให้ปลอดภัย:**
- ไม่ commit token ลง git
- ใช้ environment variable แทน

⚠️ **Monitor Usage:**
- ตรวจสอบ units ที่ใช้แต่ละเดือน
- ตั้ง alert ถ้าใกล้ limit

⚠️ **Respect Rate Limits:**
- ใช้ delay ระหว่าง requests
- ไม่ flood ด้วย requests จำนวนมาก

## Quick Start Checklist

- [ ] สมัครบัญชี Browserless.io
- [ ] รับ API Token จาก dashboard
- [ ] ทดสอบ: `BROWSERLESS_TOKEN=xxx node remote_browser_submit.js test`
- [ ] ถ้าสำเร็จ ลอง submit report จริง
- [ ] Monitor usage ที่ dashboard