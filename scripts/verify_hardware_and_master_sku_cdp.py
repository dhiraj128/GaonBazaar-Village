import asyncio
import json
import subprocess
import time
import urllib.request
import websockets
import os
import sys
import shutil

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PUB_DIR = os.path.abspath("public_web")
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
TEMP_DIR = os.path.abspath(".tmp_chrome_hardware_master_sku")
ARTIFACT_DIR = r"C:\Users\dhira\.gemini\antigravity\brain\918c8085-b60b-40a9-a077-a3344458bcc5"

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
            if os.path.exists(ARTIFACT_DIR):
                shutil.copy(filename, os.path.join(ARTIFACT_DIR, os.path.basename(filename)))
                print(f"Copied to artifact directory: {os.path.join(ARTIFACT_DIR, os.path.basename(filename))}")
            break

async def main():
    print("=== STARTING HARDWARE APIS & MASTER SKU CDP VERIFICATION ===")
    http_proc = subprocess.Popen(
        ["backend\\.venv\\Scripts\\python.exe", "-m", "http.server", "8190", "--directory", PUB_DIR],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    time.sleep(1.5)

    chrome_proc = subprocess.Popen([
        CHROME_PATH,
        "--headless=new",
        "--remote-debugging-port=8191",
        f"--user-data-dir={TEMP_DIR}",
        "--window-size=412,915",
        "http://127.0.0.1:8190/vendor/index.html"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)

    try:
        targets_raw = urllib.request.urlopen("http://127.0.0.1:8191/json").read()
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

            # 1. Authenticate vendor and switch to inventory tab
            print("\n--- TEST 1: Authenticate and Navigate to Inventory ---")
            await eval_js(ws, """
                localStorage.clear();
                localStorage.setItem('gb_vendor_authenticated', 'true');
                localStorage.setItem('gb_vendor_token', 'mock_token_hardware');
                localStorage.setItem('gb_vendor_phone', '9876543210');
                localStorage.setItem('gb_vendor_onboarding_completed', 'true');
                location.reload();
            """, mid); mid += 1
            await asyncio.sleep(2)

            await eval_js(ws, "switchDashboardTab('inventory');", mid); mid += 1
            await asyncio.sleep(0.5)

            # 2. Test UI CSS Polish: Microphone centering and clean single + button
            print("\n--- TEST 2: UI Polish (Microphone Centering & Non-Redundant Text) ---")
            ui_audit = await eval_js(ws, """
                (function() {
                    const micBtn = document.getElementById('btn-vendor-voice-search');
                    const searchInput = document.getElementById('inventory-search');
                    const typeItemSpan = document.querySelector('[data-i18n="type_item_name_btn"]');
                    const typeItemParent = typeItemSpan ? typeItemSpan.parentElement : null;

                    const micRect = micBtn ? micBtn.getBoundingClientRect() : null;
                    const inputRect = searchInput ? searchInput.getBoundingClientRect() : null;

                    return {
                        micInsideInputX: micRect && inputRect ? (micRect.right <= inputRect.right + 2 && micRect.left > inputRect.left) : false,
                        micInsideInputY: micRect && inputRect ? (micRect.top >= inputRect.top && micRect.bottom <= inputRect.bottom) : false,
                        micClasses: micBtn?.className,
                        typeItemText: typeItemSpan ? typeItemSpan.innerText.trim() : null,
                        typeItemFullText: typeItemParent ? typeItemParent.innerText.replace(/\\s+/g, ' ').trim() : null,
                        hasDuplicatePlus: typeItemParent ? /\\+\\s*\\+/.test(typeItemParent.innerText) : false
                    };
                })()
            """, mid); mid += 1
            print(f"UI Polish Audit: {json.dumps(ui_audit, indent=2)}")
            assert ui_audit.get("micInsideInputX") is True, "Microphone must be inside search input horizontally"
            assert ui_audit.get("micInsideInputY") is True, "Microphone must be centered inside search input vertically"
            assert ui_audit.get("hasDuplicatePlus") is False, "Duplicate plus sign (+ +) must NOT exist"
            assert ui_audit.get("typeItemText") == "Type Item Name", f"Expected 'Type Item Name', got '{ui_audit.get('typeItemText')}'"

            # Capture visual proof: Clean microphone button alignment and clean single + button
            await take_screenshot(ws, "proof_ui_mic_centered_and_clean_text.png", mid); mid += 1

            # 3. Test Native Hardware Camera API Enforcement
            print("\n--- TEST 3: Native Hardware Camera API Enforcement ---")
            camera_audit = await eval_js(ws, """
                (function() {
                    const fileInput = document.getElementById('vendor-camera-file-input');
                    const takePhotoBtn = document.getElementById('btn-action-take-photo');
                    return {
                        hasInput: fileInput !== null,
                        type: fileInput?.getAttribute('type'),
                        accept: fileInput?.getAttribute('accept'),
                        capture: fileInput?.getAttribute('capture'),
                        hasTakePhotoBtn: takePhotoBtn !== null
                    };
                })()
            """, mid); mid += 1
            print(f"Camera API Audit: {json.dumps(camera_audit, indent=2)}")
            assert camera_audit.get("type") == "file", "Input must be type='file'"
            assert camera_audit.get("accept") == "image/*", "Input must have accept='image/*'"
            assert camera_audit.get("capture") == "environment", "Input must strictly have capture='environment' for rear camera"

            # Test triggerCameraCapture() triggers file input click
            cam_click_test = await eval_js(ws, """
                (function() {
                    let clicked = false;
                    const input = document.getElementById('vendor-camera-file-input');
                    const origClick = input.click;
                    input.click = function() { clicked = true; };
                    triggerCameraCapture();
                    input.click = origClick;
                    return { clicked: clicked };
                })()
            """, mid); mid += 1
            print(f"Trigger Camera Capture Test: {json.dumps(cam_click_test, indent=2)}")
            assert cam_click_test.get("clicked") is True, "triggerCameraCapture must trigger camera input click"

            # Open Take Photo modal and verify preview box
            await eval_js(ws, "openPhotoCaptureModal();", mid); mid += 1
            await asyncio.sleep(0.3)
            await take_screenshot(ws, "proof_hardware_camera_capture_verified.png", mid); mid += 1
            await eval_js(ws, "closePhotoCaptureModal();", mid); mid += 1
            await asyncio.sleep(0.2)

            # 4. Test Master SKU Image Mapping for Barcode Scanner
            print("\n--- TEST 4: Master SKU Image Mapping on Barcode Detection ---")
            # Scan Aashirvaad Atta Barcode (8901030383701)
            await eval_js(ws, "handleBarcodeDetected('8901030383701');", mid); mid += 1
            await asyncio.sleep(0.5)

            barcode_sku_audit = await eval_js(ws, """
                (function() {
                    const nameInp = document.getElementById('custom-pricing-name');
                    const previewImg = document.getElementById('custom-pricing-preview-img');
                    const mrpInp = document.getElementById('custom-pricing-mrp');
                    const priceInp = document.getElementById('custom-pricing-price');
                    const stockInp = document.getElementById('custom-pricing-stock');
                    return {
                        name: nameInp ? nameInp.value : '',
                        imgSrc: previewImg ? previewImg.src : '',
                        hasValidImage: previewImg ? (previewImg.src.startsWith('http') && previewImg.src.length > 20) : false,
                        mrpBlank: mrpInp ? mrpInp.value === '' : false,
                        priceBlank: priceInp ? priceInp.value === '' : false,
                        stockBlank: stockInp ? stockInp.value === '' : false
                    };
                })()
            """, mid); mid += 1
            print(f"Barcode SKU Audit (Atta): {json.dumps(barcode_sku_audit, indent=2)}")
            assert "Aashirvaad" in barcode_sku_audit.get("name", ""), "Barcode must map to Aashirvaad Chakki Atta"
            assert barcode_sku_audit.get("hasValidImage") is True, "Must map to a valid high-quality product image URL"
            assert barcode_sku_audit.get("mrpBlank") is True, "MRP must remain blank for vendor decoupling"
            assert barcode_sku_audit.get("priceBlank") is True, "Price must remain blank for vendor decoupling"

            # 5. Test Proactive Master SKU Image Suggestion when Typing / Speaking
            print("\n--- TEST 5: Proactive Master SKU Suggestion on Item Name Typing ---")
            # Clear and type "Milk"
            await eval_js(ws, """
                const nameInp = document.getElementById('custom-pricing-name');
                nameInp.value = 'Amul Taaza Milk 1L';
                handleCustomPricingNameInput(nameInp.value);
            """, mid); mid += 1
            await asyncio.sleep(0.3)

            typed_sku_audit = await eval_js(ws, """
                (function() {
                    const previewImg = document.getElementById('custom-pricing-preview-img');
                    const suggBanner = document.getElementById('custom-pricing-sku-suggestion');
                    const suggText = document.getElementById('sku-suggestion-text');
                    const catTag = document.getElementById('custom-pricing-cat-tag');
                    return {
                        imgSrc: previewImg ? previewImg.src : '',
                        isMilkImage: previewImg ? previewImg.src.includes('photo-1550583724') : false,
                        suggBannerVisible: suggBanner ? !suggBanner.classList.contains('hidden') : false,
                        suggText: suggText ? suggText.innerText : '',
                        category: catTag ? catTag.innerText : ''
                    };
                })()
            """, mid); mid += 1
            print(f"Typed SKU Audit (Milk): {json.dumps(typed_sku_audit, indent=2)}")
            assert typed_sku_audit.get("isMilkImage") is True, "Typing Milk must proactively load Amul Milk master image"
            assert typed_sku_audit.get("suggBannerVisible") is True, "Master SKU suggestion banner must be visible"
            assert typed_sku_audit.get("category") == "Dairy", "Category must update to Dairy"

            # Capture visual proof: Proactive Master SKU image and suggestion banner
            await take_screenshot(ws, "proof_master_sku_proactive_image_matched.png", mid); mid += 1

            print("\n✅ ALL HARDWARE APIS & MASTER SKU CDP TESTS PASSED PERFECTLY!")

    finally:
        chrome_proc.terminate()
        http_proc.terminate()

if __name__ == "__main__":
    asyncio.run(main())
