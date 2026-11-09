import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

for app in ['customer', 'runner', 'vendor']:
    with open(f'public_web/{app}/index.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    print(f"\n==================== {app.upper()} STEP 1 DETAIL ====================")
    # Find step 1 container
    m = re.search(r'(<(?:div|section)[^>]*id=[\"\'](?:screen-onboarding-1|page-language)[\"\'].*?)(?=<(?:div|section)[^>]*id=[\"\'](?:screen-onboarding-2|page-login)[\"\'])', html, re.DOTALL)
    if m:
        block = m.group(1)
        buttons = re.findall(r'<button[^>]*>.*?</button>', block, re.DOTALL)
        print(f"Total buttons in Step 1: {len(buttons)}")
        for i, b in enumerate(buttons):
            print(f"Button {i}: {b.strip()}")
