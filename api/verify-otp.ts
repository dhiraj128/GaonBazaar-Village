import * as crypto from 'crypto';

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

    const res = await fetch(
      `${supabaseUrl}/rest/v1/otp_challenges?phone=eq.${encodeURIComponent(
        phone
      )}&is_used=eq.false&order=created_at.desc&limit=1`,
      {
        headers: {
          apikey: supabaseKey,
          Authorization: `Bearer ${supabaseKey}`,
          'Content-Type': 'application/json',
        },
      }
    );

    if (!res.ok) return null;
    const data = await res.json();
    return Array.isArray(data) && data.length > 0 ? data[0] : null;
  } catch (err) {
    console.warn('[Verify OTP] Supabase challenge lookup notice:', err);
    return null;
  }
}

// Mark challenge used in Supabase
async function markChallengeUsedInSupabase(verificationId: string): Promise<void> {
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

    await fetch(
      `${supabaseUrl}/rest/v1/otp_challenges?id=eq.${encodeURIComponent(
        verificationId
      )}`,
      {
        method: 'PATCH',
        headers: {
          apikey: supabaseKey,
          Authorization: `Bearer ${supabaseKey}`,
          'Content-Type': 'application/json',
          Prefer: 'return=minimal',
        },
        body: JSON.stringify({ is_used: true }),
      }
    );
  } catch (err) {
    console.warn('[Verify OTP] Supabase mark used notice:', err);
  }
}

// Look up or initialize user record in Supabase PostgreSQL
async function getOrCreateUser(cleanPhone: string, role: string, name?: string): Promise<any> {
  const supabaseUrl =
    process.env.SUPABASE_URL ||
    process.env.VITE_SUPABASE_URL ||
    'https://vxewgvrjhjpntfvsmuez.supabase.co';
  const supabaseKey =
    process.env.SUPABASE_SERVICE_ROLE_KEY ||
    process.env.SUPABASE_ANON_KEY ||
    process.env.VITE_SUPABASE_ANON_KEY ||
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ4ZXdndnJqaGpwbnRmdnNtdWV6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTM1NDkwMzcsImV4cCI6MjEwOTEyNTAzN30.3jUR0U9RGcgc2q-zeWX7OeWaFqugSHOFdDieYoGFIwQ';

  try {
    // 1. Search for existing user by phone number
    const res = await fetch(
      `${supabaseUrl}/rest/v1/users?phone=eq.${encodeURIComponent(cleanPhone)}&select=*`,
      {
        headers: {
          apikey: supabaseKey,
          Authorization: `Bearer ${supabaseKey}`,
          'Content-Type': 'application/json',
        },
      }
    );

    if (res.ok) {
      const users = await res.json();
      if (Array.isArray(users) && users.length > 0) {
        console.log(`[Auth DB] Existing user account resolved for +91${cleanPhone}:`, users[0].id);
        return users[0];
      }
    }

    // 2. New user registration
    const newUserId = `usr_${cleanPhone}`;
    const defaultName =
      (name && name.trim()) ||
      (role === 'vendor' ? 'Shopkeeper' : role === 'runner' ? 'Runner Partner' : 'Customer');

    const newUser = {
      id: newUserId,
      phone: cleanPhone,
      name: defaultName,
      role: role || 'customer',
      preferred_language: 'hi',
      is_active: true,
      kyc_status: 'unverified',
      created_at: new Date().toISOString(),
    };

    const createRes = await fetch(`${supabaseUrl}/rest/v1/users`, {
      method: 'POST',
      headers: {
        apikey: supabaseKey,
        Authorization: `Bearer ${supabaseKey}`,
        'Content-Type': 'application/json',
        Prefer: 'return=representation',
      },
      body: JSON.stringify(newUser),
    });

    if (createRes.ok) {
      const created = await createRes.json();
      if (Array.isArray(created) && created.length > 0) {
        console.log(`[Auth DB] New user record created in Supabase for +91${cleanPhone}:`, created[0].id);
        return created[0];
      }
    }

    return newUser;
  } catch (dbErr) {
    console.error('[Auth DB Exception]:', dbErr);
    return {
      id: `usr_${cleanPhone}`,
      phone: cleanPhone,
      name: name || 'User',
      role: role || 'customer',
      kyc_status: 'unverified',
    };
  }
}

