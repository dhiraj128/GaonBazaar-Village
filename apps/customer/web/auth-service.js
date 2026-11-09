/**
 * GaonBazaar Customer Authentication & Database Sync Service
 * 
 * Architecture:
 * - Frontend OTP Delivery: Firebase Authentication (SMS via signInWithPhoneNumber & RecaptchaVerifier)
 * - Primary Relational Database: Supabase (public.users table sync)
 */

import { initializeApp } from "https://www.gstatic.com/firebasejs/10.14.1/firebase-app.js";
import { 
  getAuth, 
  RecaptchaVerifier, 
  signInWithPhoneNumber 
} from "https://www.gstatic.com/firebasejs/10.14.1/firebase-auth.js";
import { createClient } from "https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/+esm";

// 1. Firebase Configuration (Technical Directive Requirement)
export const firebaseConfig = (window.APP_CONFIG && window.APP_CONFIG.FIREBASE_CONFIG) || {
  apiKey: "AIzaSyBVwI7wmdylF7499nrIGJKJP9Nvfj761xA",
  authDomain: "gaon-bazaar-village.firebaseapp.com",
  projectId: "gaon-bazaar-village",
  storageBucket: "gaon-bazaar-village.firebasestorage.app",
  messagingSenderId: "265333828276",
  appId: "1:265333828276:web:f2b9ae45032af552e785e1",
  measurementId: "G-F4E5161KN0"
};

// Initialize Firebase App & Auth
export const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);

// 2. Supabase Configuration & Client Initialization
export const SUPABASE_URL = (window.APP_CONFIG && window.APP_CONFIG.SUPABASE_URL) || "https://vxewgvrjhjpntfvsmuez.supabase.co";
export const SUPABASE_ANON_KEY = (window.APP_CONFIG && window.APP_CONFIG.SUPABASE_ANON_KEY) || "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ4ZXdndnJqaGpwbnRmdnNtdWV6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTM1NDkwMzcsImV4cCI6MjEwOTEyNTAzN30.3jUR0U9RGcgc2q-zeWX7OeWaFqugSHOFdDieYoGFIwQ";

export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// State variables
let confirmationResult = null;
let recaptchaVerifier = null;
let resendTimerInterval = null;
let resendCountdownSeconds = 30;

/**
 * Initialize invisible reCAPTCHA verifier for Firebase SMS abuse prevention
 */
export function getOrCreateRecaptchaVerifier() {
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
        console.log("Firebase reCAPTCHA verified successfully.");
      },
      'expired-callback': () => {
        console.warn("Firebase reCAPTCHA expired, resetting...");
        resetRecaptcha();
      }
    });

    window.recaptchaVerifier = recaptchaVerifier;
    return recaptchaVerifier;
  } catch (err) {
    console.error("Failed to instantiate RecaptchaVerifier:", err);
    return null;
  }
}

export function resetRecaptcha() {
  if (window.recaptchaVerifier) {
    try {
      window.recaptchaVerifier.clear();
    } catch (e) {}
    window.recaptchaVerifier = null;
    recaptchaVerifier = null;
  }
}

/**
 * Step 1: Send SMS OTP via Firebase Auth
 */
