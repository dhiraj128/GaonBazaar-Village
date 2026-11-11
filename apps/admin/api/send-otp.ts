import { getFirebaseAdmin } from './_firebaseAdmin';

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

    // Validate 10-digit Indian Mobile format (starts with 6-9) or Razorpay backdoor 9999999999
    if (!/^[6-9]\d{9}$/.test(clean) && clean !== '9999999999') {
      return res.status(400).json({
        success: false,
        code: 'auth/invalid-phone-number',
        message: 'Please enter a valid 10-digit Indian mobile number'
      });
    }

    // Razorpay Compliance Review Backdoor: ONLY 9999999999
    if (clean === '9999999999') {
      const otp = '123456';
      const expiresAt = Date.now() + 5 * 60 * 1000;
      getOtpCache().set(clean, { otp, expiresAt, attempts: 0 });
      return res.status(200).json({
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

    // 2. Store in Firestore collection 'otp_challenges' if Firebase Admin is available
    try {
      const admin = getFirebaseAdmin();
      if (admin && admin.firestore) {
        await admin.firestore().collection('otp_challenges').doc(clean).set({
          otp,
          phoneNumber: clean,
          expiresAt: new Date(expiresAt).toISOString(),
          createdAt: new Date().toISOString(),
          isUsed: false
        });
      }
    } catch (fsErr) {
      console.warn('[Send OTP] Firestore sync notice:', fsErr);
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

    const f2sData = await f2sResponse.json();
    console.log(`[Fast2SMS] Response for +91${clean}:`, f2sData);

    if (f2sResponse.ok && f2sData.return) {
      return res.status(200).json({
        success: true,
        message: 'OTP sent successfully via Fast2SMS',
        phoneNumber: clean
      });
    } else {
      const errDetail = Array.isArray(f2sData.message) ? f2sData.message.join(', ') : (f2sData.message || 'SMS Gateway rejection');
      console.error('[Fast2SMS Error]:', errDetail);
      return res.status(502).json({
        success: false,
        code: 'auth/sms-delivery-failed',
        message: `Fast2SMS delivery error: ${errDetail}`,
        details: f2sData
      });
    }
  } catch (error: any) {
    console.error('[Send OTP Serverless Fatal Error]:', error);
    return res.status(500).json({
      success: false,
      code: 'auth/internal-error',
      message: error?.message || 'Internal server error dispatching OTP'
    });
  }
}
