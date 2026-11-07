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

ARTIFACT_DIR = r"C:\Users\dhira\.gemini\antigravity\brain\918c8085-b60b-40a9-a077-a3344458bcc5"
API_KEY = "AIzaSyBqHZrBX7WMEw2vt5COVwfK7a4lZpGapMc"
PORT = 8098
CDP_PORT = 9228

async def send_cdp(ws, method, params=None, msg_id=1):
    payload = {"id": msg_id, "method": method, "params": params or {}}
    await ws.send(json.dumps(payload))
    while True:
        resp = json.loads(await ws.recv())
        if resp.get("id") == msg_id:
            return resp

async def navigate_and_wait(ws, url, msg_id=10):
    await ws.send(json.dumps({"id": msg_id, "method": "Page.navigate", "params": {"url": url}}))
    while True:
        msg = json.loads(await ws.recv())
        if msg.get("method") == "Page.loadEventFired":
            break
        if msg.get("id") == msg_id and "error" in msg:
            raise Exception("Navigate failed: " + str(msg))

async def take_screenshot(ws, filename, msg_id=100):
    res = await send_cdp(ws, "Page.captureScreenshot", {"format": "png"}, msg_id=msg_id)
    b64 = res["result"]["data"]
    out_path = os.path.join(ARTIFACT_DIR, filename)
    with open(out_path, "wb") as f:
        f.write(base64.b64decode(b64))
    print(f"Screenshot saved: {out_path}")
    return out_path

async def evaluate(ws, expr, msg_id=200):
    res = await send_cdp(ws, "Runtime.evaluate", {"expression": expr, "returnByValue": True, "awaitPromise": True}, msg_id=msg_id)
    return res.get("result", {}).get("result", {}).get("value")

