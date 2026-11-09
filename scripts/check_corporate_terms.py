with open('public_web/vendor/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re
print("Occurrences of 'CSV':", len(re.findall(r'\bCSV\b', content, re.IGNORECASE)))
print("Occurrences of 'SKU':", len(re.findall(r'\bSKU\b', content, re.IGNORECASE)))
for m in re.finditer(r'openAddProductModal', content):
    print("openAddProductModal called at:", m.start())
