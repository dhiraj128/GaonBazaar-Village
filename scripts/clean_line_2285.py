with open('public_web/customer/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

bad = 'window.renderFaqAccordion();\n      if (typeof updateCustomerLangCards === "function") updateCustomerLangCards(lang);'
good = 'window.renderFaqAccordion();'

if bad in text:
    text = text.replace(bad, good, 1)
    with open('public_web/customer/index.html', 'w', encoding='utf-8') as f:
        f.write(text)
    print('Cleaned up line 2285 successfully')
else:
    # Try CRLF
    bad_crlf = 'window.renderFaqAccordion();\r\n      if (typeof updateCustomerLangCards === "function") updateCustomerLangCards(lang);'
    if bad_crlf in text:
        text = text.replace(bad_crlf, good, 1)
        with open('public_web/customer/index.html', 'w', encoding='utf-8') as f:
            f.write(text)
        print('Cleaned up line 2285 CRLF successfully')
    else:
        print('Could not find bad pattern')
