import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/runner/index.html', 'r', encoding='utf-8') as f:
    runner = f.read()

# 1. Remove duplicate Match 5: old screen-onboarding-5 between KYC and screen-onboarding-6
# It starts with '<!-- PAGE 5: LOCATION SETUP (DELIVERY RADIUS & OPERATING HUB) -->' and ends before '<!-- PAGE 6: BANK / UPI PAYOUT SETUP'
old_dup_loc = re.search(r'<!--\s*PAGE 5:\s*LOCATION SETUP \(DELIVERY RADIUS & OPERATING HUB\)\s*-->\s*<div id="screen-onboarding-5".*?(?=<!--\s*PAGE 6:\s*BANK / UPI PAYOUT SETUP)', runner, re.DOTALL)
if old_dup_loc:
    print("Found old duplicate location block in runner, removing...")
    runner = runner[:old_dup_loc.start()] + runner[old_dup_loc.end():]

# 2. Remove duplicate Match 8 and 9 at the end of dashboard (around 67000+)
# Starts with '<!-- PAGE 6: BANK / UPI PAYOUT SETUP (ACTIVE & INTERACTIVE) -->' and ends before the bottom tabs or script
dup_end_block = re.search(r'<!--\s*PAGE 6:\s*BANK / UPI PAYOUT SETUP \(ACTIVE & INTERACTIVE\)\s*-->\s*<div id="screen-onboarding-6".*?</div>\s*</div>\s*(?=<!--\s*BOTTOM NAVIGATION BAR|\s*<nav id="bottom-tabs")', runner, re.DOTALL)
if dup_end_block:
    print("Found duplicate end block (screens 6 & 7) in runner, removing...")
    runner = runner[:dup_end_block.start()] + runner[dup_end_block.end():]

with open('public_web/runner/index.html', 'w', encoding='utf-8') as f:
    f.write(runner)

# Now check remaining screens
matches = list(re.finditer(r'<div[^>]*id=[\"\']screen-onboarding-(\d+)[\"\']', runner))
print(f"Remaining screens in runner: {len(matches)}")
for idx, m in enumerate(matches):
    print(f"[{idx}] screen-onboarding-{m.group(1)} at {m.start()}")
