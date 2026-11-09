import sys

sys.stdout.reconfigure(encoding='utf-8')

for app in ['runner', 'vendor']:
    with open(f'public_web/{app}/index.html', 'r', encoding='utf-8') as f:
        code = f.read()
    idx = code.find('id="screen-onboarding-7"')
    print(f"=== {app.upper()} SCREEN 7 ===")
    if idx != -1:
        print(code[idx:idx+1200])
