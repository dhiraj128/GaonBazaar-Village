import React, { useEffect } from 'react';

export function CustomerPortal() {
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

  return (
    <div className="fixed inset-0 w-full h-[100dvh] bg-white overflow-hidden m-0 p-0 z-50">
      <iframe
        src={`/customer/index.html?lang=${encodeURIComponent(savedLang)}&embedded=true`}
        title="Apna GaonBazaar Customer App"
        className="w-full h-full border-0 block"
        allow="camera; microphone; geolocation; payment; clipboard-write; autoplay"
        allowFullScreen
      />
    </div>
  );
}

export { MobileLogin } from './MobileLogin';
export default CustomerPortal;
