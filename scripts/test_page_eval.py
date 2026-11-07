import asyncio
import json
import time
import subprocess
import urllib.request
import websockets

async def test():
    p = subprocess.Popen([
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        "--remote-debugging-port=9239",
        r"--user-data-dir=C:\Users\dhira\AppData\Local\Temp\test_prof_9239",
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "http://127.0.0.1:8097/customer/index.html"
    ])
    time.sleep(2.0)
    try:
        pages = json.loads(urllib.request.urlopen("http://127.0.0.1:9239/json").read())
        page = next(p for p in pages if p.get("type") == "page")
        print("Page URL:", page["url"])
        async with websockets.connect(page["webSocketDebuggerUrl"]) as ws:
            await ws.send(json.dumps({
                "id": 1,
                "method": "Runtime.evaluate",
                "params": {
                    "expression": "(() => { localStorage.setItem('k', 'hello'); return localStorage.getItem('k'); })()",
                    "returnByValue": True
                }
            }))
            while True:
                res = json.loads(await ws.recv())
                if res.get("id") == 1:
                    print("FULL RES:", json.dumps(res, indent=2))
                    break
    finally:
        p.terminate()

if __name__ == "__main__":
    asyncio.run(test())
