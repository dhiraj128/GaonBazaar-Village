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
PORT = 8099
CDP_PORT = 9237
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
TEMP_DIR = r"C:\Users\dhira\AppData\Local\Temp\chrome_del_face_eval"

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
    http_proc = None
    chrome_proc = None
    try:
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{PORT}/runner/index.html", timeout=1)
            print(f"HTTP server already running on port {PORT}")
        except Exception:
            print(f"Starting HTTP server on port {PORT}")
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
            f"http://127.0.0.1:{PORT}/runner/index.html#onboarding-4"
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

        print("Connected to Chrome CDP:", ws_url)
        async with websockets.connect(ws_url, max_size=25*1024*1024) as ws:
            await send_cdp(ws, "Page.enable", msg_id=1)
            await send_cdp(ws, "DOM.enable", msg_id=2)
            await send_cdp(ws, "Runtime.enable", msg_id=3)
            await asyncio.sleep(1.0)

            print("\n=================================================================")
            print("1. RUNNER APP: VERIFY FACE VERIFICATION COMPONENT IS ERADICATED")
            print("=================================================================")

            eradication_check = await evaluate(ws, """
                (() => {
                    const s5 = document.getElementById('screen-onboarding-5');
                    const video = document.getElementById('liveness-video');
                    const canvas = document.getElementById('liveness-canvas');
                    const hasFnStart = typeof startLivenessCamera !== 'undefined';
                    const hasFnCapture = typeof captureLivenessSelfie !== 'undefined';
                    return {
                        hasScreen5: s5 !== null,
                        hasVideo: video !== null,
                        hasCanvas: canvas !== null,
                        hasFnStart,
                        hasFnCapture
                    };
                })()
            """, msg_id=10)

            print("Runner Component Eradication Check:", eradication_check)
            assert not eradication_check['hasScreen5'], "Screen-onboarding-5 must NOT exist in DOM!"
            assert not eradication_check['hasVideo'], "Liveness video element must NOT exist!"
            assert not eradication_check['hasCanvas'], "Liveness canvas element must NOT exist!"
            assert not eradication_check['hasFnStart'], "startLivenessCamera must NOT exist!"
            assert not eradication_check['hasFnCapture'], "captureLivenessSelfie must NOT exist!"
            print("  ✓ Live Face Verification component completely eradicated from Runner app!")

            print("\n=================================================================")
            print("2. RUNNER APP: TEST DIRECT ROUTING KYC -> PAYOUT SETUP")
            print("=================================================================")

            # Navigate to onboarding-4 and verify PAN
            await evaluate(ws, """
                (async () => {
                    localStorage.setItem('gb_user_phone', '9876543210');
                    localStorage.setItem('gb_runner_phone', '9876543210');
                    navigateTo('onboarding-4');
                    document.getElementById('kyc-pan-input').value = 'ABCDE1234F';
                    await submitPanVerification();
                })()
            """, msg_id=20)
            await asyncio.sleep(0.5)

            # Check button text and click proceedToNextStep
            btn_check = await evaluate(ws, """
                (() => {
                    const btnSpan = document.querySelector('#pan-verified-section button span');
                    return {
                        buttonText: btnSpan ? btnSpan.innerText.trim() : ''
                    };
                })()
            """, msg_id=21)
            print("PAN Verified Button Text:", btn_check)
            assert "Payout Setup" in btn_check['buttonText'] or "पेआउट" in btn_check['buttonText'], "Button must say Continue to Payout Setup!"

            # Proceed to next step
            route_res = await evaluate(ws, """
                (() => {
                    proceedToNextStep();
                    const s4Hidden = document.getElementById('screen-onboarding-4').classList.contains('hidden');
                    const s6Visible = !document.getElementById('screen-onboarding-6').classList.contains('hidden');
                    const s5Exists = document.getElementById('screen-onboarding-5') !== null;
                    const curScreen = state.currentScreen;
                    return { s4Hidden, s6Visible, s5Exists, curScreen };
                })()
            """, msg_id=22)

            print("Routing Result:", route_res)
            assert route_res['s4Hidden'], "Screen 4 must be hidden!"
            assert route_res['s6Visible'], "Screen 6 (Payout Setup) must be visible directly!"
            assert not route_res['s5Exists'], "Screen 5 must not exist!"
            assert route_res['curScreen'] == 'onboarding-6', "Current screen must be onboarding-6!"
            print("  ✓ User routed directly from Identity Verification to Payout Setup!")

            # Capture Screenshot Proof: Direct KYC to Payout Routing
            await take_screenshot(ws, "proof_direct_kyc_to_payout_routing.png", msg_id=23)

            # Test Back Navigation: on screen-onboarding-6, clicking back should return to onboarding-4
            back_res = await evaluate(ws, """
                (() => {
                    handleHistoryBack();
                    return {
                        s6Hidden: document.getElementById('screen-onboarding-6').classList.contains('hidden'),
                        s4Visible: !document.getElementById('screen-onboarding-4').classList.contains('hidden'),
                        curScreen: state.currentScreen
                    };
                })()
            """, msg_id=24)
            print("Back Navigation Check:", back_res)
            assert back_res['s6Hidden'], "Screen 6 must be hidden on back!"
            assert back_res['s4Visible'], "Screen 4 must be visible on back!"
            assert back_res['curScreen'] == 'onboarding-4', "Must return to onboarding-4!"
            print("  ✓ Back navigation from Payout Setup returns smoothly to Identity Verification!")

            print("\n=================================================================")
            print("3. VENDOR APP: VERIFY ERADICATION & DIRECT KYC -> PAYOUT ROUTING")
            print("=================================================================")

            # Navigate to Vendor App
            await send_cdp(ws, "Page.navigate", {"url": f"http://127.0.0.1:{PORT}/vendor/index.html#onboarding-4"}, msg_id=30)
            await asyncio.sleep(1.0)

            vendor_check = await evaluate(ws, """
                (() => {
                    localStorage.setItem('gb_user_phone', '9876543210');
                    localStorage.setItem('gb_vendor_phone', '9876543210');
                    navigateTo('onboarding-4');

                    const s5 = document.getElementById('screen-onboarding-5');
                    const hasFnStart = typeof startLivenessCamera !== 'undefined';
                    const hasFnCapture = typeof captureLivenessSelfie !== 'undefined';
                    return {
                        hasScreen5: s5 !== null,
                        hasFnStart,
                        hasFnCapture
                    };
                })()
            """, msg_id=31)
            print("Vendor Component Eradication Check:", vendor_check)
            assert not vendor_check['hasScreen5'], "Screen-onboarding-5 must NOT exist in Vendor DOM!"
            assert not vendor_check['hasFnStart'], "startLivenessCamera must NOT exist in Vendor!"
            assert not vendor_check['hasFnCapture'], "captureLivenessSelfie must NOT exist in Vendor!"
            print("  ✓ Live Face Verification component completely eradicated from Vendor app!")

            # Verify Vendor PAN and click proceedToNextStep
            vendor_route_res = await evaluate(ws, """
                (async () => {
                    document.getElementById('kyc-pan-input').value = 'ABCDE1234F';
                    await submitPanVerification();
                    proceedToNextStep();
                    const s4Hidden = document.getElementById('screen-onboarding-4').classList.contains('hidden');
                    const s6Visible = !document.getElementById('screen-onboarding-6').classList.contains('hidden');
                    return { s4Hidden, s6Visible, curScreen: state.currentScreen };
                })()
            """, msg_id=32)
            print("Vendor Routing Result:", vendor_route_res)
            assert vendor_route_res['s4Hidden'], "Vendor Screen 4 must be hidden!"
            assert vendor_route_res['s6Visible'], "Vendor Screen 6 (Payout Setup) must be visible directly!"
            assert vendor_route_res['curScreen'] == 'onboarding-6', "Vendor current screen must be onboarding-6!"
            print("  ✓ Vendor routed directly from Identity Verification to Payout Setup!")

            # Capture Screenshot Proof: Vendor Direct KYC to Payout Routing
            await take_screenshot(ws, "proof_vendor_direct_kyc_to_payout_routing.png", msg_id=33)

    finally:
        if chrome_proc:
            chrome_proc.terminate()
        if http_proc:
            http_proc.terminate()

if __name__ == '__main__':
    asyncio.run(run_evaluation())
