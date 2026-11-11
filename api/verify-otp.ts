import { getFirebaseAdmin } from './_firebaseAdmin';

interface OtpRecord {
  otp: string;
  expiresAt: number; // timestamp ms
  attempts: number;
}

const getOtpCache = (): Map<string, OtpRecord> => {
  if (!(global as any).__gb_otp_cache) {
    (global as any).__gb_otp_cache = new Map<string, OtpRecord>();
  }
  return (global as any).__gb_otp_cache;
};

export default async function handler(req: any, res: any) {
  // CORS configuration
  res.setHeader('Access-Control-Allow-Credentials', 'true');
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
  res.setHeader(
    'Access-Control-Allow-Headers',
    'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version, Authorization'
  );

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ success: false, message: 'Method Not Allowed' });
  }

  try {
    const body = typeof req.body === 'string' ? JSON.parse(req.body) : (req.body || {});
    const rawPhone = body.phoneNumber || body.phone || '';
    const clean = rawPhone.replace(/\D/g, '').slice(-10);
    const enteredOtp = String(body.otp || '').trim();

    if (!clean || !enteredOtp) {
      return res.status(400).json({
        success: false,
        code: 'auth/missing-fields',
        message: 'Phone number and 6-digit OTP code are required'
      });
    }

    let isVerified = false;

    // 1. Razorpay Compliance Review Backdoor
    if (clean === '9999999999' && (enteredOtp === '123456' || enteredOtp === '1234')) {
      isVerified = true;
    }

    // 2. Check In-Memory Cache
    const cached = getOtpCache().get(clean);
    if (!isVerified && cached) {
      if (Date.now() > cached.expiresAt) {
        getOtpCache().delete(clean);
        return res.status(400).json({
          success: false,
          code: 'auth/code-expired',
          message: 'Verification code has expired. Please request a new OTP.'
        });
      }

      if (cached.otp === enteredOtp) {
        isVerified = true;
        getOtpCache().delete(clean);
      } else {
        cached.attempts += 1;
        if (cached.attempts >= 5) {
          getOtpCache().delete(clean);
          return res.status(429).json({
            success: false,
            code: 'auth/too-many-requests',
            message: 'Too many incorrect attempts. Please request a new OTP.'
          });
        }
      }
    }

    // 3. Fallback: Check Firestore if in-memory cache missed (e.g. cold lambda instance)
    if (!isVerified && clean !== '9999999999') {
      try {
        const admin = getFirebaseAdmin();
        if (admin && admin.firestore) {
          const docRef = admin.firestore().collection('otp_challenges').doc(clean);
          const docSnap = await docRef.get();
          if (docSnap.exists) {
            const data = docSnap.data();
            const expiresAtMs = new Date(data?.expiresAt).getTime();
            if (Date.now() <= expiresAtMs && !data?.isUsed && data?.otp === enteredOtp) {
              isVerified = true;
              await docRef.update({ isUsed: true });
            }
          }
        }
      } catch (fsErr) {
        console.warn('[Verify OTP] Firestore fallback check notice:', fsErr);
      }
    }

    if (!isVerified) {
      return res.status(400).json({
        success: false,
        code: 'auth/invalid-verification-code',
        message: 'Invalid OTP code. Please enter the correct 6-digit code.'
      });
    }

    // 4. Crucial Step: Generate Firebase Custom Token
    const admin = getFirebaseAdmin();
    const formattedPhone = `+91${clean}`;
    console.log(`[Verify OTP] Minting Firebase Custom Token for: ${formattedPhone}`);

    try {
      const customToken = await admin.auth().createCustomToken(formattedPhone, {
        phone_number: formattedPhone,
        verified_via: 'fast2sms'
      });

      console.log(`[Verify OTP] Custom token successfully minted for: ${formattedPhone}`);
      return res.status(200).json({
        success: true,
        customToken,
        phoneNumber: formattedPhone
      });
    } catch (tokenErr: any) {
      console.error('[Verify OTP] Firebase Admin createCustomToken error:', tokenErr);
      return res.status(500).json({
        success: false,
        code: 'auth/custom-token-failed',
        message: tokenErr?.message || 'Failed to mint Firebase Custom Token. Ensure Firebase service account credentials are configured in Vercel.',
        details: tokenErr?.code
      });
    }
  } catch (error: any) {
    console.error('[Verify OTP Serverless Fatal Error]:', error);
    return res.status(500).json({
      success: false,
      code: 'auth/internal-error',
      message: error?.message || 'Internal server error verifying OTP'
    });
  }
}
