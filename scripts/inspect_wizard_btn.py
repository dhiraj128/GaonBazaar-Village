import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('apps/runner/lib/screens/runner_onboarding_wizard.dart', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(380, 430):
    if i < len(lines):
        print(f"{i+1}: {lines[i]}", end='')
