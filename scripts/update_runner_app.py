import os

path = "public_web/runner/index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update Phase 1 badge to remove raw coordinates
old_phase1_badge = """            <div class="absolute bottom-2.5 left-2.5 bg-white/95 backdrop-blur-xs px-2.5 py-1 rounded-lg border border-slate-200 text-[10px] font-bold text-slate-800 flex items-center space-x-1.5 shadow-xs">
              <i data-lucide="store" class="w-3.5 h-3.5 text-emerald-600"></i>
              <span>Vendor Shop: 26.2230, 85.3520</span>
            </div>"""

new_phase1_badge = """            <div class="absolute bottom-2.5 left-2.5 bg-white/95 backdrop-blur-xs px-2.5 py-1 rounded-lg border border-slate-200 text-[10px] font-bold text-slate-800 flex items-center space-x-1.5 shadow-xs">
              <i data-lucide="store" class="w-3.5 h-3.5 text-emerald-600"></i>
              <span id="vendor-shop-location-badge">Vendor Shop: Sharma Kirana</span>
            </div>"""

# 2. Update Phase 1 action buttons to clean Grid layout with 48px min-height
old_phase1_btns = """            <div class="pt-2 flex space-x-2">
              <!-- Direct Intent Scheme Navigation Link to Vendor -->
              <a id="btn-navigate-shop" 
                 href="https://www.google.com/maps/dir/?api=1&destination=26.2230,85.3520&travelmode=driving&dir_action=navigate" 
                 target="_blank" 
                 rel="noopener noreferrer" 
                 class="flex-1 py-3 px-4 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold flex items-center justify-center space-x-2 shadow-xs transition active:scale-95">
                <i data-lucide="navigation-2" class="w-4 h-4"></i>
                <span data-i18n="nav_to_vendor">Navigate to Shop</span>
              </a>
              <a id="store-phone-link" href="tel:9876543210" class="py-3 px-4 bg-slate-200 hover:bg-slate-300 text-slate-800 rounded-xl text-xs font-bold flex items-center justify-center space-x-1.5 transition active:scale-95">
                <i data-lucide="phone" class="w-4 h-4"></i>
                <span data-i18n="call_btn">Call</span>
              </a>
            </div>"""

new_phase1_btns = """            <div class="pt-2 grid grid-cols-3 gap-2 w-full">
              <!-- Direct Intent Scheme Navigation Link to Vendor (66% = 2 cols) -->
              <a id="btn-navigate-shop" 
                 href="https://www.google.com/maps/dir/?api=1&destination=26.2230,85.3520&travelmode=driving&dir_action=navigate" 
                 target="_blank" 
                 rel="noopener noreferrer" 
                 class="col-span-2 min-h-[48px] h-12 py-2 px-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold flex items-center justify-center space-x-2 shadow-xs transition active:scale-95 text-center cursor-pointer">
                <i data-lucide="navigation-2" class="w-4 h-4 shrink-0"></i>
                <span data-i18n="nav_to_vendor" class="truncate">Navigate to Shop</span>
              </a>
              <a id="store-phone-link" 
                 href="tel:9876543210" 
                 class="col-span-1 min-h-[48px] h-12 py-2 px-2 bg-slate-200 hover:bg-slate-300 text-slate-800 rounded-xl text-xs font-bold flex items-center justify-center space-x-1.5 transition active:scale-95 text-center cursor-pointer">
                <i data-lucide="phone" class="w-4 h-4 shrink-0"></i>
                <span data-i18n="call_btn" class="truncate">Call</span>
              </a>
            </div>"""

# 3. Update Phase 2 badge to remove coordinates and show landmark
old_phase2_badge = """            <div class="absolute bottom-2.5 left-2.5 bg-white/95 backdrop-blur-xs px-2.5 py-1 rounded-lg border border-slate-200 text-[10px] font-bold text-slate-800 flex items-center space-x-1.5 shadow-xs">
              <i data-lucide="map-pin" class="w-3.5 h-3.5 text-blue-600"></i>
              <span id="customer-coords-display">GPS Verified Drop-off</span>
            </div>"""

