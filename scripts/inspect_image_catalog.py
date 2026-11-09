with open('public_web/customer/index.html', 'r', encoding='utf-8') as f:
    c_content = f.read()

idx = c_content.find('const IMAGE_CATALOG =')
if idx == -1:
    idx = c_content.find('IMAGE_CATALOG =')
print("IMAGE_CATALOG definition:")
print(c_content[idx:idx+2500].encode('ascii', errors='replace').decode('ascii'))
