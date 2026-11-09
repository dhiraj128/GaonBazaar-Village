import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/runner/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(450, 520):
    if i < len(lines):
        print(f"{i+1}: {lines[i]}", end='')
