import asyncio
import os
import sys
import json
import time
import subprocess
import urllib.request
import websockets

sys.stdout.reconfigure(encoding='utf-8')

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
TEMP_DIR = r"C:\Users\dhira\AppData\Local\Temp\chrome_debug_cart_3"

async def test_debug():
    http_proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", "8095", "--directory", "public_web"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    time.sleep(1)

    chrome_proc = subprocess.Popen([
        CHROME_PATH,
        "--headless=new",
        "--remote-debugging-port=8094",
        f"--user-data-dir={TEMP_DIR}",
        "http://127.0.0.1:8095/customer/index.html"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)

    try:
        targets_raw = urllib.request.urlopen("http://127.0.0.1:8094/json").read()
        targets = json.loads(targets_raw.decode('utf-8'))
        page_target = next(t for t in targets if t.get("type") == "page")
        ws_url = page_target["webSocketDebuggerUrl"]

        async with websockets.connect(ws_url) as ws:
            expr = """
                (() => {
                    const trace = [];
                    trace.push('window.isLocationServiceable: ' + window.isLocationServiceable);
                    trace.push('cartItems.length: ' + cartItems.length);
                    trace.push('selectedCheckoutAddressId: ' + selectedCheckoutAddressId);
                    
                    try {
                        updateCheckoutModalUI();
                        trace.push('updateCheckoutModalUI succeeded');
                    } catch (e) {
                        trace.push('updateCheckoutModalUI failed: ' + e.toString());
                    }
                    
                    const modal = document.getElementById('modal-checkout-payment');
                    trace.push('modal exists: ' + Boolean(modal));
                    if (modal) {
                        modal.classList.remove('hidden');
                        trace.push('removed hidden. Now classes: ' + modal.className);
                    }
                    return trace;
                })()
            """
            await ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate", "params": {"expression": expr, "returnByValue": True}}))
            resp = json.loads(await ws.recv())
            print("Trace result:", resp.get("result", {}).get("result", {}).get("value"))

    finally:
        chrome_proc.terminate()
        http_proc.terminate()

asyncio.run(test_debug())
