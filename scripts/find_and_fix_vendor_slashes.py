import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/vendor/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Desi Toor / Arhar Dal -> Desi Toor Dal
content = content.replace('Desi Toor / Arhar Dal 1kg', 'Desi Toor Dal 1kg')
content = content.replace('Desi Toor / Arhar Dal', 'Desi Toor Dal')

# Fix 2: discount badge text in modal-custom-pricing initial HTML
# <span id="discount-badge-text">8% OFF (?20 ?????? ?? ??? / Customer Savings)</span>
content = re.sub(
    r'<span id="discount-badge-text">.*?</span>',
    '<span id="discount-badge-text">10% OFF (₹20 Customer Savings)</span>',
    content
)

# Fix 3: item_name_label in i18n
content = content.replace('"Item / Product Name"', '"Item Name"')
content = content.replace('"Item / Product Name":', '"Item Name":')

# Fix 4: check any other i18n keys or modals
# Let's check i18n.en and i18n.hi
content = content.replace('Toor / Arhar', 'Toor Dal')
content = content.replace('बचत / Customer Savings', 'Customer Savings')

with open('public_web/vendor/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Applied fixes to public_web/vendor/index.html")
