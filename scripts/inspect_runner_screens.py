import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/runner/index.html', 'r', encoding='utf-8') as f:
    runner = f.read()

for step in range(3, 8):
    pattern = rf'(<!--\s*===================================================================\s*-->\s*<!--\s*SCREEN ONBOARDING-{step}.*?)(?=<!--\s*===================================================================\s*-->\s*<!--\s*SCREEN ONBOARDING-|\n\s*<script|$)'
    m = re.search(pattern, runner, re.DOTALL)
    if m:
        print(f"==================== RUNNER SCREEN ONBOARDING-{step} ====================")
        print(m.group(1)[:1200])
        print("...\n")
