with open('public_web/customer/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

target = 'renderFaqAccordion();'
replacement = 'renderFaqAccordion();\n      if (typeof updateCustomerLangCards === "function") updateCustomerLangCards(lang);'
if target in text:
    text = text.replace(target, replacement, 1)
    with open('public_web/customer/index.html', 'w', encoding='utf-8') as f:
        f.write(text)
    print('Updated setAppLanguage in customer/index.html')
else:
    print('Target not found')
