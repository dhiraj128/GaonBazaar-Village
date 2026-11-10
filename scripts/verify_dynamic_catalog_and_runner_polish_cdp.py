# scripts/verify_dynamic_catalog_and_runner_polish_cdp.py
import asyncio
import json
import subprocess
import time
import urllib.request
import websockets
import os
import sys
import shutil

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PUB_DIR = os.path.abspath("public_web")
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
TEMP_DIR = os.path.abspath(".tmp_chrome_dynamic_catalog_runner")
ARTIFACT_DIR = r"C:\Users\dhira\.gemini\antigravity\brain\918c8085-b60b-40a9-a077-a3344458bcc5"

async def eval_js(ws, expr, msg_id):
    await ws.send(json.dumps({
        "id": msg_id,
        "method": "Runtime.evaluate",
        "params": {
            "expression": expr,
            "returnByValue": True,
            "awaitPromise": True
        }
    }))
    while True:
        raw = await ws.recv()
        resp = json.loads(raw)
        if resp.get("id") == msg_id:
            if "exceptionDetails" in resp.get("result", {}):
                print("JS EXCEPTION:", json.dumps(resp["result"]["exceptionDetails"], indent=2))
            res_val = resp.get("result", {}).get("result", {})
            if "value" in res_val:
                return res_val["value"]
            if "description" in res_val:
                return res_val["description"]
            return res_val

async def take_screenshot(ws, filename, msg_id):
    await ws.send(json.dumps({"id": msg_id, "method": "Page.captureScreenshot", "params": {"format": "png"}}))
    while True:
        raw = await ws.recv()
        resp = json.loads(raw)
        if resp.get("id") == msg_id:
            data = resp.get("result", {}).get("data", "")
            import base64
            with open(filename, "wb") as f:
                f.write(base64.b64decode(data))
            print(f"Captured screenshot: {filename}")
            if os.path.exists(ARTIFACT_DIR):
                shutil.copy(filename, os.path.join(ARTIFACT_DIR, os.path.basename(filename)))
                print(f"Copied to artifact directory: {os.path.join(ARTIFACT_DIR, os.path.basename(filename))}")
            break

