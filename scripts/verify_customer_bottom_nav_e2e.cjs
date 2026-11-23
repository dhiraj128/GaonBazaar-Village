const http = require('http');
const fs = require('fs');
const path = require('path');
const { chromium } = require('../apps/admin/node_modules/playwright');

const PUBLIC_DIR = path.join(__dirname, '../apps/admin/public');

// MIME types
const MIME_TYPES = {
  '.html': 'text/html',
  '.css': 'text/css',
  '.js': 'application/javascript',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon'
};

function startServer(port = 8089) {
  return new Promise((resolve, reject) => {
    const server = http.createServer((req, res) => {
      let reqPath = req.url.split('?')[0];
      if (reqPath === '/' || reqPath === '/customer') {
        reqPath = '/customer/index.html';
      }
      const filePath = path.join(PUBLIC_DIR, reqPath);
      const ext = path.extname(filePath);
      const contentType = MIME_TYPES[ext] || 'application/octet-stream';

      fs.readFile(filePath, (err, content) => {
        if (err) {
          if (err.code === 'ENOENT') {
            res.writeHead(404, { 'Content-Type': 'text/plain' });
            res.end('Not Found');
          } else {
            res.writeHead(500);
            res.end(`Server Error: ${err.code}`);
          }
        } else {
          res.writeHead(200, { 'Content-Type': contentType });
          res.end(content);
        }
      });
    });

    server.listen(port, () => {
      console.log(`[Local Server] Running on http://127.0.0.1:${port}`);
      resolve(server);
    });
    server.on('error', reject);
  });
}

(async () => {
  const server = await startServer(8089);
  const browser = await chromium.launch({ headless: true });

  try {
    const viewports = [
      { name: 'android_412x915', width: 412, height: 915, isMobile: true },
      { name: 'small_320x650', width: 320, height: 650, isMobile: true },
    ];

    for (const vp of viewports) {
      console.log(`\n========================================`);
      console.log(`Testing Viewport: ${vp.name} (${vp.width}x${vp.height})`);
      console.log(`========================================`);

      const context = await browser.newContext({
        viewport: { width: vp.width, height: vp.height },
        isMobile: vp.isMobile,
        deviceScaleFactor: 2
      });

      const page = await context.newPage();
      page.on('console', msg => {
        if (msg.type() === 'error') console.log(`[Browser Error]:`, msg.text());
      });

      await page.goto('http://127.0.0.1:8089/customer/index.html', { waitUntil: 'load' });
      await page.waitForTimeout(500);

      // Force view into dashboard
      await page.evaluate(() => {
        if (typeof switchTab === 'function') switchTab('home');
      });
      await page.waitForTimeout(500);

      const nav = await page.$('nav#customer-bottom-nav');
      if (!nav) throw new Error('Bottom navigation bar nav#customer-bottom-nav not found!');

      // Check all 5 tabs exist
      const tabs = ['home', 'ai', 'cart', 'orders', 'account'];
      for (const t of tabs) {
        const btn = await page.$(`#nav-btn-${t}`);
        if (!btn) throw new Error(`Tab #nav-btn-${t} missing!`);

        const svg = await btn.$('svg');
        if (!svg) throw new Error(`Tab #nav-btn-${t} is missing its SVG icon!`);

        const svgBox = await svg.boundingBox();
        if (!svgBox || svgBox.width < 10 || svgBox.height < 10) {
          throw new Error(`Tab #nav-btn-${t} SVG is invisible or collapsed! Box: ${JSON.stringify(svgBox)}`);
        }

        const label = await btn.$('.nav-label');
        if (!label) throw new Error(`Tab #nav-btn-${t} is missing its label!`);
        const labelText = await label.innerText();
        console.log(`[PASS] Tab: ${t} | Icon: ${Math.round(svgBox.width)}x${Math.round(svgBox.height)} | Label: "${labelText}"`);
      }

      // Check Home Tab is active by default
      const homeBtn = await page.$('#nav-btn-home');
      const homeClass = await homeBtn.getAttribute('class');
      if (!homeClass.includes('is-active')) {
        throw new Error(`Home tab should be active by default, got: ${homeClass}`);
      }
      console.log(`[PASS] Home tab is-active initially`);

      // Test Tab Switching for all tabs
      for (const t of tabs) {
        console.log(`Switching to tab: ${t}...`);
        await page.click(`#nav-btn-${t}`);
        await page.waitForTimeout(200);

        const activeBtn = await page.$(`#nav-btn-${t}`);
        const cls = await activeBtn.getAttribute('class');
        if (!cls.includes('is-active')) {
          throw new Error(`Tab #nav-btn-${t} did not receive is-active after click!`);
        }

        // Verify other tabs are NOT is-active
        for (const other of tabs) {
          if (other !== t) {
            const otherBtn = await page.$(`#nav-btn-${other}`);
            const otherCls = await otherBtn.getAttribute('class');
            if (otherCls.includes('is-active')) {
              throw new Error(`Tab #nav-btn-${other} unexpectedly has is-active when ${t} is active!`);
            }
          }
        }

        // Verify view is visible
        const view = await page.$(`#view-${t}`);
        const isHidden = await view.evaluate(el => el.classList.contains('hidden'));
        if (isHidden) throw new Error(`View #view-${t} should be visible after switching to ${t}!`);
        console.log(`[PASS] Successfully switched to ${t} (view visible, active indicator on)`);
      }

      // Switch back to home
      await page.click('#nav-btn-home');
      await page.waitForTimeout(300);

      // Capture after screenshots
      const shotPath = path.join(__dirname, `../after_customer_mobile_${vp.name}.png`);
      await page.screenshot({ path: shotPath, fullPage: false });
      console.log(`[Screenshot] Saved ${shotPath}`);

      // Test Hindi translations
      await page.evaluate(() => {
        if (typeof setAppLanguage === 'function') setAppLanguage('hi');
      });
      await page.waitForTimeout(300);
      const hindiNavShot = path.join(__dirname, `../after_bottom_nav_hindi_${vp.name}.png`);
      await nav.screenshot({ path: hindiNavShot });
      console.log(`[Screenshot] Saved ${hindiNavShot}`);

      await context.close();
    }

    console.log(`\n[ALL CHECKS PASSED] Bottom navigation bar successfully verified!`);
  } finally {
    await browser.close();
    server.close();
  }
})();