export async function sendCustomerOTP() {
  hideAuthError();
  const phoneInput = document.getElementById('cust-phone-input');
  const nameInput = document.getElementById('cust-name-input');
  const phone = (phoneInput?.value || '').trim();
  const name = (nameInput?.value || '').trim();

  // Validate 10-digit Indian Mobile format (must start with 6-9)
  const cleanPhone = phone.replace(/\D/g, '');
  if (!/^[6-9]\d{9}$/.test(cleanPhone)) {
    showAuthError(
      window.currentLang === 'hi'
        ? "कृपया 10 अंकों का वैध भारतीय मोबाइल नंबर दर्ज करें (6-9 से शुरू)"
        : "Please enter a valid 10-digit Indian mobile number (starts with 6-9)"
    );
    phoneInput?.focus();
    return;
  }

  // Formatted E.164 phone string
  const formattedPhoneNumber = `+91${cleanPhone}`;

  const btn = document.getElementById('send-otp-btn');
  if (btn) {
    btn.innerHTML = `<span class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></span> ${window.currentLang === 'hi' ? 'OTP भेजा जा रहा है...' : 'Sending OTP...'}`;
    btn.disabled = true;
  }

  try {
    const verifier = getOrCreateRecaptchaVerifier();
    console.log(`Dispatching Firebase SMS OTP to: ${formattedPhoneNumber}`);
    
    // Call live Firebase Auth SMS dispatch
    confirmationResult = await signInWithPhoneNumber(auth, formattedPhoneNumber, verifier);
    window.confirmationResult = confirmationResult;

    // Transition UI to Step 2 (OTP Entry)
    const phoneDisplay = document.getElementById('otp-phone-display');
    if (phoneDisplay) phoneDisplay.innerText = `+91 ${cleanPhone}`;

    document.getElementById('phone-input-section')?.classList.add('hidden');
    document.getElementById('otp-input-section')?.classList.remove('hidden');

    // Reset OTP input fields
    for (let i = 1; i <= 6; i++) {
      const box = document.getElementById(`otp-${i}`);
      if (box) box.value = '';
    }
    document.getElementById('otp-1')?.focus();

    startResendTimer();

    if (window.toastSuccess) {
      window.toastSuccess(
        window.currentLang === 'hi'
          ? "OTP आपके मोबाइल पर भेज दिया गया है!"
          : "OTP sent to your mobile phone via SMS!"
      );
    }
  } catch (error) {
    console.error("sendCustomerOTP error:", error);
    resetRecaptcha();
    handleAuthError(error);
  } finally {
    if (btn) {
      btn.innerHTML = `<span>${window.currentLang === 'hi' ? 'OTP प्राप्त करें' : 'Send OTP'}</span> <i data-lucide="send" class="w-4 h-4 ml-1"></i>`;
      btn.disabled = false;
      if (window.lucide) window.lucide.createIcons();
    }
  }
}

/**
 * Step 2: Verify OTP with Firebase and Synchronize with Supabase
 */
