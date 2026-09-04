# Fase 4 — Despliegue en EC2 + proxy 80/443 + subdominios

**Estado: ⏳ Pendiente de ejecutar**

## Evidencias previstas en esta carpeta

- [ ] `etc-hosts.txt` — Las 3 líneas de `/etc/hosts` → IP de la EC2
- [ ] `curl-subdominios.txt` — `curl -I` a `api.`, `dizzle.`, `kuma.` (200 + redirect HTTP→HTTPS)
- [ ] `nginx-t.txt` — Salida de `nginx -t` (syntax ok)
- [ ] `docker-ps-ec2.txt` — `docker ps` en la EC2 con los contenedores corriendo
- [ ] Capturas del navegador: `https://api.<dominio>`, `https://dizzle.<dominio>`, `https://kuma.<dominio>`

> Servicios corriendo en la EC2; resolución de dominio local vía `/etc/hosts` + certificados autofirmados.