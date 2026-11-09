with open('public_web/customer/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace("    async \n    // ---------------------------------------------------------------------------\n    // DEDICATED CHECKOUT PAYMENT BOTTOM SHEET LOGIC", "    // ---------------------------------------------------------------------------\n    // DEDICATED CHECKOUT PAYMENT BOTTOM SHEET LOGIC")
text = text.replace("    async \r\n    // ---------------------------------------------------------------------------\r\n    // DEDICATED CHECKOUT PAYMENT BOTTOM SHEET LOGIC", "    // ---------------------------------------------------------------------------\r\n    // DEDICATED CHECKOUT PAYMENT BOTTOM SHEET LOGIC")
text = text.replace("let currentVaultTab = 'upi';", "var currentVaultTab = 'upi';")

with open('public_web/customer/index.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated customer/index.html successfully")
