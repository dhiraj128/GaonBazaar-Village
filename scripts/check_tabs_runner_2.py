import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/runner/index.html', 'r', encoding='utf-8') as f:
    runner = f.read()

for m in re.finditer(r'id=[\"\'](tab-[a-z0-9_-]+)[\"\']', runner):
    print(f"Tab {m.group(1)} at {m.start()}")
