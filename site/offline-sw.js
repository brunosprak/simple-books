const OFFLINE_CACHE_PREFIX = "simple-ja-books-offline:v1:";
const PWA_CACHE_PREFIX = "simple-ja-books-pwa:";
const PWA_CACHE_NAME = `${PWA_CACHE_PREFIX}v1`;
const PWA_SHELL_URLS = [
  "./",
  "./princess-of-mars/",
  "./books/princess-of-mars-ja.json",
  "./manifest.webmanifest",
  "./icons/icon-192.png",
  "./icons/icon-512.png"
];

self.addEventListener("install", (event) => {
  event.waitUntil((async () => {
    const cache = await caches.open(PWA_CACHE_NAME);
    await cache.addAll(PWA_SHELL_URLS);
    await self.skipWaiting();
  })());
});

self.addEventListener("activate", (event) => {
  event.waitUntil((async () => {
    const cacheNames = await caches.keys();
    await Promise.all(cacheNames
      .filter((name) => name.startsWith(PWA_CACHE_PREFIX) && name !== PWA_CACHE_NAME)
      .map((name) => caches.delete(name)));
    await self.clients.claim();
  })());
});

async function findCachedResponse(request) {
  const cacheNames = (await caches.keys())
    .filter((name) => name.startsWith(OFFLINE_CACHE_PREFIX) || name === PWA_CACHE_NAME)
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
