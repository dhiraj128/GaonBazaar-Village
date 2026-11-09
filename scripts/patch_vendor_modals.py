with open('public_web/vendor/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

modal_start_str = '<!-- MODAL 1: ADD PRODUCT (ENTERPRISE CENTRALIZED MASTER CATALOG LIBRARY) -->'
modal_end_str = '<!-- MODAL 2: UPDATE PAYOUT WITH SMS OTP -->'

modal_start_idx = content.find(modal_start_str)
modal_end_idx = content.find(modal_end_str)

print("start_idx:", modal_start_idx, "end_idx:", modal_end_idx)

if modal_start_idx != -1 and modal_end_idx != -1:
    new_modals = """<!-- =================================================================== -->
    <!-- 1. MODAL: HTML5 BARCODE SCANNER (PACKAGED FMCG GOODS) -->
    <!-- =================================================================== -->
    <div id="modal-barcode-scanner" class="app-modal fixed inset-0 bg-black/75 backdrop-blur-xs z-50 flex items-end sm:items-center justify-center hidden p-0 sm:p-4">
      <div class="w-full max-w-md bg-white rounded-t-3xl sm:rounded-3xl p-5 shadow-2xl max-h-[92vh] overflow-y-auto space-y-4 text-left">
        <!-- Header -->
        <div class="flex items-center justify-between pb-3 border-b border-slate-100">
          <div class="flex items-center space-x-2">
            <div class="w-8 h-8 rounded-full bg-emerald-100 text-emerald-800 flex items-center justify-center">
              <i data-lucide="scan-barcode" class="w-4 h-4"></i>
            </div>
            <div>
              <h3 class="text-xs sm:text-sm font-extrabold text-slate-900">बारकोड स्कैनर / Scan Barcode</h3>
              <p class="text-[10px] text-slate-500">पैकेट पर छपा बारकोड सामने लाएं (Packaged FMCG)</p>
            </div>
          </div>
          <button type="button" onclick="closeBarcodeScannerModal()" class="w-8 h-8 rounded-full bg-slate-100 text-slate-600 hover:bg-slate-200 flex items-center justify-center transition">
            <i data-lucide="x" class="w-4 h-4"></i>
          </button>
        </div>

        <!-- Scanner Viewport Frame with Laser Animation -->
        <div class="relative w-full h-48 bg-slate-950 rounded-2xl overflow-hidden border-2 border-emerald-500 shadow-inner flex items-center justify-center">
          <video id="barcode-scanner-video" autoplay playsinline class="w-full h-full object-cover hidden"></video>
          
          <!-- Animated Laser Scanning Line -->
          <div id="barcode-laser-line" class="absolute left-0 right-0 h-0.5 bg-gradient-to-r from-emerald-400 via-emerald-200 to-emerald-400 shadow-lg shadow-emerald-400 animate-pulse" style="top: 50%;"></div>
          
          <!-- Viewfinder Target Crosshairs -->
          <div class="absolute inset-6 border-2 border-dashed border-emerald-400/60 rounded-xl pointer-events-none flex flex-col justify-between p-2">
            <div class="flex justify-between text-emerald-400 text-xs font-mono font-bold">
              <span>┌</span><span>┐</span>
            </div>
            <div class="text-center">
              <span id="barcode-scanner-status" class="px-2.5 py-1 rounded-full bg-slate-900/80 text-[10px] font-bold text-emerald-300 border border-emerald-500/40">
                कैमरा सक्रिय / Ready to Scan
              </span>
            </div>
            <div class="flex justify-between text-emerald-400 text-xs font-mono font-bold">
              <span>└</span><span>┘</span>
            </div>
          </div>
        </div>

        <!-- Manual Barcode Input -->
        <div class="space-y-1.5">
          <label class="block text-[11px] font-bold text-slate-700">बारकोड नंबर दर्ज करें / Or Enter Barcode Number</label>
          <div class="flex space-x-2">
            <input type="text" id="manual-barcode-input" placeholder="उदा. 8901030383701" class="flex-1 px-3 py-2.5 rounded-xl border border-slate-300 text-xs font-mono font-bold text-slate-900 placeholder-slate-400 focus:outline-none focus:border-emerald-600">
            <button type="button" onclick="submitManualBarcode()" class="px-4 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-xl text-xs shadow-xs transition active:scale-95 cursor-pointer">
              जाँचें / Verify
            </button>
          </div>
        </div>

        <!-- Quick 1-Tap FMCG Test Barcodes (Instant Prototyping) -->
        <div class="space-y-2 pt-1">
          <span class="text-[10px] font-bold text-slate-500 uppercase tracking-wide block">त्वरित बारकोड नमूने / Sample FMCG Barcodes:</span>
          <div class="grid grid-cols-2 gap-1.5 text-left">
            <button type="button" onclick="handleBarcodeDetected('8901030383701')" class="p-2 rounded-xl bg-slate-50 hover:bg-emerald-50 border border-slate-200 hover:border-emerald-300 text-left transition active:scale-95">
              <span class="block text-[11px] font-bold text-slate-900 truncate">आशीर्वाद आटा 5kg</span>
              <span class="block text-[9px] text-slate-500 font-mono">8901030383701 • MRP ₹260</span>
            </button>
            <button type="button" onclick="handleBarcodeDetected('8901262010053')" class="p-2 rounded-xl bg-slate-50 hover:bg-emerald-50 border border-slate-200 hover:border-emerald-300 text-left transition active:scale-95">
              <span class="block text-[11px] font-bold text-slate-900 truncate">टाटा नमक 1kg</span>
              <span class="block text-[9px] text-slate-500 font-mono">8901262010053 • MRP ₹28</span>
            </button>
            <button type="button" onclick="handleBarcodeDetected('8901491101836')" class="p-2 rounded-xl bg-slate-50 hover:bg-emerald-50 border border-slate-200 hover:border-emerald-300 text-left transition active:scale-95">
              <span class="block text-[11px] font-bold text-slate-900 truncate">फॉर्च्यून सरसों तेल 1L</span>
              <span class="block text-[9px] text-slate-500 font-mono">8901491101836 • MRP ₹165</span>
            </button>
            <button type="button" onclick="handleBarcodeDetected('8901063012111')" class="p-2 rounded-xl bg-slate-50 hover:bg-emerald-50 border border-slate-200 hover:border-emerald-300 text-left transition active:scale-95">
              <span class="block text-[11px] font-bold text-slate-900 truncate">गुड डे बिस्कुट</span>
              <span class="block text-[9px] text-slate-500 font-mono">8901063012111 • MRP ₹45</span>
            </button>
            <button type="button" onclick="handleBarcodeDetected('8901725181221')" class="p-2 rounded-xl bg-slate-50 hover:bg-emerald-50 border border-slate-200 hover:border-emerald-300 text-left transition active:scale-95">
              <span class="block text-[11px] font-bold text-slate-900 truncate">मैगी नूडल्स 280g</span>
              <span class="block text-[9px] text-slate-500 font-mono">8901725181221 • MRP ₹56</span>
            </button>
            <button type="button" onclick="handleBarcodeDetected('8901030000000')" class="p-2 rounded-xl bg-slate-50 hover:bg-emerald-50 border border-slate-200 hover:border-emerald-300 text-left transition active:scale-95">
              <span class="block text-[11px] font-bold text-slate-900 truncate">पारले-जी बिस्कुट</span>
              <span class="block text-[9px] text-slate-500 font-mono">8901030000000 • MRP ₹30</span>
            </button>
          </div>
        </div>

        <button type="button" onclick="closeBarcodeScannerModal()" class="w-full py-3 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold rounded-xl text-xs transition">
          बंद करें / Close
        </button>
      </div>
    </div>

    <!-- =================================================================== -->
    <!-- 2. MODAL: DEVICE CAMERA & PHOTO CAPTURE (UNBARCODED / FRESH ITEMS) -->
    <!-- =================================================================== -->
    <div id="modal-take-photo" class="app-modal fixed inset-0 bg-black/75 backdrop-blur-xs z-50 flex items-end sm:items-center justify-center hidden p-0 sm:p-4">
      <div class="w-full max-w-md bg-white rounded-t-3xl sm:rounded-3xl p-5 shadow-2xl max-h-[92vh] overflow-y-auto space-y-4 text-left">
        <!-- Header -->
        <div class="flex items-center justify-between pb-3 border-b border-slate-100">
          <div class="flex items-center space-x-2">
            <div class="w-8 h-8 rounded-full bg-amber-100 text-amber-800 flex items-center justify-center">
              <i data-lucide="camera" class="w-4 h-4"></i>
            </div>
            <div>
              <h3 class="text-xs sm:text-sm font-extrabold text-slate-900">फोटो खींचे / Take Real Photo</h3>
              <p class="text-[10px] text-slate-500">ताज़ा फल, सब्ज़ी, खुली दाल, मिठाई आदि</p>
            </div>
          </div>
          <button type="button" onclick="closePhotoCaptureModal()" class="w-8 h-8 rounded-full bg-slate-100 text-slate-600 hover:bg-slate-200 flex items-center justify-center transition">
            <i data-lucide="x" class="w-4 h-4"></i>
          </button>
        </div>

        <!-- Hidden Real Device Camera File Input -->
        <input type="file" id="vendor-camera-file-input" accept="image/*" capture="environment" class="hidden" onchange="handleVendorCameraPhoto(event)">

        <!-- Photo Capture / Preview Box -->
        <div class="p-4 bg-amber-50/60 rounded-2xl border-2 border-dashed border-amber-300 text-center space-y-3">
          <div id="photo-preview-container" class="hidden w-28 h-28 mx-auto rounded-2xl overflow-hidden border-2 border-amber-500 shadow-md">
            <img id="photo-preview-image" src="" alt="Snapped Photo" class="w-full h-full object-cover">
          </div>
          <div id="photo-placeholder-icon" class="w-14 h-14 mx-auto rounded-2xl bg-amber-100 text-amber-700 flex items-center justify-center">
            <i data-lucide="camera" class="w-7 h-7"></i>
          </div>
          <p class="text-xs font-bold text-amber-950" id="photo-status-text">कैमरे से सामान की असली फोटो खींचे</p>
          
          <button type="button" onclick="triggerCameraCapture()" class="w-full py-3.5 bg-amber-600 hover:bg-amber-700 text-white font-bold rounded-xl text-xs shadow-md transition active:scale-95 flex items-center justify-center space-x-2 cursor-pointer min-h-[48px]">
            <i data-lucide="aperture" class="w-4 h-4"></i>
            <span>कैमरा खोलें व फोटो खींचे / Open Camera & Snap</span>
          </button>
        </div>

        <!-- Quick Loose Item Name Chips -->
        <div class="space-y-1.5">
          <span class="text-[10px] font-bold text-slate-500 uppercase tracking-wide block">त्वरित चयन / Quick Fresh Staples:</span>
          <div class="flex flex-wrap gap-1.5">
            <button type="button" onclick="selectLooseItemChip('ताज़ा टमाटर (Fresh Tomatoes)', 'Vegetables', '1 kg', 'https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=500&q=80')" class="px-2.5 py-1.5 rounded-lg bg-slate-100 hover:bg-amber-100 border border-slate-200 text-[11px] font-bold text-slate-800 transition active:scale-95">
              🍅 ताज़ा टमाटर (1 kg)
            </button>
            <button type="button" onclick="selectLooseItemChip('देसी आलू (Local Potatoes)', 'Vegetables', '1 kg', 'https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=500&q=80')" class="px-2.5 py-1.5 rounded-lg bg-slate-100 hover:bg-amber-100 border border-slate-200 text-[11px] font-bold text-slate-800 transition active:scale-95">
              🥔 देसी आलू (1 kg)
            </button>
            <button type="button" onclick="selectLooseItemChip('लाल प्याज़ (Red Onions)', 'Vegetables', '1 kg', 'https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb?w=500&q=80')" class="px-2.5 py-1.5 rounded-lg bg-slate-100 hover:bg-amber-100 border border-slate-200 text-[11px] font-bold text-slate-800 transition active:scale-95">
              🧅 लाल प्याज़ (1 kg)
            </button>
            <button type="button" onclick="selectLooseItemChip('खुली अरहर दाल (Loose Toor Dal)', 'Grocery', '1 kg', 'https://images.unsplash.com/photo-1585032226651-759b368d7246?w=500&q=80')" class="px-2.5 py-1.5 rounded-lg bg-slate-100 hover:bg-amber-100 border border-slate-200 text-[11px] font-bold text-slate-800 transition active:scale-95">
              🌾 अरहर दाल (1 kg)
            </button>
            <button type="button" onclick="selectLooseItemChip('देसी गाय का दूध (Fresh Cow Milk)', 'Dairy', '1 L', 'https://images.unsplash.com/photo-1550583724-b2692b85b150?w=500&q=80')" class="px-2.5 py-1.5 rounded-lg bg-slate-100 hover:bg-amber-100 border border-slate-200 text-[11px] font-bold text-slate-800 transition active:scale-95">
              🥛 ताज़ा दूध (1 L)
            </button>
            <button type="button" onclick="selectLooseItemChip('स्थानीय गुलाब जामुन (Gulab Jamun)', 'Sweets', '1 kg', 'https://images.unsplash.com/photo-1541781774459-bb2af2f05b55?w=500&q=80')" class="px-2.5 py-1.5 rounded-lg bg-slate-100 hover:bg-amber-100 border border-slate-200 text-[11px] font-bold text-slate-800 transition active:scale-95">
              🍬 देसी मिठाई (1 kg)
            </button>
          </div>
        </div>

        <!-- Item Name & Unit Inputs -->
        <div class="space-y-3">
          <div>
            <label class="block text-[11px] font-bold text-slate-700 mb-1">सामान का नाम / Item Name *</label>
            <input type="text" id="loose-item-name-input" placeholder="उदा. ताज़ा टमाटर या देसी घी" class="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-xs font-bold text-slate-900 placeholder-slate-400 focus:outline-none focus:border-amber-500">
          </div>
          <div class="grid grid-cols-2 gap-2">
            <div>
              <label class="block text-[11px] font-bold text-slate-700 mb-1">इकाई / Unit</label>
              <select id="loose-item-unit-input" class="w-full px-3 py-2.5 rounded-xl border border-slate-300 text-xs font-bold text-slate-800 bg-white">
                <option value="1 kg">1 kg (किलो)</option>
                <option value="500 g">500 g (आधा किलो)</option>
                <option value="250 g">250 g (पाव)</option>
                <option value="1 L">1 L (लीटर)</option>
                <option value="1 Packet">1 Packet (पैकेट)</option>
                <option value="1 Piece">1 Piece (पीस / नग)</option>
              </select>
            </div>
            <div>
              <label class="block text-[11px] font-bold text-slate-700 mb-1">श्रेणी / Category</label>
              <select id="loose-item-cat-input" class="w-full px-3 py-2.5 rounded-xl border border-slate-300 text-xs font-bold text-slate-800 bg-white">
                <option value="Vegetables">सब्ज़ियाँ / Vegetables</option>
                <option value="Grocery">किराना / Grocery</option>
                <option value="Dairy">डेयरी / Dairy</option>
                <option value="Sweets">मिठाई / Sweets</option>
                <option value="Snacks">नमकीन / Snacks</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Continue CTA -->
        <div class="pt-2">
          <button type="button" onclick="continueToPricingFromPhoto()" class="w-full py-3.5 bg-amber-600 hover:bg-amber-700 text-white font-bold rounded-xl text-xs shadow-md transition active:scale-95 flex items-center justify-center space-x-2 cursor-pointer min-h-[48px]">
            <span>मूल्य तय करें / Continue to Pricing</span>
            <i data-lucide="arrow-right" class="w-4 h-4"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- =================================================================== -->
    <!-- 3. MODAL: THE CUSTOM PRICING FORM (NO LOCKED SKUS) -->
    <!-- =================================================================== -->
    <div id="modal-custom-pricing" class="app-modal fixed inset-0 bg-black/75 backdrop-blur-xs z-50 flex items-end sm:items-center justify-center hidden p-0 sm:p-4">
      <div class="w-full max-w-md bg-white rounded-t-3xl sm:rounded-3xl p-5 shadow-2xl max-h-[92vh] overflow-y-auto space-y-4 text-left">
        <!-- Header -->
        <div class="flex items-center justify-between pb-3 border-b border-slate-100">
          <div class="flex items-center space-x-2">
            <div class="w-8 h-8 rounded-full bg-emerald-100 text-emerald-800 flex items-center justify-center">
              <i data-lucide="indian-rupee" class="w-4 h-4"></i>
            </div>
            <div>
              <h3 class="text-xs sm:text-sm font-extrabold text-slate-900">कीमत तय करें / Set Item Price</h3>
              <p class="text-[10px] text-slate-500">आपकी दुकान, आपकी कीमत (No Locked Prices)</p>
            </div>
          </div>
          <button type="button" onclick="closeCustomPricingModal()" class="w-8 h-8 rounded-full bg-slate-100 text-slate-600 hover:bg-slate-200 flex items-center justify-center transition">
            <i data-lucide="x" class="w-4 h-4"></i>
          </button>
        </div>

        <!-- Product Preview Card (100% UNLOCKED & EDITABLE) -->
        <div class="flex items-start space-x-3 p-3.5 bg-slate-50 rounded-2xl border border-slate-200 shadow-2xs">
          <div class="relative w-16 h-16 shrink-0">
            <img id="custom-pricing-preview-img" src="https://images.unsplash.com/photo-1509440159596-0249088772ff?w=500&q=80" alt="Product Thumbnail" class="w-16 h-16 rounded-xl object-cover border-2 border-emerald-500 shadow-xs">
            <button type="button" onclick="openPhotoCaptureModal()" class="absolute -bottom-1 -right-1 w-6 h-6 rounded-full bg-slate-900 text-white flex items-center justify-center shadow-xs text-[10px]" title="Change Photo">
              <i data-lucide="camera" class="w-3 h-3"></i>
            </button>
          </div>
          <div class="flex-1 min-w-0 space-y-1">
            <label class="block text-[10px] font-bold text-slate-500 uppercase tracking-wide">सामान का नाम (बदलाव संभव) / Item Name</label>
            <input type="text" id="custom-pricing-name" class="w-full px-2.5 py-1.5 rounded-lg border border-slate-300 text-xs font-bold text-slate-900 focus:outline-none focus:border-emerald-600 bg-white" placeholder="Item Name">
            <div class="flex items-center space-x-1.5 text-[10px] text-slate-500 font-semibold pt-0.5">
              <span id="custom-pricing-cat-tag" class="px-2 py-0.5 bg-slate-200 rounded-md">Grocery</span>
              <span id="custom-pricing-unit-tag" class="px-2 py-0.5 bg-slate-200 rounded-md">1 kg</span>
            </div>
          </div>
        </div>

        <input type="hidden" id="custom-pricing-id" value="">
        <input type="hidden" id="custom-pricing-brand" value="">
        <input type="hidden" id="custom-pricing-category" value="Grocery">
        <input type="hidden" id="custom-pricing-unit" value="1 kg">

        <!-- THE CUSTOM PRICING FORM: 2 Stacked Price Inputs -->
        <div class="p-4 bg-emerald-50/60 rounded-2xl border-2 border-emerald-300 space-y-3.5">
          <span class="text-xs font-extrabold text-emerald-950 block">मूल्य निर्धारण / Pricing Details</span>

          <!-- 1. MRP Input -->
          <div class="space-y-1">
            <label class="block text-xs font-bold text-slate-700">अधिकतम खुदरा मूल्य (MRP) *</label>
            <div class="relative">
              <span class="absolute left-3.5 top-3 text-sm font-bold text-slate-400">₹</span>
              <input type="number" id="custom-pricing-mrp" step="0.5" min="1" placeholder="उदा. 260" oninput="calculateCustomPricingDiscount()" class="w-full pl-8 pr-3.5 py-3 rounded-xl border-2 border-slate-300 bg-white text-sm font-bold text-slate-900 focus:outline-none focus:border-emerald-600 transition min-h-[48px]">
            </div>
          </div>

          <!-- 2. Your Selling Price Input -->
          <div class="space-y-1">
            <label class="block text-xs font-bold text-emerald-950">आपकी बिक्री कीमत (Your Selling Price) *</label>
            <div class="relative">
              <span class="absolute left-3.5 top-3 text-base font-extrabold text-emerald-700">₹</span>
              <input type="number" id="custom-pricing-price" step="0.5" min="1" placeholder="उदा. 240" oninput="calculateCustomPricingDiscount()" class="w-full pl-8 pr-3.5 py-3 rounded-xl border-2 border-emerald-500 bg-white text-base font-extrabold text-slate-900 focus:outline-none focus:ring-2 focus:ring-emerald-500 transition shadow-xs min-h-[48px]">
            </div>
          </div>

          <!-- Dynamic Discount Badge (Green "X% OFF") -->
          <div id="custom-pricing-discount-badge" class="p-2.5 bg-emerald-100/90 border border-emerald-300 rounded-xl text-emerald-900 font-extrabold text-xs flex items-center space-x-2">
            <i data-lucide="tag" class="w-4 h-4 text-emerald-700 shrink-0"></i>
            <span id="discount-badge-text">8% OFF (₹20 ग्राहक की बचत / Customer Savings)</span>
          </div>

          <!-- Stock & In-Stock Switch -->
          <div class="grid grid-cols-2 gap-3 pt-1">
            <div>
              <label class="block text-[11px] font-bold text-slate-700 mb-1">स्टॉक मात्रा / Stock *</label>
              <input type="number" id="custom-pricing-stock" min="1" value="25" placeholder="50" class="w-full px-3 py-2.5 rounded-xl border border-slate-300 text-xs font-bold text-slate-900 bg-white">
            </div>
            <div class="flex flex-col justify-end">
              <label class="flex items-center space-x-2 p-2 bg-white rounded-xl border border-slate-200 cursor-pointer">
                <input type="checkbox" id="custom-pricing-instock" checked class="w-4 h-4 text-emerald-600 rounded border-slate-300 focus:ring-emerald-500">
                <span class="text-[11px] font-bold text-slate-800">बिक्री चालू (In-Stock)</span>
              </label>
            </div>
          </div>
        </div>

        <!-- Submit CTA (Min 48px height) -->
        <div class="pt-2">
          <button type="button" id="btn-save-custom-priced-item" onclick="saveCustomPricedItem()" class="w-full py-4 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-2xl shadow-lg shadow-emerald-700/20 text-sm active:scale-98 transition flex items-center justify-center space-x-2 cursor-pointer min-h-[48px]">
            <i data-lucide="check-circle" class="w-5 h-5"></i>
            <span>दुकान में जोड़ें / Add to Live Store</span>
          </button>
        </div>
      </div>
    </div>\n\n    """
    content = content[:modal_start_idx] + new_modals + content[modal_end_idx:]
    with open('public_web/vendor/index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("SUCCESS: 2. Replaced old modal-add-product with multimodal modals!")
else:
    print("Failed to replace modals!")
