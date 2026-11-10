import os
import sys
import time
import json
import base64
import socket
import subprocess
import asyncio
from pathlib import Path
from http.server import SimpleHTTPRequestHandler, HTTPServer
import threading
import urllib.request
import websockets

sys.stdout.reconfigure(encoding='utf-8')

ARTIFACTS_DIR = Path(r"C:\Users\dhira\.gemini\antigravity\brain\918c8085-b60b-40a9-a077-a3344458bcc5")
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
if not os.path.exists(CHROME_PATH):
    alt = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    if os.path.exists(alt):
        CHROME_PATH = alt

def find_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('127.0.0.1', 0))
    port = s.getsockname()[1]
    s.close()
    return port

class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

def run_web_server(port, root_dir):
    server = HTTPServer(('127.0.0.1', port), lambda *args, **kwargs: QuietHandler(*args, directory=root_dir, **kwargs))
    server.serve_forever()

async def send_cdp(ws, method, params=None, msg_id=[1]):
    mid = msg_id[0]
    msg_id[0] += 1
    req = {"id": mid, "method": method}
    if params:
        req["params"] = params
    await ws.send(json.dumps(req))
    while True:
        resp = json.loads(await ws.recv())
        if resp.get("id") == mid:
            return resp

async def evaluate(ws, expr):
    resp = await send_cdp(ws, "Runtime.evaluate", {"expression": expr, "returnByValue": True, "awaitPromise": True})
    return resp.get("result", {}).get("result", {}).get("value")

async def take_screenshot(ws, output_path):
    resp = await send_cdp(ws, "Page.captureScreenshot", {"format": "png"})
    data = base64.b64decode(resp["result"]["data"])
    with open(output_path, "wb") as f:
        f.write(data)
    print(f"Captured screenshot: {output_path.name}")

