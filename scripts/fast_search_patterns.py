import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

patterns = ['LanguageSelection', 'MobileLogin', 'operation-not-allowed', 'Continue ->', 'Continue →']

for root, dirs, files in os.walk('.'):
    if any(x in root for x in ['.git', '.venv', 'node_modules', 'build', '.dart_tool']):
        continue
    for f in files:
        if f.endswith(('.dart.js', '.map', '.wasm', '.png', '.jpg', '.ico', '.csv')):
            continue
        path = os.path.join(root, f)
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as fp:
                txt = fp.read()
            for p in patterns:
                if p.lower() in txt.lower():
                    print(f"Match '{p}' in {path}")
        except Exception as e:
            pass
