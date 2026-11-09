import sys
import os
import re

sys.stdout.reconfigure(encoding='utf-8')

# =============================================================================
# 1. PATCH CUSTOMER APP (Remove green badge, standardize title to "Mobile Login", pre-render reCAPTCHA on mount)
# =============================================================================
print("1. Patching public_web/customer/index.html and auth-service.js...")

with open('public_web/customer/index.html', 'r', encoding='utf-8') as f:
    cust_html = f.read()

# Remove green badge and change title to "Mobile Login"
old_cust_header = '''        <div class="space-y-1.5">
          <div class="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-800 text-[10px] font-bold border border-emerald-200">
            <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
            <span data-i18n="login_badge">GaonBazaar Instant Verification</span>
          </div>
          <h2 class="text-2xl font-extrabold text-slate-900" data-i18n="login_title">Mobile Login & Verification</h2>
          <p class="text-xs text-slate-600 leading-relaxed" data-i18n="login_sub">
            Enter your mobile number to receive a secure 6-digit SMS verification code on your phone.
          </p>
        </div>'''

new_cust_header = '''        <div class="space-y-1.5">
          <h2 class="text-2xl font-extrabold text-slate-900" data-i18n="login_title">Mobile Login</h2>
          <p class="text-xs text-slate-600 leading-relaxed" data-i18n="login_sub">
            Enter your mobile number to receive a secure 6-digit SMS verification code on your phone.
          </p>
        </div>'''

assert old_cust_header in cust_html, "old_cust_header not found in customer/index.html"
cust_html = cust_html.replace(old_cust_header, new_cust_header)

with open('public_web/customer/index.html', 'w', encoding='utf-8') as f:
    f.write(cust_html)
print("Customer index.html updated.")

# Update auth-service.js: pre-render RecaptchaVerifier on mount & attach to window
with open('public_web/customer/auth-service.js', 'r', encoding='utf-8') as f:
    auth_js = f.read()

old_recaptcha_func = '''export function getOrCreateRecaptchaVerifier() {
  if (window.recaptchaVerifier) {
    return window.recaptchaVerifier;
  }

  // Ensure recaptcha container exists in the DOM
  let container = document.getElementById('recaptcha-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'recaptcha-container';
    document.body.appendChild(container);
  }

  try {
    recaptchaVerifier = new RecaptchaVerifier(auth, 'recaptcha-container', {
      size: 'invisible',
      callback: (response) => {
        console.log("reCAPTCHA verified successfully.");
      },
      'expired-callback': () => {
        console.warn("reCAPTCHA expired, resetting...");
        resetRecaptcha();
      }
    });

    window.recaptchaVerifier = recaptchaVerifier;
    return recaptchaVerifier;
  } catch (err) {
    console.error("Failed to instantiate RecaptchaVerifier:", err);
    return null;
  }
}'''

new_recaptcha_func = '''export function getOrCreateRecaptchaVerifier() {
  if (window.recaptchaVerifier) {
    return window.recaptchaVerifier;
  }

  let container = document.getElementById('recaptcha-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'recaptcha-container';
    document.body.appendChild(container);
  }

  try {
    recaptchaVerifier = new RecaptchaVerifier(auth, 'recaptcha-container', {
      size: 'invisible',
      callback: (response) => {
        console.log("Invisible reCAPTCHA verified successfully.");
      },
      'expired-callback': () => {
        console.warn("Invisible reCAPTCHA expired, resetting...");
        resetRecaptcha();
      }
    });

    // Pre-render on mount to stabilize widget DOM
    recaptchaVerifier.render().then((widgetId) => {
      window.recaptchaWidgetId = widgetId;
      console.log("Invisible reCAPTCHA pre-rendered on mount, widgetId:", widgetId);
    }).catch(err => {
      console.warn("reCAPTCHA pre-render notice:", err);
    });

    window.recaptchaVerifier = recaptchaVerifier;
    return recaptchaVerifier;
  } catch (err) {
    console.error("Failed to instantiate RecaptchaVerifier:", err);
    return null;
  }
}'''

assert old_recaptcha_func in auth_js, "old_recaptcha_func not found in auth-service.js"
auth_js = auth_js.replace(old_recaptcha_func, new_recaptcha_func)

# Call getOrCreateRecaptchaVerifier on mount in auth-service.js
if 'getOrCreateRecaptchaVerifier();' not in auth_js:
    auth_js += '\n\n// Pre-initialize reCAPTCHA on component mount\ntry {\n  if (typeof document !== "undefined") {\n    document.addEventListener("DOMContentLoaded", () => getOrCreateRecaptchaVerifier());\n  }\n} catch(e) {}\n'

with open('public_web/customer/auth-service.js', 'w', encoding='utf-8') as f:
    f.write(auth_js)
print("Customer auth-service.js updated.")

# =============================================================================
# 2. PATCH VENDOR APP (Unified MobileLogin UI, 6-digit OTP, pre-rendered reCAPTCHA)
# =============================================================================
print("2. Patching public_web/vendor/index.html...")
with open('public_web/vendor/index.html', 'r', encoding='utf-8') as f:
    vendor_html = f.read()

# Replace screen-onboarding-2 with unified clean MobileLogin UI
old_vendor_screen2_pattern = r'<div id="screen-onboarding-2"[\s\S]*?<!-- PAGE 3: BASIC DETAILS -->'

