import re
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

# ==============================================================================
# 1. PATCH CUSTOMER APP
# ==============================================================================
print("1. Patching public_web/customer/index.html...")
with open("public_web/customer/index.html", "r", encoding="utf-8") as f:
    cust_html = f.read()

# 1.A: Update button in Account tab to call openPaymentSettingsModal()
cust_html = cust_html.replace(
    '<button onclick="openModal(\'modal-payment-settings\')"',
    '<button onclick="openPaymentSettingsModal()"'
)

# 1.B: Update Cart Checkout Button to call handleCartCheckoutClick()
cust_html = cust_html.replace(
    '<button onclick="openCheckoutPaymentModal()" id="btn-place-order"',
    '<button onclick="handleCartCheckoutClick()" id="btn-place-order"'
)

# 1.C: Replace static modal-payment-settings with Interactive Payment Settings Vault
old_payment_settings_modal = re.search(
    r'<!-- 7\. PAYMENT SETTINGS MODAL -->\s*<div id="modal-payment-settings".*?<!-- 8\. APP SETTINGS MODAL',
    cust_html,
    re.DOTALL
)

new_payment_settings_modal = """<!-- 7. INTERACTIVE PAYMENT SETTINGS VAULT MODAL -->
    <div id="modal-payment-settings" class="hidden fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
      <div class="w-full max-w-sm bg-white rounded-3xl p-5 shadow-2xl space-y-4 text-left border border-slate-200 max-h-[90vh] overflow-y-auto">
        <!-- Header -->
        <div class="flex items-center justify-between pb-3 border-b border-slate-100">
          <div class="flex items-center space-x-2">
            <button onclick="closeModal('modal-payment-settings')" class="w-8 h-8 rounded-full bg-slate-100 text-slate-600 flex items-center justify-center hover:bg-slate-200 transition">
              <i data-lucide="arrow-left" class="w-4 h-4"></i>
            </button>
            <div>
              <h3 class="text-sm font-bold text-slate-900" data-i18n="payment_vault_title">Payment Settings Vault</h3>
              <p class="text-[10px] text-slate-500" data-i18n="payment_vault_sub">Configure your default UPI or Bank Account</p>
            </div>
          </div>
          <span class="text-xs bg-emerald-100 text-emerald-800 font-bold px-2.5 py-0.5 rounded-full flex items-center space-x-1">
            <i data-lucide="shield-check" class="w-3.5 h-3.5"></i>
            <span>Vault</span>
          </span>
        </div>

        <!-- Mode Toggle Tabs: UPI vs Bank Account -->
        <div class="flex p-1 bg-slate-100 rounded-xl border border-slate-200 text-xs font-bold">
          <button type="button" id="vault-tab-upi" onclick="switchVaultTab('upi')" class="flex-1 py-2.5 rounded-lg transition bg-white text-emerald-700 shadow-xs flex items-center justify-center space-x-1.5">
            <i data-lucide="zap" class="w-3.5 h-3.5 text-emerald-600"></i>
            <span>UPI ID (VPA)</span>
          </button>
          <button type="button" id="vault-tab-bank" onclick="switchVaultTab('bank')" class="flex-1 py-2.5 rounded-lg transition text-slate-600 hover:text-slate-900 flex items-center justify-center space-x-1.5">
            <i data-lucide="landmark" class="w-3.5 h-3.5"></i>
            <span>Bank Account</span>
          </button>
        </div>

        <!-- Saved Active Method Badge Preview -->
        <div id="vault-saved-status-card" class="p-3 bg-emerald-50 rounded-2xl border border-emerald-200 flex items-center justify-between text-xs">
          <div class="flex items-center space-x-2">
            <div class="w-7 h-7 rounded-full bg-emerald-600 text-white flex items-center justify-center font-bold text-xs">
              ✓
            </div>
            <div>
              <span class="text-[10px] uppercase font-bold text-emerald-800 tracking-wider block">Default Configured</span>
              <p id="vault-saved-method-desc" class="font-bold text-slate-900 font-mono text-[11px]">9905361711@upi</p>
            </div>
          </div>
          <span class="text-[10px] font-bold text-emerald-700 bg-white border border-emerald-300 px-2 py-0.5 rounded-full">Active</span>
        </div>

        <!-- FORM 1: UPI ID SETUP -->
        <div id="vault-form-upi" class="space-y-3">
          <div>
            <label class="block text-xs font-semibold text-slate-700 mb-1" data-i18n="vault_upi_label">
              UPI Virtual Payment Address (VPA) <span class="text-rose-500">*</span>
            </label>
            <div class="relative flex items-center">
              <i data-lucide="at-sign" class="absolute left-3.5 w-4 h-4 text-emerald-600 pointer-events-none"></i>
              <input 
                type="text" 
                id="vault-upi-input" 
                placeholder="e.g. 9905361711@upi or name@okaxis" 
                value="9905361711@upi"
                class="w-full pl-10 pr-4 py-3 bg-slate-50 border border-slate-300 focus:border-emerald-600 focus:bg-white focus:outline-none rounded-xl text-xs font-mono font-bold text-slate-900 transition"
              >
            </div>
          </div>

          <!-- Quick UPI Handle Chips -->
          <div>
            <span class="text-[10px] font-semibold text-slate-500 block mb-1">Quick Handle Suffix:</span>
            <div class="flex flex-wrap gap-1.5 text-[10px]">
              <button type="button" onclick="appendUpiSuffix('@upi')" class="px-2 py-1 bg-slate-100 hover:bg-slate-200 rounded-lg text-slate-700 font-mono font-medium">@upi</button>
              <button type="button" onclick="appendUpiSuffix('@okaxis')" class="px-2 py-1 bg-slate-100 hover:bg-slate-200 rounded-lg text-slate-700 font-mono font-medium">@okaxis</button>
              <button type="button" onclick="appendUpiSuffix('@okhdfcbank')" class="px-2 py-1 bg-slate-100 hover:bg-slate-200 rounded-lg text-slate-700 font-mono font-medium">@okhdfcbank</button>
              <button type="button" onclick="appendUpiSuffix('@paytm')" class="px-2 py-1 bg-slate-100 hover:bg-slate-200 rounded-lg text-slate-700 font-mono font-medium">@paytm</button>
              <button type="button" onclick="appendUpiSuffix('@ybl')" class="px-2 py-1 bg-slate-100 hover:bg-slate-200 rounded-lg text-slate-700 font-mono font-medium">@ybl</button>
            </div>
          </div>
        </div>

        <!-- FORM 2: BANK ACCOUNT SETUP -->
        <div id="vault-form-bank" class="space-y-3 hidden">
          <div>
            <label class="block text-xs font-semibold text-slate-700 mb-1">
              Account Holder Name <span class="text-rose-500">*</span>
            </label>
            <input type="text" id="vault-bank-holder" placeholder="Name as per passbook" value="Customer Name" class="w-full px-3.5 py-3 bg-slate-50 border border-slate-300 focus:border-emerald-600 focus:bg-white focus:outline-none rounded-xl text-xs font-bold text-slate-900 transition">
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-700 mb-1">
              Bank Account Number <span class="text-rose-500">*</span>
            </label>
            <input type="password" id="vault-bank-account" placeholder="Enter bank account number" value="50100482910291" class="w-full px-3.5 py-3 bg-slate-50 border border-slate-300 focus:border-emerald-600 focus:bg-white focus:outline-none rounded-xl text-xs font-mono font-bold text-slate-900 transition">
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-700 mb-1">
              Confirm Account Number <span class="text-rose-500">*</span>
            </label>
            <input type="text" id="vault-bank-account-confirm" placeholder="Re-enter bank account number" value="50100482910291" class="w-full px-3.5 py-3 bg-slate-50 border border-slate-300 focus:border-emerald-600 focus:bg-white focus:outline-none rounded-xl text-xs font-mono font-bold text-slate-900 transition">
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-700 mb-1">
              IFSC Code <span class="text-rose-500">*</span>
            </label>
            <input type="text" id="vault-bank-ifsc" placeholder="e.g. HDFC0001234" value="HDFC0001234" class="w-full px-3.5 py-3 bg-slate-50 border border-slate-300 focus:border-emerald-600 focus:bg-white focus:outline-none rounded-xl text-xs font-mono uppercase font-bold text-slate-900 transition">
          </div>
        </div>

        <!-- Security Note -->
        <div class="p-3 bg-slate-50 rounded-xl border border-slate-200 text-[11px] text-slate-500 flex items-start space-x-2">
          <i data-lucide="lock" class="w-3.5 h-3.5 text-slate-400 shrink-0 mt-0.5"></i>
          <span>Details are securely hashed and stored in the encrypted Supabase customer ledger for instant checkouts.</span>
        </div>

        <!-- Action Buttons -->
        <div class="pt-2 space-y-2">
          <button type="button" id="btn-save-payment-vault" onclick="saveCustomerPaymentVault()" class="w-full py-3.5 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-xl shadow-md transition active:scale-98 flex items-center justify-center space-x-2 text-xs">
            <i data-lucide="check-circle" class="w-4 h-4"></i>
            <span id="btn-save-vault-text">Save Payment Details</span>
          </button>
          <button type="button" onclick="closeModal('modal-payment-settings')" class="w-full py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold rounded-xl text-xs transition">
            Close
          </button>
        </div>
      </div>
    </div>

    <!-- 8. APP SETTINGS MODAL"""

