import sys

sys.stdout.reconfigure(encoding='utf-8')

for app in ['runner', 'vendor']:
    with open(f'public_web/{app}/index.html', 'r', encoding='utf-8') as f:
        code = f.read()
    idx = code.find('function submitPayoutDetails')
    print(f"=== {app.upper()} submitPayoutDetails (pt 2) ===")
    if idx != -1:
        print(code[idx+1000:idx+2500])
