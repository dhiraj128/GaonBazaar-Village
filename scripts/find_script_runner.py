import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/runner/index.html', 'r', encoding='utf-8') as f:
    runner = f.read()

idx = runner.find('<script>')
print("<script> at:", idx)
print(runner[idx-300:idx+300])
