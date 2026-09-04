# Fase 2 — Refactor con buenas prácticas

**Estado: ⏳ Pendiente de ejecutar**

## Evidencias previstas en esta carpeta

- [ ] `pytest-verde.txt` — `pytest -v` con 0 fallos
- [ ] `bandit-corregido.txt` — `bandit -r .` sin hallazgos (o solo los aceptados)
- [ ] `trivy-corregido.txt` — `trivy image` de la imagen nueva sin HIGH/CRITICAL
- [ ] `compose-up.txt` — salida de `docker compose up -d` + `curl` a endpoints
- [ ] Capturas: antes/después de cada vulnerabilidad (columnas del `AUDITORIA.md` actualizadas)

> Referencia cruzada: `AUDITORIA.md` (tabla con estado "Corregida") y archivos refactorizados en la raíz (`app.py`, `requirements.txt`, `Dockerfile`, `docker-compose.yml`).