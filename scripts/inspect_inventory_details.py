with open('public_web/vendor/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

idx1 = content.find('id="tab-inventory"')
idx2 = content.find('id="tab-ledger"')
print("=== INVENTORY TAB CONTENT ===")
print(content[idx1:idx2].encode('ascii', errors='replace').decode('ascii'))

idx3 = content.find('id="modal-add-product"')
idx4 = content.find('id="modal-', idx3 + 20)
print("=== MODAL ADD PRODUCT FULL ===")
print(content[idx3:idx4].encode('ascii', errors='replace').decode('ascii'))
