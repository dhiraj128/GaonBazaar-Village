import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/customer/index.html', 'r', encoding='utf-8') as f:
    customer = f.read()

scripts = re.findall(r'<script>(.*?)</script>', customer, re.DOTALL)
print(f"Found {len(scripts)} inline script blocks.")
for i, s in enumerate(scripts):
    print(f"Block {i} length: {len(s)}")
