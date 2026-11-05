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

viewports = [
    {"name": "360px (Compact Mobile)", "width": 360, "height": 780},
    {"name": "393px (Standard Mobile)", "width": 393, "height": 852},
    {"name": "412px (Large Mobile)", "width": 412, "height": 915},
]

async def run_eval_for_viewport(ws, vp):
    print(f"\n--- Testing Viewport: {vp['name']} ({vp['width']}x{vp['height']}) ---")
    
    # 1. Emulation
    await ws.send(json.dumps({
        "id": 10,
        "method": "Emulation.setDeviceMetricsOverride",
        "params": {
            "width": vp["width"],
            "height": vp["height"],
            "deviceScaleFactor": 2.0,
            "mobile": True
        }
    }))
    await ws.recv()

    test_expression = """
    (async () => {
      const res = [];
      function check(pass, msg) {
        res.push({ pass: !!pass, msg });
      }

      // Wait briefly for CDN scripts (Leaflet) to be ready
      for (let i = 0; i < 30; i++) {
        if (typeof window.L !== 'undefined') break;
        await new Promise(r => setTimeout(r, 100));
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
      check(typeof window.openManageAddressesModal === 'function', 'openManageAddressesModal defined');
      check(typeof window.renderManageAddressesList === 'function', 'renderManageAddressesList defined');
      check(typeof window.renderAccountAddressSummary === 'function', 'renderAccountAddressSummary defined');
      check(typeof window.openLocationMapPickerModal === 'function', 'openLocationMapPickerModal defined');
      check(typeof window.resolveRationItemDetails === 'function', 'resolveRationItemDetails defined');
      check(typeof window.proceedToMonthlyRationOrderReview === 'function', 'proceedToMonthlyRationOrderReview defined');
      check(typeof window.confirmMonthlyRationDirectOrder === 'function', 'confirmMonthlyRationDirectOrder defined');
      check(window.productCatalog === window.productsCatalog, 'productCatalog aliases productsCatalog');

      // 2. Authenticate and enter dashboard
      localStorage.setItem('gb_customer_authenticated', 'true');
      localStorage.setItem('gb_customer_phone', '9876543210');
      localStorage.setItem('gb_active_order_id', 'GB-TEST-9901');
      localStorage.setItem('gb_active_order_otp', '7842');

      document.getElementById('page-language').classList.add('hidden');
      document.getElementById('page-login').classList.add('hidden');
      document.getElementById('dashboard-container').classList.remove('hidden');

      // 3. Scroll lock test - initially body should NOT have overflow-hidden
      check(!document.body.classList.contains('overflow-hidden'), 'Body is NOT scroll-locked on home/dashboard');

      // 4. Modals and Scroll Lock Clean-up
      openModal('modal-edit-profile');
      const editM = document.getElementById('modal-edit-profile');
      check(!editM.classList.contains('hidden'), 'modal-edit-profile opened');
      check(document.body.classList.contains('overflow-hidden'), 'Body locked while modal is open');
      closeModal('modal-edit-profile');
      check(editM.classList.contains('hidden'), 'modal-edit-profile closed');
      check(!document.body.classList.contains('overflow-hidden'), 'Body scroll restored after modal closes');

      // 5. Saved Addresses on Account Tab
      switchTab('account');
      const accV = document.getElementById('view-account');
      check(!accV.classList.contains('hidden'), 'Account view active');
      check(!document.body.classList.contains('overflow-hidden'), 'Body scrollable on Account tab');

      // Set synthetic address in state and render
      window.userSavedAddresses = [
        {
          id: 'addr_test_1',
          title: 'Home / घर',
          recipient_name: 'Ramesh Patel',
          phone: '9876543210',
          village: 'Bithoor',
          landmark: 'Near Shiva Temple',
          is_default: true,
          latitude: 26.6139,
          longitude: 80.2718
        },
        {
          id: 'addr_test_2',
          title: 'Farm / खेत',
          recipient_name: 'Ramesh Patel',
          phone: '9876543210',
          village: 'Parihar',
          landmark: 'Tubewell 4',
          is_default: false,
          latitude: 26.6200,
          longitude: 80.2800
        }
      ];
      renderAccountAddressSummary();

      const summaryCard = document.getElementById('account-default-address-container');
      check(summaryCard && !summaryCard.classList.contains('hidden'), 'Default address summary container rendered on Account');
      check(summaryCard.textContent.includes('Bithoor'), 'Default address card shows Bithoor');
      check(summaryCard.textContent.includes('Near Shiva Temple'), 'Default address card shows landmark');
      
      const countLabel = document.getElementById('saved-addresses-count-label');
      check(countLabel && countLabel.textContent.includes('2 Saved Locations'), 'Count label displays 2 Saved Locations');

      // 6. Manage Addresses Subview Modal
      openManageAddressesModal();
      const manageM = document.getElementById('modal-manage-addresses');
      check(!manageM.classList.contains('hidden'), 'Manage addresses modal opened');
      const manageItems = document.querySelectorAll('#manage-addresses-list-container > div');
      check(manageItems.length === 2, 'Manage addresses container lists exactly 2 addresses (got ' + manageItems.length + ')');
      closeModal('modal-manage-addresses');
      check(manageM.classList.contains('hidden'), 'Manage addresses modal closed');
      check(!document.body.classList.contains('overflow-hidden'), 'Body scroll unlocked after manage addresses closed');

      // 7. Location Map Picker Modal
      openLocationMapPickerModal();
      const mapM = document.getElementById('modal-location-map-picker');
      check(!mapM.classList.contains('hidden'), 'Location map picker modal opened');
      check(typeof window.locationPickerMap !== 'undefined' && window.locationPickerMap !== null, 'Leaflet locationPickerMap instance exists');
      closeModal('modal-location-map-picker');
      check(mapM.classList.contains('hidden'), 'Location map picker modal closed');

      // 8. Monthly Ration Item Resolution (No undefined, No 0.00)
      const rawAtta = {
        id: 'mr_1',
        product_name_en: 'Aashirvaad Shudh Chakki Atta',
        product_name_hi: 'आशीर्वाद चक्की आटा',
        quantity: 2,
        unit: '5 kg'
      };
      const resolvedAtta = resolveRationItemDetails(rawAtta);
      check(resolvedAtta.name !== 'undefined' && resolvedAtta.name.includes('Aashirvaad'), 'Resolved Atta has valid product name: ' + resolvedAtta.name);
      check(resolvedAtta.price > 0, 'Resolved Atta has positive unit price: ₹' + resolvedAtta.price);
      check(resolvedAtta.price * 2 === 430, 'Resolved Atta total matches 215 * 2 = 430');

      // Monthly Ration Modal Open & Render
      await openMonthlyRationModal();
      const ratM = document.getElementById('modal-monthly-ration');
      check(!ratM.classList.contains('hidden'), 'Monthly ration modal opened');
      
      const ratCards = document.querySelectorAll('#ration-items-container > div');
      check(ratCards.length > 0, 'Monthly ration items rendered cleanly in modal (got ' + ratCards.length + ')');
      const firstRatText = ratCards[0].textContent;
      check(!firstRatText.includes('undefined'), 'Monthly ration card contains NO undefined text');
      check(!firstRatText.includes('₹0.00'), 'Monthly ration card contains NO ₹0.00 pricing');

      // Test Direct Order Review Modal
      await proceedToMonthlyRationOrderReview();
      const revM = document.getElementById('modal-ration-order-review');
      check(!revM.classList.contains('hidden'), 'Monthly ration order review modal opened');
      check(document.getElementById('ration-review-items-container').children.length > 0, 'Order review list has line items');
      check(document.getElementById('ration-review-grand-total').textContent.includes('₹'), 'Order review displays computed grand total');
      closeModal('modal-ration-order-review');
      closeModal('modal-monthly-ration');
      check(!document.body.classList.contains('overflow-hidden'), 'Body unlocked after closing ration modals');

      // 9. Orders Tab & OTP Reveal
      switchTab('orders');
      const ordersV = document.getElementById('view-orders');
      check(!ordersV.classList.contains('hidden'), 'Orders view active');
      const otpEl = document.getElementById('order-otp-badge');
      if (otpEl && otpEl.textContent.includes('•')) {
        revealDeliveryOtp();
      }
      check(otpEl && !otpEl.textContent.includes('•') && otpEl.textContent.includes('7842'), 'Delivery OTP revealed on button click');

      // 10. Cart Tab & Payment Mode
      switchTab('cart');
      const upiRadio = document.querySelector('input[name="payment_mode"][value="ONLINE"]');
      check(upiRadio && upiRadio.disabled, 'UPI online radio is disabled');
      const codRadio = document.querySelector('input[name="payment_mode"][value="COD"]');
      check(codRadio && codRadio.checked, 'COD is selected by default');

      // 11. Image Verification in Catalog
      const chakkiAtta = productsCatalog.find(p => p.id === 'p1');
      check(chakkiAtta && chakkiAtta.img.includes('1509440159596'), 'Chakki Atta uses verified wheat flour sack URL: ' + chakkiAtta.img);
      const sugar = productsCatalog.find(p => p.id === 'p4');
      check(sugar && sugar.img.includes('1587132137056'), 'Sugar uses verified sugar bowl URL');
      const salt = productsCatalog.find(p => p.id === 'p10');
      check(salt && salt.img.includes('1626197031507'), 'Salt uses verified salt crystals URL');
      const det = productsCatalog.find(p => p.id === 'p9');
      check(det && det.img.includes('1583947215259'), 'Detergent uses verified detergent pack URL');
      const dal = productsCatalog.find(p => p.id === 'p7');
      check(dal && dal.img.includes('1596040033229'), 'Toor Dal uses verified pulse legumes URL: ' + (dal ? dal.img : 'not found'));

      // 12. Final switch back to Home and scroll lock check
      switchTab('home');
      check(!document.body.classList.contains('overflow-hidden'), 'Body is free to scroll on Home tab');

      return res;
    })()
    """

    await ws.send(json.dumps({
        "id": 20,
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
        if data.get("id") == 20:
            if "exceptionDetails" in data["result"]:
                print("JS Execution Exception:", data["result"]["exceptionDetails"])
                return False
            result_val = data["result"]["result"]["value"]
            all_passed = True
            for item in result_val:
                status = "PASS" if item["pass"] else "FAIL"
                if not item["pass"]:
                    all_passed = False
                print(f"  [{status}] {item['msg']}")
            print(f"Viewport {vp['name']} Result: {len(result_val)} checks, Passed: {all_passed}")
            return all_passed

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
    time.sleep(3.0)

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

            await asyncio.sleep(2.0)

            overall_pass = True
            for vp in viewports:
                ok = await run_eval_for_viewport(ws, vp)
                if not ok:
                    overall_pass = False

            print(f"\n==========================================")
            print(f"ALL VIEWPORTS EVALUATION: {'ALL PASSED' if overall_pass else 'FAILURES DETECTED'}")
            print(f"==========================================")
            if not overall_pass:
                sys.exit(1)

    finally:
        chrome_proc.terminate()
        server_proc.terminate()

if __name__ == "__main__":
    asyncio.run(main())
