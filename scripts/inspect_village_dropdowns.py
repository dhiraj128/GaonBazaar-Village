with open('public_web/vendor/index.html', 'r', encoding='utf-8') as f:
    v_content = f.read()

idx = v_content.find('function handleVendorVillageSearch')
print("=== VENDOR VILLAGE SEARCH ===")
print(v_content[idx:idx+1500].encode('ascii', errors='replace').decode('ascii'))
