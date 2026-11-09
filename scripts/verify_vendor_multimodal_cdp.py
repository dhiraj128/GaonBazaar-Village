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
TEMP_DIR = os.path.abspath(".tmp_chrome_vendor")

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
    print("=== STARTING VENDOR MULTIMODAL INVENTORY CDP VERIFICATION ===")
    http_proc = subprocess.Popen(
        ["backend\\.venv\\Scripts\\python.exe", "-m", "http.server", "8130", "--directory", PUB_DIR],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    time.sleep(1.5)

    chrome_proc = subprocess.Popen([
        CHROME_PATH,
        "--headless=new",
        "--remote-debugging-port=8131",
        f"--user-data-dir={TEMP_DIR}",
        "--window-size=412,915",
        "http://127.0.0.1:8130/vendor/index.html"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)

    try:
        targets_raw = urllib.request.urlopen("http://127.0.0.1:8131/json").read()
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
            # SETUP VENDOR AUTH & NAVIGATE TO INVENTORY TAB
            # ------------------------------------------------------------------
            print("\n1. Authenticating vendor & navigating to Inventory tab...")
            await eval_js(ws, """
                localStorage.clear();
                localStorage.setItem('gb_vendor_authenticated', 'true');
                localStorage.setItem('gb_vendor_phone', '9876543210');
                localStorage.setItem('gb_vendor_onboarding_completed', 'true');
                location.reload();
            """, mid); mid += 1
            await asyncio.sleep(2)

            await eval_js(ws, "switchDashboardTab('inventory')", mid); mid += 1
            await asyncio.sleep(1)

            inv_tab_visible = await eval_js(ws, "!document.getElementById('tab-inventory')?.classList.contains('hidden')", mid); mid += 1
            print(f"Inventory Tab Visible: {inv_tab_visible}")
            assert inv_tab_visible, "Inventory tab must be visible"

            # ------------------------------------------------------------------
            # 1. TEST SMART SEARCH BAR WITH VOICE ACTION
            # ------------------------------------------------------------------
            print("\n=== 2. Testing Smart Search Bar & Voice Integration ===")
            search_input_exists = await eval_js(ws, "!!document.getElementById('inventory-search')", mid); mid += 1
            mic_btn_exists = await eval_js(ws, "!!document.getElementById('btn-vendor-voice-search')", mid); mid += 1
            corporate_csv_exists = await eval_js(ws, "document.getElementById('tab-inventory')?.innerText.includes('Bulk Import (CSV)')", mid); mid += 1

            print(f"Search input exists: {search_input_exists}")
            print(f"Voice action mic button exists: {mic_btn_exists}")
            print(f"Corporate CSV button removed: {not corporate_csv_exists} (Expected: True)")
            assert search_input_exists, "Smart search bar must exist"
            assert mic_btn_exists, "Microphone button must exist inside search bar"
            assert not corporate_csv_exists, "Corporate Bulk Import (CSV) button must be removed"

            # Test real-time filtering with search bar
            print("Testing inventory filtering...")
            await eval_js(ws, "document.getElementById('inventory-search').value = 'Atta'; filterInventory('Atta');", mid); mid += 1
            await asyncio.sleep(0.5)
            filtered_visible = await eval_js(ws, "document.querySelectorAll('#inventory-list .product-item:not(.hidden)').length", mid); mid += 1
            print(f"Items visible when searching 'Atta': {filtered_visible}")
            assert filtered_visible > 0, "Atta items should be visible"

            # Reset search
            await eval_js(ws, "document.getElementById('inventory-search').value = ''; filterInventory('');", mid); mid += 1
            await asyncio.sleep(0.5)

            # Test voice search trigger
            await eval_js(ws, "toggleVendorVoiceSearch()", mid); mid += 1
            await asyncio.sleep(0.5)
            mic_active = await eval_js(ws, "document.getElementById('btn-vendor-voice-search')?.classList.contains('animate-pulse') || window.isVendorListening", mid); mid += 1
            print(f"Microphone activated listening state: {mic_active}")

            # Capture visual artifact 1: Inventory top with search & split action buttons
            await take_screenshot(ws, "proof_vendor_inventory_multimodal_top.png", mid); mid += 1

            # ------------------------------------------------------------------
            # 2. TEST SPLIT ACTION BUTTONS (BARCODE VS. LOOSE ITEMS)
            # ------------------------------------------------------------------
            print("\n=== 3. Testing Split Action Buttons ===")
            scan_btn_exists = await eval_js(ws, "!!document.getElementById('btn-action-scan-barcode')", mid); mid += 1
            photo_btn_exists = await eval_js(ws, "!!document.getElementById('btn-action-take-photo')", mid); mid += 1
            print(f"Scan Barcode Button Exists: {scan_btn_exists}")
            print(f"Take Photo Button Exists: {photo_btn_exists}")
            assert scan_btn_exists and photo_btn_exists, "Both split action buttons must exist"

            # --- 2.A: Test "Scan Barcode" Modal & HTML5 Scanner ---
            print("\nTesting 'Scan Barcode' flow...")
            await eval_js(ws, "openBarcodeScannerModal()", mid); mid += 1
            await asyncio.sleep(1)

            barcode_modal_visible = await eval_js(ws, "!document.getElementById('modal-barcode-scanner')?.classList.contains('hidden')", mid); mid += 1
            laser_line_exists = await eval_js(ws, "!!document.getElementById('barcode-laser-line')", mid); mid += 1
            print(f"Barcode Scanner Modal Visible: {barcode_modal_visible}")
            print(f"Laser scan line exists: {laser_line_exists}")
            assert barcode_modal_visible, "Barcode scanner modal must be open"
            assert laser_line_exists, "Laser line must exist in scanner viewport"

            await take_screenshot(ws, "proof_vendor_barcode_scanner_modal.png", mid); mid += 1

            # Tap FMCG Barcode Test Chip: Aashirvaad Atta 5kg (8901030383701)
            print("Triggering barcode scan for Aashirvaad Atta (8901030383701)...")
            await eval_js(ws, "handleBarcodeDetected('8901030383701')", mid); mid += 1
            await asyncio.sleep(1)

            # Barcode scanner should close and Custom Pricing Modal should open
            barcode_modal_closed = await eval_js(ws, "document.getElementById('modal-barcode-scanner')?.classList.contains('hidden')", mid); mid += 1
            pricing_modal_opened = await eval_js(ws, "!document.getElementById('modal-custom-pricing')?.classList.contains('hidden')", mid); mid += 1
            print(f"Barcode Scanner Modal Closed: {barcode_modal_closed}")
            print(f"Custom Pricing Modal Opened: {pricing_modal_opened}")
            assert barcode_modal_closed, "Barcode modal must close on detection"
            assert pricing_modal_opened, "Custom Pricing Form must open automatically after scan"

            # Check prefilled details
            prefilled_name = await eval_js(ws, "document.getElementById('custom-pricing-name')?.value", mid); mid += 1
            prefilled_mrp = await eval_js(ws, "document.getElementById('custom-pricing-mrp')?.value", mid); mid += 1
            prefilled_price = await eval_js(ws, "document.getElementById('custom-pricing-price')?.value", mid); mid += 1
            print(f"Prefilled Item Name: {prefilled_name}")
            print(f"Prefilled MRP: {prefilled_mrp}, Selling Price: {prefilled_price}")
            assert "Aashirvaad" in prefilled_name, "Item name must be auto-fetched from master FMCG catalog"
            assert float(prefilled_mrp) == 260.0, "MRP must match master catalog"

            # Close pricing modal
            await eval_js(ws, "closeCustomPricingModal()", mid); mid += 1
            await asyncio.sleep(0.5)

            # --- 2.B: Test "Take Photo" Modal for Loose/Fresh Items ---
            print("\nTesting 'Take Photo' flow...")
            await eval_js(ws, "openPhotoCaptureModal()", mid); mid += 1
            await asyncio.sleep(1)

            photo_modal_visible = await eval_js(ws, "!document.getElementById('modal-take-photo')?.classList.contains('hidden')", mid); mid += 1
            camera_input_has_capture = await eval_js(ws, "document.getElementById('vendor-camera-file-input')?.getAttribute('capture') === 'environment'", mid); mid += 1
            print(f"Take Photo Modal Visible: {photo_modal_visible}")
            print(f"File Input has capture='environment': {camera_input_has_capture}")
            assert photo_modal_visible, "Take Photo modal must be open"
            assert camera_input_has_capture, "Device camera capture attribute must be environment"

            # Select loose item chip: Fresh Tomatoes
            print("Selecting Loose Item chip: Fresh Tomatoes...")
            await eval_js(ws, "selectLooseItemChip('ताज़ा टमाटर (Fresh Tomatoes)', 'Vegetables', '1 kg', 'https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=500&q=80')", mid); mid += 1
            await asyncio.sleep(0.5)

            chip_name_val = await eval_js(ws, "document.getElementById('loose-item-name-input')?.value", mid); mid += 1
            print(f"Selected loose item name: {repr(chip_name_val)}")
            assert "टमाटर" in chip_name_val or "Tomatoes" in chip_name_val, "Loose item name must be populated"

            await take_screenshot(ws, "proof_vendor_take_photo_modal.png", mid); mid += 1

            # Click Continue to Pricing
            await eval_js(ws, "continueToPricingFromPhoto()", mid); mid += 1
            await asyncio.sleep(1)

            photo_modal_closed = await eval_js(ws, "document.getElementById('modal-take-photo')?.classList.contains('hidden')", mid); mid += 1
            pricing_modal_opened2 = await eval_js(ws, "!document.getElementById('modal-custom-pricing')?.classList.contains('hidden')", mid); mid += 1
            print(f"Photo Modal Closed: {photo_modal_closed}")
            print(f"Custom Pricing Modal Opened: {pricing_modal_opened2}")
            assert photo_modal_closed and pricing_modal_opened2, "Must advance smoothly from Photo to Custom Pricing"

            # ------------------------------------------------------------------
            # 3. TEST THE CUSTOM PRICING FORM (NO LOCKED SKUS & DISCOUNT BADGE)
            # ------------------------------------------------------------------
            print("\n=== 4. Testing Custom Pricing Form (No Locked SKUs) ===")
            # Check name field is NOT readonly (vendor has ultimate control)
            name_is_readonly = await eval_js(ws, "document.getElementById('custom-pricing-name')?.hasAttribute('readonly')", mid); mid += 1
            print(f"Name field is readonly: {name_is_readonly} (Expected: False - Unlocked!)")
            assert not name_is_readonly, "Name field must NOT be locked or readonly!"

            # Test custom price inputs: MRP 50, Selling Price 40 -> 20% OFF
            await eval_js(ws, """
                document.getElementById('custom-pricing-name').value = 'ताज़ा देसी टमाटर (1 kg)';
                document.getElementById('custom-pricing-mrp').value = '50';
                document.getElementById('custom-pricing-price').value = '40';
                calculateCustomPricingDiscount();
            """, mid); mid += 1
            await asyncio.sleep(0.5)

            discount_text = await eval_js(ws, "document.getElementById('discount-badge-text')?.innerText", mid); mid += 1
            print(f"Calculated Discount Badge Text: {repr(discount_text)}")
            assert "20% OFF" in discount_text, "Discount must reflect 20% OFF (50 -> 40)"
            assert "10" in discount_text, "Discount savings must show 10"

            # Test changing selling price to ₹35 -> 30% OFF
            await eval_js(ws, """
                document.getElementById('custom-pricing-price').value = '35';
                calculateCustomPricingDiscount();
            """, mid); mid += 1
            await asyncio.sleep(0.5)

            discount_text2 = await eval_js(ws, "document.getElementById('discount-badge-text')?.innerText", mid); mid += 1
            print(f"Updated Discount Badge Text (Price 35): {repr(discount_text2)}")
            assert "30% OFF" in discount_text2, "Discount must update dynamically to 30% OFF"

            await take_screenshot(ws, "proof_vendor_custom_pricing_form.png", mid); mid += 1

            # Submit and save to live store
            print("Saving custom priced item to store...")
            await eval_js(ws, "saveCustomPricedItem()", mid); mid += 1
            await asyncio.sleep(1)

            pricing_modal_closed = await eval_js(ws, "document.getElementById('modal-custom-pricing')?.classList.contains('hidden')", mid); mid += 1
            first_item_title = await eval_js(ws, "document.querySelector('#inventory-list .product-item')?.getAttribute('data-title')", mid); mid += 1
            first_item_price = await eval_js(ws, "document.querySelector('#inventory-list .product-item .text-slate-900.font-extrabold')?.innerText", mid); mid += 1
            print(f"Pricing Modal Closed: {pricing_modal_closed}")
            print(f"First Item in Live Catalog: {repr(first_item_title)} at {repr(first_item_price)}")
            assert pricing_modal_closed, "Modal must close on save"
            assert "टमाटर" in first_item_title, "Saved item must be prepended to live inventory list"
            assert "35" in first_item_price, "Saved price must match vendor price"

            print("\nALL MULTIMODAL INVENTORY TESTS PASSED 100% PERFECTLY!")

    finally:
        chrome_proc.terminate()
        http_proc.terminate()

if __name__ == "__main__":
    asyncio.run(main())
