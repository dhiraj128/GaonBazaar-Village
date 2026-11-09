with open('public_web/vendor/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

idx = content.find('function openAddProductModal')
print(content[idx:idx+1500].encode('ascii', errors='replace').decode('ascii'))
