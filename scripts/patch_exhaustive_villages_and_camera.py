# scripts/patch_exhaustive_villages_and_camera.py
import re
import os

CANONICAL_VILLAGES_JS = """    // ---------------------------------------------------------------------------
    // EXHAUSTIVE BIHAR & MUZAFFARPUR RURAL VILLAGE & PINCODE DATASET
    // ---------------------------------------------------------------------------
    const GAONBAZAAR_VILLAGES = [
      { en: "Ali Neora", hi: "अली नेओरा", pincode: "843128", district: "Muzaffarpur", block: "Minapur" },
      { en: "Aurai", hi: "औराई", pincode: "843321", district: "Muzaffarpur", block: "Aurai" },
      { en: "Bandra", hi: "बंदरा", pincode: "843115", district: "Muzaffarpur", block: "Bandra" },
      { en: "Bhabua", hi: "भभुआ", pincode: "821101", district: "Kaimur", block: "Bhabua" },
      { en: "Bochahan", hi: "बोचहां", pincode: "843103", district: "Muzaffarpur", block: "Bochahan" },
      { en: "Chaturshi", hi: "चतुरशी", pincode: "843128", district: "Muzaffarpur", block: "Minapur" },
      { en: "Darbhanga Rural", hi: "दरभंगा ग्रामीण", pincode: "846004", district: "Darbhanga", block: "Darbhanga" },
      { en: "Dharampur", hi: "धरमपुर", pincode: "843109", district: "Muzaffarpur", block: "Kanti" },
      { en: "Gaighat", hi: "गायघाट", pincode: "843118", district: "Muzaffarpur", block: "Gaighat" },
      { en: "Gopalpur", hi: "गोपालपुर", pincode: "842002", district: "Muzaffarpur", block: "Musahari" },
      { en: "Hajipur", hi: "हाजीपुर", pincode: "844101", district: "Vaishali", block: "Hajipur" },
      { en: "Kanti", hi: "कांटी", pincode: "843109", district: "Muzaffarpur", block: "Kanti" },
      { en: "Katra", hi: "कटरा", pincode: "843321", district: "Muzaffarpur", block: "Katra" },
      { en: "Kudra", hi: "कुदरा", pincode: "821108", district: "Kaimur", block: "Kudra" },
      { en: "Kurhani", hi: "कुढ़नी", pincode: "844127", district: "Muzaffarpur", block: "Kurhani" },
      { en: "Madhuban", hi: "मधुबन", pincode: "843128", district: "Muzaffarpur", block: "Minapur" },
      { en: "Mariyabad", hi: "मरियाबाद", pincode: "843128", district: "Muzaffarpur", block: "Minapur" },
      { en: "Marwan", hi: "मड़वन", pincode: "843113", district: "Muzaffarpur", block: "Marwan" },
      { en: "Minapur", hi: "मीनापुर", pincode: "843128", district: "Muzaffarpur", block: "Minapur" },
      { en: "Mohania", hi: "मोहनिया", pincode: "821109", district: "Kaimur", block: "Mohania" },
      { en: "Motipur", hi: "मोतीपुर", pincode: "843111", district: "Muzaffarpur", block: "Motipur" },
      { en: "Musahari", hi: "मुशहरी", pincode: "842002", district: "Muzaffarpur", block: "Musahari" },
      { en: "Muzaffarpur Town", hi: "मुज़फ़्फ़रपुर नगर", pincode: "842001", district: "Muzaffarpur", block: "Town" },
      { en: "Nekanama", hi: "नेकनामा", pincode: "843128", district: "Muzaffarpur", block: "Minapur" },
      { en: "Panapur", hi: "पानापुर", pincode: "843128", district: "Muzaffarpur", block: "Minapur" },
      { en: "Paroo", hi: "पारू", pincode: "843112", district: "Muzaffarpur", block: "Paroo" },
      { en: "Patna Rural", hi: "पटना ग्रामीण", pincode: "800001", district: "Patna", block: "Patna" },
      { en: "Rampur Hari", hi: "रामपुर हरी", pincode: "843128", district: "Muzaffarpur", block: "Minapur" },
      { en: "Sahebganj", hi: "साहेबगंज", pincode: "843125", district: "Muzaffarpur", block: "Sahebganj" },
      { en: "Sakra", hi: "सकरा", pincode: "843105", district: "Muzaffarpur", block: "Sakra" },
      { en: "Samastipur Rural", hi: "समस्तीपुर ग्रामीण", pincode: "848101", district: "Samastipur", block: "Samastipur" },
      { en: "Saraiya", hi: "सरैया", pincode: "843126", district: "Muzaffarpur", block: "Saraiya" },
      { en: "Shibai Patti", hi: "शिबाई पट्टी", pincode: "843128", district: "Muzaffarpur", block: "Minapur" },
      { en: "Sitamarhi Rural", hi: "सीतामढ़ी ग्रामीण", pincode: "843302", district: "Sitamarhi", block: "Sitamarhi" },
      { en: "Tengari", hi: "तेंगारी", pincode: "843128", district: "Muzaffarpur", block: "Minapur" }
    ];

    const RURAL_AREAS_LIST = GAONBAZAAR_VILLAGES.slice().sort((a, b) => a.en.localeCompare(b.en));
    window.GAONBAZAAR_VILLAGES = GAONBAZAAR_VILLAGES;
    window.RURAL_AREAS_LIST = RURAL_AREAS_LIST;"""


