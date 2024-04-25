// // Install the service worker
// self.addEventListener('install', event => {
//     console.log('Service worker installed');
//   });
  
//   // Activate the service worker
//   self.addEventListener('activate', event => {
//     console.log('Service worker activated');
//   });
  
//   // Respond to fetch events
//   self.addEventListener('fetch', event => {
//     console.log('Fetch event:', event.request.url);
//   });




var staticCacheName = 'djangopwa-v1';

self.addEventListener('install', function(event) {
    event.waitUntil(
        caches.open(staticCacheName).then(function(cache) {
            return cache.addAll([
                '',
            ]);
        })
    );
});

self.addEventListener('fetch', function(event) {
    var requestUrl = new URL(event.request.url);
    if (requestUrl.origin === location.origin) {
        if ((requestUrl.pathname === '/')) {
            event.respondWith(caches.match(''));
            return;
        }
    }
    event.respondWith(
        caches.match(event.request).then(function(response) {
            return response || fetch(event.request);
        })
    );
});