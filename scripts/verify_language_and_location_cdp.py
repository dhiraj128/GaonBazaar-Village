import asyncio
import os
import sys
import json
import time
import subprocess
import urllib.request
import base64
import websockets

sys.stdout.reconfigure(encoding='utf-8')

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
TEMP_DIR = r"C:\Users\dhira\AppData\Local\Temp\chrome_lang_loc_test"
ARTIFACT_DIR = r"C:\Users\dhira\OneDrive\Desktop\GaoBazar-Village"
BRAIN_DIR = r"C:\Users\dhira\.gemini\antigravity\brain\918c8085-b60b-40a9-a077-a3344458bcc5"

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
            return resp.get("result", {}).get("result", {}).get("value")

async def take_screenshot(ws, filename, msg_id):
    await ws.send(json.dumps({"id": msg_id, "method": "Page.captureScreenshot", "params": {"format": "png"}}))
    while True:
        raw = await ws.recv()
        resp = json.loads(raw)
        if resp.get("id") == msg_id:
            b64 = resp["result"]["data"]
            for d in [ARTIFACT_DIR, BRAIN_DIR]:
                out_path = os.path.join(d, filename)
                with open(out_path, "wb") as f:
                    f.write(base64.b64decode(b64))
            print(f"Captured screenshot: {filename}")
            return

