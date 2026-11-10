export type AppTarget = 'admin' | 'dukaan' | 'mitra' | 'customer';

/**
 * Resolves which GaonBazaar application to render based on the current hostname,
 * search parameters, and pathname.
 *
 * Strict Rendering Hierarchy:
 * 1. Explicit query param override (e.g. `?app=admin`, `?app=dukaan`, `?app=mitra`, `?app=customer`)
 *    Enables developer switching and integration testing on any environment.
 * 2. Explicit pathname prefix (e.g. `/admin`, `/dukaan`, `/vendor`, `/mitra`, `/runner`, `/customer`)
 * 3. Exact Subdomain / Hostname Matching:
 *    - `admin.apnagaonbazaar.in` (or starting with `admin.`) -> 'admin' (Super Admin Command Center)
 *    - `dukaan.apnagaonbazaar.in` (or starting with `dukaan.` or `vendor.`) -> 'dukaan' (GaonBazaar Dukaan Vendor Portal)
 *    - `mitra.apnagaonbazaar.in` (or starting with `mitra.` or `runner.`) -> 'mitra' (Gaon Mitra Runner Portal)
 *    - `apnagaonbazaar.in` or `www.apnagaonbazaar.in` -> 'customer' (Apna GaonBazaar Customer App)
 * 4. Fallback / Default:
 *    - Localhost, 127.0.0.1, Vercel preview domains, or any unrecognized host -> 'customer'
 *    - CRITICAL REQUIREMENT: Default fallback must NEVER be the Admin Panel.
 */
export function resolveAppTarget(
  hostname: string = typeof window !== 'undefined' ? window.location.hostname : '',
  search: string = typeof window !== 'undefined' ? window.location.search : '',
  pathname: string = typeof window !== 'undefined' ? window.location.pathname : ''
): AppTarget {
  const cleanHost = (hostname || '').toLowerCase().trim();
  const cleanPath = (pathname || '').toLowerCase().trim();

  // 1. Explicit query param override (?app=... or ?portal=...)
  try {
    const params = new URLSearchParams(search);
    const appQuery = (params.get('app') || params.get('portal') || '').toLowerCase().trim();
    if (appQuery === 'admin') return 'admin';
    if (appQuery === 'dukaan' || appQuery === 'vendor') return 'dukaan';
    if (appQuery === 'mitra' || appQuery === 'runner') return 'mitra';
    if (appQuery === 'customer') return 'customer';
  } catch {
    // Ignore URL parse errors
  }

  // 2. Explicit pathname prefix override
  if (cleanPath.startsWith('/admin')) {
    return 'admin';
  }
  if (cleanPath.startsWith('/dukaan') || cleanPath.startsWith('/vendor')) {
    return 'dukaan';
  }
  if (cleanPath.startsWith('/mitra') || cleanPath.startsWith('/runner')) {
    return 'mitra';
  }
  if (cleanPath.startsWith('/customer')) {
    return 'customer';
  }

  // 3. Exact Subdomain / Hostname Resolution
  // 3a. Admin Subdomain: admin.apnagaonbazaar.in (or admin.*)
  if (cleanHost === 'admin.apnagaonbazaar.in' || cleanHost.startsWith('admin.')) {
    return 'admin';
  }

  // 3b. Vendor Subdomain: dukaan.apnagaonbazaar.in (or dukaan.* / vendor.*)
  if (
    cleanHost === 'dukaan.apnagaonbazaar.in' ||
    cleanHost.startsWith('dukaan.') ||
    cleanHost.startsWith('vendor.')
  ) {
    return 'dukaan';
  }

  // 3c. Runner Subdomain: mitra.apnagaonbazaar.in (or mitra.* / runner.*)
  if (
    cleanHost === 'mitra.apnagaonbazaar.in' ||
    cleanHost.startsWith('mitra.') ||
    cleanHost.startsWith('runner.')
  ) {
    return 'mitra';
  }

  // 3d. Customer App: apnagaonbazaar.in or www.apnagaonbazaar.in
  if (cleanHost === 'apnagaonbazaar.in' || cleanHost === 'www.apnagaonbazaar.in') {
    return 'customer';
  }

  // 4. Default Fallback: Any unrecognized host (e.g. localhost, 127.0.0.1, preview URLs)
  // MUST ALWAYS DEFAULT TO CUSTOMER APP, NEVER ADMIN!
  return 'customer';
}
