import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

# 1. Update runner/index.html
with open('public_web/runner/index.html', 'r', encoding='utf-8') as f:
    runner = f.read()

runner = re.sub(
    r'under_review_sub_runner:\s*"[^"]*"',
    'under_review_sub_runner: "Your documents and bank details are under review."',
    runner,
    count=1
)
runner = re.sub(
    r'under_review_sub_runner:\s*"[^"]*"',
    'under_review_sub_runner: "आपके दस्तावेज़ और बैंक विवरण समीक्षाधीन हैं।",',
    runner,
    count=1
)

with open('public_web/runner/index.html', 'w', encoding='utf-8') as f:
    f.write(runner)

# 2. Update vendor/index.html
with open('public_web/vendor/index.html', 'r', encoding='utf-8') as f:
    vendor = f.read()

vendor = re.sub(
    r'under_review_sub:\s*"[^"]*"',
    'under_review_sub: "Your documents and bank details are under review."',
    vendor,
    count=1
)
vendor = re.sub(
    r'under_review_sub:\s*"[^"]*"',
    'under_review_sub: "आपके दस्तावेज़ और बैंक विवरण समीक्षाधीन हैं।",',
    vendor,
    count=1
)

with open('public_web/vendor/index.html', 'w', encoding='utf-8') as f:
    f.write(vendor)

print("Updated translations for runner and vendor under_review text.")
