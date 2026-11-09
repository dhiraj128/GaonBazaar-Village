import sys
import os
import re

sys.stdout.reconfigure(encoding='utf-8')

patterns = ['LanguageSelection', 'MobileLogin', 'operation-not-allowed', 'Continue ->', 'Continue →']

for root, dirs, files in os.walk('.'):
    if '.git' in root or '.venv' in root:
        continue
    for f in files:
        path = os.path.join(root, f)
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as fp:
                txt = fp.read()
            for p in patterns:
                if p.lower() in txt.lower():
                    print(f"Match '{p}' in {path}")
        except Exception:
            pass
