import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/vendor/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update Step 3: Remove Full Name and Emergency Contact fields
# Keep ONLY Shop Name and Shop Category
old_step3_fields = re.search(r'(<div class="space-y-4">.*?)(?=\s*</div>\s*</div>\s*<div class="pt-6">)', content, re.DOTALL)
if old_step3_fields:
    print("Found step 3 fields block in vendor")
    new_step3_fields = '''<div class="space-y-4">
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1" data-i18n="shop_name_label">Shop / Business Name <span class="text-rose-500">*</span></label>
              <input type="text" id="vendor-shopname" value="Sharma Kirana & General Store" placeholder="e.g. Sharma Kirana & General Store" data-i18n-placeholder="shopname_placeholder" class="w-full px-3.5 py-3 rounded-xl border border-slate-300 bg-white text-slate-900 font-bold focus:border-emerald-600 focus:ring-2 focus:ring-emerald-100 focus:outline-none shadow-xs">
            </div>

            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1" data-i18n="shop_category_label">Store Category <span class="text-rose-500">*</span></label>
              <select id="vendor-category" class="w-full px-3.5 py-3 rounded-xl border border-slate-300 bg-white text-slate-900 font-medium focus:border-emerald-600 focus:ring-2 focus:ring-emerald-100 focus:outline-none shadow-xs">
                <option value="Grocery & Kirana" data-i18n="cat_grocery">Grocery & Kirana (राशन एवं किराना)</option>
                <option value="Dairy & Milk Products" data-i18n="cat_dairy">Dairy & Milk (दूध एवं डेयरी)</option>
                <option value="Fresh Fruits & Vegetables" data-i18n="cat_veggies">Vegetables & Fruits (सब्जी एवं फल)</option>
                <option value="Pharmacy & Healthcare" data-i18n="cat_pharmacy">Pharmacy & Medicines (दवाइयाँ)</option>
                <option value="Electronics & Mobile" data-i18n="cat_electronics">Mobile & Electronics (इलेक्ट्रॉनिक्स)</option>
              </select>
            </div>
          </div>'''
    content = content.replace(old_step3_fields.group(1), new_step3_fields, 1)

# Update subtext for step 3
content = content.replace(
    'Enter your business and personal details',
    'Enter your shop and business details'
)

# 2. Extract screen-onboarding-4 (KYC) and screen-onboarding-5 (Location)
# Swap them: Location becomes screen-onboarding-4 (Step 4), KYC becomes screen-onboarding-5 (Step 5)

m_kyc = re.search(r'(<!--[^\n]*PAGE 4:[^\n]*-->\s*<div id="screen-onboarding-4".*?)(?=<!--[^\n]*PAGE 5:)', content, re.DOTALL)
m_loc = re.search(r'(<!--[^\n]*PAGE 5:[^\n]*-->\s*<div id="screen-onboarding-5".*?)(?=<!--[^\n]*PAGE 6:)', content, re.DOTALL)

print("m_kyc found:", bool(m_kyc))
print("m_loc found:", bool(m_loc))

if m_kyc and m_loc:
    kyc_block = m_kyc.group(1)
    loc_block = m_loc.group(1)

    # In Location block: change to Step 4 of 7, change id to screen-onboarding-4
    # button: "Save & Continue to KYC" -> saveVendorLocationAndProceed()
    new_loc_block = loc_block
    new_loc_block = new_loc_block.replace('<!-- PAGE 5: LOCATION SETUP (SHOP ADDRESS & MAP PIN) -->', '<!-- PAGE 4: LOCATION SETUP (SHOP ADDRESS & MAP PIN) -->')
    new_loc_block = new_loc_block.replace('id="screen-onboarding-5"', 'id="screen-onboarding-4"')
    if 'Step 4 of 7' not in new_loc_block:
        new_loc_block = re.sub(
            r'(<div class="space-y-4">\s*<!-- Header -->\s*<div>)',
            r'\1\n            <div class="flex items-center space-x-2 text-emerald-600 text-xs font-bold uppercase tracking-wider mb-2"><span class="px-2 py-0.5 bg-emerald-100 rounded">Step 4 of 7</span><span>Store Location</span></div>',
            new_loc_block,
            1
        )
    new_loc_block = new_loc_block.replace('Save & Continue to Payout', 'Save & Continue to KYC')
    new_loc_block = new_loc_block.replace('data-i18n="save_location_btn">Save & Continue to Payout<', 'data-i18n="save_location_btn">Save & Continue to KYC<')

    # In KYC block: change to Step 5 of 7, change id to screen-onboarding-5
    new_kyc_block = kyc_block
    new_kyc_block = new_kyc_block.replace('<!-- PAGE 4: IDENTITY VERIFICATION (SINGLE ID SELECTION) -->', '<!-- PAGE 5: IDENTITY VERIFICATION (SINGLE ID SELECTION) -->')
    new_kyc_block = new_kyc_block.replace('id="screen-onboarding-4"', 'id="screen-onboarding-5"')
    new_kyc_block = re.sub(r'Step 4 of 7', 'Step 5 of 7', new_kyc_block)
    if 'Step 5 of 7' not in new_kyc_block:
        new_kyc_block = re.sub(
            r'(<div class="space-y-4">\s*<!-- Header [^>]*-->\s*<div>)',
            r'\1\n            <div class="flex items-center space-x-2 text-emerald-600 text-xs font-bold uppercase tracking-wider mb-2"><span class="px-2 py-0.5 bg-emerald-100 rounded">Step 5 of 7</span><span>Identity Verification</span></div>',
            new_kyc_block,
            1
        )
    new_kyc_block = new_kyc_block.replace('Continue to Location Setup', 'Continue to Payout Setup')
    new_kyc_block = new_kyc_block.replace('Save & Continue to Location', 'Continue to Payout Setup')

    # Now replace the entire region: [kyc_block + loc_block] with [new_loc_block + new_kyc_block]
    combined_old = content[m_kyc.start():m_loc.end()]
    combined_new = new_loc_block + '\n\n      ' + new_kyc_block
    content = content[:m_kyc.start()] + combined_new + content[m_loc.end():]
    print("Successfully swapped Step 4 (Location) and Step 5 (KYC) in vendor!")

# 3. Update Step 7 review subtext and remove any OCR/DigiLocker references
content = re.sub(
    r'<p class="text-sm text-slate-600 max-w-xs mb-6" data-i18n="under_review_sub">.*?</p>',
    r'<p class="text-sm text-slate-600 max-w-xs mb-6" data-i18n="under_review_sub">Your documents and bank details are under review.</p>',
    content,
    flags=re.DOTALL
)

with open('public_web/vendor/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Vendor HTML updated successfully.")
