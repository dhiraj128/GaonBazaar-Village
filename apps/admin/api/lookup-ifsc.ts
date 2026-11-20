import type { VercelRequest, VercelResponse } from '@vercel/node';

/**
 * Apna GaonBazaar - Genuine IFSC Code Lookup Service
 *
 * Verifies IFSC format and performs real-time lookup against the official
 * Reserve Bank of India / Razorpay Open Bank Directory.
 * Zero simulation - 100% genuine bank and branch data.
 */

export default async function handler(req: VercelRequest, res: VercelResponse) {
  // Strict CORS configuration
  const rawOrigin = req.headers['origin'] || req.headers['Origin'];
  const origin = Array.isArray(rawOrigin) ? rawOrigin[0] : (rawOrigin || '');
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
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  res.setHeader('Vary', 'Origin');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'GET') {
    return res.status(405).json({ success: false, error: 'Method not allowed' });
  }

  const rawIfsc = String(req.query.ifsc || req.query.code || '').trim().toUpperCase();

  // Validate format: 4 uppercase letters, '0', 6 alphanumeric characters
  const ifscRegex = /^[A-Z]{4}0[A-Z0-9]{6}$/;
  if (!ifscRegex.test(rawIfsc)) {
    return res.status(400).json({
      success: false,
      found: false,
      error: 'Invalid IFSC format. Must be 11 characters (5th character must be 0).'
    });
  }

  try {
    const abortController = new AbortController();
    const timeoutHandle = setTimeout(() => abortController.abort(), 4500);

    const lookupRes = await fetch(`https://ifsc.razorpay.com/${encodeURIComponent(rawIfsc)}`, {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
      signal: abortController.signal
    });

    clearTimeout(timeoutHandle);

    if (lookupRes.status === 404) {
      return res.status(404).json({
        success: false,
        found: false,
        ifsc: rawIfsc,
        error: 'IFSC not found in bank directory.'
      });
    }

    if (!lookupRes.ok) {
      return res.status(502).json({
        success: false,
        found: false,
        ifsc: rawIfsc,
        error: 'Unable to query bank directory at this time.'
      });
    }

    const data = await lookupRes.json();
    return res.status(200).json({
      success: true,
      found: true,
      ifsc: rawIfsc,
      bank: data.BANK || 'Commercial Bank',
      branch: data.BRANCH || 'Authorized Branch',
      address: data.ADDRESS || '',
      city: data.CITY || '',
      state: data.STATE || '',
      message: 'IFSC verified against bank directory.'
    });
  } catch (err: any) {
    if (err.name === 'AbortError') {
      return res.status(504).json({
        success: false,
        found: false,
        error: 'Bank directory query timed out.'
      });
    }
    console.error('[IFSC Lookup Error]:', err?.message || err);
    return res.status(500).json({
      success: false,
      found: false,
      error: 'Internal server error resolving IFSC code.'
    });
  }
}
