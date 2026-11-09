import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/vendor/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# =============================================================================
# PART 1: ROUTING & ROGUE LANGUAGE SELECTOR ISOLATION
# =============================================================================
# 1.1 Ensure screen-onboarding-1 is hidden with style="display: none;"
s1_old = '<div id="screen-onboarding-1" class="app-screen flex-1 p-6 flex flex-col justify-between hidden">'
s1_new = '<div id="screen-onboarding-1" class="app-screen flex-1 p-6 flex flex-col justify-between hidden" style="display: none;">'
if s1_old in text:
    text = text.replace(s1_old, s1_new, 1)

# 1.2 Update switchDashboardTab to strictly hide all .app-screen and enforce dashboard mode
sw_old = """    function switchDashboardTab(tabName, pushHistory = true) {
      state.activeTab = tabName;
      document.querySelectorAll('.dashboard-tab').forEach(t => t.classList.add('hidden'));"""

sw_new = """    function switchDashboardTab(tabName, pushHistory = true) {
      state.activeTab = tabName;
      state.currentScreen = 'dashboard';

      // STRICT ROUTING: Suppress all onboarding screens (including language selector) on the dashboard
      document.querySelectorAll('.app-screen').forEach(s => {
        s.classList.add('hidden');
        s.style.display = 'none';
      });
      const s1 = document.getElementById('screen-onboarding-1');
      if (s1) { s1.classList.add('hidden'); s1.style.display = 'none'; }

      document.querySelectorAll('.dashboard-tab').forEach(t => {
        t.classList.add('hidden');
        t.style.display = 'none';
      });"""

if sw_old in text:
    text = text.replace(sw_old, sw_new, 1)
    print("SUCCESS: Updated switchDashboardTab")
else:
    print("WARNING: sw_old not matched")

# 1.3 Update openDashboard
od_old = """    function openDashboard(initialTab = 'orders', pushHistory = true) {
      document.querySelectorAll('.app-screen').forEach(s => s.classList.add('hidden'));"""

od_new = """    function openDashboard(initialTab = 'orders', pushHistory = true) {
      // STRICT ROUTING: Hide all onboarding screens
      document.querySelectorAll('.app-screen').forEach(s => {
        s.classList.add('hidden');
        s.style.display = 'none';
      });
      const s1 = document.getElementById('screen-onboarding-1');
      if (s1) { s1.classList.add('hidden'); s1.style.display = 'none'; }"""

if od_old in text:
    text = text.replace(od_old, od_new, 1)
    print("SUCCESS: Updated openDashboard")
else:
    print("WARNING: od_old not matched")

# =============================================================================
# PART 2: EXPAND I18N STRINGS (STRICT SINGLE-LANGUAGE, NO SLASHES)
# =============================================================================
en_key = 'inventory_title: "Live Catalog & Stock",'
en_vals = """inventory_title: "Live Catalog & Stock",
        inventory_sub: "Instant toggle visible to village customers",
        action_scan_barcode_title: "Scan Barcode",
        action_scan_barcode_sub: "Packaged FMCG Goods",
        action_take_photo_title: "Take Photo",
        action_take_photo_sub: "Fresh Produce & Loose Items",
        type_item_name_btn: "+ Type Item Name",
        view_catalog_btn: "View Catalog",
        search_inventory_placeholder: "Search or speak item (Potato, Tomato, Atta)...",
        speak_to_search_title: "Speak to Search",
        scanner_modal_title: "Scan Barcode",
        scanner_modal_sub: "Align packaged FMCG barcode inside the camera frame",
        scanner_status_ready: "Camera Ready",
        enter_barcode_number_label: "Or Enter Barcode Number",
        barcode_placeholder: "e.g. 8901030383701",
        verify_barcode_btn: "Verify",
        sample_barcodes_title: "Sample FMCG Barcodes:",
        close_btn: "Close",
        photo_modal_title: "Take Photo",
        photo_modal_sub: "Fresh fruits, vegetables, loose dal, sweets",
        photo_status_prompt: "Capture real product photo with camera",
        open_camera_btn: "Open Camera & Snap Photo",
        quick_staples_title: "Quick Fresh Staples:",
        item_name_label: "Item Name *",
        unit_label: "Unit",
        category_label: "Category",
        continue_to_pricing_btn: "Set Item Price",
        pricing_modal_title: "Set Item Price",
        pricing_modal_sub: "Your shop, your prices (No locked prices)",
        pricing_item_name_label: "Item Name (Editable)",
        pricing_details_title: "Pricing Details",
        pricing_mrp_label: "Maximum Retail Price (MRP) *",
        pricing_selling_price_label: "Your Selling Price (To Customer) *",
        pricing_stock_label: "Stock Quantity *",
        pricing_instock_label: "Available in Stock",
        add_to_live_store_btn: "Add to Live Store",
        cat_vegetables: "Vegetables",
        cat_grocery: "Grocery",
        cat_dairy: "Dairy",
        cat_sweets: "Sweets",
        cat_snacks: "Snacks",
        unit_1kg: "1 kg",
        unit_500g: "500 g",
        unit_250g: "250 g",
        unit_1l: "1 L",
        unit_1packet: "1 Packet",
        unit_1piece: "1 Piece","""

if en_key in text and 'action_scan_barcode_title' not in text:
    text = text.replace(en_key, en_vals, 1)

