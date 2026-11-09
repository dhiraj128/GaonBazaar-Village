import sys
import os
import glob
import re

sys.stdout.reconfigure(encoding='utf-8')

for root, dirs, files in os.walk('public_web'):
    for f in files:
        if f.endswith(('.js', '.html')):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8', errors='ignore') as fp:
                txt = fp.read()
            matches = re.findall(r'.{0,30}(?:test_phone|test.*otp|9876543210|9811223344|123456|1234|TEST_CREDENTIALS|recaptchaVerifier).{0,30}', txt, re.IGNORECASE)
            if matches:
                print(f"=== {path} ({len(matches)} matches) ===")
                for m in matches[:5]:
                    print("  ", m.strip())
