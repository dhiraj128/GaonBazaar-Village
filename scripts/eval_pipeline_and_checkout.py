import asyncio
import os
import sys
import json
import time
import subprocess
import urllib.request
import base64
import socket
import websockets

sys.stdout.reconfigure(encoding='utf-8')

ARTIFACT_DIR = r"C:\Users\dhira\OneDrive\Desktop\GaoBazar-Village"
BRAIN_DIR = r"C:\Users\dhira\.gemini\antigravity\brain\918c8085-b60b-40a9-a077-a3344458bcc5"
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
TEMP_DIR = r"C:\Users\dhira\AppData\Local\Temp\chrome_pipeline_eval"

def get_free_port():
    s = socket.socket()
    s.bind(('127.0.0.1', 0))
    port = s.getsockname()[1]
    s.close()
    return port

async def send_cdp(ws, method, params=None, msg_id=1):
    payload = {"id": msg_id, "method": method, "params": params or {}}
    await ws.send(json.dumps(payload))
    while True:
        resp = json.loads(await ws.recv())
        if resp.get("id") == msg_id:
            return resp

async def evaluate(ws, expr, msg_id=200):
    res = await send_cdp(ws, "Runtime.evaluate", {"expression": expr, "returnByValue": True, "awaitPromise": True}, msg_id=msg_id)
    if "exceptionDetails" in res.get("result", {}):
        print("JS EXCEPTION:", res["result"]["exceptionDetails"])
    return res.get("result", {}).get("result", {}).get("value")

async def take_screenshot(ws, filename, msg_id=100):
    res = await send_cdp(ws, "Page.captureScreenshot", {"format": "png"}, msg_id=msg_id)
    b64 = res["result"]["data"]
    for folder in [ARTIFACT_DIR, BRAIN_DIR]:
        os.makedirs(folder, exist_ok=True)
        out_path = os.path.join(folder, filename)
        with open(out_path, "wb") as f:
            f.write(base64.b64decode(b64))
    print(f"  [PROOF CAPTURED] {filename}")
    return filename

