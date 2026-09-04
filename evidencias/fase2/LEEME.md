# Fase 2 — Refactor con buenas prácticas

Evidencias del análisis **post-refactorización**. Todos los gate de calidad en **verde**.

**Fecha:** 04/09/2026 · **Imagen:** `techova:corregida` (multi-stage, sin pip en runtime)

## Archivos de evidencia

### 1. `pytest-verde.txt` — Tests deterministas (pytest)
- **Comando:** `pytest -v`
- **Resultado:** **6 passed in 0.10s**
- Tests: home 200 · buscar id válido 200 (query parametrizada con `%s`) · id inválido 400 (3 payloads) · BD caída 503 controlado · usuario no existe 404 · health determinista 5x200
- **Captura sugerida:** la salida completa con los 6 `PASSED`.

### 2. `bandit-corregido.txt` — Análisis estático limpio (Bandit)
- **Comando:** `bandit app.py -f txt` (los tests usan `assert` intencionalmente; se escanea solo `app.py`)
- **Resultado:** **No issues identified** — 0 HIGH / 0 MEDIUM / 0 LOW
- **Captura sugerida:** la línea "No issues identified".

### 3. `trivy-corregido.txt` — Escaneo de imagen limpio (Trivy)
- **Comando:** `trivy image --severity HIGH,CRITICAL --ignore-unfixed --skip-version-check techova:corregida`
- **Resultado:**
  - OS `debian 13.6`: **0** vulnerabilidades
  - Paquetes Python (flask, pymysql, gunicorn, werkzeug, etc.): **0**
- **Mejoras del Dockerfile:** multi-stage sin `pip`/`setuptools` en runtime → se eliminaron los 2 falsos positivos de `pip/_vendor/msgpack` y `setuptools` de la base
- **Captura sugerida:** la "Report Summary" con todos los targets en **0**.

### 4. `compose-up.txt` — Stack funcionando (docker compose + curl)
- **Comando:**
  ```bash
  docker compose up -d --build
  curl http://localhost:8000/...
  ```
- **Resultado:**
  - `techova-db` y `techova-app` ambos **healthy**
  - `GET /` → **200** `{"estado":"operativo",...}`
  - `GET /health` → **200 200 200 200 200** (determinista)
  - `GET /buscar?id=1` → **200** con datos reales de MariaDB (query parametrizada)
  - `GET /buscar?id=1 OR 1=1--` → **400** (inyección neutralizada)
  - `GET /buscar?id=9999` → **404**
  - `GET /buscar?id=abc` → **400**
- **Captura sugerida:** la sección de endpoints del archivo (respuestas + códigos HTTP).

## Entregable de fase

- Código refactorizado: `app.py`, `requirements.txt`, `requirements-dev.txt`, `Dockerfile`, `.dockerignore`, `docker-compose.yml`, `.env.example`, `db/init.sql`, `test_app.py`.
- `AUDITORIA.md` actualizado con la tabla "Fase 2 — remediación aplicada" (las 12 vulnerabilidades ✅).