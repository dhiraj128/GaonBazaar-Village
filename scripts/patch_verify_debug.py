with open('scripts/verify_complete_checkout_and_fixes_cdp.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = """            # Now toggle to Hindi mode and verify dropdown contains ONLY Hindi
            await eval_js(ws, \"\"\"
                setLanguage('hi');
                const inp = document.getElementById('vendor-village-name');
                if (inp) {
                    inp.value = '';
                    handleVendorVillageSearch('');
                }
            \"\"\", mid); mid += 1"""

replacement = """            # Now toggle to Hindi mode and verify dropdown contains ONLY Hindi
            debug_info = await eval_js(ws, \"\"\"
                setLanguage('hi');
                const inp = document.getElementById('vendor-village-name');
                if (inp) {
                    inp.value = '';
                    handleVendorVillageSearch('');
                }
                ({
                    currentLang: typeof currentLang !== 'undefined' ? currentLang : null,
                    winLang: window.currentLang,
                    localLang: localStorage.getItem('gaonbazaar_vendor_lang'),
                    firstHtml: document.getElementById('vendor-village-dropdown')?.innerHTML?.substring(0, 200)
                })
            \"\"\", mid); mid += 1
            print("DEBUG HINDI EVAL:", debug_info)"""

assert target in text
text = text.replace(target, replacement, 1)

with open('scripts/verify_complete_checkout_and_fixes_cdp.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Added debug info to verify script")
