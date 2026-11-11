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
      className="fixed inset-0 h-screen w-screen flex flex-col items-center justify-center bg-[#0F9D58] text-white z-50 select-none overflow-hidden m-0 p-0 border-0"
    >
      {/* Main Brand Content - 100% Brand Green, No White Cards, No Borders */}
      <div className="flex flex-col items-center justify-center text-center px-6 z-10 animate-fade-in">
        {/* Logo in Pure White directly on green background - NO white cards or borders */}
        <div className="relative mb-6 flex items-center justify-center">
          <svg
            className="w-20 h-20 sm:w-24 sm:h-24 text-white drop-shadow-md"
            viewBox="0 0 64 64"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            {/* Village Roof & Flag in White */}
            <path d="M32 6L8 24H56L32 6Z" fill="white" />
            <path d="M32 4V12M32 4L39 7L32 10" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
            {/* Storefront Pillars & Door in White */}
            <rect x="14" y="24" width="36" height="28" rx="2" stroke="white" strokeWidth="2.5" />
            <rect x="19" y="28" width="5" height="20" rx="1" fill="white" />
            <rect x="29" y="32" width="6" height="16" rx="1" fill="white" />
            <rect x="40" y="28" width="5" height="20" rx="1" fill="white" />
            {/* Delivery Cart Wheel in White */}
            <circle cx="20" cy="54" r="4" fill="white" />
            <circle cx="44" cy="54" r="4" fill="white" />
            <path d="M12 54H52" stroke="white" strokeWidth="3" strokeLinecap="round" />
          </svg>
        </div>

        {/* Brand Text strictly in English in Crisp White */}
        <h1 className="text-4xl sm:text-5xl font-black text-white tracking-tight drop-shadow-md font-sans">
          GaonBazaar
        </h1>

        {/* Subtitle strictly in English */}
        <p className="mt-3 text-sm sm:text-base font-medium text-white/90 tracking-wide max-w-xs drop-shadow-sm">
          Rural Hyperlocal Delivery
        </p>

        {/* Loading Progress Bar */}
        <div className="mt-10 flex flex-col items-center space-y-2">
          <div className="w-36 h-1.5 bg-black/20 rounded-full overflow-hidden">
            <div className="h-full bg-white rounded-full animate-[progress_2.5s_ease-in-out_infinite]" />
          </div>
          <span className="text-[11px] text-white/80 font-medium tracking-wider">
            Loading...
          </span>
        </div>
      </div>

      {/* Footer Branding strictly in English */}
      <div className="absolute bottom-6 text-center text-[10px] text-white/70 font-semibold tracking-wider uppercase">
        Digital Bharat Hyperlocal Network • 100% Secure
      </div>
    </div>
  );
}

export default SplashScreen;