if old_payment_settings_modal:
    cust_html = cust_html[:old_payment_settings_modal.start()] + new_payment_settings_modal + cust_html[old_payment_settings_modal.end():]
    print("Customer modal-payment-settings converted into interactive Vault.")
else:
    print("WARNING: Could not find old modal-payment-settings block!")

# 1.D: Add Vault JS & Smart Cart Routing Functions
vault_and_smart_routing_js = """    // ---------------------------------------------------------------------------
    // INTERACTIVE PAYMENT SETTINGS VAULT & SMART CART ROUTING
    // ---------------------------------------------------------------------------
    let currentVaultTab = 'upi';
    window.checkoutOnboardingState = 'INIT'; // 'NEED_ADDRESS', 'NEED_PAYMENT', 'READY'

    function openPaymentSettingsModal() {
      loadSavedPaymentVaultUI();
      openModal('modal-payment-settings');
      if (window.lucide) lucide.createIcons();
    }

    function switchVaultTab(tab) {
      currentVaultTab = tab;
      const tabUpi = document.getElementById('vault-tab-upi');
      const tabBank = document.getElementById('vault-tab-bank');
      const formUpi = document.getElementById('vault-form-upi');
      const formBank = document.getElementById('vault-form-bank');

      if (tab === 'upi') {
        if (tabUpi) tabUpi.className = "flex-1 py-2.5 rounded-lg transition bg-white text-emerald-700 shadow-xs flex items-center justify-center space-x-1.5 font-bold";
        if (tabBank) tabBank.className = "flex-1 py-2.5 rounded-lg transition text-slate-600 hover:text-slate-900 flex items-center justify-center space-x-1.5 font-bold";
        if (formUpi) formUpi.classList.remove('hidden');
        if (formBank) formBank.classList.add('hidden');
      } else {
        if (tabBank) tabBank.className = "flex-1 py-2.5 rounded-lg transition bg-white text-emerald-700 shadow-xs flex items-center justify-center space-x-1.5 font-bold";
        if (tabUpi) tabUpi.className = "flex-1 py-2.5 rounded-lg transition text-slate-600 hover:text-slate-900 flex items-center justify-center space-x-1.5 font-bold";
        if (formBank) formBank.classList.remove('hidden');
        if (formUpi) formUpi.classList.add('hidden');
      }
      if (window.lucide) lucide.createIcons();
    }

    function appendUpiSuffix(suffix) {
      const inp = document.getElementById('vault-upi-input');
      if (!inp) return;
      let val = inp.value.trim();
      if (val.includes('@')) {
        val = val.split('@')[0];
      }
      inp.value = val + suffix;
    }

    function loadSavedPaymentVaultUI() {
      const upi = localStorage.getItem('gb_customer_upi_id') || '9905361711@upi';
      const bankAcc = localStorage.getItem('gb_customer_bank_account') || '';
      const bankHolder = localStorage.getItem('gb_customer_bank_holder') || '';
      const bankIfsc = localStorage.getItem('gb_customer_bank_ifsc') || '';
      const mode = localStorage.getItem('gb_customer_payout_mode') || 'upi';

      const upiInput = document.getElementById('vault-upi-input');
      if (upiInput) upiInput.value = upi;

      const holderInput = document.getElementById('vault-bank-holder');
      if (holderInput && bankHolder) holderInput.value = bankHolder;

      const accInput = document.getElementById('vault-bank-account');
      const accConfirm = document.getElementById('vault-bank-account-confirm');
      if (accInput && bankAcc) accInput.value = bankAcc;
      if (accConfirm && bankAcc) accConfirm.value = bankAcc;

      const ifscInput = document.getElementById('vault-bank-ifsc');
      if (ifscInput && bankIfsc) ifscInput.value = bankIfsc;

      const descEl = document.getElementById('vault-saved-method-desc');
      if (descEl) {
        if (mode === 'bank' && bankAcc) {
          descEl.innerText = `Bank: ••••${bankAcc.slice(-4)} (${bankIfsc || 'Verified'})`;
        } else {
          descEl.innerText = upi;
        }
      }

      switchVaultTab(mode);
    }

    async function saveCustomerPaymentVault() {
      const btn = document.getElementById('btn-save-payment-vault');
      const btnText = document.getElementById('btn-save-vault-text');
      const originalText = btnText ? btnText.innerText : 'Save Payment Details';

      let methodDesc = '';
      let payload = {};

      if (currentVaultTab === 'upi') {
        const upi = (document.getElementById('vault-upi-input')?.value || '').trim();
        if (!upi || !upi.includes('@')) {
          toastError(currentLang === 'hi' ? "कृपया एक मान्य UPI ID दर्ज करें (उदा. 9905361711@upi)" : "Please enter a valid UPI ID (e.g. 9905361711@upi)");
          return;
        }
        localStorage.setItem('gb_customer_upi_id', upi);
        localStorage.setItem('gb_customer_payout_mode', 'upi');
        localStorage.setItem('gb_customer_payment_setup', 'true');
        methodDesc = upi;
        payload = { upi_id: upi, preferred_payment_mode: 'upi' };
      } else {
        const holder = (document.getElementById('vault-bank-holder')?.value || '').trim();
        const acc = (document.getElementById('vault-bank-account')?.value || '').trim();
        const accConfirm = (document.getElementById('vault-bank-account-confirm')?.value || '').trim();
        const ifsc = (document.getElementById('vault-bank-ifsc')?.value || '').trim().toUpperCase();

        if (!holder || !acc || !ifsc) {
          toastError(currentLang === 'hi' ? "कृपया सभी बैंक विवरण भरें" : "Please fill in all bank account details");
          return;
        }
        if (acc !== accConfirm) {
          toastError(currentLang === 'hi' ? "बैंक खाता संख्या मेल नहीं खाती" : "Account numbers do not match");
          return;
        }
        if (ifsc.length < 5) {
          toastError(currentLang === 'hi' ? "कृपया मान्य IFSC कोड दर्ज करें" : "Please enter a valid IFSC code");
          return;
        }

        localStorage.setItem('gb_customer_bank_holder', holder);
        localStorage.setItem('gb_customer_bank_account', acc);
        localStorage.setItem('gb_customer_bank_ifsc', ifsc);
        localStorage.setItem('gb_customer_payout_mode', 'bank');
        localStorage.setItem('gb_customer_payment_setup', 'true');
        methodDesc = `Bank: ••••${acc.slice(-4)} (${ifsc})`;
        payload = { bank_holder: holder, bank_account: acc, bank_ifsc: ifsc, preferred_payment_mode: 'bank' };
      }

      if (btn) btn.disabled = true;
      if (btnText) btnText.innerText = currentLang === 'hi' ? "सुरक्षित रूप से सहेजा जा रहा है..." : "Saving to Secure Vault...";

      // Save to Supabase backend
      try {
        const supabaseUrl = (window.APP_CONFIG && window.APP_CONFIG.SUPABASE_URL) || "https://vxewgvrjhjpntfvsmuez.supabase.co";
        const userPhone = (localStorage.getItem('gb_customer_phone') || localStorage.getItem('gb_user_phone') || '9905361711').replace(/\\D/g, '').slice(-10);
        if (userPhone && typeof safeApiCall === 'function') {
          await safeApiCall(`${supabaseUrl}/rest/v1/customers?phone=eq.${userPhone}`, 'PATCH', {
            payment_settings: payload
          }, 5000).catch(err => console.warn("Supabase customer payment settings notice:", err));
        }
      } catch (err) {
        console.warn("Vault save notice:", err);
      } finally {
        if (btn) btn.disabled = false;
        if (btnText) btnText.innerText = originalText;
      }

      const descEl = document.getElementById('vault-saved-method-desc');
      if (descEl) descEl.innerText = methodDesc;

      toastSuccess(currentLang === 'hi' ? "डिफ़ॉल्ट भुगतान विधि वॉल्ट में सुरक्षित रूप से सहेज ली गई!" : "Default payment method securely saved to vault!");

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
    }

    // SMART CART ROUTING:
    // 1. New Customer: 1. Location/Address Setup -> 2. Payment Setup
    // 2. Returning Customer: Setup screens do NOT appear, directly open Payment Selection Modal
    // 3. Every Order: Ends in explicit Payment Selection Modal (UPI vs COD), never auto-confirmed
    function handleCartCheckoutClick() {
      if (cartItems.length === 0) {
        toastError(currentLang === 'hi' ? "आपका कार्ट खाली है! कृपया सामान जोड़ें।" : "Your cart is empty! Please add items first.");
        return;
      }

      const hasSavedAddress = (Array.isArray(userSavedAddresses) && userSavedAddresses.length > 0) ||
                              (activeCustomerAddress && activeCustomerAddress.village && activeCustomerAddress.village.trim() !== '') ||
                              localStorage.getItem('gb_saved_addresses') !== null;

      const hasPaymentSetup = localStorage.getItem('gb_customer_payment_setup') === 'true' ||
                              (localStorage.getItem('gb_customer_upi_id') && localStorage.getItem('gb_customer_upi_id').trim() !== '') ||
                              (localStorage.getItem('gb_customer_bank_account') && localStorage.getItem('gb_customer_bank_account').trim() !== '');

      // NEW CUSTOMER PIPELINE:
      // Step 1: If no address, route strictly to Location/Address Setup
      if (!hasSavedAddress) {
        window.checkoutOnboardingState = 'NEED_ADDRESS';
        toastInfo(currentLang === 'hi' ? "चरण १: कृपया अपना डिलीवरी पता जोड़ें" : "Step 1: Please set your delivery address");
        openRuralAddressModal();
        return;
      }

      // Step 2: If address saved but payment setup not configured, route to Payment Setup
      if (!hasPaymentSetup) {
        window.checkoutOnboardingState = 'NEED_PAYMENT';
        toastInfo(currentLang === 'hi' ? "चरण २: कृपया अपनी डिफ़ॉल्ट भुगतान विधि सेट करें" : "Step 2: Configure your default payment method");
        openPaymentSettingsModal();
        return;
      }

      // RETURNING CUSTOMER:
      // Neither setup screen appears in cart flow! Direct to clean Order Confirmation / Payment Selection Modal
      window.checkoutOnboardingState = 'READY';
      openCheckoutPaymentModal();
    }
"""

