import asyncio
import subprocess
import os
import sys
import json
import time
import base64
import urllib.request
import websockets

sys.stdout.reconfigure(encoding='utf-8')

port = 8097
cdp_port = 9224
chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
temp_dir = r"C:\Users\dhira\AppData\Local\Temp\chrome_real_eval"
artifact_dir = r"C:\Users\dhira\.gemini\antigravity\brain\918c8085-b60b-40a9-a077-a3344458bcc5"

viewports = [
    {"name": "360px (Compact Mobile)", "width": 360, "height": 780},
    {"name": "393px (Standard Mobile)", "width": 393, "height": 852},
    {"name": "412px (Large Mobile)", "width": 412, "height": 915},
]

async def capture_screenshot(ws, filename):
    await ws.send(json.dumps({
        "id": 999,
        "method": "Page.captureScreenshot",
        "params": {"format": "png"}
    }))
    while True:
        resp = json.loads(await ws.recv())
        if resp.get("id") == 999:
            data = base64.b64decode(resp["result"]["data"])
            path = os.path.join(artifact_dir, filename)
            with open(path, "wb") as f:
                f.write(data)
            print(f"Captured screenshot: {filename} ({len(data)} bytes)")
            return path

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
      check(typeof window.submitCustomerSupportTicketWithEvidence === 'function', 'submitCustomerSupportTicketWithEvidence defined');
      check(typeof window.renderFaqAccordion === 'function', 'renderFaqAccordion defined');
      check(typeof window.revealDeliveryOtp === 'function', 'revealDeliveryOtp defined');
      check(typeof window.openManageAddressesModal === 'function', 'openManageAddressesModal defined');
      check(typeof window.renderManageAddressesList === 'function', 'renderManageAddressesList defined');
      check(typeof window.renderAccountAddressSummary === 'function', 'renderAccountAddressSummary defined');
      check(typeof window.openLocationMapPickerModal === 'function', 'openLocationMapPickerModal defined');
      check(typeof window.resolveRationItemDetails === 'function', 'resolveRationItemDetails defined');
      check(typeof window.proceedToMonthlyRationOrderReview === 'function', 'proceedToMonthlyRationOrderReview defined');
      check(typeof window.confirmMonthlyRationDirectOrder === 'function', 'confirmMonthlyRationDirectOrder defined');
      check(typeof window.openPickerPinInExternalMaps === 'function', 'openPickerPinInExternalMaps defined');
      check(typeof window.clearPickerMarkerPin === 'function', 'clearPickerMarkerPin defined');
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
          title: 'Home',
          recipient_name: 'Dhiraj Sharma',
          phone: '9876543210',
          village: 'Chaturshi, Muzaffarpur',
          landmark: 'Near Shiv Mandir',
          district: 'Muzaffarpur',
          is_default: true,
          latitude: 26.2315,
          longitude: 85.3610
        },
        {
          id: 'addr_test_2',
          title: 'Work',
          recipient_name: 'Dhiraj Sharma',
          phone: '9876543210',
          village: 'Parihar',
          landmark: 'Tubewell 4',
          district: 'Muzaffarpur',
          is_default: false,
          latitude: 26.2500,
          longitude: 85.3800
        }
      ];
      renderAccountAddressSummary();

      const summaryCard = document.getElementById('account-default-address-container');
      check(summaryCard && !summaryCard.classList.contains('hidden'), 'Default address summary container rendered on Account');
      check(summaryCard.textContent.includes('Chaturshi'), 'Default address card shows Chaturshi');
      check(summaryCard.textContent.includes('Near Shiv Mandir'), 'Default address card shows landmark');
      check(!summaryCard.textContent.includes('26.2315'), 'Default address card has NO raw latitude');
      
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

      // Test 4 delivery fee bands
      updatePickerGeofence(26.2315, 85.3610);
      const b1 = document.getElementById('picker-service-badge').textContent;
      check(b1.includes('₹15'), '0-2 km band displays ₹15: ' + b1);

      updatePickerGeofence(26.2550, 85.3610);
      const b2 = document.getElementById('picker-service-badge').textContent;
      check(b2.includes('₹20'), 'Above 2-4 km band displays ₹20: ' + b2);

      updatePickerGeofence(26.2730, 85.3610);
      const b3 = document.getElementById('picker-service-badge').textContent;
      check(b3.includes('₹25'), 'Above 4-5 km band displays ₹25: ' + b3);

      updatePickerGeofence(26.2900, 85.3610);
      const b4 = document.getElementById('picker-service-badge').textContent;
      check(b4.includes('₹35'), 'Above 5-8 km band displays ₹35: ' + b4);

      updatePickerGeofence(26.4500, 85.7000);
      const b5 = document.getElementById('picker-service-badge').textContent;
      check(b5.includes('Delivery is not available at this location yet'), 'Above 8 km shows unserviceable warning: ' + b5);
      const btnConfirm = document.getElementById('btn-confirm-map-pin');
      check(btnConfirm && btnConfirm.disabled, 'Confirm button disabled when outside 8km');

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

      // 9b. Past Orders Rendering & Buy Again Logic
      await renderPastOrdersList();
      const pastContainer = document.getElementById('past-orders-list-container');
      check(pastContainer && pastContainer.children.length > 0, 'Past orders rendered in container');
      check(!pastContainer.textContent.includes('Invalid Date'), 'Past orders contain NO Invalid Date strings');
      
      // Test handleBuyAgain on first past order
      await handleBuyAgain('GB-ORD-7108');
      check(window.cart && window.cart.length > 0, 'handleBuyAgain populated cart with past order items');
      check(!document.getElementById('view-cart').classList.contains('hidden'), 'handleBuyAgain navigated to Cart tab');
      const reorderBadge = document.getElementById('nav-cart-badge');
      check(reorderBadge && parseInt(reorderBadge.textContent) >= 1, 'handleBuyAgain dynamically updated Cart icon badge');

      // 10. Cart Tab: Clean Empty Cart vs Products
      switchTab('cart');
      window.cartItems = [];
      renderCartItems();
      const chkSections = document.getElementById('cart-checkout-sections');
      check(chkSections && chkSections.classList.contains('hidden'), 'Empty cart hides checkout sections entirely');
      check(document.getElementById('cart-items-list').textContent.includes('Your Cart is Empty'), 'Empty cart shows friendly title');
      check(document.getElementById('cart-items-list').textContent.includes('Browse Products'), 'Empty cart shows Browse Products button');

      // Test dynamic addToCart functionality
      window.cartItems = [];
      window.cart = [];
      addToCart('p1', 'Aashirvaad Shudh Chakki Atta', 215.00);
      check(window.cart.length === 1, 'addToCart successfully pushes item to global cart array');
      check(window.cart[0].id === 'p1', 'addToCart preserves product ID');
      const badge = document.getElementById('nav-cart-badge');
      check(badge && badge.textContent === '1', 'Cart badge updates dynamically on addToCart');
      
      // Add another item
      addToCart('p2', 'Kachchi Ghani Mustard Oil', 145.00);
      check(window.cart.length === 2, 'addToCart adds second item to global cart');
      check(badge && badge.textContent === '2', 'Cart badge updates to 2');
      renderCartItems();
      check(chkSections && !chkSections.classList.contains('hidden'), 'Cart with items shows checkout sections');
      check(document.getElementById('checkout-selected-address-card') !== null, 'Compact deliver-to address card present');

      const upiRadio = document.querySelector('input[name="payment_mode"][value="ONLINE"]');
      const codRadio = document.querySelector('input[name="payment_mode"][value="COD"]');
      check(codRadio && codRadio.checked, 'COD is selected by default');
      const codFeeInitial = document.getElementById('bill-cod-fee');
      check(codFeeInitial && codFeeInitial.textContent.includes('10'), 'COD fee row shows +₹10 convenience fee');
      
      // Test dynamic UPI fee logic
      selectPaymentMode('ONLINE');
      const upiFee = document.getElementById('bill-cod-fee');
      check(upiFee && upiFee.textContent.includes('0.00'), 'Selecting UPI removes COD fee to ₹0.00 discount');
      
      // Re-select COD
      selectPaymentMode('COD');
      check(codRadio.checked, 'Re-selecting COD restores COD payment mode');

      // 11. AI Support: Verify Call Me and Request Callback removed
      const allButtons = Array.from(document.querySelectorAll('button')).map(b => b.textContent.trim());
      check(!allButtons.some(t => t === 'Call Me'), 'Call Me button completely removed from DOM');
      check(!allButtons.some(t => t === 'Request Callback'), 'Request Callback button completely removed from DOM');

      // 12. Photo Evidence Upload elements in Issue Modal
      openIssueModal('GB-TEST-9901', 'DAMAGED_ITEM');
      check(!document.getElementById('modal-raise-ticket').classList.contains('hidden'), 'Issue report modal opened');
      check(document.getElementById('ticket-photo-upload-section') !== null, 'Product photo upload section exists');
      check(document.getElementById('ticket-evidence-file') !== null, 'File upload input exists');
      check(document.getElementById('ticket-photo-preview-card') !== null, 'Photo preview card exists');
      closeModal('modal-raise-ticket');

      // 13. Image Verification in Catalog & DOM Cache-Busting
      const firstCardImg = document.querySelector('.product-card img');
      check(firstCardImg && firstCardImg.src.includes('v='), 'Product card image DOM element has dynamic cache-busting timestamp: ' + (firstCardImg ? firstCardImg.src : 'null'));
      const attaImg = getProductImage('Aashirvaad Shudh Chakki Atta');
      check(attaImg.includes('1509440159596') && attaImg.includes('v='), 'getProductImage returns verified URL with cache buster: ' + attaImg);
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

      // 14. Final switch back to Home and scroll lock check
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

