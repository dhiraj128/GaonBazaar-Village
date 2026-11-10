import React, { useState, useEffect } from 'react';

export function VendorPortal() {
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    document.title = 'GaonBazaar Dukaan | गाँव बाज़ार दुकान - विक्रेता पोर्टल';
  }, []);

  return (
    <div className="fixed inset-0 w-screen h-screen bg-[#0f172a] overflow-hidden m-0 p-0 z-50">
      {!loaded && (
        <div className="absolute inset-0 flex flex-col items-center justify-center bg-[#0a101d] text-white z-10 transition-opacity duration-300">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-amber-600 to-yellow-400 flex items-center justify-center shadow-lg shadow-amber-500/20 mb-4 animate-pulse">
            <svg className="w-8 h-8 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
              <polyline points="9 22 9 12 15 12 15 22" />
            </svg>
          </div>
          <h2 className="text-xl font-bold tracking-tight text-white mb-1">GaonBazaar Dukaan</h2>
          <p className="text-xs text-amber-400 font-medium">दुकानदार पोर्टल लोड हो रहा है...</p>
        </div>
      )}
      <iframe
        src="/vendor/index.html"
        title="GaonBazaar Dukaan Vendor App"
        className="w-full h-full border-0 block"
        allow="camera; microphone; geolocation; payment; clipboard-write; autoplay"
        allowFullScreen
        onLoad={() => setLoaded(true)}
      />
    </div>
  );
}

export default VendorPortal;
