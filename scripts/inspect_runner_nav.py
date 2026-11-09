import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/runner/index.html', 'r', encoding='utf-8') as f:
    runner = f.read()

idx = runner.find('function navigateTo')
print("navigateTo in runner:")
print(runner[idx:idx+800])
