# Fase 1 — Auditoría de vulnerabilidades (línea base)

Evidencias del análisis sobre el **código original sin corregir** (`app.py`, `Dockerfile`, `test_app.py`).

**Fecha:** 04/09/2026 · **Imagen auditada:** `legacynova:original`

## Archivos de evidencia

### 1. `bandit-antiguo.txt` — Análisis estático (Bandit)
- **Comando:** `bandit app.py test_app.py -f txt`
- **Resultado:** **6 hallazgos** (1 HIGH, 2 MEDIUM, 3 LOW) → Total líneas analizadas 34
- Hallazgos: `B105` contraseña hardcodeada · `B608` SQL injection · `B201` debug=True (HIGH) · `B104` bind 0.0.0.0 · `B311` random no crypto · `B101` assert en test
- **Captura sugerida:** pantalla completa de la sección "Test results".

### 2. `pytest-fallo.txt` — Tests inestables (pytest)
- **Comando:** `pytest -v` corrido 3 veces (x3)
- **Resultado:** **3/3 corridas falladas** — `AssertionError: El servicio de salud es inestable` · `assert 500 == 200` · `ZeroDivisionError: division by zero` en `app.py:31`
- Demuestra: el endpoint `/health` falla de forma **aleatoria** (30% por llamada).
- **Captura sugerida:** la sección `FAILURES` de una corrida.

### 3. `trivy-original.txt` — Escaneo de imagen (Trivy)
- **Comando:**
  ```bash
  docker build -t legacynova:original .
  trivy image --severity HIGH,CRITICAL --ignore-unfixed --skip-version-check legacynova:original
  ```
- **Resultado:**
  - Paquetes OS: **1976** vulnerabilidades (1781 HIGH / 195 CRITICAL)
  - Paquetes Python: **8** (7 HIGH / 1 CRITICAL)
  - CVEs destacados: Flask `CVE-2023-30861` (fix 2.3.2), PyMySQL `CVE-2024-36039` (CRITICAL, fix 1.1.1), setuptools `CVE-2022-40897`/`CVE-2024-6345`/`CVE-2025-47273`, msgpack `GHSA-6v7p-g79w-8964`, wheel `CVE-2026-24049`
- **Captura sugerida:** filas de las tablas `Flask (METADATA)` y `PyMySQL (METADATA)`.

### 4. `exploit-dinamico.txt` — Explotación manual (curl)
- **Comando:** levantar la app con `python app.py` y probar endpoints (se usó puerto 5099/5100, ya que el 5050 lo ocupa otro proyecto local)
- **Resultado:**
  - **SQLi reflejada:** `Simulando consulta: SELECT * FROM usuarios WHERE id = 1 OR 1=1--`
  - **Health no determinista:** `200 500 200 500 200 200 500 500 200 200`
  - **Debugger de Werkzeug activo** con PIN `133-912-090` (permite **RCE**)
  - **Fuga de info:** traceback completo con `ZeroDivisionError` en `app.py:31`
- **Captura sugerida:** las 3 secciones del archivo.

## Entregable de fase

`AUDITORIA.md` (raíz del repo) — tabla con **12 vulnerabilidades**, severidad, ubicación, referencia y remediación.