with open('public_web/vendor/index.html', 'r', encoding='utf-8') as f:
    v_content = f.read()

idx = v_content.find('function handleVendorVillageSearch')
print("Function index:", idx)
print(repr(v_content[idx:idx+800]))
