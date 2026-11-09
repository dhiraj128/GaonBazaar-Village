with open('public_web/customer/index.html', 'r', encoding='utf-8') as f:
    c_content = f.read()

import re
images = re.findall(r'"img":\s*"([^"]+)"', c_content)
print("Customer product images:", len(images))
for img in images[:10]:
    print(" -", img)

idx = c_content.find('PRODUCT_IMAGE_CATALOG')
if idx != -1:
    print("=== PRODUCT_IMAGE_CATALOG in Customer ===")
    print(c_content[idx:idx+1500].encode('ascii', errors='replace').decode('ascii'))
