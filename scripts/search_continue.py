import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

for root, dirs, files in os.walk('.'):
    if '.git' in root or '.venv' in root or 'node_modules' in root or 'build' in root or '.dart_tool' in root:
        continue
    for f in files:
        if f.endswith(('.dart', '.html', '.js', '.jsx', '.tsx', '.ts')):
            path = os.path.join(root, f)
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as fp:
                    content = fp.read()
                if 'Continue' in content:
                    for line_no, line in enumerate(content.splitlines(), start=1):
                        if 'Continue' in line:
                            print(f"{path}:{line_no} -> {line.strip()[:100]}")
            except Exception:
                pass
