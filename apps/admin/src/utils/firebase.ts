import { initializeApp, getApps, getApp } from 'firebase/app';
import {
  getAuth,
  signInWithCustomToken,
  type Auth,
  type UserCredential
} from 'firebase/auth';

export type { UserCredential };

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
  // Recaptcha removed in favor of Fast2SMS API custom OTP flow
}

/**
 * Sends a 6-digit OTP via Fast2SMS API through Vercel Serverless Function (/api/send-otp).
 */
export async function sendFast2SmsOtp(rawPhone: string): Promise<{ success: boolean; message?: string }> {
  const clean10 = rawPhone.replace(/\D/g, '').slice(-10);
  if (!/^[6-9]\d{9}$/.test(clean10) && clean10 !== '9999999999') {
    throw {
      code: 'auth/invalid-phone-number',
      message: 'Please enter a valid 10-digit Indian mobile number'
    };
  }

  console.log('[Fast2SMS Client] Requesting OTP dispatch for:', clean10);

  const response = await fetch('/api/send-otp', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ phoneNumber: clean10 })
  });

  const data = await response.json();
  if (!response.ok || !data.success) {
    throw {
      code: data.code || 'auth/sms-failed',
      message: data.message || 'Unable to send OTP via SMS gateway. Please try again.'
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

  const response = await fetch('/api/verify-otp', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ phoneNumber: clean10, otp: cleanOtp })
  });

  const data = await response.json();
  if (!response.ok || !data.success || !data.customToken) {
    throw {
      code: data.code || 'auth/invalid-verification-code',
      message: data.message || 'Invalid or expired OTP code'
    };
  }

  console.log('[Firebase Auth] Signing in seamlessly with Custom Token...');
  const userCredential = await signInWithCustomToken(auth, data.customToken);
  console.log('[Firebase Auth] User authenticated successfully:', userCredential.user.uid);
  return userCredential;
}
