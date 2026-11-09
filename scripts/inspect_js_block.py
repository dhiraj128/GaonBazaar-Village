with open('public_web/vendor/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

idx1 = content.find('function openAddProductModal')
idx2 = content.find('// Bulk Import (CSV)')
print(content[idx1:idx2].encode('ascii', errors='replace').decode('ascii'))
