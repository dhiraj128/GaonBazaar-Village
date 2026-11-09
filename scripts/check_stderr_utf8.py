import sys
import subprocess

sys.stdout.reconfigure(encoding='utf-8')

for name in ['scripts/temp_runner_1.js', 'scripts/temp_vendor_1.js']:
    res = subprocess.run(["node", "--check", name], capture_output=True)
    print(f"=== {name} ===")
    print("Code:", res.returncode)
    print("Stderr:", res.stderr.decode('utf-8', errors='replace'))
