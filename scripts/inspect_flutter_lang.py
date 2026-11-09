import sys

sys.stdout.reconfigure(encoding='utf-8')

for path in [
    'apps/customer/lib/screens/language_selection_screen.dart',
    'apps/runner/lib/screens/runner_language_selection_screen.dart',
    'apps/vendor/lib/screens/vendor_language_selection_screen.dart'
]:
    with open(path, 'r', encoding='utf-8') as f:
        print(f"=== {path} ===")
        print(f.read())
