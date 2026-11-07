import asyncio
import json
import time
import subprocess
import urllib.request
import websockets

async def test():
    temp_dir = r"C:\Users\dhira\AppData\Local\Temp\chrome_temp_test_9232"
    chrome_cmd = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        "--remote-debugging-port=9232",
        f"--user-data-dir={temp_dir}",
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "http://127.0.0.1:8098/runner/index.html"
    ]
    p = subprocess.Popen(chrome_cmd)
    time.sleep(2.0)
    try:
        pages = json.loads(urllib.request.urlopen("http://127.0.0.1:9232/json").read())
        runner_page = next((p for p in pages if "runner" in p.get("url", "")), pages[0])
        ws_url = runner_page["webSocketDebuggerUrl"]
        async with websockets.connect(ws_url) as ws:
            await ws.send(json.dumps({"id": 1, "method": "Page.enable"}))
            await ws.send(json.dumps({"id": 2, "method": "Runtime.enable"}))

            expr = """
                new Promise((resolve) => {
                    try {
                        localStorage.setItem('gaonbazaar_runner_token', 'mock_runner_token_8899');
                        openDashboard('activerun', false);
                        openRunnerOrderChat();
                        setTimeout(() => {
                            const container = document.getElementById('runner-chat-messages');
                            const locLink = container ? container.querySelector('a[href*="maps.google.com"]') : null;
                            const img = locLink ? locLink.querySelector('img') : null;
                            resolve({
                                containerExists: !!container,
                                hasLocLink: !!locLink,
                                locLinkHref: locLink ? locLink.href : null,
                                locLinkText: locLink ? locLink.innerText : null,
                                hasImg: !!img,
                                imgSrc: img ? img.src : null
                            });
                        }, 2500);
                    } catch(e) {
                        resolve({ error: e.toString() });
                    }
                })
            """
            await ws.send(json.dumps({
                "id": 4,
                "method": "Runtime.evaluate",
                "params": {
                    "expression": expr,
                    "returnByValue": True,
                    "awaitPromise": True
                }
            }))
            while True:
                msg = json.loads(await ws.recv())
                if msg.get("id") == 4:
                    print("RUNNER EVAL OUTPUT:\n", json.dumps(msg.get("result", {}).get("result", {}).get("value"), indent=2))
                    break
    finally:
        p.terminate()

if __name__ == "__main__":
    asyncio.run(test())
