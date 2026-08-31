const CACHE_NAME = "farmacia-inventario-v1";
const FILES_TO_CACHE = [
  "./inventario_farmacia.html",
  "./manifest.json",
  "./icon-192.png",
  "./icon-512.png"
];

// Al instalar, guarda una copia de los archivos básicos de la app
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(FILES_TO_CACHE))
  );
  self.skipWaiting();
});

// Limpia versiones viejas del cache cuando se actualiza la app
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k))
      )
    )
  );
  self.clients.claim();
});

// Estrategia: intenta la red primero (para datos frescos de Supabase),
// y si no hay conexión, usa lo que tenga guardado en cache.
self.addEventListener("fetch", (event) => {
  event.respondWith(
    fetch(event.request).catch(() => caches.match(event.request))
  );
});