hi_key = 'inventory_title: "लाइव कैटलॉग और स्टॉक",'
hi_vals = """inventory_title: "लाइव कैटलॉग और स्टॉक",
        inventory_sub: "गांव के ग्राहकों के लिए तत्काल टॉगल",
        action_scan_barcode_title: "बारकोड स्कैन करें",
        action_scan_barcode_sub: "पैकेटबंद सामान (FMCG)",
        action_take_photo_title: "फोटो खींचें",
        action_take_photo_sub: "ताजा फल, सब्जी व खुले सामान",
        type_item_name_btn: "+ नया सामान टाइप करें",
        view_catalog_btn: "कैटलॉग सूची",
        search_inventory_placeholder: "सामान खोजें या बोलें (आलू, टमाटर, आटा)...",
        speak_to_search_title: "बोलकर खोजें",
        scanner_modal_title: "बारकोड स्कैनर",
        scanner_modal_sub: "पैकेट पर छपे बारकोड को कैमरे के सामने लाएं",
        scanner_status_ready: "कैमरा सक्रिय",
        enter_barcode_number_label: "या बारकोड नंबर दर्ज करें",
        barcode_placeholder: "उदा. 8901030383701",
        verify_barcode_btn: "जाँचें",
        sample_barcodes_title: "त्वरित बारकोड नमूने:",
        close_btn: "बंद करें",
        photo_modal_title: "फोटो खींचें",
        photo_modal_sub: "ताज़ा फल, सब्ज़ी, खुली दाल, मिठाई आदि",
        photo_status_prompt: "कैमरे से सामान की असली फोटो खींचे",
        open_camera_btn: "कैमरा खोलें व फोटो खींचें",
        quick_staples_title: "त्वरित ताजा सामान:",
        item_name_label: "सामान का नाम *",
        unit_label: "इकाई",
        category_label: "श्रेणी",
        continue_to_pricing_btn: "मूल्य तय करें",
        pricing_modal_title: "कीमत तय करें",
        pricing_modal_sub: "आपकी दुकान, आपकी कीमत (कोई तय सीमा नहीं)",
        pricing_item_name_label: "सामान का नाम (बदलाव संभव)",
        pricing_details_title: "मूल्य निर्धारण",
        pricing_mrp_label: "अधिकतम खुदरा मूल्य (MRP) *",
        pricing_selling_price_label: "आपकी बिक्री कीमत (ग्राहक के लिए) *",
        pricing_stock_label: "स्टॉक मात्रा *",
        pricing_instock_label: "स्टॉक में उपलब्ध है",
        add_to_live_store_btn: "दुकान में जोड़ें",
        cat_vegetables: "सब्ज़ियाँ",
        cat_grocery: "किराना",
        cat_dairy: "डेयरी",
        cat_sweets: "मिठाई",
        cat_snacks: "नमकीन",
        unit_1kg: "1 किलो",
        unit_500g: "500 ग्राम",
        unit_250g: "250 ग्राम",
        unit_1l: "1 लीटर",
        unit_1packet: "1 पैकेट",
        unit_1piece: "1 पीस","""

if hi_key in text and 'action_scan_barcode_title' not in text:
    text = text.replace(hi_key, hi_vals, 1)

# =============================================================================
# PART 3: REWRITE HTML INVENTORY AND MODALS MARKUP (NO SLASHES)
# =============================================================================
# 3.1 tab-inventory
text = re.sub(
    r'placeholder="सामान खोजें या बोलें \(आलू, टमाटर, आटा\)\.\.\. / Search or speak item\.\.\."',
    'data-i18n-placeholder="search_inventory_placeholder" placeholder="Search or speak item (Potato, Tomato, Atta)..."',
    text
)
text = re.sub(
    r'title="बोलकर खोजें / Speak to Search"',
    'data-i18n-title="speak_to_search_title" title="Speak to Search"',
    text
)

# Replace Scan Barcode card inner text
text = re.sub(
    r'<span class="block text-xs font-extrabold tracking-wide">बारकोड स्कैन करें</span>\s*<span class="block text-\[10px\] text-emerald-100 font-medium">Scan Barcode \(FMCG\)</span>',
    '<span class="block text-xs font-extrabold tracking-wide" data-i18n="action_scan_barcode_title">Scan Barcode</span>\n              <span class="block text-[10px] text-emerald-100 font-medium" data-i18n="action_scan_barcode_sub">Packaged FMCG Goods</span>',
    text
)

# Replace Take Photo card inner text
text = re.sub(
    r'<span class="block text-xs font-extrabold tracking-wide">फोटो खींचे</span>\s*<span class="block text-\[10px\] text-amber-100 font-medium">Take Photo \(Fresh/Loose\)</span>',
    '<span class="block text-xs font-extrabold tracking-wide" data-i18n="action_take_photo_title">Take Photo</span>\n              <span class="block text-[10px] text-amber-100 font-medium" data-i18n="action_take_photo_sub">Fresh Produce & Loose Items</span>',
    text
)

# Quick links
text = text.replace(
    '<span>+ नया सामान टाइप करें / Type Item Name</span>',
    '<span data-i18n="type_item_name_btn">+ Type Item Name</span>'
)
text = text.replace(
    '<span>कैटलॉग सूची / View Catalog</span>',
    '<span data-i18n="view_catalog_btn">View Catalog</span>'
)

