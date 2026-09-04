# FASE 4 — Proxy inverso nginx + 3 subdominios + HTTPS

**Objetivo:** exponer la API y 2 servicios adicionales (duzzle, kuma) mediante un proxy inverso nginx con TLS, redirigiendo todo el tráfico HTTP a HTTPS.

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
   api.techova.local  duzzle.techova.local    kuma.techova.local
        |     |     |                            |
   techova-app   techova-duzzle (dozzle)    techova-kuma (uptime-kuma)
   (gunicorn:8000)   (dozzle:8080)         (kuma:3001)
        |
   techova-db (mariadb:11)
```

- `proxy/nginx.conf` montado en el proxy: 1 bloque HTTP que redirige con `302` a HTTPS y 3 bloques HTTPS (`api`, `duzzle`, `kuma`).
- Los servicios `duzzle` y `kuma` son **imágenes externas** traídas con `docker compose` (pineadas por digest): `amir20/dozzle` (puerto 8080, con `docker.sock` montado para leer logs) y `louislam/uptime-kuma` (puerto 3001), con volúmenes `duzzle-data` y `kuma-data`. El pipeline ejecuta `docker compose pull` antes de `up`.
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
  out: duzzle por HTTPS OK
  out: kuma por HTTPS OK
  ```

## Verificación externa (desde fuera de la instancia)

`evidencias/fase4/verificacion-externa.txt`:

```
=== HTTPS API ===        curl -ksS https://3.142.51.210/health -H "Host: api.techova.local"
{"status":"ok"}

=== HTTP -> HTTPS ===    curl -sS http://3.142.51.210/ ...
HTTP 80 -> 302 (Location: https://api.techova.local/)

=== duzzle ===           <h1>Servicio duzzle</h1>
=== kuma ===             <h1>Servicio kuma</h1>
```

## Resolución DNS y certificado (DuckDNS + Let's Encrypt)

- Se registró el dominio **`techovaf4.duckdns.org`** en DuckDNS apuntando a `3.142.51.210`.
- DuckDNS activa el **wildcard** `*.techovaf4.duckdns.org`, así que `api`, `duzzle` y `kuma` resuelven por DNS público (se verificó: todos → 3.142.51.210). Ya no hay `/etc/hosts`.
- Certificados con **acme.sh** (instalado en la EC2, versión 3.1.5, con su tarea cron para renovación):
  - Emisión por **DNS-01** usando el token de DuckDNS y el plugin `dns_duckdns`, para `*.techovaf4.duckdns.org` (single-domain; emitir además la raíz provoca duplicados de TXT en DuckDNS).
  - Resultado servido por nginx:
    ```
    issuer  = Let's Encrypt (YR1)
    subject = CN=*.techovaf4.duckdns.org
    válido  hasta 2026-12-03 (renovación automática vía cron + reloadcmd 2026-11-04)
    ```
  - Los certs viven en `proxy/certs/` de la instancia (gitignored) y el job de deploy los preserva; el `--reloadcmd` de acme.sh renueva + hace `docker compose restart proxy` en la EC2.
- Con CA real el navegador **no muestra avisos**; comprobado con `curl` sin `-k`:
  ```
  https://api.techovaf4.duckdns.org/health → {"status":"ok"} HTTP 200
  https://duzzle.techovaf4.duckdns.org      → HTTP 200 (Dozzle - visor de logs)
  https://kuma.techovaf4.duckdns.org        → 302 → /setup (Uptime Kuma)
  http://api.techovaf4.duckdns.org          → 302 → https
  ```

## Incidentes resueltos

- El primer push de Fase 4 fallaba el arranque del workflow ("workflow file issue"): el bloque `script:` del job deploy había quedado desindentado y fuera de `with:`. Corregido a la indentación correcta (commit 3f77da8).
- El proxy nginx no recargaba el config nuevo en cada deploy (los bind-mounts no cambian de hash): se añadió `docker compose up -d --force-recreate proxy` al job de deploy.
- Emisión de Let's Encrypt colgada: la imagen mínima de Debian no traía `dig`/`nslookup` (se instaló `dnsutils`) y emitir wildcard + raíz a la vez duplicaba los TXT de DuckDNS; se resolvió emitiendo solo el wildcard con `--dnssleep`.
- OOM en la EC2 (t2.micro, 1 GB): al recrear el stack con Grafana + Uptime Kuma la instancia entró en swap-thrash y dejó de responder por SSH (hubo que forzar reboot desde AWS). Se añadió un swapfile de 2 GB (`/swapfile`, activo en el arranque) y se sustituyó Grafana por **Dozzle** (mucho más ligero), dejando la RAM en ~440/939 MB.
- El servicio adicional que el enunciado pedía era **Dozzle** (no Grafana): se renombró `dizzle` → `duzzle` y se desplegó `amir20/dozzle` (puerto 8080, monta `/var/run/docker.sock` de solo lectura para leer los logs de los contenedores).