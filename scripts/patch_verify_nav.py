with open('scripts/verify_complete_checkout_and_fixes_cdp.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace("nextStep(3); // Step 3: Location setup", "navigateTo('screen-onboarding-4');")
text = text.replace("nextStep(3); // Step 3: Location Hub Setup", "navigateTo('screen-onboarding-4');")

with open('scripts/verify_complete_checkout_and_fixes_cdp.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated navigateTo in verify script")
