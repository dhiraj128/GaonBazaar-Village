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
TEMP_DIR = r"C:\Users\dhira\AppData\Local\Temp\chrome_step1_check"
ARTIFACT_DIR = r"C:\Users\dhira\OneDrive\Desktop\GaoBazar-Village"
BRAIN_DIR = r"C:\Users\dhira\.gemini\antigravity\brain\918c8085-b60b-40a9-a077-a3344458bcc5"

async def capture_step1():
    http_proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", "8091", "--directory", "public_web"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    time.sleep(1)

    chrome_proc = subprocess.Popen([
        CHROME_PATH,
        "--headless=new",
        "--remote-debugging-port=8090",
        f"--user-data-dir={TEMP_DIR}",
        "--window-size=412,915",
        "http://127.0.0.1:8091/customer/index.html"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)

    try:
        targets_raw = urllib.request.urlopen("http://127.0.0.1:8090/json").read()
        targets = json.loads(targets_raw.decode('utf-8'))
        page_target = next(t for t in targets if t.get("type") == "page")
        ws_url = page_target["webSocketDebuggerUrl"]

        async with websockets.connect(ws_url) as ws:
            # Customer Step 1
            await ws.send(json.dumps({"id": 1, "method": "Page.enable"}))
            await ws.send(json.dumps({"id": 2, "method": "Runtime.evaluate", "params": {
                "expression": "localStorage.clear(); sessionStorage.clear(); location.reload();",
                "awaitPromise": True
            }}))
            await asyncio.sleep(2)
            
            res = await ws.send(json.dumps({"id": 3, "method": "Page.captureScreenshot", "params": {"format": "png"}}))
            resp = json.loads(await ws.recv())
            while resp.get("id") != 3:
                resp = json.loads(await ws.recv())
            b64 = resp["result"]["data"]
            for d in [ARTIFACT_DIR, BRAIN_DIR]:
                with open(os.path.join(d, "step1_customer_current.png"), "wb") as f:
                    f.write(base64.b64decode(b64))
            print("Captured step1_customer_current.png")

            # Runner Step 1
            await ws.send(json.dumps({"id": 4, "method": "Page.navigate", "params": {"url": "http://127.0.0.1:8091/runner/index.html"}}))
            await asyncio.sleep(2)
            await ws.send(json.dumps({"id": 5, "method": "Runtime.evaluate", "params": {
                "expression": "localStorage.clear(); sessionStorage.clear(); location.reload();",
                "awaitPromise": True
            }}))
            await asyncio.sleep(2)
            
            res = await ws.send(json.dumps({"id": 6, "method": "Page.captureScreenshot", "params": {"format": "png"}}))
            resp = json.loads(await ws.recv())
            while resp.get("id") != 6:
                resp = json.loads(await ws.recv())
            b64 = resp["result"]["data"]
            for d in [ARTIFACT_DIR, BRAIN_DIR]:
                with open(os.path.join(d, "step1_runner_current.png"), "wb") as f:
                    f.write(base64.b64decode(b64))
            print("Captured step1_runner_current.png")

            # Vendor Step 1
            await ws.send(json.dumps({"id": 7, "method": "Page.navigate", "params": {"url": "http://127.0.0.1:8091/vendor/index.html"}}))
            await asyncio.sleep(2)
            await ws.send(json.dumps({"id": 8, "method": "Runtime.evaluate", "params": {
                "expression": "localStorage.clear(); sessionStorage.clear(); location.reload();",
                "awaitPromise": True
            }}))
            await asyncio.sleep(2)
            
            res = await ws.send(json.dumps({"id": 9, "method": "Page.captureScreenshot", "params": {"format": "png"}}))
            resp = json.loads(await ws.recv())
            while resp.get("id") != 9:
                resp = json.loads(await ws.recv())
            b64 = resp["result"]["data"]
            for d in [ARTIFACT_DIR, BRAIN_DIR]:
                with open(os.path.join(d, "step1_vendor_current.png"), "wb") as f:
                    f.write(base64.b64decode(b64))
            print("Captured step1_vendor_current.png")

    finally:
        chrome_proc.terminate()
        http_proc.terminate()

asyncio.run(capture_step1())
