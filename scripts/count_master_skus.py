with open('public_web/vendor/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re
m = re.findall(r'"product_name":\s*"([^"]+)"', content)
print("Total master products:", len(m))
for name in m[:10]:
    print(" -", name)
