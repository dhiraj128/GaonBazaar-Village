import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/runner/index.html', 'r', encoding='utf-8') as f:
    runner = f.read()

matches = re.findall(r'.{0,40}under_review_sub_runner.{0,60}', runner)
for m in matches:
    print(m)

idx = runner.find('under_review_sub_runner')
if idx != -1:
    print("\nSurrounding:")
    print(runner[idx-100:idx+300])
