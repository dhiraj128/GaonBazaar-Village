with open('public_web/customer/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

idx = content.find('id="modal-checkout-payment"')
print(content[idx+3500:idx+6500].encode('ascii', errors='replace').decode('ascii'))
