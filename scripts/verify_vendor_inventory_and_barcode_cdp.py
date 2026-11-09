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
TEMP_DIR = os.path.abspath(".tmp_chrome_vendor_barcode")

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
    print("=== STARTING VENDOR STRICT SINGLE-LANGUAGE & DECOUPLED BARCODE CDP TEST ===")
    http_proc = subprocess.Popen(
        ["backend\\.venv\\Scripts\\python.exe", "-m", "http.server", "8140", "--directory", PUB_DIR],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    time.sleep(1.5)

    chrome_proc = subprocess.Popen([
        CHROME_PATH,
        "--headless=new",
        "--remote-debugging-port=8141",
        f"--user-data-dir={TEMP_DIR}",
        "--window-size=412,915",
        "http://127.0.0.1:8140/vendor/index.html"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)

    try:
        targets_raw = urllib.request.urlopen("http://127.0.0.1:8141/json").read()
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
            # SETUP VENDOR AUTH & NAVIGATE TO DASHBOARD
            # ------------------------------------------------------------------
            print("\n1. Authenticating vendor & navigating directly to Dashboard...")
            await eval_js(ws, """
                localStorage.clear();
                localStorage.setItem('gb_vendor_authenticated', 'true');
                localStorage.setItem('gb_vendor_phone', '9876543210');
                localStorage.setItem('gb_vendor_onboarding_completed', 'true');
                location.reload();
            """, mid); mid += 1
            await asyncio.sleep(2)

            # Ensure switchDashboardTab('inventory') suppresses any onboarding screens
            await eval_js(ws, "switchDashboardTab('inventory')", mid); mid += 1
            await asyncio.sleep(1)

            # ------------------------------------------------------------------
            # TEST 1: ROGUE LANGUAGE SELECTOR SUPPRESSION
            # ------------------------------------------------------------------
            print("\n=== TEST 1: Rogue Language Selector Suppression ===")
            onboarding_hidden = await eval_js(ws, """
                (function() {
                    const scr1 = document.getElementById('screen-onboarding-1');
                    if (!scr1) return true;
                    const style = window.getComputedStyle(scr1);
                    return scr1.classList.contains('hidden') || style.display === 'none';
                })()
            """, mid); mid += 1
            print(f"Onboarding Screen 1 (Language Selector) is hidden: {onboarding_hidden}")
            assert onboarding_hidden, "Screen onboarding 1 must be strictly hidden on dashboard"

            # Check that tab-inventory does not contain 'Choose Your Language'
            tab_inv_text = await eval_js(ws, "document.getElementById('tab-inventory')?.innerText || ''", mid); mid += 1
            contains_lang_selector = "Choose Your Language" in tab_inv_text or "अपनी भाषा चुनें" in tab_inv_text
            print(f"Inventory tab contains rogue language selector: {contains_lang_selector} (Expected: False)")
            assert not contains_lang_selector, "Language selector must not be rendered in inventory tab"

            await take_screenshot(ws, "proof_vendor_inventory_no_rogue_lang.png", mid); mid += 1

            # ------------------------------------------------------------------
            # TEST 2: STRICT SINGLE-LANGUAGE RENDERING (NO SLASHES)
            # ------------------------------------------------------------------
            print("\n=== TEST 2: Strict Single-Language Rendering (English vs Hindi) ===")
            # First, check in English mode
            await eval_js(ws, "setLanguage('en')", mid); mid += 1
            await asyncio.sleep(0.5)

            # Check modals and inventory elements for slashed bilingual text
            en_slashed_count = await eval_js(ws, """
                (function() {
                    const checkElements = ['tab-inventory', 'modal-barcode-scanner', 'modal-take-photo', 'modal-custom-pricing'];
                    let slashes = [];
                    checkElements.forEach(id => {
                        const el = document.getElementById(id);
                        if (el) {
                            const text = el.innerText;
                            // Match ' / ' that looks like bilingual split
                            const matches = text.match(/[A-Za-z0-9\u0900-\u097F]+\\s*\\/\\s*[A-Za-z0-9\u0900-\u097F]+/g);
                            if (matches) slashes.push(...matches);
                        }
                    });
                    return slashes;
                })()
            """, mid); mid += 1
            print(f"English mode bilingual slashes found: {en_slashed_count}")
            assert len(en_slashed_count) == 0, f"Found bilingual slashes in English mode: {en_slashed_count}"

            # Now switch to Hindi mode
            await eval_js(ws, "setLanguage('hi')", mid); mid += 1
            await asyncio.sleep(0.5)

            hi_slashed_count = await eval_js(ws, """
                (function() {
                    const checkElements = ['tab-inventory', 'modal-barcode-scanner', 'modal-take-photo', 'modal-custom-pricing'];
                    let slashes = [];
                    checkElements.forEach(id => {
                        const el = document.getElementById(id);
                        if (el) {
                            const text = el.innerText;
                            const matches = text.match(/[A-Za-z0-9\u0900-\u097F]+\\s*\\/\\s*[A-Za-z0-9\u0900-\u097F]+/g);
                            if (matches) slashes.push(...matches);
                        }
                    });
                    return slashes;
                })()
            """, mid); mid += 1
            print(f"Hindi mode bilingual slashes found: {hi_slashed_count}")
            assert len(hi_slashed_count) == 0, f"Found bilingual slashes in Hindi mode: {hi_slashed_count}"

            # Check that inventory action buttons have pure Hindi text
            scan_btn_hi = await eval_js(ws, "document.getElementById('btn-action-scan-barcode')?.innerText", mid); mid += 1
            photo_btn_hi = await eval_js(ws, "document.getElementById('btn-action-take-photo')?.innerText", mid); mid += 1
            print(f"Hindi Scan Button Text: {repr(scan_btn_hi)}")
            print(f"Hindi Photo Button Text: {repr(photo_btn_hi)}")
            assert "बारकोड स्कैन करें" in scan_btn_hi, "Scan button must show pure Hindi"
            assert "फोटो" in photo_btn_hi, "Photo button must show pure Hindi"
            assert "/" not in scan_btn_hi and "/" not in photo_btn_hi, "No slashes permitted in buttons"

            await take_screenshot(ws, "proof_vendor_strict_single_language_hi.png", mid); mid += 1

            # ------------------------------------------------------------------
            # TEST 3: DECOUPLED BARCODE SCANNER PIPELINE
            # ------------------------------------------------------------------
            print("\n=== TEST 3: Decoupled Barcode Scanner Pipeline ===")
            await eval_js(ws, "openBarcodeScannerModal()", mid); mid += 1
            await asyncio.sleep(1)

            # Check that sample barcodes do NOT contain price or MRP in their labels
            sample_chips_text = await eval_js(ws, "document.getElementById('sample-barcodes-container')?.innerText || ''", mid); mid += 1
            print(f"Sample barcodes container text: {repr(sample_chips_text)}")
            assert "MRP" not in sample_chips_text, "Sample barcodes must not show MRP"
            assert "₹" not in sample_chips_text, "Sample barcodes must not show price or ₹"

            # Trigger scan of FMCG product (Aashirvaad Atta: 8901030383701)
            print("Triggering scan of barcode '8901030383701'...")
            await eval_js(ws, "handleBarcodeDetected('8901030383701')", mid); mid += 1
            await asyncio.sleep(1)

            barcode_closed = await eval_js(ws, "document.getElementById('modal-barcode-scanner')?.classList.contains('hidden')", mid); mid += 1
            pricing_opened = await eval_js(ws, "!document.getElementById('modal-custom-pricing')?.classList.contains('hidden')", mid); mid += 1
            print(f"Barcode modal closed: {barcode_closed}")
            print(f"Custom pricing modal opened: {pricing_opened}")
            assert barcode_closed and pricing_opened, "Barcode modal must close and Custom Pricing modal must open"

            # Verify that Name and Image are fetched, but MRP, Selling Price, and Stock are completely blank
            item_name_val = await eval_js(ws, "document.getElementById('custom-pricing-name')?.value", mid); mid += 1
            item_mrp_val = await eval_js(ws, "document.getElementById('custom-pricing-mrp')?.value", mid); mid += 1
            item_price_val = await eval_js(ws, "document.getElementById('custom-pricing-price')?.value", mid); mid += 1
            item_stock_val = await eval_js(ws, "document.getElementById('custom-pricing-stock')?.value", mid); mid += 1

            print(f"Populated Item Name: {repr(item_name_val)}")
            print(f"Blank MRP: {repr(item_mrp_val)} (Expected: '')")
            print(f"Blank Selling Price: {repr(item_price_val)} (Expected: '')")
            print(f"Blank Stock: {repr(item_stock_val)} (Expected: '')")

            assert "Aashirvaad" in item_name_val or "आशीर्वाद" in item_name_val, "Item name must be populated from barcode lookup"
            assert item_mrp_val == "", "MRP must be completely blank for vendor input"
            assert item_price_val == "", "Selling price must be completely blank for vendor input"
            assert item_stock_val == "", "Stock must be completely blank for vendor input"

            # Now vendor fills custom price: MRP 260, Price 240, Stock 50
            await eval_js(ws, """
                document.getElementById('custom-pricing-mrp').value = '260';
                document.getElementById('custom-pricing-price').value = '240';
                document.getElementById('custom-pricing-stock').value = '50';
                calculateCustomPricingDiscount();
            """, mid); mid += 1
            await asyncio.sleep(0.5)

            # Check discount calculation in Hindi
            badge_text_hi = await eval_js(ws, "document.getElementById('discount-badge-text')?.innerText", mid); mid += 1
            print(f"Hindi discount badge: {repr(badge_text_hi)}")
            assert "बचत" in badge_text_hi or "छूट" in badge_text_hi or "%" in badge_text_hi, "Discount badge should be in Hindi"
            assert "/" not in badge_text_hi, "No slashes in discount badge text"

            await take_screenshot(ws, "proof_vendor_barcode_decoupled_pricing.png", mid); mid += 1

            # Save item to catalog
            await eval_js(ws, "saveCustomPricedItem()", mid); mid += 1
            await asyncio.sleep(1)

            saved_item_name = await eval_js(ws, "document.querySelector('#inventory-list .product-item')?.getAttribute('data-title')", mid); mid += 1
            saved_item_price = await eval_js(ws, "document.querySelector('#inventory-list .product-item .text-slate-900.font-extrabold')?.innerText", mid); mid += 1
            print(f"Saved Catalog Item: {repr(saved_item_name)} with price {repr(saved_item_price)}")
            assert "Aashirvaad" in saved_item_name or "आशीर्वाद" in saved_item_name, "Item should be saved into live catalog"
            assert "240" in saved_item_price, "Item price should be vendor entered 240"

            # ------------------------------------------------------------------
            # TEST 4: VOICE SEARCH INTEGRATION
            # ------------------------------------------------------------------
            print("\n=== TEST 4: Voice Search Integration ===")
            # Use window.simulateVoiceSearch('आशीर्वाद')
            await eval_js(ws, "window.simulateVoiceSearch('आशीर्वाद')", mid); mid += 1
            await asyncio.sleep(1)

            search_val = await eval_js(ws, "document.getElementById('inventory-search')?.value", mid); mid += 1
            visible_count = await eval_js(ws, "document.querySelectorAll('#inventory-list .product-item:not(.hidden)').length", mid); mid += 1
            print(f"Search input value after voice query: {repr(search_val)}")
            print(f"Visible items after voice search filter: {visible_count}")
            assert search_val == "आशीर्वाद", "Voice search must update input value"
            assert visible_count > 0, "Inventory must be filtered to matching items"

            await take_screenshot(ws, "proof_vendor_voice_search_active.png", mid); mid += 1

            print("\n=======================================================")
            print("ALL 4 TESTS PASSED FLAWLESSLY WITH 100% SPEC COMPLIANCE!")
            print("=======================================================")

    finally:
        chrome_proc.terminate()
        http_proc.terminate()

if __name__ == "__main__":
    asyncio.run(main())
