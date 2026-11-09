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
TEMP_DIR = r"C:\Users\dhira\AppData\Local\Temp\chrome_checkout_vault_test"
ARTIFACT_DIR = r"C:\Users\dhira\OneDrive\Desktop\GaoBazar-Village"
BRAIN_DIR = r"C:\Users\dhira\.gemini\antigravity\brain\918c8085-b60b-40a9-a077-a3344458bcc5"
PUB_DIR = os.path.abspath("public_web")

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
        [sys.executable, "-m", "http.server", "8120", "--directory", PUB_DIR],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    time.sleep(1.5)

    chrome_proc = subprocess.Popen([
        CHROME_PATH,
        "--headless=new",
        "--remote-debugging-port=8121",
        f"--user-data-dir={TEMP_DIR}",
        "--window-size=412,915",
        "http://127.0.0.1:8120/customer/index.html"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)

    try:
        targets_raw = urllib.request.urlopen("http://127.0.0.1:8121/json").read()
        targets = json.loads(targets_raw.decode('utf-8'))
        page_target = next(t for t in targets if t.get("type") == "page")
        ws_url = page_target["webSocketDebuggerUrl"]

        async with websockets.connect(ws_url) as ws:
            mid = 1
            await ws.send(json.dumps({"id": mid, "method": "Page.enable"})); mid += 1
            await ws.recv()

            # ------------------------------------------------------------------
            # 1. TEST INTERACTIVE PAYMENT SETTINGS VAULT (CUSTOMER APP)
            # ------------------------------------------------------------------
            print("\n=== 1. Testing Interactive Payment Settings Vault ===")
            await eval_js(ws, """
                localStorage.clear();
                sessionStorage.clear();
                localStorage.setItem('gb_customer_authenticated', 'true');
                localStorage.setItem('gb_customer_phone', '9905361711');
                location.reload();
            """, mid); mid += 1
            await asyncio.sleep(2)

            # Go to Account tab
            await eval_js(ws, "switchTab('account')", mid); mid += 1
            await asyncio.sleep(1)

            # Open Payment Settings Vault
            await eval_js(ws, "openPaymentSettingsModal()", mid); mid += 1
            await asyncio.sleep(1)

            vault_visible = await eval_js(ws, "!document.getElementById('modal-payment-settings')?.classList.contains('hidden')", mid); mid += 1
            vault_title = await eval_js(ws, "document.querySelector('#modal-payment-settings h3')?.innerText?.trim()", mid); mid += 1
            fee_guarantee_exists = await eval_js(ws, "document.getElementById('modal-payment-settings')?.innerText.includes('Platform Fee Guarantee')", mid); mid += 1

            print(f"Vault Modal Visible: {vault_visible}")
            print(f"Vault Title: {vault_title}")
            print(f"Platform Fee Guarantee Clutter Exists: {fee_guarantee_exists} (Expected: False)")
            assert vault_visible, "Payment Settings Vault should be visible"
            assert "Vault" in vault_title or "Payment" in vault_title, "Vault title should match"
            assert not fee_guarantee_exists, "Platform Fee Guarantee clutter MUST be removed from Payment Settings!"

            # Test switching between UPI and Bank tabs
            print("Testing Vault Tabs...")
            await eval_js(ws, "switchVaultTab('bank')", mid); mid += 1
            await asyncio.sleep(0.5)
            bank_form_visible = await eval_js(ws, "!document.getElementById('vault-form-bank')?.classList.contains('hidden')", mid); mid += 1
            print(f"Bank Form Visible: {bank_form_visible}")
            assert bank_form_visible, "Bank form should be visible on bank tab"

            await eval_js(ws, "switchVaultTab('upi')", mid); mid += 1
            await asyncio.sleep(0.5)
            upi_form_visible = await eval_js(ws, "!document.getElementById('vault-form-upi')?.classList.contains('hidden')", mid); mid += 1
            print(f"UPI Form Visible: {upi_form_visible}")
            assert upi_form_visible, "UPI form should be visible on upi tab"

            # Set a custom UPI ID and save
            await eval_js(ws, "document.getElementById('vault-upi-input').value = '9905361711@paytm'", mid); mid += 1
            await take_screenshot(ws, "proof_customer_payment_vault.png", mid); mid += 1

            await eval_js(ws, "saveCustomerPaymentVault()", mid); mid += 1
            await asyncio.sleep(1)

            saved_upi = await eval_js(ws, "localStorage.getItem('gb_customer_upi_id')", mid); mid += 1
            saved_setup = await eval_js(ws, "localStorage.getItem('gb_customer_payment_setup')", mid); mid += 1
            print(f"Saved UPI ID in localStorage: {saved_upi}, setup completed: {saved_setup}")
            assert saved_upi == '9905361711@paytm', "Saved UPI must match input"
            assert saved_setup == 'true', "Payment setup flag must be true"

            # ------------------------------------------------------------------
            # 2. TEST SMART CART ROUTING & CHECKOUT PIPELINE
            # ------------------------------------------------------------------
            print("\n=== 2. Testing Smart Cart Routing Pipeline ===")
            # 2.A: Test New Customer Pipeline (No Address -> Step 1 Address -> Step 2 Vault -> Payment Modal)
            await eval_js(ws, """
                localStorage.removeItem('gb_saved_addresses');
                localStorage.removeItem('gb_customer_payment_setup');
                localStorage.removeItem('gb_customer_upi_id');
                window.userSavedAddresses = [];
                window.activeCustomerAddress = { village: '' };
                addToCart('p1'); // add item to cart
                switchTab('cart');
            """, mid); mid += 1
            await asyncio.sleep(1)

            # Click Checkout as a new customer
            print("Clicking Checkout as a brand new customer...")
            await eval_js(ws, "handleCartCheckoutClick()", mid); mid += 1
            await asyncio.sleep(1)

            # Verify it routed strictly to Step 1: Address Modal
            addr_modal_visible = await eval_js(ws, "!document.getElementById('modal-rural-address')?.classList.contains('hidden')", mid); mid += 1
            print(f"Step 1 - Address Modal Visible: {addr_modal_visible}")
            assert addr_modal_visible, "New customer must be routed to Step 1 Address Setup!"

            # Fill address and save
            await eval_js(ws, """
                document.getElementById('modal-recipient-input').value = 'Ramesh Kumar';
                document.getElementById('modal-phone-input').value = '9905361711';
                document.getElementById('modal-village-input').value = 'Chaturshi';
                document.getElementById('modal-landmark-input').value = 'Near Shiv Mandir';
                saveCustomerAddress();
            """, mid); mid += 1
            await asyncio.sleep(1.5)

            # Verify it automatically advanced to Step 2: Payment Vault
            vault_modal_auto_opened = await eval_js(ws, "!document.getElementById('modal-payment-settings')?.classList.contains('hidden')", mid); mid += 1
            print(f"Step 2 - Payment Vault Auto-Opened: {vault_modal_auto_opened}")
            assert vault_modal_auto_opened, "New customer must advance from Address to Step 2 Payment Vault!"

            # Save in vault
            await eval_js(ws, "saveCustomerPaymentVault()", mid); mid += 1
            await asyncio.sleep(1.5)

            # Verify it automatically advanced to the Payment Selection Modal
            pay_modal_auto_opened = await eval_js(ws, "!document.getElementById('modal-checkout-payment')?.classList.contains('hidden')", mid); mid += 1
            print(f"Payment Selection Modal Auto-Opened: {pay_modal_auto_opened}")
            assert pay_modal_auto_opened, "Must advance to Payment Selection Modal!"

            # 2.B: Test Explicit Payment Selection Modal Options
            has_upi_option = await eval_js(ws, "!!document.getElementById('checkout-opt-upi')", mid); mid += 1
            has_cod_option = await eval_js(ws, "!!document.getElementById('checkout-opt-cod')", mid); mid += 1
            has_brand_chips = await eval_js(ws, "document.querySelectorAll('#checkout-opt-upi span').length >= 4", mid); mid += 1

            print(f"Payment Modal - UPI option: {has_upi_option}, COD option: {has_cod_option}, Brands: {has_brand_chips}")
            assert has_upi_option and has_cod_option, "Must present both UPI and COD options"

            # Test selecting COD option
            await eval_js(ws, "selectCheckoutModalPayment('COD')", mid); mid += 1
            await asyncio.sleep(0.5)
            cod_btn_text = await eval_js(ws, "document.getElementById('btn-checkout-modal-text')?.innerText", mid); mid += 1
            print(f"Selected COD - CTA Button Text: {cod_btn_text}")
            assert "COD" in cod_btn_text, "Button must reflect COD selection"

            # Select UPI option
            await eval_js(ws, "selectCheckoutModalPayment('ONLINE')", mid); mid += 1
            await asyncio.sleep(0.5)
            upi_btn_text = await eval_js(ws, "document.getElementById('btn-checkout-modal-text')?.innerText", mid); mid += 1
            print(f"Selected UPI - CTA Button Text: {upi_btn_text}")
            assert "UPI" in upi_btn_text, "Button must reflect UPI selection"

            await take_screenshot(ws, "proof_customer_checkout_payment_modal.png", mid); mid += 1

            # Close modal
            await eval_js(ws, "closeCheckoutPaymentModal()", mid); mid += 1
            await asyncio.sleep(0.5)

            # 2.C: Test Returning Customer Pipeline (Direct to Payment Modal, NO setup screens)
            print("\nTesting Returning Customer Checkout...")
            await eval_js(ws, "handleCartCheckoutClick()", mid); mid += 1
            await asyncio.sleep(0.5)

            ret_addr_hidden = await eval_js(ws, "document.getElementById('modal-rural-address')?.classList.contains('hidden')", mid); mid += 1
            ret_vault_hidden = await eval_js(ws, "document.getElementById('modal-payment-settings')?.classList.contains('hidden')", mid); mid += 1
            ret_pay_modal_visible = await eval_js(ws, "!document.getElementById('modal-checkout-payment')?.classList.contains('hidden')", mid); mid += 1

            print(f"Returning Customer - Address Modal Hidden: {ret_addr_hidden}")
            print(f"Returning Customer - Vault Modal Hidden: {ret_vault_hidden}")
            print(f"Returning Customer - Payment Modal Directly Visible: {ret_pay_modal_visible}")
            assert ret_addr_hidden and ret_vault_hidden, "Setup screens must NOT appear for returning customers!"
            assert ret_pay_modal_visible, "Payment Selection Modal must directly open for returning customers!"

            # ------------------------------------------------------------------
            # 3. TEST VENDOR BILINGUAL & ALPHABETICAL LOCATION SEARCH
            # ------------------------------------------------------------------
            print("\n=== 3. Testing Vendor Bilingual & Alphabetical Search ===")
            await eval_js(ws, "location.href = 'http://127.0.0.1:8120/vendor/index.html'", mid); mid += 1
            await asyncio.sleep(2)
            await eval_js(ws, "localStorage.clear(); sessionStorage.clear(); location.reload();", mid); mid += 1
            await asyncio.sleep(2)

            # Navigate directly to Step 4 Location
            await eval_js(ws, "navigateTo('onboarding-4')", mid); mid += 1
            await asyncio.sleep(1)

            # Check initial value is bilingual
            v_init_val = await eval_js(ws, "document.getElementById('vendor-village-name')?.value", mid); mid += 1
            print(f"Vendor Initial Village Value: {v_init_val}")
            assert "Muzaffarpur" in v_init_val and "मुज़फ़्फ़रपुर" in v_init_val, "Initial value should be bilingual"

            # Trigger full dropdown
            await eval_js(ws, "handleVendorVillageSearch('')", mid); mid += 1
            await asyncio.sleep(0.5)

            # Check items
            v_items = await eval_js(ws, """
                Array.from(document.querySelectorAll('#vendor-village-dropdown > div')).map(d => d.innerText.trim())
            """, mid); mid += 1
            print(f"Vendor Dropdown Items Count: {len(v_items)}")
            print(f"First 3 Vendor Items: {v_items[:3]}")

            # Verify bilingual format (e.g. Aurai / औराई)
            assert "/" in v_items[0], "Items must be bilingual (contains '/')"
            # Verify strict alphabetical sorting (A to Z)
            first_name = v_items[0].split('/')[0].strip()
            second_name = v_items[1].split('/')[0].strip()
            print(f"Alphabetical check: {first_name} <= {second_name}")
            assert first_name.startswith('A'), f"First item must start with A (Aurai), got: {first_name}"
            assert first_name <= second_name, "Items must be in alphabetical order"

            await take_screenshot(ws, "proof_vendor_bilingual_dropdown.png", mid); mid += 1

            # ------------------------------------------------------------------
            # 4. TEST RUNNER BILINGUAL & ALPHABETICAL LOCATION SEARCH
            # ------------------------------------------------------------------
            print("\n=== 4. Testing Runner Bilingual & Alphabetical Search ===")
            await eval_js(ws, "location.href = 'http://127.0.0.1:8120/runner/index.html'", mid); mid += 1
            await asyncio.sleep(2)
            await eval_js(ws, "localStorage.clear(); sessionStorage.clear(); location.reload();", mid); mid += 1
            await asyncio.sleep(2)

            # Navigate directly to Step 4 Location
            await eval_js(ws, "navigateTo('onboarding-4')", mid); mid += 1
            await asyncio.sleep(1)

            # Check initial value is bilingual
            r_init_val = await eval_js(ws, "document.getElementById('runner-base-village')?.value", mid); mid += 1
            print(f"Runner Initial Village Value: {r_init_val}")
            assert "Muzaffarpur" in r_init_val and "मुज़फ़्फ़रपुर" in r_init_val, "Initial value should be bilingual"

            # Trigger full dropdown
            await eval_js(ws, "handleRunnerVillageSearch('')", mid); mid += 1
            await asyncio.sleep(0.5)

            # Check items
            r_items = await eval_js(ws, """
                Array.from(document.querySelectorAll('#runner-village-dropdown > div')).map(d => d.innerText.trim())
            """, mid); mid += 1
            print(f"Runner Dropdown Items Count: {len(r_items)}")
            print(f"First 3 Runner Items: {r_items[:3]}")

            # Verify bilingual format
            assert "/" in r_items[0], "Items must be bilingual (contains '/')"
            r_first_name = r_items[0].split('/')[0].strip()
            r_second_name = r_items[1].split('/')[0].strip()
            print(f"Alphabetical check: {r_first_name} <= {r_second_name}")
            assert r_first_name.startswith('A'), f"First item must start with A (Aurai), got: {r_first_name}"
            assert r_first_name <= r_second_name, "Items must be in alphabetical order"

            await take_screenshot(ws, "proof_runner_bilingual_dropdown.png", mid); mid += 1

            print("\nALL CHECKOUT PIPELINE & BILINGUAL LOCATION TESTS PASSED 100% PERFECTLY!")

    finally:
        chrome_proc.terminate()
        http_proc.terminate()

if __name__ == "__main__":
    asyncio.run(run_tests())