def patch_vendor():
    filepath = 'public_web/vendor/index.html'
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update BIHAR_RURAL_HUBS to GAONBAZAAR_VILLAGES
    hub_pattern = re.compile(r'// --+\s*// COMPREHENSIVE BIHAR RURAL HUBS.*?(const RURAL_AREAS_LIST = BIHAR_RURAL_HUBS\.slice\(\)\.sort\(.*?\);)', re.DOTALL)
    if hub_pattern.search(content):
        content = hub_pattern.sub(CANONICAL_VILLAGES_JS, content)
        print("Vendor: Replaced BIHAR_RURAL_HUBS with GAONBAZAAR_VILLAGES")

    # 2. Update selectVendorVillage to populate pincode
    select_fn_pattern = re.compile(r'function selectVendorVillage\(villageName\)\s*\{[^}]*\}', re.DOTALL)
    new_select_fn = """function selectVendorVillage(villageName, pincode) {
      const input = document.getElementById('vendor-village-name');
      if (input) input.value = villageName;
      const pincodeInput = document.getElementById('vendor-pincode');
      if (pincodeInput && pincode) pincodeInput.value = pincode;
      const dropdown = document.getElementById('vendor-village-dropdown');
      if (dropdown) dropdown.classList.add('hidden');
    }
    window.selectVendorVillage = selectVendorVillage;"""
    if select_fn_pattern.search(content):
        content = select_fn_pattern.sub(new_select_fn, content)
        print("Vendor: Updated selectVendorVillage")

    # 3. Update handleVendorVillageSearch to display pincode and pass it to selectVendorVillage
    search_fn_pattern = re.compile(r'function handleVendorVillageSearch\(query\)\s*\{.*?window\.handleVendorVillageSearch = handleVendorVillageSearch;', re.DOTALL)
    new_search_fn = """function handleVendorVillageSearch(query) {
      const dropdown = document.getElementById('vendor-village-dropdown');
      if (!dropdown) return;
      const q = (query || '').trim().toLowerCase();
      const isHindi = (typeof currentLang !== 'undefined' ? currentLang === 'hi' : false) || 
                      (localStorage.getItem('gaonbazaar_vendor_lang') === 'hi') || 
                      (window.currentLang === 'hi');

      // Strict A-to-Z sorting:
      const sortedHubs = RURAL_AREAS_LIST.slice().sort((a, b) => {
        return a.en.localeCompare(b.en);
      });
      
      const filtered = sortedHubs.filter(item => {
        return item.en.toLowerCase().includes(q) || 
               item.hi.toLowerCase().includes(q) ||
               (item.pincode && item.pincode.includes(q));
      });
      
      let html = '';
      if (filtered.length > 0) {
        filtered.forEach(item => {
          // Display ONLY the English string OR ONLY the Hindi string based on active language:
          const singleLabel = isHindi ? item.hi : item.en;
          const safeLabel = singleLabel.replace(/["']/g, '');
          const pin = item.pincode || '';
          html += `
            <div onclick="selectVendorVillage('${safeLabel}', '${pin}')" class="px-3.5 py-2.5 hover:bg-emerald-50 cursor-pointer flex items-center justify-between text-xs font-semibold text-slate-800 transition">
              <div class="flex items-center space-x-2">
                <i data-lucide="map-pin" class="w-3.5 h-3.5 text-emerald-600 shrink-0"></i>
                <span class="font-bold text-slate-900 village-label">${singleLabel}</span>
              </div>
              <span class="text-[10px] text-emerald-700 bg-emerald-50 border border-emerald-200 px-1.5 py-0.5 rounded font-mono font-bold">${pin}</span>
            </div>
          `;
        });
      } else {
        html = `
          <div class="px-4 py-3 text-center text-xs text-slate-400">
            ${isHindi ? 'कोई गाँव नहीं मिला' : 'No village found'}
          </div>
        `;
      }

      if (q && !filtered.some(item => (isHindi ? item.hi : item.en).toLowerCase() === q)) {
        const customSafe = q.replace(/["']/g, '');
        html += `
          <div onclick="selectVendorVillage('${customSafe}', '')" class="px-3.5 py-2.5 hover:bg-emerald-50 cursor-pointer flex items-center justify-between text-xs font-semibold text-emerald-800 border-t border-slate-100 transition">
            <div class="flex items-center space-x-2">
              <i data-lucide="plus-circle" class="w-3.5 h-3.5 text-emerald-600 shrink-0"></i>
              <span>${isHindi ? 'कस्टम नाम चुनें: ' : 'Use Custom: '} "<strong>${customSafe}</strong>"</span>
            </div>
            <span class="text-[10px] text-slate-400">${isHindi ? 'कस्टम' : 'Custom'}</span>
          </div>
        `;
      }

      dropdown.innerHTML = html;
      dropdown.classList.remove('hidden');
      if (window.lucide) lucide.createIcons();
    }
    window.handleVendorVillageSearch = handleVendorVillageSearch;"""
    if search_fn_pattern.search(content):
        content = search_fn_pattern.sub(new_search_fn, content)
        print("Vendor: Updated handleVendorVillageSearch")

    # 4. In #modal-take-photo: Add WebRTC live viewfinder fallback container and button
    webrtc_html_box = """        <!-- Photo Capture / Preview Box -->
        <div class="p-4 bg-amber-50/60 rounded-2xl border-2 border-dashed border-amber-300 text-center space-y-3">
          <div id="photo-preview-container" class="hidden w-28 h-28 mx-auto rounded-2xl overflow-hidden border-2 border-amber-500 shadow-md">
            <img id="photo-preview-image" src="" alt="Snapped Photo" class="w-full h-full object-cover">
          </div>
          <div id="photo-placeholder-icon" class="w-14 h-14 mx-auto rounded-2xl bg-amber-100 text-amber-700 flex items-center justify-center">
            <i data-lucide="camera" class="w-7 h-7"></i>
          </div>

          <!-- WebRTC In-App Camera Viewfinder (Fallback for WebViews that restrict file capture) -->
          <div id="vendor-camera-stream-container" class="hidden relative w-full h-56 rounded-2xl overflow-hidden bg-black border-2 border-amber-500 shadow-inner">
            <video id="vendor-camera-stream-video" class="w-full h-full object-cover" autoplay playsinline muted></video>
            <canvas id="vendor-camera-canvas" class="hidden"></canvas>
            <div class="absolute inset-0 border-2 border-white/40 pointer-events-none rounded-2xl m-3 border-dashed"></div>
            <button type="button" onclick="snapWebRTCCameraPhoto()" id="btn-snap-webrtc-photo" class="absolute bottom-3 left-1/2 -translate-x-1/2 px-5 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-full text-xs shadow-lg active:scale-95 flex items-center space-x-1.5 cursor-pointer">
              <i data-lucide="camera" class="w-4 h-4"></i>
              <span data-i18n="snap_live_photo_btn">Snap Photo</span>
            </button>
          </div>

          <p class="text-xs font-bold text-amber-950" id="photo-status-text" data-i18n="photo_status_prompt">Capture real product photo with camera</p>
          
          <div class="space-y-2">
            <button type="button" onclick="triggerCameraCapture()" class="w-full py-3.5 bg-amber-600 hover:bg-amber-700 text-white font-bold rounded-xl text-xs shadow-md transition active:scale-95 flex items-center justify-center space-x-2 cursor-pointer min-h-[48px]">
              <i data-lucide="camera" class="w-4 h-4"></i>
              <span data-i18n="open_camera_btn">Open Camera & Snap Photo</span>
            </button>
            <button type="button" onclick="startWebRTCCameraFallback()" id="btn-start-webrtc-viewfinder" class="w-full py-2.5 bg-white hover:bg-amber-50 text-amber-800 font-bold rounded-xl text-xs border border-amber-300 transition active:scale-95 flex items-center justify-center space-x-1.5 cursor-pointer">
              <i data-lucide="video" class="w-3.5 h-3.5"></i>
              <span data-i18n="start_webrtc_btn">Live Camera Viewfinder (In-App)</span>
            </button>
          </div>
        </div>"""

    old_photo_box = re.compile(r'<!-- Photo Capture / Preview Box -->.*?<button type="button" onclick="triggerCameraCapture\(\)".*?</button>\s*</div>', re.DOTALL)
    if old_photo_box.search(content):
        content = old_photo_box.sub(webrtc_html_box, content)
        print("Vendor: Updated Photo Capture modal HTML with WebRTC Viewfinder")

    # 5. Update WebRTC JS functions and handleVendorCameraPhoto
    camera_js_block = """    let activeWebRTCCameraStream = null;

    async function startWebRTCCameraFallback() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: { ideal: "environment" } },
          audio: false
        });
        activeWebRTCCameraStream = stream;
        const video = document.getElementById('vendor-camera-stream-video');
        const streamContainer = document.getElementById('vendor-camera-stream-container');
        const placeholderIcon = document.getElementById('photo-placeholder-icon');
        const previewContainer = document.getElementById('photo-preview-container');
        
        if (previewContainer) previewContainer.classList.add('hidden');
        if (placeholderIcon) placeholderIcon.classList.add('hidden');
        if (streamContainer && video) {
          video.srcObject = stream;
          streamContainer.classList.remove('hidden');
        }
        toastInfo(currentLang === 'hi' ? "लाइव कैमरा सक्रिय है!" : "Live camera activated!");
      } catch (err) {
        console.warn("WebRTC camera not available, falling back to native file capture:", err);
        triggerCameraCapture();
      }
    }
    window.startWebRTCCameraFallback = startWebRTCCameraFallback;

    function stopWebRTCCamera() {
      if (activeWebRTCCameraStream) {
        activeWebRTCCameraStream.getTracks().forEach(t => t.stop());
        activeWebRTCCameraStream = null;
      }
      const streamContainer = document.getElementById('vendor-camera-stream-container');
      if (streamContainer) streamContainer.classList.add('hidden');
      const placeholderIcon = document.getElementById('photo-placeholder-icon');
      if (placeholderIcon) placeholderIcon.classList.remove('hidden');
    }
    window.stopWebRTCCamera = stopWebRTCCamera;

    function snapWebRTCCameraPhoto() {
      const video = document.getElementById('vendor-camera-stream-video');
      const canvas = document.getElementById('vendor-camera-canvas') || document.createElement('canvas');
      if (video && video.videoWidth) {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        const dataUrl = canvas.toDataURL('image/jpeg', 0.85);
        stopWebRTCCamera();
        currentSnappedPhotoData = dataUrl;
        
        // Auto-populate custom pricing form with snapped image and decoupled pricing
        const looseItemName = (document.getElementById('loose-item-name-input')?.value || '').trim();
        const looseItemCat = document.getElementById('loose-item-cat-input')?.value || 'Vegetables';
        const looseItemUnit = document.getElementById('loose-item-unit-input')?.value || '1 kg';

        closePhotoCaptureModal();
        openCustomPricingModal({
          title: looseItemName,
          category: looseItemCat,
          unit: looseItemUnit,
          mrp: '',
          price: '',
          stock: '',
          img: currentSnappedPhotoData
        });
        toastSuccess(currentLang === 'hi' ? "फोटो सफलतापूर्वक ली गई!" : "Photo captured successfully!");
      }
    }
    window.snapWebRTCCameraPhoto = snapWebRTCCameraPhoto;

    function handleVendorCameraPhoto(event) {
      const file = event.target.files && event.target.files[0];
      if (!file) return;

      const reader = new FileReader();
      reader.onload = function(e) {
        currentSnappedPhotoData = e.target.result;
        stopWebRTCCamera();
        closePhotoCaptureModal();

        // Auto-populate custom pricing form with snapped image and decoupled pricing
        const looseItemName = (document.getElementById('loose-item-name-input')?.value || '').trim();
        const looseItemCat = document.getElementById('loose-item-cat-input')?.value || 'Vegetables';
        const looseItemUnit = document.getElementById('loose-item-unit-input')?.value || '1 kg';

        openCustomPricingModal({
          title: looseItemName,
          category: looseItemCat,
          unit: looseItemUnit,
          mrp: '',
          price: '',
          stock: '',
          img: currentSnappedPhotoData
        });
        toastSuccess(currentLang === 'hi' ? "फोटो सफलतापूर्वक ली गई!" : "Photo captured successfully!");
      };
      reader.readAsDataURL(file);
    }
    window.handleVendorCameraPhoto = handleVendorCameraPhoto;"""

    old_handle_photo = re.compile(r'function handleVendorCameraPhoto\(event\)\s*\{.*?window\.handleVendorCameraPhoto = handleVendorCameraPhoto;', re.DOTALL)
    if old_handle_photo.search(content):
        content = old_handle_photo.sub(camera_js_block, content)
        print("Vendor: Updated handleVendorCameraPhoto and WebRTC camera methods")

    # In closePhotoCaptureModal: ensure stopWebRTCCamera is called
    close_photo_fn = re.compile(r'function closePhotoCaptureModal\(\)\s*\{.*?window\.closePhotoCaptureModal = closePhotoCaptureModal;', re.DOTALL)
    new_close_photo_fn = """function closePhotoCaptureModal() {
      stopWebRTCCamera();
      const modal = document.getElementById('modal-take-photo');
      if (modal) {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
      }
    }
    window.closePhotoCaptureModal = closePhotoCaptureModal;"""
    if close_photo_fn.search(content):
        content = close_photo_fn.sub(new_close_photo_fn, content)
        print("Vendor: Updated closePhotoCaptureModal with stopWebRTCCamera")

    # 6. Add translation keys
    if 'start_webrtc_btn:' not in content:
        content = content.replace('open_camera_btn: "Open Camera & Snap Photo",',
                                  'open_camera_btn: "Open Camera & Snap Photo",\n        start_webrtc_btn: "Live Camera Viewfinder (In-App)",\n        snap_live_photo_btn: "Snap Photo",')
        content = content.replace('open_camera_btn: "कैमरा खोलें व फोटो खींचें",',
                                  'open_camera_btn: "कैमरा खोलें व फोटो खींचें",\n        start_webrtc_btn: "लाइव कैमरा व्यूफाइंडर (ऐप में)",\n        snap_live_photo_btn: "फोटो लें",')
        print("Vendor: Added translation keys for WebRTC")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Vendor patch complete.")


