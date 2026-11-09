import sys
import os
import re

sys.stdout.reconfigure(encoding='utf-8')

for root, dirs, files in os.walk('.'):
    if '.git' in root or 'node_modules' in root or '.venv' in root:
        continue
    for f in files:
        path = os.path.join(root, f)
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as fp:
                txt = fp.read()
            if 'LanguageSelection' in txt or 'MobileLogin' in txt:
                print("Found match in:", path)
        except Exception:
            pass
