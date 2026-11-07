import re

with open('public_web/customer/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add <script src="config.js"></script> to <head>
if 'src="config.js"' not in html:
    html = html.replace(
        '<script src="https://maps.googleapis.com/maps/api/js',
        '<script src="config.js"></script>\n  <script src="https://maps.googleapis.com/maps/api/js'
    )
    print("1. Added <script src=\"config.js\"></script> to <head>")
else:
    print("1. config.js script already present in <head>")

# 2. Delete aggressive Home Screen red distance banner
old_home_banner = re.compile(
    r'\s*<!-- DYNAMIC SERVICEABILITY BANNER.*?<div id="service-unreachable-banner".*?</div>\s*</div>',
    re.DOTALL
)
if old_home_banner.search(html):
    html = old_home_banner.sub('', html, count=1)
    print("2. Deleted aggressive Home Screen service-unreachable-banner")
else:
    print("2. Warning: Home Screen service-unreachable-banner pattern not matched")

# 3. Clean Cart / Checkout banner (No raw distances)
old_cart_banner_pat = re.compile(
    r'<div id="cart-service-unreachable-banner".*?id="cart-service-unreachable-msg".*?</div>\s*</div>',
    re.DOTALL
)
new_cart_banner = '''<div id="cart-service-unreachable-banner" class="hidden p-3 bg-amber-50 border border-amber-200 rounded-2xl flex items-center space-x-2.5 text-amber-900 shadow-2xs mb-3">
            <div class="w-7 h-7 rounded-full bg-amber-100 text-amber-700 flex items-center justify-center shrink-0">
              <i data-lucide="map-pin-off" class="w-3.5 h-3.5"></i>
            </div>
            <div class="min-w-0 flex-1">
              <p class="text-xs font-semibold text-amber-900" id="cart-service-unreachable-msg">Service is currently unavailable in this location.</p>
            </div>
          </div>'''
if old_cart_banner_pat.search(html):
    html = old_cart_banner_pat.sub(new_cart_banner, html, count=1)
    print("3. Cleaned Cart checkout service-unreachable banner")
else:
    print("3. Warning: Cart banner pattern not matched")

# 4. Make Village / Locality input explicitly editable with hint
old_village_input = '<input type="text" id="modal-village-input" placeholder="e.g. Rampur Tola" class="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-lg text-xs focus:border-emerald-600 focus:outline-none">'
new_village_input = '''<input type="text" id="modal-village-input" oninput="handleVillageInputChange(this.value)" placeholder="e.g. Chaturshi, Rampur Tola" class="w-full px-3 py-2 bg-white border border-slate-300 rounded-lg text-xs text-slate-900 focus:border-emerald-600 focus:ring-1 focus:ring-emerald-500 focus:outline-none cursor-text select-text" autocomplete="off">
            <p class="text-[9px] text-slate-400 mt-0.5">Editable: If GPS detects block name (e.g. Musahri), tap here to type your exact village.</p>'''
if old_village_input in html:
    html = html.replace(old_village_input, new_village_input)
    print("4. Updated modal-village-input with editable classes, oninput handler, and helper hint")
else:
    print("4. Warning: old_village_input not matched")

# 5. Update checkServiceability JS logic to read MAX_DELIVERY_RADIUS_KM from APP_CONFIG & remove distance text
old_serviceability_pat = re.compile(
    r'function checkServiceability\(lat, lng\) \{.*?return isServiceable;\s*\}',
    re.DOTALL
)

new_serviceability = '''function checkServiceability(lat, lng) {
      const maxRadiusKm = (window.APP_CONFIG && typeof window.APP_CONFIG.MAX_DELIVERY_RADIUS_KM === 'number') 
        ? window.APP_CONFIG.MAX_DELIVERY_RADIUS_KM 
        : 8.0;
      const HUB_LAT = (window.APP_CONFIG && window.APP_CONFIG.HUB_LATITUDE) || 26.2315;
      const HUB_LNG = (window.APP_CONFIG && window.APP_CONFIG.HUB_LONGITUDE) || 85.3610;

      const userLat = (typeof lat === 'number') ? lat : (activeCustomerAddress && activeCustomerAddress.latitude ? activeCustomerAddress.latitude : HUB_LAT);
      const userLng = (typeof lng === 'number') ? lng : (activeCustomerAddress && activeCustomerAddress.longitude ? activeCustomerAddress.longitude : HUB_LNG);
      const distKm = calculateHaversineDistanceKm(HUB_LAT, HUB_LNG, userLat, userLng);
      const isServiceable = (distKm <= maxRadiusKm);
      window.isLocationServiceable = isServiceable;
      window.activeDeliveryDistanceKm = distKm;

      // Executive Directive: Completely omit/hide any aggressive Home Screen banners
      const homeBanner = document.getElementById('service-unreachable-banner');
      if (homeBanner) {
        homeBanner.classList.add('hidden');
      }

      const cartBanner = document.getElementById('cart-service-unreachable-banner');
      const btnPlace = document.getElementById('btn-place-order');

      if (isServiceable) {
        if (cartBanner) cartBanner.classList.add('hidden');
        if (btnPlace && cartItems && cartItems.length > 0) {
          btnPlace.disabled = false;
          btnPlace.classList.remove('opacity-50', 'pointer-events-none', 'cursor-not-allowed', 'bg-slate-400');
          btnPlace.classList.add('bg-emerald-600', 'hover:bg-emerald-700');
        }
      } else {
        if (cartBanner) {
          cartBanner.classList.remove('hidden');
          const cartMsg = document.getElementById('cart-service-unreachable-msg');
          if (cartMsg) cartMsg.innerText = currentLang === 'hi' 
            ? "इस स्थान पर वर्तमान में सेवा उपलब्ध नहीं है।" 
            : "Service is currently unavailable in this location.";
        }
        if (btnPlace) {
          btnPlace.disabled = true;
          btnPlace.classList.add('opacity-50', 'pointer-events-none', 'cursor-not-allowed');
          btnPlace.classList.remove('hover:bg-emerald-700');
        }
      }

      if (window.lucide) lucide.createIcons();
      return isServiceable;
    }'''

if old_serviceability_pat.search(html):
    html = old_serviceability_pat.sub(new_serviceability, html, count=1)
    print("5. Updated checkServiceability to use APP_CONFIG.MAX_DELIVERY_RADIUS_KM and silent blocking")
else:
    print("5. Warning: checkServiceability pattern not matched")

# 6. Add handleVillageInputChange helper
helper_fn = '''    function handleVillageInputChange(val) {
      const v = (val || '').trim();
      if (v) {
        activeCustomerAddress.village = v;
        localStorage.setItem('gb_customer_locality', v);
        const headerText = document.getElementById('header-location-text');
        if (headerText) headerText.innerText = v;
        const pickerFriendly = document.getElementById('picker-friendly-address-text');
        if (pickerFriendly) {
          pickerFriendly.innerText = `${v} • ${activeCustomerAddress.landmark || 'Near Shiv Mandir'}`;
        }
      }
    }
    window.handleVillageInputChange = handleVillageInputChange;

'''
if 'function handleVillageInputChange' not in html:
    html = html.replace('function checkServiceability', helper_fn + '    function checkServiceability')
    print("6. Added handleVillageInputChange function")

# 7. Update toast in placeCustomerOrder
old_place_toast = 'toastError(currentLang === \'hi\' ? "डिलीवरी आपके क्षेत्र में उपलब्ध नहीं है। कृपया नजदीकी पता चुनें।" : "Delivery Not Available in Your Area. Please select a delivery location within range.");'
new_place_toast = 'toastError(currentLang === \'hi\' ? "इस स्थान पर वर्तमान में सेवा उपलब्ध नहीं है।" : "Service is currently unavailable in this location.");'
if old_place_toast in html:
    html = html.replace(old_place_toast, new_place_toast)
    print("7. Updated placeCustomerOrder toast error message")

# 8. Ensure detectExactGPS unlocks the input field and uses Google Maps geocoding
old_detect_res = 'if (villageInput) villageInput.value = localityName;'
new_detect_res = '''if (villageInput) {
            villageInput.value = localityName;
            villageInput.disabled = false;
            villageInput.readOnly = false;
            villageInput.classList.remove('pointer-events-none', 'opacity-60', 'bg-slate-100');
            villageInput.classList.add('bg-white', 'cursor-text');
          }'''
if old_detect_res in html:
    html = html.replace(old_detect_res, new_detect_res)
    print("8. Ensured detectExactGPS unlocks villageInput with editable cursor")

with open('public_web/customer/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Saved public_web/customer/index.html successfully.")
