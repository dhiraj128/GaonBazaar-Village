with open('public_web/vendor/index.html', 'r', encoding='utf-8') as f:
    v = f.read()

# 1. FIX MICROPHONE CSS POSITIONING & ALIGNMENT
old_search_bar = '''        <!-- 1. The Smart Search Bar (Voice Integration) -->
        <div class="relative w-full">
          <i data-lucide="search" class="w-5 h-5 text-slate-400 absolute left-3.5 top-3.5 pointer-events-none"></i>
          <input type="text" id="inventory-search" oninput="filterInventory(this.value)" data-i18n-placeholder="search_inventory_placeholder" placeholder="Search or speak item (Potato, Tomato, Atta)..." class="w-full pl-11 pr-14 py-3.5 rounded-2xl border-2 border-slate-200 bg-white text-xs sm:text-sm font-semibold text-slate-800 placeholder-slate-400 focus:outline-none focus:border-emerald-600 focus:ring-2 focus:ring-emerald-100 shadow-sm transition">
          
          <!-- Voice Action Microphone Button (Min 48px touch target) -->
          <button type="button" id="btn-vendor-voice-search" onclick="toggleVendorVoiceSearch()" class="absolute right-1.5 top-1.5 w-10 h-10 rounded-xl bg-emerald-50 text-emerald-700 hover:bg-emerald-100 border border-emerald-200 flex items-center justify-center transition active:scale-90 shadow-2xs cursor-pointer" data-i18n-title="speak_to_search_title" title="Speak to Search">
            <i data-lucide="mic" id="vendor-mic-icon" class="w-5 h-5"></i>
          </button>
        </div>'''

new_search_bar = '''        <!-- 1. The Smart Search Bar (Voice Integration) -->
        <div class="relative w-full flex items-center">
          <i data-lucide="search" class="w-5 h-5 text-slate-400 absolute left-3.5 pointer-events-none"></i>
          <input type="text" id="inventory-search" oninput="filterInventory(this.value)" data-i18n-placeholder="search_inventory_placeholder" placeholder="Search or speak item (Potato, Tomato, Atta)..." class="w-full pl-11 pr-14 py-3.5 rounded-2xl border-2 border-slate-200 bg-white text-xs sm:text-sm font-semibold text-slate-800 placeholder-slate-400 focus:outline-none focus:border-emerald-600 focus:ring-2 focus:ring-emerald-100 shadow-sm transition">
          
          <!-- Voice Action Microphone Button (Perfect vertical & horizontal centering inside input right edge) -->
          <button type="button" id="btn-vendor-voice-search" onclick="toggleVendorVoiceSearch()" class="absolute right-2 top-1/2 -translate-y-1/2 w-9 h-9 rounded-xl bg-emerald-50 text-emerald-700 hover:bg-emerald-100 border border-emerald-200 flex items-center justify-center transition active:scale-90 shadow-2xs cursor-pointer" data-i18n-title="speak_to_search_title" title="Speak to Search">
            <i data-lucide="mic" id="vendor-mic-icon" class="w-4.5 h-4.5"></i>
          </button>
        </div>'''

if old_search_bar in v:
    v = v.replace(old_search_bar, new_search_bar, 1)
    print("Search bar and microphone positioning fixed.")
else:
    print("WARNING: old_search_bar not matched exact")

# 2. REMOVE REDUNDANT "+" SIGN IN "+ Type Item Name"
old_type_item_btn = '''          <button type="button" onclick="openCustomPricingModal({ title: '', mrp: 0, price: 0 })" class="text-emerald-700 hover:underline flex items-center space-x-1 cursor-pointer">
            <i data-lucide="plus" class="w-3.5 h-3.5"></i>
            <span data-i18n="type_item_name_btn">+ Type Item Name</span>
          </button>'''

