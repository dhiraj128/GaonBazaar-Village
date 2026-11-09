import sys
sys.stdout.reconfigure(encoding='utf-8')
with open('public_web/vendor/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('function setLanguage(')
print(text[idx+1100:idx+1800])