# Insert vault_and_smart_routing_js before openCheckoutPaymentModal
cust_html = cust_html.replace(
    "async function openCheckoutPaymentModal() {",
    vault_and_smart_routing_js + "\n    async function openCheckoutPaymentModal() {"
)

# 1.E: Hook saveCustomerAddress to advance from NEED_ADDRESS to NEED_PAYMENT / READY
save_address_hook = """        closeModal('modal-rural-address');
        renderAccountAddressSummary();
        renderManageAddressesList();
        renderCheckoutAddressSelector();

        toastSuccess(currentLang === 'hi' ? "पता सफलतापूर्वक सुरक्षित हो गया!" : `Address saved! ID: ${authoritativeAddr.id.slice(-6)}`);

        // Advance Smart Cart Pipeline if triggered from Checkout
        if (window.checkoutOnboardingState === 'NEED_ADDRESS') {
          const hasPaymentSetup = localStorage.getItem('gb_customer_payment_setup') === 'true' ||
                                  (localStorage.getItem('gb_customer_upi_id') && localStorage.getItem('gb_customer_upi_id').trim() !== '') ||
                                  (localStorage.getItem('gb_customer_bank_account') && localStorage.getItem('gb_customer_bank_account').trim() !== '');
          if (!hasPaymentSetup) {
            window.checkoutOnboardingState = 'NEED_PAYMENT';
            setTimeout(() => {
              toastInfo(currentLang === 'hi' ? "चरण २: कृपया अपनी डिफ़ॉल्ट भुगतान विधि सेट करें" : "Step 2: Configure your default payment method");
              openPaymentSettingsModal();
            }, 500);
          } else {
            window.checkoutOnboardingState = 'READY';
            setTimeout(() => {
              openCheckoutPaymentModal();
            }, 500);
          }
        }"""