new_type_item_btn = '''          <button type="button" onclick="openCustomPricingModal({ title: '', mrp: '', price: '', stock: '' })" class="text-emerald-700 hover:underline flex items-center space-x-1 cursor-pointer">
            <i data-lucide="plus" class="w-3.5 h-3.5"></i>
            <span data-i18n="type_item_name_btn">Type Item Name</span>
          </button>'''

if old_type_item_btn in v:
    v = v.replace(old_type_item_btn, new_type_item_btn, 1)
    print("Type item name button '+' duplication removed in HTML.")
else:
    print("WARNING: old_type_item_btn not matched exact")

# Fix in translations
v = v.replace('type_item_name_btn: "+ Type Item Name"', 'type_item_name_btn: "Type Item Name"')
v = v.replace('type_item_name_btn: "+ नया सामान टाइप करें"', 'type_item_name_btn: "सामान का नाम टाइप करें"')
print("Type item name translations updated.")

# 3. FIX PHOTO CAPTURE MODAL BUTTON (eliminate double event)
old_photo_label = '''          <label for="vendor-camera-file-input" onclick="triggerCameraCapture()" class="w-full py-3.5 bg-amber-600 hover:bg-amber-700 text-white font-bold rounded-xl text-xs shadow-md transition active:scale-95 flex items-center justify-center space-x-2 cursor-pointer min-h-[48px]">
            <i data-lucide="camera" class="w-4 h-4"></i>
            <span data-i18n="open_camera_btn">Open Camera & Snap Photo</span>
          </label>'''

new_photo_btn = '''          <button type="button" onclick="triggerCameraCapture()" class="w-full py-3.5 bg-amber-600 hover:bg-amber-700 text-white font-bold rounded-xl text-xs shadow-md transition active:scale-95 flex items-center justify-center space-x-2 cursor-pointer min-h-[48px]">
            <i data-lucide="camera" class="w-4 h-4"></i>
            <span data-i18n="open_camera_btn">Open Camera & Snap Photo</span>
          </button>'''

if old_photo_label in v:
    v = v.replace(old_photo_label, new_photo_btn, 1)
    print("Photo modal trigger button replaced cleanly.")

# 4. ENHANCE CUSTOM PRICING MODAL WITH REAL-TIME MASTER SKU PROACTIVE SUGGESTIONS
old_custom_pricing_name_div = '''          <div class="flex-1 min-w-0 space-y-1">
            <label class="block text-[10px] font-bold text-slate-500 uppercase tracking-wide" data-i18n="pricing_item_name_label">Item Name (Editable)</label>
            <input type="text" id="custom-pricing-name" class="w-full px-2.5 py-1.5 rounded-lg border border-slate-300 text-xs font-bold text-slate-900 focus:outline-none focus:border-emerald-600 bg-white" placeholder="Item Name">
            <div class="flex items-center space-x-1.5 text-[10px] text-slate-500 font-semibold pt-0.5">
              <span id="custom-pricing-cat-tag" class="px-2 py-0.5 bg-slate-200 rounded-md">Grocery</span>
              <span id="custom-pricing-unit-tag" class="px-2 py-0.5 bg-slate-200 rounded-md">1 kg</span>
            </div>
          </div>'''

new_custom_pricing_name_div = '''          <div class="flex-1 min-w-0 space-y-1">
            <label class="block text-[10px] font-bold text-slate-500 uppercase tracking-wide" data-i18n="pricing_item_name_label">Item Name (Editable)</label>
            <input type="text" id="custom-pricing-name" oninput="handleCustomPricingNameInput(this.value)" class="w-full px-2.5 py-1.5 rounded-lg border border-slate-300 text-xs font-bold text-slate-900 focus:outline-none focus:border-emerald-600 bg-white" placeholder="Item Name">
            <div class="flex items-center space-x-1.5 text-[10px] text-slate-500 font-semibold pt-0.5">
              <span id="custom-pricing-cat-tag" class="px-2 py-0.5 bg-slate-200 rounded-md">Grocery</span>
              <span id="custom-pricing-unit-tag" class="px-2 py-0.5 bg-slate-200 rounded-md">1 kg</span>
            </div>
            <!-- Proactive Master SKU Image Suggestion Banner -->
            <div id="custom-pricing-sku-suggestion" class="hidden text-[10px] text-emerald-800 bg-emerald-50 border border-emerald-200 rounded-lg p-1.5 flex items-center justify-between mt-1">
              <div class="flex items-center space-x-1 truncate">
                <i data-lucide="sparkles" class="w-3 h-3 text-emerald-600 shrink-0"></i>
                <span id="sku-suggestion-text" class="truncate font-semibold">Matched Master SKU image loaded</span>
              </div>
            </div>
          </div>'''

