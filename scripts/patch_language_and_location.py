import re
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

# ==============================================================================
# 1. PATCH CUSTOMER APP
# ==============================================================================
print("1. Patching public_web/customer/index.html...")
with open("public_web/customer/index.html", "r", encoding="utf-8") as f:
    customer_html = f.read()

# Replace language cards in Customer with controlled cards and checkmark indicators
old_customer_cards = """        <!-- Language Choice Cards -->
        <div class="space-y-3 pt-2">
          <!-- English -->
          <button onclick="selectLanguage('en')" id="lang-btn-en" class="w-full p-4 rounded-2xl border-2 border-emerald-600 bg-emerald-50/50 flex items-center justify-between transition-all duration-200">
            <div class="flex items-center space-x-3.5">
              <span class="text-2xl">🇬🇧</span>
              <div class="text-left">
                <p class="text-sm font-bold text-slate-900">English</p>
                <p class="text-[11px] text-slate-500">Default International</p>
              </div>
            </div>
            <div class="w-6 h-6 rounded-full bg-emerald-600 text-white flex items-center justify-center text-xs font-bold check-icon">
              <i data-lucide="check" class="w-3.5 h-3.5"></i>
            </div>
          </button>

          <!-- Hindi -->
          <button onclick="selectLanguage('hi')" id="lang-btn-hi" class="w-full p-4 rounded-2xl border-2 border-slate-200 bg-white hover:border-slate-300 flex items-center justify-between transition-all duration-200">
            <div class="flex items-center space-x-3.5">
              <span class="text-2xl">🇮🇳</span>
              <div class="text-left">
                <p class="text-sm font-bold text-slate-900">हिंदी (Hindi)</p>
                <p class="text-[11px] text-slate-500">शुद्ध ग्रामीण भाषा</p>
              </div>
            </div>
            <div class="w-6 h-6 rounded-full bg-transparent text-transparent flex items-center justify-center text-xs font-bold check-icon">
              <i data-lucide="check" class="w-3.5 h-3.5"></i>
            </div>
          </button>
        </div>"""

new_customer_cards = """        <!-- Language Choice Cards (Fully Controlled State) -->
        <div class="space-y-3 pt-2">
          <!-- English -->
          <button type="button" onclick="selectLanguage('en')" id="lang-btn-en" class="w-full p-4 rounded-2xl border-2 border-emerald-600 bg-emerald-50/50 flex items-center justify-between transition-all duration-200 shadow-sm active:scale-98">
            <div class="flex items-center space-x-3.5">
              <span class="text-2xl">🇬🇧</span>
              <div class="text-left">
                <p class="text-sm font-bold text-slate-900">English</p>
                <p class="text-[11px] text-slate-500">Default International</p>
              </div>
            </div>
            <div id="check-icon-en" class="w-6 h-6 rounded-full bg-emerald-600 text-white flex items-center justify-center text-xs font-bold shadow-xs">
              <i data-lucide="check" class="w-3.5 h-3.5"></i>
            </div>
          </button>

          <!-- Hindi -->
          <button type="button" onclick="selectLanguage('hi')" id="lang-btn-hi" class="w-full p-4 rounded-2xl border-2 border-slate-200 bg-white hover:border-slate-300 flex items-center justify-between transition-all duration-200 shadow-xs active:scale-98">
            <div class="flex items-center space-x-3.5">
              <span class="text-2xl">🇮🇳</span>
              <div class="text-left">
                <p class="text-sm font-bold text-slate-900">हिंदी (Hindi)</p>
                <p class="text-[11px] text-slate-500">शुद्ध ग्रामीण भाषा</p>
              </div>
            </div>
            <div id="check-icon-hi" class="w-6 h-6 rounded-full border-2 border-slate-300 bg-white flex items-center justify-center text-xs font-bold">
            </div>
          </button>
        </div>"""

if old_customer_cards in customer_html:
    customer_html = customer_html.replace(old_customer_cards, new_customer_cards)
    print("Customer language cards HTML updated.")
else:
    print("WARNING: Customer cards exact match not found; attempting regex replace...")
    customer_html = re.sub(
        r'<!-- Language Choice Cards -->.*?</div>\s*</div>\s*</div>\s*<div class="pb-6">',
        new_customer_cards + '\n      </div>\n\n      <div class="pb-6">',
        customer_html,
        flags=re.DOTALL
    )

# Now update selectLanguage in Customer JS
old_customer_select = """    function selectLanguage(lang) {
      currentLang = lang;
      setAppLanguage(lang);
    }"""

