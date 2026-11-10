import os

path = "public_web/vendor/index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update modal markup to eradicate "50 Rural Staples" text
old_modal_markup = """    <!-- Master Catalog 50 Rural Staples Toggle Modal -->
    <div id="modal-master-catalog" class="hidden fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-3 sm:p-4">
      <div class="w-full max-w-lg bg-white rounded-3xl overflow-hidden shadow-2xl text-left border border-slate-200 max-h-[90vh] flex flex-col">
        <!-- Header -->
        <div class="p-4 bg-emerald-800 text-white flex items-center justify-between shrink-0">
          <div>
            <h3 class="text-base font-extrabold flex items-center space-x-2">
              <i data-lucide="book-open" class="w-5 h-5"></i>
              <span>Master Catalog (50 Rural Staples)</span>
            </h3>
            <p class="text-xs text-emerald-100 mt-0.5">Toggle switches ON/OFF to instantly stock items in your shop.</p>
          </div>
          <button onclick="closeModal('modal-master-catalog')" class="w-8 h-8 rounded-full bg-emerald-900/60 hover:bg-emerald-900 text-white flex items-center justify-center transition active:scale-95">
            <i data-lucide="x" class="w-4 h-4"></i>
          </button>
        </div>

        <!-- Search Filter -->
        <div class="p-3 border-b border-slate-100 bg-slate-50 shrink-0">
          <div class="relative">
            <i data-lucide="search" class="w-4 h-4 text-slate-400 absolute left-3 top-2.5"></i>
            <input type="text" id="master-catalog-search" oninput="filterMasterCatalogList(this.value)" placeholder="Search 50 staples (Atta, Dal, Sugar, Oil, Biscuits)..." class="w-full pl-9 pr-3 py-2 bg-white border border-slate-200 rounded-xl text-xs focus:outline-none focus:border-emerald-600">
          </div>
        </div>

        <!-- Items List Container -->
        <div id="master-catalog-items-list" class="p-3 space-y-2.5 flex-1 overflow-y-auto">
          <!-- Dynamically populated via renderMasterCatalogToggleList() -->
        </div>

        <!-- Footer -->
        <div class="p-3.5 border-t border-slate-100 bg-white flex items-center justify-between shrink-0">
          <span id="master-catalog-enabled-count" class="text-xs font-bold text-slate-600">0 of 50 Staples Active</span>
          <button onclick="closeModal('modal-master-catalog')" class="px-5 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold shadow-xs active:scale-95 transition">
            Done
          </button>
        </div>
      </div>
    </div>"""

new_modal_markup = """    <!-- Dynamic Master Product Catalog Modal -->
    <div id="modal-master-catalog" class="hidden fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-3 sm:p-4">
      <div class="w-full max-w-lg bg-white rounded-3xl overflow-hidden shadow-2xl text-left border border-slate-200 max-h-[90vh] flex flex-col">
        <!-- Header -->
        <div class="p-4 bg-emerald-800 text-white flex items-center justify-between shrink-0">
          <div>
            <h3 class="text-base font-extrabold flex items-center space-x-2">
              <i data-lucide="book-open" class="w-5 h-5"></i>
              <span data-i18n="master_catalog_title">Master Product Catalog</span>
            </h3>
            <p class="text-xs text-emerald-100 mt-0.5" data-i18n="master_catalog_sub">Dynamic FMCG search & instant shop stocking.</p>
          </div>
          <button onclick="closeModal('modal-master-catalog')" class="w-8 h-8 rounded-full bg-emerald-900/60 hover:bg-emerald-900 text-white flex items-center justify-center transition active:scale-95">
            <i data-lucide="x" class="w-4 h-4"></i>
          </button>
        </div>

        <!-- Search Filter -->
        <div class="p-3 border-b border-slate-100 bg-slate-50 shrink-0">
          <div class="relative">
            <i data-lucide="search" class="w-4 h-4 text-slate-400 absolute left-3 top-2.5"></i>
            <input type="text" id="master-catalog-search" oninput="filterMasterCatalogList(this.value)" placeholder="Search any FMCG product (Atta, Soap, Dal, Oil, Biscuits)..." class="w-full pl-9 pr-3 py-2 bg-white border border-slate-200 rounded-xl text-xs focus:outline-none focus:border-emerald-600">
          </div>
        </div>

        <!-- Items List Container -->
        <div id="master-catalog-items-list" class="p-3 space-y-2.5 flex-1 overflow-y-auto">
          <!-- Dynamically populated via renderMasterCatalogToggleList() -->
        </div>

        <!-- Footer -->
        <div class="p-3.5 border-t border-slate-100 bg-white flex items-center justify-between shrink-0">
          <span id="master-catalog-enabled-count" class="text-xs font-bold text-slate-600">0 Items Active in Shop</span>
          <button onclick="closeModal('modal-master-catalog')" class="px-5 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold shadow-xs active:scale-95 transition">
            Done
          </button>
        </div>
      </div>
    </div>"""