async def run_evaluation():
    http_port = get_free_port()
    cdp_port = get_free_port()

    # 1. Start HTTP Server for public_web
    http_proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(http_port), "--directory", "public_web"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(1)

    # 2. Launch Chrome Headless
    chrome_proc = subprocess.Popen([
        CHROME_PATH,
        "--headless=new",
        f"--remote-debugging-port={cdp_port}",
        f"--user-data-dir={TEMP_DIR}",
        "--disable-gpu",
        "--no-sandbox",
        "--window-size=412,915",  # Mobile Viewport
        f"http://127.0.0.1:{http_port}/customer/index.html"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)

    try:
        # Get CDP websocket URL
        targets_raw = urllib.request.urlopen(f"http://127.0.0.1:{cdp_port}/json").read()
        targets = json.loads(targets_raw.decode('utf-8'))
        page_target = next(t for t in targets if t.get("type") == "page" and f"{http_port}" in t.get("url", ""))
        ws_url = page_target["webSocketDebuggerUrl"]

        async with websockets.connect(ws_url, max_size=20*1024*1024) as ws:
            await send_cdp(ws, "Page.enable")
            await send_cdp(ws, "DOM.enable")
            await send_cdp(ws, "Emulation.setDeviceMetricsOverride", {
                "width": 412,
                "height": 915,
                "deviceScaleFactor": 2.5,
                "mobile": True
            })

            print("\n=======================================================")
            print("TEST 1: CUSTOMER APP CHECKOUT PAYMENT MODAL (PART A)")
            print("=======================================================")
            
            # Setup cart with items & mock address
            await evaluate(ws, """
                (() => {
                    cartItems = [
                        { id: 'prod_1', name: 'Aashirvaad Atta 5kg', price: 210, quantity: 1, storeId: 'str_01' },
                        { id: 'prod_2', name: 'Amul Taaza Milk 1L', price: 54, quantity: 2, storeId: 'str_01' }
                    ];
                    updateCartBadge();
                    renderCartItems();
                    selectedCheckoutAddressId = 'addr_test_1';
                    userSavedAddresses = [{ id: 'addr_test_1', title: 'Home', village: 'Chaturshi', landmark: 'Near Shiv Mandir' }];
                    window.isLocationServiceable = true;
                    switchTab('cart');
                })()
            """)
            await asyncio.sleep(1)

            # Click place order to trigger modal
            await evaluate(ws, """
                (() => {
                    const btn = document.getElementById('btn-place-order');
                    if (btn) btn.click();
                })()
            """)
            await asyncio.sleep(1)

            # Check modal state
            modal_visible = await evaluate(ws, """
                (() => {
                    const m = document.getElementById('modal-checkout-payment');
                    return m && !m.classList.contains('hidden');
                })()
            """)
            print(f"Checkout Payment Bottom Sheet visible: {modal_visible}")
            assert modal_visible, "Modal checkout payment did NOT open!"

            # Check UPI and COD options
            upi_exists = await evaluate(ws, "Boolean(document.getElementById('checkout-opt-upi'))")
            cod_exists = await evaluate(ws, "Boolean(document.getElementById('checkout-opt-cod'))")
            print(f"UPI option exists: {upi_exists}, COD option exists: {cod_exists}")
            assert upi_exists and cod_exists, "Payment options missing!"

            # Capture bottom sheet screenshot proof
            await take_screenshot(ws, "proof_customer_checkout_payment_bottom_sheet.png", 101)

            # Toggle COD and check fee
            await evaluate(ws, "selectCheckoutModalPayment('COD')")
            await asyncio.sleep(0.5)
            cod_text = await evaluate(ws, "document.getElementById('btn-checkout-modal-text')?.innerText")
            print(f"COD Button Text: {cod_text}")
            assert "COD" in cod_text, "COD text not rendered on button!"

            # Toggle back to UPI
            await evaluate(ws, "selectCheckoutModalPayment('ONLINE')")
            await asyncio.sleep(0.5)
            upi_text = await evaluate(ws, "document.getElementById('btn-checkout-modal-text')?.innerText")
            print(f"UPI Button Text: {upi_text}")
            assert "UPI" in upi_text, "UPI text not rendered on button!"

            # Complete checkout via UPI
            await evaluate(ws, """
                (async () => {
                    await confirmPaymentAndPlaceOrder();
                })()
            """)
            await asyncio.sleep(2)

            orders_active = await evaluate(ws, """
                (() => {
                    const ordersTab = document.getElementById('view-orders');
                    return ordersTab && !ordersTab.classList.contains('hidden');
                })()
            """)
            print(f"Switched to Orders tab after UPI checkout: {orders_active}")
            assert orders_active, "Did not switch to orders tab after checkout!"
            await take_screenshot(ws, "proof_customer_order_placed_upi.png", 102)

            print("\n=======================================================")
            print("TEST 2: RUNNER APP ONBOARDING PIPELINE & PENNY DROP")
            print("=======================================================")
            
            # Navigate to runner app
            await send_cdp(ws, "Page.navigate", {"url": f"http://127.0.0.1:{http_port}/runner/index.html"})
            await asyncio.sleep(1.5)

            # Step 1 -> Language
            await evaluate(ws, "navigateTo('onboarding-2')")
            await asyncio.sleep(0.5)

            # Step 2 -> Mobile OTP -> Step 3
            await evaluate(ws, "navigateTo('onboarding-3')")
            await asyncio.sleep(0.5)

            # Step 3 verification: ONLY Vehicle Type and Vehicle Registration Number
            has_fullname = await evaluate(ws, "Boolean(document.getElementById('runner-fullname'))")
            has_emergency = await evaluate(ws, "Boolean(document.getElementById('runner-emergency'))")
            has_vehicletype = await evaluate(ws, "Boolean(document.getElementById('runner-vehicletype'))")
            has_vehicleno = await evaluate(ws, "Boolean(document.getElementById('runner-vehicleno'))")

            print(f"Runner Step 3 - Full Name present: {has_fullname} (must be False)")
            print(f"Runner Step 3 - Emergency present: {has_emergency} (must be False)")
            print(f"Runner Step 3 - Vehicle Type present: {has_vehicletype} (must be True)")
            print(f"Runner Step 3 - Vehicle Reg No present: {has_vehicleno} (must be True)")
            assert not has_fullname and not has_emergency, "Step 3 contains prohibited fields!"
            assert has_vehicletype and has_vehicleno, "Step 3 missing required vehicle fields!"
            await take_screenshot(ws, "proof_runner_step3_cleaned_fields.png", 201)

            # Step 3 -> Click Continue -> Transitions to Step 4 (Location Setup)
            await evaluate(ws, "saveRunnerDetailsAndProceed()")
            await asyncio.sleep(0.8)

            current_screen = await evaluate(ws, "state.currentScreen")
            print(f"Screen after Step 3: {current_screen}")
            assert current_screen == "onboarding-4", f"Expected onboarding-4, got {current_screen}"

            # Step 4 verification: Location Setup (Delivery Radius & Hub)
            step4_heading = await evaluate(ws, "document.querySelector('#screen-onboarding-4 h2')?.innerText")
            print(f"Step 4 Heading: {step4_heading}")
            assert "Delivery Radius" in step4_heading, "Step 4 is NOT Location Setup!"
            await take_screenshot(ws, "proof_runner_step4_location_radius.png", 202)

            # Step 4 -> Click "Save & Continue to KYC" -> Transitions to Step 5 (Paperless KYC)
            await evaluate(ws, "saveRunnerLocationAndProceed()")
            await asyncio.sleep(0.8)

            current_screen = await evaluate(ws, "state.currentScreen")
            print(f"Screen after Step 4: {current_screen}")
            assert current_screen == "onboarding-5", f"Expected onboarding-5, got {current_screen}"

            # Step 5 verification: Paperless KYC (Single ID selection)
            step5_heading = await evaluate(ws, "document.querySelector('#screen-onboarding-5 h2')?.innerText")
            print(f"Step 5 Heading: {step5_heading}")
            assert "Identity Verification" in step5_heading, "Step 5 is NOT KYC!"
            await take_screenshot(ws, "proof_runner_step5_paperless_kyc.png", 203)

            # Verify PAN and continue
            await evaluate(ws, """
                (() => {
                    document.getElementById('kyc-pan-input').value = 'ABCDE1234F';
                    submitPanVerification();
                })()
            """)
            await asyncio.sleep(1)

            # Click Continue to Payout Setup -> Transitions to Step 6
            await evaluate(ws, "proceedToNextStep()")
            await asyncio.sleep(0.8)

            current_screen = await evaluate(ws, "state.currentScreen")
            print(f"Screen after Step 5: {current_screen}")
            assert current_screen == "onboarding-6", f"Expected onboarding-6, got {current_screen}"

            # Step 6 verification: Payout Setup
            step6_heading = await evaluate(ws, "document.querySelector('#screen-onboarding-6 h2')?.innerText")
            print(f"Step 6 Heading: {step6_heading}")
            assert "Bank / UPI" in step6_heading, "Step 6 is NOT Payout Setup!"
            await take_screenshot(ws, "proof_runner_step6_penny_drop.png", 204)

            # Submit Payout Details (₹1 Penny Drop)
            await evaluate(ws, """
                (() => {
                    document.getElementById('upi-vpa').value = 'runner.verma@upi';
                    submitPayoutDetails('upi');
                })()
            """)
            await asyncio.sleep(2)

            # Step 7 verification: Application Under Review
            current_screen = await evaluate(ws, "state.currentScreen")
            print(f"Screen after Step 6: {current_screen}")
            assert current_screen == "onboarding-7", f"Expected onboarding-7, got {current_screen}"

            review_sub = await evaluate(ws, "document.querySelector('#screen-onboarding-7 p')?.innerText")
            print(f"Step 7 Subtext: {review_sub}")
            assert "Your documents and bank details are under review." in review_sub or "आपके दस्तावेज़ और बैंक विवरण समीक्षाधीन हैं।" in review_sub, "Under review text mismatch!"
            await take_screenshot(ws, "proof_runner_step7_under_review.png", 205)

            print("\n=======================================================")
            print("TEST 3: VENDOR APP ONBOARDING PIPELINE & PENNY DROP")
            print("=======================================================")

            # Navigate to vendor app
            await send_cdp(ws, "Page.navigate", {"url": f"http://127.0.0.1:{http_port}/vendor/index.html"})
            await asyncio.sleep(1.5)

            # Step 1 -> Language -> Step 2 -> Step 3
            await evaluate(ws, "navigateTo('onboarding-3')")
            await asyncio.sleep(0.5)

            # Step 3 verification: ONLY Shop Name and Shop Category
            v_fullname = await evaluate(ws, "Boolean(document.getElementById('vendor-fullname'))")
            v_emergency = await evaluate(ws, "Boolean(document.getElementById('vendor-emergency'))")
            v_shopname = await evaluate(ws, "Boolean(document.getElementById('vendor-shopname'))")
            v_category = await evaluate(ws, "Boolean(document.getElementById('vendor-category'))")

            print(f"Vendor Step 3 - Full Name present: {v_fullname} (must be False)")
            print(f"Vendor Step 3 - Emergency present: {v_emergency} (must be False)")
            print(f"Vendor Step 3 - Shop Name present: {v_shopname} (must be True)")
            print(f"Vendor Step 3 - Category present: {v_category} (must be True)")
            assert not v_fullname and not v_emergency, "Vendor Step 3 contains prohibited fields!"
            assert v_shopname and v_category, "Vendor Step 3 missing required shop fields!"
            await take_screenshot(ws, "proof_vendor_step3_cleaned_fields.png", 301)

            # Step 3 -> Click Continue -> Transitions to Step 4 (Shop Location Setup)
            await evaluate(ws, "saveBasicDetailsAndProceed()")
            await asyncio.sleep(0.8)

            current_screen = await evaluate(ws, "state.currentScreen")
            print(f"Vendor screen after Step 3: {current_screen}")
            assert current_screen == "onboarding-4", f"Expected onboarding-4, got {current_screen}"

            step4_v_heading = await evaluate(ws, "document.querySelector('#screen-onboarding-4 h2')?.innerText")
            print(f"Vendor Step 4 Heading: {step4_v_heading}")
            assert "Shop Location" in step4_v_heading, "Vendor Step 4 is NOT Location Setup!"
            await take_screenshot(ws, "proof_vendor_step4_shop_location.png", 302)

            # Step 4 -> Click "Save & Continue to KYC" -> Transitions to Step 5 (Paperless KYC)
            await evaluate(ws, "saveVendorLocationAndProceed()")
            await asyncio.sleep(0.8)

            current_screen = await evaluate(ws, "state.currentScreen")
            print(f"Vendor screen after Step 4: {current_screen}")
            assert current_screen == "onboarding-5", f"Expected onboarding-5, got {current_screen}"

            step5_v_heading = await evaluate(ws, "document.querySelector('#screen-onboarding-5 h2')?.innerText")
            print(f"Vendor Step 5 Heading: {step5_v_heading}")
            assert "Identity Verification" in step5_v_heading, "Vendor Step 5 is NOT KYC!"
            await take_screenshot(ws, "proof_vendor_step5_paperless_kyc.png", 303)

            # Verify PAN and proceed
            await evaluate(ws, """
                (() => {
                    document.getElementById('kyc-pan-input').value = 'BKZPS9921K';
                    submitPanVerification();
                })()
            """)
            await asyncio.sleep(1)

            # Step 5 -> Click "Continue to Payout Setup" -> Transitions to Step 6 (Payout Setup)
            await evaluate(ws, "proceedToNextStep()")
            await asyncio.sleep(0.8)

            current_screen = await evaluate(ws, "state.currentScreen")
            print(f"Vendor screen after Step 5: {current_screen}")
            assert current_screen == "onboarding-6", f"Expected onboarding-6, got {current_screen}"

            step6_v_heading = await evaluate(ws, "document.querySelector('#screen-onboarding-6 h2')?.innerText")
            print(f"Vendor Step 6 Heading: {step6_v_heading}")
            assert "Bank / UPI" in step6_v_heading, "Vendor Step 6 is NOT Payout Setup!"
            await take_screenshot(ws, "proof_vendor_step6_penny_drop.png", 304)

            # Submit Payout Details (₹1 Penny Drop)
            await evaluate(ws, """
                (() => {
                    document.getElementById('upi-vpa').value = 'sharma.kirana@okaxis';
                    submitPayoutDetails('upi');
                })()
            """)
            await asyncio.sleep(2)

            # Step 7 verification: Application Under Review
            current_screen = await evaluate(ws, "state.currentScreen")
            print(f"Vendor screen after Step 6: {current_screen}")
            assert current_screen == "onboarding-7", f"Expected onboarding-7, got {current_screen}"

            review_sub_v = await evaluate(ws, "document.querySelector('#screen-onboarding-7 p')?.innerText")
            print(f"Vendor Step 7 Subtext: {review_sub_v}")
            assert "Your documents and bank details are under review." in review_sub_v or "आपके दस्तावेज़ और बैंक विवरण समीक्षाधीन हैं।" in review_sub_v, "Vendor under review text mismatch!"
            await take_screenshot(ws, "proof_vendor_step7_under_review.png", 305)

            print("\n ALL PIPELINE & CHECKOUT TESTS PASSED WITH 100% SUCCESS!")

    finally:
        chrome_proc.terminate()
        http_proc.terminate()

if __name__ == "__main__":
    asyncio.run(run_evaluation())
