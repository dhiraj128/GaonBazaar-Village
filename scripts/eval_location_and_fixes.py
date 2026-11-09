import asyncio
import os
import sys
import json
import time
import subprocess
import urllib.request
import base64
import socket
import websockets

sys.stdout.reconfigure(encoding='utf-8')

ARTIFACT_DIR = r"C:\Users\dhira\OneDrive\Desktop\GaoBazar-Village"
BRAIN_DIR = r"C:\Users\dhira\.gemini\antigravity\brain\918c8085-b60b-40a9-a077-a3344458bcc5"
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
TEMP_DIR = r"C:\Users\dhira\AppData\Local\Temp\chrome_location_eval_dyn"

def get_free_port():
    s = socket.socket()
    s.bind(('127.0.0.1', 0))
    port = s.getsockname()[1]
    s.close()
    return port

async def send_cdp(ws, method, params=None, msg_id=1):
    payload = {"id": msg_id, "method": method, "params": params or {}}
    await ws.send(json.dumps(payload))
    while True:
        resp = json.loads(await ws.recv())
        if resp.get("id") == msg_id:
            return resp

async def evaluate(ws, expr, msg_id=200):
    res = await send_cdp(ws, "Runtime.evaluate", {"expression": expr, "returnByValue": True, "awaitPromise": True}, msg_id=msg_id)
    if "exceptionDetails" in res.get("result", {}):
        print("JS EXCEPTION:", res["result"]["exceptionDetails"])
    return res.get("result", {}).get("result", {}).get("value")

async def take_screenshot(ws, filename, msg_id=100):
    res = await send_cdp(ws, "Page.captureScreenshot", {"format": "png"}, msg_id=msg_id)
    b64 = res["result"]["data"]
    for folder in [ARTIFACT_DIR, BRAIN_DIR]:
        os.makedirs(folder, exist_ok=True)
        out_path = os.path.join(folder, filename)
        with open(out_path, "wb") as f:
            f.write(base64.b64decode(b64))
    print(f"  [PROOF CAPTURED] {filename}")
    return filename

