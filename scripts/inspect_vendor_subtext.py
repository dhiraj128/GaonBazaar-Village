import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/vendor/index.html', 'r', encoding='utf-8') as f:
    vendor = f.read()

matches = re.findall(r'.{0,40}under_review_sub[\"\':].{0,80}', vendor)
for m in matches:
    print(m)
