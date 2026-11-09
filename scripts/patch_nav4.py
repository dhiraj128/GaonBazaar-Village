# Update vendor
with open('public_web/vendor/index.html', 'r', encoding='utf-8') as f:
    v_text = f.read()

v_old = """        if (screenId === 'onboarding-4') {
          setTimeout(() => {
            if (typeof initVendorMap === 'function') initVendorMap();
            if (window.vendorMap) window.vendorMap.invalidateSize();
          }, 150);
        }"""

v_new = """        if (screenId === 'onboarding-4') {
          setTimeout(() => {
            const vInput = document.getElementById('vendor-village-name');
            if (vInput && !vInput.value) vInput.value = 'Muzaffarpur';
          }, 150);
        }"""

if v_old in v_text:
    v_text = v_text.replace(v_old, v_new)
    with open('public_web/vendor/index.html', 'w', encoding='utf-8') as f:
        f.write(v_text)
    print("Vendor on-nav-4 updated.")
else:
    print("Vendor on-nav-4 not matched.")

# Update runner
with open('public_web/runner/index.html', 'r', encoding='utf-8') as f:
    r_text = f.read()

r_old = """        if (screenId === 'onboarding-4') {
          setTimeout(() => {
            if (typeof initRunnerMap === 'function') initRunnerMap();
            if (window.runnerMap) window.runnerMap.invalidateSize();
          }, 150);
        }"""

r_new = """        if (screenId === 'onboarding-4') {
          setTimeout(() => {
            const rInput = document.getElementById('runner-base-village');
            if (rInput && !rInput.value) rInput.value = 'Muzaffarpur';
          }, 150);
        }"""

if r_old in r_text:
    r_text = r_text.replace(r_old, r_new)
    with open('public_web/runner/index.html', 'w', encoding='utf-8') as f:
        f.write(r_text)
    print("Runner on-nav-4 updated.")
else:
    print("Runner on-nav-4 not matched.")
