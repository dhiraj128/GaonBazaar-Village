with open('public_web/customer/index.html', 'r', encoding='utf-8') as f:
    text = f.read()
print('modal-checkout-payment present:', 'id="modal-checkout-payment"' in text)
print('modal-rural-address present:', 'id="modal-rural-address"' in text)
print('modal-payment-settings present:', 'id="modal-payment-settings"' in text)
print('btn-account-add-address present:', 'btn-account-add-address' in text)
print('modal-gps-btn present:', 'modal-gps-btn' in text)
