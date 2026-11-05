import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/customer/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add Leaflet CSS and JS to <head>
leaflet_head = """  <!-- Leaflet Map CSS & JS -->
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin=""/>
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
"""
if 'leaflet.css' not in content:
    content = content.replace(
        '<script type="text/javascript" src="https://cdn.jsdelivr.net/npm/toastify-js"></script>',
        '<script type="text/javascript" src="https://cdn.jsdelivr.net/npm/toastify-js"></script>\n' + leaflet_head
    )
    print("Added Leaflet to <head>")

# 2. Update view-orders section (Orders Tab HTML)
old_orders_regex = r'<!-- =================================================================== -->\s*<!-- TAB 4: ORDERS & LIVE DELIVERY TRACKING -->\s*<!-- =================================================================== -->\s*<section id="view-orders"[\s\S]*?</section>'

new_orders_html = """<!-- =================================================================== -->
      <!-- TAB 4: ORDERS & LIVE DELIVERY TRACKING -->
      <!-- =================================================================== -->
      <section id="view-orders" class="tab-view hidden flex-1 flex flex-col bg-slate-50">
        <!-- Header with Back Button -->
        <header class="sticky top-0 z-30 bg-white/95 backdrop-blur-md border-b border-slate-200 px-4 py-3 flex items-center space-x-3 shadow-2xs">
          <button onclick="historyBack()" class="w-9 h-9 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-700 flex items-center justify-center transition active:scale-95" aria-label="Back">
            <i data-lucide="arrow-left" class="w-4 h-4"></i>
          </button>
          <div>
            <h2 class="text-sm font-bold text-slate-900" data-i18n="orders_title">Your Orders</h2>
            <p class="text-[10px] text-slate-500" data-i18n="orders_sub">Live Village Tracking & History</p>
          </div>
        </header>

        <div class="p-4 space-y-4 flex-1 overflow-y-auto pb-24">
          <!-- SECTION A: ACTIVE ORDERS -->
          <div id="section-active-orders" class="space-y-3">
            <!-- Active Order Live Tracking Card -->
            <div id="active-order-card" class="bg-white p-4 rounded-3xl border border-slate-200 shadow-md space-y-3.5 relative overflow-hidden">
              <div class="flex items-center justify-between border-b border-slate-100 pb-2.5">
                <div>
                  <span class="text-[10px] font-bold text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200" data-i18n="active_mission">Active Mission</span>
                  <h3 class="text-sm font-extrabold text-slate-900 mt-0.5" id="active-order-id-display">Order #GB-9821</h3>
                </div>
                <span id="order-status-badge" class="px-2.5 py-1 bg-amber-50 text-amber-800 text-[11px] font-bold rounded-lg border border-amber-200 flex items-center space-x-1">
                  <span class="w-2 h-2 rounded-full bg-amber-500 animate-ping"></span>
                  <span id="order-status-text">Out for Delivery</span>
                </span>
              </div>

              <!-- Delivery OTP Card (Masked with Reveal on Tap) -->
              <div class="p-3 bg-emerald-50 rounded-2xl border border-emerald-200 flex items-center justify-between">
                <div>
                  <p class="text-[10px] font-semibold text-emerald-800" data-i18n="otp_handover_title">Delivery Verification OTP</p>
                  <p class="text-[10px] text-emerald-600" data-i18n="otp_handover_sub">Share with runner ONLY after inspecting goods</p>
                </div>
                <button type="button" onclick="revealDeliveryOtp()" id="order-otp-badge" class="text-base font-black text-emerald-900 font-mono tracking-widest bg-white px-2.5 py-1 rounded-xl shadow-xs border border-emerald-200 hover:bg-emerald-100 transition active:scale-95" title="Tap to reveal OTP">
                  ••••
                </button>
              </div>

              <!-- VERTICAL LIVE ORDER TRACKING TIMELINE (Phase 2.1) -->
              <div class="p-3 bg-slate-50 rounded-2xl border border-slate-200 space-y-2.5">
                <div class="flex items-center justify-between border-b border-slate-200/60 pb-1.5">
                  <span class="text-[10px] font-bold text-slate-700 uppercase tracking-wider flex items-center space-x-1">
                    <i data-lucide="git-commit" class="w-3.5 h-3.5 text-emerald-600"></i>
                    <span data-i18n="tracking_stepper_title">Live Delivery Progress</span>
                  </span>
                  <span id="tracking-last-sync-badge" class="text-[9px] font-mono text-emerald-700 font-semibold flex items-center space-x-1">
                    <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-ping"></span>
                    <span>Live Telemetry Active</span>
                  </span>
                </div>
                <!-- Vertical Stepper Container -->
                <div id="order-tracking-vertical" class="py-1">
                  <!-- Dynamically rendered via renderVerticalOrderTrackingTimeline() -->
                </div>
              </div>

              <!-- GENUINE LIVE RUNNER MAP & TELEMETRY (Phase 2.2, 2.3, 2.4, 2.5) -->
              <div class="p-3 bg-slate-50 rounded-2xl border border-slate-200 space-y-2 text-xs">
                <div class="flex items-center justify-between border-b border-slate-200/70 pb-1.5">
                  <span class="text-[10px] font-bold text-slate-700 uppercase tracking-wide flex items-center space-x-1">
                    <i data-lucide="map-pin" class="w-3.5 h-3.5 text-emerald-600"></i>
                    <span data-i18n="route_map_title">Live Route Telemetry</span>
                  </span>
                  <span id="runner-gps-timestamp" class="text-[10px] font-medium text-slate-500">Runner location temporarily unavailable</span>
                </div>

                <!-- Leaflet Interactive Delivery Map -->
                <div id="order-live-map" class="w-full h-44 rounded-xl border border-slate-200 bg-slate-100 relative z-0 overflow-hidden shadow-inner"></div>

                <!-- Pickup & Destination Cards -->
                <div class="grid grid-cols-2 gap-2 text-[11px] pt-1">
                  <div class="p-2 bg-white rounded-xl border border-slate-200 space-y-0.5">
                    <p class="text-[9px] font-bold text-slate-400 uppercase" data-i18n="store_pickup">Store Pickup</p>
                    <p id="tracking-store-name" class="font-bold text-slate-900 truncate">Sharma Kirana</p>
                    <p id="tracking-store-sub" class="text-[9px] text-slate-500 truncate">Chaturshi Chowk</p>
                  </div>
                  <div class="p-2 bg-white rounded-xl border border-slate-200 space-y-0.5">
                    <p class="text-[9px] font-bold text-slate-400 uppercase" data-i18n="customer_dest">Customer Destination</p>
                    <p id="tracking-dest-address" class="font-bold text-slate-900 truncate">Minapur Village</p>
                    <p id="tracking-dest-landmark" class="text-[9px] text-emerald-700 truncate">Near Panchayat Bhawan</p>
                  </div>
                </div>

                <!-- ETA Banner -->
                <div class="flex items-center justify-between p-2 bg-emerald-50 rounded-xl border border-emerald-200">
                  <div class="flex items-center space-x-1.5">
                    <i data-lucide="clock" class="w-3.5 h-3.5 text-emerald-700"></i>
                    <span class="text-[10px] font-semibold text-emerald-900" data-i18n="est_delivery_title">Estimated Delivery Window:</span>
                  </div>
                  <span id="order-eta-display" class="text-xs font-extrabold text-emerald-950 font-mono">~25-35 mins</span>
                </div>

                <!-- Google Maps Navigation Intent Button -->
                <a id="tracking-maps-intent-btn" href="#" target="_blank" class="w-full py-2 bg-white hover:bg-slate-50 text-emerald-800 border border-emerald-300 font-bold rounded-xl text-center text-xs flex items-center justify-center space-x-1.5 shadow-xs transition active:scale-95">
                  <i data-lucide="map" class="w-3.5 h-3.5 text-emerald-600"></i>
                  <span data-i18n="open_in_google_maps">Start Google Maps Turn-by-Turn Navigation</span>
                </a>
              </div>

              <!-- Runner Details & Action Controls -->
              <div class="bg-slate-50 p-3 rounded-2xl border border-slate-200 flex items-center justify-between">
                <div class="flex items-center space-x-2.5">
                  <div class="w-10 h-10 rounded-full bg-emerald-600 text-white flex items-center justify-center font-bold text-xs shadow-xs">
                    <i data-lucide="bike" class="w-5 h-5 text-white"></i>
                  </div>
                  <div>
                    <h4 id="order-runner-name" class="text-xs font-bold text-slate-900">Assigned Delivery Partner</h4>
                    <p id="order-runner-badge" class="text-[10px] text-slate-500">Motorcycle • GaonBazaar Partner</p>
                  </div>
                </div>
                <div class="flex space-x-1.5">
                  <a id="runner-call-link" href="tel:9800000003" class="w-8 h-8 rounded-xl bg-white border border-slate-200 text-emerald-700 flex items-center justify-center shadow-xs active:scale-95 transition" title="Call Runner">
                    <i data-lucide="phone" class="w-3.5 h-3.5"></i>
                  </a>
                  <button onclick="openRunnerChatModal()" class="w-8 h-8 rounded-xl bg-emerald-600 text-white flex items-center justify-center shadow-xs active:scale-95 transition" title="Message Runner">
                    <i data-lucide="message-square" class="w-3.5 h-3.5"></i>
                  </button>
                  <button onclick="shareCustomerConfirmedLocationPin()" class="w-8 h-8 rounded-xl bg-teal-600 text-white flex items-center justify-center shadow-xs active:scale-95 transition" title="Share Exact Doorstep Pin">
                    <i data-lucide="map-pin" class="w-3.5 h-3.5"></i>
                  </button>
                </div>
              </div>

              <!-- STRICT BINARY 3-MINUTE CANCELLATION WINDOW -->
              <div id="cancel-order-container" class="pt-1">
                <div class="p-2.5 bg-rose-50/80 rounded-2xl border border-rose-200 space-y-2">
                  <div class="flex items-center justify-between text-xs font-bold text-rose-900">
                    <span class="flex items-center space-x-1.5">
                      <i data-lucide="clock" class="w-3.5 h-3.5 text-rose-600 animate-spin"></i>
                      <span data-i18n="cancel_window_title">180s Zero-Fee Cancellation</span>
                    </span>
                    <span id="cancel-countdown-timer" class="font-mono text-rose-700 bg-white px-2 py-0.5 rounded-lg border border-rose-300">
                      03:00
                    </span>
                  </div>
                  <button onclick="cancelActiveOrderBinary()" id="cancel-order-btn" class="w-full py-2 px-3 bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-300 font-bold rounded-xl flex items-center justify-center space-x-1.5 transition active:scale-95 text-xs">
                    <i data-lucide="x-circle" class="w-3.5 h-3.5"></i>
                    <span data-i18n="cancel_order_btn">Cancel Order (Full Refund)</span>
                  </button>
                </div>
              </div>
            </div>

            <!-- Empty Active Order State Card (Shown when no active order exists) -->
            <div id="no-active-order-card" class="hidden bg-white p-5 rounded-3xl border border-slate-200 text-center space-y-2 shadow-2xs">
              <div class="w-12 h-12 rounded-full bg-emerald-50 text-emerald-600 flex items-center justify-center mx-auto text-xl">
                🛒
              </div>
              <h4 class="text-xs font-bold text-slate-800" data-i18n="no_active_orders_title">No Active Delivery Mission</h4>
              <p class="text-[11px] text-slate-500" data-i18n="no_active_orders_sub">Place an order to track live delivery, ETA, and runner location.</p>
              <button onclick="switchTab('home')" class="px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs rounded-xl transition active:scale-95 shadow-xs" data-i18n="browse_stores_btn">
                Browse Village Stores
              </button>
            </div>
          </div>

          <!-- SECTION B: PAST ORDERS (Phase 1.2 & Phase 7) -->
          <div id="section-past-orders" class="space-y-3 pt-2">
            <!-- COMPACT ENTRY: MY MONTHLY RATION LIST -->
            <div class="bg-gradient-to-r from-emerald-50 to-teal-50 p-3.5 rounded-2xl border border-emerald-200 shadow-2xs flex items-center justify-between">
              <div class="flex items-center space-x-3">
                <div class="w-10 h-10 rounded-xl bg-emerald-600 text-white flex items-center justify-center text-lg shadow-xs shrink-0">
                  🌾
                </div>
                <div>
                  <div class="flex items-center space-x-1.5">
                    <h4 class="text-xs font-extrabold text-emerald-950" data-i18n="monthly_ration_title">My Monthly Ration List</h4>
                    <span class="text-[9px] font-bold bg-emerald-600 text-white px-1.5 py-0.2 rounded-full">Village Essentials</span>
                  </div>
                  <p class="text-[10px] text-emerald-700 mt-0.5" data-i18n="monthly_ration_sub">Atta, Rice, Dal, Oil & Sugar in 1 tap</p>
                </div>
              </div>
              <button onclick="openMonthlyRationModal()" class="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white text-[11px] font-bold rounded-xl shadow-xs transition active:scale-95 shrink-0 flex items-center space-x-1">
                <span data-i18n="manage_ration_btn">Manage & Order</span>
                <i data-lucide="chevron-right" class="w-3.5 h-3.5"></i>
              </button>
            </div>

            <!-- Past Orders Title & Counter -->
            <div class="flex items-center justify-between">
              <h3 class="text-xs font-bold text-slate-900 uppercase tracking-wide text-[11px]" data-i18n="past_orders_title">Past Orders</h3>
              <span id="past-orders-count-badge" class="text-[10px] font-mono text-slate-500">History</span>
            </div>

            <!-- Dynamic Past Orders Container -->
            <div id="past-orders-list-container" class="space-y-2.5">
              <!-- Dynamically rendered via renderPastOrdersList() -->
            </div>
          </div>
        </div>
      </section>"""

