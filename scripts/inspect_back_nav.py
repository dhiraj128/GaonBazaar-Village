import sys

sys.stdout.reconfigure(encoding='utf-8')

for app in ['runner', 'vendor']:
    with open(f'public_web/{app}/index.html', 'r', encoding='utf-8') as f:
        code = f.read()
    idx = code.find('function handleHistoryBack')
    print(f"=== {app.upper()} handleHistoryBack ===")
    if idx != -1:
        print(code[idx:idx+800])
