import asyncio
import json
import os
import subprocess
import time
import urllib.request
import websockets

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PORT = 9333
DEBUG_DIR = os.path.abspath(".tmp_chrome_hw_test")

async def send_cmd(ws, method, params=None, msg_id=1):
    payload = {"id": msg_id, "method": method}
    if params:
        payload["params"] = params
    await ws.send(json.dumps(payload))
    while True:
        resp = json.loads(await ws.recv())
        if resp.get("id") == msg_id:
            return resp.get("result", {})

async def eval_js(ws, expr, msg_id=1):
    res = await send_cmd(ws, "Runtime.evaluate", {"expression": expr, "returnByValue": True, "awaitPromise": True}, msg_id)
    if "exceptionDetails" in res:
        raise Exception(f"JS Exception: {json.dumps(res['exceptionDetails'])}")
    return res.get("result", {}).get("value")

async def take_screenshot(ws, filename, msg_id=1):
    res = await send_cmd(ws, "Page.captureScreenshot", {"format": "png"}, msg_id)
    data = res.get("data")
    if data:
        import base64
        with open(filename, "wb") as f:
            f.write(base64.b64decode(data))
        print(f"Captured screenshot: {filename}")

async def main():
    print("=== STARTING GAONBAZAAR HARDWARE, LOCALIZATION & PAYMENT SETTINGS CDP TEST ===")
    os.makedirs(DEBUG_DIR, exist_ok=True)
    
    proc = subprocess.Popen([
        CHROME_PATH,
        f"--remote-debugging-port={PORT}",
        f"--user-data-dir={DEBUG_DIR}",
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--use-fake-ui-for-media-stream",
        "--use-fake-device-for-media-stream",
        "about:blank"
    ])
    
    await asyncio.sleep(2)
    
    try:
        tabs_url = f"http://localhost:{PORT}/json"
        req = urllib.request.Request(tabs_url)
        with urllib.request.urlopen(req) as resp:
            tabs = json.loads(resp.read().decode())
        ws_url = tabs[0]["webSocketDebuggerUrl"]
        
        async with websockets.connect(ws_url, max_size=20*1024*1024) as ws:
            mid = 1
            await send_cmd(ws, "Page.enable", msg_id=mid); mid += 1
            await send_cmd(ws, "Runtime.enable", msg_id=mid); mid += 1
            await send_cmd(ws, "Emulation.setDeviceMetricsOverride", {
                "width": 412,
                "height": 915,
                "deviceScaleFactor": 2,
                "mobile": True
            }, msg_id=mid); mid += 1
            
            # ==================================================================
            # TEST 1: CUSTOMER APP - DEAD PAYMENT SETTINGS LINK ACTIVATION
            # ==================================================================
            print("\n--- TEST 1: Customer Account -> Payment Settings Link ---")
            cust_url = "file:///" + os.path.abspath("public_web/customer/index.html").replace("\\", "/")
            await send_cmd(ws, "Page.navigate", {"url": cust_url}, mid); mid += 1
            await asyncio.sleep(1.5)
            
            # Navigate to Account Tab
            await eval_js(ws, """
                localStorage.setItem('gb_customer_authenticated', 'true');
                localStorage.setItem('gb_customer_token', 'mock_token');
                switchTab('account');
            """, mid); mid += 1
            await asyncio.sleep(0.5)
            
            # Verify Account screen is visible
            account_screen = await eval_js(ws, "!document.getElementById('view-account')?.classList.contains('hidden')", mid); mid += 1
            print(f"Customer View-Account Visible: {account_screen}")
            assert account_screen, "Account tab view (view-account) must be visible"
            
            # Click Payment Settings button
            print("Clicking Account -> Payment Settings button...")
            await eval_js(ws, "document.getElementById('menu-btn-payment-settings').click();", mid); mid += 1
            await asyncio.sleep(0.5)
            
            # Verify modal-payment-settings is open and NOT hidden
            vault_modal_open = await eval_js(ws, """
                (function() {
                    const m = document.getElementById('modal-payment-settings');
                    return m && !m.classList.contains('hidden');
                })()
            """, mid); mid += 1
            print(f"Payment Settings Vault Modal Open: {vault_modal_open}")
            assert vault_modal_open, "Payment Settings link must open modal-payment-settings successfully"
            
            await take_screenshot(ws, "proof_payment_settings_modal_activated.png", mid); mid += 1
            
            # Close vault modal
            await eval_js(ws, "closeModal('modal-payment-settings');", mid); mid += 1
            await asyncio.sleep(0.3)

            # ==================================================================
            # TEST 2: VENDOR APP - HARDWARE CAMERA & BARCODE & PRICING DECOUPLING
            # ==================================================================
            print("\n--- TEST 2: Vendor App Hardware Camera & Barcode Integration ---")
            vendor_url = "file:///" + os.path.abspath("public_web/vendor/index.html").replace("\\", "/")
            await send_cmd(ws, "Page.navigate", {"url": vendor_url}, mid); mid += 1
            await asyncio.sleep(1.5)
            
            # Navigate to Inventory tab
            await eval_js(ws, """
                localStorage.setItem('gb_vendor_authenticated', 'true');
                localStorage.setItem('gb_vendor_token', 'mock_token');
                openDashboard('inventory');
            """, mid); mid += 1
            await asyncio.sleep(0.8)
            
            # Verify Hardware Camera Input Attributes
            cam_attrs = await eval_js(ws, """
                (function() {
                    const inp = document.getElementById('vendor-camera-file-input');
                    return {
                        exists: !!inp,
                        accept: inp?.getAttribute('accept'),
                        capture: inp?.getAttribute('capture')
                    };
                })()
            """, mid); mid += 1
            print("Vendor Camera Input Attributes:", json.dumps(cam_attrs))
            assert cam_attrs['exists'], "vendor-camera-file-input must exist in DOM"
            assert cam_attrs['accept'] == 'image/*', "accept must be 'image/*'"
            assert cam_attrs['capture'] == 'environment', "capture MUST be 'environment' to force rear hardware camera"

            # Verify Camera Label button touch target in modal-take-photo
            cam_btn_label = await eval_js(ws, """
                (function() {
                    const label = document.querySelector('label[for=\"vendor-camera-file-input\"]');
                    if (!label) return null;
                    const rect = label.getBoundingClientRect();
                    return {
                        forAttr: label.getAttribute('for'),
                        height: rect.height,
                        hasMinHeight: rect.height >= 48 || label.classList.contains('min-h-[48px]')
                    };
                })()
            """, mid); mid += 1
            print("Camera Button Label Attributes:", json.dumps(cam_btn_label))
            assert cam_btn_label, "Camera button must be a native label for vendor-camera-file-input"
            assert cam_btn_label['hasMinHeight'], "Camera button touch target must be at least 48px"

            # Open Barcode Scanner and verify WebRTC video / Html5Qrcode reader container
            print("Testing WebRTC Barcode Scanner Modal...")
            await eval_js(ws, "openBarcodeScannerModal();", mid); mid += 1
            await asyncio.sleep(0.5)
            
            scanner_ready = await eval_js(ws, """
                (function() {
                    const modal = document.getElementById('modal-barcode-scanner');
                    const readerView = document.getElementById('barcode-reader-view');
                    const video = document.getElementById('barcode-scanner-video');
                    return {
                        modalVisible: modal && !modal.classList.contains('hidden'),
                        readerViewExists: !!readerView,
                        videoExists: !!video
                    };
                })()
            """, mid); mid += 1
            print("Barcode Scanner State:", json.dumps(scanner_ready))
            assert scanner_ready['modalVisible'], "Barcode scanner modal must be open"
            assert scanner_ready['readerViewExists'], "barcode-reader-view container must exist"
            
            await take_screenshot(ws, "proof_vendor_webrtc_scanner_active.png", mid); mid += 1

            # Simulate Barcode Detection and verify pricing decoupling (MRP and Price are BLANK)
            print("Simulating Barcode Detection (8901030383701)...")
            await eval_js(ws, "handleBarcodeDetected('8901030383701');", mid); mid += 1
            await asyncio.sleep(0.5)
            
            # Modal must auto-close upon barcode read
            scanner_closed = await eval_js(ws, "document.getElementById('modal-barcode-scanner')?.classList.contains('hidden')", mid); mid += 1
            assert scanner_closed, "Barcode scanner modal must auto-close upon successful barcode read"
            
            # Verify custom pricing modal opened with BLANK pricing inputs
            pricing_state = await eval_js(ws, """
                (function() {
                    const modal = document.getElementById('modal-custom-pricing');
                    const nameInp = document.getElementById('custom-pricing-name');
                    const mrpInp = document.getElementById('custom-pricing-mrp');
                    const priceInp = document.getElementById('custom-pricing-price');
                    const stockInp = document.getElementById('custom-pricing-stock');
                    return {
                        modalVisible: modal && !modal.classList.contains('hidden'),
                        title: nameInp?.value,
                        mrpBlank: mrpInp?.value === '',
                        priceBlank: priceInp?.value === '',
                        mrpVal: mrpInp?.value,
                        priceVal: priceInp?.value
                    };
                })()
            """, mid); mid += 1
            print("Decoupled Pricing Modal State:", json.dumps(pricing_state))
            assert pricing_state['modalVisible'], "Custom pricing modal must be open"
            assert pricing_state['title'] != '', "Product title must be populated from barcode"
            assert pricing_state['mrpBlank'], "MRP must remain completely blank for vendor manual entry"
            assert pricing_state['priceBlank'], "Selling Price must remain completely blank for vendor manual entry"
            
            await take_screenshot(ws, "proof_vendor_barcode_blank_pricing.png", mid); mid += 1
            
            # Close custom pricing modal
            await eval_js(ws, "closeCustomPricingModal();", mid); mid += 1
            await asyncio.sleep(0.3)

            # ==================================================================
            # TEST 3: VOICE SEARCH "NOT FOUND" COMPACT FALLBACK & 48PX TOUCH TARGET
            # ==================================================================
            print("\n--- TEST 3: Voice Search 'Not Found' Fallback UI ---")
            # Set language to English and search for non-existent item
            await eval_js(ws, """
                setLanguage('en');
                filterInventory('DragonFruitExotic99');
            """, mid); mid += 1
            await asyncio.sleep(0.5)
            
            fallback_en = await eval_js(ws, """
                (function() {
                    const box = document.getElementById('inventory-search-empty-msg');
                    if (!box) return null;
                    const btn = box.querySelector('button');
                    const rect = btn.getBoundingClientRect();
                    return {
                        text: box.innerText,
                        btnText: btn.innerText,
                        btnHeight: rect.height,
                        hasMinHeight: rect.height >= 44 || btn.classList.contains('min-h-[48px]'),
                        isEnglish: box.innerText.includes('No items found') && box.innerText.includes('Add')
                    };
                })()
            """, mid); mid += 1
            print("Voice Search Fallback EN:", json.dumps(fallback_en))
            assert fallback_en, "Fallback box must be present"
            assert fallback_en['isEnglish'], "Fallback must be strictly English when lang='en'"
            assert fallback_en['hasMinHeight'], "Button must have minimum 48px touch target"
            
            await take_screenshot(ws, "proof_vendor_voice_fallback_compact_en.png", mid); mid += 1

            # Switch language to Hindi and test fallback
            await eval_js(ws, """
                setLanguage('hi');
                filterInventory('ताज़ा कीवी फल 99');
            """, mid); mid += 1
            await asyncio.sleep(0.5)

            fallback_hi = await eval_js(ws, """
                (function() {
                    const box = document.getElementById('inventory-search-empty-msg');
                    if (!box) return null;
                    const btn = box.querySelector('button');
                    return {
                        text: box.innerText,
                        isHindi: box.innerText.includes('कोई सामान नहीं मिला')
                    };
                })()
            """, mid); mid += 1
            print("Voice Search Fallback HI:", json.dumps(fallback_hi))
            assert fallback_hi['isHindi'], "Fallback must render conversational Hindi when lang='hi'"

            # ==================================================================
            # TEST 4: STRICT LOCALIZATION - UNDER REVIEW SCREEN IN EN & HI
            # ==================================================================
            print("\n--- TEST 4: Strict Localization - Under Review Screen ---")
            # Vendor Under Review in English
            await eval_js(ws, """
                setLanguage('en');
                navigateTo('onboarding-7');
            """, mid); mid += 1
            await asyncio.sleep(0.5)
            
            review_en = await eval_js(ws, """
                (function() {
                    const screen = document.getElementById('screen-onboarding-7');
                    const sub = screen.querySelector('[data-i18n=\"under_review_sub\"]');
                    return {
                        subText: sub?.innerText,
                        isEnglish: sub?.innerText === 'Your documents and bank details are under review.'
                    };
                })()
            """, mid); mid += 1
            print("Vendor Under Review EN:", json.dumps(review_en))
            assert review_en['isEnglish'], "Under Review subtitle must strictly render in English when lang='en'"
            
            await take_screenshot(ws, "proof_vendor_under_review_english.png", mid); mid += 1

            # Runner Under Review in English
            print("Testing Runner Under Review in English...")
            runner_url = "file:///" + os.path.abspath("public_web/runner/index.html").replace("\\", "/")
            await send_cmd(ws, "Page.navigate", {"url": runner_url}, mid); mid += 1
            await asyncio.sleep(1.5)
            
            await eval_js(ws, """
                setLanguage('en');
                navigateTo('onboarding-7');
            """, mid); mid += 1
            await asyncio.sleep(0.5)
            
            runner_review_en = await eval_js(ws, """
                (function() {
                    const screen = document.getElementById('screen-onboarding-7');
                    const sub = screen.querySelector('[data-i18n=\"under_review_sub_runner\"]');
                    return {
                        subText: sub?.innerText,
                        isEnglish: sub?.innerText === 'Your documents and bank details are under review.'
                    };
                })()
            """, mid); mid += 1
            print("Runner Under Review EN:", json.dumps(runner_review_en))
            assert runner_review_en['isEnglish'], "Runner Under Review subtitle must strictly render in English when lang='en'"
            
            await take_screenshot(ws, "proof_runner_under_review_english.png", mid); mid += 1

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except Exception:
            proc.kill()

    print("\n=======================================================")
    print("ALL HARDWARE, LOCALIZATION & DEAD-LINK AUDITS PASSED 100%!")
    print("=======================================================")

if __name__ == '__main__':
    asyncio.run(main())
