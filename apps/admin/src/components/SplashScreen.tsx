import React, { useEffect } from 'react';

interface SplashScreenProps {
  onFinish?: () => void;
  destination?: string;
  durationMs?: number;
}

export function SplashScreen({
  onFinish,
  destination = '/language',
  durationMs = 2500,
}: SplashScreenProps) {
  useEffect(() => {
    // 1. Restore Language Selection Routing:
    // Flow: SplashScreen (2.5s delay) -> LanguageSelectionScreen -> MobileLoginScreen
    const timer = setTimeout(() => {
      if (onFinish) {
        onFinish();
      } else {
        window.history.pushState({}, '', destination);
        window.dispatchEvent(new PopStateEvent('popstate'));
      }
    }, durationMs);

    return () => clearTimeout(timer);
  }, [onFinish, destination, durationMs]);

  return (
    <div
      role="region"
      aria-label="GaonBazaar Splash Screen"
      className="fixed inset-0 min-h-screen w-full flex flex-col items-center justify-center bg-[#0F9D58] text-white z-50 select-none overflow-hidden"
    >
      {/* Subtle Background Glow Orbs */}
      <div className="absolute -top-32 -left-32 w-96 h-96 rounded-full bg-white/10 blur-3xl pointer-events-none" />
      <div className="absolute -bottom-32 -right-32 w-96 h-96 rounded-full bg-emerald-300/15 blur-3xl pointer-events-none" />

      {/* Main Brand Content */}
      <div className="flex flex-col items-center justify-center text-center px-6 z-10 animate-fade-in">
        {/* Custom App Logo Asset */}
        <div className="relative mb-6">
          <div className="w-24 h-24 sm:w-28 sm:h-28 rounded-3xl bg-white shadow-2xl shadow-black/25 flex items-center justify-center p-3 transform transition hover:scale-105">
            <svg
              className="w-16 h-16 sm:w-20 sm:h-20 text-[#0F9D58]"
              viewBox="0 0 64 64"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              {/* Village Roof & Flag */}
              <path
                d="M32 6L8 24H56L32 6Z"
                fill="#0F9D58"
              />
              <path
                d="M32 4V12M32 4L39 7L32 10"
                stroke="#E2B13C"
                strokeWidth="2.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              {/* Storefront Pillars & Door */}
              <rect x="14" y="24" width="36" height="28" rx="2" fill="#E8F5E9" />
              <rect x="18" y="28" width="6" height="20" rx="1" fill="#0F9D58" />
              <rect x="29" y="32" width="6" height="16" rx="1" fill="#0F9D58" />
              <rect x="40" y="28" width="6" height="20" rx="1" fill="#0F9D58" />
              {/* Fast Delivery Cart Wheel / Speed Ring */}
              <circle cx="20" cy="54" r="4" fill="#1B5E20" />
              <circle cx="44" cy="54" r="4" fill="#1B5E20" />
              <path d="M12 54H52" stroke="#1B5E20" strokeWidth="3" strokeLinecap="round" />
            </svg>
          </div>
          {/* Subtle Pulse Badge */}
          <div className="absolute -bottom-2 -right-2 bg-emerald-900/80 text-emerald-200 text-[10px] font-black uppercase tracking-wider px-2 py-0.5 rounded-full border border-emerald-400/40 shadow-sm">
            Live
          </div>
        </div>

        {/* Brand Text: Display "GaonBazaar" in crisp white text below the logo */}
        <h1 className="text-4xl sm:text-5xl font-black text-white tracking-tight drop-shadow-md font-sans">
          GaonBazaar
        </h1>

        {/* Subtitle / Value Proposition */}
        <p className="mt-3 text-sm sm:text-base font-semibold text-emerald-50 tracking-wide max-w-xs drop-shadow-sm">
          गाँव बाज़ार • 15 मिनट ग्रामीण डिलीवरी
        </p>

        <p className="mt-1 text-xs text-white/80 font-medium">
          Apna Gaon, Apna Bazaar
        </p>

        {/* Loading Indicator */}
        <div className="mt-10 flex flex-col items-center space-y-2">
          <div className="w-36 h-1.5 bg-black/15 rounded-full overflow-hidden">
            <div className="h-full bg-white rounded-full animate-[progress_2.5s_ease-in-out_infinite]" />
          </div>
          <span className="text-[11px] text-white/75 font-medium tracking-wider">
            आरंभ हो रहा है...
          </span>
        </div>
      </div>

      {/* Footer Branding */}
      <div className="absolute bottom-6 text-center text-[10px] text-white/70 font-semibold tracking-wider uppercase">
        Digital Bharat Hyperlocal Network • 100% Secure
      </div>
    </div>
  );
}

export default SplashScreen;