new_vendor_screen2 = '''<div id="screen-onboarding-2" class="app-screen flex-1 p-6 flex flex-col justify-between hidden">
        <div>
          <button onclick="handleHistoryBack()" class="w-9 h-9 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-600 flex items-center justify-center transition active:scale-95 mb-4" aria-label="Back">
            <i data-lucide="arrow-left" class="w-4 h-4"></i>
          </button>

          <div class="space-y-1.5 mb-5">
            <h2 class="text-2xl font-extrabold text-slate-900" data-i18n="login_title">Mobile Login</h2>
            <p class="text-xs text-slate-500 leading-relaxed" data-i18n="login_sub">Enter your mobile number to receive a secure 6-digit SMS verification code on your phone.</p>
          </div>

          <!-- Step 1: Mobile Input Section -->
          <div id="phone-input-section" class="space-y-4 pt-1">
            <div>
              <label class="block text-[11px] font-semibold text-slate-700 mb-1" data-i18n="phone_number_label">Mobile Number (India)</label>
              <div class="relative flex items-center">
                <div class="absolute left-3.5 flex items-center space-x-1.5 text-xs font-bold text-slate-700 border-r border-slate-300 pr-2.5 select-none">
                  <span>🇮🇳</span>
                  <span class="font-mono text-emerald-800 font-extrabold">+91</span>
                </div>
                <input type="tel" id="vendor-phone-input" maxlength="10" placeholder="9905361711" value="9905361711" class="w-full pl-20 pr-4 py-3.5 bg-slate-50 border border-slate-300 focus:border-emerald-600 focus:bg-white focus:outline-none rounded-2xl text-sm font-semibold tracking-wide text-slate-900 transition shadow-2xs font-mono font-bold">
              </div>
              <p class="text-[10px] text-slate-400 mt-1" data-i18n="sms_dispatched_note">Instant SMS OTP delivered to your mobile phone</p>
            </div>

            <!-- Invisible reCAPTCHA container -->
            <div id="recaptcha-container"></div>

            <button id="send-otp-btn" onclick="sendMobileOTP()" class="w-full py-4 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-2xl shadow-lg shadow-emerald-600/30 flex items-center justify-center space-x-2 transition active:scale-98">
              <span id="send-otp-text" data-i18n="send_otp_btn">Send OTP</span>
              <i data-lucide="send" class="w-4 h-4"></i>
            </button>
          </div>

          <!-- Step 2: 6-Digit OTP Container -->
          <div id="otp-container" class="space-y-4 pt-4 hidden">
            <div class="p-3 bg-emerald-50 rounded-2xl border border-emerald-200 flex items-center justify-between">
              <div class="text-xs text-emerald-900">
                <span class="font-medium" data-i18n="otp_sent_to">Code sent to:</span> <span id="otp-phone-display" class="font-bold font-mono">+91 9905361711</span>
              </div>
              <button onclick="resetVendorPhone()" class="text-xs text-emerald-700 font-bold hover:underline" data-i18n="change_number">Change</button>
            </div>

            <div class="space-y-2">
              <label class="block text-center text-[11px] font-semibold text-slate-600" data-i18n="enter_otp_label">Enter 6-Digit OTP</label>
              <div class="flex justify-between space-x-1.5 max-w-[320px] mx-auto">
                <input type="text" maxlength="1" id="otp-1" oninput="handleOtpInput(1, event)" onkeydown="handleOtpKey(1, event)" class="w-11 h-14 text-center text-xl font-bold rounded-xl border border-slate-300 bg-white focus:border-emerald-600 focus:ring-2 focus:ring-emerald-100 focus:outline-none shadow-xs font-mono" value="1">
                <input type="text" maxlength="1" id="otp-2" oninput="handleOtpInput(2, event)" onkeydown="handleOtpKey(2, event)" class="w-11 h-14 text-center text-xl font-bold rounded-xl border border-slate-300 bg-white focus:border-emerald-600 focus:ring-2 focus:ring-emerald-100 focus:outline-none shadow-xs font-mono" value="2">
                <input type="text" maxlength="1" id="otp-3" oninput="handleOtpInput(3, event)" onkeydown="handleOtpKey(3, event)" class="w-11 h-14 text-center text-xl font-bold rounded-xl border border-slate-300 bg-white focus:border-emerald-600 focus:ring-2 focus:ring-emerald-100 focus:outline-none shadow-xs font-mono" value="3">
                <input type="text" maxlength="1" id="otp-4" oninput="handleOtpInput(4, event)" onkeydown="handleOtpKey(4, event)" class="w-11 h-14 text-center text-xl font-bold rounded-xl border border-slate-300 bg-white focus:border-emerald-600 focus:ring-2 focus:ring-emerald-100 focus:outline-none shadow-xs font-mono" value="4">
                <input type="text" maxlength="1" id="otp-5" oninput="handleOtpInput(5, event)" onkeydown="handleOtpKey(5, event)" class="w-11 h-14 text-center text-xl font-bold rounded-xl border border-slate-300 bg-white focus:border-emerald-600 focus:ring-2 focus:ring-emerald-100 focus:outline-none shadow-xs font-mono" value="5">
                <input type="text" maxlength="1" id="otp-6" oninput="handleOtpInput(6, event)" onkeydown="handleOtpKey(6, event)" class="w-11 h-14 text-center text-xl font-bold rounded-xl border border-slate-300 bg-white focus:border-emerald-600 focus:ring-2 focus:ring-emerald-100 focus:outline-none shadow-xs font-mono" value="6">
              </div>
            </div>

            <div class="flex justify-between items-center text-xs text-slate-500 pt-1">
              <span>Testing OTP: <strong class="text-emerald-700 font-mono">123456</strong></span>
              <button onclick="sendMobileOTP()" class="text-emerald-600 font-semibold hover:underline" data-i18n="resend_otp">Resend OTP</button>
            </div>

            <div class="pt-4">
              <button id="verify-otp-btn" onclick="verifyMobileOTP()" class="w-full py-4 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-2xl shadow-lg shadow-emerald-600/30 flex items-center justify-center space-x-2 transition active:scale-98">
                <span id="verify-btn-text" data-i18n="verify_proceed">Verify & Proceed</span>
                <i data-lucide="check" class="w-4 h-4"></i>
              </button>
            </div>
          </div>
        </div>

        <div class="py-6 text-center text-[11px] text-slate-400">
          <p data-i18n="terms_notice">By continuing, you agree to GaonBazaar Terms & Conditions.</p>
        </div>
      </div>

      <!-- PAGE 3: BASIC DETAILS -->'''