if old_custom_pricing_name_div in v:
    v = v.replace(old_custom_pricing_name_div, new_custom_pricing_name_div, 1)
    print("Custom pricing input with proactive suggestion banner added.")

# 5. DEFINE MASTER SKU SUGGESTION & ENHANCED JS FUNCTIONS
master_sku_helper_code = '''
    // MASTER SKU PROACTIVE IMAGE MAPPING ENGINE
    const MASTER_STAPLE_MAP = {
      'atta': {
        title: 'Aashirvaad Shudh Chakki Atta',
        brand: 'Aashirvaad',
        category: 'Grocery',
        unit: '5 kg',
        image_url: 'https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=600&q=80'
      },
      'flour': {
        title: 'Wheat Flour (Atta)',
        brand: 'Chakki Fresh',
        category: 'Grocery',
        unit: '5 kg',
        image_url: 'https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=600&q=80'
      },
      'milk': {
        title: 'Amul Taaza Fresh Toned Milk',
        brand: 'Amul',
        category: 'Dairy',
        unit: '1 L',
        image_url: 'https://images.unsplash.com/photo-1550583724-b2692b85b150?w=600&q=80'
      },
      'doodh': {
        title: 'Amul Taaza Fresh Toned Milk',
        brand: 'Amul',
        category: 'Dairy',
        unit: '1 L',
        image_url: 'https://images.unsplash.com/photo-1550583724-b2692b85b150?w=600&q=80'
      },
      'salt': {
        title: 'Tata Salt Vacuum Evaporated',
        brand: 'Tata',
        category: 'Grocery',
        unit: '1 kg',
        image_url: 'https://images.unsplash.com/photo-1518110925495-5fe2fda0442c?w=500&q=80'
      },
      'namak': {
        title: 'Tata Salt Vacuum Evaporated',
        brand: 'Tata',
        category: 'Grocery',
        unit: '1 kg',
        image_url: 'https://images.unsplash.com/photo-1518110925495-5fe2fda0442c?w=500&q=80'
      },
      'oil': {
        title: 'Fortune Kachi Ghani Mustard Oil',
        brand: 'Fortune',
        category: 'Grocery',
        unit: '1 L',
        image_url: 'https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=500&q=80'
      },
      'tel': {
        title: 'Fortune Kachi Ghani Mustard Oil',
        brand: 'Fortune',
        category: 'Grocery',
        unit: '1 L',
        image_url: 'https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=500&q=80'
      },
      'sugar': {
        title: 'Madhur Pure & Hygienic Sugar',
        brand: 'Madhur',
        category: 'Grocery',
        unit: '1 kg',
        image_url: 'https://images.unsplash.com/photo-1581441363689-1f3c3c414635?w=600&q=80'
      },
      'cheeni': {
        title: 'Madhur Pure & Hygienic Sugar',
        brand: 'Madhur',
        category: 'Grocery',
        unit: '1 kg',
        image_url: 'https://images.unsplash.com/photo-1581441363689-1f3c3c414635?w=600&q=80'
      },
      'rice': {
        title: 'India Gate Basmati Rice Feast Rozzana',
        brand: 'India Gate',
        category: 'Grocery',
        unit: '1 kg',
        image_url: 'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=600&q=80'
      },
      'chawal': {
        title: 'India Gate Basmati Rice Feast Rozzana',
        brand: 'India Gate',
        category: 'Grocery',
        unit: '1 kg',
        image_url: 'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=600&q=80'
      },
      'dal': {
        title: 'Tata Sampann Unpolished Toor Dal',
        brand: 'Tata Sampann',
        category: 'Grocery',
        unit: '1 kg',
        image_url: 'https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=600&q=80'
      },
      'tea': {
        title: 'Tata Tea Gold Leaf Tea',
        brand: 'Tata Tea',
        category: 'Beverages',
        unit: '250 g',
        image_url: 'https://images.unsplash.com/photo-1576092768241-dec231879fc3?w=600&q=80'
      },
      'chai': {
        title: 'Tata Tea Gold Leaf Tea',
        brand: 'Tata Tea',
        category: 'Beverages',
        unit: '250 g',
        image_url: 'https://images.unsplash.com/photo-1576092768241-dec231879fc3?w=600&q=80'
      },
      'biscuit': {
        title: 'Parle-G Gold Glucose Biscuits',
        brand: 'Parle',
        category: 'Snacks',
        unit: '250 g',
        image_url: 'https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=500&q=80'
      },
      'maggi': {
        title: 'Maggi 2-Minute Masala Instant Noodles',
        brand: 'Nestle',
        category: 'Snacks',
        unit: '280 g',
        image_url: 'https://images.unsplash.com/photo-1612927601601-6638404737ce?w=500&q=80'
      },
      'tomato': {
        title: 'Fresh Desi Tomato (ताज़ा टमाटर)',
        brand: 'Farm Fresh',
        category: 'Vegetables',
        unit: '1 kg',
        image_url: 'https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=600&q=80'
      },
      'tamatar': {
        title: 'Fresh Desi Tomato (ताज़ा टमाटर)',
        brand: 'Farm Fresh',
        category: 'Vegetables',
        unit: '1 kg',
        image_url: 'https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=600&q=80'
      },
      'potato': {
        title: 'Fresh Pahadi Potato (ताज़ा आलू)',
        brand: 'Farm Fresh',
        category: 'Vegetables',
        unit: '1 kg',
        image_url: 'https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=600&q=80'
      },
      'aalu': {
        title: 'Fresh Pahadi Potato (ताज़ा आलू)',
        brand: 'Farm Fresh',
        category: 'Vegetables',
        unit: '1 kg',
        image_url: 'https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=600&q=80'
      },
      'onion': {
        title: 'Fresh Red Onion (ताज़ा प्याज)',
        brand: 'Farm Fresh',
        category: 'Vegetables',
        unit: '1 kg',
        image_url: 'https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb?w=600&q=80'
      },
      'pyaj': {
        title: 'Fresh Red Onion (ताज़ा प्याज)',
        brand: 'Farm Fresh',
        category: 'Vegetables',
        unit: '1 kg',
        image_url: 'https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb?w=600&q=80'
      },
      'ghee': {
        title: 'Amul Pure Buffalo / Cow Ghee',
        brand: 'Amul',
        category: 'Dairy',
        unit: '1 L',
        image_url: 'https://images.unsplash.com/photo-1628088062854-d1870b4553da?w=600&q=80'
      },
      'soap': {
        title: 'Dettol Original Bathing Soap Bar',
        brand: 'Dettol',
        category: 'Personal Care',
        unit: '125 g',
        image_url: 'https://images.unsplash.com/photo-1607006314188-755a5b5123d5?w=600&q=80'
      }
    };

    function findMasterSkuSuggestion(query) {
      if (!query || typeof query !== 'string') return null;
      const q = query.trim().toLowerCase();
      if (!q) return null;

      // 1. Check keyword staple dictionary
      for (const [key, val] of Object.entries(MASTER_STAPLE_MAP)) {
        if (q.includes(key) || key.includes(q)) {
          return val;
        }
      }

      // 2. Check MASTER_SKU_DATABASE array
      const skus = (window.MASTER_SKU_DATABASE && Array.isArray(window.MASTER_SKU_DATABASE)) 
        ? window.MASTER_SKU_DATABASE 
        : (typeof MASTER_SKU_DATABASE !== 'undefined' ? MASTER_SKU_DATABASE : []);

      let match = skus.find(s => {
        const nameEn = (s.product_name || s.name || '').toLowerCase();
        const nameHi = (s.product_name_hi || '').toLowerCase();
        const brand = (s.brand || '').toLowerCase();
        return nameEn.includes(q) || nameHi.includes(q) || (brand && q.includes(brand));
      });

      if (match) {
        return {
          title: match.product_name,
          brand: match.brand,
          category: match.category,
          unit: match.variant || match.unit || '1 kg',
          image_url: match.image_url || match.image || match.img
        };
      }

      return null;
    }
    window.findMasterSkuSuggestion = findMasterSkuSuggestion;

    function handleCustomPricingNameInput(name) {
      if (!name || name.trim().length < 2) {
        const suggBanner = document.getElementById('custom-pricing-sku-suggestion');
        if (suggBanner) suggBanner.classList.add('hidden');
        return;
      }
      const match = findMasterSkuSuggestion(name);
      const previewImg = document.getElementById('custom-pricing-preview-img');
      const catTag = document.getElementById('custom-pricing-cat-tag');
      const unitTag = document.getElementById('custom-pricing-unit-tag');
      const suggBanner = document.getElementById('custom-pricing-sku-suggestion');
      const suggText = document.getElementById('sku-suggestion-text');

      if (match && match.image_url) {
        if (previewImg) previewImg.src = match.image_url;
        if (catTag && match.category) catTag.innerText = match.category;
        if (unitTag && match.unit) unitTag.innerText = match.unit;
        currentCustomPricingImg = match.image_url;

        if (suggBanner && suggText) {
          suggBanner.classList.remove('hidden');
          suggText.innerText = (typeof currentLang !== 'undefined' && currentLang === 'hi') 
            ? `मास्टर SKU छवि: ${match.title || name}` 
            : `Master SKU: ${match.title || name}`;
          if (window.lucide) lucide.createIcons();
        }
      } else if (suggBanner) {
        suggBanner.classList.add('hidden');
      }
    }
    window.handleCustomPricingNameInput = handleCustomPricingNameInput;
'''