new_phase2_badge = """            <div class="absolute bottom-2.5 left-2.5 bg-white/95 backdrop-blur-xs px-2.5 py-1 rounded-lg border border-slate-200 text-[10px] font-bold text-slate-800 flex items-center space-x-1.5 shadow-xs">
              <i data-lucide="map-pin" class="w-3.5 h-3.5 text-blue-600"></i>
              <span id="customer-coords-display">Drop-off: Near Panchayat Bhawan</span>
            </div>"""

# 4. Update Phase 2 Action Buttons to strict 4-column Grid (50% Navigate, 25% Chat & Pin, 25% Call)
old_phase2_btns = """            <div class="pt-2 flex space-x-2">
              <!-- Direct Intent Scheme Navigation Link to Customer -->
              <a id="btn-navigate-customer" 
                 href="https://www.google.com/maps/dir/?api=1&destination=26.2315,85.3610&travelmode=driving&dir_action=navigate" 
                 target="_blank" 
                 rel="noopener noreferrer" 
                 class="flex-1 py-3 px-4 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold flex items-center justify-center space-x-2 shadow-xs transition active:scale-95">
                <i data-lucide="navigation-2" class="w-4 h-4"></i>
                <span data-i18n="nav_to_customer">Navigate to Customer</span>
              </a>
              <button onclick="openRunnerOrderChat()" class="py-3 px-3 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border border-indigo-200 rounded-xl text-xs font-bold flex items-center justify-center space-x-1.5 transition active:scale-95">
                <i data-lucide="message-square" class="w-4 h-4"></i>
                <span data-i18n="chat_btn">Chat</span>
              </button>
              <a id="cust-phone-link" href="tel:9811224488" class="py-3 px-4 bg-slate-200 hover:bg-slate-300 text-slate-800 rounded-xl text-xs font-bold flex items-center justify-center space-x-1.5">
                <i data-lucide="phone" class="w-4 h-4"></i>
                <span data-i18n="call_btn">Call</span>
              </a>
            </div>"""

new_phase2_btns = """            <div class="pt-2 grid grid-cols-4 gap-2 w-full">
              <!-- Direct Intent Scheme Navigation Link to Customer (50% = 2 cols) -->
              <a id="btn-navigate-customer" 
                 href="https://www.google.com/maps/dir/?api=1&destination=26.2315,85.3610&travelmode=driving&dir_action=navigate" 
                 target="_blank" 
                 rel="noopener noreferrer" 
                 class="col-span-2 min-h-[48px] h-12 py-2 px-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold flex items-center justify-center space-x-2 shadow-xs transition active:scale-95 text-center cursor-pointer">
                <i data-lucide="navigation-2" class="w-4 h-4 shrink-0"></i>
                <span data-i18n="nav_to_customer" class="truncate">Navigate to Customer</span>
              </a>
              <!-- Chat & Pin Button (25% = 1 col) -->
              <button type="button" 
                      onclick="openRunnerOrderChat()" 
                      class="col-span-1 min-h-[48px] h-12 py-2 px-2 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border border-indigo-200 rounded-xl text-xs font-bold flex items-center justify-center space-x-1.5 transition active:scale-95 text-center cursor-pointer">
                <i data-lucide="message-square" class="w-4 h-4 shrink-0"></i>
                <span data-i18n="chat_btn" class="truncate">Chat & Pin</span>
              </button>
              <!-- Call Button (25% = 1 col) -->
              <a id="cust-phone-link" 
                 href="tel:9811224488" 
                 class="col-span-1 min-h-[48px] h-12 py-2 px-2 bg-slate-200 hover:bg-slate-300 text-slate-800 rounded-xl text-xs font-bold flex items-center justify-center space-x-1.5 transition active:scale-95 text-center cursor-pointer">
                <i data-lucide="phone" class="w-4 h-4 shrink-0"></i>
                <span data-i18n="call_btn" class="truncate">Call</span>
              </a>
            </div>"""

