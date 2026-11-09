import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('backend/app/api/v1/payments.py', 'r', encoding='utf-8') as f:
    code = f.read()

idx = code.find('class PennyDropVerifyRequest')
print("class PennyDropVerifyRequest idx:", idx)
if idx != -1:
    print(code[idx:idx+500])
