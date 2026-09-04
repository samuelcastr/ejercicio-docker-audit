# Auditoría de Seguridad — API Legacy TechNova

**Fecha:** 04/09/2026
**Repo:** `samuelcastr/ejercicio-docker-audit`
**Alcance:** `app.py`, `Dockerfile`, `test_app.py` (versión original sin corregir)
**Herramientas:** Bandit 1.9.4, pytest 9.1.1, Trivy 0.73.0, pruebas dinámicas (curl), revisión manual

> Todas las evidencias generadas se encuentran en [`evidencias/fase1/`](evidencias/fase1/LEEME.md).

---

## Metodología

| Paso | Actividad | Herramienta | Resultado |
|------|-----------|-------------|-----------|
| 1 | Análisis estático del código | Bandit | 6 hallazgos (1 HIGH, 2 MEDIUM, 3 LOW) |
| 2 | Pruebas unitarias (x3) | pytest | 3/3 corridas falladas (test inestable) |
| 3 | Escaneo de la imagen `legacynova:original` | Trivy | 1976 CVEs SO + 8 CVEs Python |
| 4 | Explotación dinámica | curl + Flask | SQLi reflejada, health 200/500, debugger activo |
| 5 | Revisión manual | — | SQLi, fuga de info, malas prácticas Dockerfile |

---

## Tabla de vulnerabilidades encontradas

| # | Vulnerabilidad | Tipo | Severidad | Ubicación | Detección / Ref | Remediación (Fase 2) |
|---|----------------|------|-----------|-----------|-----------------|----------------------|
| 1 | **Credenciales MySQL en texto plano** (`root` / `admin_adso_2026_secreto`) | Secreto / Config | **Crítica** | `app.py:8-11` | Bandit `B105` · CWE-259 | Variables de entorno (`os.environ`) + `.env`, nunca versionar secretos |
| 2 | **SQL Injection** por concatenación de `id` sin validar | Web App | **Crítica** | `app.py:24-25` | Bandit `B608` · CWE-89 + prueba dinámica | Query parametrizada (`%s`) + cast a `int` con validación |
| 3 | **`debug=True` en producción** (debugger de Werkzeug permite ejecutar código: se generó PIN `133-912-090`) | Web App | **Alta** | `app.py:35` | Bandit `B201` · CWE-94 | `debug=False`, servir con WSGI de producción (gunicorn) |
| 4 | **`/health` no determinista**: `1/0` aleatorio (30%) | Disponibilidad | **Alta** | `app.py:30` | pytest fallo + HTTP `200/500` mezclados | Endpoint determinista, sin lógica aleatoria |
| 5 | **Fuga de información**: excepción cruda devuelta al cliente + traceback en pantalla | Info leak | **Media** | `app.py:19-20` | Manual · CWE-209 | Loguear error, responder `500` genérico, `propagate_exceptions=False` |
| 6 | **Bind a todas las interfaces** `host='0.0.0.0'` sin proxy ni firewall | Config | **Media** | `app.py:35` | Bandit `B104` · CWE-605 | Exponer solo vía nginx/gunicorn; puerto desde env |
| 7 | **Dependencias obsoletas**: `python:3.8` (EOL), `Flask 1.1.2`, `PyMySQL 0.9.3` | Supply chain | **Crítica** | `Dockerfile:1,6` | Trivy: Flask `CVE-2023-30861` (fix 2.3.2), PyMySQL `CVE-2024-36039` (fix 1.1.1) | Actualizar a `python:3.12-slim`, `Flask 3.x`, `PyMySQL 1.x` |
| 8 | **CVEs en el SO de la imagen** | Supply chain | **Alta** | base `python:3.8` | Trivy: **1976** (1781 HIGH / 195 CRITICAL) | Base más reciente + `trivy scan` en CI |
| 9 | **Malas prácticas Docker**: corre como **root**, `COPY . /app` sin `.dockerignore`, sin `requirements.txt` ni healthcheck | Docker | **Media** | `Dockerfile:2-4` | Manual | Usuario no-root, `.dockerignore`, `requirements.txt`, `HEALTHCHECK` |
| 10 | **Sin orquestación ni CI/CD** | Arquitectura | **Media** | repo | Manual | `docker-compose.yml` + pipeline GitHub Actions |
| 11 | `random` no criptográfico | Criptografía | Baja | `app.py:30` | Bandit `B311` · CWE-330 | Eliminado al hacer el health determinista |
| 12 | `assert` en test | Calidad | Baja | `test_app.py:7` | Bandit `B101` · CWE-703 | Test real con aserciones explícitas |

---

## Evidencias clave

| Evidencia | Archivo | Qué demuestra |
|-----------|---------|---------------|
| Bandit | `evidencias/fase1/bandit-antiguo.txt` | 6 hallazgos sobre el código original |
| pytest | `evidencias/fase1/pytest-fallo.txt` | 3 corridas fallidas, health inestable |
| Trivy | `evidencias/fase1/trivy-original.txt` | 1976 + 8 CVEs en la imagen original |
| Explotación | `evidencias/fase1/exploit-dinamico.txt` | SQLi reflejada, 200/500 al azar, debugger activo |

**Conclusión:** la API presenta **2 vulnerabilidades críticas explotables de forma remota** (secretos + SQLi), **debug habilitado** (RCE), **disponibilidad inestable** y una imagen con **1976+ CVEs**. Requiere refactorización completa antes de cualquier despliegue.

---

## Actualización — Fase 2: remediación aplicada (04/09/2026)

Todas las vulnerabilidades fueron corregidas en la refactorización. Evidencias en [`evidencias/fase2/`](evidencias/fase2/LEEME.md).

| # | Vulnerabilidad | Estado | Evidencia |
|---|----------------|--------|-----------|
| 1 | Credenciales en texto plano | ✅ Corregida | `app.py` usa `os.environ` · `.env.example` |
| 2 | SQL Injection | ✅ Corregida | Query parametrizada `%s` + `isdigit()` · test `id=1 OR 1=1--` → 400 |
| 3 | `debug=True` | ✅ Corregida | `debug=False` + gunicorn en producción |
| 4 | `/health` inestable | ✅ Corregida | Determinista · 5/5 HTTP 200 |
| 5 | Fuga de info | ✅ Corregida | Respuestas JSON genéricas + `logger.exception` |
| 6 | Bind 0.0.0.0 en run | ✅ Corregida | Default `127.0.0.1`; exposición solo vía contenedor |
| 7 | Dependencias obsoletas | ✅ Corregida | Flask 3.1.3 · PyMySQL 1.2.0 · gunicorn 26.2.0 · `python:3.12-slim` |
| 8 | CVEs en imagen | ✅ Corregida | Trivy: **0** HIGH/CRITICAL (debian 13.6) |
| 9 | Malas prácticas Docker | ✅ Corregida | Multi-stage, usuario `appuser` no-root, `.dockerignore`, `HEALTHCHECK` |
| 10 | Sin orquestación | ✅ Corregida | `docker-compose.yml` (db mariadb + app) |
| 11 | random no criptográfico | ✅ Corregida | Eliminado |
| 12 | assert en test | ✅ Aceptable | `assert` es intencional en tests (excluido del escaneo de app) |

**Resultado del análisis post-refactor:** `pytest` **6 passed** · `bandit` **0 issues** · `trivy` **0 vulnerabilidades** · `docker compose up` con ambos servicios **healthy**. Compare la imagen: 1976+8 CVEs antes → **0** después.