# 6. REPLACE openCustomPricingModal WITH MASTER SKU INTEGRATION
old_open_custom_pricing = '''    function openCustomPricingModal(itemData = {}) {
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
    }'''

new_open_custom_pricing = '''    function openCustomPricingModal(itemData = {}) {
      const name = itemData.title || itemData.name || itemData.product_name || "";
      const mrp = itemData.mrp !== undefined && itemData.mrp !== null ? String(itemData.mrp).trim() : "";
      const price = itemData.price !== undefined && itemData.price !== null ? String(itemData.price).trim() : "";
      const stock = itemData.stock !== undefined && itemData.stock !== null ? String(itemData.stock).trim() : "";
      let cat = itemData.category || "Grocery";
      let unit = itemData.unit || itemData.variant || "1 unit";
      let img = itemData.img || itemData.image_url || "";

      // PROACTIVE MASTER SKU LOOKUP
      const match = findMasterSkuSuggestion(name);
      if (match) {
        if (!img || img.includes('photo-1574323347407-f5e1ad6d020b')) {
          img = match.image_url;
        }
        if (cat === "Grocery" && match.category) cat = match.category;
        if (unit === "1 unit" && match.unit) unit = match.unit;
      }

      if (!img) {
        img = "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=600&q=80";
      }

      currentCustomPricingImg = img;

      const nameInp = document.getElementById('custom-pricing-name');
      const mrpInp = document.getElementById('custom-pricing-mrp');
      const priceInp = document.getElementById('custom-pricing-price');
      const stockInp = document.getElementById('custom-pricing-stock');
      const instockInp = document.getElementById('custom-pricing-instock');
      const previewImg = document.getElementById('custom-pricing-preview-img');
      const catTag = document.getElementById('custom-pricing-cat-tag');
      const unitTag = document.getElementById('custom-pricing-unit-tag');
      const suggBanner = document.getElementById('custom-pricing-sku-suggestion');
      const suggText = document.getElementById('sku-suggestion-text');

      if (nameInp) nameInp.value = name;
      // STRICT DECOUPLING: MRP, Selling Price, and Stock are left completely blank for the vendor to manually enter
      if (mrpInp) mrpInp.value = mrp ? mrp : '';
      if (priceInp) priceInp.value = price ? price : '';
      if (stockInp) stockInp.value = stock ? stock : '';
      if (instockInp) instockInp.checked = true;
      if (previewImg) previewImg.src = img;
      if (catTag) catTag.innerText = cat;
      if (unitTag) unitTag.innerText = unit;

      if (match && suggBanner && suggText) {
        suggBanner.classList.remove('hidden');
        suggText.innerText = (typeof currentLang !== 'undefined' && currentLang === 'hi') 
          ? `मास्टर SKU छवि: ${match.title || name}` 
          : `Master SKU: ${match.title || name}`;
      } else if (suggBanner) {
        suggBanner.classList.add('hidden');
      }

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
    }'''

