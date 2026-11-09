import sys
import re
import subprocess

sys.stdout.reconfigure(encoding='utf-8')

for app in ['runner', 'vendor', 'customer']:
    with open(f'public_web/{app}/index.html', 'r', encoding='utf-8') as f:
        html = f.read()
    scripts = re.findall(r'<script>(.*?)</script>', html, re.DOTALL)
    for idx, s in enumerate(scripts):
        fname = f'scripts/temp_{app}_{idx}.js'
        with open(fname, 'w', encoding='utf-8') as f:
            f.write(s)
        res = subprocess.run(["node", "--check", fname], capture_output=True)
        print(f"{app.upper()} script block {idx}: exit {res.returncode}")
        if res.returncode != 0:
            print("Stderr:", res.stderr.decode('utf-8', errors='replace'))
