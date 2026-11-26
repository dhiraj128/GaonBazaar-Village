const https = require('https');
const { chromium } = require('../apps/admin/node_modules/playwright');
const path = require('path');
const fs = require('fs');

const ARTIFACTS_DIR = 'C:/Users/dhira/.gemini/antigravity/brain/918c8085-b60b-40a9-a077-a3344458bcc5';

const PORTALS = [
  { name: 'Customer App', url: 'https://www.apnagaonbazaar.in', prefix: 'customer' },
  { name: 'Vendor App', url: 'https://dukaan.apnagaonbazaar.in', prefix: 'vendor' },
  { name: 'Runner App', url: 'https://mitra.apnagaonbazaar.in', prefix: 'runner' },
  { name: 'Super Admin', url: 'https://admin.apnagaonbazaar.in', prefix: 'admin' }
];

function checkHeaderAndStatus(url) {
  return new Promise((resolve) => {
    const req = https.get(url, { headers: { 'User-Agent': 'Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36' }, timeout: 15000 }, (res) => {
      resolve({
        url,
        statusCode: res.statusCode,
        headers: res.headers,
        hsts: res.headers['strict-transport-security'] || 'MISSING',
        csp: res.headers['content-security-policy'] || 'MISSING',
        xFrame: res.headers['x-frame-options'] || 'MISSING',
        xContentType: res.headers['x-content-type-options'] || 'MISSING',
        referrerPolicy: res.headers['referrer-policy'] || 'MISSING',
        permissionsPolicy: res.headers['permissions-policy'] || 'MISSING'
      });
    });
    req.on('error', (err) => {
      resolve({ url, error: err.message });
    });
  });
}

async function runProductionAudit() {
  console.log('--- 1. HTTP/SSL & Security Header Inspection ---');
  const headerResults = [];
  for (const portal of PORTALS) {
    const res = await checkHeaderAndStatus(portal.url);
    headerResults.push({ name: portal.name, ...res });
    console.log(`[${portal.name}] Status: ${res.statusCode} | CSP: ${res.csp ? 'Present' : 'MISSING'} | HSTS: ${res.hsts ? 'Present' : 'MISSING'}`);
  }

  console.log('\n--- 2. End-to-End Mobile Browser Audit ---');
  const browser = await chromium.launch({ headless: true });
  const auditReport = [];

  for (const portal of PORTALS) {
    console.log(`\nAuditing ${portal.name} (${portal.url})...`);
    const context = await browser.newContext({
      viewport: { width: 412, height: 915 }, // Pixel 7 Android viewport
      deviceScaleFactor: 2.625,
      isMobile: true,
      hasTouch: true,
      userAgent: 'Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
    });

    const page = await context.newPage();
    const consoleLogs = [];
    const pageErrors = [];

    page.on('console', msg => {
      if (msg.type() === 'error') consoleLogs.push(msg.text());
    });
    page.on('pageerror', err => pageErrors.push(err.message));

    try {
      const resp = await page.goto(portal.url, { waitUntil: 'networkidle', timeout: 30000 });
      await page.waitForTimeout(1500);

      const title = await page.title();
      const finalUrl = page.url();
      const status = resp ? resp.status() : 'Unknown';

      // Capture Mobile Screenshot
      const screenshotName = `prod_${portal.prefix}_mobile.png`;
      const screenshotPath = path.join(ARTIFACTS_DIR, screenshotName);
      await page.screenshot({ path: screenshotPath, fullPage: false });
      console.log(`  Screenshot saved: ${screenshotName}`);

      // Evaluate interactive nodes & icons
      const evalData = await page.evaluate(() => {
        const svgs = document.querySelectorAll('svg');
        const visibleSvgs = Array.from(svgs).filter(s => {
          const r = s.getBoundingClientRect();
          return r.width > 0 && r.height > 0;
        });

        const unrenderedLucide = document.querySelectorAll('i[data-lucide]');
        const unrenderedList = Array.from(unrenderedLucide)
          .filter(el => !el.querySelector('svg') && el.tagName.toLowerCase() !== 'svg')
          .map(el => el.getAttribute('data-lucide'));

        const buttons = document.querySelectorAll('button:not([disabled])');
        const inputs = document.querySelectorAll('input:not([disabled])');
        const links = document.querySelectorAll('a[href]');

        return {
          totalSvgs: svgs.length,
          visibleSvgs: visibleSvgs.length,
          unrenderedLucideCount: unrenderedList.length,
          unrenderedLucideNames: unrenderedList.slice(0, 10),
          buttonCount: buttons.length,
          inputCount: inputs.length,
          linkCount: links.length,
          hasBottomNav: !!document.getElementById('customer-bottom-nav') || !!document.getElementById('bottom-tabs') || !!document.querySelector('nav')
        };
      });

      auditReport.push({
        name: portal.name,
        url: portal.url,
        finalUrl,
        httpStatus: status,
        title,
        evalData,
        consoleErrors: consoleLogs,
        pageErrors: pageErrors,
        screenshot: screenshotName
      });

      console.log(`  Title: "${title}" | SVGs: ${evalData.totalSvgs} (Visible: ${evalData.visibleSvgs}) | Unrendered Lucide: ${evalData.unrenderedLucideCount}`);
    } catch (err) {
      console.error(`  Error auditing ${portal.name}:`, err.message);
      auditReport.push({
        name: portal.name,
        url: portal.url,
        error: err.message
      });
    } finally {
      await context.close();
    }
  }

  await browser.close();

  const finalSummary = {
    timestamp: new Date().toISOString(),
    headers: headerResults,
    auditReport
  };

  const reportPath = path.join(ARTIFACTS_DIR, 'production_portals_audit.json');
  fs.writeFileSync(reportPath, JSON.stringify(finalSummary, null, 2), 'utf8');
  console.log(`\nComplete audit written to: ${reportPath}`);
}

runProductionAudit().catch(err => {
  console.error('Audit failed:', err);
});
