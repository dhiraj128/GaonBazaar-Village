with open('scripts/verify_complete_checkout_and_fixes_cdp.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace("checkout-modal-pay-btn", "btn-checkout-modal-text")

with open('scripts/verify_complete_checkout_and_fixes_cdp.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated btn-checkout-modal-text")