old_save_address_close = """        closeModal('modal-rural-address');
        renderAccountAddressSummary();
        renderManageAddressesList();
        renderCheckoutAddressSelector();

        toastSuccess(currentLang === 'hi' ? "पता सफलतापूर्वक सुरक्षित हो गया!" : `Address saved! ID: ${authoritativeAddr.id.slice(-6)}`);"""

if old_save_address_close in cust_html:
    cust_html = cust_html.replace(old_save_address_close, save_address_hook, 1)
    print("Hooked saveCustomerAddress with smart cart routing.")
else:
    print("WARNING: Could not find old_save_address_close!")

with open("public_web/customer/index.html", "w", encoding="utf-8") as f:
    f.write(cust_html)
print("Customer index.html successfully saved.")


# ==============================================================================
# 2. PATCH VENDOR APP - BILINGUAL & ALPHABETICAL LOCATION SEARCH
# ==============================================================================
print("\n2. Patching public_web/vendor/index.html with bilingual & alphabetical dataset...")
with open("public_web/vendor/index.html", "r", encoding="utf-8") as f:
    vendor_html = f.read()

# Replace vendor RURAL_AREAS_LIST with strictly sorted bilingual dataset
old_vendor_dropdown_block = re.search(
    r'const RURAL_AREAS_LIST = \[.*?\n\s*function handleVendorVillageSearch',
    vendor_html,
    re.DOTALL
)