async def run_tests():
    http_proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", "8097", "--directory", "public_web"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    time.sleep(1)

    chrome_proc = subprocess.Popen([
        CHROME_PATH,
        "--headless=new",
        "--remote-debugging-port=8098",
        f"--user-data-dir={TEMP_DIR}",
        "--window-size=412,915",
        "http://127.0.0.1:8097/customer/index.html"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)

    try:
        targets_raw = urllib.request.urlopen("http://127.0.0.1:8098/json").read()
        targets = json.loads(targets_raw.decode('utf-8'))
        page_target = next(t for t in targets if t.get("type") == "page")
        ws_url = page_target["webSocketDebuggerUrl"]

        async with websockets.connect(ws_url) as ws:
            mid = 1
            await ws.send(json.dumps({"id": mid, "method": "Page.enable"})); mid += 1
            await ws.recv()

            # ----------------------------------------------------
            # 1. TEST CUSTOMER LANGUAGE TOGGLE
            # ----------------------------------------------------
            print("\n=== 1. Testing Customer Language Toggle ===")
            await eval_js(ws, "localStorage.clear(); sessionStorage.clear(); location.reload();", mid); mid += 1
            await asyncio.sleep(2)

            # Check initial styling: English should be active
            en_classes_1 = await eval_js(ws, "document.getElementById('lang-btn-en')?.className", mid); mid += 1
            hi_classes_1 = await eval_js(ws, "document.getElementById('lang-btn-hi')?.className", mid); mid += 1
            en_has_check_1 = await eval_js(ws, "document.getElementById('check-icon-en')?.innerHTML.includes('svg') || document.getElementById('check-icon-en')?.innerHTML.includes('check')", mid); mid += 1
            hi_has_check_1 = await eval_js(ws, "document.getElementById('check-icon-hi')?.innerHTML.includes('svg') || document.getElementById('check-icon-hi')?.innerHTML.includes('check')", mid); mid += 1

            print(f"Customer Initial - EN active: {'border-emerald-600' in en_classes_1}, EN checkmark: {en_has_check_1}")
            print(f"Customer Initial - HI active: {'border-emerald-600' in hi_classes_1}, HI checkmark: {hi_has_check_1}")
            assert 'border-emerald-600' in en_classes_1, "EN card should be active initially"
            assert not ('border-emerald-600' in hi_classes_1), "HI card should not be active initially"

            # Click Hindi card
            print("Clicking Hindi card...")
            await eval_js(ws, "selectLanguage('hi')", mid); mid += 1
            await asyncio.sleep(0.5)

            en_classes_2 = await eval_js(ws, "document.getElementById('lang-btn-en')?.className", mid); mid += 1
            hi_classes_2 = await eval_js(ws, "document.getElementById('lang-btn-hi')?.className", mid); mid += 1
            en_has_check_2 = await eval_js(ws, "document.getElementById('check-icon-en')?.innerHTML.includes('svg') || document.getElementById('check-icon-en')?.innerHTML.includes('check')", mid); mid += 1
            hi_has_check_2 = await eval_js(ws, "document.getElementById('check-icon-hi')?.innerHTML.includes('svg') || document.getElementById('check-icon-hi')?.innerHTML.includes('check')", mid); mid += 1

            print(f"Customer After HI click - EN active: {'border-emerald-600' in en_classes_2}, EN checkmark: {en_has_check_2}")
            print(f"Customer After HI click - HI active: {'border-emerald-600' in hi_classes_2}, HI checkmark: {hi_has_check_2}")
            assert 'border-emerald-600' in hi_classes_2, "HI card must have green border after click!"
            assert hi_has_check_2, "HI card must have checkmark after click!"
            assert not ('border-emerald-600' in en_classes_2), "EN card must lose green border!"
            assert not en_has_check_2, "EN card must lose checkmark!"

            await take_screenshot(ws, "proof_customer_language_toggle.png", mid); mid += 1

            # Click Continue -> moves to Login
            await eval_js(ws, "proceedFromLanguage()", mid); mid += 1
            await asyncio.sleep(1)
            login_visible = await eval_js(ws, "!document.getElementById('page-login')?.classList.contains('hidden')", mid); mid += 1
            print(f"Customer Login visible after language continue: {login_visible}")
            assert login_visible, "Customer should transition to Login"

            # ----------------------------------------------------
            # 2. TEST VENDOR LANGUAGE TOGGLE & REDESIGNED LOCATION
            # ----------------------------------------------------
            print("\n=== 2. Testing Vendor Language Toggle & Redesigned Location ===")
            await eval_js(ws, "location.href = 'http://127.0.0.1:8097/vendor/index.html'", mid); mid += 1
            await asyncio.sleep(2)
            await eval_js(ws, "localStorage.clear(); sessionStorage.clear(); location.reload();", mid); mid += 1
            await asyncio.sleep(2)

            # Test Vendor Language Toggle
            v_en_classes_1 = await eval_js(ws, "document.getElementById('lang-btn-en')?.className", mid); mid += 1
            v_hi_classes_1 = await eval_js(ws, "document.getElementById('lang-btn-hi')?.className", mid); mid += 1
            print(f"Vendor Initial - EN active: {'border-emerald-600' in v_en_classes_1}, HI active: {'border-emerald-600' in v_hi_classes_1}")
            assert 'border-emerald-600' in v_en_classes_1, "Vendor EN should be active initially"

            print("Clicking Vendor Hindi card...")
            await eval_js(ws, "setLanguage('hi')", mid); mid += 1
            await asyncio.sleep(0.5)

            v_en_classes_2 = await eval_js(ws, "document.getElementById('lang-btn-en')?.className", mid); mid += 1
            v_hi_classes_2 = await eval_js(ws, "document.getElementById('lang-btn-hi')?.className", mid); mid += 1
            v_hi_check = await eval_js(ws, "document.getElementById('check-icon-hi')?.innerHTML.includes('svg') || document.getElementById('check-icon-hi')?.innerHTML.includes('check')", mid); mid += 1
            v_en_check = await eval_js(ws, "document.getElementById('check-icon-en')?.innerHTML.includes('svg') || document.getElementById('check-icon-en')?.innerHTML.includes('check')", mid); mid += 1

            print(f"Vendor After HI click - EN active: {'border-emerald-600' in v_en_classes_2}, EN checkmark: {v_en_check}")
            print(f"Vendor After HI click - HI active: {'border-emerald-600' in v_hi_classes_2}, HI checkmark: {v_hi_check}")
            assert 'border-emerald-600' in v_hi_classes_2, "Vendor HI must have green border after click!"
            assert v_hi_check, "Vendor HI must have checkmark after click!"
            assert not ('border-emerald-600' in v_en_classes_2), "Vendor EN must lose green border!"
            assert not v_en_check, "Vendor EN must lose checkmark!"

            await take_screenshot(ws, "proof_vendor_language_toggle.png", mid); mid += 1

            # Proceed to Step 2 -> Step 3 -> Step 4 (Location)
            await eval_js(ws, "navigateTo('onboarding-2')", mid); mid += 1
            await asyncio.sleep(1)
            # Verify OTP
            await eval_js(ws, "verifyMobileOTP()", mid); mid += 1
            await asyncio.sleep(1)
            # Step 3: Save Store Details & Proceed
            await eval_js(ws, "saveBasicDetailsAndProceed()", mid); mid += 1
            await asyncio.sleep(1)

            # Now on Step 4 (Shop Location Setup)
            v_step4_visible = await eval_js(ws, "!document.getElementById('screen-onboarding-4')?.classList.contains('hidden')", mid); mid += 1
            print(f"Vendor Step 4 visible: {v_step4_visible}")
            assert v_step4_visible, "Vendor should be on Step 4"

            # Check that Leaflet map and GPS button are completely GONE
            v_map_exists = await eval_js(ws, "!!document.getElementById('vendor-location-map')", mid); mid += 1
            v_gps_btn_exists = await eval_js(ws, "!!document.getElementById('btn-detect-vendor-gps')", mid); mid += 1
            print(f"Vendor Map Exists: {v_map_exists} (Expected: False)")
            print(f"Vendor GPS Button Exists: {v_gps_btn_exists} (Expected: False)")
            assert not v_map_exists, "Vendor map MUST be deleted!"
            assert not v_gps_btn_exists, "Vendor GPS button MUST be deleted!"

            # Test Searchable Village Dropdown
            v_input_val = await eval_js(ws, "document.getElementById('vendor-village-name')?.value", mid); mid += 1
            print(f"Vendor Village Input Initial Value: {v_input_val}")

            # Type 'Muz' in input
            print("Typing 'Muz' in vendor village search input...")
            await eval_js(ws, """
                const inp = document.getElementById('vendor-village-name');
                inp.value = 'Muz';
                handleVendorVillageSearch('Muz');
            """, mid); mid += 1
            await asyncio.sleep(0.5)

            v_dropdown_visible = await eval_js(ws, "!document.getElementById('vendor-village-dropdown')?.classList.contains('hidden')", mid); mid += 1
            v_dropdown_items = await eval_js(ws, "document.querySelectorAll('#vendor-village-dropdown div').length", mid); mid += 1
            v_dropdown_text = await eval_js(ws, "document.getElementById('vendor-village-dropdown')?.innerText", mid); mid += 1
            print(f"Vendor Dropdown visible: {v_dropdown_visible}, items: {v_dropdown_items}, text contains Muzaffarpur: {'Muzaffarpur' in v_dropdown_text}")
            assert v_dropdown_visible, "Vendor dropdown should be visible when searching!"
            assert 'Muzaffarpur' in v_dropdown_text, "Dropdown should contain Muzaffarpur!"

            await take_screenshot(ws, "proof_vendor_searchable_dropdown.png", mid); mid += 1

            # Select 'Muzaffarpur'
            await eval_js(ws, "selectVendorVillage('Muzaffarpur')", mid); mid += 1
            await asyncio.sleep(0.5)
            v_input_after = await eval_js(ws, "document.getElementById('vendor-village-name')?.value", mid); mid += 1
            v_dropdown_hidden = await eval_js(ws, "document.getElementById('vendor-village-dropdown')?.classList.contains('hidden')", mid); mid += 1
            print(f"Vendor Village after selection: {v_input_after}, dropdown hidden: {v_dropdown_hidden}")
            assert v_input_after == 'Muzaffarpur', "Selected village should be Muzaffarpur"
            assert v_dropdown_hidden, "Dropdown should hide after selection"

            # Click Save & Continue to KYC
            await eval_js(ws, "saveVendorLocationAndProceed()", mid); mid += 1
            await asyncio.sleep(1.5)
            v_step5_visible = await eval_js(ws, "!document.getElementById('screen-onboarding-5')?.classList.contains('hidden')", mid); mid += 1
            print(f"Vendor Step 5 (KYC) visible: {v_step5_visible}")
            assert v_step5_visible, "Vendor should transition to Step 5 (KYC)!"

            # ----------------------------------------------------
            # 3. TEST RUNNER LANGUAGE TOGGLE & REDESIGNED LOCATION
            # ----------------------------------------------------
            print("\n=== 3. Testing Runner Language Toggle & Redesigned Location ===")
            await eval_js(ws, "location.href = 'http://127.0.0.1:8097/runner/index.html'", mid); mid += 1
            await asyncio.sleep(2)
            await eval_js(ws, "localStorage.clear(); sessionStorage.clear(); location.reload();", mid); mid += 1
            await asyncio.sleep(2)

            # Test Runner Language Toggle
            r_en_classes_1 = await eval_js(ws, "document.getElementById('lang-btn-en')?.className", mid); mid += 1
            r_hi_classes_1 = await eval_js(ws, "document.getElementById('lang-btn-hi')?.className", mid); mid += 1
            print(f"Runner Initial - EN active: {'border-emerald-600' in r_en_classes_1}, HI active: {'border-emerald-600' in r_hi_classes_1}")
            assert 'border-emerald-600' in r_en_classes_1, "Runner EN should be active initially"

            print("Clicking Runner Hindi card...")
            await eval_js(ws, "setLanguage('hi')", mid); mid += 1
            await asyncio.sleep(0.5)

            r_en_classes_2 = await eval_js(ws, "document.getElementById('lang-btn-en')?.className", mid); mid += 1
            r_hi_classes_2 = await eval_js(ws, "document.getElementById('lang-btn-hi')?.className", mid); mid += 1
            r_hi_check = await eval_js(ws, "document.getElementById('check-icon-hi')?.innerHTML.includes('svg') || document.getElementById('check-icon-hi')?.innerHTML.includes('check')", mid); mid += 1
            r_en_check = await eval_js(ws, "document.getElementById('check-icon-en')?.innerHTML.includes('svg') || document.getElementById('check-icon-en')?.innerHTML.includes('check')", mid); mid += 1

            print(f"Runner After HI click - EN active: {'border-emerald-600' in r_en_classes_2}, EN checkmark: {r_en_check}")
            print(f"Runner After HI click - HI active: {'border-emerald-600' in r_hi_classes_2}, HI checkmark: {r_hi_check}")
            assert 'border-emerald-600' in r_hi_classes_2, "Runner HI must have green border after click!"
            assert r_hi_check, "Runner HI must have checkmark after click!"
            assert not ('border-emerald-600' in r_en_classes_2), "Runner EN must lose green border!"
            assert not r_en_check, "Runner EN must lose checkmark!"

            await take_screenshot(ws, "proof_runner_language_toggle.png", mid); mid += 1

            # Proceed to Step 2 -> Step 3 -> Step 4 (Location)
            await eval_js(ws, "navigateTo('onboarding-2')", mid); mid += 1
            await asyncio.sleep(1)
            # Verify OTP
            await eval_js(ws, "verifyMobileOTP()", mid); mid += 1
            await asyncio.sleep(1)
            # Step 3: Save Rider Details & Proceed
            await eval_js(ws, "saveRunnerDetailsAndProceed()", mid); mid += 1
            await asyncio.sleep(1)

            # Now on Step 4 (Service Area Setup)
            r_step4_visible = await eval_js(ws, "!document.getElementById('screen-onboarding-4')?.classList.contains('hidden')", mid); mid += 1
            print(f"Runner Step 4 visible: {r_step4_visible}")
            assert r_step4_visible, "Runner should be on Step 4"

            # Check that Leaflet map, GPS button, AND radius chips are completely GONE
            r_map_exists = await eval_js(ws, "!!document.getElementById('runner-location-map')", mid); mid += 1
            r_gps_btn_exists = await eval_js(ws, "!!document.getElementById('btn-detect-gps')", mid); mid += 1
            r_radius_chips_exist = await eval_js(ws, "document.querySelectorAll('[id^=\"radius-chip-\"]').length > 0", mid); mid += 1

            print(f"Runner Map Exists: {r_map_exists} (Expected: False)")
            print(f"Runner GPS Button Exists: {r_gps_btn_exists} (Expected: False)")
            print(f"Runner Radius Chips Exist: {r_radius_chips_exist} (Expected: False)")
            assert not r_map_exists, "Runner map MUST be deleted!"
            assert not r_gps_btn_exists, "Runner GPS button MUST be deleted!"
            assert not r_radius_chips_exist, "Runner radius chips MUST be deleted!"

            # Test Searchable Base Village Dropdown
            r_input_val = await eval_js(ws, "document.getElementById('runner-base-village')?.value", mid); mid += 1
            print(f"Runner Base Village Input Initial Value: {r_input_val}")

            # Type 'Chat' in input
            print("Typing 'Chat' in runner village search input...")
            await eval_js(ws, """
                const inp = document.getElementById('runner-base-village');
                inp.value = 'Chat';
                handleRunnerVillageSearch('Chat');
            """, mid); mid += 1
            await asyncio.sleep(0.5)

            r_dropdown_visible = await eval_js(ws, "!document.getElementById('runner-village-dropdown')?.classList.contains('hidden')", mid); mid += 1
            r_dropdown_items = await eval_js(ws, "document.querySelectorAll('#runner-village-dropdown div').length", mid); mid += 1
            r_dropdown_text = await eval_js(ws, "document.getElementById('runner-village-dropdown')?.innerText", mid); mid += 1
            print(f"Runner Dropdown visible: {r_dropdown_visible}, items: {r_dropdown_items}, text contains Chaturshi: {'Chaturshi' in r_dropdown_text}")
            assert r_dropdown_visible, "Runner dropdown should be visible when searching!"
            assert 'Chaturshi' in r_dropdown_text, "Dropdown should contain Chaturshi!"

            await take_screenshot(ws, "proof_runner_searchable_dropdown.png", mid); mid += 1

            # Select 'Chaturshi'
            await eval_js(ws, "selectRunnerVillage('Chaturshi')", mid); mid += 1
            await asyncio.sleep(0.5)
            r_input_after = await eval_js(ws, "document.getElementById('runner-base-village')?.value", mid); mid += 1
            r_dropdown_hidden = await eval_js(ws, "document.getElementById('runner-village-dropdown')?.classList.contains('hidden')", mid); mid += 1
            print(f"Runner Village after selection: {r_input_after}, dropdown hidden: {r_dropdown_hidden}")
            assert r_input_after == 'Chaturshi', "Selected village should be Chaturshi"
            assert r_dropdown_hidden, "Dropdown should hide after selection"

            # Click Save & Continue to KYC
            await eval_js(ws, "saveRunnerLocationAndProceed()", mid); mid += 1
            await asyncio.sleep(1.5)
            r_step5_visible = await eval_js(ws, "!document.getElementById('screen-onboarding-5')?.classList.contains('hidden')", mid); mid += 1
            print(f"Runner Step 5 (KYC) visible: {r_step5_visible}")
            assert r_step5_visible, "Runner should transition to Step 5 (KYC)!"

            print("\nALL LANGUAGE TOGGLE & REDESIGNED LOCATION CHECKS PASSED 100% PERFECTLY!")

    finally:
        chrome_proc.terminate()
        http_proc.terminate()

if __name__ == "__main__":
    asyncio.run(run_tests())