export async function verifyCustomerOTP() {
  hideAuthError();

  // Gather 6-digit OTP code
  let code = '';
  for (let i = 1; i <= 6; i++) {
    const box = document.getElementById(`otp-${i}`);
    if (box) code += box.value.trim();
  }

  if (code.length !== 6) {
    showAuthError(
      window.currentLang === 'hi'
        ? "कृपया पूरा 6-अंकीय OTP कोड दर्ज करें"
        : "Please enter the complete 6-digit OTP code"
    );
    return;
  }

  const verifyBtn = document.getElementById('verify-otp-btn');
  if (verifyBtn) {
    verifyBtn.innerHTML = `<span class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></span> ${window.currentLang === 'hi' ? 'सत्यापित हो रहा है...' : 'Verifying...'}`;
    verifyBtn.disabled = true;
  }

  const phoneInput = document.getElementById('cust-phone-input');
  const nameInput = document.getElementById('cust-name-input');
  const rawPhone = (phoneInput?.value || '').trim().replace(/\D/g, '');
  const enteredName = (nameInput?.value || '').trim() || 'Customer';

  try {
    let authUser = null;

    if (window.confirmationResult) {
      // Live Firebase OTP confirmation
      const userCredential = await window.confirmationResult.confirm(code);
      authUser = userCredential.user;
      console.log("Firebase Auth confirmed:", authUser.uid, authUser.phoneNumber);
    } else {
      throw { code: 'auth/session-expired', message: 'No active OTP session. Please tap Send OTP again.' };
    }

    const uid = authUser.uid;
    const phoneNumber = authUser.phoneNumber || `+91${rawPhone}`;

    // Critical Step 4: Supabase Database Sync
    console.log(`Syncing user [${uid}] with Supabase database...`);
    const syncResult = await syncUserWithSupabase(uid, phoneNumber, enteredName);
    const dbUser = syncResult.user;

    // Establish persistent customer session in localStorage
    localStorage.setItem('gb_customer_authenticated', 'true');
    localStorage.setItem('gb_customer_uid', uid);
    localStorage.setItem('gb_customer_phone', rawPhone);
    localStorage.setItem('gb_customer_name', dbUser.name || enteredName);
    localStorage.setItem('gb_customer_profile', JSON.stringify({
      id: dbUser.id || uid,
      uid: uid,
      name: dbUser.name || enteredName,
      phone: `+91 ${rawPhone}`,
      role: dbUser.role || 'customer'
    }));

    // Transition UI to main dashboard
    document.getElementById('page-login')?.classList.add('hidden');
    document.getElementById('dashboard-container')?.classList.remove('hidden');
    
    if (typeof window.switchTab === 'function') {
      window.switchTab('home');
    }

    if (window.toastSuccess) {
      window.toastSuccess(
        window.currentLang === 'hi'
          ? `लॉगिन सफल! स्वागत है ${dbUser.name || enteredName}`
          : `Login verified! Welcome to GaonBazaar, ${dbUser.name || enteredName}`
      );
    }

    // Refresh profile and addresses
    if (typeof window.loadUserProfile === 'function') window.loadUserProfile();
    if (typeof window.loadUserSavedAddresses === 'function') window.loadUserSavedAddresses();
    if (typeof window.checkPaymentGatewayStatus === 'function') window.checkPaymentGatewayStatus();

  } catch (error) {
    console.error("verifyCustomerOTP error:", error);
    handleAuthError(error);
  } finally {
    if (verifyBtn) {
      verifyBtn.innerHTML = `<span>${window.currentLang === 'hi' ? 'सत्यापित करें और लॉगिन' : 'Verify & Login'}</span> <i data-lucide="arrow-right" class="w-4 h-4 ml-1"></i>`;
      verifyBtn.disabled = false;
      if (window.lucide) window.lucide.createIcons();
    }
  }
}

/**
 * Step 4: Supabase Database Sync (Critical Step)
 * - Checks if row with Firebase uid exists in public.users
 * - If exists, creates session and returns user record
 * - If does not exist, immediately performs an INSERT with uid, phoneNumber, and Name
 */
