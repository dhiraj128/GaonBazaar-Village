import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/runner/index.html', 'r', encoding='utf-8') as f:
    runner = f.read()

idx = runner.rfind('id="screen-onboarding-6"')
print("Last screen-onboarding-6 at:", idx)
print(runner[idx-100:idx+300])
# and where does it end before dashboard/bottom nav?
pos_bottom = runner.find('id="bottom-tabs"', idx)
print("id=bottom-tabs at:", pos_bottom)
if pos_bottom != -1:
    print(runner[pos_bottom-200:pos_bottom+100])
