const http = require('http');
const fs = require('fs');
const path = require('path');
const { chromium } = require('../apps/admin/node_modules/playwright');

const PUBLIC_DIR = path.join(__dirname, '../apps/admin/public');
const ARTIFACTS_DIR = 'C:/Users/dhira/.gemini/antigravity/brain/918c8085-b60b-40a9-a077-a3344458bcc5';

const MIME_TYPES = {
  '.html': 'text/html',
  '.css': 'text/css',
  '.js': 'application/javascript',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.svg': 'image/svg+xml'
};

const server = http.createServer((req, res) => {
  let reqPath = req.url.split('?')[0];
  if (reqPath === '/' || reqPath === '/customer') reqPath = '/customer/index.html';
  else if (reqPath === '/vendor') reqPath = '/vendor/index.html';
  else if (reqPath === '/runner') reqPath = '/runner/index.html';
  
  const filePath = path.join(PUBLIC_DIR, reqPath);
  fs.readFile(filePath, (err, content) => {
    if (err) {
      res.writeHead(404);
      res.end('Not Found: ' + reqPath);
    } else {
      res.writeHead(200, { 
        'Content-Type': MIME_TYPES[path.extname(filePath)] || 'text/plain',
        'Cache-Control': 'no-cache'
      });
      res.end(content);
    }
  });
});

