import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/customer/index.html', 'r', encoding='utf-8') as f:
    customer = f.read()

customer = customer.replace(
    'let selectedCheckoutModalPayment = \'ONLINE\';',
    'var selectedCheckoutModalPayment = \'ONLINE\';',
    1
)

with open('public_web/customer/index.html', 'w', encoding='utf-8') as f:
    f.write(customer)

print("Updated selectedCheckoutModalPayment to var")
