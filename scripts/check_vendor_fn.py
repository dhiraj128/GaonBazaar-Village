with open('public_web/vendor/index.html', 'r', encoding='utf-8') as f:
    v_content = f.read()

idx = v_content.find('handleVendorVillageSearch')
print("Vendor village search:")
print(repr(v_content[idx:idx+800]))
