with open('public_web/customer/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

target = """        const res = await apiRequest('/api/v1/orders', 'POST', orderPayload);
        btn.innerHTML = `<span>${currentLang === 'hi' ? 'ऑर्डर करें' : 'Place Order'}</span> <i data-lucide="arrow-right" class="w-4 h-4 ml-1"></i>`;
        btn.disabled = false;
        lucide.createIcons();

        cartItems = [];
        updateCartBadge();"""

replacement = """        const res = await apiRequest('/api/v1/orders', 'POST', orderPayload);
        btn.innerHTML = `<span>${currentLang === 'hi' ? 'ऑर्डर करें' : 'Place Order'}</span> <i data-lucide="arrow-right" class="w-4 h-4 ml-1"></i>`;
        btn.disabled = false;
        lucide.createIcons();

        if (!res || !res.id) {
          throw new Error(currentLang === 'hi' ? 'सर्वर पर ऑर्डर बनाने में असमर्थ। कृपया पुनः प्रयास करें।' : 'Order creation failed on server. Please try again.');
        }

        cartItems = [];
        updateCartBadge();"""

target_crlf = target.replace('\n', '\r\n')
replacement_crlf = replacement.replace('\n', '\r\n')

if target_crlf in text:
    text = text.replace(target_crlf, replacement_crlf)
    with open('public_web/customer/index.html', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Successfully updated order creation error guard (CRLF)!")
elif target in text:
    text = text.replace(target, replacement)
    with open('public_web/customer/index.html', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Successfully updated order creation error guard (LF)!")
else:
    print("Target not found!")