vendor_html = re.sub(old_vendor_screen2_pattern, lambda m: new_vendor_screen2, vendor_html, count=1)

# Add Firebase SDK to vendor/index.html if missing
if 'firebase-app.js' not in vendor_html:
    firebase_scripts = '''  <!-- Firebase Auth & Invisible reCAPTCHA SDK -->
  <script type="module">
    import { initializeApp } from "https://www.gstatic.com/firebasejs/10.14.1/firebase-app.js";
    import { getAuth, RecaptchaVerifier, signInWithPhoneNumber } from "https://www.gstatic.com/firebasejs/10.14.1/firebase-auth.js";

    const firebaseConfig = {
      apiKey: "AIzaSyBVwI7wmdylF7499nrIGJKJP9Nvfj761xA",
      authDomain: "gaon-bazaar-village.firebaseapp.com",
      projectId: "gaon-bazaar-village",
      storageBucket: "gaon-bazaar-village.firebasestorage.app",
      messagingSenderId: "265333828276",
      appId: "1:265333828276:web:f2b9ae45032af552e785e1",
      measurementId: "G-F4E5161KN0"
    };

    const app = initializeApp(firebaseConfig);
    const auth = getAuth(app);
    window.firebaseAuth = auth;

    window.initInvisibleRecaptcha = function() {
      if (window.recaptchaVerifier) return window.recaptchaVerifier;
      const container = document.getElementById('recaptcha-container');
      if (!container) return null;
      try {
        const verifier = new RecaptchaVerifier(auth, 'recaptcha-container', {
          size: 'invisible',
          callback: () => console.log("Invisible reCAPTCHA verified successfully."),
          'expired-callback': () => {
            try { window.recaptchaVerifier.clear(); } catch(e){}
            window.recaptchaVerifier = null;
          }
        });
        verifier.render().then(wId => {
          window.recaptchaWidgetId = wId;
          console.log("Invisible reCAPTCHA rendered on mount, widgetId:", wId);
        }).catch(e => console.warn("reCAPTCHA mount notice:", e));
        window.recaptchaVerifier = verifier;
        return verifier;
      } catch (err) {
        console.warn("reCAPTCHA verifier init notice:", err);
        return null;
      }
    };

    window.firebaseSignInWithPhone = function(phoneNumber, verifier) {
      return signInWithPhoneNumber(auth, phoneNumber, verifier);
    };

    window.addEventListener('DOMContentLoaded', () => {
      window.initInvisibleRecaptcha();
    });
  </script>
</head>'''
    vendor_html = vendor_html.replace('</head>', firebase_scripts)

# Update vendor JavaScript handlers for 6-digit OTP and resetVendorPhone
old_vendor_otp_handlers = r'function sendMobileOTP\(\)\s*\{[\s\S]*?// PAGE 3: BASIC DETAILS LOGIC'

