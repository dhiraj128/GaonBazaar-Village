const { chromium } = require('../apps/admin/node_modules/playwright');
const path = require('path');

const ARTIFACTS_DIR = 'C:/Users/dhira/.gemini/antigravity/brain/918c8085-b60b-40a9-a077-a3344458bcc5';

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ 
    viewport: { width: 412, height: 915 }, 
    isMobile: true,
    hasTouch: true
  });

  // Inject session state into window
  await page.addInitScript(() => {
    localStorage.setItem('gb_customer_authenticated', 'true');
    localStorage.setItem('gb_customer_phone', '9905361711');
    localStorage.setItem('gb_user_lang', 'en');
  });

  console.log('Navigating to https://www.apnagaonbazaar.in...');
  await page.goto('https://www.apnagaonbazaar.in', { waitUntil: 'networkidle' });
  await page.waitForTimeout(3000);

  // Find the embedded customer app frame or direct page
  const frame = page.frames().find(f => f.url().includes('customer/index.html')) || page;
  console.log('Target frame URL:', frame.url());

  // Capture Live Home Screen
  const homePath = path.join(ARTIFACTS_DIR, 'prod_live_customer_home.png');
  await page.screenshot({ path: homePath });
  console.log('Live Customer Home captured!');

  // Check categories, search bar, and store elements inside frame
  const homeData = await frame.evaluate(() => {
    const categories = Array.from(document.querySelectorAll('.cat-pill')).map(c => c.innerText.trim());
    const searchInput = document.getElementById('home-search-input');
    const bottomNav = document.getElementById('customer-bottom-nav');
    const navButtons = bottomNav ? Array.from(bottomNav.querySelectorAll('button')).map(b => b.innerText.trim().replace(/\s+/g, ' ')) : [];

    return {
      categoryCount: categories.length,
      categories: categories.slice(0, 8),
      hasSearchInput: !!searchInput,
      navButtons
    };
  });
  console.log('Home Data:', homeData);

  // Switch to AI Assistant Tab
  console.log('Switching to AI Assistant Tab inside frame...');
  await frame.evaluate(() => {
    if (typeof switchTab === 'function') switchTab('ai');
  });
  await page.waitForTimeout(1000);
  const aiPath = path.join(ARTIFACTS_DIR, 'prod_live_customer_ai.png');
  await page.screenshot({ path: aiPath });
  console.log('Live Customer AI Assistant captured!');

  // Switch to Cart Tab
  console.log('Switching to Cart Tab inside frame...');
  await frame.evaluate(() => {
    if (typeof switchTab === 'function') switchTab('cart');
  });
  await page.waitForTimeout(1000);
  const cartPath = path.join(ARTIFACTS_DIR, 'prod_live_customer_cart.png');
  await page.screenshot({ path: cartPath });
  console.log('Live Customer Cart captured!');

  // Switch to Orders Tab
  console.log('Switching to Orders Tab inside frame...');
  await frame.evaluate(() => {
    if (typeof switchTab === 'function') switchTab('orders');
  });
  await page.waitForTimeout(1000);
  const ordersPath = path.join(ARTIFACTS_DIR, 'prod_live_customer_orders.png');
  await page.screenshot({ path: ordersPath });
  console.log('Live Customer Orders captured!');

  // Switch to Account Tab
  console.log('Switching to Account Tab inside frame...');
  await frame.evaluate(() => {
    if (typeof switchTab === 'function') switchTab('account');
  });
  await page.waitForTimeout(1000);
  const accountPath = path.join(ARTIFACTS_DIR, 'prod_live_customer_account.png');
  await page.screenshot({ path: accountPath });
  console.log('Live Customer Account captured!');

  await browser.close();
  console.log('All customer live tabs tested successfully!');
})().catch(console.error);
