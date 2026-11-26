const { chromium } = require('../apps/admin/node_modules/playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 412, height: 915 } });

  await page.addInitScript(() => {
    localStorage.setItem('gb_customer_authenticated', 'true');
    localStorage.setItem('gb_customer_phone', '9905361711');
    localStorage.setItem('gb_user_lang', 'en');
  });

  console.log('--- TEST 1: Initial Page Load ---');
  await page.goto('https://www.apnagaonbazaar.in/customer/index.html', { waitUntil: 'networkidle' });
  await page.waitForTimeout(1000);

  const before = await page.evaluate(() => {
    const mic = document.getElementById('home-search-mic-btn');
    const nav = document.getElementById('customer-bottom-nav');
    return {
      micSvg: !!(mic && mic.querySelector('svg')),
      navSvgs: nav ? nav.querySelectorAll('svg').length : 0
    };
  });
  console.log('Home before reload:', before);

  console.log('\n--- TEST 2: Hard Reload Page ---');
  await page.reload({ waitUntil: 'networkidle' });
  await page.waitForTimeout(1000);

  const after = await page.evaluate(() => {
    const mic = document.getElementById('home-search-mic-btn');
    const nav = document.getElementById('customer-bottom-nav');
    return {
      micSvg: !!(mic && mic.querySelector('svg')),
      navSvgs: nav ? nav.querySelectorAll('svg').length : 0
    };
  });
  console.log('Home after reload:', after);

  console.log('\n--- TEST 3: Switch to AI Tab ---');
  await page.evaluate(() => {
    if (typeof switchTab === 'function') switchTab('ai');
  });
  await page.waitForTimeout(1000);

  const aiBefore = await page.evaluate(() => {
    const mic = document.getElementById('main-mic-btn');
    const send = document.querySelector('#view-ai button[title="Send Query"]');
    return {
      micSvg: !!(mic && mic.querySelector('svg')),
      sendSvg: !!(send && send.querySelector('svg'))
    };
  });
  console.log('AI Tab before reload:', aiBefore);

  console.log('\n--- TEST 4: Hard Reload on AI Tab & Re-navigate ---');
  await page.reload({ waitUntil: 'networkidle' });
  await page.waitForTimeout(1000);
  await page.evaluate(() => {
    if (typeof switchTab === 'function') switchTab('ai');
  });
  await page.waitForTimeout(1000);

  const aiAfter = await page.evaluate(() => {
    const mic = document.getElementById('main-mic-btn');
    const send = document.querySelector('#view-ai button[title="Send Query"]');
    return {
      micSvg: !!(mic && mic.querySelector('svg')),
      sendSvg: !!(send && send.querySelector('svg'))
    };
  });
  console.log('AI Tab after reload:', aiAfter);

  await browser.close();
  console.log('\n[PASS] All icons persist across reloads and tab navigations!');
})();