def patch_runner():
    filepath = 'public_web/runner/index.html'
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update BIHAR_RURAL_HUBS to GAONBAZAAR_VILLAGES
    hub_pattern = re.compile(r'// --+\s*// COMPREHENSIVE BIHAR RURAL HUBS.*?(const RURAL_AREAS_LIST = BIHAR_RURAL_HUBS\.slice\(\)\.sort\(.*?\);)', re.DOTALL)
    if hub_pattern.search(content):
        content = hub_pattern.sub(CANONICAL_VILLAGES_JS, content)
        print("Runner: Replaced BIHAR_RURAL_HUBS with GAONBAZAAR_VILLAGES")

    # 2. Add #runner-pincode input in runner HTML right after #runner-base-village container
    runner_pincode_html = """            <!-- 2. Operating Postal Pincode -->
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1" data-i18n="pincode_label">
                Postal Pincode <span class="text-rose-500">*</span>
              </label>
              <div class="relative flex items-center">
                <i data-lucide="hash" class="absolute left-3.5 w-4 h-4 text-blue-600 pointer-events-none"></i>
                <input type="tel" id="runner-pincode" maxlength="6" placeholder="e.g. 843128" value="843128" class="w-full pl-10 pr-4 py-3.5 rounded-xl border border-slate-300 bg-white text-slate-900 font-mono font-bold text-xs focus:border-blue-600 focus:ring-2 focus:ring-blue-100 focus:outline-none shadow-xs">
              </div>
            </div>"""

    if 'id="runner-pincode"' not in content:
        target_str = '<p class="text-[10px] text-slate-400 mt-1" data-i18n="base_village_hint">Orders will be assigned from local shops and farms around your hub</p>\n            </div>'
        if target_str in content:
            content = content.replace(target_str, target_str + '\n\n' + runner_pincode_html)
            print("Runner: Added #runner-pincode input")
        else:
            # Try with \r\n
            target_str_crlf = '<p class="text-[10px] text-slate-400 mt-1" data-i18n="base_village_hint">Orders will be assigned from local shops and farms around your hub</p>\r\n            </div>'
            if target_str_crlf in content:
                content = content.replace(target_str_crlf, target_str_crlf + '\r\n\r\n' + runner_pincode_html)
                print("Runner: Added #runner-pincode input (CRLF)")

    # 3. Update selectRunnerVillage
    select_fn_pattern = re.compile(r'function selectRunnerVillage\(villageName\)\s*\{[^}]*\}', re.DOTALL)
    new_select_fn = """function selectRunnerVillage(villageName, pincode) {
      const input = document.getElementById('runner-base-village');
      if (input) input.value = villageName;
      const pincodeInput = document.getElementById('runner-pincode');
      if (pincodeInput && pincode) pincodeInput.value = pincode;
      const dropdown = document.getElementById('runner-village-dropdown');
      if (dropdown) dropdown.classList.add('hidden');
    }
    window.selectRunnerVillage = selectRunnerVillage;"""
    if select_fn_pattern.search(content):
        content = select_fn_pattern.sub(new_select_fn, content)
        print("Runner: Updated selectRunnerVillage")

    # 4. Update handleRunnerVillageSearch
    search_fn_pattern = re.compile(r'function handleRunnerVillageSearch\(query\)\s*\{.*?window\.handleRunnerVillageSearch = handleRunnerVillageSearch;', re.DOTALL)
    new_search_fn = """function handleRunnerVillageSearch(query) {
      const dropdown = document.getElementById('runner-village-dropdown');
      if (!dropdown) return;
      const q = (query || '').trim().toLowerCase();
      const isHindi = (typeof currentLang !== 'undefined' ? currentLang === 'hi' : false) || 
                      (localStorage.getItem('gaonbazaar_runner_lang') === 'hi') || 
                      (window.currentLang === 'hi');

      // Strict A-to-Z sorting:
      const sortedHubs = RURAL_AREAS_LIST.slice().sort((a, b) => {
        return a.en.localeCompare(b.en);
      });
      
      const filtered = sortedHubs.filter(item => {
        return item.en.toLowerCase().includes(q) || 
               item.hi.toLowerCase().includes(q) ||
               (item.pincode && item.pincode.includes(q));
      });
      
      let html = '';
      if (filtered.length > 0) {
        filtered.forEach(item => {
          // Display ONLY the English string OR ONLY the Hindi string based on active language:
          const singleLabel = isHindi ? item.hi : item.en;
          const safeLabel = singleLabel.replace(/["']/g, '');
          const pin = item.pincode || '';
          html += `
            <div onclick="selectRunnerVillage('${safeLabel}', '${pin}')" class="px-3.5 py-2.5 hover:bg-blue-50 cursor-pointer flex items-center justify-between text-xs font-semibold text-slate-800 transition">
              <div class="flex items-center space-x-2">
                <i data-lucide="map-pin" class="w-3.5 h-3.5 text-blue-600 shrink-0"></i>
                <span class="font-bold text-slate-900 village-label">${singleLabel}</span>
              </div>
              <span class="text-[10px] text-blue-700 bg-blue-50 border border-blue-200 px-1.5 py-0.5 rounded font-mono font-bold">${pin}</span>
            </div>
          `;
        });
      } else {
        html = `
          <div class="px-4 py-3 text-center text-xs text-slate-400">
            ${isHindi ? 'कोई गाँव नहीं मिला' : 'No village found'}
          </div>
        `;
      }

      if (q && !filtered.some(item => (isHindi ? item.hi : item.en).toLowerCase() === q)) {
        const customSafe = q.replace(/["']/g, '');
        html += `
          <div onclick="selectRunnerVillage('${customSafe}', '')" class="px-3.5 py-2.5 hover:bg-blue-50 cursor-pointer flex items-center justify-between text-xs font-semibold text-blue-800 border-t border-slate-100 transition">
            <div class="flex items-center space-x-2">
              <i data-lucide="plus-circle" class="w-3.5 h-3.5 text-blue-600 shrink-0"></i>
              <span>${isHindi ? 'कस्टम नाम चुनें: ' : 'Use Custom: '} "<strong>${customSafe}</strong>"</span>
            </div>
            <span class="text-[10px] text-slate-400">${isHindi ? 'कस्टम' : 'Custom'}</span>
          </div>
        `;
      }

      dropdown.innerHTML = html;
      dropdown.classList.remove('hidden');
      if (window.lucide) lucide.createIcons();
    }
    window.handleRunnerVillageSearch = handleRunnerVillageSearch;"""
    if search_fn_pattern.search(content):
        content = search_fn_pattern.sub(new_search_fn, content)
        print("Runner: Updated handleRunnerVillageSearch")

    # 5. In saveRunnerLocationAndProceed: ensure pincode is saved
    if 'localStorage.setItem(\'gaonbazaar_runner_pincode\'' not in content:
        content = content.replace(
            "const village = (document.getElementById('runner-base-village')?.value || 'Chaturshi').trim();",
            "const village = (document.getElementById('runner-base-village')?.value || 'Tengari').trim();\n      const pincode = (document.getElementById('runner-pincode')?.value || '843128').trim();\n      localStorage.setItem('gaonbazaar_runner_pincode', pincode);"
        )
        print("Runner: Updated saveRunnerLocationAndProceed to store pincode")

    # 6. Add pincode_label translation if missing in Runner
    if 'pincode_label:' not in content:
        content = content.replace('hub_landmark_label: "Operating Hub Landmark",', 'pincode_label: "Postal Pincode",\n        hub_landmark_label: "Operating Hub Landmark",')
        content = content.replace('hub_landmark_label: "ऑपरेटिंग हब लैंडमार्क",', 'pincode_label: "पिनकोड",\n        hub_landmark_label: "ऑपरेटिंग हब लैंडमार्क",')
        print("Runner: Added pincode_label translation")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Runner patch complete.")