if old_open_custom_pricing in v:
    v = v.replace(old_open_custom_pricing, master_sku_helper_code + '\n' + new_open_custom_pricing, 1)
    print("openCustomPricingModal updated with proactive Master SKU engine.")
else:
    print("WARNING: old_open_custom_pricing not matched exact")

# 7. UPDATE triggerCameraCapture TO RESET INPUT VALUE
old_trigger_cam = '''    function triggerCameraCapture() {
      const input = document.getElementById('vendor-camera-file-input');
      if (input) input.click();
    }'''

new_trigger_cam = '''    function triggerCameraCapture() {
      const input = document.getElementById('vendor-camera-file-input');
      if (input) {
        input.value = '';
        input.click();
      }
    }'''

if old_trigger_cam in v:
    v = v.replace(old_trigger_cam, new_trigger_cam, 1)
    print("triggerCameraCapture reset behavior updated.")

# 8. UPDATE filterInventory EMPTY STATE BUTTON TO PASS SUGGESTED SKU IMAGE
old_filter_inv_btn = '''            <button type="button" onclick="openCustomPricingModal({ title: '${query.replace(/'/g, "\\'")}', mrp: '', price: '', stock: '' })" class="w-full sm:w-auto px-5 py-3 min-h-[48px] bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-xl text-xs transition shadow-sm active:scale-98 inline-flex items-center justify-center space-x-2 cursor-pointer">'''

new_filter_inv_btn = '''            <button type="button" onclick="const s = findMasterSkuSuggestion('${query.replace(/'/g, "\\\\'")}'); openCustomPricingModal(s ? { title: s.title, category: s.category, unit: s.unit, img: s.image_url, mrp: '', price: '', stock: '' } : { title: '${query.replace(/'/g, "\\\\'")}', mrp: '', price: '', stock: '' })" class="w-full sm:w-auto px-5 py-3 min-h-[48px] bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-xl text-xs transition shadow-sm active:scale-98 inline-flex items-center justify-center space-x-2 cursor-pointer">'''

if old_filter_inv_btn in v:
    v = v.replace(old_filter_inv_btn, new_filter_inv_btn, 1)
    print("filterInventory empty state updated with SKU suggestion.")

with open('public_web/vendor/index.html', 'w', encoding='utf-8') as f:
    f.write(v)

print("public_web/vendor/index.html updated successfully!")
