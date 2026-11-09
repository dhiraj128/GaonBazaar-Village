import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

for path in ['public_web/customer/index.html', 'public_web/runner/index.html', 'public_web/vendor/index.html']:
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    print(f"=== {path} ===")
    m = re.search(r'(<(?:div|section)[^>]*id=[\"\'](?:screen-onboarding-1|page-language)[\"\'].*?)(?=<(?:div|section)[^>]*id=[\"\'](?:screen-onboarding-2|page-login)[\"\'])', html, re.DOTALL)
    if m:
        content = m.group(1)
        buttons = re.findall(r'<button[^>]*>.*?</button>', content, re.DOTALL)
        for b in buttons:
            print("BUTTON:", b.replace('\n', ' ')[:120])