export async function syncUserWithSupabase(uid, phoneNumber, name) {
  const cleanPhone = phoneNumber.replace(/^\+91/, '').replace(/\D/g, '').trim();

  try {
    // 1. Query Supabase users table by Firebase uid or id
    const { data: existingByUid, error: uidQueryError } = await supabase
      .from('users')
      .select('*')
      .or(`firebase_uid.eq.${uid},id.eq.${uid}`);

    if (uidQueryError) {
      console.warn("Supabase query by UID error, checking fallback:", uidQueryError);
    }

    if (existingByUid && existingByUid.length > 0) {
      console.log("Supabase record found by UID:", existingByUid[0]);
      return { user: existingByUid[0], isNew: false };
    }

    // 2. Query by phone number to handle existing/migrated customer records
    const { data: existingByPhone, error: phoneQueryError } = await supabase
      .from('users')
      .select('*')
      .or(`phone.eq.${cleanPhone},phone.eq.+91${cleanPhone}`);

    if (existingByPhone && existingByPhone.length > 0) {
      const match = existingByPhone[0];
      console.log("Supabase record found by phone, linking firebase_uid:", match.id);
      
      const { data: updatedUser } = await supabase
        .from('users')
        .update({ 
          firebase_uid: uid,
          name: match.name || name || "Customer",
          updated_at: new Date().toISOString()
        })
        .eq('id', match.id)
        .select()
        .single();

      return { user: updatedUser || match, isNew: false };
    }

    // 3. Brand new customer: Immediately INSERT into Supabase users table
    const newUserRecord = {
      id: uid,
      firebase_uid: uid,
      phone: cleanPhone,
      name: name || "Customer",
      role: "customer",
      preferred_language: localStorage.getItem('gb_customer_lang') || "hi",
      is_active: true,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };

    console.log("Inserting new customer record into Supabase:", newUserRecord);
    const { data: insertedUser, error: insertError } = await supabase
      .from('users')
      .insert([newUserRecord])
      .select()
      .single();

    if (insertError) {
      console.error("Supabase user insert error:", insertError);
      // Fallback REST call if needed
      const restResp = await fetch(`${SUPABASE_URL}/rest/v1/users`, {
        method: 'POST',
        headers: {
          'apikey': SUPABASE_ANON_KEY,
          'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
          'Content-Type': 'application/json',
          'Prefer': 'return=representation'
        },
        body: JSON.stringify(newUserRecord)
      });
      if (restResp.ok) {
        const result = await restResp.json();
        return { user: result[0] || newUserRecord, isNew: true };
      }
      throw insertError;
    }

    console.log("Successfully created new customer in Supabase:", insertedUser);
    return { user: insertedUser, isNew: true };

  } catch (err) {
    console.error("syncUserWithSupabase error:", err);
    // If Supabase encounters a constraint or temporary network issue,
    // construct a valid local user record so mobile authentication does not freeze.
    return {
      user: {
        id: uid,
        firebase_uid: uid,
        phone: cleanPhone,
        name: name || "Customer",
        role: "customer"
      },
      isNew: true
    };
  }
}

/**
 * Handle Auth Errors & map Firebase error codes to friendly bilingual messages
 */
export function handleAuthError(error) {
  let message = "An error occurred during authentication. Please try again.";
  const code = error?.code || '';

  if (code === 'auth/invalid-verification-code') {
    message = window.currentLang === 'hi'
      ? "अमान्य OTP कोड! कृपया अपने फोन पर आया 6-अंकीय कोड दोबारा जांचें।"
      : "Invalid OTP code. Please enter the correct 6-digit code sent to your phone.";
  } else if (code === 'auth/code-expired') {
    message = window.currentLang === 'hi'
      ? "यह OTP कोड समाप्त हो चुका है। कृपया 'Resend OTP' दबाकर नया कोड मंगाएं।"
      : "This OTP code has expired. Please tap 'Resend OTP' to request a new code.";
  } else if (code === 'auth/too-many-requests') {
    message = window.currentLang === 'hi'
      ? "बहुत अधिक प्रयास! सुरक्षा कारणों से कुछ समय के लिए अनुरोध रोक दिया गया है। कृपया थोड़ी देर बाद प्रयास करें।"
      : "Too many attempts. Requests have been temporarily blocked for security. Please wait a few moments before trying again.";
  } else if (code === 'auth/network-request-failed') {
    message = window.currentLang === 'hi'
      ? "नेटवर्क त्रुटि! कृपया अपना इंटरनेट कनेक्शन जांचें और पुनः प्रयास करें।"
      : "Network error. Please check your internet connection and try again.";
  } else if (code === 'auth/invalid-phone-number') {
    message = window.currentLang === 'hi'
      ? "अमान्य फोन नंबर! कृपया 10 अंकों का वैध मोबाइल नंबर दर्ज करें।"
      : "Invalid phone number. Please enter a valid 10-digit Indian mobile number.";
  } else if (code === 'auth/captcha-check-failed') {
    message = window.currentLang === 'hi'
      ? "सुरक्षा जांच (reCAPTCHA) विफल रही। कृपया पुनः प्रयास करें।"
      : "Security reCAPTCHA verification failed. Please try again.";
  } else if (error?.message) {
    message = error.message;
  }

  showAuthError(message);
  if (window.toastError) {
    window.toastError(message);
  }
}

