with open('public_web/vendor/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

idx1 = content.find('id="inventory-list"')
idx2 = content.find('</div>\n      </div>\n\n      <!-- TAB 3: LEDGER', idx1)
if idx2 == -1:
    idx2 = content.find('id="tab-ledger"')

print("Length of inventory-list HTML:", idx2 - idx1)
print(content[idx1:idx1+2000].encode('ascii', errors='replace').decode('ascii'))