new_customer_select = """    function updateCustomerLangCards(lang) {
      const btnEn = document.getElementById('lang-btn-en');
      const btnHi = document.getElementById('lang-btn-hi');
      const checkEn = document.getElementById('check-icon-en');
      const checkHi = document.getElementById('check-icon-hi');

      if (lang === 'hi') {
        if (btnHi) {
          btnHi.className = "w-full p-4 rounded-2xl border-2 border-emerald-600 bg-emerald-50/50 flex items-center justify-between transition-all duration-200 shadow-sm active:scale-98";
        }
        if (checkHi) {
          checkHi.className = "w-6 h-6 rounded-full bg-emerald-600 text-white flex items-center justify-center text-xs font-bold shadow-xs";
          checkHi.innerHTML = '<i data-lucide="check" class="w-3.5 h-3.5"></i>';
        }
        if (btnEn) {
          btnEn.className = "w-full p-4 rounded-2xl border-2 border-slate-200 bg-white hover:border-slate-300 flex items-center justify-between transition-all duration-200 shadow-xs active:scale-98";
        }
        if (checkEn) {
          checkEn.className = "w-6 h-6 rounded-full border-2 border-slate-300 bg-white flex items-center justify-center text-xs font-bold";
          checkEn.innerHTML = '';
        }
      } else {
        if (btnEn) {
          btnEn.className = "w-full p-4 rounded-2xl border-2 border-emerald-600 bg-emerald-50/50 flex items-center justify-between transition-all duration-200 shadow-sm active:scale-98";
        }
        if (checkEn) {
          checkEn.className = "w-6 h-6 rounded-full bg-emerald-600 text-white flex items-center justify-center text-xs font-bold shadow-xs";
          checkEn.innerHTML = '<i data-lucide="check" class="w-3.5 h-3.5"></i>';
        }
        if (btnHi) {
          btnHi.className = "w-full p-4 rounded-2xl border-2 border-slate-200 bg-white hover:border-slate-300 flex items-center justify-between transition-all duration-200 shadow-xs active:scale-98";
        }
        if (checkHi) {
          checkHi.className = "w-6 h-6 rounded-full border-2 border-slate-300 bg-white flex items-center justify-center text-xs font-bold";
          checkHi.innerHTML = '';
        }
      }
      if (window.lucide) lucide.createIcons();
    }

    function selectLanguage(lang) {
      currentLang = lang;
      localStorage.setItem('gb_customer_lang', lang);
      updateCustomerLangCards(lang);
      setAppLanguage(lang);
    }"""

if old_customer_select in customer_html:
    customer_html = customer_html.replace(old_customer_select, new_customer_select)
    print("Customer selectLanguage function updated.")
else:
    print("WARNING: Customer selectLanguage exact match not found; attempting regex replace...")
    customer_html = re.sub(
        r'function selectLanguage\(lang\)\s*\{[^}]*\}',
        new_customer_select,
        customer_html
    )

with open("public_web/customer/index.html", "w", encoding="utf-8") as f:
    f.write(customer_html)
print("Customer index.html successfully saved.")


# ==============================================================================
# 2. PATCH VENDOR APP
# ==============================================================================
print("\n2. Patching public_web/vendor/index.html...")
with open("public_web/vendor/index.html", "r", encoding="utf-8") as f:
    vendor_html = f.read()

# 2.A: Fix Language Selection Cards in Vendor
old_vendor_cards = """          <div class="space-y-4 max-w-xs mx-auto">
            <button onclick="setLanguage('en')" id="lang-btn-en" class="w-full p-4 rounded-xl border-2 border-emerald-600 bg-emerald-50/50 flex items-center justify-between font-semibold text-slate-900 shadow-sm transition active:scale-98">
              <div class="flex items-center space-x-3">
                <span class="text-xl">🇬🇧</span>
                <span class="text-base font-bold">English</span>
              </div>
              <i data-lucide="check-circle-2" class="w-5 h-5 text-emerald-600"></i>
            </button>

            <button onclick="setLanguage('hi')" id="lang-btn-hi" class="w-full p-4 rounded-xl border-2 border-slate-200 bg-white flex items-center justify-between font-semibold text-slate-900 shadow-sm transition active:scale-98">
              <div class="flex items-center space-x-3">
                <span class="text-xl">🇮🇳</span>
                <span class="text-base font-bold">हिन्दी (Hindi)</span>
              </div>
              <i data-lucide="circle" class="w-5 h-5 text-slate-300"></i>
            </button>
          </div>"""

new_vendor_cards = """          <div class="space-y-4 max-w-xs mx-auto">
            <button type="button" onclick="setLanguage('en')" id="lang-btn-en" class="w-full p-4 rounded-xl border-2 border-emerald-600 bg-emerald-50/50 flex items-center justify-between font-semibold text-slate-900 shadow-sm transition active:scale-98">
              <div class="flex items-center space-x-3">
                <span class="text-xl">🇬🇧</span>
                <span class="text-base font-bold">English</span>
              </div>
              <div id="check-icon-en" class="w-6 h-6 rounded-full bg-emerald-600 text-white flex items-center justify-center text-xs font-bold shadow-xs">
                <i data-lucide="check" class="w-3.5 h-3.5"></i>
              </div>
            </button>

            <button type="button" onclick="setLanguage('hi')" id="lang-btn-hi" class="w-full p-4 rounded-xl border-2 border-slate-200 bg-white flex items-center justify-between font-semibold text-slate-900 shadow-sm transition active:scale-98">
              <div class="flex items-center space-x-3">
                <span class="text-xl">🇮🇳</span>
                <span class="text-base font-bold">हिन्दी (Hindi)</span>
              </div>
              <div id="check-icon-hi" class="w-6 h-6 rounded-full border-2 border-slate-300 bg-white flex items-center justify-center text-xs font-bold">
              </div>
            </button>
          </div>"""

