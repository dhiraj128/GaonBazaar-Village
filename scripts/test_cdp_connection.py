import subprocess
import os
import sys
import json
import time
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')

port = 8096
cdp_port = 9223
chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
temp_dir = r"C:\Users\dhira\AppData\Local\Temp\chrome_cdp_test"

# Serve public_web
server_proc = subprocess.Popen(
    [sys.executable, "-m", "http.server", str(port), "--directory", "public_web"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)
time.sleep(1.5)

# Launch Chrome with remote debugging
chrome_proc = subprocess.Popen([
    chrome_path,
    "--headless=new",
    "--disable-gpu",
    f"--remote-debugging-port={cdp_port}",
    f"--user-data-dir={temp_dir}",
    f"http://127.0.0.1:{port}/customer/index.html"
], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

time.sleep(2.5)

try:
    # Get WebSocket debugger URL
    resp = urllib.request.urlopen(f"http://127.0.0.1:{cdp_port}/json")
    tabs = json.loads(resp.read().decode())
    target_tab = None
    for tab in tabs:
        if "customer/index.html" in tab.get("url", ""):
            target_tab = tab
            break
    if not target_tab and tabs:
        target_tab = tabs[0]

    ws_url = target_tab["webSocketDebuggerUrl"]
    print(f"Connected to Chrome Tab: {target_tab.get('title')} | {ws_url}")

    # Use a basic WebSocket connection using standard socket or simple python script
    # We can use backend .venv which might have websockets, or write a tiny raw websocket frame
except Exception as e:
    print(f"CDP connection error: {e}")
finally:
    chrome_proc.terminate()
    server_proc.terminate()