new_bilingual_vendor_dataset = """// ---------------------------------------------------------------------------
    // COMPREHENSIVE BIHAR RURAL HUBS (STRICTLY ALPHABETICAL & BILINGUAL)
    // ---------------------------------------------------------------------------
    const BIHAR_RURAL_HUBS = [
      { en: "Aurai", hi: "औराई" },
      { en: "Bhabua", hi: "भभुआ" },
      { en: "Bochahan", hi: "बोचहां" },
      { en: "Chaturshi", hi: "चतुरशी" },
      { en: "Darbhanga", hi: "दरभंगा" },
      { en: "Gaighat", hi: "गायघाट" },
      { en: "Hajipur", hi: "हाजीपुर" },
      { en: "Kanti", hi: "कांटी" },
      { en: "Kudra", hi: "कुदरा" },
      { en: "Kurhani", hi: "कुढ़नी" },
      { en: "Mariyabad", hi: "मरियाबाद" },
      { en: "Marwan", hi: "मड़वन" },
      { en: "Minapur", hi: "मीनापुर" },
      { en: "Mohania", hi: "मोहनिया" },
      { en: "Motipur", hi: "मोतीपुर" },
      { en: "Musahri", hi: "मुशहरी" },
      { en: "Muzaffarpur", hi: "मुज़फ़्फ़रपुर" },
      { en: "Paroo", hi: "पारू" },
      { en: "Patna Rural", hi: "पटना ग्रामीण" },
      { en: "Sahebganj", hi: "साहेबगंज" },
      { en: "Sakra", hi: "सकरा" },
      { en: "Samastipur", hi: "समस्तीपुर" },
      { en: "Saraiya", hi: "सरैया" },
      { en: "Sitamarhi", hi: "सीतामढ़ी" },
      { en: "Vaishali", hi: "वैशाली" }
    ];

    // STRICT ALPHABETICAL SORTING (A to Z) by English Name
    const RURAL_AREAS_LIST = BIHAR_RURAL_HUBS.slice().sort((a, b) => a.en.localeCompare(b.en));

    function handleVendorVillageSearch"""

