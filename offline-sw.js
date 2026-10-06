const OFFLINE_CACHE_PREFIX = "simple-ja-books-offline:v1:";

self.addEventListener("install", () => {
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(self.clients.claim());
});

async function findCachedResponse(request) {
  const cacheNames = (await caches.keys())
    .filter((name) => name.startsWith(OFFLINE_CACHE_PREFIX))
    .reverse();
  for (const cacheName of cacheNames) {
    const cache = await caches.open(cacheName);
    const response = await cache.match(request, { ignoreSearch: true });
    if (response) return response;
  }
  return null;
}

async function networkFirst(request) {
  try {
    const response = await fetch(request);
    if (response.ok) return response;
    const cached = await findCachedResponse(request);
    return cached || response;
  } catch (_error) {
    const cached = await findCachedResponse(request);
    if (cached) return cached;
    throw _error;
  }
}

self.addEventListener("fetch", (event) => {
  const { request } = event;
  if (request.method !== "GET") return;
  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;
  event.respondWith(networkFirst(request));
});
