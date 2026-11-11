import { initializeApp, getApps, getApp } from 'firebase/app';
import {
  getAuth,
  RecaptchaVerifier,
  signInWithPhoneNumber,
  type ConfirmationResult,
  type Auth,
  type UserCredential
} from 'firebase/auth';

export type { ConfirmationResult, UserCredential };

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

// Global confirmation result cache
let activeConfirmationResult: ConfirmationResult | null = null;
let activeRecaptchaVerifier: RecaptchaVerifier | null = null;

/**
 * Initializes or retrieves an invisible RecaptchaVerifier attached to the Send OTP button or container.
 */
export function getOrCreateRecaptchaVerifier(preferredTargetId = 'send-otp-btn'): RecaptchaVerifier {
  if (typeof window === 'undefined') {
    throw new Error('reCAPTCHA can only be initialized in browser environment');
  }

  // If already instantiated, verify or reuse
  if (activeRecaptchaVerifier) {
    return activeRecaptchaVerifier;
  }

  // 1. Unmask the Real Firebase Error & Ensure reCAPTCHA Container is Mounted
  let targetId = preferredTargetId;
  let targetElement = document.getElementById(targetId);

  // If button not found, fallback to dedicated container
  if (!targetElement) {
    targetId = 'firebase-recaptcha-container';
    targetElement = document.getElementById(targetId);
  }

  // If neither exists, dynamically inject a safe, non-hidden container
  if (!targetElement) {
    targetElement = document.createElement('div');
    targetElement.id = 'firebase-recaptcha-container';
    targetElement.style.position = 'fixed';
    targetElement.style.bottom = '0';
    targetElement.style.opacity = '0';
    targetElement.style.pointerEvents = 'none';
    targetElement.style.zIndex = '-1';
    document.body.appendChild(targetElement);
    targetId = 'firebase-recaptcha-container';
  }

  console.log('[Firebase reCAPTCHA] Initializing invisible RecaptchaVerifier on target:', targetId);

  activeRecaptchaVerifier = new RecaptchaVerifier(auth, targetId, {
    size: 'invisible',
    callback: (response: any) => {
      console.log('[Firebase Recaptcha] Invisible challenge solved successfully, response token length:', response?.length || 0);
    },
    'expired-callback': () => {
      console.warn('[Firebase Recaptcha] Token expired. Resetting verifier...');
      resetRecaptchaVerifier();
    }
  });

  return activeRecaptchaVerifier;
}

/**
 * Clears and resets the reCAPTCHA verifier instance.
 */
export function resetRecaptchaVerifier(): void {
  if (activeRecaptchaVerifier) {
    try {
      activeRecaptchaVerifier.clear();
    } catch (e) {
      console.warn('[Firebase Recaptcha] Error clearing verifier:', e);
    }
    activeRecaptchaVerifier = null;
  }
}

/**
 * Sends a live SMS OTP via Firebase Phone Authentication with invisible reCAPTCHA.
 * Strictly enforces +91 country code prefix.
 */
export async function sendFirebaseOtp(rawPhone: string, targetId = 'send-otp-btn'): Promise<ConfirmationResult> {
  const clean10 = rawPhone.replace(/\D/g, '').slice(-10);
  if (!/^[6-9]\d{9}$/.test(clean10) && clean10 !== '9999999999') {
    throw {
      code: 'auth/invalid-phone-number',
      message: 'Please enter a valid 10-digit Indian mobile number (e.g. 9905361711)'
    };
  }

  // Enforce +91 Prefix
  const formattedPhone = `+91${clean10}`;
  console.log('[Firebase Auth] Dispatching SMS OTP to:', formattedPhone);

  const verifier = getOrCreateRecaptchaVerifier(targetId);

  try {
    const confirmationResult = await signInWithPhoneNumber(auth, formattedPhone, verifier);
    activeConfirmationResult = confirmationResult;
    console.log('[Firebase Auth] SMS verification code sent successfully to:', formattedPhone);
    return confirmationResult;
  } catch (error: any) {
    // 1. Unmask the Real Firebase Error: aggressively log to console
    console.error("FIREBASE FATAL ERROR:", error?.code, error?.message);
    console.error("FIREBASE FULL ERROR:", error);
    resetRecaptchaVerifier();
    throw error;
  }
}

/**
 * Verifies the 6-digit OTP code using the active confirmation result.
 */
export async function verifyFirebaseOtp(code: string): Promise<UserCredential> {
  if (!activeConfirmationResult) {
    throw {
      code: 'auth/null-confirmation-result',
      message: 'No active OTP verification session found. Please request a new OTP.'
    };
  }

  try {
    const result = await activeConfirmationResult.confirm(code);
    console.log('[Firebase Auth] User successfully verified via OTP:', result.user.phoneNumber);
    return result;
  } catch (error: any) {
    console.error("FIREBASE FATAL ERROR:", error?.code, error?.message);
    console.error("FIREBASE FULL ERROR:", error);
    throw error;
  }
}

export function getActiveConfirmationResult(): ConfirmationResult | null {
  return activeConfirmationResult;
}
