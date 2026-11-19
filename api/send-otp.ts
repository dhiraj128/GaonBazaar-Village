// Cross-invocation in-memory cache for Vercel functions
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
    console.error('[Send OTP sendJson error]:', e);
  }
};

// Store verification challenge in Supabase PostgreSQL table
async function saveChallengeToSupabase(record: {
  id: string;
  phone: string;
  session_id: string;
  role: string;
  expires_at: string;
}) {
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

    await fetch(`${supabaseUrl}/rest/v1/otp_challenges`, {
      method: 'POST',
      headers: {
        apikey: supabaseKey,
        Authorization: `Bearer ${supabaseKey}`,
        'Content-Type': 'application/json',
        Prefer: 'resolution=merge-duplicates',
      },
      body: JSON.stringify({
        id: record.id,
        phone: record.phone,
        session_id: record.session_id,
        otp_hash: 'VERIFYNOW',
        role: record.role || 'customer',
        attempts: 0,
        is_used: false,
        expires_at: record.expires_at,
        created_at: new Date().toISOString(),
      }),
    });
  } catch (err) {
    console.warn('[Send OTP] Supabase challenge sync notice:', err);
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
        console.error('[Send OTP Body Parse Error]:', pErr);
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
    let clean = String(rawPhone || '').replace(/[^\d+]/g, '').trim();
    if (clean.startsWith('+91')) {
      clean = clean.slice(3);
    } else if (clean.startsWith('91') && clean.length === 12) {
      clean = clean.slice(2);
    } else if (clean.startsWith('0') && clean.length === 11) {
      clean = clean.slice(1);
    }
    clean = clean.replace(/\D/g, '');

    // Validate 10-digit Indian Mobile format (strictly starts with 6-9)
    // No hardcoded numbers or static bypasses allowed
    if (!/^[6-9]\d{9}$/.test(clean)) {
      return sendJson(res, 400, {
        success: false,
        code: 'auth/invalid-phone-number',
        error: 'Enter a valid 10-digit mobile number.',
        message: 'Enter a valid 10-digit mobile number.',
      });
    }

    // Rate Limiting: 30-second cooldown per phone number
    const now = Date.now();
    const cachedRecord = getOtpCache().get(clean);
    if (cachedRecord && now - cachedRecord.lastSentAt < 30 * 1000) {
      const waitSeconds = Math.ceil((30 * 1000 - (now - cachedRecord.lastSentAt)) / 1000);
      return sendJson(res, 429, {
        success: false,
        code: 'auth/too-many-requests',
        error: `Please wait ${waitSeconds}s before requesting another OTP.`,
        message: `Please wait ${waitSeconds}s before requesting another OTP.`,
        retryAfter: waitSeconds,
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
        error: "Couldn't send the code. Please try again.",
        message: "Couldn't send the code. Please try again.",
      });
    }

    // Step 2: Dispatch real 4-digit SMS OTP via Message Central VerifyNow API v3 with 4500ms timeout
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
    console.log(`[Message Central VerifyNow] Dispatching 4-digit OTP to +91${clean}...`);

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
        console.error(`[Message Central Timeout] Send OTP request timed out after 4500ms for +91${clean}`);
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

    console.log(`[Message Central VerifyNow] Send response status for +91${clean}:`, mcResponse.status, mcData?.responseCode);

    // Step 3: Handle provider response
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
    const expiresAt = now + 5 * 60 * 1000; // 5-minute validity

    // Step 4: Persist verification session across memory cache immediately
    getOtpCache().set(clean, {
      verificationId,
      expiresAt,
      lastSentAt: now,
      attempts: 0,
    });

    // Fire challenge persistence to Supabase non-blockingly (max 350ms race to avoid blocking HTTP response)
    Promise.race([
      saveChallengeToSupabase({
        id: verificationId,
        phone: clean,
        session_id: verificationId,
        role: role,
        expires_at: new Date(expiresAt).toISOString(),
      }),
      new Promise((resolve) => setTimeout(resolve, 350)),
    ]).catch((err) => {
      console.warn('[Send OTP] Async challenge sync notice:', err);
    });

    // Step 5: Respond immediately with success and verificationId
    return sendJson(res, 200, {
      success: true,
      message: '4-digit SMS OTP dispatched successfully via Message Central VerifyNow',
      verificationId: verificationId,
      phoneNumber: clean,
    });
  } catch (error: any) {
    console.error('[SEND-OTP FATAL ERROR]:', error);
    return sendJson(res, 500, {
      success: false,
      code: 'auth/internal-error',
      error: error?.message || 'Internal server error dispatching OTP',
      message: error?.message || 'Internal server error dispatching OTP',
    });
  }
}
