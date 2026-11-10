import re

# 1. PATCH VENDOR APP
with open('public_web/vendor/index.html', 'r', encoding='utf-8') as f:
    v = f.read()

# Fix updateOrdersUIFromData with strict null-checks and default array
old_update_orders = '''    function updateOrdersUIFromData(orders) {
      const placed = orders.filter(o => o.status === 'PLACED');
      const preparing = orders.filter(o => o.status === 'ACCEPTED' || o.status === 'PREPARING');
      const ready = orders.filter(o => o.status === 'PACKED' || o.status === 'RUNNER_ASSIGNED');

      const newBadge = document.getElementById('new-orders-badge');
      const prepBadge = document.getElementById('prep-orders-badge');
      const readyBadge = document.getElementById('ready-orders-badge');

      if (newBadge) newBadge.innerText = String(placed.length);
      if (prepBadge) prepBadge.innerText = String(preparing.length);
      if (readyBadge) readyBadge.innerText = String(ready.length);

      const newEmpty = document.getElementById('new-orders-empty');
      const prepEmpty = document.getElementById('prep-orders-empty');
      const readyEmpty = document.getElementById('ready-orders-empty');

      if (newEmpty) newEmpty.classList.toggle('hidden', placed.length > 0);
      if (prepEmpty) prepEmpty.classList.toggle('hidden', preparing.length > 0);
      if (readyEmpty) readyEmpty.classList.toggle('hidden', ready.length > 0);
    }'''

new_update_orders = '''    function updateOrdersUIFromData(orders = []) {
      if (!Array.isArray(orders)) {
        orders = Array.isArray(window.currentVendorOrders) ? window.currentVendorOrders : [];
      }
      window.currentVendorOrders = orders;

      const placed = (orders || []).filter(o => o && (o.status === 'PLACED' || o.status === 'CREATED'));
      const preparing = (orders || []).filter(o => o && (o.status === 'ACCEPTED' || o.status === 'PREPARING'));
      const ready = (orders || []).filter(o => o && (o.status === 'PACKED' || o.status === 'RUNNER_ASSIGNED'));

      const newBadge = document.getElementById('new-orders-badge');
      const prepBadge = document.getElementById('prep-orders-badge');
      const readyBadge = document.getElementById('ready-orders-badge');

      if (newBadge) newBadge.innerText = String(placed?.length ?? 0);
      if (prepBadge) prepBadge.innerText = String(preparing?.length ?? 0);
      if (readyBadge) readyBadge.innerText = String(ready?.length ?? 0);

      const newEmpty = document.getElementById('new-orders-empty');
      const prepEmpty = document.getElementById('prep-orders-empty');
      const readyEmpty = document.getElementById('ready-orders-empty');

      if (newEmpty) newEmpty.classList.toggle('hidden', (placed?.length ?? 0) > 0);
      if (prepEmpty) prepEmpty.classList.toggle('hidden', (preparing?.length ?? 0) > 0);
      if (readyEmpty) readyEmpty.classList.toggle('hidden', (ready?.length ?? 0) > 0);
    }
    window.updateOrdersUIFromData = updateOrdersUIFromData;'''

if old_update_orders in v:
    v = v.replace(old_update_orders, new_update_orders, 1)
    print("Fixed updateOrdersUIFromData in vendor")
else:
    print("WARNING: old_update_orders not found exact")

# Fix line 2874 to pass safe fallback array
v = v.replace(
    "if (typeof updateOrdersUIFromData === 'function') updateOrdersUIFromData();",
    "if (typeof updateOrdersUIFromData === 'function') updateOrdersUIFromData(window.currentVendorOrders || []);"
)

# Eradicate browser "Save Password" popups in vendor
v = v.replace(
    '<input type="password" id="bank-acc-no"',
    '<input type="text" inputmode="numeric" autocomplete="off" id="bank-acc-no"'
)
v = v.replace(
    '<input type="text" id="bank-acc-no-confirm"',
    '<input type="text" inputmode="numeric" autocomplete="off" id="bank-acc-no-confirm"'
)
v = v.replace(
    '<input type="text" id="bank-ifsc"',
    '<input type="text" autocomplete="off" id="bank-ifsc"'
)
v = v.replace(
    '<input type="text" id="upi-vpa"',
    '<input type="text" autocomplete="off" id="upi-vpa"'
)