# 2. Add extra items into MASTER_STAPLE_MAP
old_soap_item = """      'soap': {
        title: 'Dettol Original Bathing Soap Bar',
        brand: 'Dettol',
        category: 'Personal Care',
        unit: '125 g',
        image_url: 'https://images.unsplash.com/photo-1607006314188-755a5b5123d5?w=600&q=80'
      }
    };"""

new_soap_item = """      'soap': {
        title: 'Lifebuoy Total Germ Protection Soap',
        brand: 'Lifebuoy',
        category: 'Personal Care',
        unit: '100 g',
        mrp: 40,
        suggested_price: 36,
        image_url: 'https://images.unsplash.com/photo-1607006314188-755a5b5123d5?w=600&q=80'
      },
      'dettol': {
        title: 'Dettol Original Bathing Soap Bar',
        brand: 'Dettol',
        category: 'Personal Care',
        unit: '125 g',
        mrp: 45,
        suggested_price: 40,
        image_url: 'https://images.unsplash.com/photo-1607006314188-755a5b5123d5?w=600&q=80'
      },
      'lux': {
        title: 'Lux Soft Glow Rose Bath Soap',
        brand: 'Lux',
        category: 'Personal Care',
        unit: '100 g',
        mrp: 38,
        suggested_price: 34,
        image_url: 'https://images.unsplash.com/photo-1607006314188-755a5b5123d5?w=600&q=80'
      },
      'shampoo': {
        title: 'Clinic Plus Strong & Long Health Shampoo (175ml)',
        brand: 'Clinic Plus',
        category: 'Personal Care',
        unit: '175 ml',
        mrp: 130,
        suggested_price: 115,
        image_url: 'https://images.unsplash.com/photo-1535585209827-a15fcdbc4c2d?w=600&q=80'
      },
      'detergent': {
        title: 'Ghadi Detergent Washing Powder (1kg)',
        brand: 'Ghadi',
        category: 'Household',
        unit: '1 kg',
        mrp: 70,
        suggested_price: 62,
        image_url: 'https://images.unsplash.com/photo-1585421514738-01798e348b17?w=600&q=80'
      },
      'surf': {
        title: 'Surf Excel Easy Wash Detergent Powder (1kg)',
        brand: 'Surf Excel',
        category: 'Household',
        unit: '1 kg',
        mrp: 145,
        suggested_price: 130,
        image_url: 'https://images.unsplash.com/photo-1585421514738-01798e348b17?w=600&q=80'
      },
      'toothpaste': {
        title: 'Colgate Strong Teeth Anticavity Toothpaste (100g)',
        brand: 'Colgate',
        category: 'Personal Care',
        unit: '100 g',
        mrp: 65,
        suggested_price: 58,
        image_url: 'https://images.unsplash.com/photo-1559591937-e62fb3d8d5bb?w=600&q=80'
      },
      'colgate': {
        title: 'Colgate Strong Teeth Toothpaste (100g)',
        brand: 'Colgate',
        category: 'Personal Care',
        unit: '100 g',
        mrp: 65,
        suggested_price: 58,
        image_url: 'https://images.unsplash.com/photo-1559591937-e62fb3d8d5bb?w=600&q=80'
      },
      'spices': {
        title: 'Everest Turmeric Powder / Haldi (200g)',
        brand: 'Everest',
        category: 'Spices',
        unit: '200 g',
        mrp: 65,
        suggested_price: 58,
        image_url: 'https://images.unsplash.com/photo-1596040033229-a9821ebd058d?w=600&q=80'
      },
      'haldi': {
        title: 'Everest Pure Turmeric Powder (200g)',
        brand: 'Everest',
        category: 'Spices',
        unit: '200 g',
        mrp: 65,
        suggested_price: 58,
        image_url: 'https://images.unsplash.com/photo-1596040033229-a9821ebd058d?w=600&q=80'
      }
    };"""

content_norm = content.replace("\r\n", "\n")

replacements = [
    (old_modal_markup, new_modal_markup, "Modal markup (remove 50 staples)"),
    (old_soap_item, new_soap_item, "Expanded MASTER_STAPLE_MAP with FMCG staples")
]

for old, new, desc in replacements:
    if old in content_norm:
        content_norm = content_norm.replace(old, new, 1)
        print(f"Applied: {desc}")
    else:
        print(f"FAILED to find: {desc}")

with open(path, "w", encoding="utf-8", newline="\r\n") as f:
    f.write(content_norm)

print("Vendor catalog overhaul completed.")
