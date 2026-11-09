import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

for name in ['runner', 'vendor', 'customer']:
    path = f'public_web/{name}/index.html'
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    screens = re.findall(r'id=[\"\']screen-([a-zA-Z0-9_-]+)[\"\']', content)
    print(f'=== {name.upper()} SCREENS ===')
    print(screens)
