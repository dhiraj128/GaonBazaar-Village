import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/customer/index.html', 'r', encoding='utf-8') as f:
    customer = f.read()

# find modal container or end of modals
matches = re.findall(r'<div[^>]*id=[\"\']modal-[^\"\']+[\"\'][^>]*>', customer)
print("Existing modals in customer:", matches)

# look at btn-place-order
idx = customer.find('id="btn-place-order"')
print("\nbtn-place-order section:")
print(customer[idx-50:idx+350])
