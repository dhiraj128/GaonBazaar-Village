import * as firebaseAdmin from 'firebase-admin';

const admin = (firebaseAdmin as any).default || firebaseAdmin;

function getFirebaseAdmin() {
  if (admin.apps && admin.apps.length > 0) {
    return admin;
  }

  const projectId = process.env.FIREBASE_PROJECT_ID || 'gaon-bazaar-village';
  const serviceAccountEnv = process.env.FIREBASE_SERVICE_ACCOUNT;
  const privateKey = process.env.FIREBASE_PRIVATE_KEY
    ? process.env.FIREBASE_PRIVATE_KEY.replace(/\\n/g, '\n')
    : undefined;
  const clientEmail = process.env.FIREBASE_CLIENT_EMAIL;

  if (serviceAccountEnv) {
    try {
      const creds = typeof serviceAccountEnv === 'string' ? JSON.parse(serviceAccountEnv) : serviceAccountEnv;
      admin.initializeApp({
        credential: admin.credential.cert(creds),
        projectId: creds.project_id || projectId,
      });
      console.log('[Firebase Admin] Initialized with FIREBASE_SERVICE_ACCOUNT');
      return admin;
    } catch (e) {
      console.error('[Verify OTP] Error parsing FIREBASE_SERVICE_ACCOUNT:', e);
    }
  }

  if (privateKey && clientEmail) {
    try {
      admin.initializeApp({
        credential: admin.credential.cert({
          projectId,
          clientEmail,
          privateKey,
        }),
        projectId,
      });
      console.log('[Firebase Admin] Initialized with privateKey and clientEmail');
      return admin;
    } catch (e) {
      console.error('[Verify OTP] Error initializing with privateKey:', e);
    }
  }

  // Initialize with application default or projectId
  try {
    admin.initializeApp({
      projectId,
    });
    console.log('[Firebase Admin] Initialized with project ID fallback');
  } catch (e) {
    console.warn('[Firebase Admin] Default initialization warning:', e);
  }

  return admin;
}

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

const sendJson = (res: any, statusCode: number, data: any) => {
  try {
    res.setHeader('Content-Type', 'application/json');
    if (typeof res.status === 'function') {
      return res.status(statusCode).json(data);
    }
    res.statusCode = statusCode;
    return res.end(JSON.stringify(data));
  } catch (e) {
    console.error('[Verify OTP sendJson error]:', e);
  }
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
  res.setHeader('Content-Type', 'application/json');

  if (req.method === 'OPTIONS') {
    return sendJson(res, 200, { success: true });
  }

  if (req.method !== 'POST') {
    return sendJson(res, 405, { success: false, error: 'Method Not Allowed', message: 'Method Not Allowed' });
  }

  try {
    let body = req.body;
    if (typeof body === 'string') {
      try {
        body = JSON.parse(body);
      } catch (pErr) {
        console.error('[Verify OTP Body Parse Error]:', pErr);
        return sendJson(res, 400, {
          success: false,
          error: 'Invalid JSON request body',
          message: 'Invalid JSON request body'
        });
      }
    }
    body = body || {};

    const rawPhone = body.phoneNumber || body.phone || '';
    const clean = rawPhone.replace(/\D/g, '').slice(-10);
    const enteredOtp = String(body.otp || '').trim();

    if (!clean || !enteredOtp) {
      return sendJson(res, 400, {
        success: false,
        code: 'auth/missing-fields',
        error: 'Phone number and 6-digit OTP code are required',
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
        return sendJson(res, 400, {
          success: false,
          code: 'auth/code-expired',
          error: 'Verification code has expired. Please request a new OTP.',
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
          return sendJson(res, 429, {
            success: false,
            code: 'auth/too-many-requests',
            error: 'Too many incorrect attempts. Please request a new OTP.',
            message: 'Too many incorrect attempts. Please request a new OTP.'
          });
        }
      }
    }

    // 3. Fallback: Check Firestore if in-memory cache missed (e.g. cold lambda instance)
    if (!isVerified && clean !== '9999999999') {
      try {
        const fbAdmin = getFirebaseAdmin();
        if (fbAdmin && fbAdmin.firestore) {
          const docRef = fbAdmin.firestore().collection('otp_challenges').doc(clean);
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
      return sendJson(res, 400, {
        success: false,
        code: 'auth/invalid-verification-code',
        error: 'Invalid OTP code. Please enter the correct 6-digit code.',
        message: 'Invalid OTP code. Please enter the correct 6-digit code.'
      });
    }

    // 4. Crucial Step: Generate Firebase Custom Token
    const formattedPhone = `+91${clean}`;
    console.log(`[Verify OTP] Minting Firebase Custom Token for: ${formattedPhone}`);

    try {
      const fbAdmin = getFirebaseAdmin();
      const customToken = await fbAdmin.auth().createCustomToken(formattedPhone, {
        phone_number: formattedPhone,
        verified_via: 'fast2sms'
      });

      console.log(`[Verify OTP] Custom token successfully minted for: ${formattedPhone}`);
      return sendJson(res, 200, {
        success: true,
        customToken,
        phoneNumber: formattedPhone
      });
    } catch (tokenErr: any) {
      console.error('[VERIFY-OTP TOKEN ERROR]:', tokenErr);
      return sendJson(res, 500, {
        success: false,
        code: 'auth/custom-token-failed',
        error: tokenErr?.message || 'Failed to mint Firebase Custom Token. Ensure Firebase service account credentials are configured.',
        message: tokenErr?.message || 'Failed to mint Firebase Custom Token. Ensure Firebase service account credentials are configured.',
        details: tokenErr?.code
      });
    }
  } catch (error: any) {
    console.error('[VERIFY-OTP FATAL ERROR]:', error);
    return sendJson(res, 500, {
      success: false,
      code: 'auth/internal-error',
      error: error?.message || 'Internal server error verifying OTP',
      message: error?.message || 'Internal server error verifying OTP'
    });
  }
}
