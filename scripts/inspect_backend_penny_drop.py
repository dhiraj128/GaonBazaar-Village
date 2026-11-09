import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('backend/app/api/v1/payments.py', 'r', encoding='utf-8') as f:
    code = f.read()

idx = code.find('verify-penny-drop')
print("verify-penny-drop idx:", idx)
if idx != -1:
    print(code[idx-50:idx+800])