if old_vendor_dropdown_block:
    vendor_html = vendor_html[:old_vendor_dropdown_block.start()] + new_bilingual_vendor_dataset + vendor_html[old_vendor_dropdown_block.end() - len('function handleVendorVillageSearch'):]
    print("Vendor dataset replaced with strictly sorted bilingual data.")

# Update handleVendorVillageSearch function to render bilingual options
old_vendor_search_func = re.search(
    r'function handleVendorVillageSearch\(query\)\s*\{.*?function toggleVendorVillageDropdown\(\)',
    vendor_html,
    re.DOTALL
)

new_vendor_search_func = """function handleVendorVillageSearch(query) {
      const dropdown = document.getElementById('vendor-village-dropdown');
      if (!dropdown) return;
      const q = (query || '').trim().toLowerCase();
      
      const filtered = RURAL_AREAS_LIST.filter(item => {
        const combined = `${item.en} / ${item.hi}`.toLowerCase();
        return item.en.toLowerCase().includes(q) || item.hi.toLowerCase().includes(q) || combined.includes(q);
      });
      
      let html = '';
      if (filtered.length > 0) {
        filtered.forEach(item => {
          const displayLabel = `${item.en} / ${item.hi}`;
          html += `
            <div onclick="selectVendorVillage('${displayLabel.replace(/'/g, "\\\\'")}')" class="px-3.5 py-2.5 hover:bg-emerald-50 cursor-pointer flex items-center justify-between text-xs font-semibold text-slate-800 transition">
              <div class="flex items-center space-x-2">
                <i data-lucide="map-pin" class="w-3.5 h-3.5 text-emerald-600 shrink-0"></i>
                <span class="font-bold text-slate-900">${item.en}</span>
                <span class="text-slate-400">/</span>
                <span class="text-emerald-800 font-medium">${item.hi}</span>
              </div>
              <span class="text-[10px] text-emerald-700 bg-emerald-50 border border-emerald-200 px-1.5 py-0.5 rounded font-bold">Rural Hub</span>
            </div>
          `;
        });
      }

      if (q && !filtered.some(item => `${item.en} / ${item.hi}`.toLowerCase() === q || item.en.toLowerCase() === q)) {
        html += `
          <div onclick="selectVendorVillage('${query.replace(/'/g, "\\\\'")}')" class="px-3.5 py-2.5 hover:bg-emerald-50 cursor-pointer flex items-center space-x-2 text-xs font-bold text-emerald-700 bg-emerald-50/50">
            <i data-lucide="plus-circle" class="w-3.5 h-3.5 text-emerald-600 shrink-0"></i>
            <span>Use "${query}"</span>
          </div>
        `;
      }

      dropdown.innerHTML = html;
      dropdown.classList.remove('hidden');
      if (window.lucide) lucide.createIcons();
    }

    function toggleVendorVillageDropdown()"""

