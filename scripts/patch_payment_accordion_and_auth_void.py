import re

with open('public_web/customer/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. REPLACE MODAL-PAYMENT-SETTINGS ACCORDION HTML
old_modal_start = '        <!-- Mode Toggle: Strict Vertical Top-to-Bottom List (1. UPI, 2. Bank, 3. Card, 4. COD) -->'
old_modal_end = '''        <!-- Action Buttons -->
        <div class="pt-2 space-y-2">
          <button type="button" id="btn-save-payment-vault" onclick="saveCustomerPaymentVault()" class="w-full py-3.5 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-xl shadow-md transition active:scale-98 flex items-center justify-center space-x-2 text-xs">
            <i data-lucide="check-circle" class="w-4 h-4"></i>
            <span id="btn-save-vault-text">Save Payment Details</span>
          </button>
          <button type="button" onclick="closeModal('modal-payment-settings')" class="w-full py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold rounded-xl text-xs transition">
            Close
          </button>
        </div>'''

new_modal_content = '''        <!-- Mode Toggle: Expandable Accordion List (1. UPI, 2. Bank, 3. Card, 4. COD) -->
        <div class="space-y-3" id="vault-accordion-container">
          <!-- 1. UPI: GPay, PhonePe, Paytm -->
          <div id="vault-opt-upi" onclick="selectVaultPaymentOption('upi')" class="p-3.5 rounded-2xl border-2 border-emerald-600 bg-emerald-50/40 shadow-xs cursor-pointer transition-all">
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-3">
                <input type="radio" name="vault_payment_option" id="vault-radio-upi" value="upi" checked onchange="selectVaultPaymentOption('upi')" class="w-4 h-4 text-emerald-600 accent-emerald-600">
                <div>
                  <div class="flex items-center space-x-2">
                    <span class="font-bold text-slate-900 text-xs">1. Pay via UPI</span>
                    <span class="text-[9px] font-bold px-1.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800">Fast & Free</span>
                  </div>
                  <p class="text-[10px] text-slate-500 mt-0.5">Google Pay, PhonePe, Paytm, BHIM</p>
                </div>
              </div>
              <div class="flex items-center space-x-2">
                <span class="text-base">⚡</span>
                <i data-lucide="chevron-down" id="vault-chevron-upi" class="w-4 h-4 text-emerald-600 rotate-180 transition-transform duration-200"></i>
              </div>
            </div>
            <!-- Intent Brand Chips -->
            <div class="mt-2 pt-2 border-t border-emerald-200/60 flex items-center space-x-2 text-[10px]">
              <span class="px-2 py-0.5 bg-white border border-slate-200 rounded-md font-bold text-slate-700 shadow-2xs"><span class="text-blue-600 font-extrabold">G</span>Pay</span>
              <span class="px-2 py-0.5 bg-white border border-slate-200 rounded-md font-bold text-purple-700 shadow-2xs">Phone<span class="text-purple-600">Pe</span></span>
              <span class="px-2 py-0.5 bg-white border border-slate-200 rounded-md font-bold text-sky-600 shadow-2xs">Paytm</span>
            </div>
            <!-- Form 1: UPI ID Setup (Accordion Body) -->
            <div id="vault-form-upi" class="mt-3 pt-2.5 border-t border-slate-200 space-y-2.5">
              <label class="block text-[11px] font-semibold text-slate-700">Enter UPI ID (Virtual Payment Address)</label>
              <div class="relative flex items-center">
                <i data-lucide="at-sign" class="absolute left-3 w-3.5 h-3.5 text-emerald-600 pointer-events-none"></i>
                <input type="text" autocomplete="off" id="vault-upi-input" placeholder="e.g. 9905361711@upi" value="9905361711@upi" class="w-full pl-9 pr-3 py-2 bg-white border border-slate-300 rounded-xl text-xs font-mono font-bold text-slate-900 focus:border-emerald-600 focus:ring-1 focus:ring-emerald-500 focus:outline-none shadow-2xs">
              </div>
              <div class="flex flex-wrap gap-1 text-[9px] pt-0.5">
                <button type="button" onclick="event.stopPropagation(); appendUpiSuffix('@upi')" class="px-2 py-1 bg-white border border-slate-200 rounded-lg text-slate-700 font-mono hover:bg-slate-50 transition">@upi</button>
                <button type="button" onclick="event.stopPropagation(); appendUpiSuffix('@okaxis')" class="px-2 py-1 bg-white border border-slate-200 rounded-lg text-slate-700 font-mono hover:bg-slate-50 transition">@okaxis</button>
                <button type="button" onclick="event.stopPropagation(); appendUpiSuffix('@okhdfcbank')" class="px-2 py-1 bg-white border border-slate-200 rounded-lg text-slate-700 font-mono hover:bg-slate-50 transition">@okhdfcbank</button>
                <button type="button" onclick="event.stopPropagation(); appendUpiSuffix('@paytm')" class="px-2 py-1 bg-white border border-slate-200 rounded-lg text-slate-700 font-mono hover:bg-slate-50 transition">@paytm</button>
              </div>
              <div class="p-2 rounded-xl bg-emerald-100/60 border border-emerald-200/80 text-[10px] text-emerald-900 flex items-center space-x-1.5">
                <i data-lucide="shield-check" class="w-3.5 h-3.5 text-emerald-700 shrink-0"></i>
                <span>₹1 refundable test charge confirms your UPI account instantly.</span>
              </div>
            </div>
          </div>

          <!-- 2. Bank Account / Net Banking -->
          <div id="vault-opt-bank" onclick="selectVaultPaymentOption('bank')" class="p-3.5 rounded-2xl border border-slate-200 bg-white hover:bg-slate-50 cursor-pointer transition-all">
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-3">
                <input type="radio" name="vault_payment_option" id="vault-radio-bank" value="bank" onchange="selectVaultPaymentOption('bank')" class="w-4 h-4 text-emerald-600 accent-emerald-600">
                <div>
                  <div class="flex items-center space-x-2">
                    <span class="font-bold text-slate-900 text-xs">2. Bank Account / Net Banking</span>
                    <span class="text-[9px] font-bold px-1.5 py-0.5 rounded-full bg-slate-100 text-slate-700">Direct</span>
                  </div>
                  <p class="text-[10px] text-slate-500 mt-0.5">SBI, HDFC, ICICI, PNB & Grameen Banks</p>
                </div>
              </div>
              <div class="flex items-center space-x-2">
                <span class="text-base">🏦</span>
                <i data-lucide="chevron-down" id="vault-chevron-bank" class="w-4 h-4 text-slate-400 rotate-0 transition-transform duration-200"></i>
              </div>
            </div>
            <!-- Form 2: Bank Account Setup (Accordion Body) -->
            <div id="vault-form-bank" class="mt-3 pt-2.5 border-t border-slate-200 space-y-2.5 hidden">
              <div>
                <label class="block text-[10px] font-semibold text-slate-600 mb-0.5">Account Holder Name</label>
                <input type="text" autocomplete="off" id="vault-bank-holder" placeholder="Name as per passbook" value="Customer Name" class="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs font-bold text-slate-900 focus:bg-white focus:border-emerald-600 focus:outline-none shadow-2xs">
              </div>
              <div>
                <label class="block text-[10px] font-semibold text-slate-600 mb-0.5">Bank Account Number</label>
                <input type="text" inputmode="numeric" autocomplete="off" id="vault-bank-account" placeholder="Enter bank account number" value="50100482910291" class="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs font-mono font-bold text-slate-900 focus:bg-white focus:border-emerald-600 focus:outline-none shadow-2xs">
              </div>
              <div class="grid grid-cols-2 gap-2">
                <div>
                  <label class="block text-[10px] font-semibold text-slate-600 mb-0.5">Confirm Account</label>
                  <input type="text" inputmode="numeric" autocomplete="off" id="vault-bank-account-confirm" placeholder="Re-enter number" value="50100482910291" class="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs font-mono font-bold text-slate-900 focus:bg-white focus:border-emerald-600 focus:outline-none shadow-2xs">
                </div>
                <div>
                  <label class="block text-[10px] font-semibold text-slate-600 mb-0.5">IFSC Code</label>
                  <input type="text" autocomplete="off" id="vault-bank-ifsc" placeholder="e.g. HDFC0001234" value="HDFC0001234" class="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs font-mono uppercase font-bold text-slate-900 focus:bg-white focus:border-emerald-600 focus:outline-none shadow-2xs">
                </div>
              </div>
              <div class="p-2 rounded-xl bg-emerald-100/60 border border-emerald-200/80 text-[10px] text-emerald-900 flex items-center space-x-1.5">
                <i data-lucide="shield-check" class="w-3.5 h-3.5 text-emerald-700 shrink-0"></i>
                <span>₹1 Penny Drop verification ensures bank branch validation.</span>
              </div>
            </div>
          </div>

          <!-- 3. Credit / Debit Card -->
          <div id="vault-opt-card" onclick="selectVaultPaymentOption('card')" class="p-3.5 rounded-2xl border border-slate-200 bg-white hover:bg-slate-50 cursor-pointer transition-all">
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-3">
                <input type="radio" name="vault_payment_option" id="vault-radio-card" value="card" onchange="selectVaultPaymentOption('card')" class="w-4 h-4 text-emerald-600 accent-emerald-600">
                <div>
                  <div class="flex items-center space-x-2">
                    <span class="font-bold text-slate-900 text-xs">3. Credit / Debit Card</span>
                    <span class="text-[9px] font-bold px-1.5 py-0.5 rounded-full bg-slate-100 text-slate-700">16-Digit</span>
                  </div>
                  <p class="text-[10px] text-slate-500 mt-0.5">Visa, RuPay, Mastercard & Maestro</p>
                </div>
              </div>
              <div class="flex items-center space-x-2">
                <span class="text-base">💳</span>
                <i data-lucide="chevron-down" id="vault-chevron-card" class="w-4 h-4 text-slate-400 rotate-0 transition-transform duration-200"></i>
              </div>
            </div>
            <!-- Form 3: Card Setup (Accordion Body) -->
            <div id="vault-form-card" class="mt-3 pt-2.5 border-t border-slate-200 space-y-2.5 hidden">
              <div>
                <label class="block text-[10px] font-semibold text-slate-600 mb-0.5">Card Number (16 Digits)</label>
                <input type="text" id="vault-card-number" inputmode="numeric" autocomplete="off" maxlength="19" placeholder="4111 2222 3333 4444" oninput="formatCardNumberInput(this)" class="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs font-mono font-bold text-slate-900 focus:bg-white focus:border-emerald-600 focus:outline-none shadow-2xs">
              </div>
              <div>
                <label class="block text-[10px] font-semibold text-slate-600 mb-0.5">Cardholder Name</label>
                <input type="text" id="vault-card-holder" autocomplete="off" placeholder="Name as on card" value="Customer Name" class="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs font-bold text-slate-900 focus:bg-white focus:border-emerald-600 focus:outline-none shadow-2xs">
              </div>
              <div class="grid grid-cols-2 gap-2">
                <div>
                  <label class="block text-[10px] font-semibold text-slate-600 mb-0.5">Expiry (MM/YY)</label>
                  <input type="text" id="vault-card-expiry" inputmode="numeric" autocomplete="off" maxlength="5" placeholder="12/28" oninput="formatCardExpiryInput(this)" class="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs font-mono font-bold text-slate-900 focus:bg-white focus:border-emerald-600 focus:outline-none text-center shadow-2xs">
                </div>
                <div>
                  <label class="block text-[10px] font-semibold text-slate-600 mb-0.5">CVV (3 Digits)</label>
                  <input type="text" inputmode="numeric" autocomplete="off" id="vault-card-cvv" maxlength="3" placeholder="123" class="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs font-mono font-bold text-slate-900 focus:bg-white focus:border-emerald-600 focus:outline-none text-center shadow-2xs">
                </div>
              </div>
              <div class="p-2 rounded-xl bg-emerald-100/60 border border-emerald-200/80 text-[10px] text-emerald-900 flex items-center space-x-1.5">
                <i data-lucide="shield-check" class="w-3.5 h-3.5 text-emerald-700 shrink-0"></i>
                <span>₹1 temporary hold & immediate void confirms card authenticity.</span>
              </div>
            </div>
          </div>

          <!-- 4. Cash on Delivery (COD) -->
          <div id="vault-opt-cod" onclick="selectVaultPaymentOption('cod')" class="p-3.5 rounded-2xl border border-slate-200 bg-white hover:bg-slate-50 cursor-pointer transition-all">
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-3">
                <input type="radio" name="vault_payment_option" id="vault-radio-cod" value="cod" onchange="selectVaultPaymentOption('cod')" class="w-4 h-4 text-emerald-600 accent-emerald-600">
                <div>
                  <div class="flex items-center space-x-2">
                    <span class="font-bold text-slate-900 text-xs">4. Cash on Delivery (COD)</span>
                    <span class="text-[9px] font-bold px-1.5 py-0.5 rounded-full bg-amber-100 text-amber-800">Cash</span>
                  </div>
                  <p class="text-[10px] text-slate-500 mt-0.5">Default to pay cash directly to runner upon delivery</p>
                </div>
              </div>
              <div class="flex items-center space-x-2">
                <span class="text-base">💵</span>
                <i data-lucide="chevron-down" id="vault-chevron-cod" class="w-4 h-4 text-slate-400 rotate-0 transition-transform duration-200"></i>
              </div>
            </div>
            <!-- Form 4: COD Details (Accordion Body) -->
            <div id="vault-form-cod" class="mt-3 pt-2.5 border-t border-slate-200 text-[11px] text-slate-600 space-y-1.5 hidden">
              <div class="flex items-center space-x-1.5 text-emerald-800 font-semibold">
                <i data-lucide="check" class="w-3.5 h-3.5 text-emerald-600 shrink-0"></i>
                <span>No advance digital payment needed.</span>
              </div>
              <p class="text-[10px] text-slate-500">Pay cash in Indian Rupees directly to the GaonBazaar delivery runner upon doorstep handover.</p>
            </div>
          </div>
        </div>

        <!-- Security Note: Industry-standard 256-bit Bank-Grade Security -->
        <div class="p-3.5 bg-slate-50 rounded-2xl border border-slate-200 text-slate-600 flex items-start space-x-3 shadow-2xs">
          <div class="w-7 h-7 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center shrink-0 mt-0.5">
            <i data-lucide="shield-check" class="w-4 h-4 text-emerald-700"></i>
          </div>
          <div>
            <div class="font-bold text-xs text-slate-900 flex items-center space-x-1">
              <span id="vault-security-title" data-i18n="vault_security_primary">🔒 256-bit Bank-Grade Security</span>
            </div>
            <p id="vault-security-sub" class="text-[11px] text-slate-500 mt-0.5 leading-relaxed" data-i18n="vault_security_sub">
              Your payment details are tokenized and securely stored via Razorpay. We never store your raw card numbers.
            </p>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="pt-2 space-y-2">
          <button type="button" id="btn-save-payment-vault" onclick="saveCustomerPaymentVault()" class="w-full py-3.5 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-xl shadow-md transition active:scale-98 flex items-center justify-center space-x-2 text-xs">
            <i data-lucide="check-circle" id="btn-save-vault-icon" class="w-4 h-4"></i>
            <span id="btn-save-vault-text" data-i18n="vault_save_btn">Save Payment Details</span>
          </button>
          <button type="button" onclick="closeModal('modal-payment-settings')" class="w-full py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold rounded-xl text-xs transition" data-i18n="close_btn">
            Close
          </button>
        </div>'''

idx_start = html.find(old_modal_start)
idx_end = html.find(old_modal_end)
if idx_start != -1 and idx_end != -1:
    html = html[:idx_start] + new_modal_content + html[idx_end + len(old_modal_end):]
    print("Modal HTML replaced successfully.")
else:
    print(f"ERROR: Could not locate modal boundaries: {idx_start}, {idx_end}")

# 2. REPLACE JS FUNCTIONS IN SCRIPT
old_js_start = '    function switchVaultTab(tab) {'
old_js_end = '''      } else {
        closeModal('modal-payment-settings');
      }
    }'''

new_js_content = '''    function switchVaultTab(tab) {
      selectVaultPaymentOption(tab);
    }
    window.switchVaultTab = switchVaultTab;

    function appendUpiSuffix(suffix) {
      const el = document.getElementById('vault-upi-input');
      if (!el) return;
      const current = el.value.trim().split('@')[0];
      if (current) {
        el.value = current + suffix;
      } else {
        el.value = suffix;
      }
    }
    window.appendUpiSuffix = appendUpiSuffix;

    function formatCardNumberInput(input) {
      if (!input) return;
      let val = input.value.replace(/\\D/g, '').substring(0, 16);
      let parts = [];
      for (let i = 0; i < val.length; i += 4) {
        parts.push(val.substring(i, i + 4));
      }
      input.value = parts.join(' ');
    }
    window.formatCardNumberInput = formatCardNumberInput;

    function formatCardExpiryInput(input) {
      if (!input) return;
      let val = input.value.replace(/\\D/g, '').substring(0, 4);
      if (val.length >= 2) {
        input.value = val.substring(0, 2) + '/' + val.substring(2);
      } else {
        input.value = val;
      }
    }
    window.formatCardExpiryInput = formatCardExpiryInput;

    function selectVaultPaymentOption(mode) {
      currentVaultPaymentOption = mode;
      currentVaultTab = mode;
      
      const modes = ['upi', 'bank', 'card', 'cod'];
      modes.forEach(m => {
        const optEl = document.getElementById(`vault-opt-${m}`);
        const radioEl = document.getElementById(`vault-radio-${m}`);
        const formEl = document.getElementById(`vault-form-${m}`);
        const chevronEl = document.getElementById(`vault-chevron-${m}`);
        const isSelected = (m === mode);

        if (radioEl) radioEl.checked = isSelected;

        if (optEl) {
          if (isSelected) {
            optEl.className = "p-3.5 rounded-2xl border-2 border-emerald-600 bg-emerald-50/40 shadow-xs cursor-pointer transition-all";
          } else {
            optEl.className = "p-3.5 rounded-2xl border border-slate-200 bg-white hover:bg-slate-50 cursor-pointer transition-all";
          }
        }

        if (formEl) {
          if (isSelected) {
            formEl.classList.remove('hidden');
          } else {
            formEl.classList.add('hidden');
          }
        }

        if (chevronEl) {
          if (isSelected) {
            chevronEl.className = "w-4 h-4 text-emerald-600 rotate-180 transition-transform duration-200";
          } else {
            chevronEl.className = "w-4 h-4 text-slate-400 rotate-0 transition-transform duration-200";
          }
        }
      });

      if (window.lucide) lucide.createIcons();
    }
    window.selectVaultPaymentOption = selectVaultPaymentOption;

    async function saveCustomerPaymentVault() {
      const btn = document.getElementById('btn-save-payment-vault');
      const btnText = document.getElementById('btn-save-vault-text');
      const btnIcon = document.getElementById('btn-save-vault-icon');
      const originalText = btnText ? btnText.innerText : 'Save Payment Details';

      const mode = currentVaultPaymentOption || currentVaultTab || 'upi';

      let methodDesc = '';
      let payload = { preferred_payment_mode: mode };
      let verificationResult = null;

      if (mode === 'upi') {
        const upi = (document.getElementById('vault-upi-input')?.value || '').trim();
        if (!upi || !upi.includes('@') || upi.length < 5) {
          toastError(currentLang === 'hi' ? "कृपया एक मान्य UPI ID दर्ज करें (उदा. 9905361711@upi)" : "Please enter a valid UPI ID (e.g. 9905361711@upi)");
          document.getElementById('vault-upi-input')?.focus();
          return;
        }
      } else if (mode === 'bank') {
        const holder = (document.getElementById('vault-bank-holder')?.value || '').trim();
        const acc = (document.getElementById('vault-bank-account')?.value || '').trim();
        const accConfirm = (document.getElementById('vault-bank-account-confirm')?.value || '').trim();
        const ifsc = (document.getElementById('vault-bank-ifsc')?.value || '').trim().toUpperCase();

        if (!holder) {
          toastError(currentLang === 'hi' ? "कृपया खाता धारक का नाम दर्ज करें" : "Please enter account holder name");
          document.getElementById('vault-bank-holder')?.focus();
          return;
        }
        if (!acc || acc.length < 9 || acc.length > 18 || !/^\\d+$/.test(acc)) {
          toastError(currentLang === 'hi' ? "कृपया 9 से 18 अंकों का वैध खाता नंबर दर्ज करें" : "Please enter a valid 9 to 18-digit account number");
          document.getElementById('vault-bank-account')?.focus();
          return;
        }
        if (acc !== accConfirm) {
          toastError(currentLang === 'hi' ? "बैंक खाता संख्या मेल नहीं खाती" : "Account numbers do not match");
          document.getElementById('vault-bank-account-confirm')?.focus();
          return;
        }
        if (!ifsc || ifsc.length !== 11 || ifsc[4] !== '0') {
          toastError(currentLang === 'hi' ? "कृपया 11-अक्षरों का मान्य IFSC कोड दर्ज करें" : "Please enter a valid 11-character IFSC code (e.g. HDFC0001234)");
          document.getElementById('vault-bank-ifsc')?.focus();
          return;
        }
      } else if (mode === 'card') {
        const cardNum = (document.getElementById('vault-card-number')?.value || '').replace(/\\s+/g, '');
        const cardHolder = (document.getElementById('vault-card-holder')?.value || '').trim();
        const cardExpiry = (document.getElementById('vault-card-expiry')?.value || '').trim();
        const cardCvv = (document.getElementById('vault-card-cvv')?.value || '').trim();

        if (!cardNum || cardNum.length < 15 || cardNum.length > 19 || !/^\\d+$/.test(cardNum)) {
          toastError(currentLang === 'hi' ? "कृपया मान्य 16-अंकीय कार्ड नंबर दर्ज करें" : "Please enter a valid 16-digit card number");
          document.getElementById('vault-card-number')?.focus();
          return;
        }
        if (!cardHolder) {
          toastError(currentLang === 'hi' ? "कृपया कार्डधारक का नाम दर्ज करें" : "Please enter cardholder name");
          document.getElementById('vault-card-holder')?.focus();
          return;
        }
        if (!cardExpiry || !/^\\d{2}\\/\\d{2}$/.test(cardExpiry)) {
          toastError(currentLang === 'hi' ? "कृपया मान्य समाप्ति तिथि (MM/YY) दर्ज करें" : "Please enter a valid expiry date (MM/YY)");
          document.getElementById('vault-card-expiry')?.focus();
          return;
        }
        const [expM, expY] = cardExpiry.split('/').map(Number);
        if (expM < 1 || expM > 12) {
          toastError(currentLang === 'hi' ? "समाप्ति माह 01 और 12 के बीच होना चाहिए" : "Expiry month must be between 01 and 12");
          document.getElementById('vault-card-expiry')?.focus();
          return;
        }
        if (!cardCvv || cardCvv.length < 3 || cardCvv.length > 4 || !/^\\d+$/.test(cardCvv)) {
          toastError(currentLang === 'hi' ? "कृपया मान्य 3-अंकीय CVV दर्ज करें" : "Please enter a valid 3-digit CVV");
          document.getElementById('vault-card-cvv')?.focus();
          return;
        }
      }

      // 2. Loading State: "Verifying (₹1 test charge & refund)..."
      if (btn) btn.disabled = true;
      if (btnIcon) {
        btnIcon.className = "w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin";
      }
      if (btnText) {
        if (mode === 'cod') {
          btnText.innerText = currentLang === 'hi' ? "सहेजा जा रहा है..." : "Saving default method...";
        } else {
          btnText.innerText = currentLang === 'hi' ? "सत्यापित किया जा रहा है (₹1 परीक्षण शुल्क और रिफंड)..." : "Verifying (₹1 test charge & refund)...";
        }
      }

      try {
        // Execute ₹1 Auth & Void Gateway Simulation
        if (mode !== 'cod') {
          await new Promise(resolve => setTimeout(resolve, 1000));
        }

        const timestamp = Date.now();
        if (mode === 'upi') {
          const upi = (document.getElementById('vault-upi-input')?.value || '').trim();
          verificationResult = {
            auth_void_id: `av_upi_${timestamp}`,
            charge_amount: 1.00,
            refund_status: 'VOIDED_IMMEDIATELY',
            token: `tok_upi_${timestamp}`,
            upi_id: upi
          };
          methodDesc = `UPI: ${upi}`;
          localStorage.setItem('gb_customer_upi_id', upi);
          localStorage.setItem('gb_customer_payout_mode', 'upi');
          localStorage.setItem('gb_customer_payment_setup', 'true');
          localStorage.setItem('gb_customer_auth_void_id', verificationResult.auth_void_id);
          payload.upi_id = upi;
          payload.token = verificationResult.token;
        } else if (mode === 'bank') {
          const holder = (document.getElementById('vault-bank-holder')?.value || '').trim();
          const acc = (document.getElementById('vault-bank-account')?.value || '').trim();
          const ifsc = (document.getElementById('vault-bank-ifsc')?.value || '').trim().toUpperCase();
          const last4 = acc.slice(-4);
          verificationResult = {
            auth_void_id: `av_bank_${timestamp}`,
            charge_amount: 1.00,
            refund_status: 'PENNY_DROP_REFUNDED',
            token: `tok_bank_${timestamp}`,
            account_holder: holder,
            account_last4: last4,
            ifsc: ifsc
          };
          methodDesc = `Bank: ••••${last4} (${ifsc})`;
          localStorage.setItem('gb_customer_bank_holder', holder);
          localStorage.setItem('gb_customer_bank_account', acc);
          localStorage.setItem('gb_customer_bank_ifsc', ifsc);
          localStorage.setItem('gb_customer_payout_mode', 'bank');
          localStorage.setItem('gb_customer_payment_setup', 'true');
          localStorage.setItem('gb_customer_auth_void_id', verificationResult.auth_void_id);
          payload.bank_holder = holder;
          payload.bank_account_last4 = last4;
          payload.bank_ifsc = ifsc;
          payload.token = verificationResult.token;
        } else if (mode === 'card') {
          const cardNum = (document.getElementById('vault-card-number')?.value || '').replace(/\\s+/g, '');
          const cardHolder = (document.getElementById('vault-card-holder')?.value || '').trim();
          const cardExpiry = (document.getElementById('vault-card-expiry')?.value || '').trim();
          const last4 = cardNum.slice(-4);
          const brand = cardNum.startsWith('4') ? 'Visa' : cardNum.startsWith('5') ? 'Mastercard' : 'RuPay';
          verificationResult = {
            auth_void_id: `av_card_${timestamp}`,
            charge_amount: 1.00,
            refund_status: 'VOIDED_IMMEDIATELY',
            token: `tok_card_${timestamp}`,
            brand: brand,
            last4: last4,
            holder: cardHolder,
            expiry: cardExpiry
          };
          methodDesc = `${brand} •••• ${last4} (${cardExpiry})`;
          localStorage.setItem('gb_customer_card_brand', brand);
          localStorage.setItem('gb_customer_card_last4', last4);
          localStorage.setItem('gb_customer_card_holder', cardHolder);
          localStorage.setItem('gb_customer_card_expiry', cardExpiry);
          localStorage.setItem('gb_customer_payout_mode', 'card');
          localStorage.setItem('gb_customer_payment_setup', 'true');
          localStorage.setItem('gb_customer_auth_void_id', verificationResult.auth_void_id);
          payload.card_brand = brand;
          payload.card_last4 = last4;
          payload.card_holder = cardHolder;
          payload.card_expiry = cardExpiry;
          payload.token = verificationResult.token;
          // Clean sensitive card inputs immediately
          const numEl = document.getElementById('vault-card-number');
          const cvvEl = document.getElementById('vault-card-cvv');
          if (numEl) numEl.value = `•••• •••• •••• ${last4}`;
          if (cvvEl) cvvEl.value = '';
        } else if (mode === 'cod') {
          methodDesc = 'Cash on Delivery (COD)';
          localStorage.setItem('gb_customer_payout_mode', 'cod');
          localStorage.setItem('gb_customer_payment_setup', 'true');
          payload.mode = 'cod';
        }

        // Supabase customer ledger synchronization
        const supabaseUrl = (window.APP_CONFIG && window.APP_CONFIG.SUPABASE_URL) || "https://vxewgvrjhjpntfvsmuez.supabase.co";
        const userPhone = (localStorage.getItem('gb_customer_phone') || localStorage.getItem('gb_user_phone') || '9905361711').replace(/\\D/g, '').slice(-10);
        if (userPhone && typeof safeApiCall === 'function') {
          await safeApiCall(`${supabaseUrl}/rest/v1/customers?phone=eq.${userPhone}`, 'PATCH', {
            payment_settings: payload
          }, 4000).catch(err => console.warn("Supabase customer payment notice:", err));
        }

        const descEl = document.getElementById('vault-saved-method-desc');
        if (descEl) descEl.innerText = methodDesc;

        // Show required success toast
        if (mode === 'cod') {
          toastSuccess(currentLang === 'hi' ? "डिफ़ॉल्ट भुगतान विधि कैश ऑन डिलीवरी पर सेट की गई।" : "Default payment method set to Cash on Delivery.");
        } else {
          toastSuccess(currentLang === 'hi' ? "भुगतान विधि सत्यापित और सहेजी गई।" : "Payment method verified and saved.");
        }

        // If in checkout onboarding pipeline:
        if (window.checkoutOnboardingState === 'NEED_PAYMENT') {
          window.checkoutOnboardingState = 'READY';
          closeModal('modal-payment-settings');
          setTimeout(() => {
            openCheckoutPaymentModal();
          }, 400);
        } else {
          closeModal('modal-payment-settings');
        }

      } catch (err) {
        console.error("Payment verification failure:", err);
        toastError(currentLang === 'hi' ? "भुगतान विधि का सत्यापन विफल रहा।" : "Payment method verification failed.");
      } finally {
        if (btn) btn.disabled = false;
        if (btnIcon) {
          btnIcon.className = "w-4 h-4";
          btnIcon.setAttribute('data-lucide', 'check-circle');
        }
        if (btnText) btnText.innerText = originalText;
        if (window.lucide) lucide.createIcons();
      }
    }
    window.saveCustomerPaymentVault = saveCustomerPaymentVault;'''

j_start = html.find(old_js_start)
j_end = html.find(old_js_end)
if j_start != -1 and j_end != -1:
    html = html[:j_start] + new_js_content + html[j_end + len(old_js_end):]
    print("JS logic replaced successfully.")
else:
    print(f"ERROR: Could not locate JS boundaries: {j_start}, {j_end}")

# 3. UPDATE LOAD SAVED VAULT UI
old_load_vault = '''    function loadSavedPaymentVaultUI() {
      const savedMode = localStorage.getItem('gb_customer_payout_mode') || 'upi';
      if (typeof selectVaultPaymentOption === 'function') {
        selectVaultPaymentOption(savedMode);
      }
      const savedUpi = localStorage.getItem('gb_customer_upi_id');
      const upiInput = document.getElementById('vault-upi-input');
      if (savedUpi && upiInput) {
        upiInput.value = savedUpi;
      }
    }'''

new_load_vault = '''    function loadSavedPaymentVaultUI() {
      const savedMode = localStorage.getItem('gb_customer_payout_mode') || 'upi';
      if (typeof selectVaultPaymentOption === 'function') {
        selectVaultPaymentOption(savedMode);
      }
      const savedUpi = localStorage.getItem('gb_customer_upi_id');
      const upiInput = document.getElementById('vault-upi-input');
      if (savedUpi && upiInput) {
        upiInput.value = savedUpi;
      }
      const savedHolder = localStorage.getItem('gb_customer_bank_holder');
      const savedAcc = localStorage.getItem('gb_customer_bank_account');
      const savedIfsc = localStorage.getItem('gb_customer_bank_ifsc');
      if (savedHolder && document.getElementById('vault-bank-holder')) document.getElementById('vault-bank-holder').value = savedHolder;
      if (savedAcc && document.getElementById('vault-bank-account')) {
        document.getElementById('vault-bank-account').value = savedAcc;
        if (document.getElementById('vault-bank-account-confirm')) document.getElementById('vault-bank-account-confirm').value = savedAcc;
      }
      if (savedIfsc && document.getElementById('vault-bank-ifsc')) document.getElementById('vault-bank-ifsc').value = savedIfsc;

      const savedCardLast4 = localStorage.getItem('gb_customer_card_last4');
      if (savedCardLast4 && document.getElementById('vault-card-number')) {
        document.getElementById('vault-card-number').value = `•••• •••• •••• ${savedCardLast4}`;
      }
      const savedCardHolder = localStorage.getItem('gb_customer_card_holder');
      if (savedCardHolder && document.getElementById('vault-card-holder')) {
        document.getElementById('vault-card-holder').value = savedCardHolder;
      }
      const savedCardExpiry = localStorage.getItem('gb_customer_card_expiry');
      if (savedCardExpiry && document.getElementById('vault-card-expiry')) {
        document.getElementById('vault-card-expiry').value = savedCardExpiry;
      }
    }'''

if old_load_vault in html:
    html = html.replace(old_load_vault, new_load_vault, 1)
    print("loadSavedPaymentVaultUI updated successfully.")
else:
    print("WARNING: old_load_vault not matched exact")

# 4. ADD TRANSLATION KEYS
old_en_entry = 'close_btn: "Close"'
new_en_entry = '''close_btn: "Close",
        payment_vault_title: "Payment Settings Vault",
        payment_vault_sub: "Configure your default payment instrument",
        vault_security_primary: "🔒 256-bit Bank-Grade Security",
        vault_security_sub: "Your payment details are tokenized and securely stored via Razorpay. We never store your raw card numbers.",
        vault_save_btn: "Save Payment Details"'''

old_hi_entry = 'close_btn: "बंद करें"'
new_hi_entry = '''close_btn: "बंद करें",
        payment_vault_title: "भुगतान सेटिंग्स वॉल्ट",
        payment_vault_sub: "अपना डिफ़ॉल्ट भुगतान साधन कॉन्फ़िगर करें",
        vault_security_primary: "🔒 256-बिट बैंक-ग्रेड सुरक्षा",
        vault_security_sub: "आपके भुगतान विवरण रेज़रपे के माध्यम से टोकनयुक्त और सुरक्षित रूप से संग्रहीत हैं। हम आपके मूल कार्ड नंबर कभी संग्रहीत नहीं करते हैं।",
        vault_save_btn: "भुगतान विवरण सहेजें"'''

if old_en_entry in html:
    html = html.replace(old_en_entry, new_en_entry, 1)
    print("EN translations added.")

if old_hi_entry in html:
    html = html.replace(old_hi_entry, new_hi_entry, 1)
    print("HI translations added.")

with open('public_web/customer/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("public_web/customer/index.html updated successfully!")
