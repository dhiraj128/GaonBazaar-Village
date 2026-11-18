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
      return admin;
    } catch (e) {
      console.error('[Verify OTP] Error initializing with privateKey:', e);
    }
  }

  try {
    admin.initializeApp({ projectId });
  } catch (e) {
    console.warn('[Firebase Admin] Default initialization warning:', e);
  }

  return admin;
}

interface OtpRecord {
  verificationId: string;
  expiresAt: number; // timestamp ms
  lastSentAt: number;
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

// Retrieve active challenge from Supabase
async function getActiveChallengeFromSupabase(phone: string): Promise<any | null> {
  try {
    const supabaseUrl =
      process.env.SUPABASE_URL ||
      process.env.VITE_SUPABASE_URL ||
      'https://vxewgvrjhjpntfvsmuez.supabase.co';
    const supabaseKey =
      process.env.SUPABASE_SERVICE_ROLE_KEY ||
      process.env.SUPABASE_ANON_KEY ||
      process.env.VITE_SUPABASE_ANON_KEY ||
      'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ4ZXdndnJqaGpwbnRmdnNtdWV6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTM1NDkwMzcsImV4cCI6MjEwOTEyNTAzN30.3jUR0U9RGcgc2q-zeWX7OeWaFqugSHOFdDieYoGFIwQ';

    const resp = await fetch(
      `${supabaseUrl}/rest/v1/otp_challenges?phone=eq.${phone}&is_used=eq.false&order=created_at.desc&limit=1`,
      {
        headers: {
          apikey: supabaseKey,
          Authorization: `Bearer ${supabaseKey}`,
          'Content-Type': 'application/json',
        },
      }
    );
    if (resp.ok) {
      const rows = await resp.json();
      if (Array.isArray(rows) && rows.length > 0) {
        return rows[0];
      }
    }
  } catch (err) {
    console.warn('[Verify OTP] Supabase fetch challenge notice:', err);
  }
  return null;
}

// Mark challenge as used in Supabase
async function markChallengeUsedInSupabase(verificationId: string) {
  try {
    const supabaseUrl =
      process.env.SUPABASE_URL ||
      process.env.VITE_SUPABASE_URL ||
      'https://vxewgvrjhjpntfvsmuez.supabase.co';
    const supabaseKey =
      process.env.SUPABASE_SERVICE_ROLE_KEY ||
      process.env.SUPABASE_ANON_KEY ||
      process.env.VITE_SUPABASE_ANON_KEY ||
      'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ4ZXdndnJqaGpwbnRmdnNtdWV6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTM1NDkwMzcsImV4cCI6MjEwOTEyNTAzN30.3jUR0U9RGcgc2q-zeWX7OeWaFqugSHOFdDieYoGFIwQ';

    await fetch(`${supabaseUrl}/rest/v1/otp_challenges?session_id=eq.${encodeURIComponent(verificationId)}`, {
      method: 'PATCH',
      headers: {
        apikey: supabaseKey,
        Authorization: `Bearer ${supabaseKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ is_used: true }),
    });
  } catch (err) {
    console.warn('[Verify OTP] Supabase mark used notice:', err);
  }
}

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
          message: 'Invalid JSON request body',
        });
      }
    }
    body = body || {};

    const rawPhone = body.phoneNumber || body.phone || '';
    let clean = String(rawPhone || '').replace(/[^\d+]/g, '').trim();
    if (clean.startsWith('+91')) {
      clean = clean.slice(3);
    } else if (clean.startsWith('91') && clean.length === 12) {
      clean = clean.slice(2);
    } else if (clean.startsWith('0') && clean.length === 11) {
      clean = clean.slice(1);
    }
    clean = clean.replace(/\D/g, '');
    const enteredOtp = String(body.otp || '').trim();
    const role = body.role || 'customer';

    if (!clean || !enteredOtp) {
      return sendJson(res, 400, {
        success: false,
        code: 'auth/missing-fields',
        error: 'Phone number and 4-digit OTP code are required',
        message: 'Phone number and 4-digit OTP code are required',
      });
    }

    // Strictly validate 4-digit OTP format (Message Central VerifyNow standard)
    if (!/^\d{4}$/.test(enteredOtp)) {
      return sendJson(res, 400, {
        success: false,
        code: 'auth/invalid-otp-format',
        error: 'Please enter a valid 4-digit OTP code',
        message: 'Please enter a valid 4-digit OTP code',
      });
    }

    // Step 1: Retrieve Message Central credentials securely
    const customerId = process.env.MESSAGE_CENTRAL_CUSTOMER_ID || '';
    const authToken = process.env.MESSAGE_CENTRAL_AUTH_TOKEN || '';

    if (!authToken) {
      console.error('[Message Central VerifyNow] CRITICAL: MESSAGE_CENTRAL_AUTH_TOKEN not configured in environment.');
      return sendJson(res, 500, {
        success: false,
        code: 'auth/gateway-not-configured',
        error: 'SMS OTP Gateway credentials (MESSAGE_CENTRAL_AUTH_TOKEN) are not configured in the server environment.',
        message: 'SMS OTP Gateway credentials (MESSAGE_CENTRAL_AUTH_TOKEN) are not configured in the server environment.',
      });
    }

    // Step 2: Resolve Verification ID
    let verificationId = body.verificationId ? String(body.verificationId) : '';

    if (!verificationId) {
      // Look up in memory cache first
      const memRecord = getOtpCache().get(clean);
      if (memRecord && memRecord.verificationId) {
        verificationId = memRecord.verificationId;
      }
    }

    if (!verificationId) {
      // Look up in Supabase persistent challenges
      const sbRecord = await getActiveChallengeFromSupabase(clean);
      if (sbRecord && sbRecord.session_id) {
        verificationId = sbRecord.session_id;
      }
    }

    if (!verificationId) {
      // Look up in Firestore
      try {
        const fbAdmin = getFirebaseAdmin();
        if (fbAdmin && fbAdmin.firestore) {
          const docSnap = await fbAdmin.firestore().collection('otp_challenges').doc(clean).get();
          if (docSnap.exists) {
            const data = docSnap.data();
            if (data?.verificationId && !data?.isUsed) {
              verificationId = data.verificationId;
            }
          }
        }
      } catch (fsErr) {
        console.warn('[Verify OTP] Firestore lookup notice:', fsErr);
      }
    }

    if (!verificationId) {
      return sendJson(res, 400, {
        success: false,
        code: 'auth/session-not-found',
        error: 'No active OTP verification session found for this number. Please request an OTP.',
        message: 'No active OTP verification session found for this number. Please request an OTP.',
      });
    }

    // Step 3: Validate with Message Central VerifyNow API
    const params = new URLSearchParams({
      countryCode: '91',
      mobileNumber: clean,
      verificationId: verificationId,
      code: enteredOtp,
    });
    if (customerId) {
      params.append('customerId', customerId);
    }

    const mcValidateUrl = `https://cpaas.messagecentral.com/verification/v3/validateOtp?${params.toString()}`;
    console.log(`[Message Central VerifyNow] Validating 4-digit OTP for +91${clean} (Verification ID: ${verificationId})...`);

    const mcResponse = await fetch(mcValidateUrl, {
      method: 'GET',
      headers: {
        authToken: authToken,
        accept: '*/*',
      },
    });

    const mcText = await mcResponse.text();
    let mcData: any = {};
    try {
      mcData = JSON.parse(mcText);
    } catch {
      mcData = { responseCode: mcResponse.status, message: mcText };
    }

    console.log(`[Message Central VerifyNow] Validation result for +91${clean}:`, mcResponse.status, mcData?.responseCode, mcData?.data?.verificationStatus);

    // Step 4: Strict Verification Check (Message Central status code 200 and VERIFICATION_COMPLETED)
    const isVerified =
      mcResponse.ok &&
      (mcData.responseCode === 200 || mcData.responseCode === '200') &&
      (mcData.data?.verificationStatus === 'VERIFICATION_COMPLETED' || mcData.data?.responseCode === '200' || mcData.data?.responseCode === 200);

    if (!isVerified) {
      const errMessage =
        mcData.data?.errorMessage ||
        mcData.message ||
        'Invalid 4-digit verification code. Please check your SMS and try again.';

      return sendJson(res, 400, {
        success: false,
        code: 'auth/invalid-verification-code',
        error: errMessage,
        message: errMessage,
        details: mcData?.data,
      });
    }

    // Step 5: Mark challenge as used to prevent replay
    getOtpCache().delete(clean);
    await markChallengeUsedInSupabase(verificationId);

    try {
      const fbAdmin = getFirebaseAdmin();
      if (fbAdmin && fbAdmin.firestore) {
        await fbAdmin.firestore().collection('otp_challenges').doc(clean).update({
          isUsed: true,
          verifiedAt: new Date().toISOString(),
        });
      }
    } catch (fsErr) {
      console.warn('[Verify OTP] Firestore mark used notice:', fsErr);
    }

    // Step 6: Mint Firebase Custom Token for authenticated session
    const formattedPhone = `+91${clean}`;
    console.log(`[Verify OTP] Message Central confirmed valid. Minting Firebase Custom Token for: ${formattedPhone}`);

    try {
      const fbAdmin = getFirebaseAdmin();
      const customToken = await fbAdmin.auth().createCustomToken(formattedPhone, {
        phone_number: formattedPhone,
        role: role,
        verified_via: 'message_central_verifynow',
      });

      console.log(`[Verify OTP] Custom token successfully minted for: ${formattedPhone}`);
      return sendJson(res, 200, {
        success: true,
        message: 'OTP verified successfully via Message Central',
        customToken,
        phoneNumber: formattedPhone,
        role,
      });
    } catch (tokenErr: any) {
      console.error('[VERIFY-OTP TOKEN ERROR]:', tokenErr);
      return sendJson(res, 500, {
        success: false,
        code: 'auth/custom-token-failed',
        error: tokenErr?.message || 'Failed to mint Firebase Custom Token. Ensure Firebase service account credentials are configured.',
        message: tokenErr?.message || 'Failed to mint Firebase Custom Token. Ensure Firebase service account credentials are configured.',
        details: tokenErr?.code,
      });
    }
  } catch (error: any) {
    console.error('[VERIFY-OTP FATAL ERROR]:', error);
    return sendJson(res, 500, {
      success: false,
      code: 'auth/internal-error',
      error: error?.message || 'Internal server error verifying OTP',
      message: error?.message || 'Internal server error verifying OTP',
    });
  }
}
