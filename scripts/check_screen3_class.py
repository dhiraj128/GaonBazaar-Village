import sys

sys.stdout.reconfigure(encoding='utf-8')

for app in ['runner', 'vendor']:
    with open(f'public_web/{app}/index.html', 'r', encoding='utf-8') as f:
        html = f.read()
    idx3 = html.find('id="screen-onboarding-3"')
    print(f"=== {app.upper()} SCREEN 3 START ===")
    print(html[idx3-50:idx3+200])
