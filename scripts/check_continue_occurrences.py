import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

for name in ['customer', 'runner', 'vendor']:
    with open(f'public_web/{name}/index.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    print(f"\n==================== {name.upper()} ====================")
    # find where continue_btn appears in html tags
    matches = re.findall(r'<[^>]*data-i18n=[\"\']continue_btn[\"\'][^>]*>.*?</[^>]+>', html, re.DOTALL)
    for m in matches:
        print("  Tag:", m.strip().replace('\n', ' '))
    # find all buttons containing arrow-right
    arrow_btns = re.findall(r'<button[^>]*>[^<]*<[^>]*arrow-right[^>]*>.*?</button>', html, re.DOTALL)
    for b in arrow_btns:
        print("  Arrow button:", b.strip().replace('\n', ' '))
