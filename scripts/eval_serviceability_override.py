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
PORT = 8099
CDP_PORT = 9228
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
TEMP_DIR = r"C:\Users\dhira\AppData\Local\Temp\chrome_serv_override_eval"

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

            await asyncio.sleep(2)

            # TEST 1: Config and Home Screen Cleanliness
            print("\n[TEST 1] Verifying APP_CONFIG and Clean Home Screen (Zero Red Distance Banners)...")
            res_home = await evaluate(ws, """
            (() => {
                const config = window.APP_CONFIG || {};
                const homeBanner = document.getElementById('service-unreachable-banner');
                const isHomeBannerInDom = !!homeBanner;
                const isHomeBannerVisible = homeBanner ? !homeBanner.classList.contains('hidden') : false;
                const homeTabText = document.getElementById('view-home') ? document.getElementById('view-home').innerText : '';
                const hasRawDistanceOnHome = homeTabText.includes('km away') || homeTabText.includes('~10.');

                return {
                    hasConfig: !!window.APP_CONFIG,
                    maxRadiusKm: config.MAX_DELIVERY_RADIUS_KM,
                    isHomeBannerInDom,
                    isHomeBannerVisible,
                    hasRawDistanceOnHome
                };
            })()
            """, msg_id=10)
            print("Home Screen Audit Result:", json.dumps(res_home, indent=2))

            assert res_home["hasConfig"] is True, "FAIL: window.APP_CONFIG not loaded from config.js"
            assert res_home["maxRadiusKm"] == 8.0, f"FAIL: Expected MAX_DELIVERY_RADIUS_KM = 8.0, got {res_home['maxRadiusKm']}"
            assert res_home["isHomeBannerInDom"] is False, "FAIL: service-unreachable-banner element should be completely removed from Home DOM"
            assert res_home["hasRawDistanceOnHome"] is False, "FAIL: Raw distance text found on Home screen"
            print("  ✓ Home Screen catalog is 100% clean with zero red distance banners.")

            await take_screenshot(ws, "proof_clean_home_no_distance_banner.png", msg_id=11)

            # TEST 2: Address Modal Manual Geocoding Override
            print("\n[TEST 2] Verifying Address Modal Manual Geocoding Override (Chaturshi over Musahri)...")
            await evaluate(ws, "openRuralAddressModal()", msg_id=20)
            await asyncio.sleep(1)

            res_input = await evaluate(ws, """
            (() => {
                const inp = document.getElementById('modal-village-input');
                if (!inp) return { exists: false };
                const isReadOnly = inp.readOnly || inp.hasAttribute('readonly');
                const isDisabled = inp.disabled || inp.hasAttribute('disabled');
                
                // Simulate geocoder auto-filling broad block name 'Musahri'
                inp.value = 'Musahri';
                inp.dispatchEvent(new Event('input', { bubbles: true }));
                const afterGeocodeVal = inp.value;

                // Simulate user tapping and manually typing exact village 'Chaturshi'
                inp.value = 'Chaturshi';
                inp.dispatchEvent(new Event('input', { bubbles: true }));
                if (typeof handleVillageInputChange === 'function') {
                    handleVillageInputChange('Chaturshi');
                }
                const finalVillageVal = inp.value;
                const activeVillage = window.activeCustomerAddress ? window.activeCustomerAddress.village : null;

                return {
                    exists: true,
                    isReadOnly,
                    isDisabled,
                    afterGeocodeVal,
                    finalVillageVal,
                    activeVillage
                };
            })()
            """, msg_id=21)
            print("Manual Override Audit Result:", json.dumps(res_input, indent=2))

            assert res_input["exists"] is True, "FAIL: modal-village-input does not exist"
            assert res_input["isReadOnly"] is False, "FAIL: modal-village-input is marked readOnly"
            assert res_input["isDisabled"] is False, "FAIL: modal-village-input is marked disabled"
            assert res_input["finalVillageVal"] == "Chaturshi", "FAIL: manual override value not accepted in input"
            assert res_input["activeVillage"] == "Chaturshi", "FAIL: activeCustomerAddress not updated with manual override"
            print("  ✓ User can manually override any geocoder block name with exact village.")

            await take_screenshot(ws, "proof_editable_village_override_modal.png", msg_id=22)
            await evaluate(ws, "closeModal('modal-rural-address')", msg_id=23)
            await asyncio.sleep(0.5)

            # TEST 3: Silent Checkout Serviceability Blocking (Zero Raw Distance)
            print("\n[TEST 3] Verifying Silent Checkout Serviceability Blocking...")
            # Add an item to cart first
            await evaluate(ws, """
            (() => {
                // Add sample item to cart
                if (window.catalogProducts && window.catalogProducts.length > 0) {
                    addToCart(window.catalogProducts[0].id);
                } else {
                    cartItems = [{ id: 'test_1', name: 'Aashirvaad Atta', price: 215, quantity: 1, unit: '5 kg' }];
                }
                // Switch to Cart tab
                switchTab('cart');
            })()
            """, msg_id=30)
            await asyncio.sleep(1)

            # Now test unserviceable coordinates (e.g. 15 km away)
            res_cart_unserv = await evaluate(ws, """
            (() => {
                // Check serviceability for coordinates 15km away
                checkServiceability(26.3500, 85.5000);

                const btnPlace = document.getElementById('btn-place-order');
                const isBtnDisabled = btnPlace ? btnPlace.disabled : false;
                const btnHasPointerEventsNone = btnPlace ? btnPlace.classList.contains('pointer-events-none') : false;
                const cartBanner = document.getElementById('cart-service-unreachable-banner');
                const isBannerVisible = cartBanner ? !cartBanner.classList.contains('hidden') : false;
                const bannerText = cartBanner ? cartBanner.innerText : '';
                const hasRawDistanceInCart = bannerText.includes('km away') || bannerText.includes('~15.') || bannerText.includes('15.0 km');

                return {
                    isBtnDisabled,
                    btnHasPointerEventsNone,
                    isBannerVisible,
                    bannerText,
                    hasRawDistanceInCart
                };
            })()
            """, msg_id=31)
            print("Cart Unserviceable Audit Result:", json.dumps(res_cart_unserv, indent=2))

            assert res_cart_unserv["isBtnDisabled"] is True, "FAIL: btn-place-order should be disabled when unserviceable"
            assert res_cart_unserv["btnHasPointerEventsNone"] is True, "FAIL: btn-place-order should have pointer-events-none"
            assert res_cart_unserv["isBannerVisible"] is True, "FAIL: cart-service-unreachable-banner should be visible"
            assert "Service is currently unavailable in this location." in res_cart_unserv["bannerText"], f"FAIL: Expected clean copy, got '{res_cart_unserv['bannerText']}'"
            assert res_cart_unserv["hasRawDistanceInCart"] is False, "FAIL: Raw distance displayed in checkout banner"
            print("  ✓ Checkout silently blocks unserviceable orders with clean copy and zero raw distances.")

            await take_screenshot(ws, "proof_clean_checkout_serviceability_disabled.png", msg_id=32)

            print("\nALL DIRECTIVE TESTS PASSED SUCCESSFULLY!")

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
