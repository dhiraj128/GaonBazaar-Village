import sys

sys.stdout.reconfigure(encoding='utf-8')

for app in ['runner', 'vendor']:
    with open(f'public_web/{app}/index.html', 'r', encoding='utf-8') as f:
        code = f.read()
    pos = code.find('id="screen-onboarding-5"')
    pos_next = code.find('id="screen-onboarding-6"')
    print(f"=== {app.upper()} SCREEN 5 ===")
    if pos != -1 and pos_next != -1:
        print(code[pos:pos_next])
