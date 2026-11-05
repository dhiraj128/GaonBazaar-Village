import asyncio
import subprocess
import os
import sys
import json
import time
import urllib.request
import websockets

sys.stdout.reconfigure(encoding='utf-8')

port = 8097
cdp_port = 9224
chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
temp_dir = r"C:\Users\dhira\AppData\Local\Temp\chrome_real_eval"

async def main():
    server_proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port), "--directory", "public_web"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(1.5)

    chrome_proc = subprocess.Popen([
        chrome_path,
        "--headless=new",
        "--disable-gpu",
        f"--remote-debugging-port={cdp_port}",
        f"--user-data-dir={temp_dir}",
        f"http://127.0.0.1:{port}/customer/index.html"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2.5)

    try:
        resp = urllib.request.urlopen(f"http://127.0.0.1:{cdp_port}/json")
        tabs = json.loads(resp.read().decode())
        
        target = None
        for t in tabs:
            if t.get("type") == "page" and "customer/index.html" in t.get("url", ""):
                target = t
                break
        if not target:
            target = [t for t in tabs if t.get("type") == "page"][0]
            
        ws_url = target["webSocketDebuggerUrl"]
        print(f"Connected to Chrome page: {target.get('url')}")

        async with websockets.connect(ws_url) as ws:
            await ws.send(json.dumps({"id": 1, "method": "Runtime.enable"}))
            await ws.recv()

            # Wait briefly for page scripts to settle
            await asyncio.sleep(1.0)

            test_expression = """
            (() => {
              const res = [];
              function check(pass, msg) {
                res.push({ pass: !!pass, msg });
              }

              // 1. Function existence
              check(typeof window.openModal === 'function', 'openModal defined');
              check(typeof window.closeModal === 'function', 'closeModal defined');
              check(typeof window.loadUserProfile === 'function', 'loadUserProfile defined');
              check(typeof window.saveUserProfile === 'function', 'saveUserProfile defined');
              check(typeof window.openMyTicketsModal === 'function', 'openMyTicketsModal defined');
              check(typeof window.submitCustomerSupportTicket === 'function', 'submitCustomerSupportTicket defined');
              check(typeof window.renderFaqAccordion === 'function', 'renderFaqAccordion defined');
              check(typeof window.revealDeliveryOtp === 'function', 'revealDeliveryOtp defined');
              check(window.productCatalog === window.productsCatalog, 'productCatalog aliases productsCatalog');

              // 2. Authenticate and enter dashboard
              localStorage.setItem('gb_customer_authenticated', 'true');
              localStorage.setItem('gb_customer_phone', '9876543210');
              localStorage.setItem('gb_active_order_id', 'GB-TEST-9901');
              localStorage.setItem('gb_active_order_otp', '7842');

              document.getElementById('page-language').classList.add('hidden');
              document.getElementById('page-login').classList.add('hidden');
              document.getElementById('dashboard-container').classList.remove('hidden');

              // 3. Modals Test
              openModal('modal-edit-profile');
              const editM = document.getElementById('modal-edit-profile');
              check(!editM.classList.contains('hidden'), 'modal-edit-profile opened');
              closeModal('modal-edit-profile');
              check(editM.classList.contains('hidden'), 'modal-edit-profile closed');

              openModal('modal-faq');
              const faqM = document.getElementById('modal-faq');
              check(!faqM.classList.contains('hidden'), 'modal-faq opened');
              renderFaqAccordion();
              const faqs = document.querySelectorAll('#faq-accordion-container .border');
              check(faqs.length === 14, 'All 14 FAQ topics rendered (got ' + faqs.length + ')');
              toggleFaqAccordion(0);
              const ans0 = document.getElementById('faq-ans-0');
              check(!ans0.classList.contains('hidden'), 'FAQ topic 0 expanded');
              closeModal('modal-faq');

              openMyTicketsModal();
              const tckM = document.getElementById('modal-my-tickets');
              check(!tckM.classList.contains('hidden'), 'modal-my-tickets opened');
              closeModal('modal-my-tickets');

              openModal('modal-payment-settings');
              const payM = document.getElementById('modal-payment-settings');
              check(!payM.classList.contains('hidden'), 'modal-payment-settings opened');
              check(payM.textContent.includes('Coming Soon'), 'Payment modal specifies Coming Soon for UPI');
              closeModal('modal-payment-settings');

              // 4. Orders Tab & OTP Reveal & Monthly Ration
              switchTab('orders');
              const ordersV = document.getElementById('view-orders');
              check(!ordersV.classList.contains('hidden'), 'Orders view active');
              revealDeliveryOtp();
              const otpEl = document.getElementById('order-otp-badge');
              check(otpEl && !otpEl.textContent.includes('•'), 'Delivery OTP revealed on button click');

              openMonthlyRationModal();
              const ratM = document.getElementById('modal-monthly-ration');
              check(!ratM.classList.contains('hidden'), 'modal-monthly-ration opened');
              closeModal('modal-monthly-ration');

              // 5. Cart Tab & Payment Mode
              switchTab('cart');
              const upiRadio = document.querySelector('input[name="payment_mode"][value="ONLINE"]');
              check(upiRadio && upiRadio.disabled, 'UPI online radio is disabled');
              const codRadio = document.querySelector('input[name="payment_mode"][value="COD"]');
              check(codRadio && codRadio.checked, 'COD is selected by default');

              // 6. Image Verification
              const sugar = productsCatalog.find(p => p.id === 'p4');
              check(sugar && sugar.img.includes('1587132137056'), 'Sugar uses verified sugar bowl URL');
              const salt = productsCatalog.find(p => p.id === 'p10');
              check(salt && salt.img.includes('1626197031507'), 'Salt uses verified salt shaker URL');
              const det = productsCatalog.find(p => p.id === 'p9');
              check(det && det.img.includes('1583947215259'), 'Detergent uses verified detergent URL');

              return res;
            })()
            """

            await ws.send(json.dumps({
                "id": 2,
                "method": "Runtime.evaluate",
                "params": {
                    "expression": test_expression,
                    "returnByValue": True,
                    "awaitPromise": True
                }
            }))

            while True:
                msg = await ws.recv()
                data = json.loads(msg)
                if data.get("id") == 2:
                    if "exceptionDetails" in data["result"]:
                        print("JS Execution Exception:", data["result"]["exceptionDetails"])
                        break
                    result_val = data["result"]["result"]["value"]
                    print("\n=== REAL BROWSER UI TEST RESULTS ===")
                    all_passed = True
                    for item in result_val:
                        status = "PASS" if item["pass"] else "FAIL"
                        if not item["pass"]:
                            all_passed = False
                        print(f"[{status}] {item['msg']}")
                    print(f"\nSummary: Total={len(result_val)}, All Passed={all_passed}")
                    break

    finally:
        chrome_proc.terminate()
        server_proc.terminate()

if __name__ == "__main__":
    asyncio.run(main())
