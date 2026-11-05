with open('public_web/customer/index.html', 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f):
        if 'id="modal-' in line:
            print(f'Line {idx+1}: {line.strip()[:70]}')