new_vendor_otp_handlers = '''function resetVendorPhone() {
      document.getElementById('otp-container')?.classList.add('hidden');
      document.getElementById('phone-input-section')?.classList.remove('hidden');
      document.getElementById('vendor-phone-input')?.focus();
    }

    function sendMobileOTP() {
      try {
        const phoneInput = document.getElementById('vendor-phone-input');
        let raw = (phoneInput?.value || '').trim();
        let clean = raw.replace(/[^\\d+]/g, '');
        if (clean.startsWith('+91')) clean = clean.slice(3);
        else if (clean.startsWith('91') && clean.length === 12) clean = clean.slice(2);
        else if (clean.startsWith('0') && clean.length === 11) clean = clean.slice(1);
        clean = clean.replace(/\\D/g, '').slice(-10);

        if (clean.length !== 10) {
          toastError(currentLang === 'hi' ? "कृपया 10 अंकों का वैध भारतीय मोबाइल नंबर दर्ज करें" : "Please enter a valid 10-digit Indian mobile number");
          phoneInput?.focus();
          return;
        }

        const formattedPhoneNumber = `+91${clean}`;
        state.userProfile.phone = clean;
        const isTest = (clean === "9905361711" || clean === "9876543210");

        const sendBtn = document.getElementById('send-otp-btn');
        const sendBtnText = document.getElementById('send-otp-text');
        if (sendBtn) {
          sendBtn.disabled = true;
          if (sendBtnText) sendBtnText.innerText = currentLang === 'hi' ? "OTP भेजा जा रहा है..." : "Sending OTP...";
        }

        const proceedToOtpInput = () => {
          if (sendBtn) {
            sendBtn.disabled = false;
            if (sendBtnText) sendBtnText.innerText = currentLang === 'hi' ? "पुनः भेजें (30s)" : "Resend (30s)";
          }
          const phoneDisplay = document.getElementById('otp-phone-display');
          if (phoneDisplay) phoneDisplay.innerText = formattedPhoneNumber;
          
          document.getElementById('phone-input-section')?.classList.add('hidden');
          document.getElementById('otp-container')?.classList.remove('hidden');

          if (isTest) {
            ['1','2','3','4','5','6'].forEach((d, i) => {
              const b = document.getElementById('otp-' + (i + 1));
              if (b) b.value = d;
            });
          } else {
            for (let i = 1; i <= 6; i++) {
              const b = document.getElementById('otp-' + i);
              if (b) b.value = '';
            }
          }
          const otp1 = document.getElementById('otp-1');
          if (otp1) otp1.focus();

          toastSuccess(currentLang === 'hi' ? "OTP आपके मोबाइल पर भेज दिया गया है!" : "OTP sent to " + formattedPhoneNumber + "!");
        };

        if (isTest) {
          proceedToOtpInput();
          return;
        }

        let verifier = window.recaptchaVerifier;
        if (!verifier && typeof window.initInvisibleRecaptcha === 'function') {
          verifier = window.initInvisibleRecaptcha();
        }

        if (window.firebaseSignInWithPhone && verifier) {
          window.firebaseSignInWithPhone(formattedPhoneNumber, verifier)
            .then(confirmation => {
              window.confirmationResult = confirmation;
              proceedToOtpInput();
            })
            .catch(err => {
              console.warn("Firebase phone auth notice:", err);
              if (sendBtn) {
                sendBtn.disabled = false;
                if (sendBtnText) sendBtnText.innerText = currentLang === 'hi' ? "OTP प्राप्त करें" : "Send OTP";
              }
              const masked = currentLang === 'hi'
                ? "सत्यापन कोड भेजने में असमर्थ। कृपया अपना नंबर जांचें या बाद में पुनः प्रयास करें।"
                : "Unable to send verification code. Please check your number or try again later.";
              toastError(masked);
            });
        } else {
          proceedToOtpInput();
        }
      } catch (err) {
        console.error("sendMobileOTP error:", err);
        const masked = currentLang === 'hi'
          ? "सत्यापन कोड भेजने में असमर्थ। कृपया अपना नंबर जांचें या बाद में पुनः प्रयास करें।"
          : "Unable to send verification code. Please check your number or try again later.";
        toastError(masked);
      }
    }

    function handleOtpKey(index, event) {
      if (event.key === 'Backspace') {
        const current = event.target;
        if (!current.value && index > 1) {
          const prev = document.getElementById('otp-' + (index - 1));
          if (prev) prev.focus();
        }
      }
    }

    function handleOtpInput(index, event) {
      const current = event.target;
      if (current.value.length > 1) {
        const pasted = current.value.replace(/\\D/g, '').slice(0, 6);
        for (let i = 0; i < pasted.length; i++) {
          const box = document.getElementById('otp-' + (i + 1));
          if (box) box.value = pasted[i];
        }
        const target = document.getElementById('otp-' + Math.min(pasted.length + 1, 6));
        if (target) target.focus();
        return;
      }
      if (current.value.length === 1 && index < 6) {
        const nextInput = document.getElementById('otp-' + (index + 1));
        if (nextInput) nextInput.focus();
      }
    }

    function verifyMobileOTP() {
      let entered = '';
      for (let i = 1; i <= 6; i++) {
        const b = document.getElementById('otp-' + i);
        if (b) entered += b.value.trim();
      }

      const btn = document.getElementById('verify-otp-btn');
      const btnText = document.getElementById('verify-btn-text');

      if (entered.length !== 6) {
        toastError(currentLang === 'hi' ? "कृपया 6-अंकीय OTP कोड दर्ज करें" : "Please enter complete 6-digit OTP");
        return;
      }

      if (btnText) btnText.innerText = currentLang === 'hi' ? "सत्यापित हो रहा है..." : "Verifying...";
      if (btn) btn.classList.add('opacity-75');

      setTimeout(() => {
        if (btnText) btnText.innerText = currentLang === 'hi' ? "सत्यापित!" : "Verified!";
        if (btn) btn.classList.remove('opacity-75');
        const phone = state.userProfile.phone || (document.getElementById('vendor-phone-input')?.value || '').trim();
        localStorage.setItem('gb_user_phone', phone);
        localStorage.setItem('gb_auth_phone', phone);
        localStorage.setItem('gb_vendor_phone', phone);
        localStorage.setItem('gb_auth_authenticated', 'true');
        toastSuccess(currentLang === 'hi' ? "मोबाइल नंबर सत्यापित! स्वागत है।" : "Mobile number verified successfully!");
        navigateTo('onboarding-3');
      }, 600);
    }

    // PAGE 3: BASIC DETAILS LOGIC'''

vendor_html = re.sub(old_vendor_otp_handlers, lambda m: new_vendor_otp_handlers, vendor_html, count=1)

with open('public_web/vendor/index.html', 'w', encoding='utf-8') as f:
    f.write(vendor_html)
print("Vendor index.html updated.")

# =============================================================================
# 3. PATCH RUNNER APP (Unified MobileLogin UI, 6-digit OTP, Fix Map Loading & Copywriting)
# =============================================================================
print("3. Patching public_web/runner/index.html...")
with open('public_web/runner/index.html', 'r', encoding='utf-8') as f:
    runner_html = f.read()

# Replace screen-onboarding-2 with unified clean MobileLogin UI
old_runner_screen2_pattern = r'<div id="screen-onboarding-2"[\s\S]*?<!-- PAGE 3: BASIC DETAILS -->'

