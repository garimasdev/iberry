// // Define a cache name
// const CACHE_NAME = 'iberry-pwa-v1';

// // List of files to cache
// const FILES_TO_CACHE = [
//     '/',
//     '/offline.html',
//     '/static/css/styles.css',
//     '/static/js/script.js',
//     '/static/images/iberry_logo.png',
//     '/static/images/iberry512.png',
//     '/static/images/iberry192.png'
// ];

// // Install event - cache files
// self.addEventListener('install', event => {
//     console.log('Service worker installed');
//     event.waitUntil(
//         caches.open(CACHE_NAME).then(cache => {
//             return cache.addAll(FILES_TO_CACHE);
//         })
//     );
// });

// // Activate event
// self.addEventListener('activate', event => {
//     console.log('Service worker activated');
//     event.waitUntil(
//         caches.keys().then(cacheNames => {
//             return Promise.all(
//                 cacheNames.map(cacheName => {
//                     if (cacheName !== CACHE_NAME) {
//                         console.log('Service worker removing old cache', cacheName);
//                         return caches.delete(cacheName);
//                     }
//                 })
//             );
//         })
//     );
// });

// Fetch event
self.addEventListener('fetch', event => {
    console.log('Fetch event:', event.request.url);
    event.respondWith(
        caches.match(event.request).then(response => {
            return response || fetch(event.request).catch(() => {
                return caches.match('/offline.html');
            });
        })
    );
});