with open('public_web/customer/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('function updateCheckoutModalUI()')
idx2 = text.find('async function confirmPaymentAndPlaceOrder()')

target = text[idx:idx2]

replacement = """function updateCheckoutModalUI() {
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
      const bankCard = document.getElementById('checkout-opt-bank');
      const cardCard = document.getElementById('checkout-opt-card');
      const codCard = document.getElementById('checkout-opt-cod');

      const upiRadio = document.getElementById('pm-radio-upi');
      const bankRadio = document.getElementById('pm-radio-bank');
      const cardRadio = document.getElementById('pm-radio-card');
      const codRadio = document.getElementById('pm-radio-cod');
      
      const btnText = document.getElementById('btn-checkout-modal-text');

      [upiCard, bankCard, cardCard, codCard].forEach(el => {
        if (el) el.className = "p-4 rounded-2xl border border-slate-200 bg-white hover:bg-slate-50 cursor-pointer transition relative";
      });
      [upiRadio, bankRadio, cardRadio, codRadio].forEach(el => {
        if (el) el.checked = false;
      });

      if (selectedCheckoutModalPayment === 'ONLINE' || selectedCheckoutModalPayment === 'UPI') {
        if (upiRadio) upiRadio.checked = true;
        if (upiCard) upiCard.className = 'p-4 rounded-2xl border-2 border-emerald-600 bg-emerald-50/60 cursor-pointer transition relative';
        if (btnText) {
          btnText.innerText = currentLang === 'hi' 
            ? `UPI द्वारा ₹${grandTotal.toFixed(2)} भुगतान करें` 
            : `Pay ₹${grandTotal.toFixed(2)} via UPI`;
        }
      } else if (selectedCheckoutModalPayment === 'BANK') {
        if (bankRadio) bankRadio.checked = true;
        if (bankCard) bankCard.className = 'p-4 rounded-2xl border-2 border-emerald-600 bg-emerald-50/60 cursor-pointer transition relative';
        if (btnText) {
          btnText.innerText = currentLang === 'hi' 
            ? `नेट बैंकिंग द्वारा ₹${grandTotal.toFixed(2)} भुगतान करें` 
            : `Pay ₹${grandTotal.toFixed(2)} via Net Banking`;
        }
      } else if (selectedCheckoutModalPayment === 'CARD') {
        if (cardRadio) cardRadio.checked = true;
        if (cardCard) cardCard.className = 'p-4 rounded-2xl border-2 border-emerald-600 bg-emerald-50/60 cursor-pointer transition relative';
        if (btnText) {
          btnText.innerText = currentLang === 'hi' 
            ? `कार्ड द्वारा ₹${grandTotal.toFixed(2)} भुगतान करें` 
            : `Pay ₹${grandTotal.toFixed(2)} via Card`;
        }
      } else if (selectedCheckoutModalPayment === 'COD') {
        if (codRadio) codRadio.checked = true;
        if (codCard) codCard.className = 'p-4 rounded-2xl border-2 border-amber-600 bg-amber-50/60 cursor-pointer transition relative';
        if (btnText) {
          btnText.innerText = currentLang === 'hi' 
            ? `COD ऑर्डर की पुष्टि करें (₹${grandTotal.toFixed(2)})` 
            : `Confirm COD Order (₹${grandTotal.toFixed(2)})`;
        }
      }
      lucide.createIcons();
    }

    """

text = text[:idx] + replacement + text[idx2:]

with open('public_web/customer/index.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("SUCCESS: Updated updateCheckoutModalUI for all 4 payment modes!")
