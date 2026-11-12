import React, { useState, useEffect } from 'react';
import { resolveAppTarget, isCustomerAuthenticated, type AppTarget } from './utils/subdomain';
import { AdminApp } from './AdminApp';
import { CustomerPortal } from './components/CustomerPortal';
import { VendorPortal } from './components/VendorPortal';
import { RunnerPortal } from './components/RunnerPortal';
import { SplashScreen } from './components/SplashScreen';
import { LanguageSelectionScreen } from './components/LanguageSelectionScreen';
import { MobileLogin } from './components/MobileLogin';
import { PullToRefresh } from './components/PullToRefresh';

/**
 * Root Subdomain Router for Apna GaonBazaar Multi-App Platform
 *
 * Routing Matrix:
 * - / (Root Route)           -> Branded Green Splash Screen (<SplashScreen />), auto-navigates to /language (or directly to customer if authenticated)
 * - /language                -> Bilingual Language Selection Screen (<LanguageSelectionScreen />), navigates to /login
 * - /login                   -> Customer Mobile Login with 6-Digit OTP (<MobileLogin />)
 * - admin.apnagaonbazaar.in  -> Super Admin Command Center (<AdminApp />)
 * - dukaan.apnagaonbazaar.in -> GaonBazaar Dukaan Vendor Portal (<VendorPortal />)
 * - mitra.apnagaonbazaar.in  -> Gaon Mitra Runner Delivery App (<RunnerPortal />)
 * - apnagaonbazaar.in        -> Root Splash Screen / Customer App (<CustomerPortal />)
 * - Fallback (localhost/etc) -> Splash on `/`, Language on `/language`, Login on `/login`, or Customer App
 */
export function App() {
  const resolveTargetSafely = (): AppTarget => {
    const rawTarget = resolveAppTarget(
      typeof window !== 'undefined' ? window.location.hostname : '',
      typeof window !== 'undefined' ? window.location.search : '',
      typeof window !== 'undefined' ? window.location.pathname : ''
    );
    // If the customer has already authenticated, bypass onboarding screens on visit or refresh
    if (isCustomerAuthenticated()) {
      if (rawTarget === 'splash' || rawTarget === 'language' || rawTarget === 'login') {
        return 'customer';
      }
    }
    return rawTarget;
  };

  const [target, setTarget] = useState<AppTarget>(resolveTargetSafely);

  useEffect(() => {
    const handleLocationChange = () => {
      setTarget(resolveTargetSafely());
    };

    window.addEventListener('popstate', handleLocationChange);
    return () => window.removeEventListener('popstate', handleLocationChange);
  }, []);

  const isLocalDev =
    typeof window !== 'undefined' &&
    (window.location.hostname === 'localhost' ||
      window.location.hostname === '127.0.0.1' ||
      window.location.hostname.endsWith('.local'));

  const navigateTo = (app: AppTarget) => {
    const path = app === 'splash' ? '/' : `/${app}`;
    window.history.pushState({}, '', path);
    setTarget(app);
  };

  const switchApp = (app: AppTarget) => {
    const url = new URL(window.location.href);
    url.searchParams.set('app', app);
    window.history.pushState({}, '', url.toString());
    setTarget(app);
  };

  return (
    <PullToRefresh>
      {/* 1. Branded Green Splash Screen as Default Root Route (/) */}
      {target === 'splash' && (
        <SplashScreen
          destination={isCustomerAuthenticated() ? '/customer' : '/language'}
          durationMs={2200}
          onFinish={() => navigateTo(isCustomerAuthenticated() ? 'customer' : 'language')}
        />
      )}

      {/* 2. Language Selection Screen (/language) */}
      {target === 'language' && (
        <LanguageSelectionScreen
          destination="/login"
          onSelect={() => navigateTo('login')}
        />
      )}

      {/* 3. Customer Mobile Login (/login) - Native Edge-to-Edge Responsive Layout */}
      {target === 'login' && (
        <MobileLogin
          title="Mobile Login"
          subtitle="Enter your mobile number to receive a secure 6-digit OTP."
          onSuccess={(user) => {
            console.log('[Auth] User successfully authenticated:', user);
            navigateTo('customer');
          }}
        />
      )}

      {/* Dynamic Subdomain Component Rendering */}
      {target === 'admin' && <AdminApp />}
      {target === 'dukaan' && <VendorPortal />}
      {target === 'mitra' && <RunnerPortal />}
      {target === 'customer' && <CustomerPortal />}

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
            onClick={() => switchApp('splash')}
            className={`px-2 py-1 rounded transition-colors font-medium ${
              target === 'splash'
                ? 'bg-[#0F9D58] text-white font-semibold'
                : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
            }`}
          >
            Splash (Root /)
          </button>
          <button
            type="button"
            onClick={() => switchApp('language')}
            className={`px-2 py-1 rounded transition-colors font-medium ${
              target === 'language'
                ? 'bg-purple-600 text-white font-semibold'
                : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
            }`}
          >
            Language (/language)
          </button>
          <button
            type="button"
            onClick={() => switchApp('login')}
            className={`px-2 py-1 rounded transition-colors font-medium ${
              target === 'login'
                ? 'bg-blue-600 text-white font-semibold'
                : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
            }`}
          >
            Login (/login)
          </button>
          <button
            type="button"
            onClick={() => switchApp('customer')}
            className={`px-2 py-1 rounded transition-colors font-medium ${
              target === 'customer'
                ? 'bg-emerald-600 text-white font-semibold'
                : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
            }`}
          >
            Customer
          </button>
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
