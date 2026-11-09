import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/vendor/index.html', 'r', encoding='utf-8') as f:
    vendor = f.read()

for step in range(1, 8):
    pos = vendor.find(f'screen-onboarding-{step}')
    print(f"step {step} pos:", pos)
    if pos != -1:
        print(vendor[pos-50:pos+300])
        print("-------------------")