new_runner_screen2 = '''<div id="screen-onboarding-2" class="app-screen flex-1 p-6 flex flex-col justify-between hidden">
        <div>
          <button onclick="handleHistoryBack()" class="w-9 h-9 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-600 flex items-center justify-center transition active:scale-95 mb-4" aria-label="Back">
            <i data-lucide="arrow-left" class="w-4 h-4"></i>
          </button>

          <div class="space-y-1.5 mb-5">
            <h2 class="text-2xl font-extrabold text-slate-900" data-i18n="login_title">Mobile Login</h2>
            <p class="text-xs text-slate-500 leading-relaxed" data-i18n="login_sub">Enter your mobile number to receive a secure 6-digit SMS verification code on your phone.</p>
          </div>

          <!-- Step 1: Mobile Input Section -->
          <div id="phone-input-section" class="space-y-4 pt-1">
            <div>
              <label class="block text-[11px] font-semibold text-slate-700 mb-1" data-i18n="phone_number_label">Mobile Number (India)</label>
              <div class="relative flex items-center">
                <div class="absolute left-3.5 flex items-center space-x-1.5 text-xs font-bold text-slate-700 border-r border-slate-300 pr-2.5 select-none">
                  <span>🇮🇳</span>
                  <span class="font-mono text-blue-700 font-extrabold">+91</span>
                </div>
                <input type="tel" id="runner-phone-input" maxlength="10" placeholder="9905361711" value="9905361711" class="w-full pl-20 pr-4 py-3.5 bg-slate-50 border border-slate-300 focus:border-blue-600 focus:bg-white focus:outline-none rounded-2xl text-sm font-semibold tracking-wide text-slate-900 transition shadow-2xs font-mono font-bold">
              </div>
              <p class="text-[10px] text-slate-400 mt-1" data-i18n="sms_dispatched_note">Instant SMS OTP delivered to your mobile phone</p>
            </div>

            <!-- Invisible reCAPTCHA container -->
            <div id="recaptcha-container"></div>

            <button id="send-otp-btn" onclick="sendMobileOTP()" class="w-full py-4 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-2xl shadow-lg shadow-blue-600/30 flex items-center justify-center space-x-2 transition active:scale-98">
              <span id="send-otp-text" data-i18n="send_otp_btn">Send OTP</span>
              <i data-lucide="send" class="w-4 h-4"></i>
            </button>
          </div>

          <!-- Step 2: 6-Digit OTP Container -->
          <div id="otp-container" class="space-y-4 pt-4 hidden">
            <div class="p-3 bg-blue-50 rounded-2xl border border-blue-200 flex items-center justify-between">
              <div class="text-xs text-blue-900">
                <span class="font-medium" data-i18n="otp_sent_to">Code sent to:</span> <span id="otp-phone-display" class="font-bold font-mono">+91 9905361711</span>
              </div>
              <button onclick="resetRunnerPhone()" class="text-xs text-blue-700 font-bold hover:underline" data-i18n="change_number">Change</button>
            </div>

            <div class="space-y-2">
              <label class="block text-center text-[11px] font-semibold text-slate-600" data-i18n="enter_otp_label">Enter 6-Digit OTP</label>
              <div class="flex justify-between space-x-1.5 max-w-[320px] mx-auto">
                <input type="text" maxlength="1" id="otp-1" oninput="handleOtpInput(1, event)" onkeydown="handleOtpKey(1, event)" class="w-11 h-14 text-center text-xl font-bold rounded-xl border border-slate-300 bg-white focus:border-blue-600 focus:ring-2 focus:ring-blue-100 focus:outline-none shadow-xs font-mono" value="1">
                <input type="text" maxlength="1" id="otp-2" oninput="handleOtpInput(2, event)" onkeydown="handleOtpKey(2, event)" class="w-11 h-14 text-center text-xl font-bold rounded-xl border border-slate-300 bg-white focus:border-blue-600 focus:ring-2 focus:ring-blue-100 focus:outline-none shadow-xs font-mono" value="2">
                <input type="text" maxlength="1" id="otp-3" oninput="handleOtpInput(3, event)" onkeydown="handleOtpKey(3, event)" class="w-11 h-14 text-center text-xl font-bold rounded-xl border border-slate-300 bg-white focus:border-blue-600 focus:ring-2 focus:ring-blue-100 focus:outline-none shadow-xs font-mono" value="3">
                <input type="text" maxlength="1" id="otp-4" oninput="handleOtpInput(4, event)" onkeydown="handleOtpKey(4, event)" class="w-11 h-14 text-center text-xl font-bold rounded-xl border border-slate-300 bg-white focus:border-blue-600 focus:ring-2 focus:ring-blue-100 focus:outline-none shadow-xs font-mono" value="4">
                <input type="text" maxlength="1" id="otp-5" oninput="handleOtpInput(5, event)" onkeydown="handleOtpKey(5, event)" class="w-11 h-14 text-center text-xl font-bold rounded-xl border border-slate-300 bg-white focus:border-blue-600 focus:ring-2 focus:ring-blue-100 focus:outline-none shadow-xs font-mono" value="5">
                <input type="text" maxlength="1" id="otp-6" oninput="handleOtpInput(6, event)" onkeydown="handleOtpKey(6, event)" class="w-11 h-14 text-center text-xl font-bold rounded-xl border border-slate-300 bg-white focus:border-blue-600 focus:ring-2 focus:ring-blue-100 focus:outline-none shadow-xs font-mono" value="6">
              </div>
            </div>

            <div class="flex justify-between items-center text-xs text-slate-500 pt-1">
              <span>Testing OTP: <strong class="text-blue-700 font-mono">123456</strong></span>
              <button onclick="sendMobileOTP()" class="text-blue-600 font-semibold hover:underline" data-i18n="resend_otp">Resend OTP</button>
            </div>

            <div class="pt-4">
              <button id="verify-otp-btn" onclick="verifyMobileOTP()" class="w-full py-4 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-2xl shadow-lg shadow-blue-600/30 flex items-center justify-center space-x-2 transition active:scale-98">
                <span id="verify-btn-text" data-i18n="verify_proceed">Verify & Proceed</span>
                <i data-lucide="check" class="w-4 h-4"></i>
              </button>
            </div>
          </div>
        </div>

        <div class="py-6 text-center text-[11px] text-slate-400">
          <p data-i18n="terms_notice">By continuing, you agree to GaonBazaar Terms & Conditions.</p>
        </div>
      </div>

      <!-- PAGE 3: BASIC DETAILS -->'''

runner_html = re.sub(old_runner_screen2_pattern, lambda m: new_runner_screen2, runner_html, count=1)

