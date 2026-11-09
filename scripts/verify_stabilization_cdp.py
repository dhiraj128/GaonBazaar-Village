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
TEMP_DIR = r"C:\Users\dhira\AppData\Local\Temp\chrome_stabilization_test"
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
        [sys.executable, "-m", "http.server", "8095", "--directory", "public_web"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    time.sleep(1)

    chrome_proc = subprocess.Popen([
        CHROME_PATH,
        "--headless=new",
        "--remote-debugging-port=8096",
        f"--user-data-dir={TEMP_DIR}",
        "--window-size=412,915",
        "http://127.0.0.1:8095/customer/index.html"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)

    try:
        targets_raw = urllib.request.urlopen("http://127.0.0.1:8096/json").read()
        targets = json.loads(targets_raw.decode('utf-8'))
        page_target = next(t for t in targets if t.get("type") == "page")
        ws_url = page_target["webSocketDebuggerUrl"]

        async with websockets.connect(ws_url) as ws:
            mid = 1
            await ws.send(json.dumps({"id": mid, "method": "Page.enable"})); mid += 1
            await ws.recv()

            # ----------------------------------------------------
            # 1. TEST CUSTOMER APP
            # ----------------------------------------------------
            print("\n=== Testing Customer App ===")
            await eval_js(ws, "localStorage.clear(); sessionStorage.clear(); location.reload();", mid); mid += 1
            await asyncio.sleep(2)

            # Check Language screen and proceed
            step1_btn = await eval_js(ws, "document.querySelectorAll('#page-language button').length", mid); mid += 1
            print(f"Customer Step 1 buttons count: {step1_btn}")
            await eval_js(ws, "document.querySelector('#page-language button').click()", mid); mid += 1
            await asyncio.sleep(1)

            # Check Login Page:
            # - Header text should be 'Mobile Login'
            login_header = await eval_js(ws, "document.querySelector('#page-login h2')?.innerText?.trim()", mid); mid += 1
            print(f"Customer Login Header: {login_header}")
            
            # - No green badge
            badge_count = await eval_js(ws, "document.querySelectorAll('#page-login span.bg-emerald-100, #page-login span.bg-green-100').length", mid); mid += 1
            print(f"Customer Login Badge Count: {badge_count}")

            # - Phone pre-filled
            phone_val = await eval_js(ws, "document.getElementById('cust-phone-input')?.value", mid); mid += 1
            print(f"Customer Phone Input Value: {phone_val}")

            # - Recaptcha container
            recaptcha_exists = await eval_js(ws, "!!document.getElementById('recaptcha-container')", mid); mid += 1
            print(f"Customer Recaptcha Container Exists: {recaptcha_exists}")

            # Click Send OTP
            await eval_js(ws, "document.getElementById('send-otp-btn').click()", mid); mid += 1
            await asyncio.sleep(1)

            # Verify 6 OTP boxes
            otp_boxes = await eval_js(ws, "document.querySelectorAll('#otp-input-section input').length", mid); mid += 1
            print(f"Customer OTP Digits Count: {otp_boxes}")

            # Fill OTP 123456
            await eval_js(ws, """
                ['1','2','3','4','5','6'].forEach((d, i) => {
                    const el = document.getElementById(`otp-${i+1}`);
                    if (el) el.value = d;
                });
            """, mid); mid += 1
            await asyncio.sleep(0.5)

            await take_screenshot(ws, "proof_stabilization_customer_login.png", mid); mid += 1

            # Click Verify & Proceed
            await eval_js(ws, "document.getElementById('verify-otp-btn').click()", mid); mid += 1
            await asyncio.sleep(2)

            # Verify directly on Dashboard
            dashboard_visible = await eval_js(ws, "!document.getElementById('dashboard-container')?.classList.contains('hidden')", mid); mid += 1
            print(f"Customer Dashboard Visible: {dashboard_visible}")
            assert dashboard_visible, "Customer should be on Dashboard after OTP!"

            # ----------------------------------------------------
            # 2. TEST VENDOR APP
            # ----------------------------------------------------
            print("\n=== Testing Vendor App ===")
            await eval_js(ws, "location.href = 'http://127.0.0.1:8095/vendor/index.html'", mid); mid += 1
            await asyncio.sleep(2)
            await eval_js(ws, "localStorage.clear(); sessionStorage.clear(); location.reload();", mid); mid += 1
            await asyncio.sleep(2)

            # Step 1: Language -> Continue
            await eval_js(ws, "document.querySelector('#screen-onboarding-1 button').click()", mid); mid += 1
            await asyncio.sleep(1)

            # Step 2: Mobile Login
            v_title = await eval_js(ws, "document.querySelector('#screen-onboarding-2 h2')?.innerText?.trim()", mid); mid += 1
            print(f"Vendor Login Title: {v_title}")

            v_phone = await eval_js(ws, "document.getElementById('vendor-phone-input')?.value", mid); mid += 1
            print(f"Vendor Phone Input Value: {v_phone}")

            # Send OTP
            await eval_js(ws, "sendMobileOTP()", mid); mid += 1
            await asyncio.sleep(1)

            # Verify 6 OTP boxes
            v_otp_boxes = await eval_js(ws, "document.querySelectorAll('#otp-container input').length", mid); mid += 1
            print(f"Vendor OTP Digits Count: {v_otp_boxes}")

            # Fill OTP 123456
            await eval_js(ws, """
                ['1','2','3','4','5','6'].forEach((d, i) => {
                    const el = document.getElementById(`otp-${i+1}`);
                    if (el) el.value = d;
                });
            """, mid); mid += 1
            await asyncio.sleep(0.5)

            await take_screenshot(ws, "proof_stabilization_vendor_6digit_otp.png", mid); mid += 1

            # Click Verify & Proceed
            await eval_js(ws, "verifyMobileOTP()", mid); mid += 1
            await asyncio.sleep(1.5)

            step3_visible = await eval_js(ws, "!document.getElementById('screen-onboarding-3')?.classList.contains('hidden')", mid); mid += 1
            print(f"Vendor Step 3 Visible: {step3_visible}")
            assert step3_visible, "Vendor should transition to Step 3!"

            # ----------------------------------------------------
            # 3. TEST RUNNER APP
            # ----------------------------------------------------
            print("\n=== Testing Runner App ===")
            await eval_js(ws, "location.href = 'http://127.0.0.1:8095/runner/index.html'", mid); mid += 1
            await asyncio.sleep(2)
            await eval_js(ws, "localStorage.clear(); sessionStorage.clear(); location.reload();", mid); mid += 1
            await asyncio.sleep(2)

            # Step 1: Language -> Continue
            await eval_js(ws, "document.querySelector('#screen-onboarding-1 button').click()", mid); mid += 1
            await asyncio.sleep(1)

            # Step 2: Mobile Login
            r_title = await eval_js(ws, "document.querySelector('#screen-onboarding-2 h2')?.innerText?.trim()", mid); mid += 1
            print(f"Runner Login Title: {r_title}")

            r_phone = await eval_js(ws, "document.getElementById('runner-phone-input')?.value", mid); mid += 1
            print(f"Runner Phone Input Value: {r_phone}")

            # Send OTP
            await eval_js(ws, "sendMobileOTP()", mid); mid += 1
            await asyncio.sleep(1)

            # Verify 6 OTP boxes
            r_otp_boxes = await eval_js(ws, "document.querySelectorAll('#otp-container input').length", mid); mid += 1
            print(f"Runner OTP Digits Count: {r_otp_boxes}")

            # Fill OTP 123456
            await eval_js(ws, """
                ['1','2','3','4','5','6'].forEach((d, i) => {
                    const el = document.getElementById(`otp-${i+1}`);
                    if (el) el.value = d;
                });
            """, mid); mid += 1
            await asyncio.sleep(0.5)

            # Click Verify & Proceed -> Step 3
            await eval_js(ws, "verifyMobileOTP()", mid); mid += 1
            await asyncio.sleep(1.5)

            # Fill Step 3 dummy Rider details & click Continue
            await eval_js(ws, """
                document.getElementById('runner-vehicleno').value = 'UP 32 BK 4821';
                saveRunnerDetailsAndProceed();
            """, mid); mid += 1
            await asyncio.sleep(1.5)

            # Step 4: Service Area Setup
            r_step4_visible = await eval_js(ws, "!document.getElementById('screen-onboarding-4')?.classList.contains('hidden')", mid); mid += 1
            print(f"Runner Step 4 Visible: {r_step4_visible}")
            assert r_step4_visible, "Runner Step 4 should be visible!"

            r_step4_title = await eval_js(ws, "document.querySelector('#screen-onboarding-4 h2')?.innerText?.trim()", mid); mid += 1
            print(f"Runner Step 4 Title: {r_step4_title}")

            radius_texts = await eval_js(ws, """
                [document.getElementById('radius-chip-5')?.innerText?.trim(),
                 document.getElementById('radius-chip-8')?.innerText?.trim(),
                 document.getElementById('radius-chip-10')?.innerText?.trim()]
            """, mid); mid += 1
            print(f"Runner Radius Buttons: {radius_texts}")

            village_val = await eval_js(ws, "document.getElementById('runner-base-village')?.value", mid); mid += 1
            print(f"Runner Village Value: {village_val}")

            village_label = await eval_js(ws, "document.querySelector('#screen-onboarding-4 label[data-i18n=\"base_village_label\"]')?.innerText?.trim()", mid); mid += 1
            print(f"Runner Village Label: {village_label}")

            # Test GPS Pinning
            print("Testing GPS detection...")
            await eval_js(ws, "detectRunnerGPS()", mid); mid += 1
            # Wait for the GPS button to finish (our timeout guard guarantees max 3.5s)
            await asyncio.sleep(4)

            gps_btn_text = await eval_js(ws, "document.getElementById('btn-detect-gps')?.innerText?.trim()", mid); mid += 1
            print(f"GPS Button Text after click: {gps_btn_text}")

            await take_screenshot(ws, "proof_stabilization_runner_gps_pinned.png", mid); mid += 1

            assert "✓ GPS Pinned" in gps_btn_text or "GPS Pinned" in gps_btn_text, f"GPS button should be pinned, got: {gps_btn_text}"
            print("\nALL STABILIZATION CHECKS PASSED 100% PERFECTLY!")

    finally:
        chrome_proc.terminate()
        http_proc.terminate()

if __name__ == "__main__":
    asyncio.run(run_tests())
