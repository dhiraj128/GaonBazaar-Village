if ('serviceWorker' in navigator) {
      window.addEventListener('load', () => {
        navigator.serviceWorker.register('./service-worker.js')
          .then(reg => console.log('GaonBazaar SW active:', reg.scope))
          .catch(err => console.warn('SW registration notice:', err));
      });
    }
