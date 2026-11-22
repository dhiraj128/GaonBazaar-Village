// GaonBazaar Rural Hyperlocal PWA Service Worker: Runner
// Offline-capable caching with network-first navigation for instant updates
const CACHE_NAME = 'gaonbazaar-runner-v1.0.2';

const PRECACHE_ASSETS = [
  './',
  './index.html',
  './runner.css',
  './manifest.json',
  './favicon.png',
  './icons/Icon-192.png',
  './icons/Icon-512.png',
  './icons/Icon-maskable-192.png',
  './icons/Icon-maskable-512.png',
  './runner_script_1.js',
  './runner_script_2.js',
  './runner_script_3.js',
  './runner_script_4.js'
];

// Install: precache critical app shell
self.addEventListener('install', (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(PRECACHE_ASSETS).catch((err) => {
        console.warn('[SW-Runner] Precache partial warning:', err);
      });
    })
  );
});

// Activate: clean up ONLY outdated runner caches (never touch customer, vendor, or user sessions)
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name.startsWith('gaonbazaar-runner-') && name !== CACHE_NAME)
          .map((name) => {
            console.log('[SW-Runner] Purging outdated runner cache:', name);
            return caches.delete(name);
          })
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch Strategy:
// 1. Navigation requests (HTML documents): Network-first with cache fallback
// 2. Dynamic API & Database requests: Network-only with JSON offline fallback
// 3. Static assets (CSS, JS, images): Stale-While-Revalidate
self.addEventListener('fetch', (event) => {
  const req = event.request;
  const url = new URL(req.url);

  // Skip non-GET and chrome-extension/schemes
  if (req.method !== 'GET' || !url.protocol.startsWith('http')) {
    return;
  }

  // Network-first for live API calls and Supabase realtime
  if (url.pathname.includes('/api/v1/') || url.hostname.includes('supabase.co') || url.hostname.includes('onrender.com')) {
    event.respondWith(
      fetch(req).catch(() => {
        return new Response(JSON.stringify({ error: 'Offline', offline: true }), {
          headers: { 'Content-Type': 'application/json' },
          status: 503
        });
      })
    );
    return;
  }

  // Network-first for navigation (HTML page load) to ensure immediate updates on reload
  if (req.mode === 'navigate' || req.destination === 'document') {
    event.respondWith(
      fetch(req)
        .then((networkResp) => {
          if (networkResp && networkResp.status === 200) {
            const copy = networkResp.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(req, copy));
          }
          return networkResp;
        })
        .catch(() => caches.match(req).then((cached) => cached || caches.match('./index.html')))
    );
    return;
  }

  // Stale-While-Revalidate for UI assets
  event.respondWith(
    caches.match(req).then((cachedResp) => {
      const fetchPromise = fetch(req).then((networkResp) => {
        if (networkResp && networkResp.status === 200 && networkResp.type !== 'opaque') {
          const respToCache = networkResp.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(req, respToCache);
          });
        }
        return networkResp;
      }).catch(() => cachedResp);

      return cachedResp || fetchPromise;
    })
  );
});
