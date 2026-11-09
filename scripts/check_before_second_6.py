import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/runner/index.html', 'r', encoding='utf-8') as f:
    runner = f.read()

idx_6_2 = runner.rfind('id="screen-onboarding-6"')
print(runner[idx_6_2-400:idx_6_2+100])
