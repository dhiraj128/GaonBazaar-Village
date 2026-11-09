import sys

sys.stdout.reconfigure(encoding='utf-8')

for app in ['runner', 'vendor']:
    with open(f'public_web/{app}/index.html', 'r', encoding='utf-8') as f:
        code = f.read()
    pos7 = code.find('id="screen-onboarding-7"')
    pos_end = code.find('<!--', pos7 + 100)
    print(f"=== {app.upper()} SCREEN 7 FULL ===")
    if pos7 != -1:
        print(code[pos7:pos7+2500])
