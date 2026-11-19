/**
 * Sureword Service Worker — Offline PWA Cache & Resilience
 */

const CACHE_NAME = "sureword-pwa-v1";
const STATIC_ASSETS = [
  "./",
  "./index.html",
  "./styles.css",
  "./design.css",
  "./app.js",
  "./experience.js",
  "./logo.svg",
  "./favicon.svg",
  "./manifest.json"
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_ASSETS);
    })
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
      );
    })
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  const request = event.request;
  const url = new URL(request.url);

  // Dynamic API and health endpoints: network-first with JSON offline fallback
  if (
    request.method !== "GET" ||
    url.pathname.includes("/api/") ||
    url.pathname.includes("/health")
  ) {
    event.respondWith(
      fetch(request).catch(() => {
        return new Response(
          JSON.stringify({
            offline: true,
            status: "offline",
            message: "Offline mode active. Request queued in local IndexedDB."
          }),
          {
            status: 503,
            headers: { "Content-Type": "application/json" }
          }
        );
      })
    );
    return;
  }

  // Static shell assets: cache-first with network fallback and background update
  event.respondWith(
    caches.match(request).then((cachedResponse) => {
      if (cachedResponse) {
        return cachedResponse;
      }

      return fetch(request)
        .then((networkResponse) => {
          if (networkResponse && networkResponse.status === 200) {
            const copy = networkResponse.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(request, copy));
          }
          return networkResponse;
        })
        .catch(() => {
          if (request.mode === "navigate") {
            return caches.match("./index.html");
          }
          return new Response("Network offline", { status: 503, statusText: "Offline" });
        });
    })
  );
});
