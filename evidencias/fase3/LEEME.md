# FASE 3 — Pipeline CI/CD

**Objetivo:** automatizar test + seguridad + desplegado continuo en GitHub Actions hacia la instancia EC2.

## Pipeline (.github/workflows/ci-cd.yml)

Dispara en cada `push` a `main` y manualmente (`workflow_dispatch`). 4 jobs encadenados:

| Job | Qué hace | Gate |
|---|---|---|
| 1-test | `pytest -v` con dependencias de `requirements-dev.txt` | falla -> aborta |
| 2-bandit | `bandit app.py` | cualquier hallazgo -> aborta |
| 3-trivy | construye la imagen y la escanea con `aquasec/trivy:0.73.0` (HIGH/CRITICAL) | vuln HIGH/CRITICAL -> aborta |
| 4-deploy | depende de los 3 anteriores; SSH a la EC2, aprovisiona Docker, copia el código, `docker compose up -d --build` y verifica `/health` | health fail -> aborta |

El job 3 solo avanza al 4 si el escaneo Trivy está limpio (gate de seguridad antes de tocar producción).

## Resultado: run principal

- Repositorio: samuelcastr/ejercicio-docker-audit
- Run: https://github.com/samuelcastr/ejercicio-docker-audit/actions/runs/33915967611
- Estado: **4/4 jobs verdes**

```
✓ 1-test   in 9s
✓ 2-bandit in 7s
✓ 3-trivy in 50s
✓ 4-deploy in 59s
```

Captura de los 4 jobs en verde (GitHub Actions): `evidencias/fase3/pipeline-verde.png`

## Destripes resueltos durante la ejecución

1. **Clave SSH dañada en GitHub Actions secrets**: al pegar el PEM desde la web se perdían/rompían saltos de línea. Se resolvió subiendo el secreto desde el archivo real con `gh secret set EC2_SSH_KEY < clave_dock.pem` (byte a byte, sin copiar/pegar).
2. **`docker-compose-v2` no existe en Debian 13**: se aprovisionó Docker desde el repo oficial de Docker (`docker-ce` + `docker-compose-plugin`), con `gnupg` previo (no viene en la imagen mínima de la EC2).

## Secretos de GitHub utilizados

| Secreto | Valor |
|---|---|
| `EC2_HOST` | 3.142.51.210 |
| `EC2_USER` | admin |
| `EC2_SSH_KEY` | clave privada PEM (subida desde archivo) |

Los secretos no se commitearon nunca (solo viven en GitHub Actions).

## Verificación post-despliegue

`evidencias/fase3/verificacion-EC2.txt` (extraído de la instancia):

```
techova-app   Up 53 seconds (healthy)   0.0.0.0:8000->8000/tcp
techova-db    Up About a minute (healthy)

GET /health -> {"status":"ok"}
GET /buscar?q=docker -> {"email":"ana@techova.co","id":1,"nombre":"Ana Pérez"}
```

La API (`/health` y `/buscar` con consulta real a MariaDB) responde, corriendo desde la EC2 con Docker Compose.

## Nota de seguridad

- El `.env` de despliegue se genera con credenciales de desarrollo dentro del pipeline. Para producción debería inyectarse desde secretos (no commiteado).
- El token PAT usado para `gh` se creó solo para operar los secretos/`gh` y quedó bajo el control de la cuenta.