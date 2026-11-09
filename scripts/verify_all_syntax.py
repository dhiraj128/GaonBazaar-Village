import re, subprocess, tempfile, os

files = [
    'public_web/customer/index.html',
    'public_web/vendor/index.html',
    'public_web/runner/index.html'
]
all_ok = True
for fpath in files:
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    scripts = re.findall(r'<script(?:\s+type="[^"]*")?>(.*?)</script>', content, re.DOTALL)
    print(f'Checking {fpath}: found {len(scripts)} inline scripts')
    for i, s in enumerate(scripts):
        if not s.strip():
            continue
        with tempfile.NamedTemporaryFile(suffix='.js', delete=False, mode='w', encoding='utf-8') as tmp:
            tmp.write(s)
            tmp_path = tmp.name
        try:
            res = subprocess.run(['node', '--check', tmp_path], capture_output=True, text=True)
            if res.returncode != 0:
                print(f'ERROR in {fpath} script {i}:\n{res.stderr}')
                all_ok = False
            else:
                print(f'  Script {i}: Syntax OK')
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

if all_ok:
    print('ALL SCRIPTS SYNTAX PERFECT!')
else:
    exit(1)
