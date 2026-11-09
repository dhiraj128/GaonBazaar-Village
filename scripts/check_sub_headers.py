import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/runner/index.html', 'r', encoding='utf-8') as f:
    runner = f.read()

sub = runner[63000:106000]
headers = re.findall(r'<!--\s*([^\n]+)\s*-->', sub)
print("Headers in range:")
for h in headers[:20]:
    print(" - ", h)
