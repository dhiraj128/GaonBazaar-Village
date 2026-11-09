with open('public_web/vendor/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

idx = content.find('filterInventory')
while idx != -1:
    print(f"filterInventory at {idx}:")
    print(content[idx-50:idx+300].encode('ascii', errors='replace').decode('ascii'))
    idx = content.find('filterInventory', idx + 1)
