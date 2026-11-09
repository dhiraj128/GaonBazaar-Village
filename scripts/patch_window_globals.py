with open('public_web/customer/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

target1 = "let cartItems = [];"
replacement1 = """let cartItems = [];
    Object.defineProperty(window, 'cartItems', {
      get: () => cartItems,
      set: (val) => { cartItems = val; },
      configurable: true
    });"""

target2 = "let selectedCheckoutAddressId = null;"
replacement2 = """let selectedCheckoutAddressId = null;
    Object.defineProperty(window, 'selectedCheckoutAddressId', {
      get: () => selectedCheckoutAddressId,
      set: (val) => { selectedCheckoutAddressId = val; },
      configurable: true
    });"""

assert target1 in text, "target1 not found"
assert target2 in text, "target2 not found"

text = text.replace(target1, replacement1, 1)
text = text.replace(target2, replacement2, 1)

with open('public_web/customer/index.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("SUCCESS: Attached cartItems and selectedCheckoutAddressId to window!")