async def take_screenshots_suite(ws):
    print("\n--- Capturing Verified Visual Screenshots for Artifacts ---")

    async def evaluate(expr):
        await ws.send(json.dumps({
            "id": 50,
            "method": "Runtime.evaluate",
            "params": {"expression": expr, "awaitPromise": True, "returnByValue": True}
        }))
        while True:
            resp = json.loads(await ws.recv())
            if resp.get("id") == 50:
                return resp.get("result", {}).get("value")

    # 1. Clean Empty Cart
    await evaluate("""
    window.cartItems = [];
    switchTab('cart');
    renderCartItems();
    """)
    await asyncio.sleep(0.4)
    await capture_screenshot(ws, "proof_final_01_clean_empty_cart.png")

    # 2. Cart with Products & Simplified Checkout
    await evaluate("""
    window.cartItems = [
        { id: 'p1', nameEn: 'Aashirvaad Shudh Chakki Atta', price: 215.00, qty: 1, unit: '5 kg', img: getProductImage('p1') },
        { id: 'p2', nameEn: 'Kachchi Ghani Mustard Oil', price: 145.00, qty: 1, unit: '1 Litre', img: getProductImage('p2') }
    ];
    renderCartItems();
    """)
    await asyncio.sleep(0.4)
    await capture_screenshot(ws, "proof_final_02_cart_with_products_simplified_checkout.png")

    # 3. Location Map Picker with 4 Distance Bands & Friendly Address
    await evaluate("""
    openLocationMapPickerModal();
    updatePickerGeofence(26.2315, 85.3610);
    """)
    await asyncio.sleep(0.6)
    await capture_screenshot(ws, "proof_final_03_readable_location_map_picker.png")

    # 4. Map Geofence Boundary Check (Out of Range)
    await evaluate("""
    updatePickerGeofence(26.4500, 85.7000);
    """)
    await asyncio.sleep(0.4)
    await capture_screenshot(ws, "proof_final_04_map_out_of_range_warning.png")
    await evaluate("closeModal('modal-location-map-picker');")

    # 5. Compact Saved Addresses Preview on Account Screen
    await evaluate("""
    switchTab('account');
    renderAccountAddressSummary();
    """)
    await asyncio.sleep(0.4)
    await capture_screenshot(ws, "proof_final_05_compact_saved_addresses_account.png")

    # 6. Manage Addresses Subview Modal
    await evaluate("""
    openManageAddressesModal();
    renderManageAddressesList();
    """)
    await asyncio.sleep(0.4)
    await capture_screenshot(ws, "proof_final_06_manage_addresses_modal.png")
    await evaluate("closeModal('modal-manage-addresses');")

    # 7. Natural AI Support Chat (Zero Callback Buttons)
    await evaluate("""
    openAiSupportChatModal();
    """)
    await asyncio.sleep(0.4)
    await capture_screenshot(ws, "proof_final_07_natural_ai_support_no_callback.png")

    # 8. Damaged Product Photo Evidence Upload Modal
    await evaluate("""
    closeModal('modal-ai-support-chat');
    openIssueModal('GB-TEST-7108', 'DAMAGED_ITEM');
    """)
    await asyncio.sleep(0.4)
    await capture_screenshot(ws, "proof_final_08_photo_evidence_upload_modal.png")

    # 9. Monthly Ration List
    await evaluate("""
    closeModal('modal-raise-ticket');
    switchTab('orders');
    openMonthlyRationModal();
    """)
    await asyncio.sleep(0.5)
    await capture_screenshot(ws, "proof_final_09_monthly_ration_list.png")

    # 10. Monthly Ration Direct Order Review with 4 Bands
    await evaluate("""
    proceedToMonthlyRationOrderReview();
    """)
    await asyncio.sleep(0.5)
    await capture_screenshot(ws, "proof_final_10_monthly_ration_direct_order_review.png")
    await evaluate("""
    closeModal('modal-ration-order-review');
    closeModal('modal-monthly-ration');
    """)

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

            # Take full screenshots in 393px viewport
            await ws.send(json.dumps({
                "id": 10,
                "method": "Emulation.setDeviceMetricsOverride",
                "params": {"width": 393, "height": 852, "deviceScaleFactor": 2.0, "mobile": True}
            }))
            await ws.recv()
            await take_screenshots_suite(ws)

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
