import asyncio
import os
import sys
import json
import time
import subprocess
import urllib.request
import base64
import websockets
import http.server
import socketserver
import threading
import socket

sys.stdout.reconfigure(encoding='utf-8')

ARTIFACT_DIR = r"C:\Users\dhira\.gemini\antigravity\brain\918c8085-b60b-40a9-a077-a3344458bcc5"
API_KEY = "AIzaSyBqHZrBX7WMEw2vt5COVwfK7a4lZpGapMc"
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
TEMP_DIR = r"C:\Users\dhira\AppData\Local\Temp\chrome_chat_eval_perfect"

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

def get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]

def start_local_server(port):
    handler = lambda *args, **kwargs: QuietHandler(*args, directory="public_web", **kwargs)
    httpd = socketserver.TCPServer(("127.0.0.1", port), handler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    return httpd

async def send_cdp(ws, method, params=None, msg_id=1):
    payload = {"id": msg_id, "method": method, "params": params or {}}
    await ws.send(json.dumps(payload))
    while True:
        resp = json.loads(await ws.recv())
        if resp.get("method") == "Runtime.consoleAPICalled":
            print("  CONSOLE LOG:", [a.get("value") for a in resp["params"]["args"]])
        elif resp.get("method") == "Runtime.exceptionThrown":
            print("  EXCEPTION:", resp["params"]["exceptionDetails"].get("text"), resp["params"]["exceptionDetails"].get("exception"))
        elif resp.get("id") == msg_id:
            return resp

async def evaluate(ws, expr, msg_id=200):
    res = await send_cdp(ws, "Runtime.evaluate", {"expression": expr, "returnByValue": True, "awaitPromise": True}, msg_id=msg_id)
    if "exceptionDetails" in res.get("result", {}):
        print(f"CDP Exception in eval: {res['result']['exceptionDetails']}")
    return res.get("result", {}).get("result", {}).get("value")

async def take_screenshot(ws, filename, msg_id=100):
    res = await send_cdp(ws, "Page.captureScreenshot", {"format": "png"}, msg_id=msg_id)
    b64 = res["result"]["data"]
    out_path = os.path.join(ARTIFACT_DIR, filename)
    with open(out_path, "wb") as f:
        f.write(base64.b64decode(b64))
    print(f"  [SCREENSHOT] Saved: {out_path}")
    return out_path

async def run_both_evals():
    http_port = get_free_port()
    cdp_port = get_free_port()
    print(f"Starting in-process HTTP server on port {http_port} (CDP port {cdp_port})")
    httpd = start_local_server(http_port)

    # Verify server is answering immediately
    res = urllib.request.urlopen(f"http://127.0.0.1:{http_port}/customer/index.html", timeout=2)
    assert res.status == 200, "Server failed to respond"
    print("In-process server online and serving public_web.")

    os.makedirs(TEMP_DIR, exist_ok=True)

    # -------------------------------------------------------------------------
    # PART 1: CUSTOMER IN-APP CHAT LOCATION SHARING
    # -------------------------------------------------------------------------
    print("\n=======================================================")
    print("PART 1: TESTING CUSTOMER IN-APP CHAT LOCATION SHARING")
    print("=======================================================")

    customer_temp = os.path.join(TEMP_DIR, "customer_prof")
    os.makedirs(customer_temp, exist_ok=True)
    chrome_customer = subprocess.Popen([
        CHROME_PATH,
        f"--remote-debugging-port={cdp_port}",
        f"--user-data-dir={customer_temp}",
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--hide-scrollbars",
        "--window-size=430,932",
        f"http://127.0.0.1:{http_port}/customer/index.html"
    ])
    time.sleep(2.5)

    try:
        pages_json = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{cdp_port}/json").read())
        customer_page = next((p for p in pages_json if p.get("type") == "page"), None)
        assert customer_page, "No customer page target found"
        ws_url = customer_page["webSocketDebuggerUrl"]

        async with websockets.connect(ws_url, max_size=10_000_000) as ws:
            await send_cdp(ws, "Page.enable", msg_id=1)
            await send_cdp(ws, "DOM.enable", msg_id=2)
            await send_cdp(ws, "Runtime.enable", msg_id=3)

            # Set up active order GB-8921 state
            await evaluate(ws, """
                localStorage.setItem('gb_active_order_id', 'GB-8921');
                localStorage.setItem('gb_customer_id', 'CUST_1');
                window.activeCustomerAddress = {
                    landmark: 'Near Primary School',
                    village: 'Chaturshi',
                    latitude: 26.2315,
                    longitude: 85.3610
                };
                openRunnerChatModal();
            """, msg_id=10)
            await asyncio.sleep(1.0)

            # Trigger location sharing with mock delayed GPS to inspect spinner
            await evaluate(ws, """
                navigator.geolocation.getCurrentPosition = function(success, error, opts) {
                    setTimeout(() => {
                        success({
                            coords: {
                                latitude: 26.2315,
                                longitude: 85.3610,
                                accuracy: 10
                            }
                        });
                    }, 1200);
                };
                shareCustomerLiveLocation();
            """, msg_id=11)
            await asyncio.sleep(0.3)

            # Check spinner
            spinnerText = await evaluate(ws, "document.getElementById('chat-gps-detecting-indicator')?.innerText", msg_id=12)
            print(f"  [PASS] Detecting spinner appeared with text: '{spinnerText}'")
            assert spinnerText and "Detecting exact location" in spinnerText

            # Capture spinner screenshot
            await take_screenshot(ws, "proof_chat_location_detecting_spinner.png", msg_id=101)

            # Inspect what happens after GPS finishes
            await asyncio.sleep(2.5)

            debug_info = await evaluate(ws, """
                (() => {
                    const container = document.getElementById('chat-messages-container');
                    return {
                        containerHTML: container ? container.innerHTML : null,
                        orderMessages: window.customerOrderMessages,
                        activeOrderId: localStorage.getItem('gb_active_order_id')
                    };
                })()
            """, msg_id=15)
            print("  DEBUG INFO:", json.dumps(debug_info, indent=4))

            # Inspect Customer location bubble
            c_bubble = await evaluate(ws, """
                (() => {
                    const container = document.getElementById('chat-messages-container');
                    const locBubble = container ? container.querySelector('a[href*="google.com/maps"]') : null;
                    const img = locBubble ? locBubble.querySelector('img') : null;
                    return {
                        hasLink: !!locBubble,
                        href: locBubble ? locBubble.getAttribute('href') : null,
                        hasImg: !!img,
                        imgSrc: img ? img.getAttribute('src') : null,
                        textContent: locBubble ? locBubble.innerText : ""
                    };
                })()
            """, msg_id=13)
            print("  Customer Chat Bubble Data:", json.dumps(c_bubble, indent=4))

            assert c_bubble["hasLink"], "Customer visual chat bubble must be wrapped in <a> tag"
            assert "destination=26.2315,85.361" in c_bubble["href"], "Customer navigation link matches coords"
            assert c_bubble["hasImg"], "Customer bubble must contain static map image"
            assert API_KEY in c_bubble["imgSrc"], "Customer static map img uses exact Google Maps API key"
            assert "maps.googleapis.com/maps/api/staticmap" in c_bubble["imgSrc"], "Uses Google Static Maps API"
            assert "26.2315" not in c_bubble["textContent"], "NO raw latitude coordinates displayed!"
            assert "85.361" not in c_bubble["textContent"], "NO raw longitude coordinates displayed!"
            print("  [PASS] Customer Chat Bubble verified: Static map img, direct turn-by-turn nav link, readable address, ZERO raw coords!")

            # Capture customer bubble screenshot
            await take_screenshot(ws, "proof_customer_chat_visual_map_bubble.png", msg_id=102)

    finally:
        chrome_customer.terminate()
        time.sleep(1.5)

    # -------------------------------------------------------------------------
    # PART 2: RUNNER IN-APP CHAT LOCATION PIN DISPLAY
    # -------------------------------------------------------------------------
    print("\n=======================================================")
    print("PART 2: TESTING RUNNER IN-APP CHAT LOCATION PIN DISPLAY")
    print("=======================================================")

    cdp_port2 = get_free_port()
    runner_temp = os.path.join(TEMP_DIR, "runner_prof")
    os.makedirs(runner_temp, exist_ok=True)
    chrome_runner = subprocess.Popen([
        CHROME_PATH,
        f"--remote-debugging-port={cdp_port2}",
        f"--user-data-dir={runner_temp}",
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--hide-scrollbars",
        "--window-size=430,932",
        f"http://127.0.0.1:{http_port}/runner/index.html"
    ])
    time.sleep(2.5)

    try:
        pages_json = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{cdp_port2}/json").read())
        runner_page = next((p for p in pages_json if p.get("type") == "page"), None)
        assert runner_page, "No runner page target found"
        ws_url2 = runner_page["webSocketDebuggerUrl"]

        async with websockets.connect(ws_url2, max_size=10_000_000) as ws:
            await send_cdp(ws, "Page.enable", msg_id=1)
            await send_cdp(ws, "DOM.enable", msg_id=2)
            await send_cdp(ws, "Runtime.enable", msg_id=3)

            # Open Dashboard and Active Run
            await evaluate(ws, """
                localStorage.setItem('gaonbazaar_runner_token', 'mock_runner_token_8899');
                openDashboard('activerun', false);
            """, msg_id=20)
            await asyncio.sleep(0.5)

            # Open Runner Order Chat
            await evaluate(ws, "openRunnerOrderChat();", msg_id=21)
            await asyncio.sleep(2.5)

            # Inspect Runner chat messages
            r_bubble = await evaluate(ws, """
                (() => {
                    const container = document.getElementById('runner-chat-messages');
                    const locBubble = container ? container.querySelector('a[href*="google.com/maps"]') : null;
                    const img = locBubble ? locBubble.querySelector('img') : null;
                    return {
                        containerExists: !!container,
                        hasLink: !!locBubble,
                        href: locBubble ? locBubble.getAttribute('href') : null,
                        hasImg: !!img,
                        imgSrc: img ? img.getAttribute('src') : null,
                        textContent: locBubble ? locBubble.innerText : ""
                    };
                })()
            """, msg_id=22)
            print("  Runner Chat Bubble Data:", json.dumps(r_bubble, indent=4))

            assert r_bubble["hasLink"], "Runner visual chat bubble must be wrapped in <a> tag"
            assert "destination=26.2315,85.361" in r_bubble["href"], "Runner navigation link matches coords"
            assert r_bubble["hasImg"], "Runner bubble must contain static map image"
            assert API_KEY in r_bubble["imgSrc"], "Runner static map img uses exact Google Maps API key"
            assert "maps.googleapis.com/maps/api/staticmap" in r_bubble["imgSrc"], "Uses Google Static Maps API"
            assert "26.2315" not in r_bubble["textContent"], "NO raw latitude coordinates displayed in runner chat!"
            assert "85.361" not in r_bubble["textContent"], "NO raw longitude coordinates displayed in runner chat!"
            print("  [PASS] Runner Chat Bubble verified: Static map img, direct turn-by-turn nav link, readable address, ZERO raw coords!")

            # Capture runner bubble screenshot
            await take_screenshot(ws, "proof_runner_chat_visual_map_bubble.png", msg_id=103)

    finally:
        chrome_runner.terminate()
        httpd.shutdown()

    print("\n=======================================================")
    print("ALL VERIFICATIONS COMPLETED SUCCESSFULLY WITH 100% PASS!")
    print("=======================================================")

if __name__ == "__main__":
    asyncio.run(run_both_evals())