if old_vendor_cards in vendor_html:
    vendor_html = vendor_html.replace(old_vendor_cards, new_vendor_cards)
    print("Vendor language cards HTML updated.")
else:
    print("WARNING: Vendor language cards exact match not found; attempting regex replace...")
    vendor_html = re.sub(
        r'<div class="space-y-4 max-w-xs mx-auto">.*?<button onclick="setLanguage\(\'en\'\).*?</button>\s*<button onclick="setLanguage\(\'hi\'\).*?</button>\s*</div>',
        new_vendor_cards,
        vendor_html,
        flags=re.DOTALL
    )

# 2.B: Redesign Location Setup Screen (Step 4) in Vendor - Eradicate Map & GPS, Add Searchable Autocomplete Dropdown
old_vendor_location_screen = re.search(
    r'<div id="screen-onboarding-4".*?<!-- PAGE 5:',
    vendor_html,
    re.DOTALL
)

new_vendor_location_screen = """<div id="screen-onboarding-4" class="app-screen flex-1 p-6 flex flex-col justify-between hidden">
        <div class="space-y-4">
          <!-- Header -->
          <div>
            <div class="flex items-center space-x-2 text-emerald-600 text-xs font-bold uppercase tracking-wider mb-2"><span class="px-2 py-0.5 bg-emerald-100 rounded">Step 4 of 7</span><span>Store Location</span></div>
            <h2 class="text-2xl font-bold text-slate-900 mb-1" data-i18n="vendor_location_title">Shop Location Setup</h2>
            <p class="text-xs text-slate-500 leading-relaxed" data-i18n="vendor_location_sub">
              Select your base village or area from the dropdown to receive local orders.
            </p>
          </div>

          <!-- Shop Location Form Card (Clean Vertically Stacked with Searchable Dropdown) -->
          <div class="p-4 rounded-2xl border border-slate-200 bg-white space-y-4 shadow-xs">
            <!-- 1. Searchable Base Village / Area Dropdown -->
            <div class="relative" id="vendor-village-container">
              <label class="block text-xs font-semibold text-slate-700 mb-1" data-i18n="village_label">
                Base Village / Area Name <span class="text-rose-500">*</span>
              </label>
              <div class="relative flex items-center">
                <i data-lucide="map-pin" class="absolute left-3.5 w-4 h-4 text-emerald-600 pointer-events-none"></i>
                <input 
                  type="text" 
                  id="vendor-village-name" 
                  autocomplete="off"
                  placeholder="Type or select village (e.g. Muzaffarpur, Chaturshi)..." 
                  value="Muzaffarpur" 
                  oninput="handleVendorVillageSearch(this.value)" 
                  onfocus="handleVendorVillageSearch(this.value)" 
                  class="w-full pl-10 pr-9 py-3.5 rounded-xl border border-slate-300 bg-white text-slate-900 font-bold text-xs focus:border-emerald-600 focus:ring-2 focus:ring-emerald-100 focus:outline-none shadow-xs transition"
                >
                <button type="button" onclick="toggleVendorVillageDropdown()" class="absolute right-3 text-slate-400 hover:text-slate-600 focus:outline-none">
                  <i data-lucide="chevron-down" class="w-4 h-4"></i>
                </button>
              </div>
              <!-- Autocomplete Dropdown List -->
              <div id="vendor-village-dropdown" class="hidden absolute left-0 right-0 top-full mt-1.5 bg-white border border-slate-200 rounded-xl shadow-xl max-h-56 overflow-y-auto z-50 divide-y divide-slate-100">
                <!-- Rendered dynamically via JS -->
              </div>
              <p class="text-[10px] text-slate-400 mt-1" data-i18n="vendor_hub_hint">Orders from customers in this rural cluster will route to your shop</p>
            </div>

            <!-- 2. Pincode -->
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1" data-i18n="pincode_label">
                Postal Pincode <span class="text-rose-500">*</span>
              </label>
              <div class="relative flex items-center">
                <i data-lucide="hash" class="absolute left-3.5 w-4 h-4 text-slate-400 pointer-events-none"></i>
                <input type="tel" id="vendor-pincode" maxlength="6" placeholder="e.g. 842001" value="842001" class="w-full pl-10 pr-4 py-3.5 rounded-xl border border-slate-300 bg-white text-slate-900 font-mono font-bold text-xs focus:border-emerald-600 focus:ring-2 focus:ring-emerald-100 focus:outline-none shadow-xs">
              </div>
            </div>

            <!-- 3. Shop Address / Landmark -->
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1" data-i18n="shop_address_label">
                Shop Address / Landmark <span class="text-rose-500">*</span>
              </label>
              <div class="relative flex items-center">
                <i data-lucide="home" class="absolute left-3.5 w-4 h-4 text-slate-400 pointer-events-none"></i>
                <input type="text" id="vendor-shop-address" placeholder="e.g. Near Shiv Mandir, Main Market" value="Near Shiv Mandir, Main Road" class="w-full pl-10 pr-4 py-3.5 rounded-xl border border-slate-300 bg-white text-slate-900 font-bold text-xs focus:border-emerald-600 focus:ring-2 focus:ring-emerald-100 focus:outline-none shadow-xs">
              </div>
            </div>
          </div>
        </div>

        <div class="pt-4 space-y-2">
          <button onclick="saveVendorLocationAndProceed()" id="btn-save-vendor-location" class="w-full py-3.5 px-4 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-bold text-xs shadow-md active:scale-98 transition flex items-center justify-center space-x-2">
            <span data-i18n="save_location_btn">Save & Continue to KYC</span>
            <i data-lucide="arrow-right" class="w-4 h-4"></i>
          </button>
          <p class="text-[11px] text-center text-slate-400" data-i18n="vendor_area_note">Cluster-based ordering ensures delivery runners can reach your storefront within minutes</p>
        </div>
      </div>

      <!-- PAGE 5:"""

