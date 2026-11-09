import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

for app in ['runner', 'vendor']:
    with open(f'public_web/{app}/index.html', 'r', encoding='utf-8') as f:
        code = f.read()
    print(f"=== {app.upper()} KYC buttons ===")
    matches = re.findall(r'<button[^>]*onclick=[\"\']([^\"\']+)[\"\'][^>]*>', code[code.find('id="screen-onboarding-4"'):code.find('id="screen-onboarding-5"')])
    print(matches)
