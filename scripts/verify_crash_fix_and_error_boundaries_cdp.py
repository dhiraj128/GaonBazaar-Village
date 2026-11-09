import asyncio
import json
import subprocess
import time
import urllib.request
import websockets
import os
import sys

# Ensure utf-8 output safe for windows console
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PUB_DIR = os.path.abspath("public_web")
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
TEMP_DIR = os.path.abspath(".tmp_chrome_vendor_crash_fix")

async def eval_js(ws, expr, msg_id):
    await ws.send(json.dumps({
        "id": msg_id,
        "method": "Runtime.evaluate",
        "params": {
            "expression": expr,
            "returnByValue": True,
            "awaitPromise": True
        }
    }))
    while True:
        raw = await ws.recv()
        resp = json.loads(raw)
        if resp.get("id") == msg_id:
            res_val = resp.get("result", {}).get("result", {})
            if "value" in res_val:
                return res_val["value"]
            if "description" in res_val:
                return res_val["description"]
            return res_val

async def take_screenshot(ws, filename, msg_id):
    await ws.send(json.dumps({"id": msg_id, "method": "Page.captureScreenshot", "params": {"format": "png"}}))
    while True:
        raw = await ws.recv()
        resp = json.loads(raw)
        if resp.get("id") == msg_id:
            data = resp.get("result", {}).get("data", "")
            import base64
            with open(filename, "wb") as f:
                f.write(base64.b64decode(data))
            print(f"Captured screenshot: {filename}")
            break