# 3.2 modal-barcode-scanner
text = re.sub(
    r'<h3 class="text-xs sm:text-sm font-extrabold text-slate-900">बारकोड स्कैनर / Scan Barcode</h3>\s*<p class="text-\[10px\] text-slate-500">पैकेट पर छपा बारकोड सामने लाएं \(Packaged FMCG\)</p>',
    '<h3 class="text-xs sm:text-sm font-extrabold text-slate-900" data-i18n="scanner_modal_title">Scan Barcode</h3>\n              <p class="text-[10px] text-slate-500" data-i18n="scanner_modal_sub">Align packaged FMCG barcode inside the camera frame</p>',
    text
)
text = re.sub(
    r'कैमरा सक्रिय / Ready to Scan',
    '<span data-i18n="scanner_status_ready">Camera Ready</span>',
    text
)
text = text.replace(
    '<label class="block text-[11px] font-bold text-slate-700">बारकोड नंबर दर्ज करें / Or Enter Barcode Number</label>',
    '<label class="block text-[11px] font-bold text-slate-700" data-i18n="enter_barcode_number_label">Or Enter Barcode Number</label>'
)
text = text.replace(
    '<input type="text" id="manual-barcode-input" placeholder="उदा. 8901030383701"',
    '<input type="text" id="manual-barcode-input" data-i18n-placeholder="barcode_placeholder" placeholder="e.g. 8901030383701"'
)
text = re.sub(
    r'<button type="button" onclick="submitManualBarcode\(\)" class="([^"]+)">\s*जाँचें / Verify\s*</button>',
    r'<button type="button" onclick="submitManualBarcode()" class="\1" data-i18n="verify_barcode_btn">Verify</button>',
    text
)
text = text.replace(
    '<span class="text-[10px] font-bold text-slate-500 uppercase tracking-wide block">त्वरित बारकोड नमूने / Sample FMCG Barcodes:</span>',
    '<span class="text-[10px] font-bold text-slate-500 uppercase tracking-wide block" data-i18n="sample_barcodes_title">Sample FMCG Barcodes:</span>'
)

# Replace the entire sample barcodes container with dynamic container
m_scan = text.find('id="modal-barcode-scanner"')
if m_scan != -1:
    grid_start = text.find('<div class="grid grid-cols-2 gap-1.5 text-left">', m_scan)
    btn_close = text.find('closeBarcodeScannerModal', grid_start)
    grid_end = text.rfind('</div>', grid_start, btn_close) + 6
    if grid_start != -1 and grid_end != -1:
        text = text[:grid_start] + '<div id="sample-barcodes-container" class="grid grid-cols-2 gap-1.5 text-left"></div>\n        </div>' + text[grid_end:]
        print("SUCCESS: Replaced sample barcodes grid with dynamic container")

text = re.sub(
    r'<button type="button" onclick="closeBarcodeScannerModal\(\)" class="([^"]+)">\s*बंद करें / Close\s*</button>',
    r'<button type="button" onclick="closeBarcodeScannerModal()" class="\1" data-i18n="close_btn">Close</button>',
    text
)

# 3.3 modal-take-photo
text = re.sub(
    r'<h3 class="text-xs sm:text-sm font-extrabold text-slate-900">फोटो खींचे / Take Real Photo</h3>\s*<p class="text-\[10px\] text-slate-500">ताज़ा फल, सब्ज़ी, खुली दाल, मिठाई आदि</p>',
    '<h3 class="text-xs sm:text-sm font-extrabold text-slate-900" data-i18n="photo_modal_title">Take Photo</h3>\n              <p class="text-[10px] text-slate-500" data-i18n="photo_modal_sub">Fresh fruits, vegetables, loose dal, sweets</p>',
    text
)
text = text.replace(
    '<p class="text-xs font-bold text-amber-950" id="photo-status-text">कैमरे से सामान की असली फोटो खींचे</p>',
    '<p class="text-xs font-bold text-amber-950" id="photo-status-text" data-i18n="photo_status_prompt">Capture real product photo with camera</p>'
)
text = text.replace(
    '<span>कैमरा खोलें व फोटो खींचे / Open Camera & Snap</span>',
    '<span data-i18n="open_camera_btn">Open Camera & Snap Photo</span>'
)
text = text.replace(
    '<span class="text-[10px] font-bold text-slate-500 uppercase tracking-wide block">त्वरित चयन / Quick Fresh Staples:</span>',
    '<span class="text-[10px] font-bold text-slate-500 uppercase tracking-wide block" data-i18n="quick_staples_title">Quick Fresh Staples:</span>'
)

# Replace loose items container
m_photo = text.find('id="modal-take-photo"')
if m_photo != -1:
    chips_start = text.find('<div class="flex flex-wrap gap-1.5">', m_photo)
    chips_end = text.find('</div>', text.find('selectLooseItemChip', chips_start)) + 6
    if chips_start != -1 and chips_end != -1:
        text = text[:chips_start] + '<div id="loose-item-chips-container" class="flex flex-wrap gap-1.5"></div>' + text[chips_end:]
        print("SUCCESS: Replaced loose items chips with dynamic container")

text = text.replace(
    '<label class="block text-[11px] font-bold text-slate-700 mb-1">सामान का नाम / Item Name *</label>',
    '<label class="block text-[11px] font-bold text-slate-700 mb-1" data-i18n="item_name_label">Item Name *</label>'
)
text = text.replace(
    '<label class="block text-[11px] font-bold text-slate-700 mb-1">इकाई / Unit</label>',
    '<label class="block text-[11px] font-bold text-slate-700 mb-1" data-i18n="unit_label">Unit</label>'
)
text = text.replace(
    '<label class="block text-[11px] font-bold text-slate-700 mb-1">श्रेणी / Category</label>',
    '<label class="block text-[11px] font-bold text-slate-700 mb-1" data-i18n="category_label">Category</label>'
)

