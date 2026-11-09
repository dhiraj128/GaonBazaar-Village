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

ARTIFACT_DIR = r"C:\Users\dhira\OneDrive\Desktop\GaoBazar-Village"
BRAIN_DIR = r"C:\Users\dhira\.gemini\antigravity\brain\918c8085-b60b-40a9-a077-a3344458bcc5"
PORT = 8097
CDP_PORT = 9235
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
TEMP_DIR = r"C:\Users\dhira\AppData\Local\Temp\chrome_paperless_eval"

async def send_cdp(ws, method, params=None, msg_id=1):
    payload = {"id": msg_id, "method": method, "params": params or {}}
    await ws.send(json.dumps(payload))
    while True:
        resp = json.loads(await ws.recv())
        if resp.get("id") == msg_id:
            return resp

async def evaluate(ws, expr, msg_id=200):
    res = await send_cdp(ws, "Runtime.evaluate", {"expression": expr, "returnByValue": True, "awaitPromise": True}, msg_id=msg_id)
    return res.get("result", {}).get("result", {}).get("value")

async def take_screenshot(ws, filename, msg_id=100):
    res = await send_cdp(ws, "Page.captureScreenshot", {"format": "png"}, msg_id=msg_id)
    b64 = res["result"]["data"]
    for folder in [ARTIFACT_DIR, BRAIN_DIR]:
        os.makedirs(folder, exist_ok=True)
        out_path = os.path.join(folder, filename)
        with open(out_path, "wb") as f:
            f.write(base64.b64decode(b64))
    print(f"  [PROOF] Captured & Saved: {filename}")
    return filename

