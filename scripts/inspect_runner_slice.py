import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/runner/index.html', 'r', encoding='utf-8') as f:
    runner = f.read()

# Let's inspect from index 28000 to 33000
print(runner[27800:33000])
