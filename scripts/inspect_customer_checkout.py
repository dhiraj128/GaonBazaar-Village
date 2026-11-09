import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/customer/index.html', 'r', encoding='utf-8') as f:
    customer = f.read()

# find functions related to checkout and payment
checkout_funcs = re.findall(r'function (?:openCheckout|placeCustomerOrder|selectPaymentMode|handleCheckout|proceedToPayment|confirmPayment)[^{]*\{', customer)
print("Checkout functions found:", checkout_funcs)

# search for payment bottom sheet or modal
modals = re.findall(r'id=[\"\']([a-zA-Z0-9_-]*(?:payment|checkout|cart)[a-zA-Z0-9_-]*)[\"\']', customer, re.IGNORECASE)
print("Modals/elements matching payment/checkout/cart:", set(modals))

# let's see how cart checkout is triggered
cart_matches = re.findall(r'<button[^>]*onclick=[\"\']([^\"\']*(?:checkout|order|payment)[^\"\']*)[\"\']', customer, re.IGNORECASE)
print("Cart/checkout button onclicks:", cart_matches)
