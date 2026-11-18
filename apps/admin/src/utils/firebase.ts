import { initializeApp, getApps, getApp } from 'firebase/app';
import {
  getAuth,
  signInWithCustomToken,
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

export function resetRecaptchaVerifier(): void {
  // Legacy no-op stub: reCAPTCHA is permanently removed in favor of Message Central VerifyNow
}

/**
 * Sends a real 4-digit SMS OTP via Message Central VerifyNow (/api/send-otp).
 * Zero hardcoded phone numbers or static OTP bypasses.
 */
export async function sendMessageCentralOtp(
  rawPhone: string,
  role: string = 'customer'
): Promise<{ success: boolean; verificationId: string; message?: string }> {
  const clean10 = rawPhone.replace(/\D/g, '').slice(-10);
  if (!/^[6-9]\d{9}$/.test(clean10)) {
    throw {
      code: 'auth/invalid-phone-number',
      message: 'Please enter a valid 10-digit Indian mobile number'
    };
  }

  console.log('[Message Central Client] Requesting 4-digit OTP dispatch for:', clean10);

  let response: Response;
  try {
    response = await fetch('/api/send-otp', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({ phoneNumber: clean10, role })
    });
  } catch (netErr: any) {
    console.error('[Message Central Client Network Exception]:', netErr);
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
    console.error('[Message Central Client Non-JSON Server Response]:', response.status, rawText);
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
 * Verifies the 4-digit OTP code with Message Central VerifyNow (/api/verify-otp),
 * receives a Firebase Custom Token, and signs in with Firebase via signInWithCustomToken.
 */
export async function verifyMessageCentralOtp(
  rawPhone: string,
  otp: string,
  verificationId?: string,
  role: string = 'customer'
): Promise<UserCredential> {
  const clean10 = rawPhone.replace(/\D/g, '').slice(-10);
  const cleanOtp = String(otp || '').trim();

  if (!cleanOtp || cleanOtp.length !== 4) {
    throw {
      code: 'auth/invalid-verification-code',
      message: 'Please enter the complete 4-digit verification code'
    };
  }

  console.log('[Message Central Client] Verifying OTP and requesting Custom Token for:', clean10);

  let response: Response;
  try {
    response = await fetch('/api/verify-otp', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({
        phoneNumber: clean10,
        otp: cleanOtp,
        verificationId: verificationId || undefined,
        role
      })
    });
  } catch (netErr: any) {
    console.error('[Message Central Verify Network Exception]:', netErr);
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
    console.error('[Message Central Verify Non-JSON Server Response]:', response.status, rawText);
    throw {
      code: 'auth/server-error',
      message: `Server returned HTTP ${response.status}: ${rawText.slice(0, 100) || 'Service temporarily unavailable'}`
    };
  }

  if (!response.ok || !data.success || !data.customToken) {
    throw {
      code: data.code || 'auth/invalid-verification-code',
      message: data.message || data.error || 'Invalid or expired OTP code. Please check your SMS.'
    };
  }

  console.log('[Firebase Auth] Message Central verified! Signing in with Custom Token...');
  const userCredential = await signInWithCustomToken(auth, data.customToken);
  console.log('[Firebase Auth] User authenticated successfully:', userCredential.user.uid);
  return userCredential;
}

// Backwards-compatible aliases
export const sendFast2SmsOtp = sendMessageCentralOtp;
export const verifyFast2SmsOtp = (rawPhone: string, otp: string) => verifyMessageCentralOtp(rawPhone, otp);
export const sendFirebaseTestPhoneOtp = async (rawPhone: string) => {
  // Disallow old test bypass; route directly into genuine provider
  return null;
};
