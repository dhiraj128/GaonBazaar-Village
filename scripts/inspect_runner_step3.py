import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/runner/index.html', 'r', encoding='utf-8') as f:
    runner = f.read()

pos3 = runner.find('id="screen-onboarding-3"')
pos4 = runner.find('id="screen-onboarding-4"')
print(runner[pos3:pos4])
