import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/runner/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update Step 3: Remove Full Name and Emergency Contact fields
# Keep ONLY Vehicle Type dropdown and Vehicle Registration Number text input
old_step3_fields = re.search(r'(<div class="space-y-4">.*?)(?=\s*</div>\s*</div>\s*<div class="pt-6">)', content, re.DOTALL)
if old_step3_fields:
    print("Found step 3 fields block in runner")
    new_step3_fields = '''<div class="space-y-4">
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1" data-i18n="vehicle_type_label">Vehicle Type <span class="text-rose-500">*</span></label>
              <select id="runner-vehicletype" class="w-full px-3.5 py-3 rounded-xl border border-slate-300 bg-white text-slate-900 font-medium focus:border-blue-600 focus:ring-2 focus:ring-blue-100 focus:outline-none shadow-xs">
                <option value="Motorcycle (Petrol Bike)" data-i18n="opt_bike">Motorcycle / Hero Splendor (Petrol Bike)</option>
                <option value="Electric Scooter (EV)" data-i18n="opt_ev">Electric Scooter / EV 2-Wheeler</option>
                <option value="Bicycle (Standard Cycle)" data-i18n="opt_cycle">Bicycle (साइकिल)</option>
                <option value="Auto / 3-Wheeler" data-i18n="opt_auto">Auto / E-Rickshaw</option>
              </select>
            </div>

            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1" data-i18n="vehicle_number_label">Vehicle Registration Number <span class="text-rose-500">*</span></label>
              <input type="text" id="runner-vehicleno" value="UP 32 BK 4821" placeholder="e.g. UP 32 AB 1234" data-i18n-placeholder="vehicleno_placeholder" class="w-full px-3.5 py-3 rounded-xl border border-slate-300 bg-white text-slate-900 font-mono uppercase font-bold focus:border-blue-600 focus:ring-2 focus:ring-blue-100 focus:outline-none shadow-xs">
            </div>
          </div>'''
    content = content.replace(old_step3_fields.group(1), new_step3_fields, 1)

# Update subtext for step 3
content = content.replace(
    'Enter your vehicle and emergency contacts',
    'Enter your vehicle details for delivery operations'
)

# 2. Extract screen-onboarding-4 (KYC) and screen-onboarding-5 (Location)
# Swap them: Location becomes screen-onboarding-4 (Step 4), KYC becomes screen-onboarding-5 (Step 5)

m_kyc = re.search(r'(<!--\s*PAGE 4: IDENTITY VERIFICATION.*?<div id="screen-onboarding-4".*?</div>\s*</div>\s*</div>\s*</div>)', content, re.DOTALL)
if not m_kyc:
    # try broader match
    m_kyc = re.search(r'(<!--[^\n]*PAGE 4:[^\n]*-->\s*<div id="screen-onboarding-4".*?)(?=<!--[^\n]*PAGE 5:)', content, re.DOTALL)

m_loc = re.search(r'(<!--[^\n]*PAGE 5:[^\n]*-->\s*<div id="screen-onboarding-5".*?)(?=<!--[^\n]*PAGE 6:)', content, re.DOTALL)

print("m_kyc found:", bool(m_kyc))
print("m_loc found:", bool(m_loc))

if m_kyc and m_loc:
    kyc_block = m_kyc.group(1)
    loc_block = m_loc.group(1)

    # In Location block: change to Step 4 of 7, change id to screen-onboarding-4
    # button: "Save & Continue to KYC" -> saveRunnerLocationAndProceed()
    new_loc_block = loc_block
    new_loc_block = new_loc_block.replace('<!-- PAGE 5: LOCATION SETUP (DELIVERY RADIUS & OPERATING HUB) -->', '<!-- PAGE 4: LOCATION SETUP (DELIVERY RADIUS & OPERATING HUB) -->')
    new_loc_block = new_loc_block.replace('id="screen-onboarding-5"', 'id="screen-onboarding-4"')
    # Add step 4 badge if not present
    if 'Step 4 of 7' not in new_loc_block:
        new_loc_block = re.sub(
            r'(<div class="space-y-4">\s*<!-- Header -->\s*<div>)',
            r'\1\n            <div class="flex items-center space-x-2 text-blue-600 text-xs font-bold uppercase tracking-wider mb-2"><span class="px-2 py-0.5 bg-blue-100 rounded">Step 4 of 7</span><span>Service Area</span></div>',
            new_loc_block,
            1
        )
    new_loc_block = new_loc_block.replace('Save & Continue to Payout', 'Save & Continue to KYC')
    new_loc_block = new_loc_block.replace('data-i18n="save_location_btn">Save & Continue to Payout<', 'data-i18n="save_location_btn">Save & Continue to KYC<')

    # In KYC block: change to Step 5 of 7, change id to screen-onboarding-5
    new_kyc_block = kyc_block
    new_kyc_block = new_kyc_block.replace('<!-- PAGE 4: IDENTITY VERIFICATION (SINGLE ID SELECTION) -->', '<!-- PAGE 5: IDENTITY VERIFICATION (SINGLE ID SELECTION) -->')
    new_kyc_block = new_kyc_block.replace('id="screen-onboarding-4"', 'id="screen-onboarding-5"')
    # update step badge to Step 5 of 7
    new_kyc_block = re.sub(r'Step 4 of 7', 'Step 5 of 7', new_kyc_block)
    if 'Step 5 of 7' not in new_kyc_block:
        new_kyc_block = re.sub(
            r'(<div class="space-y-4">\s*<!-- Header [^>]*-->\s*<div>)',
            r'\1\n            <div class="flex items-center space-x-2 text-blue-600 text-xs font-bold uppercase tracking-wider mb-2"><span class="px-2 py-0.5 bg-blue-100 rounded">Step 5 of 7</span><span>Identity Verification</span></div>',
            new_kyc_block,
            1
        )
    # Button in KYC block should proceed to Payout
    new_kyc_block = new_kyc_block.replace('Continue to Location Setup', 'Continue to Payout Setup')
    new_kyc_block = new_kyc_block.replace('Save & Continue to Location', 'Continue to Payout Setup')

    # Now replace the entire region: [kyc_block + loc_block] with [new_loc_block + new_kyc_block]
    combined_old = content[m_kyc.start():m_loc.end()]
    combined_new = new_loc_block + '\n\n      ' + new_kyc_block
    content = content[:m_kyc.start()] + combined_new + content[m_loc.end():]
    print("Successfully swapped Step 4 (Location) and Step 5 (KYC) in runner!")

# 3. Update Step 7 review subtext and remove any OCR/DigiLocker references
content = re.sub(
    r'<p class="text-sm text-slate-600 max-w-xs mb-6" data-i18n="under_review_sub_runner">.*?</p>',
    r'<p class="text-sm text-slate-600 max-w-xs mb-6" data-i18n="under_review_sub_runner">Your documents and bank details are under review.</p>',
    content,
    flags=re.DOTALL
)

with open('public_web/runner/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Runner HTML updated successfully.")
