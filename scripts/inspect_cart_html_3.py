import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/customer/index.html', 'r', encoding='utf-8') as f:
    customer = f.read()

idx = customer.find('data-i18n="payment_mode_title"')
if idx != -1:
    print(customer[idx:idx+3500])