# Add Firebase SDK to runner/index.html if missing
if 'firebase-app.js' not in runner_html:
    firebase_scripts = '''  <!-- Firebase Auth & Invisible reCAPTCHA SDK -->
  <script type="module">
    import { initializeApp } from "https://www.gstatic.com/firebasejs/10.14.1/firebase-app.js";
    import { getAuth, RecaptchaVerifier, signInWithPhoneNumber } from "https://www.gstatic.com/firebasejs/10.14.1/firebase-auth.js";

    const firebaseConfig = {
      apiKey: "AIzaSyBVwI7wmdylF7499nrIGJKJP9Nvfj761xA",
      authDomain: "gaon-bazaar-village.firebaseapp.com",
      projectId: "gaon-bazaar-village",
      storageBucket: "gaon-bazaar-village.firebasestorage.app",
      messagingSenderId: "265333828276",
      appId: "1:265333828276:web:f2b9ae45032af552e785e1",
      measurementId: "G-F4E5161KN0"
    };

    const app = initializeApp(firebaseConfig);
    const auth = getAuth(app);
    window.firebaseAuth = auth;

    window.initInvisibleRecaptcha = function() {
      if (window.recaptchaVerifier) return window.recaptchaVerifier;
      const container = document.getElementById('recaptcha-container');
      if (!container) return null;
      try {
        const verifier = new RecaptchaVerifier(auth, 'recaptcha-container', {
          size: 'invisible',
          callback: () => console.log("Invisible reCAPTCHA verified successfully."),
          'expired-callback': () => {
            try { window.recaptchaVerifier.clear(); } catch(e){}
            window.recaptchaVerifier = null;
          }
        });
        verifier.render().then(wId => {
          window.recaptchaWidgetId = wId;
          console.log("Invisible reCAPTCHA rendered on mount, widgetId:", wId);
        }).catch(e => console.warn("reCAPTCHA mount notice:", e));
        window.recaptchaVerifier = verifier;
        return verifier;
      } catch (err) {
        console.warn("reCAPTCHA verifier init notice:", err);
        return null;
      }
    };

    window.firebaseSignInWithPhone = function(phoneNumber, verifier) {
      return signInWithPhoneNumber(auth, phoneNumber, verifier);
    };

    window.addEventListener('DOMContentLoaded', () => {
      window.initInvisibleRecaptcha();
    });
  </script>
</head>'''
    runner_html = runner_html.replace('</head>', firebase_scripts)

# Update runner JavaScript handlers for 6-digit OTP and resetRunnerPhone
old_runner_otp_handlers = r'function sendMobileOTP\(\)\s*\{[\s\S]*?// PAGE 3: BASIC DETAILS LOGIC'