if old_vendor_location_screen:
    vendor_html = vendor_html[:old_vendor_location_screen.start()] + new_vendor_location_screen + vendor_html[old_vendor_location_screen.end():]
    print("Vendor Step 4 Location Screen redesigned with Searchable Dropdown.")
else:
    print("ERROR: Could not locate vendor screen-onboarding-4 block!")

# 2.C: Remove Leaflet CDN scripts from vendor head
vendor_html = re.sub(
    r'\s*<!-- Leaflet Map CSS & JS -->\s*<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"[^>]*>\s*<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"[^>]*></script>',
    '',
    vendor_html
)

# 2.D: Update JS in Vendor: controlled language state + searchable village dropdown + eradicate leaflet/map/gps
old_vendor_js_lang = re.search(
    r'function setLanguage\(lang\)\s*\{.*?// Update text using data-i18n attributes',
    vendor_html,
    re.DOTALL
)

new_vendor_js_lang = """function updateVendorLangCards(lang) {
      const btnEn = document.getElementById('lang-btn-en');
      const btnHi = document.getElementById('lang-btn-hi');
      const checkEn = document.getElementById('check-icon-en');
      const checkHi = document.getElementById('check-icon-hi');

      if (lang === 'hi') {
        if (btnHi) {
          btnHi.className = "w-full p-4 rounded-xl border-2 border-emerald-600 bg-emerald-50/50 flex items-center justify-between font-semibold text-slate-900 shadow-sm transition active:scale-98";
        }
        if (checkHi) {
          checkHi.className = "w-6 h-6 rounded-full bg-emerald-600 text-white flex items-center justify-center text-xs font-bold shadow-xs";
          checkHi.innerHTML = '<i data-lucide="check" class="w-3.5 h-3.5"></i>';
        }
        if (btnEn) {
          btnEn.className = "w-full p-4 rounded-xl border-2 border-slate-200 bg-white flex items-center justify-between font-semibold text-slate-900 shadow-sm transition active:scale-98";
        }
        if (checkEn) {
          checkEn.className = "w-6 h-6 rounded-full border-2 border-slate-300 bg-white flex items-center justify-center text-xs font-bold";
          checkEn.innerHTML = '';
        }
      } else {
        if (btnEn) {
          btnEn.className = "w-full p-4 rounded-xl border-2 border-emerald-600 bg-emerald-50/50 flex items-center justify-between font-semibold text-slate-900 shadow-sm transition active:scale-98";
        }
        if (checkEn) {
          checkEn.className = "w-6 h-6 rounded-full bg-emerald-600 text-white flex items-center justify-center text-xs font-bold shadow-xs";
          checkEn.innerHTML = '<i data-lucide="check" class="w-3.5 h-3.5"></i>';
        }
        if (btnHi) {
          btnHi.className = "w-full p-4 rounded-xl border-2 border-slate-200 bg-white flex items-center justify-between font-semibold text-slate-900 shadow-sm transition active:scale-98";
        }
        if (checkHi) {
          checkHi.className = "w-6 h-6 rounded-full border-2 border-slate-300 bg-white flex items-center justify-center text-xs font-bold";
          checkHi.innerHTML = '';
        }
      }
      if (window.lucide) lucide.createIcons();
    }

    function setLanguage(lang) {
      currentLang = lang;
      localStorage.setItem('gaonbazaar_vendor_lang', lang);
      updateVendorLangCards(lang);

      // Update text using data-i18n attributes"""

if old_vendor_js_lang:
    vendor_html = vendor_html[:old_vendor_js_lang.start()] + new_vendor_js_lang + vendor_html[old_vendor_js_lang.end():]
    print("Vendor setLanguage JS updated with controlled card state.")

# Replace initVendorMap & detectVendorGPS with Searchable Dropdown logic
vendor_map_funcs_pattern = re.search(
    r'function initVendorMap\(\)\s*\{.*?async function saveVendorLocationAndProceed\(\)',
    vendor_html,
    re.DOTALL
)

