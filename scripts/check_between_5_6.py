import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/runner/index.html', 'r', encoding='utf-8') as f:
    runner = f.read()

idx_5 = runner.find('id="screen-onboarding-5"')
print("screen-onboarding-5 at:", idx_5)
idx_6 = runner.find('id="screen-onboarding-6"')
print("screen-onboarding-6 at:", idx_6)
print(runner[idx_6-300:idx_6+200])