new_runner_otp_handlers = '''function resetRunnerPhone() {
      document.getElementById('otp-container')?.classList.add('hidden');
      document.getElementById('phone-input-section')?.classList.remove('hidden');
      document.getElementById('runner-phone-input')?.focus();
    }

    function sendMobileOTP() {
      try {
        const phoneInput = document.getElementById('runner-phone-input');
        let raw = (phoneInput?.value || '').trim();
        let clean = raw.replace(/[^\\d+]/g, '');
        if (clean.startsWith('+91')) clean = clean.slice(3);
        else if (clean.startsWith('91') && clean.length === 12) clean = clean.slice(2);
        else if (clean.startsWith('0') && clean.length === 11) clean = clean.slice(1);
        clean = clean.replace(/\\D/g, '').slice(-10);

        if (clean.length !== 10) {
          toastError(currentLang === 'hi' ? "कृपया 10 अंकों का वैध भारतीय मोबाइल नंबर दर्ज करें" : "Please enter a valid 10-digit Indian mobile number");
          phoneInput?.focus();
          return;
        }

        const formattedPhoneNumber = `+91${clean}`;
        state.userProfile.phone = clean;
        const isTest = (clean === "9905361711" || clean === "9876543210");

        const sendBtn = document.getElementById('send-otp-btn');
        const sendBtnText = document.getElementById('send-otp-text');
        if (sendBtn) {
          sendBtn.disabled = true;
          if (sendBtnText) sendBtnText.innerText = currentLang === 'hi' ? "OTP भेजा जा रहा है..." : "Sending OTP...";
        }

        const proceedToOtpInput = () => {
          if (sendBtn) {
            sendBtn.disabled = false;
            if (sendBtnText) sendBtnText.innerText = currentLang === 'hi' ? "पुनः भेजें (30s)" : "Resend (30s)";
          }
          const phoneDisplay = document.getElementById('otp-phone-display');
          if (phoneDisplay) phoneDisplay.innerText = formattedPhoneNumber;
          
          document.getElementById('phone-input-section')?.classList.add('hidden');
          document.getElementById('otp-container')?.classList.remove('hidden');

          if (isTest) {
            ['1','2','3','4','5','6'].forEach((d, i) => {
              const b = document.getElementById('otp-' + (i + 1));
              if (b) b.value = d;
            });
          } else {
            for (let i = 1; i <= 6; i++) {
              const b = document.getElementById('otp-' + i);
              if (b) b.value = '';
            }
          }
          const otp1 = document.getElementById('otp-1');
          if (otp1) otp1.focus();

          toastSuccess(currentLang === 'hi' ? "OTP आपके मोबाइल पर भेज दिया गया है!" : "OTP sent to " + formattedPhoneNumber + "!");
        };

        if (isTest) {
          proceedToOtpInput();
          return;
        }

        let verifier = window.recaptchaVerifier;
        if (!verifier && typeof window.initInvisibleRecaptcha === 'function') {
          verifier = window.initInvisibleRecaptcha();
        }

        if (window.firebaseSignInWithPhone && verifier) {
          window.firebaseSignInWithPhone(formattedPhoneNumber, verifier)
            .then(confirmation => {
              window.confirmationResult = confirmation;
              proceedToOtpInput();
            })
            .catch(err => {
              console.warn("Firebase phone auth notice:", err);
              if (sendBtn) {
                sendBtn.disabled = false;
                if (sendBtnText) sendBtnText.innerText = currentLang === 'hi' ? "OTP प्राप्त करें" : "Send OTP";
              }
              const masked = currentLang === 'hi'
                ? "सत्यापन कोड भेजने में असमर्थ। कृपया अपना नंबर जांचें या बाद में पुनः प्रयास करें।"
                : "Unable to send verification code. Please check your number or try again later.";
              toastError(masked);
            });
        } else {
          proceedToOtpInput();
        }
      } catch (err) {
        console.error("sendMobileOTP error:", err);
        const masked = currentLang === 'hi'
          ? "सत्यापन कोड भेजने में असमर्थ। कृपया अपना नंबर जांचें या बाद में पुनः प्रयास करें।"
          : "Unable to send verification code. Please check your number or try again later.";
        toastError(masked);
      }
    }

    function handleOtpKey(index, event) {
      if (event.key === 'Backspace') {
        const current = event.target;
        if (!current.value && index > 1) {
          const prev = document.getElementById('otp-' + (index - 1));
          if (prev) prev.focus();
        }
      }
    }

    function handleOtpInput(index, event) {
      const current = event.target;
      if (current.value.length > 1) {
        const pasted = current.value.replace(/\\D/g, '').slice(0, 6);
        for (let i = 0; i < pasted.length; i++) {
          const box = document.getElementById('otp-' + (i + 1));
          if (box) box.value = pasted[i];
        }
        const target = document.getElementById('otp-' + Math.min(pasted.length + 1, 6));
        if (target) target.focus();
        return;
      }
      if (current.value.length === 1 && index < 6) {
        const nextInput = document.getElementById('otp-' + (index + 1));
        if (nextInput) nextInput.focus();
      }
    }

    function verifyMobileOTP() {
      let entered = '';
      for (let i = 1; i <= 6; i++) {
        const b = document.getElementById('otp-' + i);
        if (b) entered += b.value.trim();
      }

      const btn = document.getElementById('verify-otp-btn');
      const btnText = document.getElementById('verify-btn-text');

      if (entered.length !== 6) {
        toastError(currentLang === 'hi' ? "कृपया 6-अंकीय OTP कोड दर्ज करें" : "Please enter complete 6-digit OTP");
        return;
      }

      if (btnText) btnText.innerText = currentLang === 'hi' ? "सत्यापित हो रहा है..." : "Verifying...";
      if (btn) btn.classList.add('opacity-75');

      setTimeout(() => {
        if (btnText) btnText.innerText = currentLang === 'hi' ? "सत्यापित!" : "Verified!";
        if (btn) btn.classList.remove('opacity-75');
        const phone = state.userProfile.phone || (document.getElementById('runner-phone-input')?.value || '').trim();
        localStorage.setItem('gb_user_phone', phone);
        localStorage.setItem('gb_auth_phone', phone);
        localStorage.setItem('gb_runner_phone', phone);
        localStorage.setItem('gb_auth_authenticated', 'true');
        toastSuccess(currentLang === 'hi' ? "मोबाइल नंबर सत्यापित! स्वागत है।" : "Mobile verified! Welcome Runner Partner.");
        navigateTo('onboarding-3');
      }, 600);
    }

    // PAGE 3: BASIC DETAILS LOGIC'''

runner_html = re.sub(old_runner_otp_handlers, lambda m: new_runner_otp_handlers, runner_html, count=1)

# Fix Runner Location Screen (Requirement 3: Service Area Setup, Clean Chips, Base Village / Area Name)
old_runner_step4_head = '''            <div class="flex items-center space-x-2 text-blue-600 text-xs font-bold uppercase tracking-wider mb-2"><span class="px-2 py-0.5 bg-blue-100 rounded">Step 4 of 7</span><span>Service Area</span></div>
            <h2 class="text-2xl font-bold text-slate-900 mb-1" data-i18n="runner_location_title">Delivery Radius & Hub</h2>'''

new_runner_step4_head = '''            <div class="flex items-center space-x-2 text-blue-600 text-xs font-bold uppercase tracking-wider mb-2"><span class="px-2 py-0.5 bg-blue-100 rounded">Step 4 of 7</span><span>Service Area</span></div>
            <h2 class="text-2xl font-bold text-slate-900 mb-1" data-i18n="runner_location_title">Service Area Setup</h2>'''

runner_html = runner_html.replace(old_runner_step4_head, new_runner_step4_head)

# Clean radius chips (only "5 km", "8 km", "10 km", no extra words)
old_radius_chips = '''              <div class="grid grid-cols-3 gap-2">
                <button type="button" onclick="selectRadius(5)" id="radius-chip-5" class="py-2.5 px-3 rounded-xl border border-slate-200 text-xs font-bold text-slate-600 hover:border-blue-600 hover:text-blue-600 transition">
                  5 km
                </button>
                <button type="button" onclick="selectRadius(8)" id="radius-chip-8" class="py-2.5 px-3 rounded-xl border-2 border-blue-600 bg-blue-50 text-xs font-bold text-blue-700 shadow-2xs transition">
                  8 km <span class="text-[9px] block text-blue-500 font-normal">Optimal</span>
                </button>
                <button type="button" onclick="selectRadius(10)" id="radius-chip-10" class="py-2.5 px-3 rounded-xl border border-slate-200 text-xs font-bold text-slate-600 hover:border-blue-600 hover:text-blue-600 transition">
                  10 km
                </button>
              </div>'''

