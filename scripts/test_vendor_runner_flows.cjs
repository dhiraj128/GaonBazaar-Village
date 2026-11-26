const { chromium } = require('../apps/admin/node_modules/playwright');
const path = require('path');
const fs = require('fs');

const ARTIFACTS_DIR = 'C:/Users/dhira/.gemini/antigravity/brain/918c8085-b60b-40a9-a077-a3344458bcc5';

(async () => {
  const browser = await chromium.launch();
  const results = { vendor: {}, runner: {}, admin: {} };

  // =========================================================================
  // 1. VENDOR PORTAL TESTS (https://dukaan.apnagaonbazaar.in)
  // =========================================================================
  console.log('\n--- 1. Testing Vendor Portal (https://dukaan.apnagaonbazaar.in) ---');
  const vendorContext = await browser.newContext({
    viewport: { width: 412, height: 915 },
    isMobile: true,
    hasTouch: true
  });
  const vendorPage = await vendorContext.newPage();
  
  await vendorPage.goto('https://dukaan.apnagaonbazaar.in', { waitUntil: 'networkidle' });
  await vendorPage.waitForTimeout(2000);

  // Capture Vendor Onboarding/Language Screen
  await vendorPage.screenshot({ path: path.join(ARTIFACTS_DIR, 'prod_vendor_live_lang.png') });
  console.log('Vendor live language screen captured!');

  // Access the embedded vendor app frame
  const vendorFrame = vendorPage.frames().find(f => f.url().includes('vendor/index.html')) || vendorPage;
  console.log('Vendor Frame URL:', vendorFrame.url());

  // Click continue to get to Login/Auth screen
  console.log('Clicking Continue inside Vendor Frame...');
  await vendorFrame.evaluate(() => {
    if (typeof navigateTo === 'function') navigateTo('onboarding-2');
  });
  await vendorPage.waitForTimeout(1000);

  // Capture Vendor Login Screen
  await vendorPage.screenshot({ path: path.join(ARTIFACTS_DIR, 'prod_vendor_live_login.png') });
  console.log('Vendor live login screen captured!');

  // Evaluate vendor login controls
  results.vendor.loginControls = await vendorFrame.evaluate(() => {
    const phoneInput = document.getElementById('phone-number') || document.querySelector('input[type="tel"]');
    const sendOtpBtn = document.getElementById('btn-send-otp') || document.querySelector('button[onclick*="sendOtp"], button[onclick*="OTP"]');
    const authHeading = document.getElementById('auth-heading');
    return {
      hasPhoneInput: !!phoneInput,
      hasSendOtpButton: !!sendOtpBtn,
      authHeading: authHeading ? authHeading.innerText.trim() : null
    };
  });
  console.log('Vendor Login Controls:', results.vendor.loginControls);

  // Open Vendor Dashboard directly
  console.log('Opening Vendor Dashboard inside frame...');
  await vendorFrame.evaluate(() => {
    if (typeof openDashboard === 'function') openDashboard('inventory');
  });
  await vendorPage.waitForTimeout(1000);
  await vendorPage.screenshot({ path: path.join(ARTIFACTS_DIR, 'prod_vendor_live_dashboard.png') });
  console.log('Vendor live dashboard captured!');

  await vendorContext.close();

  // =========================================================================
  // 2. RUNNER PORTAL TESTS (https://mitra.apnagaonbazaar.in)
  // =========================================================================
  console.log('\n--- 2. Testing Runner Portal (https://mitra.apnagaonbazaar.in) ---');
  const runnerContext = await browser.newContext({
    viewport: { width: 412, height: 915 },
    isMobile: true,
    hasTouch: true
  });
  const runnerPage = await runnerContext.newPage();
  
  await runnerPage.goto('https://mitra.apnagaonbazaar.in', { waitUntil: 'networkidle' });
  await runnerPage.waitForTimeout(2000);

  // Capture Runner Language Screen
  await runnerPage.screenshot({ path: path.join(ARTIFACTS_DIR, 'prod_runner_live_lang.png') });
  console.log('Runner live language screen captured!');

  // Access the embedded runner app frame
  const runnerFrame = runnerPage.frames().find(f => f.url().includes('runner/index.html')) || runnerPage;
  console.log('Runner Frame URL:', runnerFrame.url());

  // Click continue to get to Login/Auth screen
  console.log('Clicking Continue inside Runner Frame...');
  await runnerFrame.evaluate(() => {
    if (typeof navigateTo === 'function') navigateTo('onboarding-2');
  });
  await runnerPage.waitForTimeout(1000);

  // Capture Runner Login Screen
  await runnerPage.screenshot({ path: path.join(ARTIFACTS_DIR, 'prod_runner_live_login.png') });
  console.log('Runner live login screen captured!');

  // Evaluate runner login controls
  results.runner.loginControls = await runnerFrame.evaluate(() => {
    const phoneInput = document.getElementById('phone-number') || document.querySelector('input[type="tel"]');
    const sendOtpBtn = document.getElementById('btn-send-otp') || document.querySelector('button[onclick*="sendOtp"], button[onclick*="OTP"]');
    const authHeading = document.getElementById('auth-heading');
    return {
      hasPhoneInput: !!phoneInput,
      hasSendOtpButton: !!sendOtpBtn,
      authHeading: authHeading ? authHeading.innerText.trim() : null
    };
  });
  console.log('Runner Login Controls:', results.runner.loginControls);

  // Open Runner Dashboard directly
  console.log('Opening Runner Dashboard inside frame...');
  await runnerFrame.evaluate(() => {
    if (typeof openDashboard === 'function') openDashboard('missions');
  });
  await runnerPage.waitForTimeout(1000);
  await runnerPage.screenshot({ path: path.join(ARTIFACTS_DIR, 'prod_runner_live_dashboard.png') });
  console.log('Runner live dashboard captured!');

  await runnerContext.close();

  // =========================================================================
  // 3. SUPER ADMIN TESTS (https://admin.apnagaonbazaar.in)
  // =========================================================================
  console.log('\n--- 3. Testing Super Admin (https://admin.apnagaonbazaar.in) ---');
  const adminContext = await browser.newContext({
    viewport: { width: 1280, height: 800 }
  });
  const adminPage = await adminContext.newPage();
  
  await adminPage.goto('https://admin.apnagaonbazaar.in', { waitUntil: 'domcontentloaded' });
  await adminPage.waitForTimeout(3000);

  // Capture Admin Login / Dashboard Screen
  await adminPage.screenshot({ path: path.join(ARTIFACTS_DIR, 'prod_admin_live_screen.png') });
  console.log('Super Admin live screen captured!');

  results.admin.details = await adminPage.evaluate(() => {
    const title = document.title;
    const headings = Array.from(document.querySelectorAll('h1, h2, h3')).map(h => h.innerText.trim());
    const inputs = document.querySelectorAll('input');
    const buttons = Array.from(document.querySelectorAll('button')).map(b => b.innerText.trim().slice(0, 30));
    return {
      title,
      headings: headings.slice(0, 10),
      inputCount: inputs.length,
      buttons: buttons.slice(0, 10)
    };
  });
  console.log('Super Admin Details:', results.admin.details);

  await adminContext.close();
  await browser.close();

  console.log('\nAll live portal flow tests completed successfully!');
})().catch(console.error);
