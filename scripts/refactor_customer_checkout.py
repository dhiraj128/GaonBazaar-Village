import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/customer/index.html', 'r', encoding='utf-8') as f:
    customer = f.read()

# 1. Update #btn-place-order to call openCheckoutPaymentModal() instead of placeCustomerOrder()
old_btn = 'onclick="placeCustomerOrder()" id="btn-place-order"'
new_btn = 'onclick="openCheckoutPaymentModal()" id="btn-place-order"'
if old_btn in customer:
    customer = customer.replace(old_btn, new_btn, 1)
    print("Updated #btn-place-order onclick to openCheckoutPaymentModal()")
else:
    print("Warning: old_btn not found")

# 2. Add #modal-checkout-payment before modal-manage-addresses or closing body
modal_html = '''
    <!-- =================================================================== -->
    <!-- DEDICATED CHECKOUT PAYMENT SELECTION BOTTOM SHEET / MODAL -->
    <!-- =================================================================== -->
    <div id="modal-checkout-payment" class="hidden fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-end sm:items-center justify-center p-0 sm:p-4">
      <div class="w-full sm:max-w-md bg-white rounded-t-3xl sm:rounded-3xl shadow-2xl border border-slate-100 max-h-[90vh] flex flex-col overflow-hidden animate-in slide-in-from-bottom duration-200">
        <!-- Top Drag Handle -->
        <div class="pt-3 pb-1 flex justify-center sm:hidden">
          <div class="w-12 h-1.5 bg-slate-200 rounded-full"></div>
        </div>

        <!-- Modal Header -->
        <div class="px-5 py-3.5 border-b border-slate-100 flex items-center justify-between">
          <div class="flex items-center space-x-2.5">
            <div class="w-8 h-8 rounded-xl bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold">
              <i data-lucide="credit-card" class="w-4 h-4"></i>
            </div>
            <div>
              <h3 class="text-sm font-bold text-slate-900" data-i18n="checkout_payment_title">Select Payment Method</h3>
              <p class="text-[10px] text-slate-500" data-i18n="checkout_payment_sub">Safe & Verified Rural Checkout</p>
            </div>
          </div>
          <button onclick="closeCheckoutPaymentModal()" class="w-8 h-8 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-600 flex items-center justify-center transition active:scale-95">
            <i data-lucide="x" class="w-4 h-4"></i>
          </button>
        </div>

        <div class="p-5 space-y-4 overflow-y-auto">
          <!-- Order Summary Card -->
          <div class="bg-slate-50 p-3.5 rounded-2xl border border-slate-200 text-xs space-y-2">
            <div class="flex justify-between text-slate-600">
              <span data-i18n="checkout_bill_items">Item Total:</span>
              <span id="checkout-modal-item-total" class="font-bold text-slate-800">₹0.00</span>
            </div>
            <div class="flex justify-between text-slate-600">
              <span data-i18n="checkout_bill_delivery">Delivery Fee:</span>
              <span id="checkout-modal-delivery-fee" class="font-semibold text-slate-800">₹0.00</span>
            </div>
            <div class="flex justify-between text-slate-600">
              <span data-i18n="checkout_bill_platform">Platform Fee:</span>
              <span id="checkout-modal-platform-fee" class="font-semibold text-slate-800">₹3.00</span>
            </div>
            <div id="checkout-modal-cod-fee-row" class="flex justify-between text-amber-800 font-medium">
              <span data-i18n="checkout_bill_cod">COD Convenience Fee:</span>
              <span id="checkout-modal-cod-fee" class="font-bold">+₹10.00</span>
            </div>
            <div class="border-t border-slate-200 pt-2 flex justify-between items-center text-sm font-extrabold text-slate-900">
              <span data-i18n="checkout_bill_total">To Pay:</span>
              <span id="checkout-modal-grand-total" class="text-lg font-mono text-emerald-700">₹0.00</span>
            </div>
          </div>

          <!-- Payment Option 1: Pay via UPI -->
          <div id="checkout-opt-upi" onclick="selectCheckoutModalPayment('ONLINE')" class="p-4 rounded-2xl border-2 border-emerald-600 bg-emerald-50/50 cursor-pointer transition relative">
            <div class="flex items-start justify-between">
              <div class="flex items-center space-x-3">
                <input type="radio" name="checkout_modal_pm" id="pm-radio-upi" value="ONLINE" checked class="w-4 h-4 text-emerald-600 focus:ring-emerald-500">
                <div>
                  <div class="flex items-center space-x-2">
                    <span class="font-bold text-slate-900 text-xs" data-i18n="checkout_pay_upi">Pay via UPI</span>
                    <span class="text-[9px] font-bold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800">Free / Save ₹10</span>
                  </div>
                  <p class="text-[10px] text-slate-500 mt-0.5" data-i18n="checkout_pay_upi_desc">Fast & secure instant UPI payment</p>
                </div>
              </div>
              <span class="text-lg">⚡</span>
            </div>

            <!-- UPI Brand Chips -->
            <div class="mt-3 pt-2.5 border-t border-emerald-200/60 flex items-center space-x-2 overflow-x-auto text-[10px]">
              <span class="px-2 py-1 bg-white border border-slate-200 rounded-lg font-bold text-slate-700 shadow-2xs flex items-center space-x-1">
                <span class="text-blue-600 font-extrabold">G</span>Pay
              </span>
              <span class="px-2 py-1 bg-white border border-slate-200 rounded-lg font-bold text-purple-700 shadow-2xs flex items-center space-x-1">
                Phone<span class="text-purple-600">Pe</span>
              </span>
              <span class="px-2 py-1 bg-white border border-slate-200 rounded-lg font-bold text-sky-600 shadow-2xs flex items-center space-x-1">
                Paytm
              </span>
              <span class="px-2 py-1 bg-white border border-slate-200 rounded-lg font-bold text-emerald-700 shadow-2xs flex items-center space-x-1">
                BHIM
              </span>
            </div>
          </div>

          <!-- Payment Option 2: Cash on Delivery (COD) -->
          <div id="checkout-opt-cod" onclick="selectCheckoutModalPayment('COD')" class="p-4 rounded-2xl border border-slate-200 bg-white hover:bg-slate-50 cursor-pointer transition">
            <div class="flex items-start justify-between">
              <div class="flex items-center space-x-3">
                <input type="radio" name="checkout_modal_pm" id="pm-radio-cod" value="COD" class="w-4 h-4 text-emerald-600 focus:ring-emerald-500">
                <div>
                  <div class="flex items-center space-x-2">
                    <span class="font-bold text-slate-900 text-xs" data-i18n="checkout_pay_cod">Cash on Delivery (COD)</span>
                    <span class="text-[9px] font-bold px-2 py-0.5 rounded-full bg-amber-100 text-amber-800">+₹10 Fee</span>
                  </div>
                  <p class="text-[10px] text-slate-500 mt-0.5" data-i18n="checkout_pay_cod_desc">Pay cash directly to runner upon delivery</p>
                </div>
              </div>
              <span class="text-lg">💵</span>
            </div>
          </div>
        </div>

        <!-- Modal Primary CTA Button -->
        <div class="p-5 border-t border-slate-100 bg-white">
          <button id="btn-checkout-modal-confirm" onclick="confirmPaymentAndPlaceOrder()" class="w-full py-4 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-2xl shadow-lg shadow-emerald-600/30 flex items-center justify-center space-x-2 transition active:scale-98">
            <i data-lucide="zap" id="btn-checkout-modal-icon" class="w-4 h-4"></i>
            <span id="btn-checkout-modal-text">Pay ₹0.00 via UPI</span>
          </button>
        </div>
      </div>
    </div>
'''

