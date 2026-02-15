self.addEventListener('install',function(event){
    console.log("Servicio worker instalado");
    event.waitUntil(
        caches.open('v1').then(function(cache) {
            return cache.addAll([
                '/static/dist/css/style_qhawariy.css'
            ])
        })
    )
});

self.addEventListener("fetch",function(event){
    if (new URL(event.request.url).oriin !== self.location.origin){
        return;
    }
    event.respondWith(fetch(event.request));
    console.log("Interceptando peticion:",event.request.url);
});