# Replace unit select options
unit_target_re = r'<select id="loose-item-unit-input"[^>]*>.*?</select>'
unit_replacement = """<select id="loose-item-unit-input" class="w-full px-3 py-2.5 rounded-xl border border-slate-300 text-xs font-bold text-slate-800 bg-white">
                <option value="1 kg" data-i18n="unit_1kg">1 kg</option>
                <option value="500 g" data-i18n="unit_500g">500 g</option>
                <option value="250 g" data-i18n="unit_250g">250 g</option>
                <option value="1 L" data-i18n="unit_1l">1 L</option>
                <option value="1 Packet" data-i18n="unit_1packet">1 Packet</option>
                <option value="1 Piece" data-i18n="unit_1piece">1 Piece</option>
              </select>"""
text = re.sub(unit_target_re, unit_replacement, text, flags=re.DOTALL)

# Replace category select options
cat_target_re = r'<select id="loose-item-cat-input"[^>]*>.*?</select>'
cat_replacement = """<select id="loose-item-cat-input" class="w-full px-3 py-2.5 rounded-xl border border-slate-300 text-xs font-bold text-slate-800 bg-white">
                <option value="Vegetables" data-i18n="cat_vegetables">Vegetables</option>
                <option value="Grocery" data-i18n="cat_grocery">Grocery</option>
                <option value="Dairy" data-i18n="cat_dairy">Dairy</option>
                <option value="Sweets" data-i18n="cat_sweets">Sweets</option>
                <option value="Snacks" data-i18n="cat_snacks">Snacks</option>
              </select>"""
text = re.sub(cat_target_re, cat_replacement, text, flags=re.DOTALL)

text = text.replace(
    '<span>मूल्य तय करें / Continue to Pricing</span>',
    '<span data-i18n="continue_to_pricing_btn">Set Item Price</span>'
)

# 3.4 modal-custom-pricing
text = re.sub(
    r'<h3 class="text-xs sm:text-sm font-extrabold text-slate-900">कीमत तय करें / Set Item Price</h3>\s*<p class="text-\[10px\] text-slate-500">आपकी दुकान, आपकी कीमत \(No Locked Prices\)</p>',
    '<h3 class="text-xs sm:text-sm font-extrabold text-slate-900" data-i18n="pricing_modal_title">Set Item Price</h3>\n              <p class="text-[10px] text-slate-500" data-i18n="pricing_modal_sub">Your shop, your prices (No locked prices)</p>',
    text
)
text = text.replace(
    '<label class="block text-[10px] font-bold text-slate-500 uppercase tracking-wide">सामान का नाम (बदलाव संभव) / Item Name</label>',
    '<label class="block text-[10px] font-bold text-slate-500 uppercase tracking-wide" data-i18n="pricing_item_name_label">Item Name (Editable)</label>'
)
text = text.replace(
    '<span class="text-xs font-extrabold text-emerald-950 block">मूल्य निर्धारण / Pricing Details</span>',
    '<span class="text-xs font-extrabold text-emerald-950 block" data-i18n="pricing_details_title">Pricing Details</span>'
)
text = text.replace(
    '<label class="block text-xs font-bold text-slate-700">अधिकतम खुदरा मूल्य (MRP) *</label>',
    '<label class="block text-xs font-bold text-slate-700" data-i18n="pricing_mrp_label">Maximum Retail Price (MRP) *</label>'
)
text = text.replace(
    '<label class="block text-xs font-bold text-emerald-950">आपकी बिक्री कीमत (Your Selling Price) *</label>',
    '<label class="block text-xs font-bold text-emerald-950" data-i18n="pricing_selling_price_label">Your Selling Price (To Customer) *</label>'
)
text = text.replace(
    '<label class="block text-[11px] font-bold text-slate-700 mb-1">स्टॉक मात्रा / Stock *</label>',
    '<label class="block text-[11px] font-bold text-slate-700 mb-1" data-i18n="pricing_stock_label">Stock Quantity *</label>'
)
text = text.replace(
    '<span class="text-xs font-bold text-slate-800">स्टॉक में उपलब्ध है</span>',
    '<span class="text-xs font-bold text-slate-800" data-i18n="pricing_instock_label">Available in Stock</span>'
)
text = text.replace(
    '<span>दुकान में जोड़ें / Add to Live Store</span>',
    '<span data-i18n="add_to_live_store_btn">Add to Live Store</span>'
)

# Remove MRP placeholder prediction from input
text = text.replace('placeholder="उदा. 260"', 'placeholder="0.00"')
text = text.replace('placeholder="उदा. 240"', 'placeholder="0.00"')

# =============================================================================
# PART 4: REWRITE JAVASCRIPT LOGIC (DECOUPLE PRICING, VOICE SEARCH, RENDERERS)
# =============================================================================
# Locate FMCG_BARCODE_LOOKUP and replace with decoupled data (NO mrp, NO price)
lookup_start = text.find('const FMCG_BARCODE_LOOKUP = {')
lookup_end = text.find('};', lookup_start) + 2

