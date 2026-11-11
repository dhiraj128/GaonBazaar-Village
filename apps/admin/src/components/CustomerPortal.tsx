import React, { useState, useEffect } from 'react';

export function CustomerPortal() {
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    document.title = 'Apna GaonBazaar | गाँव बाज़ार - ग्रामीण त्वरित डिलीवरी';
  }, []);

  return (
    <div className="fixed inset-0 w-screen h-screen bg-[#0f172a] overflow-hidden m-0 p-0 z-50">
      {!loaded && (
        <div className="absolute inset-0 flex flex-col items-center justify-center bg-[#0a101d] text-white z-10 transition-opacity duration-300">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-emerald-600 to-green-400 flex items-center justify-center shadow-lg shadow-green-500/20 mb-4 animate-pulse">
            <svg className="w-8 h-8 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="m7.5 4.27 9 5.15" />
              <path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z" />
              <path d="m3.3 7 8.7 5 8.7-5" />
              <path d="M12 22V12" />
            </svg>
          </div>
          <h2 className="text-xl font-bold tracking-tight text-white mb-1">Apna GaonBazaar</h2>
          <p className="text-xs text-emerald-400 font-medium">लोड हो रहा है • 15 मिनट ग्रामीण डिलीवरी...</p>
        </div>
      )}
      <iframe
        src="/customer/index.html"
        title="Apna GaonBazaar Customer App"
        className="w-full h-full border-0 block"
        allow="camera; microphone; geolocation; payment; clipboard-write; autoplay"
        allowFullScreen
        onLoad={() => setLoaded(true)}
      />
    </div>
  );
}

export { MobileLogin } from './MobileLogin';
export default CustomerPortal;