new_vendor_dropdown_js = """// ---------------------------------------------------------------------------
    // RURAL VILLAGES / HUBS AUTOCOMPLETE (MUZAFFARPUR & SURROUNDING CLUSTERS)
    // ---------------------------------------------------------------------------
    const RURAL_AREAS_LIST = [
      "Muzaffarpur",
      "Chaturshi",
      "Musahri",
      "Kanti",
      "Bochahan",
      "Saraiya",
      "Motipur",
      "Sakra",
      "Kurhani",
      "Aurai",
      "Minapur",
      "Sahebganj",
      "Paroo",
      "Marwan",
      "Gaighat",
      "Kudra",
      "Mohania",
      "Bhabua",
      "Darbhanga",
      "Samastipur",
      "Hajipur",
      "Vaishali",
      "Sitamarhi",
      "Patna Rural"
    ];

    function handleVendorVillageSearch(query) {
      const dropdown = document.getElementById('vendor-village-dropdown');
      if (!dropdown) return;
      const q = (query || '').trim().toLowerCase();
      
      const filtered = RURAL_AREAS_LIST.filter(area => area.toLowerCase().includes(q));
      
      let html = '';
      if (filtered.length > 0) {
        filtered.forEach(area => {
          html += `
            <div onclick="selectVendorVillage('${area}')" class="px-3.5 py-2.5 hover:bg-emerald-50 cursor-pointer flex items-center justify-between text-xs font-semibold text-slate-800 transition">
              <div class="flex items-center space-x-2">
                <i data-lucide="map-pin" class="w-3.5 h-3.5 text-emerald-600 shrink-0"></i>
                <span>${area}</span>
              </div>
              <span class="text-[10px] text-emerald-700 bg-emerald-50 border border-emerald-200 px-1.5 py-0.5 rounded font-bold">Rural Hub</span>
            </div>
          `;
        });
      }

      if (q && !filtered.some(a => a.toLowerCase() === q)) {
        html += `
          <div onclick="selectVendorVillage('${query.replace(/'/g, "\\'")}')" class="px-3.5 py-2.5 hover:bg-emerald-50 cursor-pointer flex items-center space-x-2 text-xs font-bold text-emerald-700 bg-emerald-50/50">
            <i data-lucide="plus-circle" class="w-3.5 h-3.5 text-emerald-600 shrink-0"></i>
            <span>Use "${query}"</span>
          </div>
        `;
      }

      dropdown.innerHTML = html;
      dropdown.classList.remove('hidden');
      if (window.lucide) lucide.createIcons();
    }

    function toggleVendorVillageDropdown() {
      const dropdown = document.getElementById('vendor-village-dropdown');
      if (!dropdown) return;
      if (dropdown.classList.contains('hidden')) {
        const val = document.getElementById('vendor-village-name')?.value || '';
        handleVendorVillageSearch(val);
      } else {
        dropdown.classList.add('hidden');
      }
    }

    function selectVendorVillage(villageName) {
      const input = document.getElementById('vendor-village-name');
      if (input) input.value = villageName;
      const dropdown = document.getElementById('vendor-village-dropdown');
      if (dropdown) dropdown.classList.add('hidden');
    }

    document.addEventListener('click', (e) => {
      const container = document.getElementById('vendor-village-container');
      const dropdown = document.getElementById('vendor-village-dropdown');
      if (container && dropdown && !container.contains(e.target)) {
        dropdown.classList.add('hidden');
      }
    });

    async function saveVendorLocationAndProceed()"""

if vendor_map_funcs_pattern:
    vendor_html = vendor_html[:vendor_map_funcs_pattern.start()] + new_vendor_dropdown_js + vendor_html[vendor_map_funcs_pattern.end() - len('async function saveVendorLocationAndProceed()'):]
    print("Vendor map & GPS functions replaced with Searchable Village Dropdown logic.")
else:
    print("WARNING: Could not find vendor map functions pattern!")

with open("public_web/vendor/index.html", "w", encoding="utf-8") as f:
    f.write(vendor_html)
print("Vendor index.html successfully saved.")


# ==============================================================================
# 3. PATCH RUNNER APP
# ==============================================================================
print("\n3. Patching public_web/runner/index.html...")
with open("public_web/runner/index.html", "r", encoding="utf-8") as f:
    runner_html = f.read()

# 3.A: Fix Language Selection Cards in Runner
old_runner_cards = """          <div class="space-y-4 max-w-xs mx-auto">
            <button onclick="setLanguage('en')" id="lang-btn-en" class="w-full p-4 rounded-xl border-2 border-blue-600 bg-blue-50/50 flex items-center justify-between font-semibold text-slate-900 shadow-sm transition active:scale-98">
              <div class="flex items-center space-x-3">
                <span class="text-xl">🇬🇧</span>
                <span class="text-base font-bold">English</span>
              </div>
              <i data-lucide="check-circle-2" class="w-5 h-5 text-blue-600"></i>
            </button>

            <button onclick="setLanguage('hi')" id="lang-btn-hi" class="w-full p-4 rounded-xl border-2 border-slate-200 bg-white flex items-center justify-between font-semibold text-slate-900 shadow-sm transition active:scale-98">
              <div class="flex items-center space-x-3">
                <span class="text-xl">🇮🇳</span>
                <span class="text-base font-bold">हिन्दी (Hindi)</span>
              </div>
              <i data-lucide="circle" class="w-5 h-5 text-slate-300"></i>
            </button>
          </div>"""

