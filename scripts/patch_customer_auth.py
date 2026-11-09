import re

with open('public_web/customer/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add <script type="module" src="auth-service.js"></script> to <head>
if 'src="auth-service.js"' not in html:
    html = html.replace(
        '<script src="config.js"></script>',
        '<script src="config.js"></script>\n  <!-- Firebase SMS OTP & Supabase Database Sync Module -->\n  <script type="module" src="auth-service.js"></script>'
    )
    print("1. Added auth-service.js script tag to <head>")
else:
    print("1. auth-service.js already in <head>")

# 2. Overwrite #page-login markup
old_login_pat = re.compile(
    r'<section id="page-login"[^>]*>.*?</section>',
    re.DOTALL
)

new_login_markup = '''<section id="page-login" class="hidden flex-1 flex flex-col p-6 justify-between bg-white overflow-y-auto">
      <div class="pt-4 space-y-5">
        <button onclick="historyBack()" class="w-9 h-9 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-600 flex items-center justify-center transition active:scale-95" aria-label="Back">
          <i data-lucide="arrow-left" class="w-4 h-4"></i>
        </button>

        <div class="space-y-1.5">
          <div class="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-800 text-[10px] font-bold border border-emerald-200">
            <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
            <span>Firebase SMS + Supabase Sync</span>
          </div>
          <h2 class="text-2xl font-extrabold text-slate-900" data-i18n="login_title">Mobile Login & Verification</h2>
          <p class="text-xs text-slate-600 leading-relaxed" data-i18n="login_sub">
            Enter your mobile number to receive a secure 6-digit SMS verification code on your phone.
          </p>
        </div>

        <!-- Auth Error / Notification Banner -->
        <div id="auth-error-banner" class="hidden p-3 rounded-2xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-start space-x-2.5 shadow-2xs">
          <i data-lucide="alert-circle" class="w-4 h-4 text-rose-600 shrink-0 mt-0.5"></i>
          <span id="auth-error-text" class="flex-1 font-medium leading-relaxed"></span>
          <button onclick="hideAuthError()" class="text-rose-400 hover:text-rose-700 font-bold text-sm leading-none ml-1">✕</button>
        </div>

        <!-- Step 1: Phone and Name Input Block -->
        <div id="phone-input-section" class="space-y-4 pt-1">
          <div>
            <label class="block text-[11px] font-semibold text-slate-700 mb-1" data-i18n="name_label">
              Full Name <span class="text-slate-400 font-normal">(for new customers)</span>
            </label>
            <div class="relative flex items-center">
              <i data-lucide="user" class="absolute left-3.5 w-4 h-4 text-slate-400"></i>
              <input type="text" id="cust-name-input" placeholder="e.g. Ramesh Kumar" class="w-full pl-10 pr-4 py-3.5 bg-slate-50 border border-slate-300 focus:border-emerald-600 focus:bg-white focus:outline-none rounded-2xl text-xs font-semibold text-slate-900 transition shadow-2xs">
            </div>
          </div>

          <div>
            <label class="block text-[11px] font-semibold text-slate-700 mb-1" data-i18n="phone_label">
              Mobile Number
            </label>
            <div class="relative flex items-center">
              <span class="absolute left-3.5 text-xs font-bold text-slate-500 border-r border-slate-300 pr-2.5">+91</span>
              <input type="tel" id="cust-phone-input" maxlength="10" placeholder="9876543210" class="w-full pl-16 pr-4 py-3.5 bg-slate-50 border border-slate-300 focus:border-emerald-600 focus:bg-white focus:outline-none rounded-2xl text-sm font-semibold tracking-wide text-slate-900 transition shadow-2xs">
            </div>
            <p class="text-[10px] text-slate-400 mt-1">Live SMS OTP dispatched via Firebase Authenticator</p>
          </div>

          <!-- Invisible reCAPTCHA container for Firebase Auth abuse prevention -->
          <div id="recaptcha-container"></div>

          <button onclick="sendCustomerOTP()" id="send-otp-btn" class="w-full py-4 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-2xl shadow-lg shadow-emerald-600/30 flex items-center justify-center space-x-2 transition active:scale-98">
            <span data-i18n="send_otp_btn">Send OTP</span>
            <i data-lucide="send" class="w-4 h-4"></i>
          </button>
        </div>

        <!-- Step 2: 6-Digit OTP Boxes Block -->
        <div id="otp-input-section" class="hidden space-y-5 pt-1">
          <div class="p-3 bg-emerald-50 rounded-2xl border border-emerald-200 flex items-center justify-between">
            <div class="text-xs text-emerald-900">
              <span class="font-medium" data-i18n="otp_sent_to">Code sent to:</span> <span id="otp-phone-display" class="font-bold">+91 9876543210</span>
            </div>
            <button onclick="resetCustomerPhone()" class="text-xs text-emerald-700 font-bold hover:underline" data-i18n="change_number">Change</button>
          </div>

          <div class="space-y-2">
            <label class="block text-center text-[11px] font-semibold text-slate-600">Enter 6-Digit SMS Verification Code</label>
            <div class="flex justify-between space-x-1.5 max-w-[320px] mx-auto">
              <input type="tel" maxlength="1" id="otp-1" onkeyup="handleOtpInput(this, 'otp-2', event)" class="w-11 h-14 text-center text-xl font-bold bg-slate-50 border border-slate-300 focus:border-emerald-600 focus:bg-white focus:outline-none rounded-xl shadow-2xs transition">
              <input type="tel" maxlength="1" id="otp-2" onkeyup="handleOtpInput(this, 'otp-3', event)" class="w-11 h-14 text-center text-xl font-bold bg-slate-50 border border-slate-300 focus:border-emerald-600 focus:bg-white focus:outline-none rounded-xl shadow-2xs transition">
              <input type="tel" maxlength="1" id="otp-3" onkeyup="handleOtpInput(this, 'otp-4', event)" class="w-11 h-14 text-center text-xl font-bold bg-slate-50 border border-slate-300 focus:border-emerald-600 focus:bg-white focus:outline-none rounded-xl shadow-2xs transition">
              <input type="tel" maxlength="1" id="otp-4" onkeyup="handleOtpInput(this, 'otp-5', event)" class="w-11 h-14 text-center text-xl font-bold bg-slate-50 border border-slate-300 focus:border-emerald-600 focus:bg-white focus:outline-none rounded-xl shadow-2xs transition">
              <input type="tel" maxlength="1" id="otp-5" onkeyup="handleOtpInput(this, 'otp-6', event)" class="w-11 h-14 text-center text-xl font-bold bg-slate-50 border border-slate-300 focus:border-emerald-600 focus:bg-white focus:outline-none rounded-xl shadow-2xs transition">
              <input type="tel" maxlength="1" id="otp-6" onkeyup="handleOtpInput(this, null, event)" class="w-11 h-14 text-center text-xl font-bold bg-slate-50 border border-slate-300 focus:border-emerald-600 focus:bg-white focus:outline-none rounded-xl shadow-2xs transition">
            </div>
          </div>

          <div class="flex justify-between items-center text-xs pt-1 px-1">
            <span class="text-slate-500" data-i18n="didnt_receive">Didn't receive code?</span>
            <div>
              <button onclick="resendCustomerOTP()" id="resend-otp-btn" class="font-bold text-emerald-700 hover:underline" data-i18n="resend_otp">Resend OTP</button>
              <span id="resend-timer" class="text-slate-400 text-xs hidden">Resend in <span id="resend-countdown" class="font-bold text-slate-600">30</span>s</span>
            </div>
          </div>

          <button onclick="verifyCustomerOTP()" id="verify-otp-btn" class="w-full py-4 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-2xl shadow-lg shadow-emerald-600/30 flex items-center justify-center space-x-2 transition active:scale-98">
            <span data-i18n="verify_login_btn">Verify & Login</span>
            <i data-lucide="arrow-right" class="w-4 h-4"></i>
          </button>
        </div>
      </div>

      <div class="py-6 text-center text-[11px] text-slate-400">
        <p data-i18n="terms_notice">By continuing, you agree to GaonBazaar Rural Delivery Terms & Privacy Policy.</p>
      </div>
    </section>'''

if old_login_pat.search(html):
    html = old_login_pat.sub(new_login_markup, html, count=1)
    print("2. Overwrote #page-login markup with 6-digit OTP & Name input fields")
else:
    print("2. Warning: old_login_pat not matched")

# 3. Overwrite legacy inline OTP functions
old_otp_fn_pat = re.compile(
    r'// PHASE 11: LOGIN & REAL OTP VERIFICATION.*?async function sendCustomerOTP\(\) \{.*?function handleOtpInput\(.*?function resetCustomerPhone\(.*?function resendCustomerOTP\(.*?async function verifyCustomerOTP\(\) \{.*?loadUserSavedAddresses\(\);\s*\}',
    re.DOTALL
)

new_otp_fns = '''// PHASE 11: FIREBASE SMS OTP AUTHENTICATION & SUPABASE DATABASE SYNC
    // ---------------------------------------------------------------------------
    async function sendCustomerOTP() {
      if (window.authService && typeof window.authService.sendCustomerOTP === 'function') {
        return await window.authService.sendCustomerOTP();
      }
    }

    async function verifyCustomerOTP() {
      if (window.authService && typeof window.authService.verifyCustomerOTP === 'function') {
        return await window.authService.verifyCustomerOTP();
      }
    }

    function resendCustomerOTP() {
      if (window.authService && typeof window.authService.resendCustomerOTP === 'function') {
        return window.authService.resendCustomerOTP();
      }
    }

    function resetCustomerPhone() {
      if (window.authService && typeof window.authService.resetCustomerPhone === 'function') {
        return window.authService.resetCustomerPhone();
      }
    }

    function handleOtpInput(current, nextId, event) {
      if (window.authService && typeof window.authService.handleOtpInput === 'function') {
        return window.authService.handleOtpInput(current, nextId, event);
      }
    }

    function hideAuthError() {
      if (window.authService && typeof window.authService.hideAuthError === 'function') {
        window.authService.hideAuthError();
      }
    }'''

if old_otp_fn_pat.search(html):
    html = old_otp_fn_pat.sub(new_otp_fns, html, count=1)
    print("3. Replaced legacy inline OTP functions with authService delegation")
else:
    print("3. Warning: old_otp_fn_pat not matched directly")

with open('public_web/customer/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Saved public_web/customer/index.html successfully.")