async def main():
    print("=== STARTING DYNAMIC CATALOG & RUNNER UI POLISH CDP VERIFICATION ===")
    http_proc = subprocess.Popen(
        ["backend\\.venv\\Scripts\\python.exe", "-m", "http.server", "8196", "--directory", PUB_DIR],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    time.sleep(1.5)

    chrome_proc = subprocess.Popen([
        CHROME_PATH,
        "--headless=new",
        "--remote-debugging-port=8197",
        f"--user-data-dir={TEMP_DIR}",
        "--window-size=412,915",
        "http://127.0.0.1:8196/vendor/index.html"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)

    try:
        targets_raw = urllib.request.urlopen("http://127.0.0.1:8197/json").read()
        targets = json.loads(targets_raw.decode('utf-8'))
        page_target = next(t for t in targets if t.get("type") == "page")
        ws_url = page_target["webSocketDebuggerUrl"]

        async with websockets.connect(ws_url) as ws:
            mid = 1
            await ws.send(json.dumps({"id": mid, "method": "Page.enable"})); mid += 1
            while True:
                raw = await ws.recv()
                if json.loads(raw).get("id") == 1:
                    break

            # -----------------------------------------------------------------
            # TEST 1: DYNAMIC MASTER CATALOG & SEARCH RESOLUTION (NO 50 LIMIT)
            # -----------------------------------------------------------------
            print("\n--- TEST 1: Dynamic Master Catalog & Search Resolution ---")
            catalog_check = await eval_js(ws, """
                (async () => {
                    openMasterCatalogModal();
                    const modal = document.getElementById('modal-master-catalog');
                    const modalVisible = !modal.classList.contains('hidden');
                    const headerText = modal.querySelector('h3')?.innerText || '';
                    const has50StaplesInHeader = headerText.includes('50');

                    // Search for Atta
                    const searchInput = document.getElementById('master-catalog-search');
                    searchInput.value = 'Atta';
                    await renderMasterCatalogToggleList('Atta');
                    const itemsContainer = document.getElementById('master-catalog-items-list');
                    const attaCards = itemsContainer.querySelectorAll('.flex.items-center.justify-between');
                    const firstAttaTitle = attaCards[0]?.querySelector('h4')?.innerText || '';
                    const firstAttaImg = attaCards[0]?.querySelector('img')?.src || '';

                    // Search for Soap
                    searchInput.value = 'Soap';
                    await renderMasterCatalogToggleList('Soap');
                    const soapCards = itemsContainer.querySelectorAll('.flex.items-center.justify-between');
                    const firstSoapTitle = soapCards[0]?.querySelector('h4')?.innerText || '';
                    const firstSoapImg = soapCards[0]?.querySelector('img')?.src || '';

                    // Search for Dal
                    searchInput.value = 'Dal';
                    await renderMasterCatalogToggleList('Dal');
                    const dalCards = itemsContainer.querySelectorAll('.flex.items-center.justify-between');
                    const firstDalTitle = dalCards[0]?.querySelector('h4')?.innerText || '';
                    const firstDalImg = dalCards[0]?.querySelector('img')?.src || '';

                    // Check active count badge
                    const counterText = document.getElementById('master-catalog-enabled-count')?.innerText || '';
                    const has50InCounter = counterText.includes('50 Staples');

                    return {
                        modalVisible,
                        headerText,
                        has50StaplesInHeader,
                        attaCount: attaCards.length,
                        firstAttaTitle,
                        firstAttaImg,
                        soapCount: soapCards.length,
                        firstSoapTitle,
                        firstSoapImg,
                        dalCount: dalCards.length,
                        firstDalTitle,
                        firstDalImg,
                        counterText,
                        has50InCounter
                    };
                })()
            """, mid); mid += 1
            print("Dynamic Catalog Check:", json.dumps(catalog_check, indent=2))
            assert catalog_check['modalVisible'], "Master catalog modal must be visible"
            assert not catalog_check['has50StaplesInHeader'], "Header must not reference 50 staples"
            assert not catalog_check['has50InCounter'], "Counter must not reference 50 staples"
            assert catalog_check['attaCount'] > 0, "Atta search must return products"
            assert 'atta' in catalog_check['firstAttaTitle'].lower() or 'aashirvaad' in catalog_check['firstAttaTitle'].lower(), f"Unexpected title: {catalog_check['firstAttaTitle']}"
            assert catalog_check['firstAttaImg'].startswith('http'), f"Invalid image: {catalog_check['firstAttaImg']}"
            assert catalog_check['soapCount'] > 0, "Soap search must return products"
            assert 'soap' in catalog_check['firstSoapTitle'].lower() or 'lifebuoy' in catalog_check['firstSoapTitle'].lower() or 'dettol' in catalog_check['firstSoapTitle'].lower(), f"Unexpected title: {catalog_check['firstSoapTitle']}"
            assert catalog_check['dalCount'] > 0, "Dal search must return products"

            await take_screenshot(ws, "proof_vendor_dynamic_catalog_search.png", mid); mid += 1

            # -----------------------------------------------------------------
            # TEST 2: RUNNER COORDINATE ERADICATION & READABLE LANDMARKS
            # -----------------------------------------------------------------
            print("\n--- TEST 2: Runner Coordinate Eradication & Readable Landmarks ---")
            await ws.send(json.dumps({
                "id": mid,
                "method": "Page.navigate",
                "params": {"url": "http://127.0.0.1:8196/runner/index.html"}
            })); mid += 1
            time.sleep(2)

            runner_coords_check = await eval_js(ws, """
                (() => {
                    // Open Runner Hub & Active Run Tab
                    if (typeof simulateAdminApprovalAndOpenDashboard === 'function') {
                        simulateAdminApprovalAndOpenDashboard();
                    }
                    if (typeof switchDashboardTab === 'function') {
                        switchDashboardTab('activerun');
                    }

                    const phase1Badge = document.getElementById('vendor-shop-location-badge')?.innerText || '';
                    const phase2Badge = document.getElementById('customer-coords-display')?.innerText || '';
                    const customerLandmark = document.getElementById('order-customer-landmark')?.innerText || '';

                    const rawLatLongRegex = /\\d{1,3}\\.\\d{4}/;
                    const phase1HasRawGPS = rawLatLongRegex.test(phase1Badge);
                    const phase2HasRawGPS = rawLatLongRegex.test(phase2Badge);

                    // Test updatePhase1VendorMap function updates name correctly
                    updatePhase1VendorMap(26.2230, 85.3520, "Gupta General Store");
                    const updatedPhase1Badge = document.getElementById('vendor-shop-location-badge')?.innerText || '';

                    return {
                        phase1Badge,
                        phase2Badge,
                        customerLandmark,
                        phase1HasRawGPS,
                        phase2HasRawGPS,
                        updatedPhase1Badge
                    };
                })()
            """, mid); mid += 1
            print("Runner Landmark & GPS Check:", json.dumps(runner_coords_check, indent=2))
            assert not runner_coords_check['phase1HasRawGPS'], f"Phase 1 badge must NOT contain raw lat/long: {runner_coords_check['phase1Badge']}"
            assert not runner_coords_check['phase2HasRawGPS'], f"Phase 2 badge must NOT contain raw lat/long: {runner_coords_check['phase2Badge']}"
            assert "Vendor Shop" in runner_coords_check['phase1Badge'], "Phase 1 badge must have readable store name"
            assert "Drop-off" in runner_coords_check['phase2Badge'], "Phase 2 badge must have readable drop-off landmark"
            assert "Gupta General Store" in runner_coords_check['updatedPhase1Badge'], "updatePhase1VendorMap must bind store name"

            await take_screenshot(ws, "proof_runner_readable_landmarks_no_gps.png", mid); mid += 1

            # -----------------------------------------------------------------
            # TEST 3: RUNNER ACTION BUTTONS (CSS GRID 50/25/25, >= 48PX HEIGHT)
            # -----------------------------------------------------------------
            print("\n--- TEST 3: Runner Action Buttons CSS Grid & Height Verification ---")
            buttons_css_check = await eval_js(ws, """
                (() => {
                    // Activate Phase 2 delivery view
                    state.activeRunState = 'delivery';
                    const step1 = document.getElementById('run-step-1');
                    const step2 = document.getElementById('run-step-2');
                    if (step1) step1.className = "bg-white p-4 rounded-2xl border border-slate-200 shadow-xs space-y-3.5 opacity-80";
                    if (step2) {
                        step2.className = "bg-white p-4 rounded-2xl border-2 border-blue-500 shadow-lg space-y-3.5 opacity-100";
                    }

                    const navBtn = document.getElementById('btn-navigate-customer');
                    const chatBtn = navBtn.parentElement.querySelector('button');
                    const callBtn = document.getElementById('cust-phone-link');

                    const navRect = navBtn.getBoundingClientRect();
                    const chatRect = chatBtn.getBoundingClientRect();
                    const callRect = callBtn.getBoundingClientRect();
                    const parentRect = navBtn.parentElement.getBoundingClientRect();

                    const parentDisplay = window.getComputedStyle(navBtn.parentElement).display;
                    const parentGridCols = window.getComputedStyle(navBtn.parentElement).gridTemplateColumns;

                    return {
                        parentDisplay,
                        parentGridCols,
                        parentWidth: parentRect.width,
                        navWidth: navRect.width,
                        navHeight: navRect.height,
                        chatWidth: chatRect.width,
                        chatHeight: chatRect.height,
                        callWidth: callRect.width,
                        callHeight: callRect.height,
                        chatText: chatBtn.innerText.trim(),
                        navWidthPercent: Math.round((navRect.width / parentRect.width) * 100),
                        chatWidthPercent: Math.round((chatRect.width / parentRect.width) * 100),
                        callWidthPercent: Math.round((callRect.width / parentRect.width) * 100)
                    };
                })()
            """, mid); mid += 1
            print("Buttons CSS Layout Check:", json.dumps(buttons_css_check, indent=2))
            assert buttons_css_check['parentDisplay'] == 'grid', f"Parent must use CSS grid: {buttons_css_check['parentDisplay']}"
            assert buttons_css_check['navHeight'] >= 48, f"Navigate button height must be >= 48px, got {buttons_css_check['navHeight']}"
            assert buttons_css_check['chatHeight'] >= 48, f"Chat button height must be >= 48px, got {buttons_css_check['chatHeight']}"
            assert buttons_css_check['callHeight'] >= 48, f"Call button height must be >= 48px, got {buttons_css_check['callHeight']}"
            assert abs(buttons_css_check['navHeight'] - buttons_css_check['chatHeight']) <= 1, "Buttons must have identical heights"
            assert abs(buttons_css_check['chatHeight'] - buttons_css_check['callHeight']) <= 1, "Buttons must have identical heights"
            assert "Chat & Pin" in buttons_css_check['chatText'], f"Chat button text must include Chat & Pin: {buttons_css_check['chatText']}"
            assert 45 <= buttons_css_check['navWidthPercent'] <= 55, f"Navigate button should take approx 50% width, got {buttons_css_check['navWidthPercent']}%"
            assert 20 <= buttons_css_check['chatWidthPercent'] <= 28, f"Chat button should take approx 25% width, got {buttons_css_check['chatWidthPercent']}%"
            assert 20 <= buttons_css_check['callWidthPercent'] <= 28, f"Call button should take approx 25% width, got {buttons_css_check['callWidthPercent']}%"

            await take_screenshot(ws, "proof_runner_action_buttons_grid_layout.png", mid); mid += 1

            print("\n=======================================================")
            print("ALL 3 TEST SUITES PASSED WITH 100% SUCCESS!")
            print("=======================================================")

    finally:
        chrome_proc.terminate()
        http_proc.terminate()
        if os.path.exists(TEMP_DIR):
            shutil.rmtree(TEMP_DIR, ignore_errors=True)

if __name__ == '__main__':
    asyncio.run(main())
