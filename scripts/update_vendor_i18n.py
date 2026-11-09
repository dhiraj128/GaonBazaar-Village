with open('public_web/vendor/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Add i18n keys if needed
if "action_scan_barcode:" not in content:
    target_en = 'inventory_title: "Live Catalog & Stock",'
    replace_en = target_en + '\n        action_scan_barcode: "Scan Barcode (FMCG)",\n        action_take_photo: "Take Photo (Fresh/Loose)",'
    content = content.replace(target_en, replace_en, 1)

    target_hi = 'inventory_title: "दुकान का सामान और स्टॉक",'
    if target_hi in content:
        replace_hi = target_hi + '\n        action_scan_barcode: "बारकोड स्कैन करें",\n        action_take_photo: "फोटो खींचे",'
        content = content.replace(target_hi, replace_hi, 1)

    with open('public_web/vendor/index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("SUCCESS: i18n keys updated")
else:
    print("i18n keys already present")
