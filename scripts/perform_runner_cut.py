import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/runner/index.html', 'r', encoding='utf-8') as f:
    runner = f.read()

pos_cut_start = runner.find('<!-- PAGE 6: BANK / UPI PAYOUT SETUP (ACTIVE & INTERACTIVE) -->')
pos_cut_end = runner.find('<!-- PAGE 6: BANK / UPI PAYOUT SETUP (ACTIVE & INTERACTIVE) -->', pos_cut_start + 100)

print(f"Cutting from {pos_cut_start} to {pos_cut_end}...")
clean_runner = runner[:pos_cut_start] + runner[pos_cut_end:]

matches = list(re.finditer(r'<div[^>]*id=[\"\']screen-onboarding-(\d+)[\"\']', clean_runner))
print(f"Screens after cut: {len(matches)}")
for idx, m in enumerate(matches):
    print(f"[{idx}] screen-onboarding-{m.group(1)} at {m.start()}")

tabs = list(re.finditer(r'id=[\"\'](tab-[a-z0-9_-]+)[\"\']', clean_runner))
print(f"Tabs after cut: {len(tabs)}")
for t in tabs:
    print(f"Tab: {t.group(1)} at {t.start()}")

with open('public_web/runner/index.html', 'w', encoding='utf-8') as f:
    f.write(clean_runner)

print("Saved clean runner/index.html successfully.")
