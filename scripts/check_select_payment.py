import sys
sys.stdout.reconfigure(encoding='utf-8')
with open('public_web/customer/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('function updateCheckoutModalUI()')
idx2 = text.find('async function confirmPaymentAndPlaceOrder()')
print(text[idx:idx2])
