import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/customer/index.html', 'r', encoding='utf-8') as f:
    customer = f.read()

funcs = re.findall(r'function [a-zA-Z0-9_]*(?:cart|badge)[a-zA-Z0-9_]*\([^)]*\)', customer, re.IGNORECASE)
print("Cart/badge functions in customer:", funcs)
