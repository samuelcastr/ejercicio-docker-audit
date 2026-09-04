# Fase 3 — Pipeline GitHub Actions en verde

**Estado: ⏳ Pendiente de ejecutar**

## Evidencias previstas en esta carpeta

- [ ] `workflow-verde.png` — Screenshot de GitHub Actions: jobs `test`, `bandit`, `trivy`, `deploy` en verde
- [ ] `log-deploy.txt` — Paso `deploy` con `docker compose up -d` + `nginx reload` OK
- [ ] `url-workflow.txt` — URL del último run del workflow

> El workflow se define en `.github/workflows/ci-cd.yml`. Requiere secrets del repo (`EC2_HOST`, `EC2_USER`, `EC2_SSH_KEY`).