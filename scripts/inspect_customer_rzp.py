import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/customer/index.html', 'r', encoding='utf-8') as f:
    customer = f.read()

rzp = re.findall(r'.{0,50}Razorpay.{0,50}', customer)
print("Razorpay mentions in customer:", len(rzp))
for r in rzp[:5]:
    print(" - ", r)

upi = re.findall(r'.{0,50}upi.{0,50}', customer, re.IGNORECASE)
print("UPI mentions in customer:", len(upi))
for u in upi[:5]:
    print(" - ", u)
