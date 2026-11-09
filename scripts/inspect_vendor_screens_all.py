import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/vendor/index.html', 'r', encoding='utf-8') as f:
    vendor = f.read()

matches = list(re.finditer(r'<div[^>]*id=[\"\'](screen-onboarding-\d+)[\"\']', vendor))
for idx, m in enumerate(matches):
    start = m.start()
    screen_id = m.group(1)
    h2 = re.search(r'<h[1-3][^>]*>(.*?)</h[1-3]>', vendor[start:start+1500])
    h_text = h2.group(1) if h2 else "NO HEADING"
    print(f"[{idx}] at {start}: {screen_id} -> {h_text}")