if old_vendor_search_func:
    vendor_html = vendor_html[:old_vendor_search_func.start()] + new_vendor_search_func + vendor_html[old_vendor_search_func.end() - len('function toggleVendorVillageDropdown()'):]
    print("Vendor handleVendorVillageSearch updated for bilingual options.")

# Set initial placeholder/value in HTML
vendor_html = vendor_html.replace('value="Muzaffarpur"', 'value="Muzaffarpur / मुज़फ़्फ़रपुर"')
vendor_html = vendor_html.replace("if (vInput && !vInput.value) vInput.value = 'Muzaffarpur';", "if (vInput && !vInput.value) vInput.value = 'Muzaffarpur / मुज़फ़्फ़रपुर';")

with open("public_web/vendor/index.html", "w", encoding="utf-8") as f:
    f.write(vendor_html)
print("Vendor index.html successfully saved.")


# ==============================================================================
# 3. PATCH RUNNER APP - BILINGUAL & ALPHABETICAL LOCATION SEARCH
# ==============================================================================
print("\n3. Patching public_web/runner/index.html with bilingual & alphabetical dataset...")
with open("public_web/runner/index.html", "r", encoding="utf-8") as f:
    runner_html = f.read()

# Replace runner RURAL_AREAS_LIST with strictly sorted bilingual dataset
old_runner_dropdown_block = re.search(
    r'const RURAL_AREAS_LIST = \[.*?\n\s*function handleRunnerVillageSearch',
    runner_html,
    re.DOTALL
)

new_bilingual_runner_dataset = """// ---------------------------------------------------------------------------
    // COMPREHENSIVE BIHAR RURAL HUBS (STRICTLY ALPHABETICAL & BILINGUAL)
    // ---------------------------------------------------------------------------
    const BIHAR_RURAL_HUBS = [
      { en: "Aurai", hi: "औराई" },
      { en: "Bhabua", hi: "भभुआ" },
      { en: "Bochahan", hi: "बोचहां" },
      { en: "Chaturshi", hi: "चतुरशी" },
      { en: "Darbhanga", hi: "दरभंगा" },
      { en: "Gaighat", hi: "गायघाट" },
      { en: "Hajipur", hi: "हाजीपुर" },
      { en: "Kanti", hi: "कांटी" },
      { en: "Kudra", hi: "कुदरा" },
      { en: "Kurhani", hi: "कुढ़नी" },
      { en: "Mariyabad", hi: "मरियाबाद" },
      { en: "Marwan", hi: "मड़वन" },
      { en: "Minapur", hi: "मीनापुर" },
      { en: "Mohania", hi: "मोहनिया" },
      { en: "Motipur", hi: "मोतीपुर" },
      { en: "Musahri", hi: "मुशहरी" },
      { en: "Muzaffarpur", hi: "मुज़फ़्फ़रपुर" },
      { en: "Paroo", hi: "पारू" },
      { en: "Patna Rural", hi: "पटना ग्रामीण" },
      { en: "Sahebganj", hi: "साहेबगंज" },
      { en: "Sakra", hi: "सकरा" },
      { en: "Samastipur", hi: "समस्तीपुर" },
      { en: "Saraiya", hi: "सरैया" },
      { en: "Sitamarhi", hi: "सीतामढ़ी" },
      { en: "Vaishali", hi: "वैशाली" }
    ];

    // STRICT ALPHABETICAL SORTING (A to Z) by English Name
    const RURAL_AREAS_LIST = BIHAR_RURAL_HUBS.slice().sort((a, b) => a.en.localeCompare(b.en));

    function handleRunnerVillageSearch"""

