import React, { useState, useEffect } from 'react';

export function RunnerPortal() {
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    document.title = 'Gaon Mitra | गाँव मित्र - डिलीवरी पार्टनर पोर्टल';
  }, []);

  return (
    <div className="fixed inset-0 w-screen h-screen bg-[#0f172a] overflow-hidden m-0 p-0 z-50">
      {!loaded && (
        <div className="absolute inset-0 flex flex-col items-center justify-center bg-[#0a101d] text-white z-10 transition-opacity duration-300">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-cyan-600 to-blue-400 flex items-center justify-center shadow-lg shadow-cyan-500/20 mb-4 animate-pulse">
            <svg className="w-8 h-8 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="18.5" cy="17.5" r="3.5" />
              <circle cx="5.5" cy="17.5" r="3.5" />
              <circle cx="15" cy="5" r="1" />
              <path d="M12 17.5V14l-3-3 4-3 2 3h2" />
            </svg>
          </div>
          <h2 className="text-xl font-bold tracking-tight text-white mb-1">Gaon Mitra</h2>
          <p className="text-xs text-cyan-400 font-medium">डिलीवरी पार्टनर ऐप लोड हो रहा है...</p>
        </div>
      )}
      <iframe
        src="/runner/index.html"
        title="Gaon Mitra Runner App"
        className="w-full h-full border-0 block"
        allow="camera; microphone; geolocation; payment; clipboard-write; autoplay"
        allowFullScreen
        onLoad={() => setLoaded(true)}
      />
    </div>
  );
}

export default RunnerPortal;
