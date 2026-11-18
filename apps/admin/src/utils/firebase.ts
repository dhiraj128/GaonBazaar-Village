/**
 * GaonBazaar Pure Message Central & Backend Session Authentication Client
 * Zero Firebase dependencies - Powered directly by Message Central VerifyNow and Supabase backend.
 */

export interface AuthUser {
  uid: string;
  id: string;
  phone: string;
  role: string;
  name: string;
  getIdToken: () => Promise<string>;
}

export interface UserCredential {
  user: AuthUser;
  token?: string;
}

export type ConfirmationResult = any;

export function resetRecaptchaVerifier(): void {
  // Legacy stub: permanent no-op
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
      message: 'Please enter a valid 10-digit Indian mobile number',
    };
  }

  console.log('[Message Central Client] Requesting 4-digit OTP dispatch for:', clean10);

  let response: Response;
  try {
    response = await fetch('/api/send-otp', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
      body: JSON.stringify({ phoneNumber: clean10, role }),
    });
  } catch (netErr: any) {
    console.error('[Message Central Client Network Exception]:', netErr);
    throw {
      code: 'auth/network-error',
      message: 'Network connection error. Please verify your internet connection.',
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
      message: `Server returned HTTP ${response.status}: ${rawText.slice(0, 100) || 'Service temporarily unavailable'}`,
    };
  }

  if (!response.ok || !data.success) {
    throw {
      code: data.code || 'auth/sms-failed',
      message: data.message || data.error || 'Unable to send OTP via SMS gateway. Please try again.',
    };
  }

  return data;
}

/**
 * Verifies the 4-digit OTP code with Message Central VerifyNow (/api/verify-otp),
 * receives a secure backend JWT session token, and establishes authenticated session.
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
      message: 'Please enter the complete 4-digit verification code',
    };
  }

  console.log('[Message Central Client] Verifying OTP and requesting JWT Session for:', clean10);

  let response: Response;
  try {
    response = await fetch('/api/verify-otp', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
      body: JSON.stringify({
        phoneNumber: clean10,
        otp: cleanOtp,
        verificationId: verificationId || undefined,
        role,
      }),
    });
  } catch (netErr: any) {
    console.error('[Message Central Verify Network Exception]:', netErr);
    throw {
      code: 'auth/network-error',
      message: 'Network connection error. Please verify your internet connection.',
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
      message: `Server returned HTTP ${response.status}: ${rawText.slice(0, 100) || 'Service temporarily unavailable'}`,
    };
  }

  const token = data.token || data.accessToken || data.customToken;

  if (!response.ok || !data.success || !token) {
    throw {
      code: data.code || 'auth/invalid-verification-code',
      message: data.message || data.error || 'Invalid or expired OTP code. Please check your SMS.',
    };
  }

  const authUser: AuthUser = {
    uid: data.user?.id || `usr_${clean10}`,
    id: data.user?.id || `usr_${clean10}`,
    phone: data.user?.phone || `+91${clean10}`,
    role: data.user?.role || role,
    name: data.user?.name || 'Customer',
    getIdToken: async () => token,
  };

  try {
    localStorage.setItem('gaonbazaar_admin_jwt_token', token);
    localStorage.setItem('gb_customer_token', token);
    localStorage.setItem('gb_customer_jwt', token);
    localStorage.setItem('gb_auth_token', token);
  } catch {}

  console.log('[Auth Success] User authenticated successfully via Backend JWT:', authUser.uid);
  return { user: authUser, token };
}

// Backwards-compatible aliases
export const sendFast2SmsOtp = sendMessageCentralOtp;
export const verifyFast2SmsOtp = (rawPhone: string, otp: string) => verifyMessageCentralOtp(rawPhone, otp);
export const sendFirebaseTestPhoneOtp = async (rawPhone: string) => null;
