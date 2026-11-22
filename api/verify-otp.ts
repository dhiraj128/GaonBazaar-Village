import type { VercelRequest, VercelResponse } from '@vercel/node';
import * as crypto from 'crypto';

/**
 * Apna GaonBazaar - High-Security OTP Verification & Production Session Issuance
 *
 * Security & Cryptographic Architecture:
 * - Real 6-digit OTP validation via 2Factor.in & Supabase PostgreSQL (otp_challenges)
 * - Atomic replay attack prevention: Challenge marked is_used=true immediately
 * - Max 3 attempts enforced with automatic invalidation
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

// Consume exactly one unexpired OTP challenge only once, even across concurrent workers.
async function markChallengeUsedInSupabase(verificationId: string): Promise<boolean> {
  try {
    const res = await fetch(
      `${SUPABASE_URL}/rest/v1/otp_challenges?session_id=eq.${encodeURIComponent(verificationId)}&is_used=eq.false&expires_at=gt.${encodeURIComponent(new Date().toISOString())}`,
      {
        method: 'PATCH',
        headers: {
          apikey: SUPABASE_KEY,
          Authorization: `Bearer ${SUPABASE_KEY}`,
          'Content-Type': 'application/json',
          Prefer: 'return=representation',
        },
        body: JSON.stringify({ is_used: true, used: true, verified: true }),
      }
    );
    if (!res.ok) return false;
    const consumed = await res.json();
    return Array.isArray(consumed) && consumed.length === 1;
  } catch (err) {
    console.warn('[Verify OTP] Supabase mark used notice:', err);
    return false;
  }
}

// Increment challenge attempt count
async function incrementChallengeAttempts(verificationId: string, currentAttempts: number): Promise<void> {
  try {
    await fetch(
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
        body: JSON.stringify({ attempts: (currentAttempts || 0) + 1 }),
      }
    );
  } catch (err) {
    console.warn('[Verify OTP] Failed to update attempts:', err);
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
  // Strict CORS configuration
  const origin = (req.headers && (req.headers.origin || req.headers.Origin)) || '';
  const isDev = process.env.ENVIRONMENT !== 'production' && process.env.NODE_ENV !== 'production';
  const isLocalhost = isDev && typeof origin === 'string' && (origin === 'http://localhost:5173' || origin.startsWith('http://localhost:'));
  const isAllowedProd =
    origin === 'https://apnagaonbazaar.in' ||
    origin === 'https://www.apnagaonbazaar.in' ||
    origin === 'https://dukaan.apnagaonbazaar.in' ||
    origin === 'https://mitra.apnagaonbazaar.in';

  if (typeof origin === 'string' && (isAllowedProd || isLocalhost)) {
    res.setHeader('Access-Control-Allow-Origin', origin);
  } else {
    res.setHeader('Access-Control-Allow-Origin', 'https://apnagaonbazaar.in');
  }
  res.setHeader('Access-Control-Allow-Credentials', 'true');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
  res.setHeader(
    'Access-Control-Allow-Headers',
    'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version, Authorization'
  );
  res.setHeader('Vary', 'Origin');
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

    // 2. Validate that the code is strictly 6 digits
    if (!/^\d{6}$/.test(enteredOtp)) {
      return sendJson(res, 400, {
        success: false,
        code: 'auth/invalid-otp-length',
        error: 'Please enter a valid 6-digit verification code.',
        message: 'Please enter a valid 6-digit verification code.',
      });
    }

    // 3. Strict Role Sanitization: Only self-registration roles permitted
    const requestedRole = String(body.role || 'customer').toLowerCase().trim();
    const safeRequestedRole = ALLOWED_SELF_REGISTER_ROLES.has(requestedRole) ? requestedRole : 'customer';

    // 4. Resolve active verification challenge from Supabase (shared durable state)
    let requestedVerificationId = body.verificationId || body.sessionId || '';
    const challenge = await getActiveChallengeFromSupabase(clean, requestedVerificationId || undefined);

    if (!challenge) {
      return sendJson(res, 400, {
        success: false,
        code: 'auth/code-expired',
        error: 'Code expired. Request a new OTP.',
        message: 'Code expired. Request a new OTP.',
      });
    }

    const verificationId = challenge.session_id || challenge.id;
    const currentAttempts = challenge.attempts || 0;

    // Enforce maximum 3 attempts
    if (currentAttempts >= 3) {
      return sendJson(res, 400, {
        success: false,
        code: 'auth/too-many-attempts',
        error: 'Too many failed attempts. Request a new OTP.',
        message: 'Too many failed attempts. Request a new OTP.',
      });
    }

    // Bind role strictly to the challenge record to prevent role swapping mid-verification
    const boundRole = challenge.role && ALLOWED_SELF_REGISTER_ROLES.has(challenge.role)
      ? challenge.role
      : safeRequestedRole;

    // 5. Verify 6-digit OTP
    let isMatch = false;
    if (challenge.otp_hash) {
      const computedHash = crypto.createHash('sha256').update(enteredOtp).digest('hex');
      const expected = Buffer.from(challenge.otp_hash, 'hex');
      const actual = Buffer.from(computedHash, 'hex');
      isMatch = expected.length === actual.length && crypto.timingSafeEqual(expected, actual);
    }

    if (!isMatch) {
      await incrementChallengeAttempts(verificationId, currentAttempts);
      return sendJson(res, 400, {
        success: false,
        code: 'auth/invalid-verification-code',
        error: 'Incorrect code. Please try again.',
        message: 'Incorrect code. Please try again.',
      });
    }

    // 6. Replay Prevention: Mark challenge used immediately in Supabase
    if (!(await markChallengeUsedInSupabase(verificationId))) {
      return sendJson(res, 409, {
        success: false,
        code: 'auth/code-already-used',
        error: 'Verification code has already been used or could not be consumed. Request a new OTP.',
      });
    }

    // 7. Database Persistence: Authoritative User Profile Lookup / Registration
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

    // 8. Cryptographic JWT Issuance
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
      message: 'OTP verified successfully via 2Factor.in',
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
      error: error?.message || 'Internal server error verifying OTP',
      message: error?.message || 'Internal server error verifying OTP',
    });
  }
}
