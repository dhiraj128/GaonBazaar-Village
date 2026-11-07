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
temp_dir = r"C:\Users\dhira\AppData\Local\Temp\chrome_vendor_eval"

async def eval_vendor():
    # 1. Start HTTP Server if not already responding
    http_proc = None
    try:
        urllib.request.urlopen(f"http://127.0.0.1:{port}/vendor/index.html", timeout=1)
        print("Using active HTTP server on port", port)
    except Exception:
        print("Starting HTTP server on port", port)
        http_proc = subprocess.Popen(
            [sys.executable, "-m", "http.server", str(port), "--directory", "public_web"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        time.sleep(1.5)

    # 2. Launch Chrome
    chrome_proc = None
    try:
        urllib.request.urlopen(f"http://127.0.0.1:{cdp_port}/json", timeout=1)
        print("Chrome CDP already active on port", cdp_port)
    except Exception:
        os.makedirs(temp_dir, exist_ok=True)
        chrome_proc = subprocess.Popen([
            chrome_path,
            f"--remote-debugging-port={cdp_port}",
            f"--user-data-dir={temp_dir}",
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            f"http://127.0.0.1:{port}/vendor/index.html"
        ])
        time.sleep(2)

    # Connect to Vendor page
    pages_json = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{cdp_port}/json").read())
    vendor_page = next((p for p in pages_json if "vendor" in p.get("url", "")), None)
    if not vendor_page:
        # Navigate an available page
        ws_url = pages_json[0]["webSocketDebuggerUrl"]
        async with websockets.connect(ws_url, max_size=10_000_000) as ws:
            await ws.send(json.dumps({
                "id": 1,
                "method": "Page.navigate",
                "params": {"url": f"http://127.0.0.1:{port}/vendor/index.html"}
            }))
            await asyncio.sleep(2)
        pages_json = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{cdp_port}/json").read())
        vendor_page = pages_json[0]

    ws_url = vendor_page["webSocketDebuggerUrl"]
    print("Connected to Vendor page WebSocket:", ws_url)

    async with websockets.connect(ws_url, max_size=10_000_000) as ws:
        await ws.send(json.dumps({"id": 2, "method": "Page.enable"}))
        await ws.send(json.dumps({"id": 3, "method": "Runtime.enable"}))

        vendor_test_expr = """
        (() => {
          const res = [];
          const check = (pass, msg) => res.push({ pass: !!pass, msg });

          // 1. MASTER_SKU_DATABASE Verification
          check(Array.isArray(window.MASTER_SKU_DATABASE), 'MASTER_SKU_DATABASE is array');
          check(window.MASTER_SKU_DATABASE.length >= 30, 'MASTER_SKU_DATABASE contains at least 30 items (found ' + window.MASTER_SKU_DATABASE.length + ')');

          const firstSku = window.MASTER_SKU_DATABASE[0];
          check(firstSku.id && firstSku.product_name && firstSku.brand && firstSku.mrp > 0 && firstSku.image_url, 'SKU has id, product_name, brand, mrp, image_url');
          check(firstSku.image_url.startsWith('https://'), 'SKU image_url is valid https link');

          // 2. Open Add Product Modal
          openAddProductModal();
          const modal = document.getElementById('modal-add-product');
          check(!modal.classList.contains('hidden'), 'modal-add-product opened via openAddProductModal');

          // 3. Search Master SKU Library
          const searchInput = document.getElementById('catalog-library-search');
          check(searchInput !== null, 'catalog-library-search exists');
          searchInput.value = 'atta';
          filterMasterCatalog();

          const resultsContainer = document.getElementById('master-catalog-results');
          check(resultsContainer.children.length > 0, 'master-catalog-results populated with matching items');

          // 4. Select SKU and verify locked fields
          const atta = window.MASTER_SKU_DATABASE.find(s => s.product_name.includes('Atta'));
          selectCatalogItem(atta);

          const nameInp = document.getElementById('new-item-name');
          const brandInp = document.getElementById('new-item-brand');
          const mrpInp = document.getElementById('new-item-mrp');
          const priceInp = document.getElementById('new-item-price');
          const stockInp = document.getElementById('new-item-stock');
          const previewImg = document.getElementById('add-item-preview-img');

          check(nameInp.readOnly === true, 'Product Name is LOCKED (read-only)');
          check(brandInp.readOnly === true, 'Brand is LOCKED (read-only)');
          check(mrpInp.readOnly === true, 'MRP is LOCKED (read-only)');
          check(nameInp.value === atta.product_name, 'Product Name auto-filled from library: ' + nameInp.value);
          check(mrpInp.value == atta.mrp, 'MRP auto-filled from library: ' + mrpInp.value);
          check(previewImg.src.includes('unsplash.com'), 'Preview image auto-filled with locked library photo');

          check(priceInp.readOnly === false, 'Selling Price is vendor EDITABLE');
          check(stockInp.readOnly === false, 'Stock Quantity is vendor EDITABLE');

          // 5. Submit to Live Store
          priceInp.value = 235;
          stockInp.value = 40;
          submitLiveStoreItem();

          check(modal.classList.contains('hidden'), 'modal-add-product closed after adding to store');
          
          const inventory = JSON.parse(localStorage.getItem('gb_vendor_inventory') || '[]');
          const addedItem = inventory.find(i => i.product_name === atta.product_name || i.name === atta.product_name);
          check(addedItem !== undefined, 'Item added to live store inventory');
          check(addedItem && addedItem.price === 235, 'Item saved with vendor selling price ₹235');
          check(addedItem && addedItem.stock === 40, 'Item saved with stock quantity 40');
          check(addedItem && addedItem.image_url.includes('unsplash.com'), 'Item saved with locked platform image');

          return res;
        })()
        """

        await ws.send(json.dumps({
            "id": 10,
            "method": "Runtime.evaluate",
            "params": {
                "expression": vendor_test_expr,
                "returnByValue": True,
                "awaitPromise": True
            }
        }))

        while True:
            msg = await ws.recv()
            data = json.loads(msg)
            if data.get("id") == 10:
                if "exceptionDetails" in data["result"]:
                    print("JS Exception in Vendor test:", data["result"]["exceptionDetails"])
                    return False
                items = data["result"]["result"]["value"]
                all_passed = True
                print("\n--- Vendor Master SKU Library Test Results ---")
                for it in items:
                    st = "PASS" if it["pass"] else "FAIL"
                    if not it["pass"]: all_passed = False
                    print(f"  [{st}] {it['msg']}")
                return all_passed

    if chrome_proc: chrome_proc.terminate()
    if http_proc: http_proc.terminate()

if __name__ == "__main__":
    success = asyncio.run(eval_vendor())
    sys.exit(0 if success else 1)
