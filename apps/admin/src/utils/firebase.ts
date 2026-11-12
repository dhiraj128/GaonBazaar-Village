import { initializeApp, getApps, getApp } from 'firebase/app';
import {
  getAuth,
  signInWithCustomToken,
  signInWithPhoneNumber,
  RecaptchaVerifier,
  type Auth,
  type UserCredential,
  type ConfirmationResult
} from 'firebase/auth';

export type { UserCredential, ConfirmationResult };

export const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY || "AIzaSyBVwI7wmdylF7499nrIGJKJP9Nvfj761xA",
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || "gaon-bazaar-village.firebaseapp.com",
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID || "gaon-bazaar-village",
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || "gaon-bazaar-village.firebasestorage.app",
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || "265333828276",
  appId: import.meta.env.VITE_FIREBASE_APP_ID || "1:265333828276:web:f2b9ae45032af552e785e1",
  measurementId: import.meta.env.VITE_FIREBASE_MEASUREMENT_ID || "G-F4E5161KN0"
};

export const app = getApps().length > 0 ? getApp() : initializeApp(firebaseConfig);
export const auth: Auth = getAuth(app);

/**
 * No-op stub for backwards compatibility
 */
export function resetRecaptchaVerifier(): void {
  // Recaptcha reset hook
  if (typeof window !== 'undefined' && (window as any).recaptchaVerifier) {
    try {
      (window as any).recaptchaVerifier.clear();
    } catch {}
    (window as any).recaptchaVerifier = null;
  }
}

/**
 * Initiates Firebase Phone Auth specifically for whitelisted test phone numbers
 * (e.g., +919905361711 or +919999999999) with static OTP 123456.
 * Configured in Firebase Console under "Phone numbers for testing".
 */
export async function sendFirebaseTestPhoneOtp(rawPhone: string): Promise<ConfirmationResult | null> {
  const clean10 = rawPhone.replace(/\D/g, '').slice(-10);
  const formattedPhone = `+91${clean10}`;
  console.log('[Firebase Test Flow] Initiating Phone Auth for whitelisted test number:', formattedPhone);

  if (typeof window === 'undefined') return null;

  try {
    let container = document.getElementById('recaptcha-test-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'recaptcha-test-container';
      container.style.position = 'fixed';
      container.style.bottom = '0';
      container.style.opacity = '0';
      container.style.pointerEvents = 'none';
      container.style.zIndex = '-1';
      document.body.appendChild(container);
    }

    const appVerifier = new RecaptchaVerifier(auth, 'recaptcha-test-container', {
      size: 'invisible',
      callback: () => {
        console.log('[Firebase Test Recaptcha] Verified automatically for test number');
      }
    });

    const confirmationResult = await signInWithPhoneNumber(auth, formattedPhone, appVerifier);
    console.log('[Firebase Test Flow] confirmationResult obtained successfully for:', formattedPhone);
    return confirmationResult;
  } catch (err: any) {
    console.warn('[Firebase Test Flow Notice]: Could not create native confirmationResult, proceeding with compliance bypass:', err);
    return null;
  }
}

/**
 * Sends a 6-digit OTP via Fast2SMS API through Vercel Serverless Function (/api/send-otp).
 * Whitelisted test numbers (9905361711, 9999999999) bypass external SMS APIs.
 */
export async function sendFast2SmsOtp(rawPhone: string): Promise<{ success: boolean; message?: string }> {
  const clean10 = rawPhone.replace(/\D/g, '').slice(-10);
  if (!/^[6-9]\d{9}$/.test(clean10) && clean10 !== '9999999999') {
    throw {
      code: 'auth/invalid-phone-number',
      message: 'Please enter a valid 10-digit Indian mobile number'
    };
  }

  // Whitelisted Compliance Test Numbers: DO NOT trigger external SMS APIs
  if (clean10 === '9905361711' || clean10 === '9999999999') {
    console.log('[Fast2SMS Client] Test number bypassed from external SMS:', clean10);
    return {
      success: true,
      message: 'Razorpay Compliance Review: Static code 123456 active'
    };
  }

  console.log('[Fast2SMS Client] Requesting OTP dispatch for:', clean10);

  let response: Response;
  try {
    response = await fetch('/api/send-otp', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({ phoneNumber: clean10 })
    });
  } catch (netErr: any) {
    console.error('[Fast2SMS Client Network Exception]:', netErr);
    throw {
      code: 'auth/network-error',
      message: 'Network connection error. Please verify your internet connection.'
    };
  }

  const rawText = await response.text();
  let data: any = {};
  try {
    data = JSON.parse(rawText);
  } catch (parseErr) {
    console.error('[Fast2SMS Client Non-JSON Server Response]:', response.status, rawText);
    throw {
      code: 'auth/server-error',
      message: `Server returned HTTP ${response.status}: ${rawText.slice(0, 100) || 'Service temporarily unavailable'}`
    };
  }

  if (!response.ok || !data.success) {
    throw {
      code: data.code || 'auth/sms-failed',
      message: data.message || data.error || 'Unable to send OTP via SMS gateway. Please try again.'
    };
  }

  return data;
}

/**
 * Verifies the 6-digit OTP code with /api/verify-otp, receives a Firebase Custom Token,
 * and signs in with Firebase via signInWithCustomToken.
 */
export async function verifyFast2SmsOtp(rawPhone: string, otp: string): Promise<UserCredential> {
  const clean10 = rawPhone.replace(/\D/g, '').slice(-10);
  const cleanOtp = String(otp || '').trim();

  if (!cleanOtp || cleanOtp.length < 4) {
    throw {
      code: 'auth/invalid-verification-code',
      message: 'Please enter the complete verification code'
    };
  }

  console.log('[Fast2SMS Client] Verifying OTP and requesting Custom Token for:', clean10);

  let response: Response;
  try {
    response = await fetch('/api/verify-otp', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({ phoneNumber: clean10, otp: cleanOtp })
    });
  } catch (netErr: any) {
    console.error('[Fast2SMS Verify Network Exception]:', netErr);
    throw {
      code: 'auth/network-error',
      message: 'Network connection error. Please verify your internet connection.'
    };
  }

  const rawText = await response.text();
  let data: any = {};
  try {
    data = JSON.parse(rawText);
  } catch (parseErr) {
    console.error('[Fast2SMS Verify Non-JSON Server Response]:', response.status, rawText);
    throw {
      code: 'auth/server-error',
      message: `Server returned HTTP ${response.status}: ${rawText.slice(0, 100) || 'Service temporarily unavailable'}`
    };
  }

  if (!response.ok || !data.success || !data.customToken) {
    throw {
      code: data.code || 'auth/invalid-verification-code',
      message: data.message || data.error || 'Invalid or expired OTP code'
    };
  }

  console.log('[Firebase Auth] Signing in seamlessly with Custom Token...');
  const userCredential = await signInWithCustomToken(auth, data.customToken);
  console.log('[Firebase Auth] User authenticated successfully:', userCredential.user.uid);
  return userCredential;
}
