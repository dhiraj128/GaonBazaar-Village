with open('public_web/vendor/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re
matches = re.findall(r'function (render[A-Za-z0-9_]+|filter[A-Za-z0-9_]+|toggle[A-Za-z0-9_]+)', content)
print("Matching functions:", matches)
for fn in ['renderInventory', 'renderInventoryList', 'filterInventory', 'renderVendorInventory']:
    idx = content.find(f'function {fn}')
    if idx != -1:
        print(f"=== {fn} ===")
        print(content[idx:idx+600].encode('ascii', errors='replace').decode('ascii'))