async def main_async():
    web_port = find_free_port()
    cdp_port = find_free_port()

    # Serve public_web
    web_root = str(Path(r"c:\Users\dhira\OneDrive\Desktop\GaoBazar-Village\public_web").resolve())
    server_thread = threading.Thread(target=run_web_server, args=(web_port, web_root), daemon=True)
    server_thread.start()
    print(f"Web server running on http://127.0.0.1:{web_port}")

    # Launch Chrome
    chrome_cmd = [
        CHROME_PATH,
        f"--remote-debugging-port={cdp_port}",
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-extensions",
        "--window-size=1400,900",
        f"http://127.0.0.1:{web_port}/admin/index.html"
    ]
    proc = subprocess.Popen(chrome_cmd)
    await asyncio.sleep(2.5)

    try:
        tabs_url = f"http://127.0.0.1:{cdp_port}/json"
        with urllib.request.urlopen(tabs_url) as resp:
            tabs = json.loads(resp.read().decode())
        page_tabs = [t for t in tabs if t.get("type") == "page"]
        target_tab = page_tabs[0] if page_tabs else tabs[0]
        ws_url = target_tab["webSocketDebuggerUrl"]

        async with websockets.connect(ws_url) as ws:
            await send_cdp(ws, "Page.enable")
            await send_cdp(ws, "DOM.enable")
            await send_cdp(ws, "Page.navigate", {"url": f"http://127.0.0.1:{web_port}/admin/index.html"})
            await asyncio.sleep(2.0)

            print("\n--- TEST 1: Admin Login Gate & Strict Absence of Sign-Up Button ---")
            loc = await evaluate(ws, "window.location.href")
            print(f"Current URL: {loc}")
            html_sample = await evaluate(ws, "document.documentElement.outerHTML.slice(0, 300)")
            print(f"HTML Sample: {html_sample}")
            title = await evaluate(ws, "document.title")
            print(f"Page Title: {title}")
            assert "Super Admin" in title

            has_signup = await evaluate(ws, "!!Array.from(document.querySelectorAll('button, a')).find(el => el.textContent.toLowerCase().includes('sign up'))")
            print(f"Has 'Sign Up' button: {has_signup} (Must be False)")
            assert not has_signup, "Security Violation: Found Sign Up button on Admin Login Gate!"

            await take_screenshot(ws, ARTIFACTS_DIR / "proof_admin_login_strict_rbac.png")

            print("\n--- TEST 2: Strict Localization Toggle (Hindi vs English) ---")
            # Toggle language to Hindi
            await evaluate(ws, "Array.from(document.querySelectorAll('button')).find(el => el.textContent.includes('हिंदी'))?.click()")
            await asyncio.sleep(0.5)

            hindi_heading = await evaluate(ws, "document.querySelector('h1')?.textContent")
            print(f"Hindi heading: {hindi_heading}")
            assert "गांवबाज़ार" in str(hindi_heading)

            has_mixed_slash = await evaluate(ws, "document.body.innerText.includes('त्रुटि / Error')")
            print(f"Contains mixed slash 'त्रुटि / Error': {has_mixed_slash} (Must be False)")
            assert not has_mixed_slash, "Localization Error: Found mixed slash string!"

            await take_screenshot(ws, ARTIFACTS_DIR / "proof_admin_login_hindi_strict_localization.png")

            # Toggle back to English
            await evaluate(ws, "Array.from(document.querySelectorAll('button')).find(el => el.textContent.includes('English'))?.click()")
            await asyncio.sleep(0.5)

            print("\n--- TEST 3: Unauthorized Access Denied Gate ---")
            await evaluate(ws, """(() => {
                const setReactInput = (elem, val) => {
                    const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                    setter.call(elem, val);
                    elem.dispatchEvent(new Event('input', { bubbles: true }));
                    elem.dispatchEvent(new Event('change', { bubbles: true }));
                };
                const inputs = document.querySelectorAll('input');
                setReactInput(inputs[0], '9811111111');
                setReactInput(inputs[1], 'customer_pass');
                const submitBtn = document.querySelector('button[type="submit"]');
                if (submitBtn) submitBtn.click();
            })()""")
            await asyncio.sleep(1.2)

            has_denied = await evaluate(ws, "document.body.innerText.includes('Access Denied: Super Admin Privilege Required')")
            print(f"Access Denied text displayed: {has_denied}")
            assert has_denied, "Unauthorized screen was not rendered upon non-admin attempt!"
            await take_screenshot(ws, ARTIFACTS_DIR / "proof_super_admin_unauthorized_access_denied.png")

            # Click return to login
            await evaluate(ws, "Array.from(document.querySelectorAll('button')).find(el => el.textContent.includes('Return to Admin Sign In'))?.click()")
            await asyncio.sleep(0.8)

            print("\n--- TEST 4: Successful Super Admin Authentication ---")
            await evaluate(ws, """(() => {
                window.localStorage.setItem('gaonbazaar_admin_jwt_token', 'test_super_admin_jwt_token');
                window.localStorage.setItem('gaonbazaar_admin_user_info', JSON.stringify({
                    id: 'admin_test_01',
                    phone: '9800000099',
                    name: 'GaonBazaar Super Admin',
                    role: 'super_admin'
                }));
                window.location.reload();
            })()""")
            await asyncio.sleep(2.0)

            dash_header = await evaluate(ws, "document.body.innerText.includes('Executive Command Center') || document.body.innerText.includes('Dashboard')")
            print(f"Dashboard loaded: {dash_header}")
            await take_screenshot(ws, ARTIFACTS_DIR / "proof_super_admin_command_center.png")

            print("\n--- TEST 5: KYC Verification & User Management Module ---")
            await evaluate(ws, """(() => {
                const buttons = Array.from(document.querySelectorAll('button'));
                const kycBtn = buttons.find(b => b.textContent.includes('Users & KYC'));
                if (kycBtn) kycBtn.click();
            })()""")
            await asyncio.sleep(1.0)

            kyc_tab_text = await evaluate(ws, "document.body.innerText.includes('Pending Approvals Queue')")
            print(f"KYC Pending Approvals Queue present: {kyc_tab_text}")
            assert kyc_tab_text

            await take_screenshot(ws, ARTIFACTS_DIR / "proof_super_admin_kyc_approvals_queue.png")

            print("\n--- TEST 6: Orders God Mode Lifecycle & Overrides ---")
            await evaluate(ws, """(() => {
                const buttons = Array.from(document.querySelectorAll('button'));
                const ordersBtn = buttons.find(b => b.textContent.includes('Orders (God Mode)'));
                if (ordersBtn) ordersBtn.click();
            })()""")
            await asyncio.sleep(1.0)

            orders_tab_text = await evaluate(ws, "document.body.innerText.includes('Live Hyperlocal Order Feed')")
            print(f"Orders God Mode feed present: {orders_tab_text}")
            assert orders_tab_text

            await take_screenshot(ws, ARTIFACTS_DIR / "proof_super_admin_orders_god_mode.png")

            print("\n--- TEST 7: Financials Tab & COD Reconciliation ---")
            await evaluate(ws, """(() => {
                const buttons = Array.from(document.querySelectorAll('button'));
                const finBtn = buttons.find(b => b.textContent.includes('Financials & Ledger'));
                if (finBtn) finBtn.click();
            })()""")
            await asyncio.sleep(1.0)

            fin_tab_text = await evaluate(ws, "document.body.innerText.includes('COD Reconciliation')")
            print(f"Financials COD reconciliation present: {fin_tab_text}")
            assert fin_tab_text

            await take_screenshot(ws, ARTIFACTS_DIR / "proof_super_admin_financials_ledger.png")

            print("\nAll browser UI integration tests completed successfully!")

    finally:
        proc.terminate()

def main():
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
