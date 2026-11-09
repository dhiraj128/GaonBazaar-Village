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
TEMP_DIR = r"C:\Users\dhira\AppData\Local\Temp\chrome_debug_cart_2"

async def test_debug():
    http_proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", "8097", "--directory", "public_web"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    time.sleep(1)

    chrome_proc = subprocess.Popen([
        CHROME_PATH,
        "--headless=new",
        "--remote-debugging-port=8096",
        f"--user-data-dir={TEMP_DIR}",
        "http://127.0.0.1:8097/customer/index.html"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)

    try:
        targets_raw = urllib.request.urlopen("http://127.0.0.1:8096/json").read()
        targets = json.loads(targets_raw.decode('utf-8'))
        page_target = next(t for t in targets if t.get("type") == "page")
        ws_url = page_target["webSocketDebuggerUrl"]

        async with websockets.connect(ws_url) as ws:
            expr = """
                (async () => {
                    const logs = [];
                    try {
                        cartItems = [{ id: 'p1', name: 'Item', price: 100, quantity: 1, storeId: 's1' }];
                        renderCartItems();
                        selectedCheckoutAddressId = 'addr_1';
                        window.isLocationServiceable = true;
                        
                        logs.push('Before call');
                        const p = openCheckoutPaymentModal();
                        logs.push('Called');
                        await p;
                        logs.push('Awaited');

                        const m = document.getElementById('modal-checkout-payment');
                        return {
                            logs: logs,
                            hasModal: Boolean(m),
                            classList: m ? Array.from(m.classList) : null
                        };
                    } catch (e) {
                        return { logs: logs, error: e.toString(), stack: e.stack };
                    }
                })()
            """
            await ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate", "params": {"expression": expr, "returnByValue": True, "awaitPromise": True}}))
            resp = json.loads(await ws.recv())
            print("Step by step result:", resp.get("result", {}).get("result", {}).get("value"))

    finally:
        chrome_proc.terminate()
        http_proc.terminate()

asyncio.run(test_debug())
