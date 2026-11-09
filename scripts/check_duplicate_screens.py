import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/runner/index.html', 'r', encoding='utf-8') as f:
    runner = f.read()

pos_5_1 = runner.find('id="screen-onboarding-5"')
pos_5_2 = runner.find('id="screen-onboarding-5"', pos_5_1 + 30)

print("First onboarding-5 at:", pos_5_1)
print(runner[pos_5_1:pos_5_1+300])

print("\nSecond onboarding-5 at:", pos_5_2)
print(runner[pos_5_2:pos_5_2+300])
