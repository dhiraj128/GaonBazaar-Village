with open('public_web/customer/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

target = '<button onclick="openRuralAddressModal()" class="text-[11px] font-bold text-emerald-700 hover:underline flex items-center space-x-1">'
replacement = '<button id="btn-account-add-address" onclick="openRuralAddressModal()" class="text-[11px] font-bold text-emerald-700 hover:underline flex items-center space-x-1">'

if target in text:
    text = text.replace(target, replacement, 1)
    with open('public_web/customer/index.html', 'w', encoding='utf-8') as f:
        f.write(text)
    print("SUCCESS: Added id='btn-account-add-address'")
else:
    print("ERROR: Target not found")
