import type { VercelRequest, VercelResponse } from '@vercel/node';

/**
 * Apna GaonBazaar - High-Speed Real SMS OTP Dispatch via Message Central VerifyNow API
 *
 * Security & Reliability Architecture:
 * - Direct carrier delivery via Message Central VerifyNow API v3
 * - Durable rate limiting (30s cooldown) backed by Supabase PostgreSQL (otp_challenges)
 * - Cross-serverless instance synchronization (Zero dependence on volatile in-memory Map)
 * - Strict role validation: Only self-registration roles permitted ('customer', 'vendor', 'runner')
 * - Full PII masking in serverless logs (No raw phone numbers or credentials logged)
 * - Guaranteed challenge persistence before response
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
    console.error('[Send OTP sendJson error]:', e);
  }
}

// Durable Rate Limit Check: Query Supabase for latest challenge for this phone
async function checkDurableRateLimit(cleanPhone: string): Promise<{ limited: boolean; waitSeconds: number }> {
  try {
    const res = await fetch(
      `${SUPABASE_URL}/rest/v1/otp_challenges?phone=eq.${encodeURIComponent(
        cleanPhone
      )}&order=created_at.desc&limit=1`,
      {
        headers: {
          apikey: SUPABASE_KEY,
          Authorization: `Bearer ${SUPABASE_KEY}`,
          'Content-Type': 'application/json',
        },
      }
    );

    if (res.ok) {
      const records = await res.json();
      if (Array.isArray(records) && records.length > 0) {
        const lastCreatedAt = new Date(records[0].created_at).getTime();
        const elapsed = Date.now() - lastCreatedAt;
        if (elapsed < 30 * 1000) {
          const waitSeconds = Math.ceil((30 * 1000 - elapsed) / 1000);
          return { limited: true, waitSeconds };
        }
      }
    }
  } catch (err) {
    console.warn('[Send OTP] Rate limit query notice:', err);
  }
  return { limited: false, waitSeconds: 0 };
}

// Store verification challenge in Supabase PostgreSQL table
async function saveChallengeToSupabase(record: {
  id: string;
  phone: string;
  session_id: string;
  role: string;
  expires_at: string;
}): Promise<boolean> {
  try {
    const res = await fetch(`${SUPABASE_URL}/rest/v1/otp_challenges`, {
      method: 'POST',
      headers: {
        apikey: SUPABASE_KEY,
        Authorization: `Bearer ${SUPABASE_KEY}`,
        'Content-Type': 'application/json',
        Prefer: 'resolution=merge-duplicates',
      },
      body: JSON.stringify({
        id: record.id,
        phone: record.phone,
        session_id: record.session_id,
        otp_hash: 'VERIFYNOW',
        role: record.role,
        attempts: 0,
        is_used: false,
        expires_at: record.expires_at,
        created_at: new Date().toISOString(),
      }),
    });
    return res.ok;
  } catch (err) {
    console.error('[Send OTP] Supabase challenge persistence exception:', err);
    return false;
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

    // 1. Validate 10-digit Indian Mobile format (strictly starts with 6-9)
    if (!/^[6-9]\d{9}$/.test(clean)) {
      return sendJson(res, 400, {
        success: false,
        code: 'auth/invalid-phone-number',
        error: 'Enter a valid 10-digit mobile number.',
        message: 'Enter a valid 10-digit mobile number.',
      });
    }

    // Masked phone for compliant logging (PII protection)
    const maskedPhone = `+91 XXXXX ${clean.slice(-4)}`;

    // 2. Strict Role Sanitization: Never allow untrusted escalation to 'admin' / 'super_admin'
    const requestedRole = String(body.role || 'customer').toLowerCase().trim();
    const safeRole = ALLOWED_SELF_REGISTER_ROLES.has(requestedRole) ? requestedRole : 'customer';

    // 3. Durable Rate Limiting: 30-second cooldown per phone number via shared PostgreSQL state
    const rateLimit = await checkDurableRateLimit(clean);
    if (rateLimit.limited) {
      return sendJson(res, 429, {
        success: false,
        code: 'auth/too-many-requests',
        error: `Please wait ${rateLimit.waitSeconds}s before requesting another OTP.`,
        message: `Please wait ${rateLimit.waitSeconds}s before requesting another OTP.`,
        retryAfter: rateLimit.waitSeconds,
      });
    }

    // 4. Retrieve Message Central credentials securely from server-side environment
    const customerId = process.env.MESSAGE_CENTRAL_CUSTOMER_ID || '';
    const authToken = process.env.MESSAGE_CENTRAL_AUTH_TOKEN || '';

    if (!authToken) {
      console.error('[CRITICAL] Missing MESSAGE_CENTRAL_AUTH_TOKEN in serverless environment.');
      return sendJson(res, 500, {
        success: false,
        code: 'auth/missing-credentials',
        error: "Couldn't send the code. Please try again.",
        message: "Couldn't send the code. Please try again.",
      });
    }

    // 5. Dispatch real 4-digit SMS OTP via Message Central VerifyNow API v3 with 4500ms timeout
    const params = new URLSearchParams({
      countryCode: '91',
      flowType: 'SMS',
      mobileNumber: clean,
      otpLength: '4',
    });
    if (customerId) {
      params.append('customerId', customerId);
    }

    const mcSendUrl = `https://cpaas.messagecentral.com/verification/v3/send?${params.toString()}`;
    console.log(`[Message Central VerifyNow] Dispatching 4-digit OTP to ${maskedPhone}...`);

    const abortController = new AbortController();
    const timeoutHandle = setTimeout(() => abortController.abort(), 4500);

    let mcResponse: any;
    let mcText = '';
    try {
      mcResponse = await fetch(mcSendUrl, {
        method: 'POST',
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
        console.error(`[Message Central Timeout] Send OTP request timed out after 4500ms for ${maskedPhone}`);
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

    console.log(`[Message Central VerifyNow] Send response status for ${maskedPhone}:`, mcResponse.status, mcData?.responseCode);

    // 6. Handle provider response
    if (!mcResponse.ok || (mcData.responseCode !== 200 && mcData.responseCode !== '200') || !mcData.data?.verificationId) {
      const errDetail =
        mcData.data?.errorMessage ||
        mcData.message ||
        mcData?.error ||
        `Message Central returned status ${mcResponse.status}`;

      console.error(`[Message Central VerifyNow Delivery Failure]:`, errDetail);
      return sendJson(res, 502, {
        success: false,
        code: 'auth/sms-delivery-failed',
        error: "Couldn't send the code. Please try again.",
        message: "Couldn't send the code. Please try again.",
        providerStatus: mcData?.responseCode || mcResponse.status,
      });
    }

    const verificationId = String(mcData.data.verificationId);
    const expiresAt = Date.now() + 5 * 60 * 1000; // 5-minute validity

    // 7. Durably Persist Verification Challenge to Supabase
    // Requirement: Must await durable insert to prevent lost verification sessions across serverless instances
    const saved = await saveChallengeToSupabase({
      id: verificationId,
      phone: clean,
      session_id: verificationId,
      role: safeRole,
      expires_at: new Date(expiresAt).toISOString(),
    });

    if (!saved) {
      console.error(`[Send OTP] Failed to save verification challenge for ${maskedPhone} to Supabase`);
      return sendJson(res, 502, {
        success: false,
        code: 'auth/storage-failed',
        error: "Failed to persist verification challenge. Please try again.",
        message: "Failed to persist verification challenge. Please try again.",
      });
    }

    // 8. Respond with success and verificationId
    return sendJson(res, 200, {
      success: true,
      message: '4-digit SMS OTP dispatched successfully via Message Central VerifyNow',
      verificationId: verificationId,
      phoneNumber: clean,
    });
  } catch (error: any) {
    console.error('[SEND-OTP FATAL ERROR]:', error?.message || error);
    return sendJson(res, 500, {
      success: false,
      code: 'auth/internal-error',
      error: 'Internal server error dispatching OTP',
      message: 'Internal server error dispatching OTP',
    });
  }
}
