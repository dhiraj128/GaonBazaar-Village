with open('scripts/verify_complete_checkout_and_fixes_cdp.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace("#vendor-village-dropdown button span:first-child", "#vendor-village-dropdown span.font-bold")
text = text.replace("#runner-village-dropdown button span:first-child", "#runner-village-dropdown span.font-bold")

with open('scripts/verify_complete_checkout_and_fixes_cdp.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated dropdown selectors in verify script")