target_pos = customer.find('<div id="modal-manage-addresses"')
if target_pos != -1:
    customer = customer[:target_pos] + modal_html + '\n    ' + customer[target_pos:]
    print("Inserted #modal-checkout-payment into customer HTML")
else:
    print("Warning: could not find modal-manage-addresses insertion point")

# 3. Add JavaScript functions for modal checkout payment
js_payment_functions = '''
    // ---------------------------------------------------------------------------
    // DEDICATED CHECKOUT PAYMENT BOTTOM SHEET LOGIC
    // ---------------------------------------------------------------------------
    let selectedCheckoutModalPayment = 'ONLINE';

    async function openCheckoutPaymentModal() {
      if (window.isLocationServiceable === false) {
        toastError(currentLang === 'hi' ? "इस स्थान पर वर्तमान में सेवा उपलब्ध नहीं है।" : "Service is currently unavailable in this location.");
        return;
      }
      if (cartItems.length === 0) {
        toastError(currentLang === 'hi' ? "आपका कार्ट खाली है! कृपया सामान जोड़ें।" : "Your cart is empty! Please add items first.");
        return;
      }

      // Check and validate address
      let addressId = selectedCheckoutAddressId;
      if (!addressId) {
        const village = (document.getElementById('checkout-village-input')?.value || '').trim();
        const landmark = (document.getElementById('checkout-landmark-input')?.value || '').trim();

        if (document.getElementById('checkout-no-address-card') && !document.getElementById('checkout-no-address-card').classList.contains('hidden') && !village) {
          toastError(currentLang === 'hi' ? "कृपया अपना डिलीवरी पता चुनें या जोड़ें" : "Please select or add your delivery address");
          return;
        }
      }

      // Default to ONLINE (UPI)
      selectedCheckoutModalPayment = 'ONLINE';
      updateCheckoutModalUI();

      const modal = document.getElementById('modal-checkout-payment');
      if (modal) {
        modal.classList.remove('hidden');
        lucide.createIcons();
      }
    }

    function closeCheckoutPaymentModal() {
      const modal = document.getElementById('modal-checkout-payment');
      if (modal) modal.classList.add('hidden');
    }

    function selectCheckoutModalPayment(mode) {
      selectedCheckoutModalPayment = mode;
      updateCheckoutModalUI();
    }

    function updateCheckoutModalUI() {
      const itemTotal = cartItems.reduce((acc, item) => acc + (item.price * item.quantity), 0);
      const deliveryFee = 0.00; // Rural free delivery / base promo
      const platformFee = 3.00;
      const codFee = selectedCheckoutModalPayment === 'COD' ? 10.00 : 0.00;
      const grandTotal = itemTotal + deliveryFee + platformFee + codFee;

      const itemTotalEl = document.getElementById('checkout-modal-item-total');
      if (itemTotalEl) itemTotalEl.innerText = `₹${itemTotal.toFixed(2)}`;

      const delFeeEl = document.getElementById('checkout-modal-delivery-fee');
      if (delFeeEl) delFeeEl.innerText = `₹${deliveryFee.toFixed(2)}`;

      const platFeeEl = document.getElementById('checkout-modal-platform-fee');
      if (platFeeEl) platFeeEl.innerText = `₹${platformFee.toFixed(2)}`;

      const codRowEl = document.getElementById('checkout-modal-cod-fee-row');
      const codFeeEl = document.getElementById('checkout-modal-cod-fee');
      if (codRowEl && codFeeEl) {
        if (selectedCheckoutModalPayment === 'COD') {
          codRowEl.classList.remove('hidden');
          codFeeEl.innerText = `+₹10.00`;
          codFeeEl.className = 'font-bold text-amber-800';
        } else {
          codRowEl.classList.remove('hidden');
          codFeeEl.innerText = `₹0.00 (Free)`;
          codFeeEl.className = 'font-bold text-emerald-700';
        }
      }

      const grandTotalEl = document.getElementById('checkout-modal-grand-total');
      if (grandTotalEl) grandTotalEl.innerText = `₹${grandTotal.toFixed(2)}`;

      // Update Radio and card styles
      const upiCard = document.getElementById('checkout-opt-upi');
      const codCard = document.getElementById('checkout-opt-cod');
      const upiRadio = document.getElementById('pm-radio-upi');
      const codRadio = document.getElementById('pm-radio-cod');
      const btn = document.getElementById('btn-checkout-modal-confirm');
      const btnText = document.getElementById('btn-checkout-modal-text');

      if (selectedCheckoutModalPayment === 'ONLINE') {
        if (upiRadio) upiRadio.checked = true;
        if (codRadio) codRadio.checked = false;
        if (upiCard) {
          upiCard.className = 'p-4 rounded-2xl border-2 border-emerald-600 bg-emerald-50/60 cursor-pointer transition relative';
        }
        if (codCard) {
          codCard.className = 'p-4 rounded-2xl border border-slate-200 bg-white hover:bg-slate-50 cursor-pointer transition';
        }
        if (btnText) {
          btnText.innerText = currentLang === 'hi' 
            ? `UPI द्वारा ₹${grandTotal.toFixed(2)} भुगतान करें` 
            : `Pay ₹${grandTotal.toFixed(2)} via UPI`;
        }
      } else {
        if (upiRadio) upiRadio.checked = false;
        if (codRadio) codRadio.checked = true;
        if (upiCard) {
          upiCard.className = 'p-4 rounded-2xl border border-slate-200 bg-white hover:bg-slate-50 cursor-pointer transition';
        }
        if (codCard) {
          codCard.className = 'p-4 rounded-2xl border-2 border-amber-600 bg-amber-50/60 cursor-pointer transition';
        }
        if (btnText) {
          btnText.innerText = currentLang === 'hi' 
            ? `COD ऑर्डर की पुष्टि करें (₹${grandTotal.toFixed(2)})` 
            : `Confirm COD Order (₹${grandTotal.toFixed(2)})`;
        }
      }
      lucide.createIcons();
    }

    async function confirmPaymentAndPlaceOrder() {
      const btn = document.getElementById('btn-checkout-modal-confirm');
      const originalHtml = btn ? btn.innerHTML : '';
      
      if (selectedCheckoutModalPayment === 'ONLINE') {
        if (btn) {
          btn.innerHTML = `<span class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></span> ${currentLang === 'hi' ? 'UPI ऐप से जुड़ रहे हैं...' : 'Initiating UPI Payment...'}`;
          btn.disabled = true;
        }

        // Simulate secure UPI payment gateway intent / authorization
        await new Promise(r => setTimeout(r, 900));

        try {
          await executeOrderPlacementWithMethod('ONLINE');
        } finally {
          if (btn) {
            btn.innerHTML = originalHtml;
            btn.disabled = false;
            lucide.createIcons();
          }
        }
      } else {
        if (btn) {
          btn.innerHTML = `<span class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></span> ${currentLang === 'hi' ? 'ऑर्डर दर्ज हो रहा है...' : 'Placing Order...'}`;
          btn.disabled = true;
        }

        try {
          await executeOrderPlacementWithMethod('COD');
        } finally {
          if (btn) {
            btn.innerHTML = originalHtml;
            btn.disabled = false;
            lucide.createIcons();
          }
        }
      }
    }

    async function executeOrderPlacementWithMethod(paymentMode) {
      let addressId = selectedCheckoutAddressId;

      // If user has not selected an existing address, validate and create inline address
      if (!addressId) {
        const recipient = (document.getElementById('checkout-recipient-input')?.value || '').trim();
        const village = (document.getElementById('checkout-village-input')?.value || '').trim();
        const landmark = (document.getElementById('checkout-landmark-input')?.value || '').trim();

        if (!village) {
          toastError(currentLang === 'hi' ? "कृपया अपना गाँव या मोहल्ला दर्ज करें" : "Please enter your village / locality name");
          closeCheckoutPaymentModal();
          document.getElementById('checkout-village-input')?.focus();
          return;
        }
        if (!landmark) {
          toastError(currentLang === 'hi' ? "कृपया एक प्रमुख ग्रामीण लैंडमार्क लिखें" : "Please provide a prominent rural landmark for delivery");
          closeCheckoutPaymentModal();
          document.getElementById('checkout-landmark-input')?.focus();
          return;
        }

        try {
          const newAddr = await apiRequest('/api/v1/addresses', 'POST', {
            title: "Home",
            recipient_name: recipient || "Customer",
            phone: localStorage.getItem('gb_customer_phone') || "9876543210",
            village: village,
            landmark: landmark,
            latitude: window.detectedLatitude || 26.2315,
            longitude: window.detectedLongitude || 85.3610,
            block: "Minapur",
            district: "Muzaffarpur",
            state: "Bihar",
            is_default: true
          });
          if (newAddr && newAddr.id) {
            addressId = newAddr.id;
            selectedCheckoutAddressId = addressId;
            loadUserSavedAddresses();
          }
        } catch (addrErr) {
          console.error("Address auto-creation notice:", addrErr);
          if (userSavedAddresses.length > 0) addressId = userSavedAddresses[0].id;
        }
      }

      if (!addressId && userSavedAddresses.length > 0) {
        addressId = userSavedAddresses[0].id;
      }

      const storeId = cartItems[0]?.storeId || 'str_01';
      const orderPayload = {
        store_id: storeId,
        delivery_address_id: addressId,
        payment_method: paymentMode,
        items: cartItems.map(c => ({ product_id: c.id, quantity: c.quantity })),
        customer_notes: (document.getElementById('checkout-landmark-input')?.value || '')
      };

      try {
        const res = await apiRequest('/api/v1/orders', 'POST', orderPayload);
        closeCheckoutPaymentModal();

        cartItems = [];
        updateCartBadge();

        localStorage.setItem('gb_order_placed_time', Date.now().toString());
        if (res && res.id) {
          localStorage.setItem('gb_active_order_id', res.id);
          if (res.delivery_otp) {
            localStorage.setItem('gb_active_order_otp', res.delivery_otp);
          }
          isDeliveryOtpRevealed = false;
          syncActiveOrderUI();
        }

        switchTab('orders');
        startOrderCancellationTimer();
        syncActiveOrderUI();
        toastSuccess(currentLang === 'hi' ? "ऑर्डर सफलतापूर्वक दर्ज हो गया!" : "Order placed successfully! Delivery partner assigned.");
      } catch (err) {
        console.error("Order placement error:", err);
        toastError(currentLang === 'hi' ? "ऑर्डर दर्ज करने में त्रुटि। कृपया पुनः प्रयास करें।" : "Failed to place order. Please try again.");
      }
    }
'''

# Insert js_payment_functions right above placeCustomerOrder
pco_idx = customer.find('function placeCustomerOrder()')
if pco_idx != -1:
    customer = customer[:pco_idx] + js_payment_functions + '\n    ' + customer[pco_idx:]
    print("Inserted JS payment functions into customer HTML")
else:
    print("Warning: could not find function placeCustomerOrder() insertion point")

with open('public_web/customer/index.html', 'w', encoding='utf-8') as f:
    f.write(customer)

print("Customer HTML updated successfully.")
