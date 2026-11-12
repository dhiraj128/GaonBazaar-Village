import { useEffect } from 'react';

/**
 * Hosts the existing customer PWA exactly once. The PWA itself handles
 * language selection, phone login and dashboard restoration.
 * No extra loading splash or pre-login screens are layered on top of it.
 */
export function CustomerPortal() {
  useEffect(() => {
    document.title = 'Apna GaonBazaar | गाँव बाज़ार - ग्रामीण त्वरित डिलीवरी';
  }, []);

  return (
    <main
      className="fixed inset-0 w-full overflow-hidden bg-white m-0 p-0"
      style={{ height: '100dvh', minHeight: '100vh' }}
    >
      <iframe
        src="/customer/index.html"
        title="Apna GaonBazaar Customer App"
        className="block w-full h-full border-0 m-0 p-0"
        allow="camera; microphone; geolocation; payment; clipboard-write; autoplay"
        allowFullScreen
      />
    </main>
  );
}

export default CustomerPortal;
