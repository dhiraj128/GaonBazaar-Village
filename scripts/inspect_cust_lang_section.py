import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/customer/index.html', 'r', encoding='utf-8') as f:
    customer = f.read()

idx = customer.find('id="page-language"')
if idx == -1:
    idx = customer.find('proceedFromLanguage')
print(customer[idx-100:idx+1500])
