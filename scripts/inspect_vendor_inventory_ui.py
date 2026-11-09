with open('public_web/vendor/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

idx1 = content.find('id="tab-inventory"')
print("=== TAB INVENTORY ===")
print(content[idx1:idx1+1500])

idx2 = content.find('id="modal-add-product"')
if idx2 != -1:
    print("=== MODAL ADD PRODUCT ===")
    print(content[idx2:idx2+2000])
else:
    print("modal-add-product not found, searching for add product modals:")
    import re
    for m in re.finditer(r'id="modal-[^"]+"', content):
        print(m.group(0))
