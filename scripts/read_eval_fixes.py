import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('scripts/eval_location_and_fixes.py', 'r', encoding='utf-8') as f:
    code = f.read()

print(code[:1800])
