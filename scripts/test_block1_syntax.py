import sys
import re
import subprocess

sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/customer/index.html', 'r', encoding='utf-8') as f:
    customer = f.read()

scripts = re.findall(r'<script>(.*?)</script>', customer, re.DOTALL)
block1 = scripts[1]

with open('scripts/temp_block1.js', 'w', encoding='utf-8') as f:
    f.write(block1)

res = subprocess.run(["node", "--check", "scripts/temp_block1.js"], capture_output=True, text=True)
print("Node check return code:", res.returncode)
print("Node check stdout:", res.stdout)
print("Node check stderr:", res.stderr)
