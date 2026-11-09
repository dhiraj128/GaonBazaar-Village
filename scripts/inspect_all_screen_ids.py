import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

for app in ['runner', 'vendor']:
    with open(f'public_web/{app}/index.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    print(f"\n==================== {app.upper()} SCREENS ====================")
    matches = list(re.finditer(r'<div[^>]*id=[\"\'](screen-onboarding-\d+)[\"\'][^>]*>', html))
    for m in matches:
        print(f"Pos {m.start()}: {m.group(0)}")
