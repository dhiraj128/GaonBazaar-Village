import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

for app in ['runner', 'vendor']:
    with open(f'public_web/{app}/index.html', 'r', encoding='utf-8') as f:
        code = f.read()
    m = re.search(r'function proceedToNextStep\(\)[^{]*\{.*?\n    \}', code, re.DOTALL)
    print(f"=== {app.upper()} proceedToNextStep ===")
    if m:
        print(m.group(0))
