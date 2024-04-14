// Install the service worker
self.addEventListener('install', event => {
    console.log('Service worker installed');
  });
  
  // Activate the service worker
  self.addEventListener('activate', event => {
    console.log('Service worker activated');
  });
  
  // Respond to fetch events
  self.addEventListener('fetch', event => {
    console.log('Fetch event:', event.request.url);
  });