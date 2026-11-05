import subprocess
import os
import sys
import json
import time
import urllib.request
import urllib.parse

sys.stdout.reconfigure(encoding='utf-8')

port = 8095
chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
temp_dir = r"C:\Users\dhira\AppData\Local\Temp\chrome_ui_test"

# Serve public_web
server_proc = subprocess.Popen(
    [sys.executable, "-m", "http.server", str(port), "--directory", "public_web"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)
time.sleep(1.5)

print(f"Local test server running on http://127.0.0.1:{port}")

# Test script to execute inside Customer page
test_js = """
(() => {
  const results = [];
  function assert(condition, message) {
    if (!condition) {
      results.push({ pass: false, message });
      console.error('FAIL: ' + message);
    } else {
      results.push({ pass: true, message });
      console.log('PASS: ' + message);
    }
  }

  try {
    // 1. Initial State & Language
    assert(typeof window.openModal === 'function', 'window.openModal is a function');
    assert(typeof window.closeModal === 'function', 'window.closeModal is a function');
    assert(typeof window.loadUserProfile === 'function', 'window.loadUserProfile is a function');
    assert(typeof window.saveUserProfile === 'function', 'window.saveUserProfile is a function');
    assert(typeof window.openMyTicketsModal === 'function', 'window.openMyTicketsModal is a function');
    assert(typeof window.submitCustomerSupportTicket === 'function', 'window.submitCustomerSupportTicket is a function');
    assert(typeof window.renderFaqAccordion === 'function', 'window.renderFaqAccordion is a function');
    assert(typeof window.revealDeliveryOtp === 'function', 'window.revealDeliveryOtp is a function');
    assert(Array.isArray(window.productsCatalog), 'window.productsCatalog is an array');
    assert(window.productCatalog === window.productsCatalog, 'window.productCatalog aliases window.productsCatalog');

    // Authenticate customer in session
    localStorage.setItem('gb_customer_authenticated', 'true');
    localStorage.setItem('gb_customer_phone', '9876543210');
    localStorage.setItem('gb_customer_jwt', 'test_jwt_token_rural_123');
    localStorage.setItem('gb_active_order_id', 'GB-TEST-9901');
    localStorage.setItem('gb_active_order_otp', '7842');

    document.getElementById('page-language').classList.add('hidden');
    document.getElementById('page-login').classList.add('hidden');
    document.getElementById('dashboard-container').classList.remove('hidden');

    // 2. Test Account Modals
    switchTab('account');
    loadUserProfile();
    const nameEl = document.getElementById('user-display-name');
    assert(nameEl && nameEl.textContent.trim().length > 0, 'User profile display name populated: ' + nameEl?.textContent);

    // Test Edit Profile Modal
    openModal('modal-edit-profile');
    const editModal = document.getElementById('modal-edit-profile');
    assert(!editModal.classList.contains('hidden'), 'Edit Profile modal is open (not hidden)');
    const editNameInput = document.getElementById('edit-profile-name');
    assert(editNameInput && editNameInput.value.length > 0, 'Edit Profile name input populated');
    closeModal('modal-edit-profile');
    assert(editModal.classList.contains('hidden'), 'Edit Profile modal closed cleanly');

    // Test FAQ Modal and Accordion
    openModal('modal-faq');
    const faqModal = document.getElementById('modal-faq');
    assert(!faqModal.classList.contains('hidden'), 'FAQ modal is open');
    renderFaqAccordion();
    const faqContainer = document.getElementById('faq-accordion-container');
    const faqCards = faqContainer.querySelectorAll('.border');
    assert(faqCards.length >= 10, 'FAQ accordion rendered ' + faqCards.length + ' topic cards');
    // Test toggle first FAQ
    toggleFaqAccordion(0);
    const ans0 = document.getElementById('faq-ans-0');
    assert(!ans0.classList.contains('hidden'), 'FAQ topic 0 expanded on click');
    closeModal('modal-faq');
    assert(faqModal.classList.contains('hidden'), 'FAQ modal closed cleanly');

    // Test Support Tickets Modal
    openMyTicketsModal();
    const ticketsModal = document.getElementById('modal-my-tickets');
    assert(!ticketsModal.classList.contains('hidden'), 'My Tickets modal is open');
    closeModal('modal-my-tickets');

    // Test Payment Settings Modal
    openModal('modal-payment-settings');
    const payModal = document.getElementById('modal-payment-settings');
    assert(!payModal.classList.contains('hidden'), 'Payment Settings modal is open');
    assert(payModal.textContent.includes('Coming Soon'), 'Payment modal shows UPI Coming Soon');
    assert(payModal.textContent.includes('Cash on Delivery'), 'Payment modal shows Cash on Delivery');
    closeModal('modal-payment-settings');

    // 3. Test Orders Tab & OTP Reveal
    switchTab('orders');
    const ordersView = document.getElementById('view-orders');
    assert(!ordersView.classList.contains('hidden'), 'Orders tab is active');
    revealDeliveryOtp();
    const otpBadge = document.getElementById('order-otp-badge');
    assert(otpBadge && (otpBadge.textContent.includes('7842') || otpBadge.textContent.includes('4921') || otpBadge.textContent.includes('6629')), 'Delivery OTP revealed on button click: ' + otpBadge?.textContent.trim());

    // 4. Test Monthly Ration Card & Modal
    openMonthlyRationModal();
    const rationModal = document.getElementById('modal-monthly-ration');
    assert(!rationModal.classList.contains('hidden'), 'Monthly Ration modal is open');
    closeModal('modal-monthly-ration');

    // 5. Test Cart Tab & Payment Truth
    switchTab('home');
    addProductToCart('p1', 2);
    addProductToCart('p2', 1);
    switchTab('cart');
    const cartView = document.getElementById('view-cart');
    assert(!cartView.classList.contains('hidden'), 'Cart view is active');
    const onlineRadio = document.querySelector('input[name="payment_mode"][value="ONLINE"]');
    assert(onlineRadio && onlineRadio.disabled === true, 'Online UPI radio in Cart is disabled (honest sandbox)');
    const codRadio = document.querySelector('input[name="payment_mode"][value="COD"]');
    assert(codRadio && codRadio.checked === true, 'COD radio in Cart is active and checked by default');

    // 6. Test Product Image Integrity
    const sugarItem = productsCatalog.find(p => p.id === 'p4');
    assert(sugarItem && !sugarItem.img.includes('1581441363689'), 'Sugar does not use old rose image URL: ' + sugarItem?.img);
    assert(sugarItem && sugarItem.img.includes('1587132137056'), 'Sugar uses verified sugar bowl URL');

    const saltItem = productsCatalog.find(p => p.id === 'p10');
    assert(saltItem && !saltItem.img.includes('1518110903415'), 'Salt does not use broken 404 image URL');
    assert(saltItem && saltItem.img.includes('1626197031507'), 'Salt uses verified salt shaker URL');

    const detergentItem = productsCatalog.find(p => p.id === 'p9');
    assert(detergentItem && !detergentItem.img.includes('1585421514738'), 'Detergent does not use blue surgical glove image');
    assert(detergentItem && detergentItem.img.includes('1583947215259'), 'Detergent uses verified detergent packet URL');

  } catch (err) {
    results.push({ pass: false, message: 'Exception during DOM execution: ' + err.stack });
  }

  window.__testResults = results;
  return results;
})();
"""

# Create a test runner HTML page that loads customer index and runs the test
runner_html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Customer UI Test Harness</title>
</head>
<body>
  <iframe id="app-frame" src="/customer/index.html" style="width: 412px; height: 915px; border: 1px solid #ccc;"></iframe>
  <script>
    const frame = document.getElementById('app-frame');
    frame.onload = () => {{
      setTimeout(() => {{
        try {{
          const win = frame.contentWindow;
          const res = win.eval(`{test_js}`);
          document.body.setAttribute('data-test-status', 'FINISHED');
          document.body.setAttribute('data-test-results', JSON.stringify(res));
          console.log('TEST_RUN_COMPLETE: ' + JSON.stringify(res));
        }} catch(e) {{
          document.body.setAttribute('data-test-status', 'ERROR');
          document.body.setAttribute('data-test-error', e.message);
          console.error(e);
        }}
      }}, 1200);
    }};
  </script>
</body>
</html>"""

with open("public_web/test_runner.html", "w", encoding="utf-8") as f:
    f.write(runner_html)

print("Running headless Chrome against http://127.0.0.1:" + str(port) + "/test_runner.html ...")

try:
    cmd = [
        chrome_path,
        "--headless=new",
        "--disable-gpu",
        "--enable-logging=stderr",
        "--v=1",
        f"--user-data-dir={temp_dir}",
        f"http://127.0.0.1:{port}/test_runner.html"
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
    time.sleep(6)
    proc.terminate()
    stdout, stderr = proc.communicate(timeout=5)
    
    print("\n--- Chrome Log Output ---")
    matched = False
    for line in (stdout + stderr).splitlines():
        if "TEST_RUN_COMPLETE" in line or "PASS:" in line or "FAIL:" in line:
            print(line)
            matched = True
            
    if not matched:
        print("Stderr sample:")
        print(stderr[:1000])

finally:
    server_proc.terminate()
    server_proc.wait()
    if os.path.exists("public_web/test_runner.html"):
        os.remove("public_web/test_runner.html")
    print("\nTest run finished.")
