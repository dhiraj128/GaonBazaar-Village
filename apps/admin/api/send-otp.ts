import * as firebaseAdmin from 'firebase-admin';

const admin = (firebaseAdmin as any).default || firebaseAdmin;

function getFirebaseAdmin() {
  try {
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
        return admin;
      } catch (e) {
        console.error('[Send OTP] Error parsing FIREBASE_SERVICE_ACCOUNT:', e);
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
        return admin;
      } catch (e) {
        console.error('[Send OTP] Error initializing with privateKey:', e);
      }
    }

    try {
      admin.initializeApp({ projectId });
    } catch (e) {
      console.warn('[Send OTP] Default initialization notice:', e);
    }

    return admin;
  } catch (err) {
    console.warn('[Send OTP] getFirebaseAdmin caught exception:', err);
    return null;
  }
}

// Cross-invocation in-memory cache for Vercel functions
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
    console.error('[Send OTP sendJson error]:', e);
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
        console.error('[Send OTP Body Parse Error]:', pErr);
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

    // Validate 10-digit Indian Mobile format (starts with 6-9) or Razorpay backdoor 9999999999
    if (!/^[6-9]\d{9}$/.test(clean) && clean !== '9999999999') {
      return sendJson(res, 400, {
        success: false,
        code: 'auth/invalid-phone-number',
        error: 'Please enter a valid 10-digit Indian mobile number',
        message: 'Please enter a valid 10-digit Indian mobile number'
      });
    }

    // Razorpay Compliance Review Backdoor: ONLY 9999999999
    if (clean === '9999999999') {
      const otp = '123456';
      const expiresAt = Date.now() + 5 * 60 * 1000;
      getOtpCache().set(clean, { otp, expiresAt, attempts: 0 });
      return sendJson(res, 200, {
        success: true,
        message: 'Razorpay Compliance Review: Static code 123456 active',
        phoneNumber: clean
      });
    }

    // Generate secure 6-digit OTP
    const otp = Math.floor(100000 + Math.random() * 900000).toString();
    const expiresAt = Date.now() + 5 * 60 * 1000;

    // 1. Store in memory cache
    getOtpCache().set(clean, { otp, expiresAt, attempts: 0 });

    // 2. Optional: Store in Firestore collection 'otp_challenges'
    try {
      const fbAdmin = getFirebaseAdmin();
      if (fbAdmin && fbAdmin.firestore) {
        await fbAdmin.firestore().collection('otp_challenges').doc(clean).set({
          otp,
          phoneNumber: clean,
          expiresAt: new Date(expiresAt).toISOString(),
          createdAt: new Date().toISOString(),
          isUsed: false
        });
        console.log(`[Send OTP] Challenge synced to Firestore for +91${clean}`);
      }
    } catch (fsErr) {
      console.warn('[Send OTP] Firestore sync notice (continuing without Firestore):', fsErr);
    }

    // 3. Dispatch SMS via Fast2SMS API
    const fast2smsApiKey = process.env.FAST2SMS_API_KEY || 'XsoSYvBFIKVteH8tVfguXYkVcFsxVrVLFDbeH3sTPPv0vyErS6yuPzySrgai1ir1lVg31OVM8CnyXiio';

    console.log(`[Fast2SMS] Dispatching OTP to +91${clean}...`);
    const f2sResponse = await fetch('https://www.fast2sms.com/dev/bulkV2', {
      method: 'POST',
      headers: {
        'authorization': fast2smsApiKey,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        route: 'otp',
        variables_values: otp,
        numbers: clean
      })
    });

    const f2sText = await f2sResponse.text();
    let f2sData: any = {};
    try {
      f2sData = JSON.parse(f2sText);
    } catch {
      f2sData = { return: false, message: f2sText };
    }

    console.log(`[Fast2SMS] Response for +91${clean}:`, f2sData);

    if (f2sResponse.ok && f2sData.return) {
      return sendJson(res, 200, {
        success: true,
        message: 'OTP sent successfully via Fast2SMS',
        phoneNumber: clean
      });
    } else {
      const errDetail = Array.isArray(f2sData.message)
        ? f2sData.message.join(', ')
        : (f2sData.message || 'SMS Gateway rejection');
      console.error('[Fast2SMS Delivery Error]:', errDetail);
      return sendJson(res, 502, {
        success: false,
        code: 'auth/sms-delivery-failed',
        error: `Fast2SMS delivery error: ${errDetail}`,
        message: `Fast2SMS delivery error: ${errDetail}`,
        details: f2sData
      });
    }
  } catch (error: any) {
    console.error('[SEND-OTP FATAL ERROR]:', error);
    return sendJson(res, 500, {
      success: false,
      code: 'auth/internal-error',
      error: error?.message || 'Internal server error dispatching OTP',
      message: error?.message || 'Internal server error dispatching OTP'
    });
  }
}
