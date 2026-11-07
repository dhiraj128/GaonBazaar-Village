import asyncio
import os
import sys
import json
import time
import subprocess
import urllib.request
import websockets

CDP_PORT = 9226
PORT = 8098

async def debug_runner():
    chrome_cmd = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        "--headless=new",
        f"--remote-debugging-port={CDP_PORT}",
        f"--user-data-dir=C:\\Users\\dhira\\AppData\\Local\\Temp\\chrome_debug_{CDP_PORT}",
        "--disable-gpu",
        "--no-sandbox",
        "--window-size=430,932"
    ]
    chrome_proc = subprocess.Popen(chrome_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.5)

    try:
        req = urllib.request.Request(f"http://127.0.0.1:{CDP_PORT}/json/new", method="PUT")
        res = urllib.request.urlopen(req)
        tab_info = json.loads(res.read().decode())
        ws_url = tab_info["webSocketDebuggerUrl"]

        async with websockets.connect(ws_url) as ws:
            await ws.send(json.dumps({"id": 1, "method": "Page.enable"}))
            await ws.send(json.dumps({"id": 2, "method": "Runtime.enable"}))
            await ws.send(json.dumps({"id": 3, "method": "Page.navigate", "params": {"url": f"http://127.0.0.1:{PORT}/runner/index.html"}}))

            await asyncio.sleep(2.0)

            # Evaluate openDashboard and openRunnerOrderChat with full try/catch
            eval_res = await ws.send(json.dumps({
                "id": 4,
                "method": "Runtime.evaluate",
                "params": {
                    "expression": """
                        (async () => {
                            try {
                                localStorage.setItem('gaonbazaar_runner_token', 'mock_runner_token_8899');
                                openDashboard('activerun', false);
                                openRunnerOrderChat();
                                await new Promise(r => setTimeout(r, 1000));
                                const container = document.getElementById('runner-chat-messages');
                                return {
                                    containerHTML: container ? container.innerHTML : 'CONTAINER_NOT_FOUND',
                                    messagesCount: state.orderMessages ? state.orderMessages.length : 0
                                };
                            } catch(err) {
                                return { error: err.message, stack: err.stack };
                            }
                        })()
                    """,
                    "returnByValue": True,
                    "awaitPromise": True
                }
            }))

            while True:
                msg = json.loads(await ws.recv())
                if msg.get("id") == 4:
                    print("EVAL RESULT:\n", json.dumps(msg.get("result", {}).get("result", {}).get("value"), indent=2))
                    break
                elif msg.get("method") == "Runtime.exceptionThrown":
                    print("EXCEPTION:\n", json.dumps(msg, indent=2))
                elif msg.get("method") == "Runtime.consoleAPICalled":
                    print("CONSOLE:", msg.get("params", {}).get("type"), [a.get("value") for a in msg.get("params", {}).get("args", [])])

    finally:
        chrome_proc.terminate()

if __name__ == "__main__":
    asyncio.run(debug_runner())
