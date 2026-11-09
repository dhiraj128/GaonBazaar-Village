import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/runner/index.html', 'r', encoding='utf-8') as f:
    runner = f.read()

for step in range(1, 8):
    pos = runner.find(f'screen-onboarding-{step}')
    print(f"step {step} pos:", pos)
    if pos != -1:
        print(runner[pos-50:pos+300])
        print("-------------------")
