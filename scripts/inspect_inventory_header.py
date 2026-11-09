with open('public_web/vendor/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Locate tab-inventory header & search section
idx_start = content.find('id="tab-inventory"')
idx_list = content.find('id="inventory-list"', idx_start)
print("=== TAB INVENTORY HEADER & SEARCH SECTION ===")
print(content[idx_start:idx_list].encode('ascii', errors='replace').decode('ascii'))
