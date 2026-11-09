import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

for app in ['customer', 'runner', 'vendor']:
    path = f'public_web/{app}/index.html'
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    print(f"==================== {app.upper()} STEP 1 ====================")
    # search for screen-onboarding-1 or language selection screen
    m = re.search(r'(<div[^>]*id=[\"\']screen-(?:onboarding-1|language)[^\"\']*[\"\'].*?)(?=<div[^>]*id=[\"\']screen-|\n\s*<script|$)', html, re.DOTALL)
    if not m:
        m = re.search(r'(<div[^>]*id=[\"\'][^\"\']*language[^\"\']*[\"\'].*?)(?=<div[^>]*id=[\"\']screen-|\n\s*<script|$)', html, re.DOTALL)
    if m:
        buttons = re.findall(r'<button[^>]*>.*?</button>', m.group(1), re.DOTALL)
        print(f"Found {len(buttons)} buttons:")
        for b in buttons:
            print("  --- BUTTON ---")
            print("  ", b.strip().replace('\n', ' '))
    else:
        print("No language screen found by id!")
