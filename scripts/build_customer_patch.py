import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/customer/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. ADD LEAFLET CSS & JS TO HEAD IF NOT PRESENT
leaflet_head = """  <!-- Leaflet Map CSS & JS -->
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin=""/>
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
"""
if 'leaflet.css' not in content:
    content = content.replace(
        '<script type="text/javascript" src="https://cdn.jsdelivr.net/npm/toastify-js"></script>',
        '<script type="text/javascript" src="https://cdn.jsdelivr.net/npm/toastify-js"></script>\n' + leaflet_head
    )
    print("Leaflet added to head")

# 2. ADD MODALS (MODAL-MONTHLY-RATION AND MODAL-LOCATION-MAP-PICKER)
modals_to_add = """
    <!-- ===================================================================== -->
    <!-- MONTHLY RATION LIST MODAL (Phase 7: My Monthly Ration List) -->
    <!-- ===================================================================== -->
    <div id="modal-monthly-ration" class="hidden fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
      <div class="w-full max-w-sm bg-white rounded-3xl p-4 shadow-2xl flex flex-col max-h-[90vh] border border-slate-200">
        <!-- Header -->
        <div class="flex items-center justify-between pb-3 border-b border-slate-100">
          <div class="flex items-center space-x-2.5">
            <button onclick="closeModal('modal-monthly-ration')" class="w-8 h-8 rounded-full bg-slate-100 text-slate-600 flex items-center justify-center hover:bg-slate-200 transition">
              <i data-lucide="arrow-left" class="w-4 h-4"></i>
            </button>
            <div>
              <div class="flex items-center space-x-1.5">
                <h3 class="text-xs font-bold text-slate-900" data-i18n="monthly_ration_title">My Monthly Ration List</h3>
                <span class="text-[9px] bg-emerald-100 text-emerald-800 font-bold px-1.5 py-0.2 rounded">Essentials</span>
              </div>
              <p class="text-[10px] text-slate-500">Auto-synced with nearest store stock & prices</p>
            </div>
          </div>
          <button onclick="saveCurrentMonthlyRationList()" class="px-2.5 py-1 bg-emerald-50 hover:bg-emerald-100 text-emerald-800 text-[10px] font-bold rounded-lg border border-emerald-200">
            Save List
          </button>
        </div>

        <!-- Add Custom Item Bar -->
        <div class="pt-3 pb-2 flex items-center space-x-1.5">
          <select id="ration-add-item-select" class="flex-1 text-xs bg-slate-50 border border-slate-200 rounded-xl px-2.5 py-2 text-slate-700 focus:outline-none focus:border-emerald-600">
            <!-- Populated via JS -->
          </select>
          <button onclick="addCustomItemToMonthlyRation()" class="px-3 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-xl text-xs transition active:scale-95 shrink-0 flex items-center space-x-1">
            <i data-lucide="plus" class="w-3.5 h-3.5"></i>
            <span>Add</span>
          </button>
        </div>

        <!-- Ration Items List -->
        <div id="ration-items-container" class="flex-1 overflow-y-auto space-y-2 py-1 pr-1">
          <!-- Dynamically populated via renderMonthlyRationItems() -->
        </div>

        <!-- Bottom Actions & Estimated Total -->
        <div class="pt-3 border-t border-slate-100 space-y-2.5">
          <div class="flex items-center justify-between text-xs bg-slate-50 p-2.5 rounded-xl border border-slate-200">
            <div>
              <span class="text-[10px] text-slate-500 uppercase font-bold block">Estimated Total</span>
              <span id="ration-total-items-count" class="text-[10px] font-medium text-slate-600">0 items</span>
            </div>
            <span id="ration-estimated-total-amount" class="text-sm font-extrabold text-emerald-900 font-mono">₹0.00</span>
          </div>

          <div class="grid grid-cols-2 gap-2">
            <button onclick="saveCurrentMonthlyRationList()" class="py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-800 font-bold rounded-xl text-xs transition active:scale-95 text-center">
              Save Changes
            </button>
            <button onclick="addMonthlyRationListToCart()" id="btn-ration-add-to-cart" class="py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-xl text-xs transition active:scale-95 shadow-xs flex items-center justify-center space-x-1">
              <i data-lucide="shopping-cart" class="w-3.5 h-3.5"></i>
              <span>Check & Add to Cart</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ===================================================================== -->
    <!-- LOCATION MAP PICKER MODAL (Phase 3: Interactive Draggable Pin) -->
    <!-- ===================================================================== -->
    <div id="modal-location-map-picker" class="hidden fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
      <div class="w-full max-w-sm bg-white rounded-3xl p-4 shadow-2xl flex flex-col border border-slate-200 space-y-3">
        <!-- Header -->
        <div class="flex items-center justify-between pb-2 border-b border-slate-100">
          <div class="flex items-center space-x-2">
            <button onclick="closeModal('modal-location-map-picker')" class="w-7 h-7 rounded-full bg-slate-100 text-slate-600 flex items-center justify-center">
              <i data-lucide="arrow-left" class="w-3.5 h-3.5"></i>
            </button>
            <div>
              <h3 class="text-xs font-bold text-slate-900" data-i18n="map_picker_title">Select Delivery Location</h3>
              <p class="text-[10px] text-slate-500">Drag pin or tap map to set exact home/shop</p>
            </div>
          </div>
          <button onclick="detectExactGPS(false)" class="text-[10px] text-emerald-700 bg-emerald-50 px-2 py-1 rounded-lg border border-emerald-200 font-bold flex items-center space-x-1">
            <i data-lucide="crosshair" class="w-3 h-3"></i>
            <span>Current GPS</span>
          </button>
        </div>

        <!-- Leaflet Map Container -->
        <div id="location-picker-canvas" class="w-full h-56 rounded-2xl border border-slate-200 bg-slate-100 overflow-hidden relative z-0 shadow-inner"></div>

        <!-- Selected Coords & Geofence Status -->
        <div class="p-2.5 bg-slate-50 rounded-xl border border-slate-200 space-y-1.5 text-xs">
          <div class="flex items-center justify-between">
            <span class="text-[10px] font-bold text-slate-500 uppercase">Selected GPS Pin:</span>
            <span id="picker-coords-text" class="font-mono text-[11px] font-bold text-slate-800">26.2315, 85.3610</span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-[10px] font-bold text-slate-500 uppercase">Distance to Store:</span>
            <span id="picker-distance-text" class="font-bold text-slate-800">~1.2 km</span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-[10px] font-bold text-slate-500 uppercase">Service Status:</span>
            <span id="picker-service-badge" class="text-[10px] font-extrabold px-1.5 py-0.2 rounded bg-emerald-100 text-emerald-800">Serviceable (Delivery ₹15)</span>
          </div>
        </div>

        <!-- Action Button -->
        <button onclick="confirmMapPickedLocation()" id="btn-confirm-map-pin" class="w-full py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-xl text-xs shadow-xs transition active:scale-95 flex items-center justify-center space-x-1.5">
          <i data-lucide="check" class="w-3.5 h-3.5"></i>
          <span>Confirm This Pin for Delivery</span>
        </button>
      </div>
    </div>
"""

