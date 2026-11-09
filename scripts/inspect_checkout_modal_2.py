with open('public_web/customer/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

idx = content.find('id="modal-checkout-payment"')
idx2 = content.find('</div>\n    </div>', idx + 1000)
print(content[idx+2000:idx+4500].encode('ascii', errors='replace').decode('ascii'))
