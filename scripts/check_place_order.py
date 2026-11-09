import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/customer/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

idx = c.find('function placeCustomerOrder')
print("=== placeCustomerOrder ===")
print(c[idx:idx+1200])

idx2 = c.find('function selectPaymentMode')
print("=== selectPaymentMode ===")
print(c[idx2:idx2+600])
