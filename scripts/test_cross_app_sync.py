import asyncio
import subprocess
import os
import sys
import json
import time
import urllib.request
import websockets

sys.stdout.reconfigure(encoding='utf-8')

port = 8097
cdp_port = 9224
chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
temp_dir = r"C:\Users\dhira\AppData\Local\Temp\chrome_cross_eval"

async def test_cross_app():
    # 1. Start HTTP Server if not already responding
    http_proc = None
    try:
        urllib.request.urlopen(f"http://127.0.0.1:{port}/runner/index.html", timeout=1)
        print("HTTP server active on port", port)
    except Exception:
        print("Starting HTTP server on port", port)
        http_proc = subprocess.Popen(
            [sys.executable, "-m", "http.server", str(port), "--directory", "public_web"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        time.sleep(1.5)

    # 2. Check Chrome CDP
    chrome_proc = None
    try:
        urllib.request.urlopen(f"http://127.0.0.1:{cdp_port}/json", timeout=1)
        print("Chrome CDP active on port", cdp_port)
    except Exception:
        print("Starting Chrome on port", cdp_port)
        os.makedirs(temp_dir, exist_ok=True)
        chrome_proc = subprocess.Popen([
            chrome_path,
            f"--remote-debugging-port={cdp_port}",
            f"--user-data-dir={temp_dir}",
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            f"http://127.0.0.1:{port}/customer/index.html"
        ])
        time.sleep(2)

    # Open runner tab
    req = urllib.request.Request(f"http://127.0.0.1:{cdp_port}/json/new?http://127.0.0.1:{port}/runner/index.html", method='PUT')
    urllib.request.urlopen(req)
    await asyncio.sleep(1)

    pages_json = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{cdp_port}/json").read())
    cust_page = next((p for p in pages_json if "customer" in p.get("url", "")), None)
    runner_page = next((p for p in pages_json if "runner" in p.get("url", "")), None)

    print("Connecting to Customer page WebSocket...")
    async with websockets.connect(cust_page["webSocketDebuggerUrl"], max_size=10_000_000) as ws_cust, \
               websockets.connect(runner_page["webSocketDebuggerUrl"], max_size=10_000_000) as ws_runner:
        
        await ws_cust.send(json.dumps({"id": 1, "method": "Runtime.enable"}))
        await ws_runner.send(json.dumps({"id": 1, "method": "Runtime.enable"}))

        # Setup customer active order
        await ws_cust.send(json.dumps({
            "id": 2,
            "method": "Runtime.evaluate",
            "params": {
                "expression": """
                localStorage.setItem('gb_active_order_id', 'GB-8921');
                switchTab('orders');
                renderVerticalOrderTrackingTimeline([], 'ACCEPTED');
                document.getElementById('order-status-text').innerText;
                """,
                "returnByValue": True
            }
        }))
        msg_cust = json.loads(await ws_cust.recv())
        while msg_cust.get("id") != 2: msg_cust = json.loads(await ws_cust.recv())
        print("Customer initial order status:", msg_cust["result"]["result"]["value"])

        # In Runner: Setup and click confirmVendorPickup()
        print("Triggering Runner Confirm Pickup...")
        await ws_runner.send(json.dumps({
            "id": 3,
            "method": "Runtime.evaluate",
            "params": {
                "expression": """
                localStorage.setItem('gaonbazaar_runner_token', 'mock_runner_token_8899');
                openDashboard('activerun', false);
                confirmVendorPickup();
                """,
                "awaitPromise": True
            }
        }))
        msg_runner = json.loads(await ws_runner.recv())
        while msg_runner.get("id") != 3: msg_runner = json.loads(await ws_runner.recv())

        # Give 500ms for BroadcastChannel / event propagation
        await asyncio.sleep(0.5)

        # In Customer: Check if order-status-text and vertical progress updated to OUT_FOR_DELIVERY
        await ws_cust.send(json.dumps({
            "id": 4,
            "method": "Runtime.evaluate",
            "params": {
                "expression": """
                (() => {
                  const text = document.getElementById('order-status-text')?.innerText;
                  const vertical = document.getElementById('order-tracking-vertical')?.textContent;
                  const hasOutForDelivery = vertical && vertical.includes('Out for Delivery');
                  return { text, hasOutForDelivery };
                })()
                """,
                "returnByValue": True
            }
        }))
        msg_check = json.loads(await ws_cust.recv())
        while msg_check.get("id") != 4: msg_check = json.loads(await ws_cust.recv())
        val = msg_check["result"]["result"]["value"]
        print("Customer updated status after Runner pickup:", val)
        assert "Out for Delivery" in val["text"] or val["hasOutForDelivery"], "Customer progress updated to Out for Delivery"
        print("[PASS] Cross-app synchronization successfully verified in real time!")
        return True

    if chrome_proc: chrome_proc.terminate()
    if http_proc: http_proc.terminate()

if __name__ == "__main__":
    success = asyncio.run(test_cross_app())
    sys.exit(0 if success else 1)
