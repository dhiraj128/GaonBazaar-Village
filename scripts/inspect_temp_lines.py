import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('scripts/temp_block1.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines[4165:4205], start=4166):
    print(f"{idx}: {line}", end='')
