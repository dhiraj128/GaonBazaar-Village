import React, { useEffect } from 'react';

export function CustomerPortal() {
  const [isLoaded, setIsLoaded] = React.useState(false);
  const [hasError, setHasError] = React.useState(false);
  const [reloadKey, setReloadKey] = React.useState(0);

  useEffect(() => {
    document.title = 'Apna GaonBazaar | गाँव बाज़ार - ग्रामीण त्वरित डिलीवरी';
  }, []);

  const savedLang = (() => {
    try {
      return localStorage.getItem('gb_customer_lang') || 'en';
    } catch {
      return 'en';
    }
  })();

  // 8-second fallback timeout for slow or failing connections
  useEffect(() => {
    const timer = setTimeout(() => {
      if (!isLoaded) {
        setHasError(true);
      }
    }, 8000);
    return () => clearTimeout(timer);
  }, [isLoaded, reloadKey]);

  const handleRetry = () => {
    setHasError(false);
    setIsLoaded(false);
    setReloadKey((prev) => prev + 1);
  };

  const iframeSrc = `/customer/index.html?lang=${encodeURIComponent(savedLang)}&embedded=true&_v=${reloadKey}`;

  return (
    <div className="fixed inset-0 w-full h-[100dvh] bg-slate-50 overflow-hidden m-0 p-0 z-50">
      {/* Loading Skeleton & Brand Splash Screen */}
      {!isLoaded && !hasError && (
        <div className="absolute inset-0 z-10 flex flex-col items-center justify-center bg-slate-50 p-6 text-center select-none animate-in fade-in duration-200">
          <div className="w-20 h-20 mb-4 rounded-2xl bg-emerald-600 flex items-center justify-center shadow-lg shadow-emerald-600/20 animate-pulse">
            <svg className="w-10 h-10 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="m2 7 4.41-4.41A2 2 0 0 1 7.83 2h8.34a2 2 0 0 1 1.42.59L22 7" />
              <path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8" />
              <path d="M15 22v-4a2 2 0 0 0-2-2h-2a2 2 0 0 0-2 2v4" />
              <path d="M2 7h20" />
            </svg>
          </div>
          <h1 className="text-xl font-black text-slate-800 tracking-tight">अपना गाँव बाज़ार</h1>
          <p className="text-xs font-semibold text-emerald-700 mt-1">Apna GaonBazaar • ग्रामीण त्वरित सेवा</p>
          <div className="mt-6 flex items-center space-x-2 text-slate-500 text-xs">
            <div className="w-4 h-4 border-2 border-emerald-600 border-t-transparent rounded-full animate-spin"></div>
            <span>सत्यापित हो रहा है / Connecting...</span>
          </div>
        </div>
      )}

      {/* Error Recovery Card */}
      {hasError && !isLoaded && (
        <div className="absolute inset-0 z-20 flex flex-col items-center justify-center bg-slate-50 p-6 text-center select-none">
          <div className="w-16 h-16 mb-4 rounded-2xl bg-amber-100 text-amber-600 flex items-center justify-center shadow-sm">
            <svg className="w-8 h-8" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
          </div>
          <h2 className="text-base font-bold text-slate-800">कनेक्शन धीमा है या लोड नहीं हो सका</h2>
          <p className="text-xs text-slate-500 mt-1 max-w-xs">
            The connection is taking longer than expected. Please retry or open directly.
          </p>
          <div className="mt-5 flex flex-col sm:flex-row gap-3 w-full max-w-xs">
            <button
              onClick={handleRetry}
              className="flex-1 px-4 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs rounded-xl shadow-md transition active:scale-95"
            >
              पुनः प्रयास करें / Retry
            </button>
            <a
              href={`/customer/index.html?lang=${encodeURIComponent(savedLang)}`}
              className="flex-1 px-4 py-2.5 bg-white border border-slate-300 hover:bg-slate-50 text-slate-700 font-bold text-xs rounded-xl text-center shadow-xs transition"
            >
              सीधा खोलें / Direct App
            </a>
          </div>
        </div>
      )}

      <iframe
        key={reloadKey}
        src={iframeSrc}
        title="Apna GaonBazaar Customer App"
        className={`w-full h-full border-0 block transition-opacity duration-300 ${isLoaded ? 'opacity-100' : 'opacity-0'}`}
        allow="camera; microphone; geolocation; payment; clipboard-write; autoplay"
        allowFullScreen
        onLoad={() => setIsLoaded(true)}
        onError={() => setHasError(true)}
      />
    </div>
  );
}

export { MobileLogin } from './MobileLogin';
export default CustomerPortal;
