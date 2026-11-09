import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/vendor/index.html', 'r', encoding='utf-8') as f:
    vendor = f.read()

# Check where saveBasicDetailsAndProceed is defined
m = re.search(r'function saveBasicDetailsAndProceed\(\)[^{]*\{.*?\n    \}', vendor, re.DOTALL)
if m:
    print("Vendor saveBasicDetailsAndProceed:")
    print(m.group(0))

# Check where saveVendorLocationAndProceed is defined
m2 = re.search(r'function saveVendorLocationAndProceed\(\)[^{]*\{.*?\n    \}', vendor, re.DOTALL)
if m2:
    print("\nVendor saveVendorLocationAndProceed:")
    print(m2.group(0))

# Check where saveKycAndProceedToPayout is defined
m3 = re.search(r'function saveKycAndProceedToPayout\(\)[^{]*\{.*?\n    \}', vendor, re.DOTALL)
if m3:
    print("\nVendor saveKycAndProceedToPayout:")
    print(m3.group(0))
