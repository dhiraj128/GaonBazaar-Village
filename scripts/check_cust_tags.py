import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/customer/index.html', 'r', encoding='utf-8') as f:
    customer = f.read()

idx1 = customer.find('id="page-language"')
idx2 = customer.find('id="page-login"')
lang_html = customer[idx1:idx2]

opens = lang_html.count('<div') + lang_html.count('<section')
closes = lang_html.count('</div') + lang_html.count('</section')
print(f"Customer Language - Opens: {opens}, Closes: {closes}")
