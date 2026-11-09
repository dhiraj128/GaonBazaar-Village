import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/customer/index.html', 'r', encoding='utf-8') as f:
    customer = f.read()

# find placeCustomerOrder function
m = re.search(r'function placeCustomerOrder\(\) \{.*?\n\}', customer, re.DOTALL)
if m:
    print("placeCustomerOrder:")
    print(m.group(0)[:1500])

# find view-cart modal/section
m2 = re.search(r'<div[^>]*id=[\"\']view-cart[\"\'].*?</div>\s*<!--\s*END.*?(?=<div[^>]*id=[\"\']view-)', customer, re.DOTALL)
if not m2:
    m2 = re.search(r'<div[^>]*id=[\"\']view-cart[\"\'].*?(?=<div[^>]*id=[\"\']view-orders)', customer, re.DOTALL)
if m2:
    print("\nCart section length:", len(m2.group(0)))
    # print the bottom section of cart (payment options / checkout button)
    lines = m2.group(0).split('\n')
    print("\n".join(lines[-60:]))
