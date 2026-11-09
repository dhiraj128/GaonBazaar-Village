import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/runner/index.html', 'r', encoding='utf-8') as f:
    runner = f.read()

# Let's inspect where screens start and end
# Screen 1: id="screen-onboarding-1"
# Screen 2: id="screen-onboarding-2"
# Screen 3: id="screen-onboarding-3"
# Screen 4: id="screen-onboarding-4"
# Screen 5: id="screen-onboarding-5"
# Screen 6: id="screen-onboarding-6"
# Screen 7: id="screen-onboarding-7"

# Let's find all onboarding screen IDs and their positions
matches = list(re.finditer(r'<div[^>]*id=[\"\']screen-onboarding-(\d+)[\"\']', runner))
for idx, m in enumerate(matches):
    print(f"Match {idx}: screen-onboarding-{m.group(1)} at {m.start()}")
