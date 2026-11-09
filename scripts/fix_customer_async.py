import sys
import subprocess

sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/customer/index.html', 'r', encoding='utf-8') as f:
    customer = f.read()

customer = customer.replace('function placeCustomerOrder() {', 'async function placeCustomerOrder() {', 1)

with open('public_web/customer/index.html', 'w', encoding='utf-8') as f:
    f.write(customer)

import re
scripts = re.findall(r'<script>(.*?)</script>', customer, re.DOTALL)
with open('scripts/temp_block1.js', 'w', encoding='utf-8') as f:
    f.write(scripts[1])

res = subprocess.run(["node", "--check", "scripts/temp_block1.js"], capture_output=True, text=True)
print("Node check return code:", res.returncode)
print("Node check stderr:", res.stderr)
