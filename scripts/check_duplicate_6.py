import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/runner/index.html', 'r', encoding='utf-8') as f:
    runner = f.read()

pos_6_1 = runner.find('id="screen-onboarding-6"')
pos_6_2 = runner.find('id="screen-onboarding-6"', pos_6_1 + 30)

print("First onboarding-6 at:", pos_6_1)
print("Second onboarding-6 at:", pos_6_2)
print(runner[pos_6_2:pos_6_2+400])
