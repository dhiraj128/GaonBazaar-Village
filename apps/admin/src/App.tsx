import React, { useState, useEffect } from 'react';
import { resolveAppTarget, type AppTarget } from './utils/subdomain';
import { AdminApp } from './AdminApp';
import { CustomerPortal } from './components/CustomerPortal';
import { VendorPortal } from './components/VendorPortal';
import { RunnerPortal } from './components/RunnerPortal';
import { PullToRefresh } from './components/PullToRefresh';

/**
 * Root Subdomain Router for Apna GaonBazaar Multi-App Platform
 * Customer entry routes (/, /language, /login, /customer) all mount the
 * SAME customer application, which owns its language -> OTP -> dashboard flow.
 * Admin, vendor and runner domains keep their existing independent portals.
 */
export function App() {
  const [target, setTarget] = useState<AppTarget>(() =>
    resolveAppTarget(
      typeof window !== 'undefined' ? window.location.hostname : '',
      typeof window !== 'undefined' ? window.location.search : '',
      typeof window !== 'undefined' ? window.location.pathname : ''
    )
  );

  useEffect(() => {
    const handleLocationChange = () => {
      setTarget(resolveAppTarget(window.location.hostname, window.location.search, window.location.pathname));
    };

    window.addEventListener('popstate', handleLocationChange);
    return () => window.removeEventListener('popstate', handleLocationChange);
  }, []);

  const isLocalDev =
    typeof window !== 'undefined' &&
    (window.location.hostname === 'localhost' ||
      window.location.hostname === '127.0.0.1' ||
      window.location.hostname.endsWith('.local'));

  const switchApp = (app: AppTarget) => {
    const url = new URL(window.location.href);
    url.searchParams.set('app', app);
    window.history.pushState({}, '', url.toString());
    setTarget(app);
  };

  return (
    <PullToRefresh>
      {/* One customer application owns language selection, OTP and dashboard.
          Do not mount a second React onboarding flow before the customer iframe. */}
      {(['splash', 'language', 'login', 'customer'] as AppTarget[]).includes(target) && (
        <CustomerPortal />
      )}

      {/* Dynamic Subdomain Component Rendering */}
      {target === 'admin' && <AdminApp />}
      {target === 'dukaan' && <VendorPortal />}
      {target === 'mitra' && <RunnerPortal />}

      {/* Local Development Quick Switcher — only visible on localhost/127.0.0.1 */}
      {isLocalDev && (
        <aside
          aria-label="Local Development Subdomain Switcher"
          className="fixed bottom-3 right-3 z-[9999] bg-slate-900/95 border border-slate-700/80 rounded-xl px-3 py-2 text-xs shadow-2xl backdrop-blur-md text-slate-300 flex items-center gap-2"
        >
          <span className="font-mono text-emerald-400 font-semibold uppercase tracking-wider text-[10px]">
            Dev Switcher:
          </span>
          <button
            type="button"
            onClick={() => switchApp('dukaan')}
            className={`px-2 py-1 rounded transition-colors font-medium ${
              target === 'dukaan'
                ? 'bg-amber-600 text-white font-semibold'
                : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
            }`}
          >
            Vendor (Dukaan)
          </button>
          <button
            type="button"
            onClick={() => switchApp('mitra')}
            className={`px-2 py-1 rounded transition-colors font-medium ${
              target === 'mitra'
                ? 'bg-cyan-600 text-white font-semibold'
                : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
            }`}
          >
            Runner (Mitra)
          </button>
          <button
            type="button"
            onClick={() => switchApp('admin')}
            className={`px-2 py-1 rounded transition-colors font-medium ${
              target === 'admin'
                ? 'bg-red-600 text-white font-semibold'
                : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
            }`}
          >
            Super Admin
          </button>
        </aside>
      )}
    </PullToRefresh>
  );
}

export default App;
