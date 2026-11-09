import sys

sys.stdout.reconfigure(encoding='utf-8')

for app in ['runner', 'vendor']:
    with open(f'public_web/{app}/index.html', 'r', encoding='utf-8') as f:
        html = f.read()
    idx1 = html.find('id="screen-onboarding-1"')
    idx2 = html.find('id="screen-onboarding-2"')
    print(f"=== {app.upper()} SCREEN 1 EXACT ===")
    print(html[idx1:idx2])
