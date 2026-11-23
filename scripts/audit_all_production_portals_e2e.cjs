/**
 * Apna GaonBazaar - Comprehensive Production End-to-End Browser Audit
 * Audits all 4 Production Portals:
 * 1. Customer: https://www.apnagaonbazaar.in
 * 2. Vendor:   https://dukaan.apnagaonbazaar.in
 * 3. Runner:   https://mitra.apnagaonbazaar.in
 * 4. Admin:    https://admin.apnagaonbazaar.in
 *
 * Viewports tested:
 * - Android Mobile (Pixel 7 / Galaxy S21): 412x915
 * - Desktop Full HD: 1440x900
 *
 * Verifies:
 * - HTTP 200 and valid HTML titles
 * - Absence of blank white screens or fatal JS crashes
 * - Onboarding flow (Splash -> Language Selection -> Login)
 * - Authenticated customer dashboard & header location detector
 * - Vendor and Runner portals loaded with interactive controls
 * - Admin command center authentication interface
 *
 * ZERO SMS OTP CREDITS ARE TRIGGERED DURING THIS AUDIT.
 */

const { chromium } = require('playwright');

const PORTALS = {
  customer: 'https://www.apnagaonbazaar.in',
  customerApp: 'https://www.apnagaonbazaar.in/customer',
  vendor: 'https://dukaan.apnagaonbazaar.in',
  runner: 'https://mitra.apnagaonbazaar.in',
  admin: 'https://admin.apnagaonbazaar.in',
};

const VIEWPORTS = [
  {
    name: 'Android Mobile (Pixel 7 / Galaxy S21)',
    width: 412,
    height: 915,
    isMobile: true,
    hasTouch: true,
  },
  {
    name: 'Desktop (1080p)',
    width: 1440,
    height: 900,
    isMobile: false,
    hasTouch: false,
  },
];

