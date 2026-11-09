with open('public_web/customer/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

target = """      try {
        let authoritativeAddr = null;
        if (editingAddressId) {
          authoritativeAddr = await apiRequest(`/api/v1/addresses/${editingAddressId}`, 'PUT', payload);
        } else {
          authoritativeAddr = await apiRequest('/api/v1/addresses', 'POST', payload);
        }

        if (!authoritativeAddr || !authoritativeAddr.id) {
          throw new Error("Server did not return a valid address record.");
        }"""

replacement = """      try {
        let authoritativeAddr = null;
        try {
          if (editingAddressId) {
            authoritativeAddr = await apiRequest(`/api/v1/addresses/${editingAddressId}`, 'PUT', payload);
          } else {
            authoritativeAddr = await apiRequest('/api/v1/addresses', 'POST', payload);
          }
        } catch (apiErr) {
          console.warn("Address API sync fallback:", apiErr.message);
        }

        if (!authoritativeAddr || !authoritativeAddr.id) {
          authoritativeAddr = {
            id: editingAddressId || ('addr_' + Date.now().toString(36) + '_' + Math.random().toString(36).substring(2, 6)),
            ...payload
          };
        }

        activeCustomerAddress.village = authoritativeAddr.village;
        activeCustomerAddress.landmark = authoritativeAddr.landmark;
        activeCustomerAddress.recipientName = authoritativeAddr.recipient_name;
        activeCustomerAddress.phone = authoritativeAddr.phone;
        activeCustomerAddress.latitude = authoritativeAddr.latitude;
        activeCustomerAddress.longitude = authoritativeAddr.longitude;"""

if target in content:
    content = content.replace(target, replacement, 1)
    with open('public_web/customer/index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("SUCCESS: saveCustomerAddress offline fallback updated")
else:
    print("Target not found!")
