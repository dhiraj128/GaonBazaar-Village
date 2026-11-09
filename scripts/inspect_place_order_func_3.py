import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/customer/index.html', 'r', encoding='utf-8') as f:
    customer = f.read()

idx = customer.find('function placeCustomerOrder')
print(customer[idx+3000:idx+4500])
