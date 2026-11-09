with open('public_web/vendor/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re
matches = [
    'openAddProductModal',
    'selectMasterSku',
    'submitLiveStoreItem',
    'recalculateDiscount',
    'filterMasterCatalog',
    'filterInventory',
    'getVendorInventory',
    'saveVendorInventory'
]

for m in matches:
    idx = content.find(f'function {m}')
    if idx != -1:
        print(f"=== {m} ===")
        print(content[idx:idx+600].encode('ascii', errors='replace').decode('ascii'))
