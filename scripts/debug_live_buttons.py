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
TEMP_DIR = r"C:\Users\dhira\AppData\Local\Temp\chrome_debug_dom_btn"

async def test_dom():
    http_proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", "8089", "--directory", "public_web"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    time.sleep(1)

    chrome_proc = subprocess.Popen([
        CHROME_PATH,
        "--headless=new",
        "--remote-debugging-port=8088",
        f"--user-data-dir={TEMP_DIR}",
        "http://127.0.0.1:8089/runner/index.html"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)

    try:
        targets_raw = urllib.request.urlopen("http://127.0.0.1:8088/json").read()
        targets = json.loads(targets_raw.decode('utf-8'))
        page_target = next(t for t in targets if t.get("type") == "page")
        ws_url = page_target["webSocketDebuggerUrl"]

        async with websockets.connect(ws_url) as ws:
            expr = """
                (() => {
                    const screen1 = document.getElementById('screen-onboarding-1');
                    // Find all buttons that are currently visible or inside screen1
                    const allButtons = Array.from(document.querySelectorAll('button')).filter(b => {
                        const rect = b.getBoundingClientRect();
                        return rect.width > 0 && rect.height > 0;
                    }).map(b => ({
                        outerHTML: b.outerHTML,
                        parent: b.parentElement ? b.parentElement.outerHTML.slice(0, 100) : null,
                        innerText: b.innerText,
                        onclick: b.getAttribute('onclick'),
                        id: b.id,
                        className: b.className
                    }));
                    return allButtons;
                })()
            """
            await ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate", "params": {"expression": expr, "returnByValue": True}}))
            resp = json.loads(await ws.recv())
            print("Visible buttons in runner:")
            for b in resp.get("result", {}).get("result", {}).get("value", []):
                print(b)
    finally:
        chrome_proc.terminate()
        http_proc.terminate()

asyncio.run(test_dom())
