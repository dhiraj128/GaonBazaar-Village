import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/customer/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

idx = c.find('function openCheckoutModal')
if idx == -1:
    idx = c.find('openModal(\'modal-checkout\'')
if idx == -1:
    idx = c.find('modal-checkout')

print("Found at:", idx)
print(c[idx:idx+1500])
