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

  console.log('Navigating to https://www.apnagaonbazaar.in...');
  await page.goto('https://www.apnagaonbazaar.in', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(3000);

  // Click continue on language screen
  console.log('Clicking Continue on Language Screen...');
  const continueBtn = await page.waitForSelector('button:has-text("Continue")', { timeout: 5000 });
  await continueBtn.click();
  await page.waitForTimeout(1000);

  // Capture Login Screen
  await page.screenshot({ path: path.join(ARTIFACTS_DIR, 'prod_customer_login_screen.png') });
  console.log('Login screen captured!');

  // Check login screen fields
  const loginDetails = await page.evaluate(() => {
    const phoneInput = document.getElementById('login-phone') || document.querySelector('input[type="tel"]');
    const otpBtn = document.getElementById('btn-send-otp') || document.querySelector('button[onclick*="sendOtp"]');
    return {
      hasPhoneInput: !!phoneInput,
      hasOtpButton: !!otpBtn,
      otpButtonText: otpBtn ? otpBtn.innerText.trim() : null
    };
  });
  console.log('Login screen details:', loginDetails);

  await browser.close();
})().catch(console.error);