async def run_paperless_eval():
    http_proc = None
    chrome_proc = None
    try:
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{PORT}/runner/index.html", timeout=1)
            print("Using existing HTTP server on port", PORT)
        except Exception:
            print("Starting HTTP server on port", PORT)
            http_proc = subprocess.Popen(
                [sys.executable, "-m", "http.server", str(PORT), "--directory", "public_web"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            time.sleep(1)

        os.makedirs(TEMP_DIR, exist_ok=True)
        chrome_cmd = [
            CHROME_PATH,
            f"--remote-debugging-port={CDP_PORT}",
            f"--user-data-dir={TEMP_DIR}",
            "--headless=new",
            "--disable-gpu",
            "--no-first-run",
            "--no-default-browser-check",
            "--window-size=430,932",
            f"http://127.0.0.1:{PORT}/runner/index.html#onboarding-3"
        ]
        chrome_proc = subprocess.Popen(chrome_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(2)

        req = urllib.request.urlopen(f"http://127.0.0.1:{CDP_PORT}/json", timeout=5)
        pages = json.loads(req.read().decode())
        ws_url = None
        for p in pages:
            if p.get("type") == "page" and "http" in p.get("url", ""):
                ws_url = p.get("webSocketDebuggerUrl")
                break
        if not ws_url:
            ws_url = pages[0].get("webSocketDebuggerUrl")

        print("Connecting to Chrome CDP at:", ws_url)
        async with websockets.connect(ws_url, max_size=25*1024*1024) as ws:
            await send_cdp(ws, "Page.enable", msg_id=1)
            await send_cdp(ws, "DOM.enable", msg_id=2)
            await send_cdp(ws, "Runtime.enable", msg_id=3)

            print("\n=======================================================")
            print("TEST 1: FIX RUNNER APP BLOCKAGE (STEP 3 -> STEP 4)")
            print("=======================================================")

            # Setup test runner persona on Screen 3
            await evaluate(ws, """
                (() => {
                    localStorage.setItem('gb_user_phone', '9876543210');
                    localStorage.setItem('gb_runner_phone', '9876543210');
                    navigateTo('onboarding-3');
                    document.getElementById('runner-fullname').value = 'Sonu Kumar Verma';
                    document.getElementById('runner-vehicletype').value = 'Motorcycle (Petrol Bike)';
                    document.getElementById('runner-vehicleno').value = 'UP 32 BK 4821';
                    document.getElementById('runner-emergency').value = '9811445566';
                })()
            """, msg_id=10)
            await asyncio.sleep(0.5)

            # Capture Screen 3 input state before transition
            await take_screenshot(ws, "proof_runner_step3_details_saved.png", msg_id=11)

            # Click Continue (saveRunnerDetailsAndProceed)
            transition_res = await evaluate(ws, """
                (() => {
                    saveRunnerDetailsAndProceed();
                    const s3 = document.getElementById('screen-onboarding-3');
                    const s4 = document.getElementById('screen-onboarding-4');
                    return {
                        s3Hidden: s3.classList.contains('hidden'),
                        s4Visible: !s4.classList.contains('hidden'),
                        savedName: localStorage.getItem('gb_runner_name'),
                        savedVehNo: localStorage.getItem('gb_runner_vehicle_no'),
                        savedEmerg: localStorage.getItem('gb_runner_emergency')
                    };
                })()
            """, msg_id=12)
            print("  Step 3 Transition Result:", transition_res)
            assert transition_res['s3Hidden'], "Screen 3 should be hidden!"
            assert transition_res['s4Visible'], "Screen 4 should be visible after clicking Continue!"
            assert transition_res['savedVehNo'] == 'UP 32 BK 4821', "Vehicle number not saved to storage!"
            print("  ✓ Step 3 unblocked and successfully transitioned to Step 4!")

            print("\n=======================================================")
            print("TEST 2: VERIFY ZERO CAMERA BOXES & PAPERLESS KYC (STEP 4)")
            print("=======================================================")

            camera_check = await evaluate(ws, """
                (() => {
                    const s4 = document.getElementById('screen-onboarding-4');
                    const hasVideo = s4.querySelector('video') !== null;
                    const hasCanvas = s4.querySelector('canvas') !== null;
                    const hasPanInput = document.getElementById('kyc-pan-input') !== null;
                    const hasAadhaarInput = document.getElementById('kyc-aadhaar-input') !== null;
                    const hasPanBtn = document.getElementById('btn-verify-pan') !== null;
                    const hasAadhaarBtn = document.getElementById('btn-send-aadhaar-otp') !== null;
                    return {
                        hasVideo,
                        hasCanvas,
                        hasPanInput,
                        hasAadhaarInput,
                        hasPanBtn,
                        hasAadhaarBtn
                    };
                })()
            """, msg_id=20)
            print("  Paperless KYC DOM Audit:", camera_check)
            assert not camera_check['hasVideo'], "ERROR: Physical camera video element still present in Step 4!"
            assert not camera_check['hasCanvas'], "ERROR: Camera canvas element still present in Step 4!"
            assert camera_check['hasPanInput'] and camera_check['hasAadhaarInput'], "Missing PAN/Aadhaar inputs!"

            # Capture initial Step 4 Paperless KYC Screen
            await take_screenshot(ws, "proof_runner_step4_cashfree_paperless_kyc.png", msg_id=21)

            # Verify PAN via Cashfree
            await evaluate(ws, """
                document.getElementById('kyc-pan-input').value = 'ABCDE1234F';
                submitPanVerification();
            """, msg_id=22)
            await asyncio.sleep(1.0)

            pan_state = await evaluate(ws, """
                (() => {
                    const panSec = document.getElementById('pan-verified-section');
                    const badge = document.getElementById('pan-status-badge');
                    return {
                        panVerified: !panSec.classList.contains('hidden'),
                        badgeText: badge ? badge.innerText : ''
                    };
                })()
            """, msg_id=23)
            print("  PAN Verification State:", pan_state)
            assert pan_state['panVerified'], "PAN verified section not shown!"

            # Request Aadhaar OTP
            await evaluate(ws, """
                document.getElementById('kyc-aadhaar-input').value = '5489 1204 9012';
                submitAadhaarOtpRequest();
            """, msg_id=24)
            await asyncio.sleep(1.0)

            # Submit Aadhaar OTP & Complete KYC
            await evaluate(ws, """
                document.getElementById('kyc-aadhaar-otp-input').value = '123456';
                submitAadhaarVerification();
            """, msg_id=25)
            await asyncio.sleep(1.5)

            kyc_final = await evaluate(ws, """
                (() => {
                    const aadhaarSec = document.getElementById('aadhaar-verified-section');
                    const completionCard = document.getElementById('kyc-completion-card');
                    return {
                        aadhaarVerified: !aadhaarSec.classList.contains('hidden'),
                        completionVisible: !completionCard.classList.contains('hidden'),
                        isKycStored: localStorage.getItem('gb_kyc_verified') === 'true'
                    };
                })()
            """, msg_id=26)
            print("  KYC Final Completion State:", kyc_final)
            assert kyc_final['aadhaarVerified'], "Aadhaar verified section not shown!"
            assert kyc_final['completionVisible'], "KYC completion card not shown!"
            assert kyc_final['isKycStored'], "KYC status not saved to localStorage!"

            # Capture completed Paperless KYC Screen
            await take_screenshot(ws, "proof_runner_step4_kyc_completed.png", msg_id=27)

            # Click Continue to Liveness
            await evaluate(ws, "completeKycAndProceed();", msg_id=28)
            await asyncio.sleep(0.5)

            s5_check = await evaluate(ws, "!document.getElementById('screen-onboarding-5').classList.contains('hidden')", msg_id=29)
            assert s5_check, "Did not navigate to Screen 5 (Face Liveness)!"
            print("  ✓ Paperless KYC completed and navigated to Screen 5!")

            print("\n=======================================================")
            print("TEST 3: CROSS-APP AUTH PERSISTENCE (VENDOR APP RESTORE)")
            print("=======================================================")

            # Navigate to Vendor App
            await send_cdp(ws, "Page.navigate", {"url": f"http://127.0.0.1:{PORT}/vendor/index.html#onboarding-2"}, msg_id=30)
            await asyncio.sleep(2.0)

            vendor_auth_check = await evaluate(ws, """
                (() => {
                    const phoneInput = document.getElementById('vendor-phone-input');
                    const savedUserPhone = localStorage.getItem('gb_user_phone');
                    return {
                        savedUserPhone,
                        inputPrefilledValue: phoneInput ? phoneInput.value : '',
                        isMatching: phoneInput ? phoneInput.value === savedUserPhone : false
                    };
                })()
            """, msg_id=31)
            print("  Vendor Cross-App Auth Check:", vendor_auth_check)
            assert vendor_auth_check['savedUserPhone'] == '9876543210', "Saved phone mismatch!"
            assert vendor_auth_check['inputPrefilledValue'] == '9876543210', "Vendor phone input not prefilled from cross-app session!"
            print("  ✓ Cross-App Auth persistence validated: 9876543210 restored in Vendor app!")

            await take_screenshot(ws, "proof_cross_app_auth_persistence.png", msg_id=32)

            print("\n=======================================================")
            print("ALL FIXES VERIFIED AND VALIDATED 100% SUCCESFULLY!")
            print("=======================================================")

    finally:
        if chrome_proc:
            chrome_proc.terminate()
            chrome_proc.wait()
        if http_proc:
            http_proc.terminate()
            http_proc.wait()

if __name__ == "__main__":
    asyncio.run(run_paperless_eval())
