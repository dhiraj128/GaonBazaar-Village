import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/runner/index.html', 'r', encoding='utf-8') as f:
    runner = f.read()

sub = runner[34000:63200]
headers = re.findall(r'<!--\s*([^\n]+)\s*-->', sub)
print("Headers between 34000 and 63200:")
for h in headers[:20]:
    print(" - ", h)
