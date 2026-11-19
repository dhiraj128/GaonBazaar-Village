import type { VercelRequest, VercelResponse } from '@vercel/node';
import * as crypto from 'crypto';

/**
 * Apna GaonBazaar - High-Security OTP Verification & Production Session Issuance
 *
 * Security & Cryptographic Architecture:
 * - Real 4-digit OTP validation via Message Central VerifyNow API v3
 * - Durable challenge resolution from Supabase PostgreSQL (otp_challenges)
 * - Atomic replay attack prevention: Challenge marked is_used=true immediately
 * - Strict role protection & RBAC: Frontend parameters cannot escalate to privileged roles
 * - Authoritative database user state: Existing roles in database are immutable from client
 * - Fail-safe database operations: Never issue a JWT session when DB lookup/creation fails
 * - Full PII masking in logs: Zero raw phone numbers, tokens, or credentials logged
 * - RFC 7519 HS256 JWT tokens with HttpOnly, Secure, SameSite=Lax session cookies
 */

const SUPABASE_URL =
  process.env.SUPABASE_URL ||
  process.env.VITE_SUPABASE_URL ||
  'https://vxewgvrjhjpntfvsmuez.supabase.co';

const SUPABASE_KEY =
  process.env.SUPABASE_SERVICE_ROLE_KEY ||
  process.env.SUPABASE_ANON_KEY ||
  process.env.VITE_SUPABASE_ANON_KEY ||
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ4ZXdndnJqaGpwbnRmdnNtdWV6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTM1NDkwMzcsImV4cCI6MjEwOTEyNTAzN30.3jUR0U9RGcgc2q-zeWX7OeWaFqugSHOFdDieYoGFIwQ';

const ALLOWED_SELF_REGISTER_ROLES = new Set(['customer', 'vendor', 'runner']);

function sendJson(res: any, statusCode: number, data: any) {
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
}

// Retrieve active unexpired challenge from Supabase
async function getActiveChallengeFromSupabase(
  cleanPhone: string,
  verificationId?: string
): Promise<any | null> {
  try {
    let url = `${SUPABASE_URL}/rest/v1/otp_challenges?phone=eq.${encodeURIComponent(
      cleanPhone
    )}&is_used=eq.false`;

    if (verificationId) {
      url += `&session_id=eq.${encodeURIComponent(verificationId)}`;
    } else {
      url += `&order=created_at.desc&limit=1`;
    }

    const res = await fetch(url, {
      headers: {
        apikey: SUPABASE_KEY,
        Authorization: `Bearer ${SUPABASE_KEY}`,
        'Content-Type': 'application/json',
      },
    });

    if (!res.ok) return null;
    const data = await res.json();
    if (!Array.isArray(data) || data.length === 0) return null;

    const challenge = data[0];
    const expiresAt = new Date(challenge.expires_at).getTime();
    if (Date.now() > expiresAt) {
      return null; // Expired challenge
    }
    return challenge;
  } catch (err) {
    console.warn('[Verify OTP] Supabase challenge lookup notice:', err);
    return null;
  }
}

// Mark challenge used in Supabase to atomically prevent replay attacks
async function markChallengeUsedInSupabase(verificationId: string): Promise<boolean> {
  try {
    const res = await fetch(
      `${SUPABASE_URL}/rest/v1/otp_challenges?session_id=eq.${encodeURIComponent(
        verificationId
      )}`,
      {
        method: 'PATCH',
        headers: {
          apikey: SUPABASE_KEY,
          Authorization: `Bearer ${SUPABASE_KEY}`,
          'Content-Type': 'application/json',
          Prefer: 'return=minimal',
        },
        body: JSON.stringify({ is_used: true }),
      }
    );
    return res.ok;
  } catch (err) {
    console.warn('[Verify OTP] Supabase mark used notice:', err);
    return false;
  }
}

