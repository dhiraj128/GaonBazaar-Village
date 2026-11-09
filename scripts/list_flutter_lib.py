import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

for app in ['customer', 'runner', 'vendor', 'admin']:
    p = f'apps/{app}/lib'
    if os.path.exists(p):
        print(f"=== {p} ===")
        for root, dirs, files in os.walk(p):
            for f in files:
                print(os.path.join(root, f).replace('\\', '/'))