async def main():
    print("=== STARTING VENDOR CRASH RESOLUTION & ERROR BOUNDARIES CDP TEST ===")
    http_proc = subprocess.Popen(
        ["backend\\.venv\\Scripts\\python.exe", "-m", "http.server", "8160", "--directory", PUB_DIR],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    time.sleep(1.5)

    chrome_proc = subprocess.Popen([
        CHROME_PATH,
        "--headless=new",
        "--remote-debugging-port=8161",
        f"--user-data-dir={TEMP_DIR}",
        "--window-size=412,915",
        "http://127.0.0.1:8160/vendor/index.html"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)

    try:
        targets_raw = urllib.request.urlopen("http://127.0.0.1:8161/json").read()
        targets = json.loads(targets_raw.decode('utf-8'))
        page_target = next(t for t in targets if t.get("type") == "page")
        ws_url = page_target["webSocketDebuggerUrl"]

        async with websockets.connect(ws_url) as ws:
            mid = 1
            await ws.send(json.dumps({"id": mid, "method": "Page.enable"})); mid += 1
            while True:
                raw = await ws.recv()
                if json.loads(raw).get("id") == 1:
                    break

            # ------------------------------------------------------------------
            # 1. AUTHENTICATE & TEST WHITE SCREEN OF DEATH RESOLUTION
            # ------------------------------------------------------------------
            print("\n=== TEST 1: White Screen of Death Resolution ===")
            await eval_js(ws, """
                localStorage.clear();
                localStorage.setItem('gb_vendor_authenticated', 'true');
                localStorage.setItem('gb_vendor_token', 'mock_token_123');
                localStorage.setItem('gaonbazaar_vendor_token', 'mock_token_123');
                localStorage.setItem('gb_vendor_phone', '9876543210');
                localStorage.setItem('gb_vendor_onboarding_completed', 'true');
                location.reload();
            """, mid); mid += 1
            await asyncio.sleep(2)

            # Switch to inventory tab
            await eval_js(ws, "switchDashboardTab('inventory')", mid); mid += 1
            await asyncio.sleep(1)

            # Check that inventory tab is active and visible with healthy offsetHeight
            inv_stats = await eval_js(ws, """
                (function() {
                    const el = document.getElementById('tab-inventory');
                    if (!el) return { exists: false };
                    const style = window.getComputedStyle(el);
                    return {
                        exists: true,
                        hidden: el.classList.contains('hidden'),
                        styleDisplay: el.style.display,
                        computedDisplay: style.display,
                        offsetHeight: el.offsetHeight
                    };
                })()
            """, mid); mid += 1
            print(f"Inventory Tab Render Stats: {json.dumps(inv_stats, indent=2)}")
            assert inv_stats.get('exists') is True, "tab-inventory must exist"
            assert inv_stats.get('hidden') is False, "tab-inventory must not have hidden class"
            assert inv_stats.get('computedDisplay') == 'block', "tab-inventory computed display must be block"
            assert inv_stats.get('offsetHeight', 0) > 300, "tab-inventory must have substantial rendered height (>300px)"

            # Capture visual proof 1: Clean rendered inventory dashboard
            await take_screenshot(ws, "proof_vendor_crash_resolved_dashboard.png", mid); mid += 1

            # ------------------------------------------------------------------
            # 2. TEST SECTION ERROR BOUNDARY COMPONENT
            # ------------------------------------------------------------------
            print("\n=== TEST 2: Section Error Boundary Fallback UI ===")
            # Simulate a fatal render exception inside inventory section
            await eval_js(ws, """
                SectionErrorBoundary.wrap('tab-inventory', function() {
                    throw new Error('Simulated Fatal Null Reference inside Inventory Component');
                }, 'Inventory Section');
            """, mid); mid += 1
            await asyncio.sleep(0.5)

            # Verify that fallback UI caught the error cleanly without breaking global shell
            boundary_stats = await eval_js(ws, """
                (function() {
                    const el = document.getElementById('tab-inventory');
                    const boundary = el ? el.querySelector('.section-error-boundary') : null;
                    return {
                        hasBoundary: !!boundary,
                        fallbackText: boundary ? boundary.innerText : '',
                        topNavVisible: !document.getElementById('top-nav')?.classList.contains('hidden'),
                        bottomTabsVisible: !document.getElementById('bottom-tabs')?.classList.contains('hidden')
                    };
                })()
            """, mid); mid += 1
            print(f"Error Boundary Fallback Stats: {json.dumps(boundary_stats, indent=2)}")
            assert boundary_stats['hasBoundary'] is True, "SectionErrorBoundary must render fallback container"
            assert "Something went wrong loading this section" in boundary_stats['fallbackText'], "Fallback must display user-friendly message"
            assert boundary_stats['topNavVisible'] is True, "Header must remain visible and unbroken"
            assert boundary_stats['bottomTabsVisible'] is True, "Bottom navigation must remain fully alive"

            # Capture visual proof 2: Error boundary fallback UI
            await take_screenshot(ws, "proof_vendor_error_boundary_fallback.png", mid); mid += 1

            # Verify recovery: switch to Orders tab and verify it renders perfectly
            print("Verifying tab switching recovery from error boundary...")
            await eval_js(ws, "switchDashboardTab('orders')", mid); mid += 1
            await asyncio.sleep(0.5)

            orders_visible = await eval_js(ws, """
                (function() {
                    const o = document.getElementById('tab-orders');
                    return o && !o.classList.contains('hidden') && o.offsetHeight > 200;
                })()
            """, mid); mid += 1
            print(f"Orders Tab successfully active and rendered: {orders_visible}")
            assert orders_visible, "Switching tabs recovers cleanly without global crash"

            # Reload to restore inventory DOM after error boundary test
            await eval_js(ws, "location.reload()", mid); mid += 1
            await asyncio.sleep(2)
            await eval_js(ws, "switchDashboardTab('inventory')", mid); mid += 1
            await asyncio.sleep(1)

            # ------------------------------------------------------------------
            # 3. VERIFY STRICT SINGLE-LANGUAGE RENDERING (NO SLASHES)
            # ------------------------------------------------------------------

            # Test English mode
            await eval_js(ws, "setLanguage('en')", mid); mid += 1
            await asyncio.sleep(0.5)
            en_slashes = await eval_js(ws, """
                (function() {
                    const checkIds = ['tab-inventory', 'modal-barcode-scanner', 'modal-take-photo', 'modal-custom-pricing'];
                    let slashes = [];
                    checkIds.forEach(id => {
                        const el = document.getElementById(id);
                        if (el) {
                            const matches = el.innerText.match(/[A-Za-z0-9\u0900-\u097F]+\\s*\\/\\s*[A-Za-z0-9\u0900-\u097F]+/g);
                            if (matches) slashes.push(...matches);
                        }
                    });
                    return slashes;
                })()
            """, mid); mid += 1
            print(f"English mode bilingual slashes: {en_slashes}")
            assert len(en_slashes) == 0, f"Found slashes in English mode: {en_slashes}"

            # Test Hindi mode
            await eval_js(ws, "setLanguage('hi')", mid); mid += 1
            await asyncio.sleep(0.5)
            hi_slashes = await eval_js(ws, """
                (function() {
                    const checkIds = ['tab-inventory', 'modal-barcode-scanner', 'modal-take-photo', 'modal-custom-pricing'];
                    let slashes = [];
                    checkIds.forEach(id => {
                        const el = document.getElementById(id);
                        if (el) {
                            const matches = el.innerText.match(/[A-Za-z0-9\u0900-\u097F]+\\s*\\/\\s*[A-Za-z0-9\u0900-\u097F]+/g);
                            if (matches) slashes.push(...matches);
                        }
                    });
                    return slashes;
                })()
            """, mid); mid += 1
            print(f"Hindi mode bilingual slashes: {hi_slashes}")
            assert len(hi_slashes) == 0, f"Found slashes in Hindi mode: {hi_slashes}"

            # Verify pure Hindi button strings
            scan_hi_text = await eval_js(ws, "document.getElementById('btn-action-scan-barcode')?.innerText || ''", mid); mid += 1
            photo_hi_text = await eval_js(ws, "document.getElementById('btn-action-take-photo')?.innerText || ''", mid); mid += 1
            assert "बारकोड स्कैन करें" in scan_hi_text, "Scan button must be pure Hindi"
            assert "फोटो खींचें" in photo_hi_text, "Photo button must be pure Hindi"

            await take_screenshot(ws, "proof_vendor_strict_single_lang_verified.png", mid); mid += 1

            # ------------------------------------------------------------------
            # 4. VERIFY ROGUE LANGUAGE COMPONENT REMOVAL
            # ------------------------------------------------------------------
            print("\n=== TEST 4: Rogue Component Removal ===")
            rogue_lang_stats = await eval_js(ws, """
                (function() {
                    const scr1 = document.getElementById('screen-onboarding-1');
                    const tabInv = document.getElementById('tab-inventory');
                    return {
                        screen1Hidden: !scr1 || scr1.classList.contains('hidden') || scr1.style.display === 'none',
                        invHasRogueLang: tabInv ? (tabInv.innerText.includes('Choose Your Language') || tabInv.innerText.includes('अपनी भाषा चुनें')) : false
                    };
                })()
            """, mid); mid += 1
            print(f"Rogue Language Selector Stats: {json.dumps(rogue_lang_stats, indent=2)}")
            assert rogue_lang_stats['screen1Hidden'] is True, "Onboarding step 1 must be strictly hidden on dashboard"
            assert rogue_lang_stats['invHasRogueLang'] is False, "Inventory tab must not contain language selection card"

            # ------------------------------------------------------------------
            # 5. VERIFY DECOUPLED BARCODE SCANNER PIPELINE
            # ------------------------------------------------------------------
            print("\n=== TEST 5: Decoupled Barcode Scanner Pipeline ===")
            await eval_js(ws, "openBarcodeScannerModal()", mid); mid += 1
            await asyncio.sleep(1)

            # Check sample chips contain NO price or MRP
            sample_chips = await eval_js(ws, "document.getElementById('sample-barcodes-container')?.innerText || ''", mid); mid += 1
            print(f"Sample barcodes text: {repr(sample_chips)}")
            assert "MRP" not in sample_chips and "₹" not in sample_chips, "Sample barcodes must not show price or MRP"

            # Trigger scan of barcode 8901030383701 (Aashirvaad Atta)
            await eval_js(ws, "handleBarcodeDetected('8901030383701')", mid); mid += 1
            await asyncio.sleep(1)

            # Scanner closes, pricing modal opens
            scanner_closed = await eval_js(ws, "document.getElementById('modal-barcode-scanner')?.classList.contains('hidden')", mid); mid += 1
            pricing_open = await eval_js(ws, "!document.getElementById('modal-custom-pricing')?.classList.contains('hidden')", mid); mid += 1
            assert scanner_closed and pricing_open, "Scanner modal must close and Custom Pricing modal must open"

            # Check populated name/image and completely empty pricing inputs
            name_val = await eval_js(ws, "document.getElementById('custom-pricing-name')?.value", mid); mid += 1
            mrp_val = await eval_js(ws, "document.getElementById('custom-pricing-mrp')?.value", mid); mid += 1
            price_val = await eval_js(ws, "document.getElementById('custom-pricing-price')?.value", mid); mid += 1
            stock_val = await eval_js(ws, "document.getElementById('custom-pricing-stock')?.value", mid); mid += 1

            print(f"Fetched Item Name: {repr(name_val)}")
            print(f"Blank MRP: {repr(mrp_val)} (Expected: '')")
            print(f"Blank Price: {repr(price_val)} (Expected: '')")
            print(f"Blank Stock: {repr(stock_val)} (Expected: '')")

            assert "Aashirvaad" in name_val or "आशीर्वाद" in name_val, "Name must be fetched from barcode lookup"
            assert mrp_val == "", "MRP must be completely blank"
            assert price_val == "", "Selling Price must be completely blank"
            assert stock_val == "", "Stock must be completely blank"

            # Enter vendor custom price
            await eval_js(ws, """
                document.getElementById('custom-pricing-mrp').value = '275';
                document.getElementById('custom-pricing-price').value = '250';
                document.getElementById('custom-pricing-stock').value = '40';
                calculateCustomPricingDiscount();
            """, mid); mid += 1
            await asyncio.sleep(0.5)

            await take_screenshot(ws, "proof_vendor_decoupled_barcode_verified.png", mid); mid += 1

            # Save item
            await eval_js(ws, "saveCustomPricedItem()", mid); mid += 1
            await asyncio.sleep(1)

            saved_item_title = await eval_js(ws, "document.querySelector('#inventory-list .product-item')?.getAttribute('data-title')", mid); mid += 1
            saved_item_price = await eval_js(ws, "document.querySelector('#inventory-list .product-item .text-slate-900.font-extrabold')?.innerText", mid); mid += 1
            print(f"Saved live store item: {repr(saved_item_title)} at {repr(saved_item_price)}")
            assert "Aashirvaad" in saved_item_title or "आशीर्वाद" in saved_item_title, "Saved item must be listed in inventory"
            assert "250" in saved_item_price, "Saved price must reflect vendor custom price 250"

            print("\n=======================================================")
            print("ALL 5 VERIFICATION TESTS PASSED FLAWLESSLY WITH 100% SUCCESS!")
            print("=======================================================")

    finally:
        chrome_proc.terminate()
        http_proc.terminate()

if __name__ == "__main__":
    asyncio.run(main())