new_runner_cards = """          <div class="space-y-4 max-w-xs mx-auto">
            <button type="button" onclick="setLanguage('en')" id="lang-btn-en" class="w-full p-4 rounded-xl border-2 border-emerald-600 bg-emerald-50/50 flex items-center justify-between font-semibold text-slate-900 shadow-sm transition active:scale-98">
              <div class="flex items-center space-x-3">
                <span class="text-xl">🇬🇧</span>
                <span class="text-base font-bold">English</span>
              </div>
              <div id="check-icon-en" class="w-6 h-6 rounded-full bg-emerald-600 text-white flex items-center justify-center text-xs font-bold shadow-xs">
                <i data-lucide="check" class="w-3.5 h-3.5"></i>
              </div>
            </button>

            <button type="button" onclick="setLanguage('hi')" id="lang-btn-hi" class="w-full p-4 rounded-xl border-2 border-slate-200 bg-white flex items-center justify-between font-semibold text-slate-900 shadow-sm transition active:scale-98">
              <div class="flex items-center space-x-3">
                <span class="text-xl">🇮🇳</span>
                <span class="text-base font-bold">हिन्दी (Hindi)</span>
              </div>
              <div id="check-icon-hi" class="w-6 h-6 rounded-full border-2 border-slate-300 bg-white flex items-center justify-center text-xs font-bold">
              </div>
            </button>
          </div>"""

if old_runner_cards in runner_html:
    runner_html = runner_html.replace(old_runner_cards, new_runner_cards)
    print("Runner language cards HTML updated.")
else:
    print("WARNING: Runner language cards exact match not found; attempting regex replace...")
    runner_html = re.sub(
        r'<div class="space-y-4 max-w-xs mx-auto">.*?<button onclick="setLanguage\(\'en\'\).*?</button>\s*<button onclick="setLanguage\(\'hi\'\).*?</button>\s*</div>',
        new_runner_cards,
        runner_html,
        flags=re.DOTALL
    )

# 3.B: Redesign Location Setup Screen (Step 4) in Runner - Eradicate Map, GPS & Radius Chips; Add Searchable Dropdown
old_runner_location_screen = re.search(
    r'<div id="screen-onboarding-4".*?<!-- PAGE 5:',
    runner_html,
    re.DOTALL
)

new_runner_location_screen = """<div id="screen-onboarding-4" class="app-screen flex-1 p-6 flex flex-col justify-between hidden">
        <div class="space-y-4">
          <!-- Header -->
          <div>
            <div class="flex items-center space-x-2 text-blue-600 text-xs font-bold uppercase tracking-wider mb-2"><span class="px-2 py-0.5 bg-blue-100 rounded">Step 4 of 7</span><span>Service Area</span></div>
            <h2 class="text-2xl font-bold text-slate-900 mb-1" data-i18n="runner_location_title">Service Area Setup</h2>
            <p class="text-xs text-slate-500 leading-relaxed" data-i18n="runner_location_sub">
              Select your base village or operating hub from the searchable dropdown
            </p>
          </div>

          <!-- Service Area Form Card (Clean Vertically Stacked with Searchable Dropdown) -->
          <div class="p-4 rounded-2xl border border-slate-200 bg-white space-y-4 shadow-xs">
            <!-- 1. Searchable Base Village / Area Dropdown -->
            <div class="relative" id="runner-village-container">
              <label class="block text-xs font-semibold text-slate-700 mb-1" data-i18n="base_village_label">
                Base Village / Area Name <span class="text-rose-500">*</span>
              </label>
              <div class="relative flex items-center">
                <i data-lucide="map-pin" class="absolute left-3.5 w-4 h-4 text-blue-600 pointer-events-none"></i>
                <input 
                  type="text" 
                  id="runner-base-village" 
                  autocomplete="off"
                  placeholder="Type or select village (e.g. Muzaffarpur, Chaturshi)..." 
                  value="Muzaffarpur" 
                  oninput="handleRunnerVillageSearch(this.value)" 
                  onfocus="handleRunnerVillageSearch(this.value)" 
                  class="w-full pl-10 pr-9 py-3.5 rounded-xl border border-slate-300 bg-white text-slate-900 font-bold text-xs focus:border-blue-600 focus:ring-2 focus:ring-blue-100 focus:outline-none shadow-xs transition"
                >
                <button type="button" onclick="toggleRunnerVillageDropdown()" class="absolute right-3 text-slate-400 hover:text-slate-600 focus:outline-none">
                  <i data-lucide="chevron-down" class="w-4 h-4"></i>
                </button>
              </div>
              <!-- Autocomplete Dropdown List -->
              <div id="runner-village-dropdown" class="hidden absolute left-0 right-0 top-full mt-1.5 bg-white border border-slate-200 rounded-xl shadow-xl max-h-56 overflow-y-auto z-50 divide-y divide-slate-100">
                <!-- Rendered dynamically via JS -->
              </div>
              <p class="text-[10px] text-slate-400 mt-1" data-i18n="base_village_hint">Orders will be assigned from local shops and farms around your hub</p>
            </div>

            <!-- 2. Operating Landmark / Hub Details -->
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1" data-i18n="hub_landmark_label">
                Operating Hub Landmark <span class="text-slate-400 font-normal">(Optional)</span>
              </label>
              <div class="relative flex items-center">
                <i data-lucide="landmark" class="absolute left-3.5 w-4 h-4 text-slate-400 pointer-events-none"></i>
                <input type="text" id="runner-landmark" placeholder="e.g. Near Market Chowk, Main Bus Stand" value="Near Market Chowk" class="w-full pl-10 pr-4 py-3.5 rounded-xl border border-slate-300 bg-white text-slate-900 font-bold text-xs focus:border-blue-600 focus:ring-2 focus:ring-blue-100 focus:outline-none shadow-xs">
              </div>
            </div>
          </div>
        </div>

        <div class="pt-4 space-y-2">
          <button onclick="saveRunnerLocationAndProceed()" id="btn-save-runner-location" class="w-full py-3.5 px-4 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-bold text-xs shadow-md active:scale-98 transition flex items-center justify-center space-x-2">
            <span data-i18n="save_location_btn">Save & Continue to KYC</span>
            <i data-lucide="arrow-right" class="w-4 h-4"></i>
          </button>
          <p class="text-[11px] text-center text-slate-400" data-i18n="rural_geofence_note">Base village cluster setup ensures timely deliveries within 15-30 minutes</p>
        </div>
      </div>

      <!-- PAGE 5:"""