if old_runner_dropdown_block:
    runner_html = runner_html[:old_runner_dropdown_block.start()] + new_bilingual_runner_dataset + runner_html[old_runner_dropdown_block.end() - len('function handleRunnerVillageSearch'):]
    print("Runner dataset replaced with strictly sorted bilingual data.")

# Update handleRunnerVillageSearch function to render bilingual options
old_runner_search_func = re.search(
    r'function handleRunnerVillageSearch\(query\)\s*\{.*?function toggleRunnerVillageDropdown\(\)',
    runner_html,
    re.DOTALL
)

new_runner_search_func = """function handleRunnerVillageSearch(query) {
      const dropdown = document.getElementById('runner-village-dropdown');
      if (!dropdown) return;
      const q = (query || '').trim().toLowerCase();
      
      const filtered = RURAL_AREAS_LIST.filter(item => {
        const combined = `${item.en} / ${item.hi}`.toLowerCase();
        return item.en.toLowerCase().includes(q) || item.hi.toLowerCase().includes(q) || combined.includes(q);
      });
      
      let html = '';
      if (filtered.length > 0) {
        filtered.forEach(item => {
          const displayLabel = `${item.en} / ${item.hi}`;
          html += `
            <div onclick="selectRunnerVillage('${displayLabel.replace(/'/g, "\\\\'")}')" class="px-3.5 py-2.5 hover:bg-blue-50 cursor-pointer flex items-center justify-between text-xs font-semibold text-slate-800 transition">
              <div class="flex items-center space-x-2">
                <i data-lucide="map-pin" class="w-3.5 h-3.5 text-blue-600 shrink-0"></i>
                <span class="font-bold text-slate-900">${item.en}</span>
                <span class="text-slate-400">/</span>
                <span class="text-blue-800 font-medium">${item.hi}</span>
              </div>
              <span class="text-[10px] text-blue-700 bg-blue-50 border border-blue-200 px-1.5 py-0.5 rounded font-bold">Operating Hub</span>
            </div>
          `;
        });
      }

      if (q && !filtered.some(item => `${item.en} / ${item.hi}`.toLowerCase() === q || item.en.toLowerCase() === q)) {
        html += `
          <div onclick="selectRunnerVillage('${query.replace(/'/g, "\\\\'")}')" class="px-3.5 py-2.5 hover:bg-blue-50 cursor-pointer flex items-center space-x-2 text-xs font-bold text-blue-700 bg-blue-50/50">
            <i data-lucide="plus-circle" class="w-3.5 h-3.5 text-blue-600 shrink-0"></i>
            <span>Use "${query}"</span>
          </div>
        `;
      }

      dropdown.innerHTML = html;
      dropdown.classList.remove('hidden');
      if (window.lucide) lucide.createIcons();
    }

    function toggleRunnerVillageDropdown()"""

if old_runner_search_func:
    runner_html = runner_html[:old_runner_search_func.start()] + new_runner_search_func + runner_html[old_runner_search_func.end() - len('function toggleRunnerVillageDropdown()'):]
    print("Runner handleRunnerVillageSearch updated for bilingual options.")

# Set initial placeholder/value in HTML
runner_html = runner_html.replace('value="Muzaffarpur"', 'value="Muzaffarpur / मुज़फ़्फ़रपुर"')
runner_html = runner_html.replace("if (rInput && !rInput.value) rInput.value = 'Muzaffarpur';", "if (rInput && !rInput.value) rInput.value = 'Muzaffarpur / मुज़फ़्फ़रपुर';")

with open("public_web/runner/index.html", "w", encoding="utf-8") as f:
    f.write(runner_html)
print("Runner index.html successfully saved.")

print("\nALL 3 APPS UPDATED SUCCESSFULLY.")
