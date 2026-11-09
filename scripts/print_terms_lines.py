with open('public_web/vendor/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re
print("=== CSV LINES ===")
for line in content.splitlines():
    if re.search(r'\bCSV\b', line, re.I):
        print(line.strip().encode('ascii', errors='replace').decode('ascii')[:120])

print("=== SKU LINES (first 10) ===")
for line in content.splitlines():
    if re.search(r'\bSKU\b', line, re.I):
        print(line.strip().encode('ascii', errors='replace').decode('ascii')[:120])
