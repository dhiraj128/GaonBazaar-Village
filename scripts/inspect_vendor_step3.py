import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/vendor/index.html', 'r', encoding='utf-8') as f:
    vendor = f.read()

pos3 = vendor.find('id="screen-onboarding-3"')
pos4 = vendor.find('id="screen-onboarding-4"')
print(vendor[pos3:pos4])
