with open('public_web/customer/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update openCheckoutPaymentModal address resolution
target_open = """      // Check and validate address
      let addressId = selectedCheckoutAddressId;
      if (!addressId) {
        const village = (document.getElementById('checkout-village-input')?.value || '').trim();"""

replacement_open = """      // Check and validate address
      if (!selectedCheckoutAddressId && Array.isArray(userSavedAddresses) && userSavedAddresses.length > 0) {
        const def = userSavedAddresses.find(a => a.is_default) || userSavedAddresses[0];
        selectedCheckoutAddressId = def ? def.id : userSavedAddresses[0].id;
      }
      let addressId = selectedCheckoutAddressId;
      if (!addressId) {
        const village = (document.getElementById('checkout-village-input')?.value || '').trim();"""

if target_open in content:
    content = content.replace(target_open, replacement_open, 1)
    print("SUCCESS: openCheckoutPaymentModal address resolution updated")
else:
    print("Target open not found")

# 2. In saveCustomerAddress, set selectedCheckoutAddressId = authoritativeAddr.id
target_save = """        localStorage.setItem('gb_saved_addresses', JSON.stringify(userSavedAddresses));
        editingAddressId = null;

        closeModal('modal-rural-address');"""

replacement_save = """        localStorage.setItem('gb_saved_addresses', JSON.stringify(userSavedAddresses));
        editingAddressId = null;
        selectedCheckoutAddressId = authoritativeAddr.id;
        const noAddrCard = document.getElementById('checkout-no-address-card');
        if (noAddrCard) noAddrCard.classList.add('hidden');

        closeModal('modal-rural-address');"""

if target_save in content:
    content = content.replace(target_save, replacement_save, 1)
    print("SUCCESS: saveCustomerAddress selectedCheckoutAddressId updated")
else:
    print("Target save not found")

with open('public_web/customer/index.html', 'w', encoding='utf-8') as f:
    f.write(content)