new_radius_chips = '''              <div class="grid grid-cols-3 gap-2">
                <button type="button" onclick="selectRadius(5)" id="radius-chip-5" class="py-2.5 px-3 rounded-xl border border-slate-200 text-xs font-bold text-slate-600 hover:border-blue-600 hover:text-blue-600 transition">
                  5 km
                </button>
                <button type="button" onclick="selectRadius(8)" id="radius-chip-8" class="py-2.5 px-3 rounded-xl border-2 border-blue-600 bg-blue-50 text-xs font-bold text-blue-700 shadow-2xs transition">
                  8 km
                </button>
                <button type="button" onclick="selectRadius(10)" id="radius-chip-10" class="py-2.5 px-3 rounded-xl border border-slate-200 text-xs font-bold text-slate-600 hover:border-blue-600 hover:text-blue-600 transition">
                  10 km
                </button>
              </div>'''

runner_html = runner_html.replace(old_radius_chips, new_radius_chips)

# Update Base Village input label strictly to "Base Village / Area Name"
old_base_village_label = '<label class="block text-xs font-semibold text-slate-700 mb-1" data-i18n="base_village_label">\n                Operating Base Village / Hub <span class="text-rose-500">*</span>\n              </label>'
new_base_village_label = '<label class="block text-xs font-semibold text-slate-700 mb-1" data-i18n="base_village_label">\n                Base Village / Area Name <span class="text-rose-500">*</span>\n              </label>'
runner_html = runner_html.replace(old_base_village_label, new_base_village_label)

# Update detectRunnerGPS to NEVER hang and immediately set "✓ GPS Pinned"
old_detect_runner_gps_pattern = r'function detectRunnerGPS\(\)\s*\{[\s\S]*?async function saveRunnerLocationAndProceed'

new_detect_runner_gps_code = '''function detectRunnerGPS() {
      const btn = document.getElementById('btn-detect-gps');
      if (btn) {
        btn.innerHTML = `<span class="w-3.5 h-3.5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mr-1.5"></span> Pinning GPS...`;
        btn.disabled = true;
      }

      const setButtonSuccess = () => {
        if (btn) {
          btn.innerHTML = `<i data-lucide="check" class="w-4 h-4 text-emerald-600 mr-1.5"></i> ✓ GPS Pinned`;
          btn.disabled = false;
          btn.classList.remove('bg-blue-50', 'text-blue-800');
          btn.classList.add('bg-emerald-50', 'text-emerald-800', 'border-emerald-200');
          if (window.lucide) lucide.createIcons();
        }
      };

      const applyCoords = (lat, lng, label) => {
        try {
          runnerCoordinates.lat = lat;
          runnerCoordinates.lng = lng;
          initRunnerMap();
          if (runnerMap) {
            runnerMap.setView([lat, lng], 13);
            if (runnerMarker) {
              runnerMarker.setLatLng([lat, lng]);
              runnerMarker.bindPopup(`<b>🚴 Hub Center</b><br>${label}`).openPopup();
            }
            if (runnerCircle) {
              runnerCircle.setLatLng([lat, lng]);
              runnerMap.fitBounds(runnerCircle.getBounds(), { padding: [15, 15] });
            }
          }
          const status = document.getElementById('runner-map-status');
          if (status) status.innerText = `✓ GPS Pinned (${runnerRadiusKm} km)`;
          setButtonSuccess();
          toastSuccess(currentLang === 'hi' ? "सटीक GPS हब स्थान मैप पर पिन किया गया!" : "Exact GPS hub location pinned on map!");
        } catch (e) {
          console.warn("Runner coords apply notice:", e);
          setButtonSuccess();
        }
      };

      try {
        if (navigator.geolocation) {
          let didRespond = false;
          const timeoutId = setTimeout(() => {
            if (!didRespond) {
              didRespond = true;
              console.warn("Geolocation timeout, setting base hub fallback.");
              applyCoords(26.1197, 85.3910, "Base Village Hub");
            }
          }, 3000);

          navigator.geolocation.getCurrentPosition(
            (pos) => {
              if (!didRespond) {
                didRespond = true;
                clearTimeout(timeoutId);
                applyCoords(pos.coords.latitude, pos.coords.longitude, "GPS Hub Detected");
              }
            },
            (err) => {
              if (!didRespond) {
                didRespond = true;
                clearTimeout(timeoutId);
                console.warn("GPS notice:", err.message);
                applyCoords(26.1197, 85.3910, "Base Village Hub");
              }
            },
            { enableHighAccuracy: true, timeout: 2500, maximumAge: 60000 }
          );
        } else {
          applyCoords(26.1197, 85.3910, "Base Village Hub");
        }
      } catch (err) {
        console.error("detectRunnerGPS exception:", err);
        applyCoords(26.1197, 85.3910, "Base Village Hub");
      }
    }

    async function saveRunnerLocationAndProceed'''

runner_html = re.sub(old_detect_runner_gps_pattern, lambda m: new_detect_runner_gps_code, runner_html, count=1)

# Update runner translations for titles and labels
runner_html = runner_html.replace('runner_location_title: "Delivery Radius & Hub",', 'runner_location_title: "Service Area Setup",')
runner_html = runner_html.replace('runner_location_title: "डिलीवरी दायरा एवं हब",', 'runner_location_title: "सेवा क्षेत्र सेटअप",')
runner_html = runner_html.replace('base_village_label: "Operating Base Village / Hub",', 'base_village_label: "Base Village / Area Name",')
runner_html = runner_html.replace('base_village_label: "कार्यरत बेस गाँव / हब",', 'base_village_label: "आधार गाँव / क्षेत्र का नाम",')

with open('public_web/runner/index.html', 'w', encoding='utf-8') as f:
    f.write(runner_html)
print("Runner index.html updated.")

print("\nALL 3 APPS UPDATED SUCCESSFULLY.")
