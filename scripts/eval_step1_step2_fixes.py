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
TEMP_DIR = r"C:\Users\dhira\AppData\Local\Temp\chrome_step1_eval"
ARTIFACT_DIR = r"C:\Users\dhira\OneDrive\Desktop\GaoBazar-Village"
BRAIN_DIR = r"C:\Users\dhira\.gemini\antigravity\brain\918c8085-b60b-40a9-a077-a3344458bcc5"

async def eval_all():
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
        print(f"[Screenshot Saved]: {filename}")

    try:
        targets_raw = urllib.request.urlopen("http://127.0.0.1:8096/json").read()
        targets = json.loads(targets_raw.decode('utf-8'))
        page_target = next(t for t in targets if t.get("type") == "page")
        ws_url = page_target["webSocketDebuggerUrl"]

        async with websockets.connect(ws_url) as ws:
            await send_cmd(ws, "Page.enable")

            # -------------------------------------------------------------
            # TEST 1: RUNNER STEP 1 (SINGLE BUTTON & TEST PHONE PREFILL)
            # -------------------------------------------------------------
            print("\n=== EVALUATING RUNNER APP ===")
            await send_cmd(ws, "Page.navigate", {"url": "http://127.0.0.1:8095/runner/index.html"})
            await asyncio.sleep(2)
            await send_cmd(ws, "Runtime.evaluate", {"expression": "localStorage.clear(); sessionStorage.clear(); location.reload();", "awaitPromise": True})
            await asyncio.sleep(2)

            res = await send_cmd(ws, "Runtime.evaluate", {
                "expression": """(() => {
                    const btns = Array.from(document.querySelectorAll('button')).filter(b => {
                        const style = window.getComputedStyle(b);
                        const isVisible = b.offsetParent !== null && style.display !== 'none' && style.visibility !== 'hidden';
                        return isVisible && (b.innerText.includes('Continue') || b.innerText.includes('आगे'));
                    });
                    return {
                        count: btns.length,
                        texts: btns.map(b => b.innerText.trim())
                    };
                })()""",
                "returnByValue": True
            })
            val = res.get("result", {}).get("result", {}).get("value")
            print(f"Runner Step 1 visible Continue buttons: {val['count']} (texts: {val['texts']})")
            assert val['count'] == 1, f"Expected exactly 1 continue button in Runner Step 1, found {val['count']}"
            await save_screenshot(ws, "proof_step1_runner_single_button.png")

            # Navigate to Step 2
            await send_cmd(ws, "Runtime.evaluate", {"expression": "goToOnboardingStep(2);"})
            await asyncio.sleep(1)

            res2 = await send_cmd(ws, "Runtime.evaluate", {
                "expression": """(() => {
                    const phone = document.getElementById('runner-phone-input')?.value;
                    const o1 = document.getElementById('otp-1')?.value;
                    const o2 = document.getElementById('otp-2')?.value;
                    const o3 = document.getElementById('otp-3')?.value;
                    const o4 = document.getElementById('otp-4')?.value;
                    return { phone, otp: o1 + o2 + o3 + o4 };
                })()""",
                "returnByValue": True
            })
            val2 = res2.get("result", {}).get("result", {}).get("value")
            print(f"Runner Step 2 prefilled phone: {val2['phone']}, OTP: {val2['otp']}")
            assert val2['phone'] == "9876543210", f"Expected runner phone 9876543210, got {val2['phone']}"
            assert val2['otp'] == "1234", f"Expected runner otp 1234, got {val2['otp']}"

            # -------------------------------------------------------------
            # TEST 2: VENDOR STEP 1 (SINGLE BUTTON & TEST PHONE PREFILL)
            # -------------------------------------------------------------
            print("\n=== EVALUATING VENDOR APP ===")
            await send_cmd(ws, "Page.navigate", {"url": "http://127.0.0.1:8095/vendor/index.html"})
            await asyncio.sleep(2)
            await send_cmd(ws, "Runtime.evaluate", {"expression": "localStorage.clear(); sessionStorage.clear(); location.reload();", "awaitPromise": True})
            await asyncio.sleep(2)

            res = await send_cmd(ws, "Runtime.evaluate", {
                "expression": """(() => {
                    const btns = Array.from(document.querySelectorAll('button')).filter(b => {
                        const style = window.getComputedStyle(b);
                        const isVisible = b.offsetParent !== null && style.display !== 'none' && style.visibility !== 'hidden';
                        return isVisible && (b.innerText.includes('Continue') || b.innerText.includes('आगे'));
                    });
                    return {
                        count: btns.length,
                        texts: btns.map(b => b.innerText.trim())
                    };
                })()""",
                "returnByValue": True
            })
            val = res.get("result", {}).get("result", {}).get("value")
            print(f"Vendor Step 1 visible Continue buttons: {val['count']} (texts: {val['texts']})")
            assert val['count'] == 1, f"Expected exactly 1 continue button in Vendor Step 1, found {val['count']}"
            await save_screenshot(ws, "proof_step1_vendor_single_button.png")

            # Navigate to Step 2
            await send_cmd(ws, "Runtime.evaluate", {"expression": "goToOnboardingStep(2);"})
            await asyncio.sleep(1)

            res2 = await send_cmd(ws, "Runtime.evaluate", {
                "expression": """(() => {
                    const phone = document.getElementById('vendor-phone-input')?.value;
                    const o1 = document.getElementById('otp-1')?.value;
                    const o2 = document.getElementById('otp-2')?.value;
                    const o3 = document.getElementById('otp-3')?.value;
                    const o4 = document.getElementById('otp-4')?.value;
                    return { phone, otp: o1 + o2 + o3 + o4 };
                })()""",
                "returnByValue": True
            })
            val2 = res2.get("result", {}).get("result", {}).get("value")
            print(f"Vendor Step 2 prefilled phone: {val2['phone']}, OTP: {val2['otp']}")
            assert val2['phone'] == "9876543210", f"Expected vendor phone 9876543210, got {val2['phone']}"
            assert val2['otp'] == "1234", f"Expected vendor otp 1234, got {val2['otp']}"

            # -------------------------------------------------------------
            # TEST 3: CUSTOMER STEP 1 & 2 (SINGLE BUTTON, PRE-FILL, ERROR MASKING)
            # -------------------------------------------------------------
            print("\n=== EVALUATING CUSTOMER APP ===")
            await send_cmd(ws, "Page.navigate", {"url": "http://127.0.0.1:8095/customer/index.html"})
            await asyncio.sleep(2)
            await send_cmd(ws, "Runtime.evaluate", {"expression": "localStorage.clear(); sessionStorage.clear(); location.reload();", "awaitPromise": True})
            await asyncio.sleep(2)

            res = await send_cmd(ws, "Runtime.evaluate", {
                "expression": """(() => {
                    const btns = Array.from(document.querySelectorAll('button')).filter(b => {
                        const style = window.getComputedStyle(b);
                        const isVisible = b.offsetParent !== null && style.display !== 'none' && style.visibility !== 'hidden';
                        return isVisible && (b.innerText.includes('Continue') || b.innerText.includes('आगे'));
                    });
                    return {
                        count: btns.length,
                        texts: btns.map(b => b.innerText.trim())
                    };
                })()""",
                "returnByValue": True
            })
            val = res.get("result", {}).get("result", {}).get("value")
            print(f"Customer Step 1 visible Continue buttons: {val['count']} (texts: {val['texts']})")
            assert val['count'] == 1, f"Expected exactly 1 continue button in Customer Step 1, found {val['count']}"
            await save_screenshot(ws, "proof_step1_customer_single_button.png")

            # Proceed from Language to Step 2 Login
            await send_cmd(ws, "Runtime.evaluate", {"expression": "proceedFromLanguage();"})
            await asyncio.sleep(1)

            res_phone = await send_cmd(ws, "Runtime.evaluate", {
                "expression": "document.getElementById('cust-phone-input')?.value",
                "returnByValue": True
            })
            phone_val = res_phone.get("result", {}).get("result", {}).get("value")
            print(f"Customer Step 2 prefilled phone: {phone_val}")
            assert phone_val == "9876543210", f"Expected customer phone 9876543210, got {phone_val}"

            # Trigger sendCustomerOTP()
            await send_cmd(ws, "Runtime.evaluate", {"expression": "sendCustomerOTP();", "awaitPromise": True})
            await asyncio.sleep(1)

            res_otp = await send_cmd(ws, "Runtime.evaluate", {
                "expression": """(() => {
                    let code = '';
                    for (let i = 1; i <= 6; i++) {
                        code += (document.getElementById('otp-' + i)?.value || '');
                    }
                    return code;
                })()""",
                "returnByValue": True
            })
            otp_val = res_otp.get("result", {}).get("result", {}).get("value")
            print(f"Customer Step 2 prefilled test OTP: {otp_val}")
            assert otp_val == "123456", f"Expected customer test OTP 123456, got {otp_val}"
            await save_screenshot(ws, "proof_step2_prefilled_test_credentials.png")

            # Test Error Masking
            print("\n=== TESTING ERROR MASKING ===")
            await send_cmd(ws, "Runtime.evaluate", {
                "expression": """(() => {
                    window.authService.handleAuthError({
                        code: 'auth/operation-not-allowed',
                        message: 'Firebase: Error (auth/operation-not-allowed).'
                    });
                })()"""
            })
            await asyncio.sleep(1)

            res_err = await send_cmd(ws, "Runtime.evaluate", {
                "expression": """(() => {
                    const text = document.getElementById('auth-error-text')?.innerText || '';
                    const banner = document.getElementById('auth-error-banner');
                    const isVisible = banner && !banner.classList.contains('hidden');
                    return { text, isVisible };
                })()""",
                "returnByValue": True
            })
            err_val = res_err.get("result", {}).get("result", {}).get("value")
            print(f"Masked Error Text: '{err_val['text']}', Visible: {err_val['isVisible']}")
            assert err_val['isVisible'], "Error banner should be visible"
            assert "Firebase" not in err_val['text'], "Error message must NEVER expose Firebase!"
            assert "operation-not-allowed" not in err_val['text'], "Error message must NEVER expose raw code!"
            expected_msg = "Unable to send verification code. Please check your number or try again later."
            assert err_val['text'] == expected_msg, f"Expected exact masked message, got '{err_val['text']}'"
            await save_screenshot(ws, "proof_step2_masked_error_ui.png")

            print("\nALL VERIFICATIONS AND ASSERTIONS PASSED PERFECTLY!")

    finally:
        chrome_proc.terminate()
        http_proc.terminate()

if __name__ == "__main__":
    asyncio.run(eval_all())
