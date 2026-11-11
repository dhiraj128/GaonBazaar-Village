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
 * Initializes or retrieves an invisible RecaptchaVerifier attached to the recaptcha-container.
 */
export function getOrCreateRecaptchaVerifier(preferredTargetId = 'recaptcha-container'): RecaptchaVerifier {
  if (typeof window === 'undefined') {
    throw new Error('reCAPTCHA can only be initialized in browser environment');
  }

  // Check window global reference as well
  if ((window as any).recaptchaVerifier) {
    activeRecaptchaVerifier = (window as any).recaptchaVerifier;
    return activeRecaptchaVerifier as RecaptchaVerifier;
  }

  // If already instantiated, verify or reuse
  if (activeRecaptchaVerifier) {
    (window as any).recaptchaVerifier = activeRecaptchaVerifier;
    return activeRecaptchaVerifier;
  }

  // 1. Unmask the Real Firebase Error & Ensure reCAPTCHA Container is Mounted
  let targetId = preferredTargetId;
  let targetElement = document.getElementById(targetId);

  // If preferred target not found, fallback to dedicated 'recaptcha-container'
  if (!targetElement) {
    targetId = 'recaptcha-container';
    targetElement = document.getElementById(targetId);
  }

  // If still does not exist, check legacy container id
  if (!targetElement) {
    const legacyEl = document.getElementById('firebase-recaptcha-container');
    if (legacyEl) {
      targetId = 'firebase-recaptcha-container';
      targetElement = legacyEl;
    }
  }

  // If neither exists, dynamically inject a safe, dedicated container
  if (!targetElement) {
    targetElement = document.createElement('div');
    targetElement.id = 'recaptcha-container';
    document.body.appendChild(targetElement);
    targetId = 'recaptcha-container';
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

  (window as any).recaptchaVerifier = activeRecaptchaVerifier;
  return activeRecaptchaVerifier;
}

/**
 * Clears and resets the reCAPTCHA verifier instance.
 */
export function resetRecaptchaVerifier(): void {
  // Use window.recaptchaVerifier.clear() before resetting to prevent hanging/spinning
  if (typeof window !== 'undefined' && (window as any).recaptchaVerifier) {
    try {
      (window as any).recaptchaVerifier.clear();
      console.log('[Firebase Recaptcha] window.recaptchaVerifier cleared successfully');
    } catch (e) {
      console.warn('[Firebase Recaptcha] Error clearing window.recaptchaVerifier:', e);
    }
    (window as any).recaptchaVerifier = null;
  }

  if (activeRecaptchaVerifier) {
    try {
      activeRecaptchaVerifier.clear();
    } catch (e) {
      console.warn('[Firebase Recaptcha] Error clearing activeRecaptchaVerifier:', e);
    }
    activeRecaptchaVerifier = null;
  }

  // Clear inner DOM of container so stale iframes/scripts don't persist
  if (typeof document !== 'undefined') {
    const el = document.getElementById('recaptcha-container');
    if (el) {
      el.innerHTML = '';
    }
    const legacyEl = document.getElementById('firebase-recaptcha-container');
    if (legacyEl) {
      legacyEl.innerHTML = '';
    }
  }
}

/**
 * Sends a live SMS OTP via Firebase Phone Authentication with invisible reCAPTCHA.
 * Strictly enforces +91 country code prefix (+91${clean10}) with no spaces or dashes.
 */
export async function sendFirebaseOtp(rawPhone: string, targetId = 'recaptcha-container'): Promise<ConfirmationResult> {
  const clean10 = rawPhone.replace(/\D/g, '').slice(-10);
  if (!/^[6-9]\d{9}$/.test(clean10) && clean10 !== '9999999999') {
    throw {
      code: 'auth/invalid-phone-number',
      message: 'Please enter a valid 10-digit Indian mobile number'
    };
  }

  // Enforce +91 Prefix strictly formatted as +91${clean10}
  const formattedPhone = `+91${clean10}`;
  console.log('[Firebase Auth] Dispatching SMS OTP to:', formattedPhone);

  const verifier = getOrCreateRecaptchaVerifier(targetId);

  try {
    // Wrap with a 20-second timeout to prevent indefinite spinning when domain is unauthorized
    const confirmationPromise = signInWithPhoneNumber(auth, formattedPhone, verifier);
    const timeoutPromise = new Promise<never>((_, reject) => {
      setTimeout(() => {
        reject({
          code: 'auth/captcha-timeout',
          message: 'reCAPTCHA verification timed out. Ensure apnagaonbazaar.in is added to Firebase Authorized Domains.'
        });
      }, 20000);
    });

    const confirmationResult = await Promise.race([confirmationPromise, timeoutPromise]);
    activeConfirmationResult = confirmationResult;
    console.log('[Firebase Auth] SMS verification code sent successfully to:', formattedPhone);
    return confirmationResult;
  } catch (error: any) {
    // 1. Unmask the Real Firebase Error: aggressively log to console
    console.error("FIREBASE ERROR:", error);
    console.error("FIREBASE FATAL ERROR:", error?.code, error?.message);
    console.error("FIREBASE FULL ERROR:", error);

    // Always clear window.recaptchaVerifier and active verifier in catch block
    if (typeof window !== 'undefined' && (window as any).recaptchaVerifier) {
      try {
        (window as any).recaptchaVerifier.clear();
      } catch (e) {}
      (window as any).recaptchaVerifier = null;
    }
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
