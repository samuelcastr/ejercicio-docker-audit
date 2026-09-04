# Ejercicio Docker Audit

Ejercicio de auditoría, refactor y despliegue de una API en Flask con CI/CD y HTTPS. El pipeline (pytest, bandit, trivy) valida los cambios y despliega el stack en una EC2 con nginx reverse proxy, Docker Compose y certificado Let's Encrypt (DuckDNS).

## URLs del despliegue

| Servicio | URL | Descripción |
|----------|-----|-------------|
| API | https://api.techovaf4.duckdns.org | API principal en Flask (Gunicorn). Health check en `/health` → `{"status":"ok"}` |
| duzzle | https://duzzle.techovaf4.duckdns.org | **Dozzle**: visor en tiempo real de los logs de los contenedores Docker |
| kuma | https://kuma.techovaf4.duckdns.org | **Uptime Kuma**: monitorización y alertas de disponibilidad de servicios |

Todo el tráfico HTTP redirige a HTTPS (302). Los tres subdominios usan un certificado wildcard `*.techovaf4.duckdns.org` de Let's Encrypt con renovación automática.

## Estructura del stack

```
Internet → nginx (80/443, TLS)
            ├── /api    → techova-app    (Flask/gunicorn, :8000)
            ├── /duzzle → techova-duzzle (Dozzle, :8080)
            └── /kuma   → techova-kuma   (uptime-kuma, :3001)
                          techova-db     (mariadb:11)
```

## Fases

1. **Auditoría** de la aplicación original (`AUDITORIA.md`).
2. **Refactor**: pytest + bandit + trivy en verde.
3. **CI/CD**: pipeline GitHub Actions (`test`, `bandit`, `trivy`, `deploy`).
4. **Deploy con HTTPS**: nginx reverse proxy, DuckDNS, Let's Encrypt.

Evidencias de cada fase en [`evidencias/`](evidencias/).

## Desarrollo

```sh
pip install -r requirements-dev.txt
pytest -v
```