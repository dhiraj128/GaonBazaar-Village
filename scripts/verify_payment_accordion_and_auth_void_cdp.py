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
TEMP_DIR = os.path.abspath(".tmp_chrome_payment_accordion")
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
    print("=== STARTING PAYMENT ACCORDION & ₹1 AUTH/VOID CDP VERIFICATION ===")
    http_proc = subprocess.Popen(
        ["backend\\.venv\\Scripts\\python.exe", "-m", "http.server", "8180", "--directory", PUB_DIR],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    time.sleep(1.5)

    chrome_proc = subprocess.Popen([
        CHROME_PATH,
        "--headless=new",
        "--remote-debugging-port=8181",
        f"--user-data-dir={TEMP_DIR}",
        "--window-size=412,915",
        "http://127.0.0.1:8180/customer/index.html"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)

    try:
        targets_raw = urllib.request.urlopen("http://127.0.0.1:8181/json").read()
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

            # Setup authenticated customer and open payment settings modal
            print("\n--- TEST 1: Open Payment Settings Vault Modal ---")
            await eval_js(ws, """
                localStorage.clear();
                localStorage.setItem('gb_customer_authenticated', 'true');
                localStorage.setItem('gb_customer_phone', '9905361711');
                localStorage.setItem('gb_customer_lang', 'en');
                openPaymentSettingsModal();
            """, mid); mid += 1
            await asyncio.sleep(0.5)

            # Check Security Copywriting
            print("\n--- TEST 2: Professional Security Copywriting ---")
            sec_copy = await eval_js(ws, """
                (function() {
                    const titleEl = document.getElementById('vault-security-title');
                    const subEl = document.getElementById('vault-security-sub');
                    return {
                        primaryText: titleEl ? titleEl.innerText : '',
                        subText: subEl ? subEl.innerText : ''
                    };
                })()
            """, mid); mid += 1
            print(f"Security Copy Audit: {json.dumps(sec_copy, indent=2)}")
            assert "🔒 256-bit Bank-Grade Security" in sec_copy.get("primaryText", ""), "Primary security text mismatch"
            assert "Razorpay" in sec_copy.get("subText", ""), "Sub-text must mention Razorpay tokenization"
            assert "never store your raw card numbers" in sec_copy.get("subText", ""), "Sub-text must state raw card numbers are never stored"

            # Check Accordion UPI default expansion
            print("\n--- TEST 3: Expandable Accordion Defaults & Card Expansion ---")
            upi_state = await eval_js(ws, """
                (function() {
                    const fUpi = document.getElementById('vault-form-upi');
                    const fBank = document.getElementById('vault-form-bank');
                    const fCard = document.getElementById('vault-form-card');
                    const fCod = document.getElementById('vault-form-cod');
                    return {
                        upiHidden: fUpi?.classList.contains('hidden'),
                        bankHidden: fBank?.classList.contains('hidden'),
                        cardHidden: fCard?.classList.contains('hidden'),
                        codHidden: fCod?.classList.contains('hidden'),
                        upiHeight: fUpi?.offsetHeight
                    };
                })()
            """, mid); mid += 1
            print(f"Initial Accordion State (UPI default): {json.dumps(upi_state, indent=2)}")
            assert upi_state.get("upiHidden") is False, "UPI accordion form must be expanded initially"
            assert upi_state.get("bankHidden") is True, "Bank accordion form must be hidden initially"
            assert upi_state.get("cardHidden") is True, "Card accordion form must be hidden initially"

            # Expand Credit / Debit Card Accordion
            print("\n--- TEST 4: Expanding Card Accordion ---")
            await eval_js(ws, "selectVaultPaymentOption('card');", mid); mid += 1
            await asyncio.sleep(0.3)

            card_state = await eval_js(ws, """
                (function() {
                    const fUpi = document.getElementById('vault-form-upi');
                    const fBank = document.getElementById('vault-form-bank');
                    const fCard = document.getElementById('vault-form-card');
                    const fCod = document.getElementById('vault-form-cod');
                    const rCard = document.getElementById('vault-radio-card');
                    const numInput = document.getElementById('vault-card-number');
                    const cvvInput = document.getElementById('vault-card-cvv');
                    return {
                        rCardChecked: rCard?.checked,
                        cardHidden: fCard?.classList.contains('hidden'),
                        upiHidden: fUpi?.classList.contains('hidden'),
                        bankHidden: fBank?.classList.contains('hidden'),
                        cardOffsetHeight: fCard?.offsetHeight,
                        cardNumVisible: numInput !== null,
                        cvvVisible: cvvInput !== null
                    };
                })()
            """, mid); mid += 1
            print(f"Card Accordion Expanded State: {json.dumps(card_state, indent=2)}")
            assert card_state.get("rCardChecked") is True, "Radio card must be checked"
            assert card_state.get("cardHidden") is False, "Card form must NOT be hidden"
            assert card_state.get("upiHidden") is True, "UPI form must be hidden when card is expanded"
            assert card_state.get("cardOffsetHeight", 0) > 100, "Card form must have valid rendered height"

            # Capture visual proof: Card expanded accordion
            await take_screenshot(ws, "proof_payment_accordion_card_expanded.png", mid); mid += 1

            # Expand Bank Accordion
            print("\n--- TEST 5: Expanding Bank Accordion ---")
            await eval_js(ws, "selectVaultPaymentOption('bank');", mid); mid += 1
            await asyncio.sleep(0.3)

            bank_state = await eval_js(ws, """
                (function() {
                    const fBank = document.getElementById('vault-form-bank');
                    const fCard = document.getElementById('vault-form-card');
                    const rBank = document.getElementById('vault-radio-bank');
                    return {
                        rBankChecked: rBank?.checked,
                        bankHidden: fBank?.classList.contains('hidden'),
                        cardHidden: fCard?.classList.contains('hidden'),
                        bankOffsetHeight: fBank?.offsetHeight
                    };
                })()
            """, mid); mid += 1
            print(f"Bank Accordion Expanded State: {json.dumps(bank_state, indent=2)}")
            assert bank_state.get("rBankChecked") is True, "Radio bank must be checked"
            assert bank_state.get("bankHidden") is False, "Bank form must be expanded"
            assert bank_state.get("cardHidden") is True, "Card form must be collapsed"

            # Expand COD Accordion
            print("\n--- TEST 6: Expanding COD Accordion ---")
            await eval_js(ws, "selectVaultPaymentOption('cod');", mid); mid += 1
            await asyncio.sleep(0.3)

            cod_state = await eval_js(ws, """
                (function() {
                    const fCod = document.getElementById('vault-form-cod');
                    const fBank = document.getElementById('vault-form-bank');
                    const rCod = document.getElementById('vault-radio-cod');
                    return {
                        rCodChecked: rCod?.checked,
                        codHidden: fCod?.classList.contains('hidden'),
                        bankHidden: fBank?.classList.contains('hidden')
                    };
                })()
            """, mid); mid += 1
            print(f"COD Accordion Expanded State: {json.dumps(cod_state, indent=2)}")
            assert cod_state.get("rCodChecked") is True, "Radio COD must be checked"
            assert cod_state.get("codHidden") is False, "COD details must be expanded"
            assert cod_state.get("bankHidden") is True, "Bank form must be collapsed"

            # Test ₹1 Auth & Void Verification with Card
            print("\n--- TEST 7: ₹1 Auth & Void Verification Flow ---")
            await eval_js(ws, "selectVaultPaymentOption('card');", mid); mid += 1
            await asyncio.sleep(0.2)

            # Populate card details
            await eval_js(ws, """
                document.getElementById('vault-card-number').value = '4111 2222 3333 4444';
                document.getElementById('vault-card-holder').value = 'Dhiraj Sharma';
                document.getElementById('vault-card-expiry').value = '12/28';
                document.getElementById('vault-card-cvv').value = '987';
            """, mid); mid += 1

            # Trigger saveCustomerPaymentVault via setTimeout and snapshot mid-flight loading state
            await eval_js(ws, """
                window.__authVoidCompleted = false;
                setTimeout(async () => {
                    await saveCustomerPaymentVault();
                    window.__authVoidCompleted = true;
                }, 50);
            """, mid); mid += 1
            await asyncio.sleep(0.3)

            # Capture visual proof of ₹1 Auth & Void loading state
            loading_snapshot = await eval_js(ws, """
                (function() {
                    const btn = document.getElementById('btn-save-payment-vault');
                    const btnText = document.getElementById('btn-save-vault-text');
                    return {
                        disabled: btn?.disabled,
                        text: btnText?.innerText
                    };
                })()
            """, mid); mid += 1
            print(f"Verification Button Loading Snapshot: {json.dumps(loading_snapshot, indent=2)}")
            assert loading_snapshot.get("disabled") is True, "Button must be disabled during verification"
            assert "Verifying (₹1 test charge & refund)..." in loading_snapshot.get("text", ""), f"Button text must match required verifying text (got {loading_snapshot.get('text')})"

            await take_screenshot(ws, "proof_payment_auth_void_verifying.png", mid); mid += 1

            # Await completion
            for _ in range(30):
                is_done = await eval_js(ws, "window.__authVoidCompleted === true", mid); mid += 1
                if is_done:
                    break
                await asyncio.sleep(0.1)

            # Check verification outcomes
            verification_outcome = await eval_js(ws, """
                (function() {
                    return {
                        mode: localStorage.getItem('gb_customer_payout_mode'),
                        paymentSetup: localStorage.getItem('gb_customer_payment_setup'),
                        authVoidId: localStorage.getItem('gb_customer_auth_void_id'),
                        cardBrand: localStorage.getItem('gb_customer_card_brand'),
                        cardLast4: localStorage.getItem('gb_customer_card_last4'),
                        rawCardNumStored: localStorage.getItem('gb_customer_card_number'),
                        rawCvvStored: localStorage.getItem('gb_customer_card_cvv'),
                        cvvInputCleared: document.getElementById('vault-card-cvv')?.value === '',
                        cardNumMasked: document.getElementById('vault-card-number')?.value.includes('••••')
                    };
                })()
            """, mid); mid += 1
            print(f"Verification & Security Outcome: {json.dumps(verification_outcome, indent=2)}")
            assert verification_outcome.get("mode") == "card", "Payout mode must be 'card'"
            assert verification_outcome.get("paymentSetup") == "true", "Payment setup must be 'true'"
            assert verification_outcome.get("authVoidId", "").startswith("av_card_"), "Auth void ID must be recorded"
            assert verification_outcome.get("cardBrand") == "Visa", "Brand must be Visa"
            assert verification_outcome.get("cardLast4") == "4444", "Last4 must be 4444"
            assert verification_outcome.get("rawCardNumStored") is None, "Raw card number must NEVER be stored in localStorage"
            assert verification_outcome.get("rawCvvStored") is None, "CVV must NEVER be stored in localStorage"
            assert verification_outcome.get("cvvInputCleared") is True, "CVV input field must be cleared"
            assert verification_outcome.get("cardNumMasked") is True, "Card input field must be masked"

            # Capture visual proof of completed verification
            await take_screenshot(ws, "proof_payment_auth_void_verified_success.png", mid); mid += 1

            print("\n✅ ALL PAYMENT ACCORDION & ₹1 AUTH/VOID CDP TESTS PASSED PERFECTLY!")

    finally:
        chrome_proc.terminate()
        http_proc.terminate()

if __name__ == "__main__":
    asyncio.run(main())
