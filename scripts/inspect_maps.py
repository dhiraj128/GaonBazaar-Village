import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

for app in ['runner', 'vendor']:
    with open(f'public_web/{app}/index.html', 'r', encoding='utf-8') as f:
        code = f.read()
    print(f"=== {app.upper()} Maps ===")
    matches = re.findall(r'.{0,40}(?:init.*Map|google\.maps|MapTypeId).{0,40}', code)
    for m in matches[:10]:
        print(" - ", m)