if old_runner_location_screen:
    runner_html = runner_html[:old_runner_location_screen.start()] + new_runner_location_screen + runner_html[old_runner_location_screen.end():]
    print("Runner Step 4 Location Screen redesigned with Searchable Dropdown (Map, GPS, Radius deleted).")
else:
    print("ERROR: Could not locate runner screen-onboarding-4 block!")

# 3.C: Remove Leaflet CDN scripts from runner head
runner_html = re.sub(
    r'\s*<!-- Leaflet Map CSS & JS -->\s*<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"[^>]*>\s*<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"[^>]*></script>',
    '',
    runner_html
)

# 3.D: Update JS in Runner: controlled language state + searchable village dropdown + eradicate leaflet/map/gps/radius
old_runner_js_lang = re.search(
    r'function setLanguage\(lang\)\s*\{.*?// Update text using data-i18n attributes',
    runner_html,
    re.DOTALL
)

new_runner_js_lang = """function updateRunnerLangCards(lang) {
      const btnEn = document.getElementById('lang-btn-en');
      const btnHi = document.getElementById('lang-btn-hi');
      const checkEn = document.getElementById('check-icon-en');
      const checkHi = document.getElementById('check-icon-hi');

      if (lang === 'hi') {
        if (btnHi) {
          btnHi.className = "w-full p-4 rounded-xl border-2 border-emerald-600 bg-emerald-50/50 flex items-center justify-between font-semibold text-slate-900 shadow-sm transition active:scale-98";
        }
        if (checkHi) {
          checkHi.className = "w-6 h-6 rounded-full bg-emerald-600 text-white flex items-center justify-center text-xs font-bold shadow-xs";
          checkHi.innerHTML = '<i data-lucide="check" class="w-3.5 h-3.5"></i>';
        }
        if (btnEn) {
          btnEn.className = "w-full p-4 rounded-xl border-2 border-slate-200 bg-white flex items-center justify-between font-semibold text-slate-900 shadow-sm transition active:scale-98";
        }
        if (checkEn) {
          checkEn.className = "w-6 h-6 rounded-full border-2 border-slate-300 bg-white flex items-center justify-center text-xs font-bold";
          checkEn.innerHTML = '';
        }
      } else {
        if (btnEn) {
          btnEn.className = "w-full p-4 rounded-xl border-2 border-emerald-600 bg-emerald-50/50 flex items-center justify-between font-semibold text-slate-900 shadow-sm transition active:scale-98";
        }
        if (checkEn) {
          checkEn.className = "w-6 h-6 rounded-full bg-emerald-600 text-white flex items-center justify-center text-xs font-bold shadow-xs";
          checkEn.innerHTML = '<i data-lucide="check" class="w-3.5 h-3.5"></i>';
        }
        if (btnHi) {
          btnHi.className = "w-full p-4 rounded-xl border-2 border-slate-200 bg-white flex items-center justify-between font-semibold text-slate-900 shadow-sm transition active:scale-98";
        }
        if (checkHi) {
          checkHi.className = "w-6 h-6 rounded-full border-2 border-slate-300 bg-white flex items-center justify-center text-xs font-bold";
          checkHi.innerHTML = '';
        }
      }
      if (window.lucide) lucide.createIcons();
    }

    function setLanguage(lang) {
      currentLang = lang;
      localStorage.setItem('gaonbazaar_runner_lang', lang);
      updateRunnerLangCards(lang);

      // Update text using data-i18n attributes"""

