import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

for app in ['customer', 'runner', 'vendor']:
    path = f'public_web/{app}/index.html'
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    print(f"\n==================== {app.upper()} ALL CONTINUE BUTTONS ====================")
    matches = re.finditer(r'<button[^>]*>[^<]*(?:continue|जारी रखें)[^<]*</button>', html, re.IGNORECASE)
    for m in matches:
        print("  Match:", m.group(0))
        # print context around it
        start = max(0, m.start() - 150)
        end = min(len(html), m.end() + 150)
        print("  Context:\n", html[start:end])
        print("  ---------------------------------")
    
    # Also search for data-i18n="continue_btn"
    matches_i18n = re.finditer(r'<button[^>]*data-i18n=[\"\']continue_btn[\"\'][^>]*>.*?</button>', html, re.DOTALL)
    for m in matches_i18n:
        print("  i18n Match on button:", m.group(0).replace('\n', ' '))
    matches_i18n_span = re.finditer(r'<button[^>]*>.*?<span[^>]*data-i18n=[\"\']continue_btn[\"\'][^>]*>.*?</span>.*?</button>', html, re.DOTALL)
    for m in matches_i18n_span:
        print("  i18n Span Match on button:", m.group(0).replace('\n', ' '))
