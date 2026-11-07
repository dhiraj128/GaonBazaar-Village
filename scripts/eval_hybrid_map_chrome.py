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
CDP_PORT = 9226
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
TEMP_DIR = r"C:\Users\dhira\AppData\Local\Temp\chrome_map_eval"

async def send_cdp(ws, method, params=None, msg_id=1):
    payload = {"id": msg_id, "method": method, "params": params or {}}
    await ws.send(json.dumps(payload))
    while True:
        resp = json.loads(await ws.recv())
        if resp.get("id") == msg_id:
            return resp

async def evaluate(ws, expr, msg_id=200):
    res = await send_cdp(ws, "Runtime.evaluate", {"expression": expr, "returnByValue": True, "awaitPromise": True}, msg_id=msg_id)
    return res.get("result", {}).get("result", {}).get("value")

async def take_screenshot(ws, filename, msg_id=100):
    res = await send_cdp(ws, "Page.captureScreenshot", {"format": "png"}, msg_id=msg_id)
    b64 = res["result"]["data"]
    out_path = os.path.join(ARTIFACT_DIR, filename)
    with open(out_path, "wb") as f:
        f.write(base64.b64decode(b64))
    print(f"  [SCREENSHOT] Saved: {out_path}")
    return out_path

async def run_eval():
    http_proc = None
    chrome_proc = None
    try:
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{PORT}/customer/index.html", timeout=1)
            print("Using existing HTTP server on port", PORT)
        except Exception:
            print("Starting HTTP server on port", PORT)
            http_proc = subprocess.Popen(
                [sys.executable, "-m", "http.server", str(PORT), "--directory", "public_web"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            time.sleep(1)

        os.makedirs(TEMP_DIR, exist_ok=True)
        chrome_cmd = [
            CHROME_PATH,
            f"--remote-debugging-port={CDP_PORT}",
            f"--user-data-dir={TEMP_DIR}",
            "--headless=new",
            "--disable-gpu",
            "--no-first-run",
            "--no-default-browser-check",
            "--window-size=430,932",
            f"http://127.0.0.1:{PORT}/customer/index.html"
        ]
        chrome_proc = subprocess.Popen(chrome_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(2)

        # Get WebSocket URL
        req = urllib.request.urlopen(f"http://127.0.0.1:{CDP_PORT}/json", timeout=5)
        pages = json.loads(req.read().decode())
        ws_url = None
        for p in pages:
            if p.get("type") == "page":
                ws_url = p.get("webSocketDebuggerUrl")
                break
        if not ws_url:
            ws_url = pages[0].get("webSocketDebuggerUrl")

        print("Connecting to Chrome CDP at:", ws_url)
        async with websockets.connect(ws_url, max_size=20*1024*1024) as ws:
            await send_cdp(ws, "Page.enable", msg_id=1)
            await send_cdp(ws, "DOM.enable", msg_id=2)
            await send_cdp(ws, "Runtime.enable", msg_id=3)

            # Wait for app to initialize
            await asyncio.sleep(2)

            # Open location map picker modal
            print("\n[ACTION] Triggering openLocationMapPickerModal()...")
            await evaluate(ws, "openLocationMapPickerModal()", msg_id=10)

            # Wait for Google Maps SDK to load, tiles to render, and resize triggers to settle
            print("[INFO] Waiting for Google Maps Hybrid Satellite tiles to paint...")
            await asyncio.sleep(3)

            # Audit map parameters
            eval_script = """
            (() => {
                const hasGmaps = typeof google !== 'undefined' && !!google.maps;
                const hasMap = !!window.locationPickerMap;
                let mapTypeId = null;
                let zoom = null;
                let center = null;
                if (hasMap) {
                    mapTypeId = window.locationPickerMap.getMapTypeId();
                    zoom = window.locationPickerMap.getZoom();
                    const c = window.locationPickerMap.getCenter();
                    center = c ? { lat: c.lat(), lng: c.lng() } : null;
                }
                const modal = document.getElementById('modal-location-map-picker');
                const isModalVisible = modal && !modal.classList.contains('hidden');
                const canvas = document.getElementById('location-picker-canvas');
                // Check if google maps injected container and canvas/tile elements
                const canvasChildCount = canvas ? canvas.childElementCount : 0;
                const canvasText = canvas ? canvas.innerHTML : '';
                const hasGmStyle = canvasText.includes('gm-style');
                const badge = document.getElementById('picker-service-badge') ? document.getElementById('picker-service-badge').innerText : '';
                const distance = document.getElementById('picker-distance-text') ? document.getElementById('picker-distance-text').innerText : '';

                return {
                    hasGmaps,
                    hasMap,
                    mapTypeId,
                    zoom,
                    center,
                    isModalVisible,
                    canvasChildCount,
                    hasGmStyle,
                    badge,
                    distance
                };
            })()
            """
            result = await evaluate(ws, eval_script, msg_id=11)
            print("\n=== GOOGLE MAPS AUDIT RESULTS ===")
            print(json.dumps(result, indent=2))

            assert result["hasGmaps"] is True, "FAIL: Google Maps JS SDK not loaded"
            assert result["hasMap"] is True, "FAIL: locationPickerMap instance not initialized"
            assert result["mapTypeId"] == "hybrid", f"FAIL: Expected mapTypeId 'hybrid', got {result['mapTypeId']}"
            assert result["zoom"] == 18, f"FAIL: Expected zoom 18, got {result['zoom']}"
            assert result["isModalVisible"] is True, "FAIL: modal-location-map-picker is hidden"
            assert result["canvasChildCount"] > 0, "FAIL: location-picker-canvas has no children"
            assert result["hasGmStyle"] is True, "FAIL: Google Maps style container gm-style not rendered"

            print("\n[PASS] All Directives Verified:")
            print("  1. Map initialization & tile rendering: SUCCESS (gm-style injected, non-blank container)")
            print("  2. Map visual layer: HYBRID (Satellite + Village Labels)")
            print("  3. Zoom level: 18 (Actionable doorstep resolution)")
            print(f"  4. Geofence & Serviceability: {result.get('badge')} ({result.get('distance')})")

            # Capture visual screenshot proof
            await asyncio.sleep(1)
            screenshot_path = await take_screenshot(ws, "proof_hybrid_satellite_location_picker.png", msg_id=12)
            print("  Artifact created:", screenshot_path)

    finally:
        if chrome_proc:
            chrome_proc.terminate()
            try:
                chrome_proc.wait(timeout=3)
            except Exception:
                chrome_proc.kill()
        if http_proc:
            http_proc.terminate()
            try:
                http_proc.wait(timeout=3)
            except Exception:
                http_proc.kill()

if __name__ == "__main__":
    asyncio.run(run_eval())