export function showAuthError(message) {
  const banner = document.getElementById('auth-error-banner');
  const text = document.getElementById('auth-error-text');
  if (banner && text) {
    text.innerText = message;
    banner.classList.remove('hidden');
  }
}

export function hideAuthError() {
  const banner = document.getElementById('auth-error-banner');
  if (banner) {
    banner.classList.add('hidden');
  }
}

/**
 * Reset phone view & clear OTP fields
 */
export function resetCustomerPhone() {
  hideAuthError();
  document.getElementById('otp-input-section')?.classList.add('hidden');
  document.getElementById('phone-input-section')?.classList.remove('hidden');
  document.getElementById('cust-phone-input')?.focus();
}

/**
 * Resend OTP with countdown timer
 */
export async function resendCustomerOTP() {
  if (resendCountdownSeconds > 0 && resendTimerInterval) {
    return;
  }
  await sendCustomerOTP();
}

export function startResendTimer() {
  const timerSpan = document.getElementById('resend-timer');
  const countdownSpan = document.getElementById('resend-countdown');
  const resendBtn = document.getElementById('resend-otp-btn');

  if (resendTimerInterval) {
    clearInterval(resendTimerInterval);
  }

  resendCountdownSeconds = 30;
  if (timerSpan) timerSpan.classList.remove('hidden');
  if (resendBtn) resendBtn.classList.add('hidden');
  if (countdownSpan) countdownSpan.innerText = resendCountdownSeconds;

  resendTimerInterval = setInterval(() => {
    resendCountdownSeconds--;
    if (countdownSpan) countdownSpan.innerText = resendCountdownSeconds;
    if (resendCountdownSeconds <= 0) {
      clearInterval(resendTimerInterval);
      resendTimerInterval = null;
      if (timerSpan) timerSpan.classList.add('hidden');
      if (resendBtn) resendBtn.classList.remove('hidden');
    }
  }, 1000);
}

/**
 * 6-Digit OTP Box auto-advance and backspace navigation
 */
export function handleOtpInput(current, nextId, event) {
  hideAuthError();

  // Support backspace to jump to previous input box
  if (event && event.key === 'Backspace' && !current.value) {
    const prev = current.previousElementSibling;
    if (prev && prev.tagName === 'INPUT') {
      prev.focus();
    }
    return;
  }

  // Paste handler: if user pastes full 6-digit code into first box
  if (current.value.length > 1) {
    const pasted = current.value.replace(/\D/g, '').slice(0, 6);
    for (let i = 0; i < pasted.length; i++) {
      const box = document.getElementById(`otp-${i + 1}`);
      if (box) box.value = pasted[i];
    }
    const target = document.getElementById(`otp-${Math.min(pasted.length + 1, 6)}`);
    if (target) target.focus();
    return;
  }

  if (current.value.length >= 1 && nextId) {
    const next = document.getElementById(nextId);
    if (next) next.focus();
  }
}

// Bind to window for HTML onclick and input event handlers
window.authService = {
  auth,
  app,
  supabase,
  sendCustomerOTP,
  verifyCustomerOTP,
  resendCustomerOTP,
  resetCustomerPhone,
  handleOtpInput,
  syncUserWithSupabase,
  handleAuthError,
  showAuthError,
  hideAuthError,
  resetRecaptcha
};
window.sendCustomerOTP = sendCustomerOTP;
window.verifyCustomerOTP = verifyCustomerOTP;
window.resendCustomerOTP = resendCustomerOTP;
window.resetCustomerPhone = resetCustomerPhone;
window.handleOtpInput = handleOtpInput;
window.hideAuthError = hideAuthError;
window.syncUserWithSupabase = syncUserWithSupabase;
window.resetRecaptcha = resetRecaptcha;

console.log("GaonBazaar Firebase Auth & Supabase Sync service initialized successfully.");
