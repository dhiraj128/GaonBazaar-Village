with open('public_web/vendor/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

idx = content.find('MASTER_SKU_DATABASE')
if idx != -1:
    print(content[idx:idx+2500].encode('ascii', errors='replace').decode('ascii'))