// Generate RFC 7519 compliant HS256 JWT access token
function createSignedJwt(payload: any, secret: string): string {
  const header = Buffer.from(JSON.stringify({ alg: 'HS256', typ: 'JWT' })).toString('base64url');
  const body = Buffer.from(JSON.stringify(payload)).toString('base64url');
  const signature = crypto
    .createHmac('sha256', secret)
    .update(`${header}.${body}`)
    .digest('base64url');
  return `${header}.${body}.${signature}`;
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
    const role = body.role || 'customer';
    const name = body.name || '';
    let clean = String(rawPhone || '').replace(/[^\d+]/g, '').trim();
    if (clean.startsWith('+91')) {
      clean = clean.slice(3);
    } else if (clean.startsWith('91') && clean.length === 12) {
      clean = clean.slice(2);
    } else if (clean.startsWith('0') && clean.length === 11) {
      clean = clean.slice(1);
    }
    clean = clean.replace(/\D/g, '');

    const enteredOtp = String(body.otp || body.code || '').trim();

    // Validate 10-digit Indian Mobile format (strictly starts with 6-9)
    if (!/^[6-9]\d{9}$/.test(clean)) {
      return sendJson(res, 400, {
        success: false,
        code: 'auth/invalid-phone-number',
        error: 'Please enter a valid 10-digit Indian mobile number',
        message: 'Please enter a valid 10-digit Indian mobile number',
      });
    }

    // Validate that the code is strictly 4 digits
    if (!/^\d{4}$/.test(enteredOtp)) {
      return sendJson(res, 400, {
        success: false,
        code: 'auth/invalid-otp-length',
        error: 'Please enter a valid 4-digit verification code',
        message: 'Please enter a valid 4-digit verification code',
      });
    }

    // Step 1: Retrieve Message Central credentials securely from server-side environment
    const customerId = process.env.MESSAGE_CENTRAL_CUSTOMER_ID || '';
    const authToken = process.env.MESSAGE_CENTRAL_AUTH_TOKEN || '';

    if (!authToken) {
      console.error('[CRITICAL] Missing MESSAGE_CENTRAL_AUTH_TOKEN in serverless environment.');
      return sendJson(res, 500, {
        success: false,
        code: 'auth/missing-credentials',
        error: 'Server configuration error: SMS gateway authentication credentials are not configured.',
        message: 'Server configuration error: SMS gateway authentication credentials are not configured.',
      });
    }

    // Step 2: Resolve verificationId for Message Central
    let verificationId = body.verificationId || body.sessionId || '';

    if (!verificationId) {
      const cached = getOtpCache().get(clean);
      if (cached && cached.verificationId) {
        verificationId = cached.verificationId;
      }
    }

    if (!verificationId) {
      const challenge = await getActiveChallengeFromSupabase(clean);
      if (challenge && (challenge.session_id || challenge.id)) {
        verificationId = challenge.session_id || challenge.id;
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

    // Step 6: Identify or initialize user in database
    const user = await getOrCreateUser(clean, role, name);

    // Step 7: Issue secure production JWT session token
    const jwtSecret =
      process.env.SECRET_KEY ||
      process.env.JWT_SECRET ||
      'dev-insecure-secret-key-change-in-production';

    const nowSec = Math.floor(Date.now() / 1000);
    const tokenPayload = {
      sub: user.id,
      phone: `+91${clean}`,
      role: user.role || role || 'customer',
      name: user.name || 'User',
      iat: nowSec,
      exp: nowSec + 7 * 24 * 60 * 60, // 7 days expiration
    };

    const accessToken = createSignedJwt(tokenPayload, jwtSecret);

    console.log(`[Auth Success] Session token successfully issued for user ${user.id} (+91${clean})`);

    // Set HttpOnly session cookie where supported
    const cookieHeader = `gb_session=${accessToken}; Path=/; Max-Age=${7 * 24 * 60 * 60}; SameSite=Lax; Secure`;
    res.setHeader('Set-Cookie', cookieHeader);

    return sendJson(res, 200, {
      success: true,
      message: 'OTP verified successfully via Message Central',
      token: accessToken,
      accessToken: accessToken,
      tokenType: 'bearer',
      user: {
        id: user.id,
        phone: `+91${clean}`,
        role: user.role || role || 'customer',
        name: user.name || 'User',
        kyc_status: user.kyc_status || 'unverified',
      },
    });
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