decoupled_lookup = """const FMCG_BARCODE_LOOKUP = {
      "8901030383701": {
        titleEn: "Aashirvaad Shudh Chakki Atta (5 kg)",
        titleHi: "आशीर्वाद शुद्ध चक्की आटा (5 kg)",
        brand: "Aashirvaad",
        category: "Grocery",
        unit: "5 kg",
        img: "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=600&q=80"
      },
      "8901262010053": {
        titleEn: "Tata Salt Vacuum Evaporated (1 kg)",
        titleHi: "टाटा नमक (1 kg)",
        brand: "Tata",
        category: "Grocery",
        unit: "1 kg",
        img: "https://images.unsplash.com/photo-1518110925495-5fe2fda0442c?w=500&q=80"
      },
      "8901491101836": {
        titleEn: "Fortune Kachi Ghani Mustard Oil (1 L)",
        titleHi: "फॉर्च्यून कच्ची घानी सरसों तेल (1 L)",
        brand: "Fortune",
        category: "Grocery",
        unit: "1 L",
        img: "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=500&q=80"
      },
      "8901063012111": {
        titleEn: "Britannia Good Day Butter Cookies (200 g)",
        titleHi: "ब्रिटानिया गुड डे बटर कुकीज (200 g)",
        brand: "Britannia",
        category: "Snacks",
        unit: "200 g",
        img: "https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=500&q=80"
      },
      "8901725181221": {
        titleEn: "Maggi 2-Minute Masala Noodles (280 g)",
        titleHi: "मैगी 2-मिनट मसाला नूडल्स (280 g)",
        brand: "Nestle",
        category: "Snacks",
        unit: "280 g",
        img: "https://images.unsplash.com/photo-1612927601601-6638404737ce?w=500&q=80"
      },
      "8901030000000": {
        titleEn: "Parle-G Glucose Biscuits (250 g)",
        titleHi: "पारले-जी ग्लूकोज बिस्कुट (250 g)",
        brand: "Parle",
        category: "Snacks",
        unit: "250 g",
        img: "https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=500&q=80"
      }
    };

    const SAMPLE_BARCODES_LIST = [
      { code: '8901030383701', en: 'Aashirvaad Chakki Atta (5 kg)', hi: 'आशीर्वाद चक्की आटा (5 kg)' },
      { code: '8901262010053', en: 'Tata Salt (1 kg)', hi: 'टाटा नमक (1 kg)' },
      { code: '8901491101836', en: 'Fortune Mustard Oil (1 L)', hi: 'फॉर्च्यून सरसों तेल (1 L)' },
      { code: '8901063012111', en: 'Britannia Good Day (200 g)', hi: 'गुड डे बिस्कुट (200 g)' },
      { code: '8901725181221', en: 'Maggi Noodles (280 g)', hi: 'मैगी नूडल्स (280 g)' },
      { code: '8901030000000', en: 'Parle-G Biscuits (250 g)', hi: 'पारले-जी बिस्कुट (250 g)' }
    ];

    const LOOSE_ITEM_CHIPS = [
      { en: "Fresh Tomatoes (1 kg)", hi: "ताज़ा टमाटर (1 kg)", cat: "Vegetables", unit: "1 kg", img: "https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=500&q=80", icon: "🍅" },
      { en: "Local Potatoes (1 kg)", hi: "देसी आलू (1 kg)", cat: "Vegetables", unit: "1 kg", img: "https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=500&q=80", icon: "🥔" },
      { en: "Red Onions (1 kg)", hi: "लाल प्याज़ (1 kg)", cat: "Vegetables", unit: "1 kg", img: "https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb?w=500&q=80", icon: "🧅" },
      { en: "Loose Toor Dal (1 kg)", hi: "अरहर दाल (1 kg)", cat: "Grocery", unit: "1 kg", img: "https://images.unsplash.com/photo-1585032226651-759b368d7246?w=500&q=80", icon: "🌾" },
      { en: "Fresh Cow Milk (1 L)", hi: "ताज़ा गाय का दूध (1 L)", cat: "Dairy", unit: "1 L", img: "https://images.unsplash.com/photo-1550583724-b2692b85b150?w=500&q=80", icon: "🥛" },
      { en: "Gulab Jamun (1 kg)", hi: "देसी गुलाब जामुन (1 kg)", cat: "Sweets", unit: "1 kg", img: "https://images.unsplash.com/photo-1541781774459-bb2af2f05b55?w=500&q=80", icon: "🍬" }
    ];

    function renderSampleBarcodes() {
      const container = document.getElementById('sample-barcodes-container');
      if (!container) return;
      const isHi = (typeof currentLang !== 'undefined' ? currentLang === 'hi' : false) || 
                   (localStorage.getItem('gaonbazaar_vendor_lang') === 'hi') || 
                   (window.currentLang === 'hi');
      container.innerHTML = SAMPLE_BARCODES_LIST.map(item => `
        <button type="button" onclick="handleBarcodeDetected('${item.code}')" class="p-2.5 rounded-xl bg-slate-50 hover:bg-emerald-50 border border-slate-200 hover:border-emerald-300 text-left transition active:scale-95 cursor-pointer">
          <span class="block text-[11px] font-bold text-slate-900 truncate">${isHi ? item.hi : item.en}</span>
          <span class="block text-[10px] text-emerald-700 font-mono font-semibold">${item.code}</span>
        </button>
      `).join('');
    }
    window.renderSampleBarcodes = renderSampleBarcodes;

    function renderLooseItemChips() {
      const container = document.getElementById('loose-item-chips-container');
      if (!container) return;
      const isHi = (typeof currentLang !== 'undefined' ? currentLang === 'hi' : false) || 
                   (localStorage.getItem('gaonbazaar_vendor_lang') === 'hi') || 
                   (window.currentLang === 'hi');
      container.innerHTML = LOOSE_ITEM_CHIPS.map(item => {
        const title = isHi ? item.hi : item.en;
        return `
          <button type="button" onclick="selectLooseItemChip('${title.replace(/'/g, "\\'")}', '${item.cat}', '${item.unit}', '${item.img}')" class="px-2.5 py-1.5 rounded-lg bg-slate-100 hover:bg-amber-100 border border-slate-200 text-[11px] font-bold text-slate-800 transition active:scale-95 cursor-pointer">
            ${item.icon} ${title}
          </button>
        `;
      }).join('');
    }
    window.renderLooseItemChips = renderLooseItemChips;"""

if lookup_start != -1 and lookup_end != -1:
    text = text[:lookup_start] + decoupled_lookup + text[lookup_end:]
    print("SUCCESS: Decoupled FMCG_BARCODE_LOOKUP and added dynamic renderers")

