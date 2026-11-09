import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/customer/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx1 = text.find('id="page-login"')
idx2 = text.find('</section>', idx1)
print(text[idx1:idx2+10])
