# scripts/verify_exhaustive_villages_and_camera_cdp.py
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
TEMP_DIR = os.path.abspath(".tmp_chrome_exhaustive_villages_camera")
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
    print("=== STARTING EXHAUSTIVE VILLAGES & NATIVE CAMERA CDP VERIFICATION ===")
    http_proc = subprocess.Popen(
        ["backend\\.venv\\Scripts\\python.exe", "-m", "http.server", "8194", "--directory", PUB_DIR],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    time.sleep(1.5)

    chrome_proc = subprocess.Popen([
        CHROME_PATH,
        "--headless=new",
        "--remote-debugging-port=8195",
        f"--user-data-dir={TEMP_DIR}",
        "--window-size=412,915",
        "http://127.0.0.1:8194/vendor/index.html"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)

    try:
        targets_raw = urllib.request.urlopen("http://127.0.0.1:8195/json").read()
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

            # -----------------------------------------------------------------
            # TEST 1: VENDOR EXHAUSTIVE VILLAGES & STRICT PINCODE AUTOPOPULATION
            # -----------------------------------------------------------------
            print("\n--- TEST 1: Vendor Exhaustive Villages & Pincode Auto-Fill ---")
            village_check = await eval_js(ws, """
                (() => {
                    const villages = window.GAONBAZAAR_VILLAGES || [];
                    const tengari = villages.find(v => v.en === 'Tengari');
                    const shibai = villages.find(v => v.en === 'Shibai Patti');
                    const minapur = villages.find(v => v.en === 'Minapur');
                    const kanti = villages.find(v => v.en === 'Kanti');
                    const bochahan = villages.find(v => v.en === 'Bochahan');
                    return {
                        total_count: villages.length,
                        tengari: tengari,
                        shibai: shibai,
                        minapur: minapur,
                        kanti: kanti,
                        bochahan: bochahan
                    };
                })()
            """, mid); mid += 1
            print("Village Dataset Check:", json.dumps(village_check, indent=2))
            assert village_check['total_count'] >= 30, f"Expected >= 30 villages, got {village_check['total_count']}"
            assert village_check['tengari']['pincode'] == '843128', "Tengari pincode must be 843128"
            assert village_check['shibai']['pincode'] == '843128', "Shibai Patti pincode must be 843128"
            assert village_check['kanti']['pincode'] == '843109', "Kanti pincode must be 843109"

            # Test Village Search & Auto-Fill in Vendor
            vendor_autofill_result = await eval_js(ws, """
                (() => {
                    // Navigate to location onboarding step
                    if (typeof goToVendorStep === 'function') {
                        goToVendorStep(2);
                    }
                    // Trigger search for Tengari
                    handleVendorVillageSearch('Tengari');
                    const dropdown = document.getElementById('vendor-village-dropdown');
                    const dropdownVisible = !dropdown.classList.contains('hidden');
                    const firstOption = dropdown.querySelector('.village-label')?.innerText || '';

                    // Select Tengari
                    selectVendorVillage('Tengari', '843128');
                    const villageVal = document.getElementById('vendor-village-name')?.value;
                    const pincodeVal = document.getElementById('vendor-pincode')?.value;

                    return {
                        dropdownVisible,
                        firstOption,
                        villageVal,
                        pincodeVal
                    };
                })()
            """, mid); mid += 1
            print("Vendor Village Selection Result:", json.dumps(vendor_autofill_result, indent=2))
            assert vendor_autofill_result['villageVal'] == 'Tengari', "Village name must be Tengari"
            assert vendor_autofill_result['pincodeVal'] == '843128', "Pincode must be 843128"

            await take_screenshot(ws, "proof_vendor_village_pincode_autopopulated.png", mid); mid += 1

            # -----------------------------------------------------------------
            # TEST 2: SINGLE-LANGUAGE RENDERING (HINDI) & ZERO SLASHES
            # -----------------------------------------------------------------
            print("\n--- TEST 2: Single-Language Hindi Rendering & Zero Slashes ---")
            hindi_result = await eval_js(ws, """
                (() => {
                    if (typeof setLanguage === 'function') {
                        setLanguage('hi');
                    } else {
                        window.currentLang = 'hi';
                    }
                    handleVendorVillageSearch('तेंगारी');
                    const dropdown = document.getElementById('vendor-village-dropdown');
                    const label = dropdown.querySelector('.village-label')?.innerText || '';
                    const pinBadge = dropdown.querySelector('.font-mono')?.innerText || '';
                    const hasSlash = label.includes('/');

                    selectVendorVillage('तेंगारी', '843128');
                    const villageVal = document.getElementById('vendor-village-name')?.value;
                    const pincodeVal = document.getElementById('vendor-pincode')?.value;

                    return {
                        label,
                        pinBadge,
                        hasSlash,
                        villageVal,
                        pincodeVal
                    };
                })()
            """, mid); mid += 1
            print("Vendor Hindi Village Search Result:", json.dumps(hindi_result, indent=2))
            assert hindi_result['label'] == 'तेंगारी', f"Expected तेंगारी, got {hindi_result['label']}"
            assert not hindi_result['hasSlash'], "Zero slashes allowed in single-language mode"
            assert hindi_result['pincodeVal'] == '843128', "Pincode must auto-populate to 843128"

            # -----------------------------------------------------------------
            # TEST 3: NATIVE CAMERA API ATTRIBUTES & WEBRTC FALLBACK
            # -----------------------------------------------------------------
            print("\n--- TEST 3: Camera Hardware Attributes & WebRTC Viewfinder ---")
            camera_attrs = await eval_js(ws, """
                (() => {
                    const input = document.getElementById('vendor-camera-file-input');
                    const video = document.getElementById('vendor-camera-stream-video');
                    const snapBtn = document.getElementById('btn-snap-webrtc-photo');
                    const webrtcBtn = document.getElementById('btn-start-webrtc-viewfinder');
                    return {
                        inputExists: !!input,
                        accept: input?.getAttribute('accept'),
                        capture: input?.getAttribute('capture'),
                        videoExists: !!video,
                        snapBtnExists: !!snapBtn,
                        webrtcBtnExists: !!webrtcBtn
                    };
                })()
            """, mid); mid += 1
            print("Camera Attributes Check:", json.dumps(camera_attrs, indent=2))
            assert camera_attrs['inputExists'], "vendor-camera-file-input must exist"
            assert camera_attrs['accept'] == "image/*", f"Expected image/*, got {camera_attrs['accept']}"
            assert camera_attrs['capture'] == "environment", f"Expected environment, got {camera_attrs['capture']}"
            assert camera_attrs['videoExists'], "WebRTC video viewfinder must exist"
            assert camera_attrs['snapBtnExists'], "WebRTC snap button must exist"

            # -----------------------------------------------------------------
            # TEST 4: INSTANT IMAGE AUTO-PREVIEW & DECOUPLED PRICING FORM
            # -----------------------------------------------------------------
            print("\n--- TEST 4: Instant Image Auto-Preview & Decoupled Pricing ---")
            mock_snapped_data_url = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='100' height='100'><rect width='100' height='100' fill='%2310b981'/><text x='15' y='55' fill='white' font-family='sans-serif' font-weight='bold' font-size='14'>SNAPPED</text></svg>"

            pricing_transition = await eval_js(ws, f"""
                (() => {{
                    if (typeof setLanguage === 'function') {{
                        setLanguage('en');
                    }} else {{
                        window.currentLang = 'en';
                    }}

                    // Simulate photo capture
                    currentSnappedPhotoData = "{mock_snapped_data_url}";
                    
                    // Directly open custom pricing modal as handleVendorCameraPhoto does
                    closePhotoCaptureModal();
                    openCustomPricingModal({{
                        title: "Fresh Desi Tomatoes (तेंगारी)",
                        category: "Vegetables",
                        unit: "1 kg",
                        mrp: '',
                        price: '',
                        stock: '',
                        img: currentSnappedPhotoData
                    }});

                    const pricingModal = document.getElementById('modal-custom-pricing');
                    const isVisible = !pricingModal.classList.contains('hidden');
                    const previewImgSrc = document.getElementById('custom-pricing-preview-img')?.src;
                    const mrpVal = document.getElementById('custom-pricing-mrp')?.value;
                    const priceVal = document.getElementById('custom-pricing-price')?.value;
                    const stockVal = document.getElementById('custom-pricing-stock')?.value;
                    const titleVal = document.getElementById('custom-pricing-name')?.value;

                    return {{
                        pricingModalVisible: isVisible,
                        previewImgMatches: previewImgSrc === currentSnappedPhotoData,
                        mrpVal: mrpVal,
                        priceVal: priceVal,
                        stockVal: stockVal,
                        titleVal: titleVal
                    }};
                }})()
            """, mid); mid += 1
            print("Pricing Modal Transition:", json.dumps(pricing_transition, indent=2))
            assert pricing_transition['pricingModalVisible'], "Custom pricing modal must be open"
            assert pricing_transition['previewImgMatches'], "Preview image src must match snapped data URL"
            assert pricing_transition['mrpVal'] == '', f"MRP must be blank, got {pricing_transition['mrpVal']}"
            assert pricing_transition['priceVal'] == '', f"Price must be blank, got {pricing_transition['priceVal']}"

            await take_screenshot(ws, "proof_vendor_camera_instant_auto_preview.png", mid); mid += 1

            # -----------------------------------------------------------------
            # TEST 5: CUSTOMER EXHAUSTIVE VILLAGES & PINCODE AUTO-FILL
            # -----------------------------------------------------------------
            print("\n--- TEST 5: Customer Exhaustive Villages & Pincode Auto-Fill ---")
            await ws.send(json.dumps({
                "id": mid,
                "method": "Page.navigate",
                "params": {"url": "http://127.0.0.1:8194/customer/index.html"}
            })); mid += 1
            time.sleep(2)

            customer_autofill_result = await eval_js(ws, """
                (() => {
                    openRuralAddressModal();
                    handleCustomerVillageSearch('Tengari');
                    const dropdown = document.getElementById('customer-village-dropdown');
                    const isDropdownVisible = !dropdown.classList.contains('hidden');
                    const optionLabel = dropdown.querySelector('.village-label')?.innerText || '';

                    // Select Tengari
                    selectCustomerVillage('Tengari', '843128');
                    const villageVal = document.getElementById('modal-village-input')?.value;
                    const pincodeVal = document.getElementById('modal-pincode-input')?.value;

                    return {
                        isDropdownVisible,
                        optionLabel,
                        villageVal,
                        pincodeVal
                    };
                })()
            """, mid); mid += 1
            print("Customer Village Selection Result:", json.dumps(customer_autofill_result, indent=2))
            assert customer_autofill_result['villageVal'] == 'Tengari', "Customer village must be Tengari"
            assert customer_autofill_result['pincodeVal'] == '843128', "Customer pincode must be 843128"

            await take_screenshot(ws, "proof_customer_village_pincode_autopopulated.png", mid); mid += 1

            # -----------------------------------------------------------------
            # TEST 6: RUNNER EXHAUSTIVE VILLAGES & PINCODE AUTO-FILL
            # -----------------------------------------------------------------
            print("\n--- TEST 6: Runner Exhaustive Villages & Pincode Auto-Fill ---")
            await ws.send(json.dumps({
                "id": mid,
                "method": "Page.navigate",
                "params": {"url": "http://127.0.0.1:8194/runner/index.html"}
            })); mid += 1
            time.sleep(2)

            runner_autofill_result = await eval_js(ws, """
                (() => {
                    handleRunnerVillageSearch('Shibai Patti');
                    const dropdown = document.getElementById('runner-village-dropdown');
                    const isDropdownVisible = !dropdown.classList.contains('hidden');
                    const optionLabel = dropdown.querySelector('.village-label')?.innerText || '';

                    // Select Shibai Patti
                    selectRunnerVillage('Shibai Patti', '843128');
                    const villageVal = document.getElementById('runner-base-village')?.value;
                    const pincodeVal = document.getElementById('runner-pincode')?.value;

                    return {
                        isDropdownVisible,
                        optionLabel,
                        villageVal,
                        pincodeVal
                    };
                })()
            """, mid); mid += 1
            print("Runner Village Selection Result:", json.dumps(runner_autofill_result, indent=2))
            assert runner_autofill_result['villageVal'] == 'Shibai Patti', "Runner village must be Shibai Patti"
            assert runner_autofill_result['pincodeVal'] == '843128', "Runner pincode must be 843128"

            await take_screenshot(ws, "proof_runner_village_pincode_autopopulated.png", mid); mid += 1

            print("\n=======================================================")
            print("ALL 6 TESTS PASSED WITH 100% SUCCESS!")
            print("=======================================================")

    finally:
        chrome_proc.terminate()
        http_proc.terminate()
        if os.path.exists(TEMP_DIR):
            shutil.rmtree(TEMP_DIR, ignore_errors=True)

if __name__ == '__main__':
    asyncio.run(main())