async def run_test():
    # 1. Start HTTP Server
    http_proc = None
    try:
        urllib.request.urlopen(f"http://127.0.0.1:{PORT}/customer/index.html", timeout=1)
    except Exception:
        http_proc = subprocess.Popen(
            [sys.executable, "-m", "http.server", str(PORT), "--directory", "public_web"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        time.sleep(1.2)

    # 2. Start Chrome
    chrome_cmd = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        "--headless=new",
        f"--remote-debugging-port={CDP_PORT}",
        f"--user-data-dir=C:\\Users\\dhira\\AppData\\Local\\Temp\\chrome_chat_eval_{CDP_PORT}",
        "--disable-gpu",
        "--no-sandbox",
        "--hide-scrollbars",
        "--window-size=430,932"
    ]
    chrome_proc = subprocess.Popen(chrome_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2.0)

    try:
        # A. TEST CUSTOMER APP
        print("--- TESTING CUSTOMER IN-APP CHAT LOCATION SHARING ---")
        req = urllib.request.Request(f"http://127.0.0.1:{CDP_PORT}/json/new", method="PUT")
        tab1 = json.loads(urllib.request.urlopen(req).read().decode())
        ws_url1 = tab1["webSocketDebuggerUrl"]

        async with websockets.connect(ws_url1) as ws:
            await send_cdp(ws, "Page.enable")
            await send_cdp(ws, "DOM.enable")
            await send_cdp(ws, "Runtime.enable")

            await navigate_and_wait(ws, f"http://127.0.0.1:{PORT}/customer/index.html")
            await asyncio.sleep(1.5)

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
            """, 201)

            # Open runner chat modal
            await evaluate(ws, "openRunnerChatModal();", 202)
            await asyncio.sleep(0.8)

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
            """, 203)
            await asyncio.sleep(0.3)

            has_spinner = await evaluate(ws, "!!document.getElementById('chat-gps-detecting-indicator')", 204)
            spinnerText = await evaluate(ws, "document.getElementById('chat-gps-detecting-indicator')?.innerText", 205)
            print(f"Detecting exact location spinner appeared: {has_spinner} (text: '{spinnerText}')")
            assert has_spinner, "FAIL: Spinner did not appear immediately upon location pin click!"
            assert "Detecting exact location" in (spinnerText or ""), "FAIL: Spinner text mismatch!"

            await take_screenshot(ws, "proof_chat_location_detecting_spinner.png", 101)

            # Wait for GPS resolving & static map bubble rendering
            await asyncio.sleep(1.8)

            bubble_data = await evaluate(ws, """
                (() => {
                    const container = document.getElementById('chat-messages-container');
                    const lastBubble = container.lastElementChild;
                    const link = lastBubble.querySelector('a');
                    const img = lastBubble.querySelector('img');
                    const text = lastBubble.innerText;
                    return {
                        hasLink: !!link,
                        href: link ? link.getAttribute('href') : null,
                        target: link ? link.getAttribute('target') : null,
                        hasImg: !!img,
                        imgSrc: img ? img.getAttribute('src') : null,
                        textContent: text
                    };
                })()
            """, 206)
            print("Customer Chat Bubble Data:", json.dumps(bubble_data, indent=2))

            assert bubble_data["hasLink"], "FAIL: Visual chat bubble must be wrapped in an <a> tag!"
            assert "https://www.google.com/maps/dir/?api=1&destination=26.2315,85.361" in bubble_data["href"], f"FAIL: Link destination incorrect: {bubble_data['href']}"
            assert bubble_data["hasImg"], "FAIL: Visual chat bubble must have static map img!"
            assert API_KEY in bubble_data["imgSrc"], "FAIL: Image src must use exact provided API key!"
            assert "maps.googleapis.com/maps/api/staticmap" in bubble_data["imgSrc"], "FAIL: Image must be Google Static Maps!"
            assert "26.2315" not in bubble_data["textContent"], "FAIL: Bubble text must NOT show raw latitude coordinates!"
            assert "85.361" not in bubble_data["textContent"], "FAIL: Bubble text must NOT show raw longitude coordinates!"

            await take_screenshot(ws, "proof_customer_chat_visual_map_bubble.png", 102)

        # B. TEST RUNNER APP IN FRESH TAB
        print("\n--- TESTING RUNNER IN-APP CHAT LOCATION PIN DISPLAY ---")
        req2 = urllib.request.Request(f"http://127.0.0.1:{CDP_PORT}/json/new", method="PUT")
        tab2 = json.loads(urllib.request.urlopen(req2).read().decode())
        ws_url2 = tab2["webSocketDebuggerUrl"]

        async with websockets.connect(ws_url2) as ws2:
            await send_cdp(ws2, "Page.enable")
            await send_cdp(ws2, "DOM.enable")
            await send_cdp(ws2, "Runtime.enable")

            await navigate_and_wait(ws2, f"http://127.0.0.1:{PORT}/runner/index.html")
            await asyncio.sleep(1.5)

            # Open Dashboard and Active Run
            await evaluate(ws2, """
                localStorage.setItem('gaonbazaar_runner_token', 'mock_runner_token_8899');
                openDashboard('activerun', false);
            """, 301)
            await asyncio.sleep(0.5)

            # Open Runner Order Chat
            await evaluate(ws2, """
                openRunnerOrderChat();
            """, 302)
            await asyncio.sleep(1.2)

            runner_bubble_data = await evaluate(ws2, """
                (() => {
                    const container = document.getElementById('runner-chat-messages');
                    const locBubble = container ? container.querySelector('a[href*="maps.google.com"]') : null;
                    const img = locBubble ? locBubble.querySelector('img') : null;
                    const text = locBubble ? locBubble.innerText : "";
                    return {
                        hasLink: !!locBubble,
                        href: locBubble ? locBubble.getAttribute('href') : null,
                        hasImg: !!img,
                        imgSrc: img ? img.getAttribute('src') : null,
                        textContent: text
                    };
                })()
            """, 303)
            print("Runner Chat Bubble Data:", json.dumps(runner_bubble_data, indent=2))

            assert runner_bubble_data["hasLink"], "FAIL: Runner visual chat bubble must be wrapped in an <a> tag!"
            assert "https://www.google.com/maps/dir/?api=1&destination=26.2315,85.361" in runner_bubble_data["href"], f"FAIL: Runner link destination incorrect: {runner_bubble_data['href']}"
            assert runner_bubble_data["hasImg"], "FAIL: Runner visual chat bubble must have static map img!"
            assert API_KEY in runner_bubble_data["imgSrc"], "FAIL: Runner image src must use exact provided API key!"
            assert "26.2315" not in runner_bubble_data["textContent"], "FAIL: Runner bubble text must NOT show raw latitude coordinates!"
            assert "85.361" not in runner_bubble_data["textContent"], "FAIL: Runner bubble text must NOT show raw longitude coordinates!"

            await take_screenshot(ws2, "proof_runner_chat_visual_map_bubble.png", 103)

            print("\nALL AUTOMATED TESTS PASSED WITH 100% SUCCESS!")

    finally:
        chrome_proc.terminate()
        if http_proc:
            http_proc.terminate()

if __name__ == "__main__":
    asyncio.run(run_test())
