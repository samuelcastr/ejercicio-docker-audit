# Evidencias — Ejercicio Docker Audit

Carpeta de **evidencias por fase** del proyecto. Cada submódulo explica qué se probó, qué comando generó la evidencia y qué demuestra.

## Estructura

```
evidencias/
├── README.md            ← este índice
├── fase1/               ← Auditoría de vulnerabilidades (línea base)
│   ├── LEEME.md
│   ├── bandit-antiguo.txt
│   ├── pytest-fallo.txt
│   ├── trivy-original.txt
│   └── exploit-dinamico.txt
├── fase2/               ← Código refactorizado + análisis en VERDE (pendiente)
│   └── LEEME.md
├── fase3/               ← Pipeline GitHub Actions todo en verde (pendiente)
│   └── LEEME.md
└── fase4/               ← Despliegue EC2 + proxy 80/443 + subdominios (pendiente)
    └── LEEME.md
```

## Resumen por fase

| Fase | Estado | Evidencia principal |
|------|--------|---------------------|
| **1. Auditoría** | ✅ Completa | Tabla en `AUDITORIA.md` + 4 archivos de salida |
| **2. Refactor** | ⏳ Pendiente | pytest/bandit/trivy en verde + `docker compose up` |
| **3. Pipeline** | ⏳ Pendiente | Screenshot de GitHub Actions con 4 jobs verdes |
| **4. Despliegue** | ⏳ Pendiente | `/etc/hosts`, curl 3 subdominios, nginx, `docker ps` en EC2 |

---

## Cómo se genera cada evidencia (reproducibilidad)

Todas las corridas se hacen dentro del entorno virtual `.venv`:

```bash
cd ~/Proyectos/ejercicio-docker-audit
source .venv/bin/activate
```

| Evidencia | Comando |
|-----------|---------|
| Bandit | `bandit app.py test_app.py -f txt` |
| pytest | `pytest -v` (repetir 3x para demostrar inestabilidad) |
| Trivy | `docker build -t legacynova:original . && trivy image --severity HIGH,CRITICAL --ignore-unfixed legacynova:original` |
| Explotación | `python app.py` + `curl` contra los endpoints |

> Las capturas de pantalla de cada fase se agregan junto a los archivos `.txt/.md` correspondientes.