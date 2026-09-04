# FASE 4 — Proxy inverso nginx + 3 subdominios + HTTPS

**Objetivo:** exponer la API y 2 servicios adicionales (dizzle, kuma) mediante un proxy inverso nginx con TLS, redirigiendo todo el tráfico HTTP a HTTPS.

## Arquitectura del stack (EC2, docker compose)

```
                Internet
                   |
             80 / 443
                   |
        +--- techova-proxy (nginx:alpine) --termino TLS + reescrituras
        |           |                      + cabeceras de seguridad
        |           | proxy_pass
        |     +-----+----------------------------+
        |     |     |                            |
   api.techova.local  dizzle.techova.local    kuma.techova.local
        |     |     |                            |
   techova-app   techova-dizzle (nginx)      techova-kuma (nginx)
   (gunicorn:8000)  (HTML placeholder)        (HTML placeholder)
        |
   techova-db (mariadb:11)
```

- `proxy/nginx.conf` montado en el proxy: 1 bloque HTTP que redirige con `302` a HTTPS y 3 bloques HTTPS (`api`, `dizzle`, `kuma`).
- Certificado **autofirmado** wildcard/SAN para `*.techova.local`, generado en el deploy con `openssl` (evita commitear claves).
- Cabeceras de seguridad en el proxy: `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`, `Strict-Transport-Security` (HSTS).
- TLS 1.2/1.3 únicamente.

## Ejecución del pipeline

- Run: https://github.com/samuelcastr/ejercicio-docker-audit/actions/runs/33916619129
- Estado: **4/4 jobs verdes** (`1-test` 9s, `2-bandit` 8s, `3-trivy` 31s, `4-deploy` 41s)
- En el job de deploy, tras `docker compose up`, se verifica:
  ```
  out: == Verificacion HTTPS ==
  out: API por HTTPS OK
  out: dizzle por HTTPS OK
  out: kuma por HTTPS OK
  ```

## Verificación externa (desde fuera de la instancia)

`evidencias/fase4/verificacion-externa.txt`:

```
=== HTTPS API ===        curl -ksS https://3.142.51.210/health -H "Host: api.techova.local"
{"status":"ok"}

=== HTTP -> HTTPS ===    curl -sS http://3.142.51.210/ ...
HTTP 80 -> 302 (Location: https://api.techova.local/)

=== dizzle ===           <h1>Servicio dizzle</h1>
=== kuma ===             <h1>Servicio kuma</h1>
```

## Resolución DNS local (sin dominio real)

No hay dominio público: los nombres se resuelven con una entrada en `/etc/hosts` de cada máquina cliente:

```
3.142.51.210 api.techova.local dizzle.techova.local kuma.techova.local
```

Como el certificado es autofirmado, el navegador mostrará un aviso al primer acceso; se acepta para esta práctica. En producción se usaría un certificado emitido por una CA o Let's Encrypt.

## Incidente resuelto

- El primer push de Fase 4 fallaba el arranque del workflow ("workflow file issue"): el bloque `script:` del job deploy había quedado desindentado y fuera de `with:`. Corregido a la indentación correcta (commit 3f77da8).