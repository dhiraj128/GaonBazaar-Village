import sys
import re
sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/customer/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

modals = re.findall(r'id=["\'](modal-[a-zA-Z0-9_-]+)["\']', c)
print("Modals in customer:", modals)

# Also find functions with checkout or order
funcs = re.findall(r'function\s+([a-zA-Z0-9_]*(?:checkout|order|pay)[a-zA-Z0-9_]*)', c, re.IGNORECASE)
print("Checkout/Order/Pay functions:", funcs)
