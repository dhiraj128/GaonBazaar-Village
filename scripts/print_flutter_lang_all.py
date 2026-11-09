import sys

sys.stdout.reconfigure(encoding='utf-8')

for p in [
    'apps/customer/lib/screens/language_selection_screen.dart',
    'apps/runner/lib/screens/runner_language_selection_screen.dart',
    'apps/vendor/lib/screens/vendor_language_selection_screen.dart'
]:
    with open(p, 'r', encoding='utf-8') as f:
        print(f"=== {p} ===")
        print(f.read())
