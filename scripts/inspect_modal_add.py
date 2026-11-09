with open('public_web/vendor/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

idx_modal = content.find('id="modal-add-product"')
idx_next_modal = content.find('<!-- MODAL 2: UPDATE PAYOUT WITH SMS OTP -->', idx_modal)
print("=== MODAL ADD PRODUCT BOUNDS ===")
print(content[idx_modal-50:idx_next_modal].encode('ascii', errors='replace').decode('ascii'))