async function runAudit() {
  const browser = await chromium.launch({ headless: true });
  const results = { customer: {}, vendor: {}, runner: {}, errors: [] };

  try {
    // -------------------------------------------------------------------------
    // 1. AUDIT CUSTOMER APP
    // -------------------------------------------------------------------------
    console.log('\n================ AUDITING CUSTOMER PORTAL ================');
    const customerContext = await browser.newContext({
      viewport: { width: 390, height: 844 },
      deviceScaleFactor: 2
    });
    const page = await customerContext.newPage();
    page.on('console', msg => {
      if (msg.type() === 'error') results.errors.push(`Customer Console Error: ${msg.text()}`);
    });
    page.on('pageerror', err => results.errors.push(`Customer Page Error: ${err.message}`));

    // Set mock authenticated state to enter main dashboard immediately
    await page.addInitScript(() => {
      localStorage.setItem('gb_customer_authenticated', 'true');
      localStorage.setItem('gb_customer_jwt', 'mock-jwt-token');
      localStorage.setItem('gb_user_lang', 'en');
    });

    await page.goto('http://127.0.0.1:8093/customer/index.html', { waitUntil: 'networkidle' });
    await page.waitForTimeout(1000);

    // Switch to AI Assistant tab
    console.log('-> Navigating to Customer AI Assistant tab...');
    await page.evaluate(() => {
      if (typeof switchTab === 'function') switchTab('ai');
    });
    await page.waitForTimeout(500);

    const aiMetrics = await page.evaluate(() => {
      const micBtn = document.getElementById('main-mic-btn');
      const micSvg = micBtn ? micBtn.querySelector('svg') : null;
      const micBox = micSvg ? micSvg.getBoundingClientRect() : null;

      const sendBtn = document.querySelector('#view-ai button[title="Send Query"]');
      const sendSvg = sendBtn ? sendBtn.querySelector('svg') : null;
      const sendBox = sendSvg ? sendSvg.getBoundingClientRect() : null;

      const headerBot = document.querySelector('#view-ai header .w-9.h-9.rounded-full.bg-emerald-100');
      const headerBotSvg = headerBot ? headerBot.querySelector('svg') : null;
      const headerBotBox = headerBotSvg ? headerBotSvg.getBoundingClientRect() : null;

      const headerBack = document.querySelector('#view-ai header button[aria-label="Back"]');
      const headerBackSvg = headerBack ? headerBack.querySelector('svg') : null;
      const headerBackBox = headerBackSvg ? headerBackSvg.getBoundingClientRect() : null;

      return {
        micVisible: micBox && micBox.width > 0 && micBox.height > 0,
        micWidth: micBox ? micBox.width : 0,
        micHeight: micBox ? micBox.height : 0,
        sendVisible: sendBox && sendBox.width > 0 && sendBox.height > 0,
        sendWidth: sendBox ? sendBox.width : 0,
        sendHeight: sendBox ? sendBox.height : 0,
        headerBotVisible: headerBotBox && headerBotBox.width > 0 && headerBotBox.height > 0,
        headerBotWidth: headerBotBox ? headerBotBox.width : 0,
        headerBotHeight: headerBotBox ? headerBotBox.height : 0,
        headerBackVisible: headerBackBox && headerBackBox.width > 0 && headerBackBox.height > 0,
        headerBackWidth: headerBackBox ? headerBackBox.width : 0,
        headerBackHeight: headerBackBox ? headerBackBox.height : 0
      };
    });

    results.customer.ai = aiMetrics;
    console.log('Customer AI Assistant Icon Metrics:', JSON.stringify(aiMetrics, null, 2));

    // Capture Customer AI Assistant screenshot
    const customerAiShotPath = path.join(ARTIFACTS_DIR, 'audit_customer_ai_assistant.png');
    await page.screenshot({ path: customerAiShotPath, fullPage: false });
    console.log('Saved:', customerAiShotPath);

    // Switch back to Home tab
    console.log('-> Navigating to Customer Home tab...');
    await page.evaluate(() => {
      if (typeof switchTab === 'function') switchTab('home');
    });
    await page.waitForTimeout(500);

    const homeMetrics = await page.evaluate(() => {
      const searchMic = document.getElementById('home-search-mic-btn');
      const searchMicSvg = searchMic ? searchMic.querySelector('svg') : null;
      const searchMicBox = searchMicSvg ? searchMicSvg.getBoundingClientRect() : null;

      const searchInputIcon = document.querySelector('#view-home .relative.flex.items-center i[data-lucide="search"] svg, #view-home .relative.flex.items-center svg.lucide-search');
      const searchInputIconBox = searchInputIcon ? searchInputIcon.getBoundingClientRect() : null;

      const bottomNav = document.getElementById('customer-bottom-nav');
      const navButtons = bottomNav ? Array.from(bottomNav.querySelectorAll('button')).map(btn => {
        const svg = btn.querySelector('svg');
        const box = svg ? svg.getBoundingClientRect() : null;
        const text = btn.querySelector('span') ? btn.querySelector('span').innerText : '';
        return {
          id: btn.id,
          text: text,
          hasSvg: !!svg,
          visible: box && box.width > 0 && box.height > 0
        };
      }) : [];

      return {
        searchMicVisible: searchMicBox && searchMicBox.width > 0 && searchMicBox.height > 0,
        searchMicWidth: searchMicBox ? searchMicBox.width : 0,
        searchMicHeight: searchMicBox ? searchMicBox.height : 0,
        searchInputIconVisible: searchInputIconBox && searchInputIconBox.width > 0 && searchInputIconBox.height > 0,
        navButtons: navButtons
      };
    });

    results.customer.home = homeMetrics;
    console.log('Customer Home Icon Metrics:', JSON.stringify(homeMetrics, null, 2));

    // Capture Customer Home screenshot
    const customerHomeShotPath = path.join(ARTIFACTS_DIR, 'audit_customer_home.png');
    await page.screenshot({ path: customerHomeShotPath, fullPage: false });
    console.log('Saved:', customerHomeShotPath);

    // Check Hindi Language on Customer Home
    console.log('-> Switching to Hindi Language on Customer Home...');
    await page.evaluate(() => {
      if (typeof toggleQuickLanguage === 'function') toggleQuickLanguage();
    });
    await page.waitForTimeout(500);
    const customerHindiShotPath = path.join(ARTIFACTS_DIR, 'audit_customer_hindi_home.png');
    await page.screenshot({ path: customerHindiShotPath, fullPage: false });
    console.log('Saved:', customerHindiShotPath);

    await customerContext.close();

    // -------------------------------------------------------------------------
    // 2. AUDIT VENDOR PORTAL
    // -------------------------------------------------------------------------
    console.log('\n================ AUDITING VENDOR PORTAL ================');
    const vendorContext = await browser.newContext({
      viewport: { width: 390, height: 844 },
      deviceScaleFactor: 2
    });
    const vendorPage = await vendorContext.newPage();
    vendorPage.on('console', msg => {
      if (msg.type() === 'error') results.errors.push(`Vendor Console Error: ${msg.text()}`);
    });
    vendorPage.on('pageerror', err => results.errors.push(`Vendor Page Error: ${err.message}`));

    await vendorPage.goto('http://127.0.0.1:8093/vendor/index.html', { waitUntil: 'networkidle' });
    await vendorPage.waitForTimeout(500);

    // Capture Vendor Language Onboarding
    const vendorLangShotPath = path.join(ARTIFACTS_DIR, 'audit_vendor_onboarding.png');
    await vendorPage.screenshot({ path: vendorLangShotPath, fullPage: false });
    console.log('Saved:', vendorLangShotPath);

    // Open Vendor Dashboard directly
    console.log('-> Opening Vendor Dashboard...');
    await vendorPage.evaluate(() => {
      if (typeof openDashboard === 'function') openDashboard('inventory');
    });
    await vendorPage.waitForTimeout(500);

    const vendorMetrics = await vendorPage.evaluate(() => {
      const allLucideTags = document.querySelectorAll('i[data-lucide]');
      const unrendered = Array.from(allLucideTags).filter(el => !el.querySelector('svg') && el.tagName.toLowerCase() !== 'svg');
      
      const allSvgs = document.querySelectorAll('svg');
      const visibleSvgs = Array.from(allSvgs).filter(s => {
        const r = s.getBoundingClientRect();
        return r.width > 0 && r.height > 0;
      });

      return {
        totalLucideNodes: allLucideTags.length,
        unrenderedCount: unrendered.length,
        unrenderedNames: unrendered.slice(0, 10).map(el => el.getAttribute('data-lucide')),
        totalSvgs: allSvgs.length,
        visibleSvgsCount: visibleSvgs.length,
        lucideGlobalAvailable: typeof window.lucide !== 'undefined',
        createIconsAvailable: typeof (window.lucide && window.lucide.createIcons) === 'function'
      };
    });

    results.vendor = vendorMetrics;
    console.log('Vendor Dashboard Icon Metrics:', JSON.stringify(vendorMetrics, null, 2));

    const vendorDashShotPath = path.join(ARTIFACTS_DIR, 'audit_vendor_dashboard.png');
    await vendorPage.screenshot({ path: vendorDashShotPath, fullPage: false });
    console.log('Saved:', vendorDashShotPath);

    await vendorContext.close();

    // -------------------------------------------------------------------------
    // 3. AUDIT RUNNER PORTAL
    // -------------------------------------------------------------------------
    console.log('\n================ AUDITING RUNNER PORTAL ================');
    const runnerContext = await browser.newContext({
      viewport: { width: 390, height: 844 },
      deviceScaleFactor: 2
    });
    const runnerPage = await runnerContext.newPage();
    runnerPage.on('console', msg => {
      if (msg.type() === 'error') results.errors.push(`Runner Console Error: ${msg.text()}`);
    });
    runnerPage.on('pageerror', err => results.errors.push(`Runner Page Error: ${err.message}`));

    await runnerPage.goto('http://127.0.0.1:8093/runner/index.html', { waitUntil: 'networkidle' });
    await runnerPage.waitForTimeout(500);

    // Capture Runner Language Onboarding
    const runnerLangShotPath = path.join(ARTIFACTS_DIR, 'audit_runner_onboarding.png');
    await runnerPage.screenshot({ path: runnerLangShotPath, fullPage: false });
    console.log('Saved:', runnerLangShotPath);

    // Open Runner Dashboard
    console.log('-> Opening Runner Dashboard...');
    await runnerPage.evaluate(() => {
      if (typeof openDashboard === 'function') {
        openDashboard('missions');
      }
    });
    await runnerPage.waitForTimeout(1000);

    const runnerMetrics = await runnerPage.evaluate(() => {
      const allLucideTags = document.querySelectorAll('i[data-lucide]');
      const unrendered = Array.from(allLucideTags).filter(el => !el.querySelector('svg') && el.tagName.toLowerCase() !== 'svg');
      
      const allSvgs = document.querySelectorAll('svg');
      const visibleSvgs = Array.from(allSvgs).filter(s => {
        const r = s.getBoundingClientRect();
        return r.width > 0 && r.height > 0;
      });

      return {
        totalLucideNodes: allLucideTags.length,
        unrenderedCount: unrendered.length,
        unrenderedNames: unrendered.slice(0, 10).map(el => el.getAttribute('data-lucide')),
        totalSvgs: allSvgs.length,
        visibleSvgsCount: visibleSvgs.length,
        lucideGlobalAvailable: typeof window.lucide !== 'undefined',
        createIconsAvailable: typeof (window.lucide && window.lucide.createIcons) === 'function'
      };
    });

    results.runner = runnerMetrics;
    console.log('Runner Dashboard Icon Metrics:', JSON.stringify(runnerMetrics, null, 2));

    const runnerDashShotPath = path.join(ARTIFACTS_DIR, 'audit_runner_dashboard.png');
    await runnerPage.screenshot({ path: runnerDashShotPath, fullPage: false });
    console.log('Saved:', runnerDashShotPath);

    await runnerContext.close();

    console.log('\n================ AUDIT SUMMARY ================');
    console.log('All tests completed successfully!');
    console.log('Errors logged:', results.errors);

  } finally {
    await browser.close();
    server.close();
  }
}

server.listen(8093, () => {
  runAudit().catch(err => {
    console.error('Audit failed with error:', err);
    server.close();
    process.exit(1);
  });
});
