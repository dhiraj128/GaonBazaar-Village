import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/customer/index.html', 'r', encoding='utf-8') as f:
    customer = f.read()

matches = re.findall(r'.{0,30}isLocationServiceable.{0,30}', customer)
print("isLocationServiceable occurrences:", len(matches))
for m in matches:
    print(" - ", m)
