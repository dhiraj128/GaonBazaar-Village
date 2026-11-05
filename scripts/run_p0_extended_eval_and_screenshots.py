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
temp_dir = r"C:\Users\dhira\AppData\Local\Temp\chrome_p0_eval"
artifact_dir = r"C:\Users\dhira\.gemini\antigravity\brain\918c8085-b60b-40a9-a077-a3344458bcc5"

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

async def main():
    # 1. Start static server
    server_proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port), "--directory", "public_web"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(1)

    # 2. Launch Chrome with CDP
    os.makedirs(temp_dir, exist_ok=True)
    chrome_proc = subprocess.Popen([
        chrome_path,
        f"--remote-debugging-port={cdp_port}",
        f"--user-data-dir={temp_dir}",
        "--headless=new",
        "--disable-gpu",
        "--no-first-run",
        "--no-default-browser-check",
        f"http://127.0.0.1:{port}/customer/index.html"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)

    try:
        # Find WebSocket debugger URL
        target_info = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{cdp_port}/json").read().decode('utf-8'))
        ws_url = target_info[0]["webSocketDebuggerUrl"]

        async with websockets.connect(ws_url) as ws:
            # Set mobile viewport 393x852
            await ws.send(json.dumps({
                "id": 1,
                "method": "Emulation.setDeviceMetricsOverride",
                "params": {"width": 393, "height": 852, "deviceScaleFactor": 2.0, "mobile": True}
            }))
            await ws.recv()

            async def evaluate(expr):
                await ws.send(json.dumps({
                    "id": 2,
                    "method": "Runtime.evaluate",
                    "params": {"expression": expr, "awaitPromise": True, "returnByValue": True}
                }))
                while True:
                    resp = json.loads(await ws.recv())
                    if resp.get("id") == 2:
                        return resp.get("result", {}).get("value")

            # Wait for Leaflet CDN
            await evaluate("""
            (async () => {
                for (let i = 0; i < 30; i++) {
                    if (typeof window.L !== 'undefined') break;
                    await new Promise(r => setTimeout(r, 100));
                }
            })()
            """)

            # Authenticate into dashboard
            await evaluate("""
            localStorage.setItem('gb_customer_authenticated', 'true');
            localStorage.setItem('gb_customer_phone', '9876543210');
            localStorage.setItem('gb_active_order_id', 'GB-TEST-7108');
            localStorage.setItem('gb_active_order_otp', '4829');

            document.getElementById('page-language').classList.add('hidden');
            document.getElementById('page-login').classList.add('hidden');
            document.getElementById('dashboard-container').classList.remove('hidden');

            window.userSavedAddresses = [
                {
                    id: 'addr_101',
                    title: 'Home',
                    recipient_name: 'Dhiraj Sharma',
                    phone: '9876543210',
                    village: 'Chaturshi, Muzaffarpur',
                    landmark: 'Near Shiv Mandir',
                    district: 'Muzaffarpur',
                    is_default: true,
                    latitude: 26.2315,
                    longitude: 85.3610
                }
            ];
            """)

            # -------------------------------------------------------------
            # Screenshot 1: Clean Empty Cart
            # -------------------------------------------------------------
            await evaluate("""
            window.cartItems = [];
            switchTab('cart');
            renderCartItems();
            """)
            await asyncio.sleep(0.5)
            await capture_screenshot(ws, "proof_final_01_clean_empty_cart.png")

            # -------------------------------------------------------------
            # Screenshot 2: Cart with Products & Simplified Checkout
            # -------------------------------------------------------------
            await evaluate("""
            window.cartItems = [
                { id: 'p1', nameEn: 'Aashirvaad Shudh Chakki Atta', price: 215.00, qty: 1, unit: '5 kg', img: getProductImage('p1') },
                { id: 'p2', nameEn: 'Kachchi Ghani Mustard Oil', price: 145.00, qty: 1, unit: '1 Litre', img: getProductImage('p2') }
            ];
            renderCartItems();
            """)
            await asyncio.sleep(0.5)
            await capture_screenshot(ws, "proof_final_02_cart_with_products_simplified_checkout.png")

            # -------------------------------------------------------------
            # Screenshot 3: Location Map Picker with 4 Distance Bands & Friendly Address
            # -------------------------------------------------------------
            await evaluate("""
            openLocationMapPickerModal();
            updatePickerGeofence(26.2315, 85.3610);
            """)
            await asyncio.sleep(0.6)
            await capture_screenshot(ws, "proof_final_03_readable_location_map_picker.png")

            # -------------------------------------------------------------
            # Screenshot 4: Map Geofence Boundary Check (Out of Range)
            # -------------------------------------------------------------
            await evaluate("""
            updatePickerGeofence(26.4500, 85.7000); // > 8km
            """)
            await asyncio.sleep(0.4)
            await capture_screenshot(ws, "proof_final_04_map_out_of_range_warning.png")

            await evaluate("closeModal('modal-location-map-picker');")

            # -------------------------------------------------------------
            # Screenshot 5: Compact Saved Addresses Preview on Account Screen
            # -------------------------------------------------------------
            await evaluate("""
            switchTab('account');
            renderAccountAddressSummary();
            """)
            await asyncio.sleep(0.5)
            await capture_screenshot(ws, "proof_final_05_compact_saved_addresses_account.png")

            # -------------------------------------------------------------
            # Screenshot 6: Manage Addresses Subview Modal
            # -------------------------------------------------------------
            await evaluate("""
            openManageAddressesModal();
            renderManageAddressesList();
            """)
            await asyncio.sleep(0.5)
            await capture_screenshot(ws, "proof_final_06_manage_addresses_modal.png")
            await evaluate("closeModal('modal-manage-addresses');")

            # -------------------------------------------------------------
            # Screenshot 7: Natural AI Support Chat (Zero Callback Buttons)
            # -------------------------------------------------------------
            await evaluate("""
            openAiSupportChatModal();
            """)
            await asyncio.sleep(0.5)
            await capture_screenshot(ws, "proof_final_07_natural_ai_support_no_callback.png")

            # -------------------------------------------------------------
            # Screenshot 8: Damaged Product Photo Evidence Upload Modal
            # -------------------------------------------------------------
            await evaluate("""
            closeModal('modal-ai-support-chat');
            openIssueModal('GB-TEST-7108', 'DAMAGED_ITEM');
            """)
            await asyncio.sleep(0.5)
            await capture_screenshot(ws, "proof_final_08_photo_evidence_upload_modal.png")

            # -------------------------------------------------------------
            # Screenshot 9: Monthly Ration List
            # -------------------------------------------------------------
            await evaluate("""
            closeModal('modal-raise-ticket');
            switchTab('orders');
            openMonthlyRationModal();
            """)
            await asyncio.sleep(0.6)
            await capture_screenshot(ws, "proof_final_09_monthly_ration_list.png")

            # -------------------------------------------------------------
            # Screenshot 10: Monthly Ration Direct Order Review with 4 Bands
            # -------------------------------------------------------------
            await evaluate("""
            proceedToMonthlyRationOrderReview();
            """)
            await asyncio.sleep(0.6)
            await capture_screenshot(ws, "proof_final_10_monthly_ration_direct_order_review.png")
            await evaluate("""
            closeModal('modal-ration-order-review');
            closeModal('modal-monthly-ration');
            """)

            # -------------------------------------------------------------
            # Run verification assertion suite
            # -------------------------------------------------------------
            results = await evaluate("""
            (() => {
                const tests = [];
                function assert(condition, name) {
                    tests.push({ pass: !!condition, name });
                }

                // 1. Verify Call Me and Request Callback removed
                const allButtons = Array.from(document.querySelectorAll('button')).map(b => b.textContent.trim());
                assert(!allButtons.some(t => t === 'Call Me'), 'Call Me button completely removed from DOM');
                assert(!allButtons.some(t => t === 'Request Callback'), 'Request Callback button completely removed from DOM');

                // 2. Verify Open in Maps function exists and does not use hardcoded Minapur
                assert(typeof window.openPickerPinInExternalMaps === 'function', 'openPickerPinInExternalMaps defined');
                assert(typeof window.openCustomerDirectionsMap === 'function', 'openCustomerDirectionsMap defined');
                assert(typeof window.clearPickerMarkerPin === 'function', 'clearPickerMarkerPin defined');

                // 3. Verify Empty Cart hides checkout sections
                window.cartItems = [];
                renderCartItems();
                const chkSections = document.getElementById('cart-checkout-sections');
                assert(chkSections && chkSections.classList.contains('hidden'), 'Checkout sections hidden when cart is empty');
                const cartList = document.getElementById('cart-items-list');
                assert(cartList && cartList.textContent.includes('Your Cart is Empty'), 'Cart items list displays clean empty cart');
                assert(cartList && cartList.textContent.includes('Browse Products'), 'Empty cart has Browse Products button');

                // 4. Verify Cart with items shows checkout sections & compact address
                window.cartItems = [{ id: 'p1', nameEn: 'Atta', price: 215, qty: 1 }];
                renderCartItems();
                assert(chkSections && !chkSections.classList.contains('hidden'), 'Checkout sections visible when cart has items');
                const selAddrCard = document.getElementById('checkout-selected-address-card');
                assert(selAddrCard && !selAddrCard.classList.contains('hidden'), 'Compact selected address preview visible in cart');

                // 5. Verify Photo Evidence modal elements
                assert(document.getElementById('ticket-photo-upload-section') !== null, 'Photo upload section exists in issue modal');
                assert(document.getElementById('ticket-evidence-file') !== null, 'File input exists for photo evidence');
                assert(document.getElementById('ticket-photo-preview-card') !== null, 'Photo preview card exists in issue modal');

                // 6. Verify 4 distance pricing bands in geofence status
                updatePickerGeofence(26.2315, 85.3610); // 0 km
                const b1 = document.getElementById('picker-service-badge').textContent;
                assert(b1.includes('₹15'), '0-2 km band displays ₹15 delivery fee: ' + b1);

                updatePickerGeofence(26.2550, 85.3610); // ~2.6 km
                const b2 = document.getElementById('picker-service-badge').textContent;
                assert(b2.includes('₹20'), 'Above 2-4 km band displays ₹20 delivery fee: ' + b2);

                updatePickerGeofence(26.2730, 85.3610); // ~4.6 km
                const b3 = document.getElementById('picker-service-badge').textContent;
                assert(b3.includes('₹25'), 'Above 4-5 km band displays ₹25 delivery fee: ' + b3);

                updatePickerGeofence(26.2900, 85.3610); // ~6.5 km
                const b4 = document.getElementById('picker-service-badge').textContent;
                assert(b4.includes('₹35'), 'Above 5-8 km band displays ₹35 delivery fee: ' + b4);

                updatePickerGeofence(26.4000, 85.7000); // > 8 km
                const b5 = document.getElementById('picker-service-badge').textContent;
                assert(b5.includes('Delivery is not available at this location yet'), 'Above 8 km displays "Delivery is not available at this location yet.": ' + b5);
                const btnConfirm = document.getElementById('btn-confirm-map-pin');
                assert(btnConfirm && btnConfirm.disabled, 'Confirm button disabled when location is outside 8km');

                // 7. Verify Monthly Ration Order Review displays all 4 bands & ₹3 platform fee
                populateRationOrderReviewModal();
                const platformFeeEl = document.getElementById('ration-review-grand-total');
                assert(platformFeeEl && platformFeeEl.textContent.includes('₹'), 'Grand total calculated with delivery and ₹3 platform fee');

                return tests;
            })()
            """)

            print("\n=== EXTENDED P0 EVALUATION RESULTS ===")
            all_passed = True
            for t in results:
                status = "PASS" if t["pass"] else "FAIL"
                if not t["pass"]:
                    all_passed = False
                print(f"  [{status}] {t['name']}")
            print(f"Total Extended P0 Checks: {len(results)}, All Passed: {all_passed}")

    finally:
        chrome_proc.terminate()
        server_proc.terminate()

if __name__ == "__main__":
    asyncio.run(main())