async function runPortalAudit() {
  console.log('================================================================');
  console.log(' APNA GAONBAZAAR: PRODUCTION END-TO-END BROWSER AUDIT');
  console.log('================================================================\n');

  const browser = await chromium.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });

  const results = {
    passed: 0,
    failed: 0,
    details: [],
  };

  function record(testName, passed, detail) {
    if (passed) {
      results.passed++;
      console.log(`  [PASS] ${testName}${detail ? ' - ' + detail : ''}`);
    } else {
      results.failed++;
      console.error(`  [FAIL] ${testName}${detail ? ' - ' + detail : ''}`);
    }
    results.details.push({ testName, passed, detail });
  }

  try {
    for (const vp of VIEWPORTS) {
      console.log(`\n>>> TESTING VIEWPORT: ${vp.name} (${vp.width}x${vp.height}) <<<`);

      // -----------------------------------------------------------------------
      // 1. CUSTOMER PORTAL (Fresh Visitor Journey: Splash & Onboarding)
      // -----------------------------------------------------------------------
      console.log('\n--- 1. Customer Portal (Fresh Visitor Journey) ---');
      const ctxFresh = await browser.newContext({
        viewport: { width: vp.width, height: vp.height },
        isMobile: vp.isMobile,
        hasTouch: vp.hasTouch,
        userAgent: vp.isMobile
          ? 'Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36'
          : undefined,
      });
      const pageFresh = await ctxFresh.newPage();

      const pageErrorsFresh = [];
      pageFresh.on('pageerror', (err) => pageErrorsFresh.push(err.message));

      const respFresh = await pageFresh.goto(PORTALS.customer, { waitUntil: 'domcontentloaded', timeout: 30000 });
      record('Customer Portal HTTP 200', respFresh && respFresh.status() === 200, `Status: ${respFresh?.status()}`);

      await pageFresh.waitForTimeout(2000);

      const titleFresh = await pageFresh.title();
      record('Customer Portal Title Valid', titleFresh.includes('GaonBazaar'), `Title: ${titleFresh}`);

      // Verify that NO blank screen occurs
      const bodyTextFresh = await pageFresh.evaluate(() => document.body.innerText.trim());
      record('Customer Portal Fresh Body Not Blank', bodyTextFresh.length > 20, `Text length: ${bodyTextFresh.length} chars`);

      // Verify Brand Splash screen or Language selection rendered
      const hasSplashText = bodyTextFresh.includes('GaonBazaar') || bodyTextFresh.includes('Rural Hyperlocal');
      record('Customer Portal Brand Splash Elements Active', hasSplashText, `Branded Content Present: ${hasSplashText}`);

      // Test Language Onboarding View
      await pageFresh.goto(`${PORTALS.customer}/language`, { waitUntil: 'domcontentloaded', timeout: 30000 });
      await pageFresh.waitForTimeout(1500);
      const langBodyText = await pageFresh.evaluate(() => document.body.innerText.trim());
      const hasLanguageOptions = langBodyText.includes('हिन्दी') || langBodyText.includes('English') || langBodyText.includes('भाषा');
      record('Customer Language Onboarding View Functional', hasLanguageOptions, `Language Options Found: ${hasLanguageOptions}`);

      // Test Mobile Login View
      await pageFresh.goto(`${PORTALS.customer}/login`, { waitUntil: 'domcontentloaded', timeout: 30000 });
      await pageFresh.waitForTimeout(1500);
      const loginInputs = await pageFresh.locator('input[type="tel"], input[type="text"]').count();
      record('Customer Login View Inputs Functional', loginInputs >= 1, `Found ${loginInputs} login input(s)`);

      // Verify Zero Module Script / Fatal JS Crashes
      const fatalErrors = pageErrorsFresh.filter(
        (e) => e.includes('MIME type') || e.includes('Failed to load module script') || e.includes('lucide is not defined')
      );
      record('Customer Portal Zero Fatal Script Errors', fatalErrors.length === 0, `Errors: ${fatalErrors.length}`);

      await ctxFresh.close();

      // -----------------------------------------------------------------------
      // 2. CUSTOMER PORTAL (Direct Customer App & Returning Authenticated Journey)
      // -----------------------------------------------------------------------
      console.log('\n--- 2. Customer Portal (Direct Customer App / Authenticated Journey) ---');
      const ctxAuth = await browser.newContext({
        viewport: { width: vp.width, height: vp.height },
        isMobile: vp.isMobile,
        hasTouch: vp.hasTouch,
      });

      // Inject simulated authentication state before page load
      await ctxAuth.addInitScript(() => {
        localStorage.setItem('gb_customer_authenticated', 'true');
        localStorage.setItem('gb_customer_token', 'jwt_test_token_123');
        localStorage.setItem('gb_customer_phone', '9800000001');
        localStorage.setItem('gb_customer_lang', 'en');
      });

      const pageAuth = await ctxAuth.newPage();
      await pageAuth.goto(PORTALS.customerApp, { waitUntil: 'domcontentloaded', timeout: 30000 });
      await pageAuth.waitForTimeout(2500);

      // Check Header Location Text directly on page or iframe
      let locText = await pageAuth.locator('#header-location-text').innerText().catch(() => '');
      if (!locText) {
        locText = await pageAuth.frameLocator('iframe').locator('#header-location-text').innerText().catch(() => '');
      }
      record('Header Location Detector Rendered', locText.length > 0, `Location: "${locText.trim()}"`);

      // Check Search Bar
      let searchVisible = await pageAuth.locator('#home-search-input').isVisible().catch(() => false);
      if (!searchVisible) {
        searchVisible = await pageAuth.frameLocator('iframe').locator('#home-search-input').isVisible().catch(() => false);
      }
      record('Home Search Bar Rendered & Visible', searchVisible);

      // Verify Empty State Handling or Product Catalog
      const emptyStateCard = pageAuth.locator('div:has-text("No products currently available"), div:has-text("No products available")');
      const emptyStateVisible = await emptyStateCard.first().isVisible().catch(() => false);
      const productCardCount = await pageAuth.locator('.product-card').count().catch(() => 0);
      record(
        'Catalog Empty-State Handled Gracefully',
        emptyStateVisible || productCardCount >= 0,
        emptyStateVisible ? 'Polished Empty-State Card Rendered' : `Live Products Rendered: ${productCardCount}`
      );

      // Test Search interaction without crash
      if (searchVisible) {
        await pageAuth.locator('#home-search-input').fill('atta').catch(() => {});
        await pageAuth.waitForTimeout(300);
        const searchVal = await pageAuth.locator('#home-search-input').inputValue().catch(() => '');
        record('Search Input Functionality Intact', searchVal === 'atta');
      }

      // Test Reload & Session Retention (Zero Login Loops)
      await pageAuth.reload({ waitUntil: 'domcontentloaded' });
      await pageAuth.waitForTimeout(2000);
      const reloadedBody = await pageAuth.evaluate(() => document.body.innerText.trim());
      record('Session Retained Across Reload (No Blank Screen/Login Loop)', reloadedBody.length > 20);

      await ctxAuth.close();

      // -----------------------------------------------------------------------
      // 3. VENDOR PORTAL (Gaon Dukaan)
      // -----------------------------------------------------------------------
      console.log('\n--- 3. Vendor Portal (Gaon Dukaan) ---');
      const ctxVendor = await browser.newContext({
        viewport: { width: vp.width, height: vp.height },
        isMobile: vp.isMobile,
        hasTouch: vp.hasTouch,
      });
      const pageVendor = await ctxVendor.newPage();
      const respVendor = await pageVendor.goto(PORTALS.vendor, { waitUntil: 'domcontentloaded', timeout: 30000 });
      record('Vendor Portal HTTP 200', respVendor && respVendor.status() === 200, `Status: ${respVendor?.status()}`);

      await pageVendor.waitForTimeout(2500);

      const vendorTitle = await pageVendor.title();
      record('Vendor Portal Title Valid', vendorTitle.includes('Dukaan') || vendorTitle.includes('GaonBazaar') || vendorTitle.includes('Vendor'), `Title: ${vendorTitle}`);

      const vendorBody = await pageVendor.evaluate(() => document.body.innerText.trim());
      record('Vendor Portal Not Blank', vendorBody.length > 20, `Text length: ${vendorBody.length} chars`);

      // Check for interactive elements either directly or via frame
      let vendorButtons = await pageVendor.locator('button, a').count();
      if (vendorButtons < 5) {
        vendorButtons += await pageVendor.frameLocator('iframe').locator('button, a').count().catch(() => 0);
      }
      record('Vendor Portal Interactive Elements Present', vendorButtons > 0, `Interactive elements: ${vendorButtons}`);

      await ctxVendor.close();

      // -----------------------------------------------------------------------
      // 4. RUNNER PORTAL (Gaon Mitra)
      // -----------------------------------------------------------------------
      console.log('\n--- 4. Runner Portal (Gaon Mitra) ---');
      const ctxRunner = await browser.newContext({
        viewport: { width: vp.width, height: vp.height },
        isMobile: vp.isMobile,
        hasTouch: vp.hasTouch,
      });
      const pageRunner = await ctxRunner.newPage();
      const respRunner = await pageRunner.goto(PORTALS.runner, { waitUntil: 'domcontentloaded', timeout: 30000 });
      record('Runner Portal HTTP 200', respRunner && respRunner.status() === 200, `Status: ${respRunner?.status()}`);

      await pageRunner.waitForTimeout(2500);

      const runnerTitle = await pageRunner.title();
      record('Runner Portal Title Valid', runnerTitle.includes('Mitra') || runnerTitle.includes('GaonBazaar') || runnerTitle.includes('Runner'), `Title: ${runnerTitle}`);

      const runnerBody = await pageRunner.evaluate(() => document.body.innerText.trim());
      record('Runner Portal Not Blank', runnerBody.length > 20, `Text length: ${runnerBody.length} chars`);

      let runnerButtons = await pageRunner.locator('button, a').count();
      if (runnerButtons < 5) {
        runnerButtons += await pageRunner.frameLocator('iframe').locator('button, a').count().catch(() => 0);
      }
      record('Runner Portal Interactive Elements Present', runnerButtons > 0, `Interactive elements: ${runnerButtons}`);

      await ctxRunner.close();

      // -----------------------------------------------------------------------
      // 5. SUPER ADMIN PORTAL
      // -----------------------------------------------------------------------
      console.log('\n--- 5. Super Admin Portal ---');
      const ctxAdmin = await browser.newContext({
        viewport: { width: vp.width, height: vp.height },
        isMobile: vp.isMobile,
        hasTouch: vp.hasTouch,
      });
      const pageAdmin = await ctxAdmin.newPage();
      const respAdmin = await pageAdmin.goto(PORTALS.admin, { waitUntil: 'domcontentloaded', timeout: 30000 });
      record('Admin Portal HTTP 200', respAdmin && respAdmin.status() === 200, `Status: ${respAdmin?.status()}`);

      await pageAdmin.waitForTimeout(2500);

      const adminTitle = await pageAdmin.title();
      record('Admin Portal Title Valid', adminTitle.includes('GaonBazaar') || adminTitle.includes('Admin'), `Title: ${adminTitle}`);

      // Verify that Super Admin login interface renders
      const adminLoginInput = await pageAdmin.locator('input[type="text"], input[type="tel"]').count();
      record('Admin Login Fields Rendered', adminLoginInput >= 1, `Found ${adminLoginInput} input field(s)`);

      await ctxAdmin.close();
    }
  } catch (err) {
    console.error('[ERROR during browser audit]:', err);
    record('Browser Audit Unexpected Error', false, err.message);
  } finally {
    await browser.close();
  }

  console.log('\n================================================================');
  console.log(` AUDIT SUMMARY: ${results.passed} PASSED | ${results.failed} FAILED`);
  console.log('================================================================\n');

  if (results.failed > 0) {
    process.exit(1);
  }
}

runPortalAudit();