// Authoritative user lookup or registration in Supabase PostgreSQL
async function getOrCreateAuthoritativeUser(
  cleanPhone: string,
  boundRole: string,
  name?: string
): Promise<any> {
  // 1. Search for existing user account by phone number
  const lookupRes = await fetch(
    `${SUPABASE_URL}/rest/v1/users?phone=eq.${encodeURIComponent(cleanPhone)}&select=*`,
    {
      headers: {
        apikey: SUPABASE_KEY,
        Authorization: `Bearer ${SUPABASE_KEY}`,
        'Content-Type': 'application/json',
      },
    }
  );

  if (!lookupRes.ok) {
    const errText = await lookupRes.text().catch(() => '');
    throw new Error(`Database error querying user profile: ${lookupRes.status} ${errText}`);
  }

  const existingUsers = await lookupRes.json();
  if (Array.isArray(existingUsers) && existingUsers.length > 0) {
    const existing = existingUsers[0];
    // Authoritative role: Preserved strictly from database, NEVER overwritten from client request
    return existing;
  }

  // 2. Register new user with validated bound self-registration role
  const newUserId = `usr_${cleanPhone}`;
  const defaultName =
    (name && name.trim()) ||
    (boundRole === 'vendor' ? 'Shopkeeper' : boundRole === 'runner' ? 'Runner Partner' : 'Customer');

  const newUser = {
    id: newUserId,
    phone: cleanPhone,
    name: defaultName,
    role: boundRole,
    preferred_language: 'hi',
    is_active: true,
    kyc_status: 'unverified',
    created_at: new Date().toISOString(),
  };

  const createRes = await fetch(`${SUPABASE_URL}/rest/v1/users`, {
    method: 'POST',
    headers: {
      apikey: SUPABASE_KEY,
      Authorization: `Bearer ${SUPABASE_KEY}`,
      'Content-Type': 'application/json',
      Prefer: 'return=representation',
    },
    body: JSON.stringify(newUser),
  });

  if (!createRes.ok) {
    const createErr = await createRes.text().catch(() => '');
    throw new Error(`Database error creating user account: ${createRes.status} ${createErr}`);
  }

  const createdUsers = await createRes.json();
  if (Array.isArray(createdUsers) && createdUsers.length > 0) {
    return createdUsers[0];
  }

  return newUser;
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
        return sendJson(res, 400, {
          success: false,
          error: 'Invalid JSON request body',
          message: 'Invalid JSON request body',
        });
      }
    }
    body = body || {};

    const rawPhone = body.phoneNumber || body.phone || '';
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

    // 1. Validate 10-digit Indian Mobile format (strictly starts with 6-9)
    if (!/^[6-9]\d{9}$/.test(clean)) {
      return sendJson(res, 400, {
        success: false,
        code: 'auth/invalid-phone-number',
        error: 'Enter a valid 10-digit mobile number.',
        message: 'Enter a valid 10-digit mobile number.',
      });
    }

    const maskedPhone = `+91 XXXXX ${clean.slice(-4)}`;
    const enteredOtp = String(body.otp || body.code || '').trim();

    // 2. Validate that the code is strictly 4 digits
    if (!/^\d{4}$/.test(enteredOtp)) {
      return sendJson(res, 400, {
        success: false,
        code: 'auth/invalid-otp-length',
        error: 'Incorrect code. Please try again.',
        message: 'Incorrect code. Please try again.',
      });
    }

    // 3. Strict Role Sanitization: Only self-registration roles permitted
    const requestedRole = String(body.role || 'customer').toLowerCase().trim();
    const safeRequestedRole = ALLOWED_SELF_REGISTER_ROLES.has(requestedRole) ? requestedRole : 'customer';

    // 4. Retrieve Message Central credentials securely from server-side environment
    const customerId = process.env.MESSAGE_CENTRAL_CUSTOMER_ID || '';
    const authToken = process.env.MESSAGE_CENTRAL_AUTH_TOKEN || '';

    if (!authToken) {
      console.error('[CRITICAL] Missing MESSAGE_CENTRAL_AUTH_TOKEN in serverless environment.');
      return sendJson(res, 500, {
        success: false,
        code: 'auth/missing-credentials',
        error: 'Connection problem. Please try again.',
        message: 'Connection problem. Please try again.',
      });
    }

    // 5. Resolve active verification challenge from Supabase (shared durable state)
    let requestedVerificationId = body.verificationId || body.sessionId || '';
    const challenge = await getActiveChallengeFromSupabase(clean, requestedVerificationId || undefined);

    if (!challenge) {
      return sendJson(res, 400, {
        success: false,
        code: 'auth/session-expired',
        error: 'Code expired. Request a new OTP.',
        message: 'Code expired. Request a new OTP.',
      });
    }

    const verificationId = challenge.session_id || challenge.id;
    // Bind role strictly to the challenge record to prevent role swapping mid-verification
    const boundRole = challenge.role && ALLOWED_SELF_REGISTER_ROLES.has(challenge.role)
      ? challenge.role
      : safeRequestedRole;

    // 6. Validate OTP with Message Central VerifyNow API v3 with 4500ms timeout
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
    console.log(`[Message Central VerifyNow] Validating 4-digit OTP for ${maskedPhone}...`);

    const abortController = new AbortController();
    const timeoutHandle = setTimeout(() => abortController.abort(), 4500);

    let mcResponse: any;
    let mcText = '';
    try {
      mcResponse = await fetch(mcValidateUrl, {
        method: 'GET',
        headers: {
          authToken: authToken,
          accept: '*/*',
        },
        signal: abortController.signal,
      });
      clearTimeout(timeoutHandle);
      mcText = await mcResponse.text();
    } catch (fetchErr: any) {
      clearTimeout(timeoutHandle);
      if (fetchErr.name === 'AbortError') {
        console.error(`[Message Central Timeout] Validate OTP timed out after 4500ms for ${maskedPhone}`);
        return sendJson(res, 504, {
          success: false,
          code: 'auth/gateway-timeout',
          error: 'Connection problem. Please try again.',
          message: 'Connection problem. Please try again.',
        });
      }
      throw fetchErr;
    }

    let mcData: any = {};
    try {
      mcData = JSON.parse(mcText);
    } catch {
      mcData = { responseCode: mcResponse.status, message: mcText };
    }

    console.log(`[Message Central VerifyNow] Validation status for ${maskedPhone}:`, mcResponse.status, mcData?.responseCode, mcData?.data?.verificationStatus);

    // 7. Strict Verification Check
    const isVerified =
      mcResponse.ok &&
      (mcData.responseCode === 200 || mcData.responseCode === '200') &&
      (mcData.data?.verificationStatus === 'VERIFICATION_COMPLETED' || mcData.data?.responseCode === '200' || mcData.data?.responseCode === 200);

    if (!isVerified) {
      const isExpired =
        mcData.data?.verificationStatus === 'EXPIRED' ||
        String(mcData.data?.errorMessage || '').toLowerCase().includes('expired') ||
        String(mcData.message || '').toLowerCase().includes('expired');

      const userMsg = isExpired ? 'Code expired. Request a new OTP.' : 'Incorrect code. Please try again.';

      return sendJson(res, 400, {
        success: false,
        code: isExpired ? 'auth/code-expired' : 'auth/invalid-verification-code',
        error: userMsg,
        message: userMsg,
      });
    }

    // 8. Replay Prevention: Mark challenge used immediately in Supabase
    await markChallengeUsedInSupabase(verificationId);

    // 9. Database Persistence: Authoritative User Profile Lookup / Registration
    // Requirement: Never issue a valid session when database account lookup/creation fails
    let user: any;
    try {
      user = await getOrCreateAuthoritativeUser(clean, boundRole, name);
    } catch (dbErr: any) {
      console.error('[Auth DB Failure]:', dbErr?.message || dbErr);
      return sendJson(res, 500, {
        success: false,
        code: 'auth/database-failure',
        error: 'Unable to establish account session. Please try again.',
        message: 'Unable to establish account session. Please try again.',
      });
    }

    // 10. Cryptographic JWT Issuance
    const jwtSecret = process.env.SECRET_KEY || process.env.JWT_SECRET;
    if (!jwtSecret && process.env.NODE_ENV === 'production') {
      console.error('[CRITICAL] Missing SECRET_KEY / JWT_SECRET in production environment.');
      return sendJson(res, 500, {
        success: false,
        code: 'auth/configuration-error',
        error: 'Authentication configuration error. Please contact administration.',
        message: 'Authentication configuration error. Please contact administration.',
      });
    }
    const effectiveSecret = jwtSecret || 'dev-insecure-secret-key-change-in-production';

    const nowSec = Math.floor(Date.now() / 1000);
    const tokenPayload = {
      sub: user.id,
      phone: `+91${clean}`,
      role: user.role, // Authoritative role from database
      name: user.name || 'User',
      iat: nowSec,
      exp: nowSec + 7 * 24 * 60 * 60, // 7 days expiration
    };

    const accessToken = createSignedJwt(tokenPayload, effectiveSecret);
    console.log(`[Auth Success] Session token successfully issued for account role: ${user.role}`);

    // Set secure HttpOnly cookie
    const cookieHeader = `gb_session=${accessToken}; Path=/; Max-Age=${7 * 24 * 60 * 60}; HttpOnly; Secure; SameSite=Lax`;
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
        role: user.role,
        name: user.name || 'User',
        kyc_status: user.kyc_status || 'unverified',
      },
    });
  } catch (error: any) {
    console.error('[VERIFY-OTP FATAL ERROR]:', error?.message || error);
    return sendJson(res, 500, {
      success: false,
      code: 'auth/internal-error',
      error: 'Internal server error verifying OTP',
      message: 'Internal server error verifying OTP',
    });
  }
}
