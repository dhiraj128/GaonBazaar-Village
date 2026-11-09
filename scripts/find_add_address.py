with open('public_web/customer/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'Add Address', text, re.IGNORECASE)]
for idx in matches:
    print(f"--- Match at {idx} ---")
    print(text[max(0, idx-150):min(len(text), idx+150)])