# Add autocomplete="one-time-code" to OTP inputs
for i in range(1, 7):
    v = v.replace(f'id="otp-{i}"', f'id="otp-{i}" autocomplete="one-time-code"')

v = v.replace('id="kyc-aadhaar-otp-input"', 'id="kyc-aadhaar-otp-input" autocomplete="one-time-code"')
v = v.replace('id="handover-otp-input"', 'id="handover-otp-input" autocomplete="one-time-code"')
v = v.replace('id="payout-security-otp"', 'id="payout-security-otp" autocomplete="one-time-code"')

with open('public_web/vendor/index.html', 'w', encoding='utf-8') as f:
    f.write(v)
print("Vendor updated.")


# 2. PATCH RUNNER APP
with open('public_web/runner/index.html', 'r', encoding='utf-8') as f:
    r = f.read()

r = r.replace(
    '<input type="password" id="bank-acc-no"',
    '<input type="text" inputmode="numeric" autocomplete="off" id="bank-acc-no"'
)
r = r.replace(
    '<input type="text" id="bank-acc-no-confirm"',
    '<input type="text" inputmode="numeric" autocomplete="off" id="bank-acc-no-confirm"'
)
r = r.replace(
    '<input type="text" id="bank-ifsc"',
    '<input type="text" autocomplete="off" id="bank-ifsc"'
)
r = r.replace(
    '<input type="text" id="upi-vpa"',
    '<input type="text" autocomplete="off" id="upi-vpa"'
)

for i in range(1, 7):
    r = r.replace(f'id="otp-{i}"', f'id="otp-{i}" autocomplete="one-time-code"')

r = r.replace('id="cust-delivery-otp"', 'id="cust-delivery-otp" autocomplete="one-time-code"')
r = r.replace('id="payout-security-otp"', 'id="payout-security-otp" autocomplete="one-time-code"')
r = r.replace('id="kyc-aadhaar-otp-input"', 'id="kyc-aadhaar-otp-input" autocomplete="one-time-code"')
r = r.replace('id="new-payout-target"', 'id="new-payout-target" autocomplete="off"')

with open('public_web/runner/index.html', 'w', encoding='utf-8') as f:
    f.write(r)
print("Runner updated.")


# 3. PATCH CUSTOMER APP
with open('public_web/customer/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace(
    '<input type="password" id="vault-bank-account"',
    '<input type="text" inputmode="numeric" autocomplete="off" id="vault-bank-account"'
)
c = c.replace(
    '<input type="text" id="vault-bank-account-confirm"',
    '<input type="text" inputmode="numeric" autocomplete="off" id="vault-bank-account-confirm"'
)
c = c.replace(
    '<input type="text" id="vault-bank-ifsc"',
    '<input type="text" autocomplete="off" id="vault-bank-ifsc"'
)
c = c.replace(
    '<input type="text" id="vault-bank-holder"',
    '<input type="text" autocomplete="off" id="vault-bank-holder"'
)
c = c.replace(
    '<input type="text" id="vault-upi-input"',
    '<input type="text" autocomplete="off" id="vault-upi-input"'
)
c = c.replace(
    '<input type="password" id="vault-card-cvv"',
    '<input type="text" inputmode="numeric" autocomplete="off" id="vault-card-cvv"'
)
c = c.replace(
    '<input type="password" id="checkout-card-cvv"',
    '<input type="text" inputmode="numeric" autocomplete="off" id="checkout-card-cvv"'
)

for i in range(1, 7):
    c = c.replace(f'id="otp-{i}"', f'id="otp-{i}" autocomplete="one-time-code"')

c = c.replace('id="kyc-aadhaar-otp-input"', 'id="kyc-aadhaar-otp-input" autocomplete="one-time-code"')

with open('public_web/customer/index.html', 'w', encoding='utf-8') as f:
    f.write(c)
print("Customer updated.")