def patch_customer():
    filepath = 'public_web/customer/index.html'
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Add GAONBAZAAR_VILLAGES to customer
    if 'const GAONBAZAAR_VILLAGES =' not in content:
        customer_villages_block = CANONICAL_VILLAGES_JS + """
    function handleCustomerVillageSearch(query) {
      const dropdown = document.getElementById('customer-village-dropdown');
      if (!dropdown) return;
      const q = (query || '').trim().toLowerCase();
      const isHindi = (typeof currentLang !== 'undefined' ? currentLang === 'hi' : false) || 
                      (localStorage.getItem('gaonbazaar_customer_lang') === 'hi') || 
                      (window.currentLang === 'hi');

      const sortedHubs = RURAL_AREAS_LIST.slice().sort((a, b) => a.en.localeCompare(b.en));
      const filtered = sortedHubs.filter(item => {
        return item.en.toLowerCase().includes(q) || 
               item.hi.toLowerCase().includes(q) ||
               (item.pincode && item.pincode.includes(q));
      });

      let html = '';
      if (filtered.length > 0) {
        filtered.forEach(item => {
          const singleLabel = isHindi ? item.hi : item.en;
          const safeLabel = singleLabel.replace(/["']/g, '');
          const pin = item.pincode || '';
          html += `
            <div onclick="selectCustomerVillage('${safeLabel}', '${pin}')" class="px-3 py-2 hover:bg-emerald-50 cursor-pointer flex items-center justify-between text-xs font-semibold text-slate-800 transition">
              <div class="flex items-center space-x-2">
                <i data-lucide="map-pin" class="w-3 h-3 text-emerald-600 shrink-0"></i>
                <span class="font-bold text-slate-900 village-label">${singleLabel}</span>
              </div>
              <span class="text-[9px] text-emerald-700 bg-emerald-50 border border-emerald-200 px-1 py-0.5 rounded font-mono font-bold">${pin}</span>
            </div>
          `;
        });
      } else {
        html = `
          <div class="px-3 py-2 text-center text-xs text-slate-400">
            ${isHindi ? 'कोई गाँव नहीं मिला' : 'No village found'}
          </div>
        `;
      }

      dropdown.innerHTML = html;
      dropdown.classList.remove('hidden');
      if (window.lucide) lucide.createIcons();
    }
    window.handleCustomerVillageSearch = handleCustomerVillageSearch;

    function toggleCustomerVillageDropdown() {
      const dropdown = document.getElementById('customer-village-dropdown');
      if (dropdown) {
        if (dropdown.classList.contains('hidden')) {
          handleCustomerVillageSearch(document.getElementById('modal-village-input')?.value || '');
        } else {
          dropdown.classList.add('hidden');
        }
      }
    }
    window.toggleCustomerVillageDropdown = toggleCustomerVillageDropdown;

    function selectCustomerVillage(villageName, pincode) {
      const villageInput = document.getElementById('modal-village-input');
      const pincodeInput = document.getElementById('modal-pincode-input');
      if (villageInput) villageInput.value = villageName;
      if (pincodeInput && pincode) pincodeInput.value = pincode;
      activeCustomerAddress.village = villageName;
      activeCustomerAddress.pincode = pincode;
      localStorage.setItem('gb_customer_locality', villageName);
      if (pincode) localStorage.setItem('gb_customer_pincode', pincode);
      const headerText = document.getElementById('header-location-text');
      if (headerText) headerText.innerText = villageName;
      const dropdown = document.getElementById('customer-village-dropdown');
      if (dropdown) dropdown.classList.add('hidden');
    }
    window.selectCustomerVillage = selectCustomerVillage;
"""
        # Insert before handleVillageInputChange
        if 'function handleVillageInputChange' in content:
            content = content.replace('function handleVillageInputChange', customer_villages_block + '\n    function handleVillageInputChange')
            print("Customer: Added GAONBAZAAR_VILLAGES and village search functions")

    # 2. In #modal-rural-address: replace simple village input with searchable container and add postal pincode input
    village_html_target = re.compile(r'<div>\s*<label class="block text-\[10px\] font-semibold text-slate-500 mb-0\.5" data-i18n="village_label">Village / Locality</label>\s*<input type="text" id="modal-village-input"[^>]*>.*?</div>', re.DOTALL)
    new_village_and_pincode_html = """          <!-- Village / Locality with Searchable Autocomplete -->
          <div class="relative" id="customer-village-container">
            <label class="block text-[10px] font-semibold text-slate-500 mb-0.5" data-i18n="village_label">Village / Locality</label>
            <div class="relative flex items-center">
              <input type="text" id="modal-village-input" oninput="handleCustomerVillageSearch(this.value)" onfocus="handleCustomerVillageSearch(this.value)" placeholder="e.g. Tengari, Shibai Patti, Minapur" class="w-full pl-3 pr-8 py-2 bg-white border border-slate-300 rounded-lg text-xs text-slate-900 focus:border-emerald-600 focus:ring-1 focus:ring-emerald-500 focus:outline-none cursor-text select-text font-bold" autocomplete="off">
              <button type="button" onclick="toggleCustomerVillageDropdown()" class="absolute right-2 text-slate-400 hover:text-slate-600 focus:outline-none">
                <i data-lucide="chevron-down" class="w-3.5 h-3.5"></i>
              </button>
            </div>
            <div id="customer-village-dropdown" class="hidden absolute left-0 right-0 top-full mt-1 bg-white border border-slate-200 rounded-xl shadow-xl max-h-48 overflow-y-auto z-50 divide-y divide-slate-100">
              <!-- Rendered dynamically via JS -->
            </div>
            <p class="text-[9px] text-slate-400 mt-0.5">Select your village or panchayat to connect with local kirana stores.</p>
          </div>

          <!-- Postal Pincode -->
          <div>
            <label class="block text-[10px] font-semibold text-slate-500 mb-0.5" data-i18n="pincode_label">Postal Pincode</label>
            <input type="tel" id="modal-pincode-input" maxlength="6" placeholder="e.g. 843128" value="843128" class="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-lg text-xs font-mono font-bold text-slate-900 focus:border-emerald-600 focus:outline-none">
          </div>"""

    if 'id="customer-village-dropdown"' not in content:
        content = village_html_target.sub(new_village_and_pincode_html, content)
        print("Customer: Added searchable village autocomplete & pincode input in address modal")

    # 3. In saveCustomerAddress(): Save pincode
    if 'pincode: (document.getElementById(\'modal-pincode-input\')' not in content:
        content = content.replace(
            "state: districtStr.split(',')[1]?.trim() || \"Bihar\",",
            "state: districtStr.split(',')[1]?.trim() || \"Bihar\",\n        pincode: (document.getElementById('modal-pincode-input')?.value || '843128').trim(),"
        )
        print("Customer: Updated saveCustomerAddress to include pincode in payload")

    # 4. In openRuralAddressModal: Populate pincode field when editing
    if 'const pincodeInp = document.getElementById(\'modal-pincode-input\');' not in content:
        content = content.replace(
            "const distInp = document.getElementById('modal-district-input');",
            "const distInp = document.getElementById('modal-district-input');\n          const pincodeInp = document.getElementById('modal-pincode-input');"
        )
        content = content.replace(
            "if (distInp) distInp.value = `${addr.district || 'Muzaffarpur'}, ${addr.state || 'Bihar'}`;",
            "if (distInp) distInp.value = `${addr.district || 'Muzaffarpur'}, ${addr.state || 'Bihar'}`;\n          if (pincodeInp) pincodeInp.value = addr.pincode || '843128';"
        )
        print("Customer: Updated openRuralAddressModal to populate pincode")

    # 5. Add click listener to close customer village dropdown when clicking outside
    if 'customer-village-dropdown' in content and 'customer-village-container' not in content:
        content += """
    <script>
    document.addEventListener('click', (e) => {
      const container = document.getElementById('customer-village-container');
      const dropdown = document.getElementById('customer-village-dropdown');
      if (container && dropdown && !container.contains(e.target)) {
        dropdown.classList.add('hidden');
      }
    });
    </script>
"""

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Customer patch complete.")


if __name__ == '__main__':
    patch_vendor()
    patch_runner()
    patch_customer()