async def run_evaluation():
    http_port = get_free_port()
    cdp_port = get_free_port()
    http_proc = None
    chrome_proc = None

    try:
        print(f"Starting HTTP server on port {http_port}")
        http_proc = subprocess.Popen(
            [sys.executable, "-m", "http.server", str(http_port), "--directory", "public_web"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        # Wait for HTTP server to respond
        for _ in range(10):
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{http_port}/runner/index.html", timeout=1) as r:
                    if r.status == 200:
                        print("HTTP server is responsive!")
                        break
            except Exception:
                time.sleep(0.5)

        os.makedirs(TEMP_DIR, exist_ok=True)
        chrome_cmd = [
            CHROME_PATH,
            f"--remote-debugging-port={cdp_port}",
            f"--user-data-dir={TEMP_DIR}",
            "--headless=new",
            "--disable-gpu",
            "--no-first-run",
            "--no-default-browser-check",
            "--window-size=430,932",
            f"http://127.0.0.1:{http_port}/runner/index.html"
        ]
        chrome_proc = subprocess.Popen(chrome_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(2)

        req = urllib.request.urlopen(f"http://127.0.0.1:{cdp_port}/json", timeout=5)
        pages = json.loads(req.read().decode())
        ws_url = None
        for p in pages:
            if p.get("type") == "page" and "http" in p.get("url", ""):
                ws_url = p.get("webSocketDebuggerUrl")
                break
        if not ws_url:
            ws_url = pages[0].get("webSocketDebuggerUrl")

        print("Connected to Chrome CDP:", ws_url)
        async with websockets.connect(ws_url, max_size=25*1024*1024) as ws:
            await send_cdp(ws, "Page.enable", msg_id=1)
            await send_cdp(ws, "DOM.enable", msg_id=2)
            await send_cdp(ws, "Runtime.enable", msg_id=3)
            await asyncio.sleep(1.0)

            print("\n=================================================================")
            print("1. RUNNER APP: FULL ONBOARDING FLOW & LOCATION SETUP (NO WHITE SCREEN)")
            print("=================================================================")

            # Check that initial screen is onboarding-1 and not blank
            init_check = await evaluate(ws, """
                (() => {
                    const s1 = document.getElementById('screen-onboarding-1');
                    return {
                        hasS1: s1 !== null,
                        s1Visible: s1 && !s1.classList.contains('hidden'),
                        curScreen: state.currentScreen
                    };
                })()
            """, msg_id=10)
            print("Runner Initial State:", init_check)
            assert init_check['s1Visible'], "Step 1 (Language) must be visible on launch!"

            # Step 1: Language -> Continue to Step 2
            await evaluate(ws, """
                (() => {
                    setLanguage('en');
                    navigateTo('onboarding-2');
                })()
            """, msg_id=11)
            await asyncio.sleep(0.3)
            s2_vis = await evaluate(ws, "!document.getElementById('screen-onboarding-2').classList.contains('hidden')", msg_id=12)
            assert s2_vis, "Step 2 should be visible!"
            print("  ✓ Step 1 -> Step 2 transition successful")

            # Step 2: Mobile OTP -> Verify -> Step 3
            await evaluate(ws, """
                (() => {
                    document.getElementById('runner-phone-input').value = '9876543210';
                    sendMobileOTP();
                    document.getElementById('otp-1').value = '1';
                    document.getElementById('otp-2').value = '2';
                    document.getElementById('otp-3').value = '3';
                    document.getElementById('otp-4').value = '4';
                    verifyMobileOTP();
                })()
            """, msg_id=13)
            await asyncio.sleep(1.0)
            s3_vis = await evaluate(ws, "!document.getElementById('screen-onboarding-3').classList.contains('hidden')", msg_id=14)
            assert s3_vis, "Step 3 should be visible!"
            print("  ✓ Step 2 -> Step 3 transition successful")

            # Step 3: Rider Details -> Continue -> Step 4
            await evaluate(ws, """
                (() => {
                    document.getElementById('runner-fullname').value = 'Sonu Kumar Verma';
                    document.getElementById('runner-vehicletype').value = 'Motorcycle (Petrol Bike)';
                    document.getElementById('runner-vehicleno').value = 'UP 32 BK 4821';
                    document.getElementById('runner-emergency').value = '9811445566';
                    saveRunnerDetailsAndProceed();
                })()
            """, msg_id=15)
            await asyncio.sleep(0.3)
            s4_vis = await evaluate(ws, "!document.getElementById('screen-onboarding-4').classList.contains('hidden')", msg_id=16)
            assert s4_vis, "Step 4 should be visible!"
            print("  ✓ Step 3 -> Step 4 transition successful")

            # Step 4: Verify PAN -> Button says Continue to Location Setup
            btn_text = await evaluate(ws, """
                (async () => {
                    document.getElementById('kyc-pan-input').value = 'ABCDE1234F';
                    await submitPanVerification();
                    const span = document.querySelector('#pan-verified-section button span');
                    return span ? span.innerText.trim() : '';
                })()
            """, msg_id=17)
            print("  PAN verified button text:", btn_text)
            assert "Location" in btn_text or "स्थान" in btn_text, "Button must direct to Location Setup!"

            # Proceed to Step 5: Location Setup
            await evaluate(ws, "proceedToNextStep()", msg_id=18)
            await asyncio.sleep(0.3)

            s5_check = await evaluate(ws, """
                (() => {
                    const s5 = document.getElementById('screen-onboarding-5');
                    const isVisible = s5 && !s5.classList.contains('hidden');
                    const villageVal = document.getElementById('runner-base-village')?.value;
                    const radiusBtn = document.getElementById('radius-chip-8');
                    const gpsDisp = document.getElementById('runner-gps-display')?.innerText;
                    return { isVisible, villageVal, hasRadiusBtn: radiusBtn !== null, gpsDisp };
                })()
            """, msg_id=19)

            print("Runner Step 5 (Location Setup) State:", s5_check)
            assert s5_check['isVisible'], "Screen-onboarding-5 must be visible!"
            assert s5_check['hasRadiusBtn'], "Radius selection chips must be present!"
            print("  ✓ Step 5 (Delivery Radius & Hub Location) restored and fully functional!")

            # Capture Screenshot: Runner Location Setup Step 5
            await take_screenshot(ws, "proof_runner_location_setup_step5.png", msg_id=20)

            # Save Location -> Proceed to Step 6: Payout Setup
            await evaluate(ws, """
                (async () => {
                    selectRadius(8);
                    await saveRunnerLocationAndProceed();
                })()
            """, msg_id=21)
            await asyncio.sleep(0.3)
            s6_vis = await evaluate(ws, "!document.getElementById('screen-onboarding-6').classList.contains('hidden')", msg_id=22)
            assert s6_vis, "Step 6 (Payout Setup) must be visible!"
            print("  ✓ Step 5 -> Step 6 transition successful")

            # Step 6: Submit Payout -> Step 7: Under Review
            await evaluate(ws, """
                (async () => {
                    switchPayoutMode('upi');
                    document.getElementById('upi-vpa').value = 'sonu@okaxis';
                    await submitPayoutDetails();
                })()
            """, msg_id=23)
            await asyncio.sleep(0.3)
            s7_check = await evaluate(ws, """
                (() => {
                    const s7 = document.getElementById('screen-onboarding-7');
                    const isVisible = s7 && !s7.classList.contains('hidden');
                    const text = s7.innerText;
                    const hasDigiLocker = text.toLowerCase().includes('digilocker');
                    const hasOcr = text.toLowerCase().includes('ocr');
                    const hasPennyDrop = text.includes('₹1 Penny Drop');
                    return { isVisible, hasDigiLocker, hasOcr, hasPennyDrop };
                })()
            """, msg_id=24)
            print("Runner Step 7 (Under Review) State:", s7_check)
            assert s7_check['isVisible'], "Step 7 must be visible!"
            assert not s7_check['hasDigiLocker'], "Runner review screen must NOT have DigiLocker!"
            assert not s7_check['hasOcr'], "Runner review screen must NOT have OCR!"
            assert s7_check['hasPennyDrop'], "Runner review screen must display ₹1 Penny Drop Verification!"
            print("  ✓ Runner review screen verified with ₹1 Penny Drop Verification and zero obsolete text!")

            # Capture Screenshot: Runner Review Screen
            await take_screenshot(ws, "proof_runner_review_screen.png", msg_id=25)

            print("\n=================================================================")
            print("2. VENDOR APP: RESTORE LOCATION SETUP & CLEAN UNDER REVIEW SCREEN")
            print("=================================================================")

            # Navigate to Vendor
            await send_cdp(ws, "Page.navigate", {"url": f"http://127.0.0.1:{http_port}/vendor/index.html#onboarding-4"}, msg_id=30)
            await asyncio.sleep(1.0)

            # Vendor Step 4: Verify PAN -> Continue to Location Setup
            await evaluate(ws, """
                (async () => {
                    localStorage.setItem('gb_user_phone', '9876543210');
                    localStorage.setItem('gb_vendor_phone', '9876543210');
                    navigateTo('onboarding-4');
                    document.getElementById('kyc-pan-input').value = 'ABCDE1234F';
                    await submitPanVerification();
                    proceedToNextStep();
                })()
            """, msg_id=31)
            await asyncio.sleep(0.5)

            vendor_s5 = await evaluate(ws, """
                (() => {
                    const s5 = document.getElementById('screen-onboarding-5');
                    const isVisible = s5 && !s5.classList.contains('hidden');
                    const addressVal = document.getElementById('vendor-shop-address')?.value;
                    const villageVal = document.getElementById('vendor-village-name')?.value;
                    const pincodeVal = document.getElementById('vendor-pincode')?.value;
                    return { isVisible, addressVal, villageVal, pincodeVal };
                })()
            """, msg_id=32)
            print("Vendor Step 5 (Shop Location Setup) State:", vendor_s5)
            assert vendor_s5['isVisible'], "Vendor Screen 5 must be visible!"
            assert vendor_s5['addressVal'] and vendor_s5['villageVal'], "Shop address and village must be present!"
            print("  ✓ Vendor Shop Location Setup step restored and verified!")

            # Capture Screenshot: Vendor Location Setup Step 5
            await take_screenshot(ws, "proof_vendor_location_setup_step5.png", msg_id=33)

            # Vendor Step 5 -> Step 6 -> Step 7
            await evaluate(ws, """
                (async () => {
                    await saveVendorLocationAndProceed();
                    switchPayoutMode('upi');
                    document.getElementById('upi-vpa').value = 'ramesh@upi';
                    await submitPayoutDetails();
                })()
            """, msg_id=34)
            await asyncio.sleep(0.5)

            vendor_s7 = await evaluate(ws, """
                (() => {
                    const s7 = document.getElementById('screen-onboarding-7');
                    const isVisible = s7 && !s7.classList.contains('hidden');
                    const text = s7 ? s7.innerText : '';
                    const hasDigiLocker = text.toLowerCase().includes('digilocker');
                    const hasOcr = text.toLowerCase().includes('ocr');
                    const hasPennyDrop = text.includes('₹1 Penny Drop');
                    const badgeText = document.getElementById('vendor-penny-drop-badge')?.innerText;
                    return { isVisible, hasDigiLocker, hasOcr, hasPennyDrop, badgeText };
                })()
            """, msg_id=35)
            print("Vendor Step 7 (Under Review) State:", vendor_s7)
            assert vendor_s7['isVisible'], "Vendor Screen 7 must be visible!"
            assert not vendor_s7['hasDigiLocker'], "DigiLocker MUST be completely removed!"
            assert not vendor_s7['hasOcr'], "OCR MUST be completely removed!"
            assert vendor_s7['hasPennyDrop'], "₹1 Penny Drop Bank Verification must be present!"
            print("  ✓ Vendor review screen cleaned: Zero DigiLocker/OCR, ₹1 Penny Drop active!")

            # Capture Screenshot: Vendor Review Screen
            await take_screenshot(ws, "proof_vendor_review_penny_drop.png", msg_id=36)

            print("\n=================================================================")
            print("3. CUSTOMER APP: ACTIVATE ONLINE UPI/QR & CLEAN COD UI")
            print("=================================================================")

            # Navigate to Customer App
            await send_cdp(ws, "Page.navigate", {"url": f"http://127.0.0.1:{http_port}/customer/index.html"}, msg_id=40)
            await asyncio.sleep(1.0)

            # Open Payment Settings Modal
            await evaluate(ws, """
                (() => {
                    openModal('modal-payment-settings');
                })()
            """, msg_id=41)
            await asyncio.sleep(0.5)

            cust_pay = await evaluate(ws, """
                (() => {
                    const modal = document.getElementById('modal-payment-settings');
                    const text = modal ? modal.innerText : '';
                    const hasComingSoon = text.includes('Coming Soon');
                    const hasActiveBadge = text.includes('Active');
                    const hasCod = text.includes('Cash on Delivery (COD)');
                    const hasUpi = text.includes('Online UPI / QR Payment');
                    return {
                        hasComingSoon,
                        hasActiveBadge,
                        hasCod,
                        hasUpi
                    };
                })()
            """, msg_id=42)
            print("Customer Payment Settings State:", cust_pay)
            assert not cust_pay['hasComingSoon'], "Coming Soon badge MUST be removed!"
            assert cust_pay['hasActiveBadge'], "Online UPI must have Active badge!"
            assert cust_pay['hasCod'], "COD must be present!"
            assert cust_pay['hasUpi'], "Online UPI must be present!"
            print("  ✓ Customer Payment Settings verified: Online UPI active, COD cleaned!")

            # Capture Screenshot: Customer Payment Settings Modal
            await take_screenshot(ws, "proof_customer_payment_settings_active.png", msg_id=43)

    finally:
        if chrome_proc:
            chrome_proc.terminate()
        if http_proc:
            http_proc.terminate()

if __name__ == '__main__':
    asyncio.run(run_evaluation())
