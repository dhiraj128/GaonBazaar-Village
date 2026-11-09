with open('public_web/vendor/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

idx = content.find('modal-add-product')
print("Index:", idx)
print("Before:", repr(content[idx-120:idx]))
print("After:", repr(content[idx:idx+120]))