# Replace handleBarcodeDetected implementation (strictly decouples pricing)
hbd_start = text.find('function handleBarcodeDetected(barcode) {')
hbd_end = text.find('window.handleBarcodeDetected = handleBarcodeDetected;', hbd_start) + len('window.handleBarcodeDetected = handleBarcodeDetected;')

new_hbd = """function handleBarcodeDetected(barcode) {
      closeBarcodeScannerModal();
      const code = String(barcode).trim();
      const isHi = (typeof currentLang !== 'undefined' ? currentLang === 'hi' : false) || 
                   (localStorage.getItem('gaonbazaar_vendor_lang') === 'hi') || 
                   (window.currentLang === 'hi');

      // Check FMCG Barcode Database (Decoupled: Only Name & Image, No Prices)
      let rawItem = FMCG_BARCODE_LOOKUP[code];
      let item = null;

      if (rawItem) {
        item = {
          title: isHi ? rawItem.titleHi : rawItem.titleEn,
          brand: rawItem.brand,
          category: rawItem.category,
          unit: rawItem.unit,
          img: rawItem.img,
          mrp: '',
          price: '',
          stock: ''
        };
      } else {
        const skus = (window.MASTER_SKU_DATABASE && Array.isArray(window.MASTER_SKU_DATABASE)) ? window.MASTER_SKU_DATABASE : MASTER_SKU_DATABASE;
        const matchedSku = skus.find(s => (s.id || '').includes(code) || (s.product_name || '').toLowerCase().includes(code.toLowerCase()));
        if (matchedSku) {
          item = {
            title: isHi ? (matchedSku.product_name_hi || matchedSku.product_name) : matchedSku.product_name,
            brand: matchedSku.brand,
            category: matchedSku.category,
            unit: matchedSku.variant || matchedSku.unit,
            img: matchedSku.image_url,
            mrp: '',
            price: '',
            stock: ''
          };
        } else {
          item = {
            title: isHi ? `पैकेटबंद सामान (${code.slice(-6)})` : `Packaged Product (${code.slice(-6)})`,
            brand: "FMCG",
            category: "Grocery",
            unit: "1 unit",
            img: "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=600&q=80",
            mrp: '',
            price: '',
            stock: ''
          };
        }
      }

      toastSuccess(isHi ? `बारकोड मिला: ${item.title}` : `Barcode matched: ${item.title}`);
      
      // DECOUPLED PRICING PIPELINE:
      // Pass Name and Image, leaving MRP, Price, and Stock COMPLETELY BLANK for vendor manual entry
      openCustomPricingModal(item);
    }
    window.handleBarcodeDetected = handleBarcodeDetected;"""

if hbd_start != -1 and hbd_end != -1:
    text = text[:hbd_start] + new_hbd + text[hbd_end:]
    print("SUCCESS: Updated handleBarcodeDetected with decoupled pricing")

# Replace continueToPricingFromPhoto implementation (strictly decouples pricing)
cpp_start = text.find('function continueToPricingFromPhoto() {')
cpp_end = text.find('window.continueToPricingFromPhoto = continueToPricingFromPhoto;', cpp_start) + len('window.continueToPricingFromPhoto = continueToPricingFromPhoto;')

new_cpp = """function continueToPricingFromPhoto() {
      const name = (document.getElementById('loose-item-name-input')?.value || '').trim();
      const unit = document.getElementById('loose-item-unit-input')?.value || '1 kg';
      const cat = document.getElementById('loose-item-cat-input')?.value || 'Vegetables';
      const isHi = (typeof currentLang !== 'undefined' ? currentLang === 'hi' : false) || 
                   (localStorage.getItem('gaonbazaar_vendor_lang') === 'hi') || 
                   (window.currentLang === 'hi');

      if (!name) {
        toastError(isHi ? "कृपया सामान का नाम दर्ज करें।" : "Please enter the item name.");
        document.getElementById('loose-item-name-input')?.focus();
        return;
      }

      closePhotoCaptureModal();
      
      // Decoupled Pricing: Leave MRP, Selling Price, and Stock completely blank
      openCustomPricingModal({
        title: name,
        category: cat,
        unit: unit,
        mrp: '',
        price: '',
        stock: '',
        img: currentSnappedPhotoData || "https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=500&q=80"
      });
    }
    window.continueToPricingFromPhoto = continueToPricingFromPhoto;"""

if cpp_start != -1 and cpp_end != -1:
    text = text[:cpp_start] + new_cpp + text[cpp_end:]
    print("SUCCESS: Updated continueToPricingFromPhoto with decoupled pricing")

# Replace openCustomPricingModal implementation (strictly blank pricing inputs)
ocp_start = text.find('function openCustomPricingModal(itemData = {}) {')
ocp_end = text.find('window.openCustomPricingModal = openCustomPricingModal;', ocp_start) + len('window.openCustomPricingModal = openCustomPricingModal;')