if 'id="modal-monthly-ration"' not in content:
    # Insert right before modal-rural-address
    content = content.replace('<div id="modal-rural-address"', modals_to_add + '\n    <div id="modal-rural-address"')
    print("Modals added before modal-rural-address")

# 3. ADD "SELECT ON MAP" BUTTON INSIDE MODAL-RURAL-ADDRESS
map_btn_html = """
        <!-- Map Picker Action (Phase 3: Exact Location Pin) -->
        <div class="p-3 bg-indigo-50 rounded-xl border border-indigo-200 flex items-center justify-between">
          <div class="min-w-0 pr-2">
            <p class="text-[11px] font-bold text-indigo-950" data-i18n="map_picker_header">Select Exact Pin on Map</p>
            <p id="modal-map-pin-status" class="text-[10px] text-indigo-700 truncate">Tap map to pinpoint village doorstep</p>
          </div>
          <button type="button" onclick="openLocationMapPickerModal()" id="modal-map-picker-btn" class="py-1.5 px-3 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-lg text-[11px] shadow-xs active:scale-95 transition flex items-center space-x-1.5 shrink-0">
            <i data-lucide="map" class="w-3.5 h-3.5"></i>
            <span data-i18n="open_map_btn">Open Map</span>
          </button>
        </div>
"""

if 'openLocationMapPickerModal()' not in content:
    content = content.replace('<!-- Detailed Form Fields -->', map_btn_html + '\n        <!-- Detailed Form Fields -->')
    print("Map picker button added to modal-rural-address")

with open('public_web/customer/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Modals & Map picker button successfully written to customer index.html")