if old_runner_js_lang:
    runner_html = runner_html[:old_runner_js_lang.start()] + new_runner_js_lang + runner_html[old_runner_js_lang.end():]
    print("Runner setLanguage JS updated with controlled card state.")

# Replace initRunnerMap, selectRadius, detectRunnerGPS with Searchable Dropdown logic
runner_map_funcs_pattern = re.search(
    r'function initRunnerMap\(\)\s*\{.*?async function saveRunnerLocationAndProceed\(\)',
    runner_html,
    re.DOTALL
)

new_runner_dropdown_js = """// ---------------------------------------------------------------------------
    // RURAL VILLAGES / HUBS AUTOCOMPLETE (MUZAFFARPUR & SURROUNDING CLUSTERS)
    // ---------------------------------------------------------------------------
    const RURAL_AREAS_LIST = [
      "Muzaffarpur",
      "Chaturshi",
      "Musahri",
      "Kanti",
      "Bochahan",
      "Saraiya",
      "Motipur",
      "Sakra",
      "Kurhani",
      "Aurai",
      "Minapur",
      "Sahebganj",
      "Paroo",
      "Marwan",
      "Gaighat",
      "Kudra",
      "Mohania",
      "Bhabua",
      "Darbhanga",
      "Samastipur",
      "Hajipur",
      "Vaishali",
      "Sitamarhi",
      "Patna Rural"
    ];

    function handleRunnerVillageSearch(query) {
      const dropdown = document.getElementById('runner-village-dropdown');
      if (!dropdown) return;
      const q = (query || '').trim().toLowerCase();
      
      const filtered = RURAL_AREAS_LIST.filter(area => area.toLowerCase().includes(q));
      
      let html = '';
      if (filtered.length > 0) {
        filtered.forEach(area => {
          html += `
            <div onclick="selectRunnerVillage('${area}')" class="px-3.5 py-2.5 hover:bg-blue-50 cursor-pointer flex items-center justify-between text-xs font-semibold text-slate-800 transition">
              <div class="flex items-center space-x-2">
                <i data-lucide="map-pin" class="w-3.5 h-3.5 text-blue-600 shrink-0"></i>
                <span>${area}</span>
              </div>
              <span class="text-[10px] text-blue-700 bg-blue-50 border border-blue-200 px-1.5 py-0.5 rounded font-bold">Operating Hub</span>
            </div>
          `;
        });
      }

      if (q && !filtered.some(a => a.toLowerCase() === q)) {
        html += `
          <div onclick="selectRunnerVillage('${query.replace(/'/g, "\\'")}')" class="px-3.5 py-2.5 hover:bg-blue-50 cursor-pointer flex items-center space-x-2 text-xs font-bold text-blue-700 bg-blue-50/50">
            <i data-lucide="plus-circle" class="w-3.5 h-3.5 text-blue-600 shrink-0"></i>
            <span>Use "${query}"</span>
          </div>
        `;
      }

      dropdown.innerHTML = html;
      dropdown.classList.remove('hidden');
      if (window.lucide) lucide.createIcons();
    }

    function toggleRunnerVillageDropdown() {
      const dropdown = document.getElementById('runner-village-dropdown');
      if (!dropdown) return;
      if (dropdown.classList.contains('hidden')) {
        const val = document.getElementById('runner-base-village')?.value || '';
        handleRunnerVillageSearch(val);
      } else {
        dropdown.classList.add('hidden');
      }
    }

    function selectRunnerVillage(villageName) {
      const input = document.getElementById('runner-base-village');
      if (input) input.value = villageName;
      const dropdown = document.getElementById('runner-village-dropdown');
      if (dropdown) dropdown.classList.add('hidden');
    }

    document.addEventListener('click', (e) => {
      const container = document.getElementById('runner-village-container');
      const dropdown = document.getElementById('runner-village-dropdown');
      if (container && dropdown && !container.contains(e.target)) {
        dropdown.classList.add('hidden');
      }
    });

    async function saveRunnerLocationAndProceed()"""

if runner_map_funcs_pattern:
    runner_html = runner_html[:runner_map_funcs_pattern.start()] + new_runner_dropdown_js + runner_html[runner_map_funcs_pattern.end() - len('async function saveRunnerLocationAndProceed()'):]
    print("Runner map, GPS & radius functions replaced with Searchable Village Dropdown logic.")
else:
    print("WARNING: Could not find runner map functions pattern!")

with open("public_web/runner/index.html", "w", encoding="utf-8") as f:
    f.write(runner_html)
print("Runner index.html successfully saved.")

print("\nALL 3 APPS PATCHED SUCCESSFULLY.")