content = re.sub(old_orders_regex, new_orders_html, content, count=1)
print("Updated view-orders section in HTML")

# 3. Add Monthly Ration Modal and Location Map Picker Modal before closing container
modals_html = """
    <!-- 14. MY MONTHLY RATION LIST MODAL (Phase 7) -->
    <div id="modal-monthly-ration" class="hidden fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
      <div class="w-full max-w-sm bg-white rounded-3xl p-4 shadow-2xl flex flex-col max-h-[90vh] border border-slate-200">
        <!-- Header -->
        <div class="flex items-center justify-between pb-3 border-b border-slate-100">
          <div class="flex items-center space-x-2.5">
            <button onclick="closeModal('modal-monthly-ration')" class="w-7 h-7 rounded-full bg-slate-100 text-slate-600 flex items-center justify-center">
              <i data-lucide="arrow-left" class="w-3.5 h-3.5"></i>
            </button>
            <div>
              <h3 class="text-xs font-extrabold text-slate-900 flex items-center space-x-1.5">
                <span>🌾</span>
                <span data-i18n="ration_modal_title">My Monthly Ration List</span>
              </h3>
              <p class="text-[10px] text-emerald-700 font-semibold" data-i18n="ration_modal_sub">Village Grocery Essentials</p>
            </div>
          </div>
          <button onclick="addNewRationItemPrompt()" class="px-2 py-1 bg-emerald-50 hover:bg-emerald-100 text-emerald-800 text-[10px] font-bold rounded-lg border border-emerald-300 active:scale-95 transition flex items-center space-x-1">
            <i data-lucide="plus" class="w-3 h-3"></i>
            <span>Add Item</span>
          </button>
        </div>

        <!-- Ration Items List -->
        <div id="monthly-ration-items-container" class="flex-1 overflow-y-auto py-2.5 space-y-2 text-xs">
          <!-- Dynamically populated via renderMonthlyRationItems() -->
        </div>

        <!-- Pricing & Stock Summary Card -->
        <div id="ration-validation-summary" class="p-2.5 bg-slate-50 rounded-2xl border border-slate-200 text-xs space-y-1">
          <div class="flex items-center justify-between">
            <span class="text-[11px] text-slate-600 font-medium">Estimated Total (Live Store):</span>
            <span id="ration-total-amount" class="text-xs font-extrabold text-slate-900">₹0.00</span>
          </div>
          <p id="ration-store-name" class="text-[10px] text-slate-500">Checking nearest store stock...</p>
        </div>

        <!-- Footer Actions -->
        <div class="pt-3 border-t border-slate-100 grid grid-cols-2 gap-2">
          <button onclick="saveCurrentMonthlyRationList()" class="py-2.5 px-3 bg-slate-100 hover:bg-slate-200 text-slate-800 font-bold rounded-xl text-xs transition active:scale-95">
            Save List
          </button>
          <button onclick="addMonthlyRationListToCart()" id="btn-add-ration-to-cart" class="py-2.5 px-3 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-xl text-xs transition active:scale-95 shadow-xs flex items-center justify-center space-x-1.5">
            <i data-lucide="shopping-cart" class="w-3.5 h-3.5"></i>
            <span>Add to Cart</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 15. INTERACTIVE LOCATION MAP PICKER MODAL (Phase 3 & 4) -->
    <div id="modal-location-map-picker" class="hidden fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
      <div class="w-full max-w-sm bg-white rounded-3xl p-4 shadow-2xl flex flex-col max-h-[92vh] border border-slate-200">
        <!-- Header -->
        <div class="flex items-center justify-between pb-2.5 border-b border-slate-100">
          <div class="flex items-center space-x-2">
            <button onclick="closeModal('modal-location-map-picker')" class="w-7 h-7 rounded-full bg-slate-100 text-slate-600 flex items-center justify-center">
              <i data-lucide="arrow-left" class="w-3.5 h-3.5"></i>
            </button>
            <div>
              <h3 class="text-xs font-bold text-slate-900">Pick Exact Doorstep Pin</h3>
              <p class="text-[10px] text-slate-500">Drag map pin to your house</p>
            </div>
          </div>
          <button onclick="detectGPSInMapPicker()" class="px-2 py-1 bg-emerald-50 text-emerald-800 font-bold text-[10px] rounded-lg border border-emerald-200 flex items-center space-x-1">
            <i data-lucide="crosshair" class="w-3 h-3 text-emerald-600"></i>
            <span>My GPS</span>
          </button>
        </div>

        <!-- Leaflet Map Container -->
        <div id="picker-leaflet-map" class="w-full h-56 rounded-2xl border border-slate-200 my-2 relative z-0"></div>

        <!-- Coordinates & Estimated Village -->
        <div class="p-2.5 bg-slate-50 rounded-2xl border border-slate-200 text-xs space-y-1">
          <div class="flex items-center justify-between">
            <span class="text-[10px] font-bold text-slate-400 uppercase">Selected Coordinates</span>
            <span id="picker-coords-text" class="text-[11px] font-mono font-bold text-slate-800">26.2315, 85.3610</span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-[10px] font-bold text-slate-400 uppercase">Nearest Village</span>
            <span id="picker-village-hint" class="text-xs font-bold text-emerald-800">Minapur (Pilot Hub)</span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-[10px] font-bold text-slate-400 uppercase">8km Geofence</span>
            <span id="picker-serviceable-badge" class="text-[10px] font-bold text-emerald-700 bg-emerald-100 px-1.5 py-0.2 rounded">Serviceable</span>
          </div>
        </div>

        <!-- Action Button -->
        <button onclick="confirmMapPickedLocation()" class="mt-3 w-full py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-xl text-xs shadow-xs transition active:scale-95 flex items-center justify-center space-x-1.5">
          <i data-lucide="check" class="w-3.5 h-3.5"></i>
          <span>Confirm This Pin for Delivery</span>
        </button>
      </div>
    </div>
"""

if 'id="modal-monthly-ration"' not in content:
    content = content.replace('<!-- =================================================================== -->\n    <!-- MODALS & POPUPS -->', '<!-- =================================================================== -->\n    <!-- MODALS & POPUPS -->' + modals_html)
    print("Added Monthly Ration and Map Picker modals to HTML")

with open('public_web/customer/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Part 1 & 2 completed.")
