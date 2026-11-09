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
CDP_PORT = 9233
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
TEMP_DIR = r"C:\Users\dhira\AppData\Local\Temp\chrome_payout_eval"

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

async def run_payout_eval():
    http_proc = None
    chrome_proc = None
    try:
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{PORT}/vendor/index.html", timeout=1)
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
            f"http://127.0.0.1:{PORT}/vendor/index.html"
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
            print("STEP 1: AUDIT VENDOR ONBOARDING PAYOUT SETUP (SCREEN 6)")
            print("=======================================================")

            # Navigate to onboarding-6
            await evaluate(ws, """
                navigateTo('onboarding-6');
                switchPayoutMode('upi');
            """, msg_id=10)
            await asyncio.sleep(0.5)

            # Check 1: No Coming Soon / disabled
            checks = await evaluate(ws, """
                (() => {
                    const s6 = document.getElementById('screen-onboarding-6');
                    const hasComingSoon = s6.innerText.toLowerCase().includes('coming soon');
                    const upiTab = document.getElementById('payout-tab-upi') !== null;
                    const bankTab = document.getElementById('payout-tab-bank') !== null;
                    const upiInput = document.getElementById('upi-vpa') !== null;
                    const upiBtn = document.getElementById('btn-save-submit-upi') !== null;
                    const bankBtn = document.getElementById('btn-save-submit-bank') !== null;
                    const hasDisabledOverlay = s6.querySelector('.pointer-events-none') !== null;

                    return {
                        hasComingSoon,
                        upiTab,
                        bankTab,
                        upiInput,
                        upiBtn,
                        bankBtn,
                        hasDisabledOverlay,
                        s6Visible: !s6.classList.contains('hidden')
                    };
                })()
            """, msg_id=11)
            print("  Screen 6 Checks:", checks)
            assert not checks['hasComingSoon'], "Screen 6 contains 'Coming Soon' placeholder!"
            assert not checks['hasDisabledOverlay'], "Screen 6 contains disabled overlay!"
            assert checks['upiTab'] and checks['bankTab'], "Screen 6 missing payout tabs!"
            assert checks['upiBtn'] and checks['bankBtn'], "Screen 6 missing Save & Submit buttons!"

            # Capture Tab 1 (UPI ID) Proof Screenshot
            await take_screenshot(ws, "proof_vendor_payout_tab1_upi.png", msg_id=12)

            print("\n=======================================================")
            print("STEP 2: TEST TAB 2 (BANK ACCOUNT) & VALIDATION")
            print("=======================================================")

            # Switch to bank mode and test mismatch
            match_res = await evaluate(ws, """
                (() => {
                    switchPayoutMode('bank');
                    document.getElementById('bank-acc-no').value = '50100456789012';
                    document.getElementById('bank-acc-no-confirm').value = '50100999999999';
                    checkAccountMatch();
                    const msg = document.getElementById('acc-match-msg');
                    const mismatchText = msg.innerText;

                    // Now fix match
                    document.getElementById('bank-acc-no-confirm').value = '50100456789012';
                    checkAccountMatch();
                    const matchText = msg.innerText;

                    return { mismatchText, matchText };
                })()
            """, msg_id=20)
            print("  Account Match Validation:", match_res)
            assert "do not match" in match_res['mismatchText'], "Mismatch validation failed!"
            assert "match" in match_res['matchText'] and "do not" not in match_res['matchText'], "Match validation failed!"

            # Capture Tab 2 (Bank Account) Proof Screenshot
            await take_screenshot(ws, "proof_vendor_payout_tab2_bank.png", msg_id=21)

            print("\n=======================================================")
            print("STEP 3: FORM SUBMISSION & ROUTING TO UNDER REVIEW SCREEN")
            print("=======================================================")

            # Submit payout form
            await evaluate(ws, """
                submitPayoutDetails('bank');
            """, msg_id=30)
            await asyncio.sleep(1.5)

            # Verify screen 7 visible and status in pending_admin_approval
            sub_res = await evaluate(ws, """
                (() => {
                    const s7 = document.getElementById('screen-onboarding-7');
                    const s7Visible = s7 && !s7.classList.contains('hidden');
                    const status = localStorage.getItem('gb_vendor_status');
                    return { s7Visible, status };
                })()
            """, msg_id=31)
            print("  Post-Submission State:", sub_res)
            assert sub_res['s7Visible'], "Did not route to screen-onboarding-7!"
            assert sub_res['status'] == 'pending_admin_approval', "Status was not updated to pending_admin_approval!"

            # Capture Screen 7 (Under Review) Proof Screenshot
            await take_screenshot(ws, "proof_onboarding_under_review_screen.png", msg_id=32)

            print("\n=======================================================")
            print("STEP 4: AUDIT RUNNER ONBOARDING PAYOUT SETUP")
            print("=======================================================")

            # Navigate to Runner app
            await send_cdp(ws, "Page.navigate", {"url": f"http://127.0.0.1:{PORT}/runner/index.html#onboarding-6"}, msg_id=40)
            await asyncio.sleep(2)

            # Wait for readyState
            for _ in range(10):
                ready = await evaluate(ws, "document.readyState === 'complete'", msg_id=400 + _)
                if ready:
                    break
                await asyncio.sleep(0.5)

            # Navigate to Runner screen 6
            runner_checks = await evaluate(ws, """
                (() => {
                    try {
                        if (typeof navigateTo === 'function') {
                            navigateTo('onboarding-6');
                        }
                        const s6 = document.getElementById('screen-onboarding-6');
                        if (!s6) return { error: 'screen-onboarding-6 not found' };

                        const hasComingSoon = s6.innerText.toLowerCase().includes('coming soon');
                        const hasDisabled = s6.querySelector('.pointer-events-none') !== null;
                        const upiBtn = document.getElementById('btn-save-submit-upi') !== null;
                        const bankBtn = document.getElementById('btn-save-submit-bank') !== null;

                        // Switch to Bank
                        if (typeof switchPayoutMode === 'function') {
                            switchPayoutMode('bank');
                        }
                        return {
                            hasComingSoon,
                            hasDisabled,
                            upiBtn,
                            bankBtn,
                            s6Visible: !s6.classList.contains('hidden')
                        };
                    } catch (e) {
                        return { error: e.message };
                    }
                })()
            """, msg_id=41)
            print("  Runner Screen 6 Checks:", runner_checks)
            assert runner_checks and not runner_checks.get('error'), f"Runner check error: {runner_checks.get('error')}"
            assert not runner_checks['hasComingSoon'], "Runner s6 contains 'Coming Soon'!"
            assert not runner_checks['hasDisabled'], "Runner s6 contains disabled class!"
            assert runner_checks['upiBtn'] and runner_checks['bankBtn'], "Runner missing submit buttons!"

            # Submit Runner payout and verify screen 7
            await evaluate(ws, """
                submitPayoutDetails('bank');
            """, msg_id=42)
            await asyncio.sleep(1.5)

            runner_s7 = await evaluate(ws, """
                (() => {
                    const s7 = document.getElementById('screen-onboarding-7');
                    const s7Visible = s7 && !s7.classList.contains('hidden');
                    const status = localStorage.getItem('gb_runner_status');
                    return { s7Visible, status };
                })()
            """, msg_id=43)
            print("  Runner Post-Submission State:", runner_s7)
            assert runner_s7['s7Visible'], "Runner did not route to screen-onboarding-7!"
            assert runner_s7['status'] == 'pending_admin_approval', "Runner status not pending_admin_approval!"

            await take_screenshot(ws, "proof_runner_payout_under_review.png", msg_id=44)

            print("\n=======================================================")
            print("ALL EVALUATION CHECKS PASSED WITH 100% SUCCESS!")
            print("=======================================================")

    finally:
        if chrome_proc:
            chrome_proc.terminate()
            chrome_proc.wait()
        if http_proc:
            http_proc.terminate()
            http_proc.wait()

if __name__ == "__main__":
    asyncio.run(run_payout_eval())
