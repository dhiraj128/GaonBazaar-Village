const { chromium } = require('../apps/admin/node_modules/playwright');
const path = require('path');
const fs = require('fs');

const ARTIFACTS_DIR = 'C:/Users/dhira/.gemini/antigravity/brain/918c8085-b60b-40a9-a077-a3344458bcc5';

async function verifyLiveProduction() {
  console.log('=== STARTING LIVE PRODUCTION ICON & PORTAL AUDIT ===\n');
  const browser = await chromium.launch({ headless: true });
  const results = {
    customer: {},
    vendor: {},
    runner: {},
    admin: {},
    summary: { passed: 0, failed: 0 }
  };

  try {
    // -------------------------------------------------------------------------
    // 1. AUDIT CUSTOMER LIVE PORTAL
    // -------------------------------------------------------------------------
    console.log('--- AUDITING LIVE CUSTOMER APP (https://www.apnagaonbazaar.in) ---');
    const customerContext = await browser.newContext({
      viewport: { width: 412, height: 915 },
      deviceScaleFactor: 2.625,
      isMobile: true,
      hasTouch: true
    });
    const customerPage = await customerContext.newPage();

    // Authenticated state injection to reach dashboard
    await customerPage.addInitScript(() => {
      localStorage.setItem('gb_customer_authenticated', 'true');
      localStorage.setItem('gb_customer_phone', '9905361711');
      localStorage.setItem('gb_user_lang', 'en');
    });

    await customerPage.goto('https://www.apnagaonbazaar.in/customer/index.html', { waitUntil: 'networkidle' });
    await customerPage.waitForTimeout(2000);

    // Capture Customer Home
    const customerHomeShot = path.join(ARTIFACTS_DIR, 'live_prod_customer_home.png');
    await customerPage.screenshot({ path: customerHomeShot, fullPage: false });
    console.log('Saved:', customerHomeShot);

    const customerHomeMetrics = await customerPage.evaluate(() => {
      const searchMic = document.getElementById('home-search-mic-btn');
      const searchMicSvg = searchMic ? searchMic.querySelector('svg') : null;
      const searchMicBox = searchMicSvg ? searchMicSvg.getBoundingClientRect() : null;

      const searchInputIcon = document.querySelector('#view-home i[data-lucide="search"] svg, #view-home svg.lucide-search');
      const searchInputIconBox = searchInputIcon ? searchInputIcon.getBoundingClientRect() : null;

      const bottomNav = document.getElementById('customer-bottom-nav');
      const navButtons = bottomNav ? Array.from(bottomNav.querySelectorAll('button')).map(btn => {
        const svg = btn.querySelector('svg');
        const box = svg ? svg.getBoundingClientRect() : null;
        return {
          id: btn.id,
          text: btn.innerText.trim().replace(/\s+/g, ' '),
          hasSvg: !!svg,
          box: box ? { width: box.width, height: box.height } : null
        };
      }) : [];

      return {
        searchMicVisible: searchMicBox && searchMicBox.width > 0 && searchMicBox.height > 0,
        searchMicDimensions: searchMicBox ? { width: searchMicBox.width, height: searchMicBox.height } : null,
        searchInputIconVisible: searchInputIconBox && searchInputIconBox.width > 0 && searchInputIconBox.height > 0,
        navButtons
      };
    });
    results.customer.home = customerHomeMetrics;
    console.log('Customer Home Metrics:', JSON.stringify(customerHomeMetrics, null, 2));

    // Switch to AI Assistant Tab
    console.log('-> Navigating to Customer AI Assistant tab...');
    await customerPage.evaluate(() => {
      if (typeof switchTab === 'function') switchTab('ai');
    });
    await customerPage.waitForTimeout(1000);

    const customerAiShot = path.join(ARTIFACTS_DIR, 'live_prod_customer_ai.png');
    await customerPage.screenshot({ path: customerAiShot, fullPage: false });
    console.log('Saved:', customerAiShot);

    const customerAiMetrics = await customerPage.evaluate(() => {
      const micBtn = document.getElementById('main-mic-btn');
      const micSvg = micBtn ? micBtn.querySelector('svg') : null;
      const micBox = micSvg ? micSvg.getBoundingClientRect() : null;

      const sendBtn = document.querySelector('#view-ai button[title="Send Query"]');
      const sendSvg = sendBtn ? sendBtn.querySelector('svg') : null;
      const sendBox = sendSvg ? sendSvg.getBoundingClientRect() : null;

      const headerBot = document.querySelector('#view-ai header .w-9.h-9.rounded-full');
      const headerBotSvg = headerBot ? headerBot.querySelector('svg') : null;
      const headerBotBox = headerBotSvg ? headerBotSvg.getBoundingClientRect() : null;

      return {
        mainMicVisible: micBox && micBox.width > 0 && micBox.height > 0,
        mainMicDimensions: micBox ? { width: micBox.width, height: micBox.height } : null,
        sendArrowVisible: sendBox && sendBox.width > 0 && sendBox.height > 0,
        sendArrowDimensions: sendBox ? { width: sendBox.width, height: sendBox.height } : null,
        headerBotVisible: headerBotBox && headerBotBox.width > 0 && headerBotBox.height > 0,
        headerBotDimensions: headerBotBox ? { width: headerBotBox.width, height: headerBotBox.height } : null
      };
    });
    results.customer.ai = customerAiMetrics;
    console.log('Customer AI Assistant Metrics:', JSON.stringify(customerAiMetrics, null, 2));
    await customerContext.close();

    // -------------------------------------------------------------------------
    // 2. AUDIT VENDOR LIVE PORTAL
    // -------------------------------------------------------------------------
    console.log('\n--- AUDITING LIVE VENDOR APP (https://dukaan.apnagaonbazaar.in) ---');
    const vendorContext = await browser.newContext({
      viewport: { width: 412, height: 915 },
      deviceScaleFactor: 2.625,
      isMobile: true,
      hasTouch: true
    });
    const vendorPage = await vendorContext.newPage();

    await vendorPage.addInitScript(() => {
      localStorage.setItem('gb_vendor_authenticated', 'true');
      localStorage.setItem('gb_vendor_phone', '9800000001');
      localStorage.setItem('gb_user_lang', 'en');
    });

    await vendorPage.goto('https://dukaan.apnagaonbazaar.in/vendor/index.html', { waitUntil: 'networkidle' });
    await vendorPage.waitForTimeout(2000);

    const vendorShot = path.join(ARTIFACTS_DIR, 'live_prod_vendor_dashboard.png');
    await vendorPage.screenshot({ path: vendorShot, fullPage: false });
    console.log('Saved:', vendorShot);

    const vendorMetrics = await vendorPage.evaluate(() => {
      const searchMic = document.getElementById('search-mic-btn');
      const searchMicSvg = searchMic ? searchMic.querySelector('svg') : null;
      const searchMicBox = searchMicSvg ? searchMicSvg.getBoundingClientRect() : null;

      const barcodeBtn = document.getElementById('btn-scan-barcode');
      const barcodeSvg = barcodeBtn ? barcodeBtn.querySelector('svg') : null;
      const barcodeBox = barcodeSvg ? barcodeSvg.getBoundingClientRect() : null;

      const photoBtn = document.getElementById('btn-quick-photo');
      const photoSvg = photoBtn ? photoBtn.querySelector('svg') : null;
      const photoBox = photoSvg ? photoSvg.getBoundingClientRect() : null;

      const bottomNav = document.querySelector('nav.fixed.bottom-0');
      const navButtons = bottomNav ? Array.from(bottomNav.querySelectorAll('button')).map(btn => {
        const svg = btn.querySelector('svg');
        const box = svg ? svg.getBoundingClientRect() : null;
        return {
          id: btn.id,
          text: btn.innerText.trim().replace(/\s+/g, ' '),
          hasSvg: !!svg,
          box: box ? { width: box.width, height: box.height } : null
        };
      }) : [];

      return {
        searchMicVisible: searchMicBox && searchMicBox.width > 0 && searchMicBox.height > 0,
        barcodeVisible: barcodeBox && barcodeBox.width > 0 && barcodeBox.height > 0,
        photoVisible: photoBox && photoBox.width > 0 && photoBox.height > 0,
        navButtons
      };
    });
    results.vendor = vendorMetrics;
    console.log('Vendor Metrics:', JSON.stringify(vendorMetrics, null, 2));
    await vendorContext.close();

    // -------------------------------------------------------------------------
    // 3. AUDIT RUNNER LIVE PORTAL
    // -------------------------------------------------------------------------
    console.log('\n--- AUDITING LIVE RUNNER APP (https://mitra.apnagaonbazaar.in) ---');
    const runnerContext = await browser.newContext({
      viewport: { width: 412, height: 915 },
      deviceScaleFactor: 2.625,
      isMobile: true,
      hasTouch: true
    });
    const runnerPage = await runnerContext.newPage();

    await runnerPage.addInitScript(() => {
      localStorage.setItem('gb_runner_authenticated', 'true');
      localStorage.setItem('gb_runner_phone', '9800000003');
      localStorage.setItem('gb_user_lang', 'en');
    });

    await runnerPage.goto('https://mitra.apnagaonbazaar.in/runner/index.html', { waitUntil: 'networkidle' });
    await runnerPage.waitForTimeout(2000);

    const runnerShot = path.join(ARTIFACTS_DIR, 'live_prod_runner_dashboard.png');
    await runnerPage.screenshot({ path: runnerShot, fullPage: false });
    console.log('Saved:', runnerShot);

    const runnerMetrics = await runnerPage.evaluate(() => {
      const dutyCard = document.querySelector('.bg-emerald-600.text-white');
      const dutySvg = dutyCard ? dutyCard.querySelector('svg') : null;
      const dutyBox = dutySvg ? dutySvg.getBoundingClientRect() : null;

      const bottomNav = document.querySelector('nav.fixed.bottom-0');
      const navButtons = bottomNav ? Array.from(bottomNav.querySelectorAll('button')).map(btn => {
        const svg = btn.querySelector('svg');
        const box = svg ? svg.getBoundingClientRect() : null;
        return {
          id: btn.id,
          text: btn.innerText.trim().replace(/\s+/g, ' '),
          hasSvg: !!svg,
          box: box ? { width: box.width, height: box.height } : null
        };
      }) : [];

      return {
        dutyIconVisible: dutyBox && dutyBox.width > 0 && dutyBox.height > 0,
        navButtons
      };
    });
    results.runner = runnerMetrics;
    console.log('Runner Metrics:', JSON.stringify(runnerMetrics, null, 2));
    await runnerContext.close();

    // -------------------------------------------------------------------------
    // 4. AUDIT SUPER ADMIN LIVE PORTAL
    // -------------------------------------------------------------------------
    console.log('\n--- AUDITING LIVE ADMIN APP (https://admin.apnagaonbazaar.in) ---');
    const adminContext = await browser.newContext({
      viewport: { width: 1280, height: 800 }
    });
    const adminPage = await adminContext.newPage();
    await adminPage.goto('https://admin.apnagaonbazaar.in', { waitUntil: 'domcontentloaded' });
    await adminPage.waitForTimeout(3000);

    const adminShot = path.join(ARTIFACTS_DIR, 'live_prod_admin_login.png');
    await adminPage.screenshot({ path: adminShot, fullPage: false });
    console.log('Saved:', adminShot);

    const adminMetrics = await adminPage.evaluate(() => {
      const loginCard = document.querySelector('form') || document.querySelector('button');
      const title = document.title;
      return {
        title,
        hasControls: !!loginCard
      };
    });
    results.admin = adminMetrics;
    console.log('Admin Metrics:', JSON.stringify(adminMetrics, null, 2));
    await adminContext.close();

  } catch (err) {
    console.error('Audit exception:', err);
  } finally {
    await browser.close();
    fs.writeFileSync(path.join(ARTIFACTS_DIR, 'live_production_audit_results.json'), JSON.stringify(results, null, 2));
    console.log('\n=== AUDIT COMPLETE ===');
  }
}

verifyLiveProduction();