new_ocp = """function openCustomPricingModal(itemData = {}) {
      const name = itemData.title || itemData.name || itemData.product_name || "";
      const mrp = itemData.mrp !== undefined && itemData.mrp !== null ? String(itemData.mrp).trim() : "";
      const price = itemData.price !== undefined && itemData.price !== null ? String(itemData.price).trim() : "";
      const stock = itemData.stock !== undefined && itemData.stock !== null ? String(itemData.stock).trim() : "";
      const cat = itemData.category || "Grocery";
      const unit = itemData.unit || itemData.variant || "1 unit";
      const img = itemData.img || itemData.image_url || "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=600&q=80";

      currentCustomPricingImg = img;

      const nameInp = document.getElementById('custom-pricing-name');
      const mrpInp = document.getElementById('custom-pricing-mrp');
      const priceInp = document.getElementById('custom-pricing-price');
      const stockInp = document.getElementById('custom-pricing-stock');
      const instockInp = document.getElementById('custom-pricing-instock');
      const previewImg = document.getElementById('custom-pricing-preview-img');
      const catTag = document.getElementById('custom-pricing-cat-tag');
      const unitTag = document.getElementById('custom-pricing-unit-tag');

      if (nameInp) nameInp.value = name;
      // STRICT DECOUPLING: MRP, Selling Price, and Stock are left completely blank for the vendor to manually enter
      if (mrpInp) mrpInp.value = mrp ? mrp : '';
      if (priceInp) priceInp.value = price ? price : '';
      if (stockInp) stockInp.value = stock ? stock : '';
      if (instockInp) instockInp.checked = true;
      if (previewImg) previewImg.src = img;
      if (catTag) catTag.innerText = cat;
      if (unitTag) unitTag.innerText = unit;

      calculateCustomPricingDiscount();

      openModal('modal-custom-pricing');
      if (window.lucide) lucide.createIcons();

      setTimeout(() => {
        if (name && mrpInp) {
          mrpInp.focus();
        } else if (nameInp) {
          nameInp.focus();
        }
      }, 200);
    }
    window.openCustomPricingModal = openCustomPricingModal;"""

if ocp_start != -1 and ocp_end != -1:
    text = text[:ocp_start] + new_ocp + text[ocp_end:]
    print("SUCCESS: Updated openCustomPricingModal with blank pricing inputs")

# Replace calculateCustomPricingDiscount implementation (pure single-language text)
ccd_start = text.find('function calculateCustomPricingDiscount() {')
ccd_end = text.find('window.calculateCustomPricingDiscount = calculateCustomPricingDiscount;', ccd_start) + len('window.calculateCustomPricingDiscount = calculateCustomPricingDiscount;')

new_ccd = """function calculateCustomPricingDiscount() {
      const mrp = parseFloat(document.getElementById('custom-pricing-mrp')?.value) || 0;
      const price = parseFloat(document.getElementById('custom-pricing-price')?.value) || 0;
      const badge = document.getElementById('custom-pricing-discount-badge');
      const badgeText = document.getElementById('discount-badge-text');

      if (!badge || !badgeText) return;
      const isHi = (typeof currentLang !== 'undefined' ? currentLang === 'hi' : false) || 
                   (localStorage.getItem('gaonbazaar_vendor_lang') === 'hi') || 
                   (window.currentLang === 'hi');

      if (mrp > 0 && price > 0 && mrp > price) {
        const discountPct = Math.round(((mrp - price) / mrp) * 100);
        const savings = (mrp - price).toFixed(0);
        badgeText.innerText = isHi 
          ? `${discountPct}% छूट (₹${savings} ग्राहक बचत)` 
          : `${discountPct}% OFF (₹${savings} Customer Savings)`;
        badge.className = "p-2.5 bg-emerald-100 border border-emerald-300 rounded-xl text-emerald-900 font-extrabold text-xs flex items-center space-x-2";
      } else if (mrp > 0 && price > 0 && price >= mrp) {
        badgeText.innerText = isHi ? "MRP पर बिक्री" : "Standard Price";
        badge.className = "p-2.5 bg-slate-100 border border-slate-200 rounded-xl text-slate-700 font-bold text-xs flex items-center space-x-2";
      } else {
        badgeText.innerText = isHi ? "कीमत दर्ज करें" : "Enter Price";
        badge.className = "p-2.5 bg-slate-100 border border-slate-200 rounded-xl text-slate-500 font-bold text-xs flex items-center space-x-2";
      }
    }
    window.calculateCustomPricingDiscount = calculateCustomPricingDiscount;"""

if ccd_start != -1 and ccd_end != -1:
    text = text[:ccd_start] + new_ccd + text[ccd_end:]
    print("SUCCESS: Updated calculateCustomPricingDiscount with single-language text")

# Replace setLanguage implementation (updates data-i18n, placeholder, title, and calls dynamic renderers)
sl_start = text.find('function setLanguage(lang) {')
sl_end = text.find('function toggleAppLanguage() {', sl_start)

new_sl = """function setLanguage(lang) {
      currentLang = lang;
      window.currentLang = lang;
      localStorage.setItem('gaonbazaar_vendor_lang', lang);
      updateVendorLangCards(lang);

      // Update text using data-i18n attributes
      document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (i18n[lang] && i18n[lang][key]) {
          el.innerText = i18n[lang][key];
        }
      });

      // Update placeholders using data-i18n-placeholder
      document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        const key = el.getAttribute('data-i18n-placeholder');
        if (i18n[lang] && i18n[lang][key]) {
          el.setAttribute('placeholder', i18n[lang][key]);
        }
      });

      // Update titles using data-i18n-title
      document.querySelectorAll('[data-i18n-title]').forEach(el => {
        const key = el.getAttribute('data-i18n-title');
        if (i18n[lang] && i18n[lang][key]) {
          el.setAttribute('title', i18n[lang][key]);
        }
      });

      // Update select dropdown options using data-i18n
      document.querySelectorAll('option[data-i18n]').forEach(opt => {
        const key = opt.getAttribute('data-i18n');
        if (i18n[lang] && i18n[lang][key]) {
          opt.innerText = i18n[lang][key];
        }
      });

      // Render dynamic localized components
      if (typeof renderSampleBarcodes === 'function') renderSampleBarcodes();
      if (typeof renderLooseItemChips === 'function') renderLooseItemChips();

      // Update header indicator
      const langLabel = document.getElementById('current-lang-label');
      if (langLabel) {
        langLabel.innerText = lang === 'en' ? 'English' : 'हिन्दी';
      }
      
      const accLang = document.getElementById('account-lang-name');
      if (accLang) {
        accLang.innerText = lang === 'en' ? 'English' : 'हिन्दी';
      }

      if (window.lucide) lucide.createIcons();
    }
    window.setLanguage = setLanguage;\n\n    """

