with open('public_web/vendor/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# We will locate `// Bulk Import (CSV)` or `function openAddProductModal` and insert our comprehensive controller
target_js = """    function openAddProductModal() {
      const searchInput = document.getElementById('catalog-library-search');
      if (searchInput) searchInput.value = "";
      renderMasterCatalog("");
      const placeholder = document.getElementById('no-sku-selected-placeholder');
      const formFields = document.getElementById('sku-form-fields');
      if (placeholder) placeholder.classList.remove('hidden');
      if (formFields) formFields.classList.add('hidden');
      recalculateDiscount();
      openModal('modal-add-product');
    }"""

new_controller_code = """    // =========================================================================
    // MULTIMODAL INVENTORY CONTROLLER: VOICE, BARCODE & REAL CAMERA PHOTO
    // =========================================================================
    var vendorSpeechRecognizer = null;
    var isVendorListening = false;
    var currentCustomPricingImg = "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=500&q=80";

    // 1. SMART SEARCH BAR (VOICE INTEGRATION VIA WEB SPEECH API)
    function toggleVendorVoiceSearch() {
      const searchInput = document.getElementById('inventory-search');
      const micBtn = document.getElementById('btn-vendor-voice-search');
      const micIcon = document.getElementById('vendor-mic-icon');
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

      if (!SpeechRecognition) {
        toastWarning(currentLang === 'hi' 
          ? "इस ब्राउज़र में आवाज़ पहचान समर्थित नहीं है, कृपया टाइप करें।" 
          : "Voice recognition not supported in this browser. Please type to search.");
        if (searchInput) searchInput.focus();
        return;
      }

      if (isVendorListening) {
        stopVendorVoiceSearch();
        return;
      }

      try {
        if (vendorSpeechRecognizer) vendorSpeechRecognizer.abort();
        vendorSpeechRecognizer = new SpeechRecognition();
        vendorSpeechRecognizer.lang = currentLang === 'hi' ? 'hi-IN' : 'en-IN';
        vendorSpeechRecognizer.interimResults = false;
        vendorSpeechRecognizer.maxAlternatives = 1;

        isVendorListening = true;
        if (micBtn) {
          micBtn.classList.add('bg-rose-100', 'text-rose-700', 'border-rose-400', 'animate-pulse');
          micBtn.classList.remove('bg-emerald-50', 'text-emerald-700', 'border-emerald-200');
        }
        toastInfo(currentLang === 'hi' ? "सुन रहे हैं... सामान का नाम बोलिए (उदा. टमाटर, आटा)!" : "Listening... Speak item name (e.g. Tomato, Atta)!");

        vendorSpeechRecognizer.onresult = function(e) {
          const transcript = e.results[0][0].transcript.trim();
          stopVendorVoiceSearch();

          if (searchInput) {
            searchInput.value = transcript;
            filterInventory(transcript);
          }

          toastSuccess(currentLang === 'hi' ? `पहचाना गया: "${transcript}"` : `Voice recognized: "${transcript}"`);

          // Check if zero items matched in active inventory, auto-fill into Custom Pricing Form
          const activeCards = Array.from(document.querySelectorAll('#inventory-list .product-item:not(.hidden)'));
          if (activeCards.length === 0) {
            // Check if matches in master catalog
            const skus = (window.MASTER_SKU_DATABASE && Array.isArray(window.MASTER_SKU_DATABASE)) ? window.MASTER_SKU_DATABASE : MASTER_SKU_DATABASE;
            const match = skus.find(s => s.product_name.toLowerCase().includes(transcript.toLowerCase()) || (s.brand || '').toLowerCase().includes(transcript.toLowerCase()));
            if (match) {
              openCustomPricingModal({
                title: match.product_name,
                brand: match.brand,
                category: match.category,
                unit: match.variant || match.unit,
                mrp: match.mrp,
                price: match.suggested_price || match.mrp,
                img: match.image_url
              });
            } else {
              openCustomPricingModal({
                title: transcript,
                brand: "",
                category: "Grocery",
                unit: "1 kg",
                mrp: 50,
                price: 45,
                img: "https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=500&q=80"
              });
            }
          }
        };

        vendorSpeechRecognizer.onerror = function(err) {
          console.warn("Vendor voice error:", err);
          stopVendorVoiceSearch();
          toastWarning(currentLang === 'hi' ? "आवाज़ नहीं सुनी गई, कृपया दोबारा बोलें या टाइप करें।" : "Speech not detected. Please speak clearly or type.");
        };

        vendorSpeechRecognizer.onend = function() {
          stopVendorVoiceSearch();
        };

        vendorSpeechRecognizer.start();
      } catch (err) {
        console.error("Speech start error:", err);
        stopVendorVoiceSearch();
      }
    }
    window.toggleVendorVoiceSearch = toggleVendorVoiceSearch;

    function stopVendorVoiceSearch() {
      isVendorListening = false;
      const micBtn = document.getElementById('btn-vendor-voice-search');
      if (micBtn) {
        micBtn.classList.remove('bg-rose-100', 'text-rose-700', 'border-rose-400', 'animate-pulse');
        micBtn.classList.add('bg-emerald-50', 'text-emerald-700', 'border-emerald-200');
      }
      if (vendorSpeechRecognizer) {
        try { vendorSpeechRecognizer.stop(); } catch(e) {}
      }
    }

    // 2. THE SPLIT ACTION 1: HTML5 BARCODE SCANNER (PACKAGED FMCG GOODS)
    var barcodeStream = null;

    const FMCG_BARCODE_LOOKUP = {
      "8901030383701": {
        title: "Aashirvaad Shudh Chakki Atta (5 kg)",
        brand: "Aashirvaad",
        category: "Grocery",
        unit: "5 kg",
        mrp: 260.0,
        price: 240.0,
        img: "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=500&q=80"
      },
      "8901262010053": {
        title: "Tata Salt Vacuum Evaporated (1 kg)",
        brand: "Tata",
        category: "Grocery",
        unit: "1 kg",
        mrp: 28.0,
        price: 26.0,
        img: "https://images.unsplash.com/photo-1518110925495-5fe2fda0442c?w=500&q=80"
      },
      "8901491101836": {
        title: "Fortune Kachi Ghani Mustard Oil (1 L)",
        brand: "Fortune",
        category: "Grocery",
        unit: "1 L",
        mrp: 165.0,
        price: 145.0,
        img: "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=500&q=80"
      },
      "8901063012111": {
        title: "Britannia Good Day Butter Cookies (200 g)",
        brand: "Britannia",
        category: "Snacks",
        unit: "200 g",
        mrp: 45.0,
        price: 40.0,
        img: "https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=500&q=80"
      },
      "8901725181221": {
        title: "Maggi 2-Minute Masala Noodles (280 g)",
        brand: "Nestle",
        category: "Snacks",
        unit: "280 g",
        mrp: 56.0,
        price: 52.0,
        img: "https://images.unsplash.com/photo-1612927601601-6638404737ce?w=500&q=80"
      },
      "8901030000000": {
        title: "Parle-G Gold Glucose Biscuits (250 g)",
        brand: "Parle",
        category: "Snacks",
        unit: "250 g",
        mrp: 30.0,
        price: 28.0,
        img: "https://images.unsplash.com/photo-1590080875515-8a3a8dc5735e?w=500&q=80"
      }
    };

    function openBarcodeScannerModal() {
      const modal = document.getElementById('modal-barcode-scanner');
      if (modal) {
        modal.classList.remove('hidden');
        modal.classList.add('flex');
      }
      startBarcodeCamera();
    }
    window.openBarcodeScannerModal = openBarcodeScannerModal;

    function closeBarcodeScannerModal() {
      stopBarcodeCamera();
      const modal = document.getElementById('modal-barcode-scanner');
      if (modal) {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
      }
    }
    window.closeBarcodeScannerModal = closeBarcodeScannerModal;

    async function startBarcodeCamera() {
      const video = document.getElementById('barcode-scanner-video');
      const statusEl = document.getElementById('barcode-scanner-status');
      if (!video) return;

      if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        try {
          barcodeStream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: 'environment', width: { ideal: 640 }, height: { ideal: 480 } }
          });
          video.srcObject = barcodeStream;
          video.classList.remove('hidden');
          if (statusEl) statusEl.innerText = currentLang === 'hi' ? "कैमरा चालू • बारकोड सामने लाएं" : "Camera Active • Align Barcode";
        } catch (err) {
          console.warn("Camera access fallback:", err.message);
          if (statusEl) statusEl.innerText = currentLang === 'hi' ? "कैमरा अनुकरण • नीचे दिए गए बारकोड पर टैप करें" : "Scanner Ready • Tap sample barcodes below";
        }
      }
    }

    function stopBarcodeCamera() {
      if (barcodeStream) {
        barcodeStream.getTracks().forEach(t => t.stop());
        barcodeStream = null;
      }
      const video = document.getElementById('barcode-scanner-video');
      if (video) video.classList.add('hidden');
    }

    function handleBarcodeDetected(barcode) {
      closeBarcodeScannerModal();
      const code = String(barcode).trim();
      
      // Check FMCG Barcode Database
      let item = FMCG_BARCODE_LOOKUP[code];
      if (!item) {
        // Fallback: match in MASTER_SKU_DATABASE
        const skus = (window.MASTER_SKU_DATABASE && Array.isArray(window.MASTER_SKU_DATABASE)) ? window.MASTER_SKU_DATABASE : MASTER_SKU_DATABASE;
        const matchedSku = skus.find(s => (s.id || '').includes(code) || (s.product_name || '').toLowerCase().includes(code.toLowerCase()));
        if (matchedSku) {
          item = {
            title: matchedSku.product_name,
            brand: matchedSku.brand,
            category: matchedSku.category,
            unit: matchedSku.variant || matchedSku.unit,
            mrp: matchedSku.mrp,
            price: matchedSku.suggested_price || matchedSku.mrp,
            img: matchedSku.image_url
          };
        } else {
          item = {
            title: `Packaged FMCG Product (${code.slice(-6)})`,
            brand: "FMCG Brand",
            category: "Grocery",
            unit: "1 unit",
            mrp: 100.0,
            price: 90.0,
            img: "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=500&q=80"
          };
        }
      }

      toastSuccess(currentLang === 'hi' ? `बारकोड मिला: ${item.title}` : `Barcode matched: ${item.title}`);
      openCustomPricingModal(item);
    }
    window.handleBarcodeDetected = handleBarcodeDetected;

    function submitManualBarcode() {
      const inp = document.getElementById('manual-barcode-input');
      const val = (inp ? inp.value : '').trim();
      if (!val) {
        toastError(currentLang === 'hi' ? "कृपया बारकोड नंबर दर्ज करें।" : "Please enter a barcode number.");
        return;
      }
      handleBarcodeDetected(val);
    }
    window.submitManualBarcode = submitManualBarcode;

    // 3. THE SPLIT ACTION 2: REAL CAMERA PHOTO CAPTURE (LOOSE & FRESH ITEMS)
    var currentSnappedPhotoData = null;

    function openPhotoCaptureModal() {
      const modal = document.getElementById('modal-take-photo');
      if (modal) {
        modal.classList.remove('hidden');
        modal.classList.add('flex');
      }
      if (window.lucide) lucide.createIcons();
    }
    window.openPhotoCaptureModal = openPhotoCaptureModal;

    function closePhotoCaptureModal() {
      const modal = document.getElementById('modal-take-photo');
      if (modal) {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
      }
    }
    window.closePhotoCaptureModal = closePhotoCaptureModal;

    function triggerCameraCapture() {
      const input = document.getElementById('vendor-camera-file-input');
      if (input) input.click();
    }
    window.triggerCameraCapture = triggerCameraCapture;

    function handleVendorCameraPhoto(event) {
      const file = event.target.files && event.target.files[0];
      if (!file) return;

      const reader = new FileReader();
      reader.onload = function(e) {
        currentSnappedPhotoData = e.target.result;
        const previewContainer = document.getElementById('photo-preview-container');
        const previewImg = document.getElementById('photo-preview-image');
        const placeholderIcon = document.getElementById('photo-placeholder-icon');
        const statusText = document.getElementById('photo-status-text');

        if (previewImg && previewContainer) {
          previewImg.src = currentSnappedPhotoData;
          previewContainer.classList.remove('hidden');
          if (placeholderIcon) placeholderIcon.classList.add('hidden');
          if (statusText) statusText.innerText = currentLang === 'hi' ? "✓ असली फोटो तैयार है! अब नाम व मूल्य तय करें।" : "✓ Photo captured! Set item name and pricing.";
        }
        toastSuccess(currentLang === 'hi' ? "फोटो सफलतापूर्वक ली गई!" : "Photo captured successfully!");
      };
      reader.readAsDataURL(file);
    }
    window.handleVendorCameraPhoto = handleVendorCameraPhoto;

    function selectLooseItemChip(name, category, unit, defaultImg) {
      const nameInp = document.getElementById('loose-item-name-input');
      const unitInp = document.getElementById('loose-item-unit-input');
      const catInp = document.getElementById('loose-item-cat-input');
      if (nameInp) nameInp.value = name;
      if (unitInp) unitInp.value = unit;
      if (catInp) catInp.value = category;

      if (!currentSnappedPhotoData && defaultImg) {
        currentSnappedPhotoData = defaultImg;
        const previewContainer = document.getElementById('photo-preview-container');
        const previewImg = document.getElementById('photo-preview-image');
        const placeholderIcon = document.getElementById('photo-placeholder-icon');
        if (previewImg && previewContainer) {
          previewImg.src = defaultImg;
          previewContainer.classList.remove('hidden');
          if (placeholderIcon) placeholderIcon.classList.add('hidden');
        }
      }
    }
    window.selectLooseItemChip = selectLooseItemChip;

    function continueToPricingFromPhoto() {
      const name = (document.getElementById('loose-item-name-input')?.value || '').trim();
      const unit = document.getElementById('loose-item-unit-input')?.value || '1 kg';
      const cat = document.getElementById('loose-item-cat-input')?.value || 'Vegetables';

      if (!name) {
        toastError(currentLang === 'hi' ? "कृपया सामान का नाम दर्ज करें।" : "Please enter the item name.");
        document.getElementById('loose-item-name-input')?.focus();
        return;
      }

      closePhotoCaptureModal();
      openCustomPricingModal({
        title: name,
        category: cat,
        unit: unit,
        mrp: 40.0,
        price: 35.0,
        img: currentSnappedPhotoData || "https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=500&q=80"
      });
    }
    window.continueToPricingFromPhoto = continueToPricingFromPhoto;

    // 4. THE CUSTOM PRICING FORM (NO LOCKED SKUS, MRP & SELLING PRICE)
    function openCustomPricingModal(itemData = {}) {
      const name = itemData.title || itemData.name || itemData.product_name || "";
      const mrp = Number(itemData.mrp) || 0;
      const price = Number(itemData.price) || Number(itemData.suggested_price) || mrp;
      const cat = itemData.category || "Grocery";
      const unit = itemData.unit || itemData.variant || "1 unit";
      const img = itemData.img || itemData.image_url || "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=500&q=80";

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
      if (mrpInp) mrpInp.value = mrp > 0 ? mrp : (price > 0 ? price : 50);
      if (priceInp) priceInp.value = price > 0 ? price : 45;
      if (stockInp) stockInp.value = 25;
      if (instockInp) instockInp.checked = true;
      if (previewImg) previewImg.src = img;
      if (catTag) catTag.innerText = cat;
      if (unitTag) unitTag.innerText = unit;

      const catHidden = document.getElementById('custom-pricing-category');
      const unitHidden = document.getElementById('custom-pricing-unit');
      const brandHidden = document.getElementById('custom-pricing-brand');
      if (catHidden) catHidden.value = cat;
      if (unitHidden) unitHidden.value = unit;
      if (brandHidden) brandHidden.value = itemData.brand || "";

      calculateCustomPricingDiscount();

      const modal = document.getElementById('modal-custom-pricing');
      if (modal) {
        modal.classList.remove('hidden');
        modal.classList.add('flex');
      }
      if (window.lucide) lucide.createIcons();
    }
    window.openCustomPricingModal = openCustomPricingModal;

    function closeCustomPricingModal() {
      const modal = document.getElementById('modal-custom-pricing');
      if (modal) {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
      }
    }
    window.closeCustomPricingModal = closeCustomPricingModal;

    // Backward compatibility alias for openAddProductModal
    function openAddProductModal() {
      openCustomPricingModal({
        title: "",
        category: "Grocery",
        unit: "1 kg",
        mrp: 60.0,
        price: 54.0,
        img: "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=500&q=80"
      });
    }
    window.openAddProductModal = openAddProductModal;

    function calculateCustomPricingDiscount() {
      const mrp = parseFloat(document.getElementById('custom-pricing-mrp')?.value) || 0;
      const price = parseFloat(document.getElementById('custom-pricing-price')?.value) || 0;
      const badge = document.getElementById('custom-pricing-discount-badge');
      const badgeText = document.getElementById('discount-badge-text');

      if (!badge || !badgeText) return;

      if (mrp > 0 && price > 0 && mrp > price) {
        const discountPct = Math.round(((mrp - price) / mrp) * 100);
        const savings = (mrp - price).toFixed(0);
        badgeText.innerText = `${discountPct}% OFF (₹${savings} ग्राहक की बचत / Customer Savings)`;
        badge.className = "p-2.5 bg-emerald-100 border border-emerald-300 rounded-xl text-emerald-900 font-extrabold text-xs flex items-center space-x-2";
      } else if (mrp > 0 && price >= mrp) {
        badgeText.innerText = "MRP पर बिक्री (0% छूट) / Selling at MRP";
        badge.className = "p-2.5 bg-slate-100 border border-slate-300 rounded-xl text-slate-700 font-bold text-xs flex items-center space-x-2";
      } else {
        badgeText.innerText = "कीमत दर्ज करें / Enter valid prices";
        badge.className = "p-2.5 bg-slate-100 border border-slate-200 rounded-xl text-slate-500 font-bold text-xs flex items-center space-x-2";
      }
    }
    window.calculateCustomPricingDiscount = calculateCustomPricingDiscount;

    function saveCustomPricedItem() {
      const name = (document.getElementById('custom-pricing-name')?.value || '').trim();
      const mrp = parseFloat(document.getElementById('custom-pricing-mrp')?.value) || 0;
      const price = parseFloat(document.getElementById('custom-pricing-price')?.value) || 0;
      const stock = parseInt(document.getElementById('custom-pricing-stock')?.value, 10) || 25;
      const inStock = document.getElementById('custom-pricing-instock')?.checked !== false;
      const cat = document.getElementById('custom-pricing-category')?.value || 'Grocery';
      const unit = document.getElementById('custom-pricing-unit')?.value || '1 unit';
      const brand = document.getElementById('custom-pricing-brand')?.value || '';

      if (!name) {
        toastError(currentLang === 'hi' ? "कृपया सामान का नाम दर्ज करें।" : "Please enter the item name.");
        document.getElementById('custom-pricing-name')?.focus();
        return;
      }
      if (price <= 0) {
        toastError(currentLang === 'hi' ? "कृपया वैध बिक्री मूल्य दर्ज करें (> ₹0)।" : "Please enter a valid selling price (> ₹0).");
        document.getElementById('custom-pricing-price')?.focus();
        return;
      }

      const effectiveMrp = mrp > 0 ? mrp : price;
      const discountPct = effectiveMrp > price ? Math.round(((effectiveMrp - price) / effectiveMrp) * 100) : 0;
      const prodId = 'prod_' + Date.now().toString(36) + '_' + Math.random().toString(36).substr(2, 4);

      const newItem = {
        id: prodId,
        title: name,
        name: name,
        brand: brand,
        category: cat,
        variant: unit,
        unit: unit,
        mrp: effectiveMrp,
        price: price,
        discount_pct: discountPct,
        stock: stock,
        in_stock: inStock,
        img: currentCustomPricingImg || "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=500&q=80"
      };

      let inventory = getVendorInventory();
      inventory.unshift(newItem);
      saveVendorInventory(inventory);

      // Prepend to DOM #inventory-list
      const list = document.getElementById('inventory-list');
      if (list) {
        const card = document.createElement('div');
        card.className = "product-item bg-white p-3 rounded-xl border border-slate-200 shadow-xs flex items-center justify-between gap-2.5 w-full overflow-hidden";
        card.setAttribute('data-id', prodId);
        card.setAttribute('data-title', name);
        card.setAttribute('data-category', cat);

        const discountMarkup = discountPct > 0 
          ? `<span class="text-[10px] text-slate-400 line-through">₹${effectiveMrp.toFixed(2)}</span>
             <span class="px-1.5 py-0.2 rounded text-[9px] font-bold bg-emerald-100 text-emerald-800">${discountPct}% OFF</span>`
          : `<span class="text-[10px] text-slate-400 font-semibold">MRP ₹${effectiveMrp.toFixed(2)}</span>`;

        card.innerHTML = `
          <div class="flex items-center space-x-2.5 min-w-0 flex-1 overflow-hidden">
            <img src="${newItem.img}" alt="${name}" class="w-12 h-12 shrink-0 rounded-lg object-cover border border-slate-200 shadow-2xs" style="width: 48px; height: 48px; min-width: 48px; max-width: 48px; min-height: 48px; max-height: 48px; object-fit: cover;">
            <div class="min-w-0 flex-1 overflow-hidden">
              <div class="flex items-center space-x-1 min-w-0">
                <h4 class="text-xs font-bold text-slate-900 truncate">${name}</h4>
                <span class="text-[10px] text-slate-500 font-medium shrink-0">(${unit})</span>
              </div>
              <div class="flex items-center space-x-1.5 mt-0.5 flex-wrap">
                <span class="text-xs font-extrabold text-slate-900">₹${price.toFixed(2)}</span>
                ${discountMarkup}
              </div>
              <div class="flex items-center space-x-1.5 mt-0.5 text-[10px]">
                <span class="text-slate-500 font-medium">Stock: <strong class="text-slate-700">${stock} units</strong></span>
                <span class="text-slate-300">•</span>
                <span class="stock-label font-bold text-emerald-600 block">${inStock ? 'IN STOCK' : 'OUT OF STOCK'}</span>
              </div>
            </div>
          </div>
          <label class="relative inline-flex items-center cursor-pointer shrink-0 ml-1">
            <input type="checkbox" ${inStock ? 'checked' : ''} onchange="toggleProductStock(this, '${prodId}', '${name.replace(/'/g, "\\'")}')" class="sr-only peer">
            <div class="w-9 h-5 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-emerald-600"></div>
          </label>
        `;
        list.insertBefore(card, list.firstChild);
      }

      updateLiveItemsCounter();
      closeCustomPricingModal();
      toastSuccess(currentLang === 'hi' ? `${name} दुकान में सफलतापूर्वक जोड़ा गया!` : `${name} added to live store!`);
    }
    window.saveCustomPricedItem = saveCustomPricedItem;

    function updateLiveItemsCounter() {
      const counter = document.getElementById('vendor-live-items-counter');
      if (counter) {
        const total = document.querySelectorAll('#inventory-list .product-item').length;
        counter.innerText = `${total} Items Live`;
      }
    }
    window.updateLiveItemsCounter = updateLiveItemsCounter;

    // 5. INVENTORY FILTER / REAL-TIME SEARCH
    function filterInventory(query = null) {
      if (query === null) {
        query = document.getElementById('inventory-search')?.value || '';
      }
      const q = query.toLowerCase().trim();
      const items = document.querySelectorAll('#inventory-list .product-item');
      let visibleCount = 0;

      items.forEach(card => {
        const title = (card.getAttribute('data-title') || '').toLowerCase();
        const cat = (card.getAttribute('data-category') || '').toLowerCase();
        const text = card.textContent.toLowerCase();

        if (!q || title.includes(q) || cat.includes(q) || text.includes(q)) {
          card.classList.remove('hidden');
          card.classList.add('flex');
          visibleCount++;
        } else {
          card.classList.add('hidden');
          card.classList.remove('flex');
        }
      });

      const emptyMsg = document.getElementById('inventory-search-empty-msg');
      if (visibleCount === 0 && q.length > 0) {
        if (!emptyMsg) {
          const emptyDiv = document.createElement('div');
          emptyDiv.id = 'inventory-search-empty-msg';
          emptyDiv.className = "p-5 bg-slate-50 border-2 border-dashed border-slate-300 rounded-2xl text-center space-y-2";
          emptyDiv.innerHTML = `
            <p class="text-xs font-bold text-slate-700">कोई सामान नहीं मिला: "${query}"</p>
            <p class="text-[11px] text-slate-500">क्या आप इसे अपनी दुकान में नए सामान के रूप में जोड़ना चाहते हैं?</p>
            <button type="button" onclick="openCustomPricingModal({ title: '${query.replace(/'/g, "\\'")}', mrp: 50, price: 45 })" class="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-xl text-xs transition shadow-xs active:scale-95 inline-flex items-center space-x-1.5">
              <i data-lucide="plus" class="w-3.5 h-3.5"></i>
              <span>+ "${query}" को दुकान में जोड़ें</span>
            </button>
          `;
          document.getElementById('inventory-list')?.appendChild(emptyDiv);
          if (window.lucide) lucide.createIcons();
        }
      } else if (emptyMsg) {
        emptyMsg.remove();
      }
    }
    window.filterInventory = filterInventory;\n"""

if target_js in content:
    content = content.replace(target_js, new_controller_code, 1)
    with open('public_web/vendor/index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("SUCCESS: Inserted multimodal inventory controller in vendor/index.html")
else:
    print("Target openAddProductModal not found in content!")
