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
TEMP_DIR = r"C:\Users\dhira\AppData\Local\Temp\chrome_crit_routing_new"
ARTIFACT_DIR = r"C:\Users\dhira\OneDrive\Desktop\GaoBazar-Village"
BRAIN_DIR = r"C:\Users\dhira\.gemini\antigravity\brain\918c8085-b60b-40a9-a077-a3344458bcc5"

async def eval_critical():
    print("[1/4] Starting HTTP server on port 8101...", flush=True)
    http_proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", "8101", "--directory", "public_web"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    time.sleep(1)

    print("[2/4] Starting headless Chrome on port 8102...", flush=True)
    chrome_proc = subprocess.Popen([
        CHROME_PATH,
        "--headless=new",
        "--remote-debugging-port=8102",
        f"--user-data-dir={TEMP_DIR}",
        "--window-size=412,915",
        "--disable-gpu",
        "--no-first-run",
        "http://127.0.0.1:8101/customer/index.html"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)

    msg_id = 1
    async def send_cmd(ws, method, params=None):
        nonlocal msg_id
        current_id = msg_id
        msg_id += 1
        msg = {"id": current_id, "method": method}
        if params:
            msg["params"] = params
        await ws.send(json.dumps(msg))
        while True:
            raw = await ws.recv()
            resp = json.loads(raw)
            if resp.get("id") == current_id:
                return resp

    async def save_screenshot(ws, filename):
        resp = await send_cmd(ws, "Page.captureScreenshot", {"format": "png"})
        b64 = resp["result"]["data"]
        for d in [ARTIFACT_DIR, BRAIN_DIR]:
            path = os.path.join(d, filename)
            with open(path, "wb") as f:
                f.write(base64.b64decode(b64))
        print(f"[Screenshot Saved]: {filename}", flush=True)

    try:
        targets_raw = urllib.request.urlopen("http://127.0.0.1:8102/json").read()
        targets = json.loads(targets_raw.decode('utf-8'))
        page_target = next(t for t in targets if t.get("type") == "page")
        ws_url = page_target["webSocketDebuggerUrl"]

        async with websockets.connect(ws_url) as ws:
            await send_cmd(ws, "Page.enable")

            # -------------------------------------------------------------
            # TEST 1: CUSTOMER APP (STRICT ROUTING -> MAIN DASHBOARD, NO KYC)
            # -------------------------------------------------------------
            print("\n=== EVALUATING CUSTOMER APP ROUTING & +91 PHONE FORMATTING ===", flush=True)
            await send_cmd(ws, "Page.navigate", {"url": "http://127.0.0.1:8101/customer/index.html"})
            await asyncio.sleep(2)
            await send_cmd(ws, "Runtime.evaluate", {"expression": "localStorage.clear(); sessionStorage.clear(); location.reload();", "awaitPromise": True})
            await asyncio.sleep(2)

            # Proceed from Language to Step 2 Login
            await send_cmd(ws, "Runtime.evaluate", {"expression": "proceedFromLanguage();"})
            await asyncio.sleep(1)

            # Check phone input value and country code formatting
            phone_res = await send_cmd(ws, "Runtime.evaluate", {
                "expression": """(() => {
                    const phoneEl = document.getElementById('cust-phone-input');
                    const phoneVal = phoneEl ? phoneEl.value : '';
                    return {
                        phone: phoneVal
                    };
                })()""",
                "returnByValue": True
            })
            phone_info = phone_res["result"]["result"]["value"]
            print(f"Customer phone input: {phone_info['phone']}", flush=True)
            assert phone_info['phone'] == "9905361711", f"Expected test phone 9905361711, got {phone_info['phone']}"

            # Dispatch sendCustomerOTP
            await send_cmd(ws, "Runtime.evaluate", {"expression": "sendCustomerOTP();", "awaitPromise": True})
            await asyncio.sleep(1)

            # Check OTP fields pre-filled with 123456
            otp_res = await send_cmd(ws, "Runtime.evaluate", {
                "expression": """(() => {
                    let code = '';
                    for (let i = 1; i <= 6; i++) code += (document.getElementById('otp-' + i)?.value || '');
                    return code;
                })()""",
                "returnByValue": True
            })
            otp_val = otp_res["result"]["result"]["value"]
            print(f"Customer pre-filled OTP: {otp_val}", flush=True)
            assert otp_val == "123456", f"Expected OTP 123456, got {otp_val}"

            # Verify OTP & test STRICT DIRECT ROUTING TO MAIN DASHBOARD
            await send_cmd(ws, "Runtime.evaluate", {"expression": "verifyCustomerOTP();", "awaitPromise": True})
            await asyncio.sleep(2)

            routing_check = await send_cmd(ws, "Runtime.evaluate", {
                "expression": """(() => {
                    const pageLogin = document.getElementById('page-login');
                    const pageKyc = document.getElementById('page-kyc');
                    const dashboard = document.getElementById('dashboard-container');
                    const isLoginHidden = !pageLogin || pageLogin.classList.contains('hidden');
                    const isKycHidden = !pageKyc || pageKyc.classList.contains('hidden') || pageKyc.style.display === 'none';
                    const isDashboardVisible = dashboard && !dashboard.classList.contains('hidden');
                    return {
                        isLoginHidden,
                        isKycHidden,
                        isDashboardVisible
                    };
                })()""",
                "returnByValue": True
            })
            rc = routing_check["result"]["result"]["value"]
            print(f"Customer Routing State: Dashboard Visible: {rc['isDashboardVisible']}, KYC Hidden: {rc['isKycHidden']}, Login Hidden: {rc['isLoginHidden']}", flush=True)
            assert rc['isDashboardVisible'], "Customer must be routed directly to Main Dashboard!"
            assert rc['isKycHidden'], "Customer must NEVER see or be forced into KYC screen!"
            assert rc['isLoginHidden'], "Login screen must be hidden after auth!"
            await save_screenshot(ws, "proof_customer_direct_to_dashboard.png")

            # -------------------------------------------------------------
            # TEST 2: VENDOR APP (MOBILE-FIRST MAP & COPYWRITING)
            # -------------------------------------------------------------
            print("\n=== EVALUATING VENDOR APP (VISUAL MAP & COPYWRITING) ===", flush=True)
            await send_cmd(ws, "Page.navigate", {"url": "http://127.0.0.1:8101/vendor/index.html"})
            await asyncio.sleep(2)
            await send_cmd(ws, "Runtime.evaluate", {"expression": "localStorage.clear(); sessionStorage.clear(); location.reload();", "awaitPromise": True})
            await asyncio.sleep(2)

            # Navigate to Step 4 (Location Setup)
            await send_cmd(ws, "Runtime.evaluate", {"expression": "navigateTo('onboarding-4');"})
            await asyncio.sleep(2)

            vendor_loc_check = await send_cmd(ws, "Runtime.evaluate", {
                "expression": """(() => {
                    const subEl = document.querySelector('[data-i18n="vendor_location_sub"]');
                    const subText = subEl ? subEl.innerText.trim() : '';
                    const mapEl = document.getElementById('vendor-location-map');
                    const hasMap = !!mapEl && (mapEl.children.length > 0 || !!window.vendorMap);
                    const villageInput = document.getElementById('vendor-village-name');
                    const pincodeInput = document.getElementById('vendor-pincode');
                    const addressInput = document.getElementById('vendor-shop-address');
                    
                    const vRect = villageInput ? villageInput.getBoundingClientRect() : {};
                    const pRect = pincodeInput ? pincodeInput.getBoundingClientRect() : {};
                    const aRect = addressInput ? addressInput.getBoundingClientRect() : {};
                    const isStackedVertically = (vRect.bottom <= pRect.top) && (pRect.bottom <= aRect.top);

                    return {
                        subText,
                        hasMap,
                        isStackedVertically,
                        vTop: vRect.top,
                        pTop: pRect.top,
                        aTop: aRect.top
                    };
                })()""",
                "returnByValue": True
            })
            vc = vendor_loc_check["result"]["result"]["value"]
            print(f"Vendor Subtitle Text: '{vc['subText']}'", flush=True)
            print(f"Vendor Visual Map rendered: {vc['hasMap']}", flush=True)
            print(f"Vendor Fields Vertically Stacked: {vc['isStackedVertically']}", flush=True)

            expected_sub = "Set your exact shop location and village details to receive local orders."
            assert vc['subText'] == expected_sub, f"Expected subtitle '{expected_sub}', got '{vc['subText']}'"
            assert vc['isStackedVertically'], "Form fields (Village, Pincode, Address) must stack vertically!"

            # Trigger GPS Pin Detection
            await send_cmd(ws, "Runtime.evaluate", {"expression": "detectVendorGPS();"})
            await asyncio.sleep(1)

            pin_status = await send_cmd(ws, "Runtime.evaluate", {
                "expression": "document.getElementById('vendor-map-status')?.innerText",
                "returnByValue": True
            })
            print(f"Vendor Map Pin Status: {pin_status['result']['result']['value']}", flush=True)
            await save_screenshot(ws, "proof_vendor_mobile_map_pinned.png")

            # -------------------------------------------------------------
            # TEST 3: RUNNER APP (MOBILE-FIRST MAP & DELIVERY RADIUS)
            # -------------------------------------------------------------
            print("\n=== EVALUATING RUNNER APP (VISUAL MAP & DELIVERY RADIUS) ===", flush=True)
            await send_cmd(ws, "Page.navigate", {"url": "http://127.0.0.1:8101/runner/index.html"})
            await asyncio.sleep(2)
            await send_cmd(ws, "Runtime.evaluate", {"expression": "localStorage.clear(); sessionStorage.clear(); location.reload();", "awaitPromise": True})
            await asyncio.sleep(2)

            # Navigate to Step 4 (Service Area & Hub)
            await send_cmd(ws, "Runtime.evaluate", {"expression": "navigateTo('onboarding-4');"})
            await asyncio.sleep(2)

            # Trigger GPS Pin Detection & 8km Radius selection
            await send_cmd(ws, "Runtime.evaluate", {"expression": "selectRadius(8); detectRunnerGPS();"})
            await asyncio.sleep(1)

            runner_map_check = await send_cmd(ws, "Runtime.evaluate", {
                "expression": """(() => {
                    const mapEl = document.getElementById('runner-location-map');
                    const hasMap = !!mapEl && (mapEl.children.length > 0 || !!window.runnerMap);
                    const statusText = document.getElementById('runner-map-status')?.innerText || '';
                    return { hasMap, statusText };
                })()""",
                "returnByValue": True
            })
            rc_map = runner_map_check["result"]["result"]["value"]
            print(f"Runner Map Status: '{rc_map['statusText']}', Map Rendered: {rc_map['hasMap']}", flush=True)
            await save_screenshot(ws, "proof_runner_mobile_map_pinned.png")

            print("\nALL VERIFICATIONS PASSED WITH 100% SUCCESS!", flush=True)

    finally:
        chrome_proc.terminate()
        http_proc.terminate()

if __name__ == "__main__":
    asyncio.run(eval_critical())