if sl_start != -1 and sl_end != -1:
    text = text[:sl_start] + new_sl + text[sl_end:]
    print("SUCCESS: Updated setLanguage with comprehensive attribute updating and dynamic rendering")

# Update toggleVendorVoiceSearch and expose testing hook
vvs_start = text.find('function toggleVendorVoiceSearch() {')
vvs_end = text.find('window.toggleVendorVoiceSearch = toggleVendorVoiceSearch;', vvs_start) + len('window.toggleVendorVoiceSearch = toggleVendorVoiceSearch;')

new_vvs = """function toggleVendorVoiceSearch() {
      const searchInput = document.getElementById('inventory-search');
      const micBtn = document.getElementById('btn-vendor-voice-search');
      const micIcon = document.getElementById('vendor-mic-icon');
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

      const isHi = (typeof currentLang !== 'undefined' ? currentLang === 'hi' : false) || 
                   (localStorage.getItem('gaonbazaar_vendor_lang') === 'hi') || 
                   (window.currentLang === 'hi');

      if (!SpeechRecognition) {
        const simulatedVoice = prompt(isHi 
          ? "आवाज़ से सामान का नाम बोलें (उदा. आटा, दूध, तेल):" 
          : "Speak item name (e.g. Atta, Milk, Oil):", isHi ? "आटा" : "Atta");
        if (simulatedVoice) {
          if (searchInput) {
            searchInput.value = simulatedVoice;
            filterInventory(simulatedVoice);
          }
          toastSuccess(isHi ? `पहचाना गया: "${simulatedVoice}"` : `Voice recognized: "${simulatedVoice}"`);
        }
        return;
      }

      if (isVendorListening) {
        stopVendorVoiceSearch();
        return;
      }

      try {
        if (vendorSpeechRecognizer) vendorSpeechRecognizer.abort();
        vendorSpeechRecognizer = new SpeechRecognition();
        vendorSpeechRecognizer.lang = isHi ? 'hi-IN' : 'en-IN';
        vendorSpeechRecognizer.interimResults = false;
        vendorSpeechRecognizer.maxAlternatives = 1;

        isVendorListening = true;
        if (micBtn) {
          micBtn.classList.add('bg-rose-100', 'text-rose-700', 'border-rose-400', 'animate-pulse');
          micBtn.classList.remove('bg-emerald-50', 'text-emerald-700', 'border-emerald-200');
        }
        toastInfo(isHi ? "सुन रहे हैं... सामान का नाम बोलिए (उदा. टमाटर, आटा)!" : "Listening... Speak item name (e.g. Tomato, Atta)!");

        vendorSpeechRecognizer.onresult = function(e) {
          const transcript = e.results[0][0].transcript.trim();
          stopVendorVoiceSearch();

          if (searchInput) {
            searchInput.value = transcript;
            filterInventory(transcript);
          }

          toastSuccess(isHi ? `पहचाना गया: "${transcript}"` : `Voice recognized: "${transcript}"`);
        };

        vendorSpeechRecognizer.onerror = function(e) {
          console.warn("Speech recognition error:", e.error);
          stopVendorVoiceSearch();
          if (e.error === 'not-allowed') {
            toastWarning(isHi ? "माइक्रोफ़ोन की अनुमति नहीं है।" : "Microphone permission denied.");
          }
        };

        vendorSpeechRecognizer.onend = function() {
          stopVendorVoiceSearch();
        };

        vendorSpeechRecognizer.start();
      } catch (err) {
        console.warn("Speech recognition start failed:", err);
        stopVendorVoiceSearch();
      }
    }
    window.toggleVendorVoiceSearch = toggleVendorVoiceSearch;
    window.filterInventory = filterInventory;

    // Direct Voice Simulation Hook for automated verification and emulator environments
    window.simulateVoiceSearch = function(queryText) {
      const searchInput = document.getElementById('inventory-search');
      const micBtn = document.getElementById('btn-vendor-voice-search');
      const isHi = (typeof currentLang !== 'undefined' ? currentLang === 'hi' : false) || 
                   (localStorage.getItem('gaonbazaar_vendor_lang') === 'hi') || 
                   (window.currentLang === 'hi');

      if (micBtn) {
        micBtn.classList.add('bg-rose-100', 'text-rose-700', 'border-rose-400', 'animate-pulse');
        setTimeout(() => {
          micBtn.classList.remove('bg-rose-100', 'text-rose-700', 'border-rose-400', 'animate-pulse');
        }, 300);
      }

      if (searchInput) {
        searchInput.value = queryText;
        filterInventory(queryText);
      }
      toastSuccess(isHi ? `पहचाना गया: "${queryText}"` : `Voice recognized: "${queryText}"`);
    };"""

if vvs_start != -1 and vvs_end != -1:
    text = text[:vvs_start] + new_vvs + text[vvs_end:]
    print("SUCCESS: Updated toggleVendorVoiceSearch and added simulateVoiceSearch")

# Write out updated content
with open('public_web/vendor/index.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("\nSUCCESS: All vendor overhaul changes written cleanly to public_web/vendor/index.html!")
