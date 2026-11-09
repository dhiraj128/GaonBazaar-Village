with open('scripts/verify_complete_checkout_and_fixes_cdp.py', 'r', encoding='utf-8') as f:
    text = f.read()

idx1 = text.find('=== PART 4: Testing Dynamic Single-Language Dropdowns (Vendor App) ===')
idx2 = text.find('=== PART 5: Testing Dynamic Single-Language Dropdowns (Runner App) ===')

replacement = """=== PART 4: Testing Dynamic Single-Language Dropdowns (Vendor App) ===\")
            await eval_js(ws, \"window.location.href = 'http://127.0.0.1:8120/vendor/index.html'\", mid); mid += 1
            await asyncio.sleep(2)

            await eval_js(ws, \"\"\"
                localStorage.clear();
                sessionStorage.clear();
                location.reload();
            \"\"\", mid); mid += 1
            await asyncio.sleep(2)

            # Go to location step in Vendor app
            await eval_js(ws, \"\"\"
                setLanguage('en');
                navigateTo('screen-onboarding-4');
            \"\"\", mid); mid += 1
            await asyncio.sleep(1)

            # Trigger vendor village dropdown in English mode
            await eval_js(ws, \"\"\"
                handleVendorVillageSearch('');
            \"\"\", mid); mid += 1
            await asyncio.sleep(0.5)

            en_options = await eval_js(ws, \"\"\"
                Array.from(document.querySelectorAll('#vendor-village-dropdown span.village-label')).map(el => el.innerText.trim())
            \"\"\", mid); mid += 1
            print(f\"Vendor English Dropdown Options (sample 5): {en_options[:5] if en_options else 'None'}\")
            assert en_options and len(en_options) > 0, \"Vendor village dropdown options must be rendered!\"
            assert all('/' not in opt for opt in en_options), \"Vendor English dropdown must not contain slashes ('/')!\"
            assert all(not any('\\u0900' <= char <= '\\u097F' for char in opt) for opt in en_options), \"Vendor English dropdown must not contain Hindi characters!\"

            # Now toggle to Hindi mode and verify dropdown contains ONLY Hindi
            debug_res = await eval_js(ws, \"\"\"
                (() => {
                    try {
                        setLanguage('hi');
                        handleVendorVillageSearch('');
                        return 'OK: currentLang=' + window.currentLang;
                    } catch(err) {
                        return 'ERR: ' + err.message;
                    }
                })()
            \"\"\", mid); mid += 1
            print(f\"Toggle Hindi result: {debug_res}\")
            await asyncio.sleep(0.5)

            hi_options = await eval_js(ws, \"\"\"
                Array.from(document.querySelectorAll('#vendor-village-dropdown span.village-label')).map(el => el.innerText.trim())
            \"\"\", mid); mid += 1
            print(f\"Vendor Hindi Dropdown Options (sample 5): {hi_options[:5] if hi_options else 'None'}\")
            assert hi_options and len(hi_options) > 0, \"Vendor Hindi dropdown options must be rendered!\"
            assert all('/' not in opt for opt in hi_options), \"Vendor Hindi dropdown must not contain slashes ('/')!\"
            assert any(any('\\u0900' <= char <= '\\u097F' for char in opt) for opt in hi_options), \"Vendor Hindi dropdown must display Hindi characters!\"

            await take_screenshot(ws, \"proof_single_language_dropdown_vendor.png\", mid); mid += 1

            # """

text = text[:idx1] + replacement + text[idx2:]

with open('scripts/verify_complete_checkout_and_fixes_cdp.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated Part 4 in verify script")
