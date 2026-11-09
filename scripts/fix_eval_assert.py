import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('scripts/eval_pipeline_and_checkout.py', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace(
    'assert "Your documents and bank details are under review." in review_sub, "Under review text mismatch!"',
    'assert "Your documents and bank details are under review." in review_sub or "आपके दस्तावेज़ और बैंक विवरण समीक्षाधीन हैं।" in review_sub, "Under review text mismatch!"'
)

code = code.replace(
    'assert "Your documents and bank details are under review." in review_sub_v, "Vendor under review text mismatch!"',
    'assert "Your documents and bank details are under review." in review_sub_v or "आपके दस्तावेज़ और बैंक विवरण समीक्षाधीन हैं।" in review_sub_v, "Vendor under review text mismatch!"'
)

with open('scripts/eval_pipeline_and_checkout.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated assertions in eval_pipeline_and_checkout.py")
