with open('public_web/customer/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

idx = content.find('id="modal-rural-address"')
print(content[idx:idx+3000].encode('ascii', errors='replace').decode('ascii'))
