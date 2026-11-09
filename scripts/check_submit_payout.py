import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/runner/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

idx = c.find('function submitPayoutDetails')
print(c[idx:idx+1200])