# 5. Update updatePhase1VendorMap and updatePhase2CustomerMap in JS
old_update_vendor_map = """    function updatePhase1VendorMap(lat, lng) {
      const vLat = Number(lat || state.activeMission?.store_latitude || 26.2230).toFixed(4);
      const vLng = Number(lng || state.activeMission?.store_longitude || 85.3520).toFixed(4);
      const mapImg = document.getElementById('vendor-static-map-img');
      if (mapImg) {
        mapImg.src = `https://maps.googleapis.com/maps/api/staticmap?center=${vLat},${vLng}&zoom=16&size=600x260&scale=2&maptype=roadmap&markers=color:green%7Clabel:V%7C${vLat},${vLng}&key=${GMAPS_API_KEY}`;
      }
      const navBtn = document.getElementById('btn-navigate-shop');
      if (navBtn) {
        navBtn.href = `https://www.google.com/maps/dir/?api=1&destination=${vLat},${vLng}&travelmode=driving&dir_action=navigate`;
      }
    }"""

new_update_vendor_map = """    function updatePhase1VendorMap(lat, lng, storeName) {
      const vLat = Number(lat || state.activeMission?.store_latitude || 26.2230).toFixed(4);
      const vLng = Number(lng || state.activeMission?.store_longitude || 85.3520).toFixed(4);
      const sName = storeName || state.activeMission?.store_name || "Sharma Kirana";
      const mapImg = document.getElementById('vendor-static-map-img');
      if (mapImg) {
        mapImg.src = `https://maps.googleapis.com/maps/api/staticmap?center=${vLat},${vLng}&zoom=16&size=600x260&scale=2&maptype=roadmap&markers=color:green%7Clabel:V%7C${vLat},${vLng}&key=${GMAPS_API_KEY}`;
      }
      const badge = document.getElementById('vendor-shop-location-badge');
      if (badge) {
        badge.innerText = `Vendor Shop: ${sName}`;
      }
      const navBtn = document.getElementById('btn-navigate-shop');
      if (navBtn) {
        navBtn.href = `https://www.google.com/maps/dir/?api=1&destination=${vLat},${vLng}&travelmode=driving&dir_action=navigate`;
      }
    }"""

old_update_cust_map = """      const coordsDisp = document.getElementById('customer-coords-display');
      if (coordsDisp) {
        coordsDisp.innerText = `Customer Location: ${latStr}, ${lngStr}`;
      }"""

new_update_cust_map = """      const coordsDisp = document.getElementById('customer-coords-display');
      if (coordsDisp) {
        const dropLandmark = state.activeMission?.customer_landmark || state.activeMission?.delivery_landmark || "Near Panchayat Bhawan";
        coordsDisp.innerText = `Drop-off: ${dropLandmark}`;
      }"""

content_norm = content.replace("\r\n", "\n")

replacements = [
    (old_phase1_badge, new_phase1_badge, "Phase 1 Badge (coordinates eradicated)"),
    (old_phase1_btns, new_phase1_btns, "Phase 1 Action Buttons (Grid layout)"),
    (old_phase2_badge, new_phase2_badge, "Phase 2 Badge (coordinates eradicated)"),
    (old_phase2_btns, new_phase2_btns, "Phase 2 Action Buttons (Grid 50/25/25 48px layout)"),
    (old_update_vendor_map, new_update_vendor_map, "JS updatePhase1VendorMap (human readable name)"),
    (old_update_cust_map, new_update_cust_map, "JS updatePhase2CustomerMap (human readable landmark)")
]

for old, new, desc in replacements:
    if old in content_norm:
        content_norm = content_norm.replace(old, new, 1)
        print(f"Applied: {desc}")
    else:
        print(f"FAILED to find: {desc}")

with open(path, "w", encoding="utf-8", newline="\r\n") as f:
    f.write(content_norm)

print("Runner app update finished.")
