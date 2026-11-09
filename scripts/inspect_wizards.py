import sys

sys.stdout.reconfigure(encoding='utf-8')

for p in [
    'apps/runner/lib/screens/runner_onboarding_wizard.dart',
    'apps/vendor/lib/screens/vendor_onboarding_wizard.dart'
]:
    with open(p, 'r', encoding='utf-8') as f:
        txt = f.read()
    print(f"=== {p} ===")
    for line_no, line in enumerate(txt.splitlines(), start=1):
        if 'Continue' in line or 'आगे बढ़ें' in line or 'Language' in line:
            print(f"Line {line_no}: {line.strip()}")
