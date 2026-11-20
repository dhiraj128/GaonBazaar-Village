(function() {
      try {
        var params = new URLSearchParams(window.location.search);
        var pLang = params.get('lang');
        if (pLang === 'en' || pLang === 'hi') {
          localStorage.setItem('gb_customer_lang', pLang);
        }
        var isAuth = localStorage.getItem('gb_customer_authenticated') === 'true' ||
                     localStorage.getItem('gb_customer_logged_in') === 'true' ||
                     localStorage.getItem('gb_auth_authenticated') === 'true' ||
                     !!localStorage.getItem('gb_customer_token') ||
                     params.get('embedded') === 'true';
        if (isAuth) {
          document.documentElement.classList.add('customer-authenticated');
        }
      } catch (e) {}
    })();
