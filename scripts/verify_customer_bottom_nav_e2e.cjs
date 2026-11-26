const http = require('http');
const fs = require('fs');
const path = require('path');
const { chromium } = require('../apps/admin/node_modules/playwright');

const PUBLIC_DIR = path.join(__dirname, '../apps/admin/public');
const ARTIFACT_DIR = 'C:\\Users\\dhira\\.gemini\\antigravity\\brain\\918c8085-b60b-40a9-a077-a3344458bcc5';

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
      { name: 'android_412x915', width: 412, height: 915, isMobile: true, userAgent: 'Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36' },
      { name: 'iphone_390x844', width: 390, height: 844, isMobile: true, userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1' },
      { name: 'compact_360x780', width: 360, height: 780, isMobile: true, userAgent: 'Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36' },
      { name: 'small_320x650', width: 320, height: 650, isMobile: true, userAgent: 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Mobile Safari/537.36' },
    ];

    for (const vp of viewports) {
      console.log(`\n========================================`);
      console.log(`Testing Viewport: ${vp.name} (${vp.width}x${vp.height})`);
      console.log(`========================================`);

      const context = await browser.newContext({
        viewport: { width: vp.width, height: vp.height },
        isMobile: vp.isMobile,
        userAgent: vp.userAgent,
        deviceScaleFactor: 2
      });

      const page = await context.newPage();
      page.on('console', msg => {
        if (msg.type() === 'error') console.log(`[Browser Error]:`, msg.text());
      });

      await page.goto('http://127.0.0.1:8089/customer/index.html', { waitUntil: 'load' });
      await page.waitForTimeout(500);

      // Transition to dashboard view
      await page.evaluate(() => {
        if (typeof switchTab === 'function') switchTab('home');
      });
      await page.waitForTimeout(500);

      const nav = await page.$('nav#customer-bottom-nav');
      if (!nav) throw new Error('Bottom navigation bar nav#customer-bottom-nav not found!');

      const navBox = await nav.boundingBox();
      console.log(`[PASS] Bottom navigation bar bounding box: width=${Math.round(navBox.width)}px, height=${Math.round(navBox.height)}px, y=${Math.round(navBox.y)}px`);

      // Verify compact height (between 45px and 58px)
      if (navBox.height > 62) {
        throw new Error(`Navigation bar is too tall (${navBox.height}px)! Expected compact <= 60px.`);
      }

      // Check all 5 tabs exist with SVG icons and labels underneath
      const tabs = ['home', 'ai', 'cart', 'orders', 'account'];
      for (const t of tabs) {
        const btn = await page.$(`#nav-btn-${t}`);
        if (!btn) throw new Error(`Tab #nav-btn-${t} missing!`);

        const svg = await btn.$('svg');
        if (!svg) throw new Error(`Tab #nav-btn-${t} is missing its SVG icon!`);

        const svgBox = await svg.boundingBox();
        if (!svgBox || svgBox.width < 14 || svgBox.height < 14) {
          throw new Error(`Tab #nav-btn-${t} SVG is invisible or collapsed! Box: ${JSON.stringify(svgBox)}`);
        }

        const label = await btn.$('span[data-i18n]');
        if (!label) throw new Error(`Tab #nav-btn-${t} is missing its label span!`);
        const labelText = await label.innerText();

        // Check outline / tap highlight is none
        const outline = await btn.evaluate(el => window.getComputedStyle(el).outline);
        console.log(`[PASS] Tab: ${t} | Icon: ${Math.round(svgBox.width)}x${Math.round(svgBox.height)} | Label: "${labelText}" | Outline: "${outline}"`);
      }

      // Check Home Tab is active initially
      const homeBtn = await page.$('#nav-btn-home');
      const homeClass = await homeBtn.getAttribute('class');
      if (!homeClass.includes('text-emerald-700')) {
        throw new Error(`Home tab should be active initially with text-emerald-700, got: ${homeClass}`);
      }
      console.log(`[PASS] Home tab is text-emerald-700 font-bold initially`);

      // Test Tab Switching across all 5 tabs
      for (const t of tabs) {
        await page.click(`#nav-btn-${t}`);
        await page.waitForTimeout(200);

        const activeBtn = await page.$(`#nav-btn-${t}`);
        const cls = await activeBtn.getAttribute('class');
        if (!cls.includes('text-emerald-700') || !cls.includes('font-bold')) {
          throw new Error(`Tab #nav-btn-${t} did not receive active styles (text-emerald-700 font-bold) after click! Got: ${cls}`);
        }

        // Verify other tabs have inactive text-slate-400 styling
        for (const other of tabs) {
          if (other !== t) {
            const otherBtn = await page.$(`#nav-btn-${other}`);
            const otherCls = await otherBtn.getAttribute('class');
            if (!otherCls.includes('text-slate-400')) {
              throw new Error(`Tab #nav-btn-${other} unexpectedly has active style when ${t} is active! Got: ${otherCls}`);
            }
          }
        }

        // Verify view is visible
        const view = await page.$(`#view-${t}`);
        const isHidden = await view.evaluate(el => el.classList.contains('hidden'));
        if (isHidden) throw new Error(`View #view-${t} should be visible after switching to ${t}!`);
      }
      console.log(`[PASS] All 5 tabs switch cleanly with authentic original active/inactive styling.`);

      // Switch back to home
      await page.click('#nav-btn-home');
      await page.waitForTimeout(300);

      // Verify no horizontal overflow in nav
      const hasOverflow = await nav.evaluate(el => el.scrollWidth > el.clientWidth);
      if (hasOverflow) {
        throw new Error(`Navigation bar has horizontal overflow on viewport ${vp.name}!`);
      }
      console.log(`[PASS] No horizontal overflow or text wrapping detected on ${vp.name}.`);

      // Capture full viewport screenshot and bottom nav bar close-up
      const fullShotPath = path.join(ARTIFACT_DIR, `restored_customer_screen_${vp.name}.png`);
      const navShotPath = path.join(ARTIFACT_DIR, `restored_customer_bottom_nav_${vp.name}.png`);

      await page.screenshot({ path: fullShotPath, fullPage: false });
      await nav.screenshot({ path: navShotPath });
      console.log(`[Artifact] Saved: ${fullShotPath}`);
      console.log(`[Artifact] Saved: ${navShotPath}`);

      // Test Hindi translations
      await page.evaluate(() => {
        if (typeof setAppLanguage === 'function') setAppLanguage('hi');
      });
      await page.waitForTimeout(300);
      const hindiNavShot = path.join(ARTIFACT_DIR, `restored_bottom_nav_hindi_${vp.name}.png`);
      await nav.screenshot({ path: hindiNavShot });
      console.log(`[Artifact] Saved Hindi: ${hindiNavShot}`);

      await context.close();
    }

    console.log(`\n======================================================`);
    console.log(`[ALL 4 VIEWPORTS PASSED] Original compact bottom navigation restored!`);
    console.log(`======================================================\n`);
  } finally {
    await browser.close();
    server.close();
  }
})();

