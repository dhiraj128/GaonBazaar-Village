import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('scripts/capture_all_proof_screenshots.py', 'r', encoding='utf-8') as f:
    code = f.read()

print(code[:1500])
