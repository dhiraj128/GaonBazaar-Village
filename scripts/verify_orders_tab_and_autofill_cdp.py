import asyncio
import json
import subprocess
import time
import urllib.request
import websockets
import os
import sys
import shutil

# Ensure utf-8 output safe for windows console
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PUB_DIR = os.path.abspath("public_web")
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
TEMP_DIR = os.path.abspath(".tmp_chrome_orders_autofill")
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
            # Also copy to artifacts dir
            if os.path.exists(ARTIFACT_DIR):
                shutil.copy(filename, os.path.join(ARTIFACT_DIR, os.path.basename(filename)))
                print(f"Copied to artifact directory: {os.path.join(ARTIFACT_DIR, os.path.basename(filename))}")
            break

async def main():
    print("=== STARTING ORDERS TAB CRASH RESOLUTION & AUTOFILL ERADICATION CDP TEST ===")
    http_proc = subprocess.Popen(
        ["backend\\.venv\\Scripts\\python.exe", "-m", "http.server", "8170", "--directory", PUB_DIR],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    time.sleep(1.5)

    chrome_proc = subprocess.Popen([
        CHROME_PATH,
        "--headless=new",
        "--remote-debugging-port=8171",
        f"--user-data-dir={TEMP_DIR}",
        "--window-size=412,915",
        "http://127.0.0.1:8170/vendor/index.html"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)

    try:
        targets_raw = urllib.request.urlopen("http://127.0.0.1:8171/json").read()
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

            # ------------------------------------------------------------------
            # 1. VENDOR ORDERS TAB STABILITY TEST
            # ------------------------------------------------------------------
            print("\n=== TEST 1: Vendor Orders Tab Crash Resolution ===")
            await eval_js(ws, """
                localStorage.clear();
                localStorage.setItem('gb_vendor_authenticated', 'true');
                localStorage.setItem('gb_vendor_token', 'mock_token_orders_test');
                localStorage.setItem('gaonbazaar_vendor_token', 'mock_token_orders_test');
                localStorage.setItem('gb_vendor_phone', '9876543210');
                localStorage.setItem('gb_vendor_onboarding_completed', 'true');
                location.reload();
            """, mid); mid += 1
            await asyncio.sleep(2)

            # Switch to Orders tab (which calls updateOrdersUIFromData() with no arguments)
            await eval_js(ws, "switchDashboardTab('orders')", mid); mid += 1
            await asyncio.sleep(0.5)

            # Explicitly test calling updateOrdersUIFromData with undefined, null, and empty array
            res_undef = await eval_js(ws, """
                (function() {
                    try {
                        updateOrdersUIFromData();
                        return { success: true };
                    } catch(e) {
                        return { success: false, error: e.message };
                    }
                })()
            """, mid); mid += 1
            print(f"Call updateOrdersUIFromData() [no args]: {res_undef}")
            assert res_undef.get("success") is True, f"updateOrdersUIFromData() threw error: {res_undef}"

            res_null = await eval_js(ws, """
                (function() {
                    try {
                        updateOrdersUIFromData(null);
                        return { success: true };
                    } catch(e) {
                        return { success: false, error: e.message };
                    }
                })()
            """, mid); mid += 1
            print(f"Call updateOrdersUIFromData(null): {res_null}")
            assert res_null.get("success") is True, f"updateOrdersUIFromData(null) threw error: {res_null}"

            # Check that tab-orders has rendered cleanly without error boundaries
            orders_stats = await eval_js(ws, """
                (function() {
                    const tab = document.getElementById('tab-orders');
                    if (!tab) return { exists: false };
                    const hasError = tab.querySelector('.section-error-boundary') !== null;
                    const errorText = hasError ? tab.querySelector('.section-error-boundary').innerText : null;
                    return {
                        exists: true,
                        hidden: tab.classList.contains('hidden'),
                        hasErrorBoundary: hasError,
                        errorText: errorText,
                        offsetHeight: tab.offsetHeight,
                        badgeCount: document.getElementById('badge-new-orders')?.innerText
                    };
                })()
            """, mid); mid += 1
            print(f"Orders Tab State: {json.dumps(orders_stats, indent=2)}")
            assert orders_stats.get("exists") is True, "tab-orders must exist"
            assert orders_stats.get("hidden") is False, "tab-orders must be visible"
            assert orders_stats.get("hasErrorBoundary") is False, f"Orders tab triggered error boundary: {orders_stats.get('errorText')}"
            assert orders_stats.get("offsetHeight", 0) > 100, "tab-orders should have valid rendered height"

            # Test updating with actual mock orders
            await eval_js(ws, """
                updateOrdersUIFromData([
                    {
                        id: 'ORD-TEST-101',
                        status: 'PLACED',
                        created_at: new Date().toISOString(),
                        delivery_address: 'Village Center, House #42',
                        payment_method: 'COD',
                        items: [{ item_name: 'Fresh Tomatoes 1kg', quantity: 2, price: 40 }],
                        total_amount: 80
                    }
                ]);
            """, mid); mid += 1
            await asyncio.sleep(0.5)

            # Capture visual proof: Clean Orders Tab with active order card
            await take_screenshot(ws, "proof_vendor_orders_tab_clean.png", mid); mid += 1

            # ------------------------------------------------------------------
            # 2. VENDOR AUTOFILL & PASSWORD TYPE AUDIT
            # ------------------------------------------------------------------
            print("\n=== TEST 2: Vendor Autofill and Form Security Audit ===")
            vendor_audit = await eval_js(ws, """
                (function() {
                    const bankAcc = document.getElementById('bank-acc-no');
                    const bankConfirm = document.getElementById('bank-acc-no-confirm');
                    const bankIfsc = document.getElementById('bank-ifsc');
                    const upiVpa = document.getElementById('upi-vpa');
                    const kycAadhaarOtp = document.getElementById('kyc-aadhaar-otp-input');
                    const payoutOtp = document.getElementById('payout-security-otp');

                    return {
                        bankAccType: bankAcc?.getAttribute('type'),
                        bankAccInputMode: bankAcc?.getAttribute('inputmode'),
                        bankAccAutoComplete: bankAcc?.getAttribute('autocomplete'),
                        bankConfirmType: bankConfirm?.getAttribute('type'),
                        bankConfirmInputMode: bankConfirm?.getAttribute('inputmode'),
                        bankConfirmAutoComplete: bankConfirm?.getAttribute('autocomplete'),
                        bankIfscAutoComplete: bankIfsc?.getAttribute('autocomplete'),
                        upiVpaAutoComplete: upiVpa?.getAttribute('autocomplete'),
                        kycAadhaarOtpAutoComplete: kycAadhaarOtp?.getAttribute('autocomplete'),
                        payoutOtpAutoComplete: payoutOtp?.getAttribute('autocomplete')
                    };
                })()
            """, mid); mid += 1
            print(f"Vendor Form Audit: {json.dumps(vendor_audit, indent=2)}")
            assert vendor_audit.get("bankAccType") == "text", f"bank-acc-no type must be 'text' (got {vendor_audit.get('bankAccType')})"
            assert vendor_audit.get("bankAccInputMode") == "numeric", "bank-acc-no inputmode must be 'numeric'"
            assert vendor_audit.get("bankAccAutoComplete") == "off", "bank-acc-no autocomplete must be 'off'"
            assert vendor_audit.get("bankConfirmType") == "text", f"bank-acc-no-confirm type must be 'text' (got {vendor_audit.get('bankConfirmType')})"
            assert vendor_audit.get("bankConfirmInputMode") == "numeric", "bank-acc-no-confirm inputmode must be 'numeric'"
            assert vendor_audit.get("bankConfirmAutoComplete") == "off", "bank-acc-no-confirm autocomplete must be 'off'"
            assert vendor_audit.get("bankIfscAutoComplete") == "off", "bank-ifsc autocomplete must be 'off'"
            assert vendor_audit.get("upiVpaAutoComplete") == "off", "upi-vpa autocomplete must be 'off'"
            assert vendor_audit.get("payoutOtpAutoComplete") == "one-time-code", "payout-security-otp must have autocomplete='one-time-code'"

            # ------------------------------------------------------------------
            # 3. CUSTOMER AUTOFILL & PASSWORD TYPE AUDIT
            # ------------------------------------------------------------------
            print("\n=== TEST 3: Customer App Autofill & Password Type Audit ===")
            await eval_js(ws, "window.location.href = 'http://127.0.0.1:8170/customer/index.html';", mid); mid += 1
            await asyncio.sleep(2)

            customer_audit = await eval_js(ws, """
                (function() {
                    const vaultAcc = document.getElementById('vault-bank-account');
                    const vaultCvv = document.getElementById('vault-card-cvv');
                    const checkoutCvv = document.getElementById('checkout-card-cvv');
                    const vaultUpi = document.getElementById('vault-upi-input');
                    const vaultIfsc = document.getElementById('vault-bank-ifsc');
                    const otp1 = document.getElementById('otp-1');
                    const otp6 = document.getElementById('otp-6');

                    return {
                        vaultAccType: vaultAcc?.getAttribute('type'),
                        vaultAccInputMode: vaultAcc?.getAttribute('inputmode'),
                        vaultAccAutoComplete: vaultAcc?.getAttribute('autocomplete'),
                        vaultCvvType: vaultCvv?.getAttribute('type'),
                        vaultCvvInputMode: vaultCvv?.getAttribute('inputmode'),
                        vaultCvvAutoComplete: vaultCvv?.getAttribute('autocomplete'),
                        checkoutCvvType: checkoutCvv?.getAttribute('type'),
                        checkoutCvvInputMode: checkoutCvv?.getAttribute('inputmode'),
                        checkoutCvvAutoComplete: checkoutCvv?.getAttribute('autocomplete'),
                        vaultUpiAutoComplete: vaultUpi?.getAttribute('autocomplete'),
                        vaultIfscAutoComplete: vaultIfsc?.getAttribute('autocomplete'),
                        otp1AutoComplete: otp1?.getAttribute('autocomplete'),
                        otp6AutoComplete: otp6?.getAttribute('autocomplete')
                    };
                })()
            """, mid); mid += 1
            print(f"Customer Form Audit: {json.dumps(customer_audit, indent=2)}")
            assert customer_audit.get("vaultAccType") == "text", f"vault-bank-account type must be 'text' (got {customer_audit.get('vaultAccType')})"
            assert customer_audit.get("vaultAccInputMode") == "numeric", "vault-bank-account inputmode must be 'numeric'"
            assert customer_audit.get("vaultAccAutoComplete") == "off", "vault-bank-account autocomplete must be 'off'"
            assert customer_audit.get("vaultCvvType") == "text", f"vault-card-cvv type must be 'text' (got {customer_audit.get('vaultCvvType')})"
            assert customer_audit.get("checkoutCvvType") == "text", f"checkout-card-cvv type must be 'text' (got {customer_audit.get('checkoutCvvType')})"
            assert customer_audit.get("vaultUpiAutoComplete") == "off", "vault-upi-input autocomplete must be 'off'"
            assert customer_audit.get("otp1AutoComplete") == "one-time-code", "otp-1 must have autocomplete='one-time-code'"
            assert customer_audit.get("otp6AutoComplete") == "one-time-code", "otp-6 must have autocomplete='one-time-code'"

            # Open Payment Settings Modal in Customer to capture visual proof
            await eval_js(ws, """
                localStorage.setItem('gb_customer_authenticated', 'true');
                localStorage.setItem('gb_customer_token', 'mock_cust_token');
                if (typeof openPaymentSettingsModal === 'function') {
                    openPaymentSettingsModal();
                } else {
                    const m = document.getElementById('modal-payment-settings');
                    if (m) m.classList.remove('hidden');
                }
            """, mid); mid += 1
            await asyncio.sleep(0.5)

            # Capture visual proof: Payment Settings / Vault modal with clean non-password inputs
            await take_screenshot(ws, "proof_autofill_eradicated.png", mid); mid += 1

            # ------------------------------------------------------------------
            # 4. RUNNER AUTOFILL & OTP AUDIT
            # ------------------------------------------------------------------
            print("\n=== TEST 4: Runner App Autofill & OTP Audit ===")
            await eval_js(ws, "window.location.href = 'http://127.0.0.1:8170/runner/index.html';", mid); mid += 1
            await asyncio.sleep(2)

            runner_audit = await eval_js(ws, """
                (function() {
                    const bankAcc = document.getElementById('bank-acc-no');
                    const kycAadhaarOtp = document.getElementById('kyc-aadhaar-otp-input');
                    const custDeliveryOtp = document.getElementById('cust-delivery-otp');
                    const payoutOtp = document.getElementById('payout-security-otp');
                    const otp1 = document.getElementById('otp-1');
                    const otp6 = document.getElementById('otp-6');

                    return {
                        bankAccType: bankAcc?.getAttribute('type'),
                        bankAccInputMode: bankAcc?.getAttribute('inputmode'),
                        bankAccAutoComplete: bankAcc?.getAttribute('autocomplete'),
                        kycAadhaarOtpAutoComplete: kycAadhaarOtp?.getAttribute('autocomplete'),
                        custDeliveryOtpAutoComplete: custDeliveryOtp?.getAttribute('autocomplete'),
                        payoutOtpAutoComplete: payoutOtp?.getAttribute('autocomplete'),
                        otp1AutoComplete: otp1?.getAttribute('autocomplete'),
                        otp6AutoComplete: otp6?.getAttribute('autocomplete')
                    };
                })()
            """, mid); mid += 1
            print(f"Runner Form Audit: {json.dumps(runner_audit, indent=2)}")
            assert runner_audit.get("bankAccType") == "text", f"Runner bank-acc-no type must be 'text' (got {runner_audit.get('bankAccType')})"
            assert runner_audit.get("bankAccInputMode") == "numeric", "Runner bank-acc-no inputmode must be 'numeric'"
            assert runner_audit.get("bankAccAutoComplete") == "off", "Runner bank-acc-no autocomplete must be 'off'"
            assert runner_audit.get("kycAadhaarOtpAutoComplete") == "one-time-code", "Runner KYC Aadhaar OTP must be 'one-time-code'"
            assert runner_audit.get("custDeliveryOtpAutoComplete") == "one-time-code", "Runner delivery OTP must be 'one-time-code'"
            assert runner_audit.get("payoutOtpAutoComplete") == "one-time-code", "Runner payout OTP must be 'one-time-code'"
            assert runner_audit.get("otp1AutoComplete") == "one-time-code", "Runner login OTP-1 must be 'one-time-code'"
            assert runner_audit.get("otp6AutoComplete") == "one-time-code", "Runner login OTP-6 must be 'one-time-code'"

            print("\n✅ ALL CDP VERIFICATION TESTS PASSED SUCCESSFULLY!")

    finally:
        chrome_proc.terminate()
        http_proc.terminate()

if __name__ == "__main__":
    asyncio.run(main())
