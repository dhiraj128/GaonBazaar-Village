import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/runner/index.html', 'r', encoding='utf-8') as f:
    runner = f.read()

# Check where saveRunnerDetailsAndProceed is defined
m = re.search(r'function saveRunnerDetailsAndProceed\(\)[^{]*\{.*?\n    \}', runner, re.DOTALL)
if m:
    print("Runner saveRunnerDetailsAndProceed:")
    print(m.group(0))

# Check where saveRunnerLocationAndProceed is defined
m2 = re.search(r'function saveRunnerLocationAndProceed\(\)[^{]*\{.*?\n    \}', runner, re.DOTALL)
if m2:
    print("\nRunner saveRunnerLocationAndProceed:")
    print(m2.group(0))

# Check where saveKycAndProceedToPayout is defined
m3 = re.search(r'function saveKycAndProceedToPayout\(\)[^{]*\{.*?\n    \}', runner, re.DOTALL)
if m3:
    print("\nRunner saveKycAndProceedToPayout:")
    print(m3.group(0))
