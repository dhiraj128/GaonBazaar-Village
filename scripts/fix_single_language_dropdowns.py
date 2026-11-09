with open('public_web/vendor/index.html', 'r', encoding='utf-8') as f:
    v_content = f.read()

v_start = v_content.find('function handleVendorVillageSearch(query) {')
v_end = v_content.find('function selectVendorVillage(', v_start)

new_v_fn = """function handleVendorVillageSearch(query) {
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
        return item.en.toLowerCase().includes(q) || item.hi.toLowerCase().includes(q);
      });
      
      let html = '';
      if (filtered.length > 0) {
        filtered.forEach(item => {
          // Display ONLY the English string OR ONLY the Hindi string based on active language:
          const singleLabel = isHindi ? item.hi : item.en;
          html += `
            <div onclick="selectVendorVillage('${singleLabel.replace(/'/g, "\\'")}')" class="px-3.5 py-2.5 hover:bg-emerald-50 cursor-pointer flex items-center justify-between text-xs font-semibold text-slate-800 transition">
              <div class="flex items-center space-x-2">
                <i data-lucide="map-pin" class="w-3.5 h-3.5 text-emerald-600 shrink-0"></i>
                <span class="font-bold text-slate-900 village-label">${singleLabel}</span>
              </div>
              <span class="text-[10px] text-emerald-700 bg-emerald-50 border border-emerald-200 px-1.5 py-0.5 rounded font-bold">${isHindi ? 'ग्रामीण केंद्र' : 'Rural Hub'}</span>
            </div>
          `;
        });
      }

      if (q && !filtered.some(item => (isHindi ? item.hi : item.en).toLowerCase() === q)) {
        html += `
          <div onclick="selectVendorVillage('${query.replace(/'/g, "\\'")}')" class="px-3.5 py-2.5 hover:bg-emerald-50 cursor-pointer flex items-center justify-between text-xs font-semibold text-emerald-800 border-t border-slate-100 transition">
            <div class="flex items-center space-x-2">
              <i data-lucide="plus-circle" class="w-3.5 h-3.5 text-emerald-600 shrink-0"></i>
              <span>${isHindi ? 'कस्टम नाम चुनें: ' : 'Use Custom: '} "<strong>${query}</strong>"</span>
            </div>
            <span class="text-[10px] text-slate-400">${isHindi ? 'कस्टम' : 'Custom'}</span>
          </div>
        `;
      }

      dropdown.innerHTML = html;
      dropdown.classList.remove('hidden');
      if (window.lucide) lucide.createIcons();
    }
    window.handleVendorVillageSearch = handleVendorVillageSearch;\n\n    """

if v_start != -1 and v_end != -1:
    v_content = v_content[:v_start] + new_v_fn + v_content[v_end:]
    # Also attach window.currentLang in setLanguage
    v_content = v_content.replace(
        "function setLanguage(lang) {\n      currentLang = lang;",
        "function setLanguage(lang) {\n      currentLang = lang;\n      window.currentLang = lang;"
    )
    with open('public_web/vendor/index.html', 'w', encoding='utf-8') as f:
        f.write(v_content)
    print("SUCCESS: Vendor updated!")

# 2. Runner
with open('public_web/runner/index.html', 'r', encoding='utf-8') as f:
    r_content = f.read()

r_start = r_content.find('function handleRunnerVillageSearch(query) {')
r_end = r_content.find('function selectRunnerVillage(', r_start)

new_r_fn = """function handleRunnerVillageSearch(query) {
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
        return item.en.toLowerCase().includes(q) || item.hi.toLowerCase().includes(q);
      });
      
      let html = '';
      if (filtered.length > 0) {
        filtered.forEach(item => {
          // Display ONLY the English string OR ONLY the Hindi string based on active language:
          const singleLabel = isHindi ? item.hi : item.en;
          html += `
            <div onclick="selectRunnerVillage('${singleLabel.replace(/'/g, "\\'")}')" class="px-3.5 py-2.5 hover:bg-blue-50 cursor-pointer flex items-center justify-between text-xs font-semibold text-slate-800 transition">
              <div class="flex items-center space-x-2">
                <i data-lucide="map-pin" class="w-3.5 h-3.5 text-blue-600 shrink-0"></i>
                <span class="font-bold text-slate-900 village-label">${singleLabel}</span>
              </div>
              <span class="text-[10px] text-blue-700 bg-blue-50 border border-blue-200 px-1.5 py-0.5 rounded font-bold">${isHindi ? 'ऑपरेटिंग हब' : 'Operating Hub'}</span>
            </div>
          `;
        });
      }

      if (q && !filtered.some(item => (isHindi ? item.hi : item.en).toLowerCase() === q)) {
        html += `
          <div onclick="selectRunnerVillage('${query.replace(/'/g, "\\'")}')" class="px-3.5 py-2.5 hover:bg-blue-50 cursor-pointer flex items-center justify-between text-xs font-semibold text-blue-800 border-t border-slate-100 transition">
            <div class="flex items-center space-x-2">
              <i data-lucide="plus-circle" class="w-3.5 h-3.5 text-blue-600 shrink-0"></i>
              <span>${isHindi ? 'कस्टम नाम चुनें: ' : 'Use Custom: '} "<strong>${query}</strong>"</span>
            </div>
            <span class="text-[10px] text-slate-400">${isHindi ? 'कस्टम' : 'Custom'}</span>
          </div>
        `;
      }

      dropdown.innerHTML = html;
      dropdown.classList.remove('hidden');
      if (window.lucide) lucide.createIcons();
    }
    window.handleRunnerVillageSearch = handleRunnerVillageSearch;\n\n    """

if r_start != -1 and r_end != -1:
    r_content = r_content[:r_start] + new_r_fn + r_content[r_end:]
    r_content = r_content.replace(
        "function setLanguage(lang) {\n      currentLang = lang;",
        "function setLanguage(lang) {\n      currentLang = lang;\n      window.currentLang = lang;"
    )
    with open('public_web/runner/index.html', 'w', encoding='utf-8') as f:
        f.write(r_content)
    print("SUCCESS: Runner updated!")
