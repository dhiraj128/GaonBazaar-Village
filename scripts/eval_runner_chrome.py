import asyncio
import subprocess
import os
import sys
import json
import time
import urllib.request
import websockets

sys.stdout.reconfigure(encoding='utf-8')

port = 8097
cdp_port = 9224
chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
temp_dir = r"C:\Users\dhira\AppData\Local\Temp\chrome_runner_eval"

async def eval_runner():
    # 1. Start HTTP Server if not already responding
    http_proc = None
    try:
        urllib.request.urlopen(f"http://127.0.0.1:{port}/runner/index.html", timeout=1)
        print("Using active HTTP server on port", port)
    except Exception:
        print("Starting HTTP server on port", port)
        http_proc = subprocess.Popen(
            [sys.executable, "-m", "http.server", str(port), "--directory", "public_web"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        time.sleep(1.5)

    # 2. Check Chrome CDP
    try:
        urllib.request.urlopen(f"http://127.0.0.1:{cdp_port}/json", timeout=1)
        print("Chrome CDP active on port", cdp_port)
    except Exception:
        print("Starting Chrome on port", cdp_port)
        os.makedirs(temp_dir, exist_ok=True)
        subprocess.Popen([
            chrome_path,
            f"--remote-debugging-port={cdp_port}",
            f"--user-data-dir={temp_dir}",
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            f"http://127.0.0.1:{port}/runner/index.html"
        ])
        time.sleep(2)

    # Connect to Runner page
    pages_json = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{cdp_port}/json").read())
    runner_page = next((p for p in pages_json if "runner" in p.get("url", "")), None)
    if not runner_page:
        ws_url = pages_json[0]["webSocketDebuggerUrl"]
        async with websockets.connect(ws_url, max_size=10_000_000) as ws:
            await ws.send(json.dumps({
                "id": 1,
                "method": "Page.navigate",
                "params": {"url": f"http://127.0.0.1:{port}/runner/index.html"}
            }))
            await asyncio.sleep(2)
        pages_json = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{cdp_port}/json").read())
        runner_page = pages_json[0]

    ws_url = runner_page["webSocketDebuggerUrl"]
    print("Connected to Runner page WebSocket:", ws_url)

    async with websockets.connect(ws_url, max_size=10_000_000) as ws:
        await ws.send(json.dumps({"id": 2, "method": "Page.enable"}))
        await ws.send(json.dumps({"id": 3, "method": "Runtime.enable"}))

        runner_test_expr = """
        (async () => {
          const res = [];
          const check = (pass, msg) => res.push({ pass: !!pass, msg });

          // 1. Enter Dashboard directly and navigate to Active Run
          localStorage.setItem('gaonbazaar_runner_token', 'mock_runner_token_8899');
          openDashboard('activerun', false);

          const activeTab = document.getElementById('tab-activerun');
          check(!activeTab.classList.contains('hidden'), 'Active Run tab is visible');

          // 2. PHASE 1: VENDOR PICKUP FLOW
          const step1 = document.getElementById('run-step-1');
          check(step1 !== null, 'Phase 1 container exists');
          check(step1.textContent.includes('Phase 1: Proceed to Shop for Pickup'), 'Phase 1 title rendered: Proceed to Shop for Pickup');

          // Verify static Google map showing Vendor coordinates
          const vendorMap = document.getElementById('vendor-static-map-img');
          check(vendorMap !== null, 'Vendor static map img element exists');
          check(vendorMap.src.includes('maps.googleapis.com/maps/api/staticmap'), 'Vendor map src uses Google Static Maps API');
          check(vendorMap.src.includes('AIzaSyBqHZrBX7WMEw2vt5COVwfK7a4lZpGapMc'), 'Vendor map src uses provided Google Maps API key');
          check(vendorMap.src.includes('26.2230,85.3520'), 'Vendor map centers on exact vendor coordinates');

          // Verify Navigate to Shop direct intent link
          const navShopBtn = document.getElementById('btn-navigate-shop');
          check(navShopBtn !== null, 'Navigate to Shop button exists');
          const expectedShopIntent = 'https://www.google.com/maps/dir/?api=1&destination=26.2230,85.3520&travelmode=driving&dir_action=navigate';
          check(navShopBtn.href === expectedShopIntent, 'Navigate to Shop href uses direct intent scheme');

          // Verify Vendor Details
          const storeName = document.getElementById('order-store-name');
          const storeAddr = document.getElementById('order-store-address');
          const pickupOtp = document.getElementById('order-pickup-otp');
          check(storeName && storeName.textContent.includes('Sharma Kirana'), 'Store name displayed');
          check(storeAddr && storeAddr.textContent.includes('Shop #4'), 'Store address displayed');
          check(pickupOtp && pickupOtp.textContent.length === 4, '4-digit pickup OTP displayed: ' + pickupOtp.textContent);

          // Verify Confirm Pickup Button
          const confirmBtn = document.getElementById('btn-confirm-pickup');
          check(confirmBtn !== null, 'Confirm Pickup button exists');

          // 3. PHASE 1 -> PHASE 2 TRANSITION: CONFIRM PICKUP
          await confirmVendorPickup();

          const badge1 = document.getElementById('step-1-status-badge');
          check(badge1 && badge1.textContent.includes('PICKUP COMPLETED'), 'Phase 1 status badge updated to PICKUP COMPLETED');

          const step2 = document.getElementById('run-step-2');
          check(step2 !== null, 'Phase 2 container exists');
          check(!step2.classList.contains('pointer-events-none'), 'Phase 2 activated (pointer-events-none removed)');
          check(!step2.classList.contains('opacity-60'), 'Phase 2 opacity restored to active');

          const badge2 = document.getElementById('step-2-status-badge');
          check(badge2 && badge2.textContent.includes('DELIVERING'), 'Phase 2 status badge is IN PROGRESS (DELIVERING)');

          // Verify Customer Static Google Map
          const custMap = document.getElementById('customer-static-map-img');
          check(custMap !== null, 'Customer static map img element exists');
          check(custMap.src.includes('maps.googleapis.com/maps/api/staticmap'), 'Customer map src uses Google Static Maps API');
          check(custMap.src.includes('AIzaSyBqHZrBX7WMEw2vt5COVwfK7a4lZpGapMc'), 'Customer map src uses provided Google Maps API key');
          const navCustBtn = document.getElementById('btn-navigate-customer');
          check(navCustBtn !== null, 'Navigate to Customer button exists');
          const expectedCustIntent = 'https://www.google.com/maps/dir/?api=1&destination=26.2315,85.3610&travelmode=driving&dir_action=navigate';
          const custCoordsOk = custMap.src.includes('26.2315') && custMap.src.includes('85.3610');
          check(custCoordsOk, 'Customer map centers on exact customer coordinates: ' + custMap.src);
          const navIntentOk = (navCustBtn.href === expectedCustIntent) || navCustBtn.href.includes('destination=26.2315,85.3610');
          check(navIntentOk, 'Navigate to Customer href uses direct intent scheme: ' + navCustBtn.href);

          // Verify Customer Details, Readable Landmark & OTP Input
          const custName = document.getElementById('order-customer-name');
          const custAddr = document.getElementById('order-customer-address');
          const custLandmark = document.getElementById('order-customer-landmark');
          check(custName && custName.textContent.includes('Sunita Devi'), 'Customer name displayed');
          check(custAddr && custAddr.textContent.includes('Minapur Village'), 'Customer address displayed');
          check(custLandmark && custLandmark.textContent.includes('Landmark:'), 'Customer rural landmark displayed');

          const custOtpInput = document.getElementById('cust-delivery-otp');
          check(custOtpInput !== null && custOtpInput.maxLength === 4, '4-digit delivery OTP input field exists');

          // Verify Complete Delivery Button
          const completeBtn = document.getElementById('btn-complete-delivery');
          check(completeBtn !== null, 'Complete Delivery button exists');

          // Verify WebSocket event emission on pickup
          const lastEvent = JSON.parse(localStorage.getItem('gb_last_runner_event') || '{}');
          check(lastEvent.status === 'OUT_FOR_DELIVERY', 'WebSocket event emitted for OUT_FOR_DELIVERY: ' + lastEvent.status);

          // 4. PHASE 2 COMPLETION: VERIFY OTP AND COMPLETE DELIVERY
          custOtpInput.value = '7842';
          await verifyCustomerDeliveryAndFinish('GB-8921');

          check(step2.textContent.includes('Delivery Completed Successfully'), 'Delivery marked completed upon OTP verification');
          const finalEvent = JSON.parse(localStorage.getItem('gb_last_runner_event') || '{}');
          check(finalEvent.status === 'DELIVERED', 'WebSocket event emitted for DELIVERED: ' + finalEvent.status);

          return res;
        })()
        """

        await ws.send(json.dumps({
            "id": 100,
            "method": "Runtime.evaluate",
            "params": {
                "expression": runner_test_expr,
                "returnByValue": True,
                "awaitPromise": True
            }
        }))

        while True:
            msg = await ws.recv()
            data = json.loads(msg)
            if data.get("id") == 100:
                if "exceptionDetails" in data["result"]:
                    print("JS Exception in Runner test:", data["result"]["exceptionDetails"])
                    return False
                items = data["result"]["result"]["value"]
                all_passed = True
                print("\n--- Runner Two-Phase Navigation Workflow Test Results ---")
                for it in items:
                    st = "PASS" if it["pass"] else "FAIL"
                    if not it["pass"]: all_passed = False
                    print(f"  [{st}] {it['msg']}")
                return all_passed

if __name__ == "__main__":
    success = asyncio.run(eval_runner())
    sys.exit(0 if success else 1)
