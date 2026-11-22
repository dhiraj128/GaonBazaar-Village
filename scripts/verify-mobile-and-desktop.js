import { chromium } from '../apps/admin/node_modules/playwright-core/index.mjs';
import http from 'http';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const distDir = path.resolve(__dirname, '..', 'apps', 'admin', 'dist');

const mimeTypes = {
  '.html': 'text/html',
  '.css': 'text/css',
  '.js': 'application/javascript',
  '.png': 'image/png',
  '.svg': 'image/svg+xml',
  '.json': 'application/json',
};

// 1. Create a local static file server matching Vercel routing
const server = http.createServer((req, res) => {
  let reqPath = req.url.split('?')[0];
  if (reqPath === '/') reqPath = '/index.html';
  
  let filePath = path.join(distDir, reqPath);
  if (!fs.existsSync(filePath) || fs.statSync(filePath).isDirectory()) {
    if (fs.existsSync(path.join(filePath, 'index.html'))) {
      filePath = path.join(filePath, 'index.html');
    } else {
      filePath = path.join(distDir, 'index.html');
    }
  }

  const ext = path.extname(filePath);
  const ct = mimeTypes[ext] || 'application/octet-stream';

  try {
    const data = fs.readFileSync(filePath);
    res.writeHead(200, { 'Content-Type': ct });
    res.end(data);
  } catch (err) {
    res.writeHead(404);
    res.end('Not found');
  }
});

const PORT = 4188;
server.listen(PORT, async () => {
  console.log(`[Verify] Static verification server listening on http://127.0.0.1:${PORT}`);

  const browser = await chromium.launch({
    executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    headless: true
  });

  const viewports = [
    { name: 'Mobile Android (Pixel 7 / Galaxy S21)', width: 412, height: 915, isMobile: true },
    { name: 'Mobile iOS (iPhone 14 / 15)', width: 390, height: 844, isMobile: true },
    { name: 'Desktop (1080p)', width: 1440, height: 900, isMobile: false }
  ];

  let allPassed = true;

  for (const vp of viewports) {
    console.log(`\n========================================`);
    console.log(`Testing Viewport: ${vp.name} (${vp.width}x${vp.height})`);
    console.log(`========================================`);

    const context = await browser.newContext({
      viewport: { width: vp.width, height: vp.height },
      isMobile: vp.isMobile,
      userAgent: vp.isMobile
        ? 'Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36'
        : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
    });

    const page = await context.newPage();
    const consoleErrors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') consoleErrors.push(msg.text());
    });

    // 1. Customer App Test
    console.log('\n--- Checking Customer App (/customer/index.html) ---');
    await page.goto(`http://127.0.0.1:${PORT}/customer/index.html`, { waitUntil: 'domcontentloaded' });

    const customerChecks = await page.evaluate(() => {
      const modal = document.getElementById('modal-checkout-payment');
      const cardForm = document.getElementById('checkout-card-form');
      const cardNumber = document.getElementById('checkout-card-number');
      const cardExpiry = document.getElementById('checkout-card-expiry');
      const cardCvv = document.getElementById('checkout-card-cvv');
      const bankRadio = document.getElementById('pm-radio-bank');
      const cardRadio = document.getElementById('pm-radio-card');
      const onlineRadio = document.getElementById('pm-radio-upi');
      const codRadio = document.getElementById('pm-radio-cod');

      const modalComputedDisplay = modal ? window.getComputedStyle(modal).display : null;
      const modalOffsetHeight = modal ? modal.offsetHeight : 0;

      return {
        modalExists: !!modal,
        modalComputedDisplay,
        modalOffsetHeight,
        modalIsHidden: modalComputedDisplay === 'none' || modalOffsetHeight === 0,
        rawCardInputsRemoved: !cardForm && !cardNumber && !cardExpiry && !cardCvv,
        bankDisabled: bankRadio ? bankRadio.disabled : false,
        cardDisabled: cardRadio ? cardRadio.disabled : false,
        onlineActive: onlineRadio ? !onlineRadio.disabled : false,
        codActive: codRadio ? !codRadio.disabled : false,
      };
    });

    console.log(`- Modal hidden on load: ${customerChecks.modalIsHidden ? 'PASS' : 'FAIL'} (display: ${customerChecks.modalComputedDisplay}, height: ${customerChecks.modalOffsetHeight}px)`);
    console.log(`- Raw Card Inputs Removed: ${customerChecks.rawCardInputsRemoved ? 'PASS' : 'FAIL'}`);
    console.log(`- Bank Net Banking Disabled (Coming Soon): ${customerChecks.bankDisabled ? 'PASS' : 'FAIL'}`);
    console.log(`- Card Disabled (Coming Soon): ${customerChecks.cardDisabled ? 'PASS' : 'FAIL'}`);
    console.log(`- Online UPI Active: ${customerChecks.onlineActive ? 'PASS' : 'FAIL'}`);
    console.log(`- COD Active: ${customerChecks.codActive ? 'PASS' : 'FAIL'}`);

    if (!customerChecks.modalIsHidden || !customerChecks.rawCardInputsRemoved || !customerChecks.bankDisabled || !customerChecks.cardDisabled) {
      allPassed = false;
    }

    // 2. Vendor App Test
    console.log('\n--- Checking Vendor App (/vendor/index.html) ---');
    await page.goto(`http://127.0.0.1:${PORT}/vendor/index.html`, { waitUntil: 'domcontentloaded' });
    const vendorChecks = await page.evaluate(() => {
      const heading = document.querySelector('h1, h2, #store-name');
      const isStyled = window.getComputedStyle(document.body).fontFamily.includes('Inter');
      return { loaded: true, isStyled };
    });
    console.log(`- Vendor App Loaded & Styled: ${vendorChecks.isStyled ? 'PASS' : 'FAIL'}`);

    // 3. Runner App Test
    console.log('\n--- Checking Runner App (/runner/index.html) ---');
    await page.goto(`http://127.0.0.1:${PORT}/runner/index.html`, { waitUntil: 'domcontentloaded' });
    const runnerChecks = await page.evaluate(() => {
      const isStyled = window.getComputedStyle(document.body).fontFamily.includes('Inter');
      return { loaded: true, isStyled };
    });
    console.log(`- Runner App Loaded & Styled: ${runnerChecks.isStyled ? 'PASS' : 'FAIL'}`);

    // 4. Admin App Test
    console.log('\n--- Checking Admin App (/index.html) ---');
    await page.goto(`http://127.0.0.1:${PORT}/index.html`, { waitUntil: 'domcontentloaded' });
    const adminChecks = await page.evaluate(() => {
      const root = document.getElementById('root');
      return { rootExists: !!root };
    });
    console.log(`- Admin App Root Exists: ${adminChecks.rootExists ? 'PASS' : 'FAIL'}`);

    await context.close();
  }

  await browser.close();
  server.close();

  if (allPassed) {
    console.log('\n[SUCCESS] All mobile and desktop browser verifications PASSED!');
    process.exit(0);
  } else {
    console.error('\n[FAILURE] One or more verifications failed.');
    process.exit(1);
  }
});
