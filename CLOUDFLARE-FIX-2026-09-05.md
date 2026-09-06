# 🛠️ Cloudflare 502 Fix — api.sinkialabs.com

**Status**: ✅ **RESUELTO Y VERIFICADO**
**Fecha**: 2026-09-05 / 2026-09-06 (verificación final)
**Rama de contexto**: `synkia-recovery-2026-09-05`
**Issue**: `api.sinkialabs.com` devolvía **502 Bad Gateway**; el resto de subdominios de `sinkialabs.com` funcionaban con normalidad.
**Ticket relacionado**: Sigue al incidente previo documentado en `CLOUDFLARE-FIX-COMPLETE.md` (2026-08-06). Esta es una recurrencia con **causa raíz distinta**, provocada por el cambio de arquitectura del backend (proceso nativo → contenedor Docker).

---

## Diagnóstico

### 1. El túnel de Cloudflare estaba activo

`launchctl print gui/501/com.synkia.cloudflared` mostraba `state = running`,
proceso vivo (PID 1744 al inicio del diagnóstico). El túnel en sí **nunca
estuvo caído**; el error no era de conectividad de Cloudflare.

### 2. Ingress apuntaba a un puerto muerto en el host

`~/.cloudflared/config.yml` tenía:

```yaml
- hostname: api.sinkialabs.com
  service: http://localhost:3001
```

Verificación (`lsof -nP -iTCP:3001 -sTCP:LISTEN`) confirmó que **nada
escuchaba en el puerto 3001 del host**.

### 3. Causa raíz: migración a Docker sin actualizar el ingress

El proceso nativo `sinkia-api` que antes escuchaba directamente en
`localhost:3001` fue reemplazado por el contenedor `sinkia-erp`, que expone
su puerto interno **3001 del contenedor** en el **puerto 3003 del host**:

```
sinkia-erp   Up 22 hours (healthy)   0.0.0.0:3003->3001/tcp
```

`sinkialabs.com` (la raíz) ya apuntaba correctamente a `localhost:3003` y
funcionaba (200 OK). Sólo `api.sinkialabs.com` se quedó apuntando al puerto
viejo tras la migración, sin que nadie actualizara esa entrada del ingress.

---

## Fix aplicado

**Archivo**: `/Users/davidnows/.cloudflared/config.yml` (excluido del repo por `.gitignore`; ver nota al final)

```diff
  - hostname: api.sinkialabs.com
-   service: http://localhost:3001
+   service: http://localhost:3003
```

### Pasos ejecutados

1. **Backup** del config antes de tocar nada:
   `~/.cloudflared/config.yml.bak-20260906-024506`
2. **Confirmación del backend real**: `curl http://localhost:3003/api/health/ping` → `200`
3. **Edición** de la línea de ingress (arriba).
4. **Validación de sintaxis**: `cloudflared tunnel ingress validate` → `OK`
5. **Recarga del túnel** sin downtime largo:
   `launchctl kickstart -k gui/501/com.synkia.cloudflared`
   → nuevo PID `45533`, `state = active` en ambas conexiones del connector.
6. **Verificación pública** de las 21 rutas del ingress.
7. **Verificación funcional en navegador** (Playwright headless) contra
   `sinkialabs.com` para confirmar que la UI renderiza sin pantalla en
   blanco tras el fix (ver sección Validación).

---

## Validación

### Endpoints públicos (curl, 21/21 rutas)

| Hostname | Antes | Después |
|---|---|---|
| `api.sinkialabs.com` | **502** | **200** ✅ |
| `sinkialabs.com`, `www`, `app` | 200 | 200 |
| `hub`, `control`, `mc`, `claw`, `sinkia`, `chat`, `commerce`, `pos`, `qdrant`, `vectors`, `search`, `search-cloud`, `agent`, `n8n` | 200 | 200 |
| `memory`, `odysseus`, `telegram` | 302 (redirect login normal) | 302 |

```bash
curl https://api.sinkialabs.com/api/health/ping
# {"ok":true,"ts":1788655894507}
```

### Verificación funcional en navegador (Playwright headless, UA real)

6 rutas de la SPA verificadas contra `sinkialabs.com`:

```
Rutas verificadas:     6
Sin pantalla en blanco: 6/6
Page errors totales:   0
Failed requests:       0

⚫⚫⚫  PANTALLA EN BLANCO CONFIRMADA RESUELTA  ⚫⚫⚫
```

Renders confirmados con contenido real (charts de Recharts montados,
headings correctos, KPIs con datos):

- `/` → redirige a `/ceodashboard`, 1148 chars, 2 charts, "Panel CEO" + "Mission Control"
- `/ceodashboard` → mismo resultado directo
- `/revodashboard` → 548 chars, 4 charts, "Dashboard Revo Xef"
- `/documentarchive` → 12038 chars, "Archivo Global"
- `/dashboard` → 1188 chars, 1 chart, "CONTROL CENTRAL" con KPIs reales
  (Facturación, Gastos, Margen Bruto, IA Documental, Equipo, Compliance)

Screenshot de referencia capturado durante la verificación mostrando el
Control Central completamente renderizado, sin ningún indicio de pantalla
en blanco ni error JS en consola de aplicación.

---

## Mapa de servicios vigente (post-fix)

| Hostname | Puerto host | Servicio |
|---|---|---|
| `sinkialabs.com` / `www` / `app` / **`api`** | `3003` | `sinkia-erp` (Docker, ERP unificado) |
| `hub` | `18791` | Hub |
| `memory` | `9600` | Memory service |
| `control` | `7777` | Control panel |
| `mc` | `5173` | Vite dev server (Mission Control) |
| `claw` / `search-cloud` / `agent` | `3120` | OpenClaw / search cloud |
| `sinkia` | `3000` | (servicio auxiliar) |
| `chat` | `3030` | Open WebUI |
| `commerce` / `pos` | `4400` | Commerce/POS |
| `qdrant` / `vectors` | `6335` | Qdrant vector DB |
| `search` | `8888` | SearXNG |
| `odysseus` | `7080` | Odysseus |
| `n8n` | `5678` | n8n workflows |
| `telegram` | `8787` | Telegram bot API |

**Nota importante**: `sinkialabs.com`, `www`, `app` y `api` comparten el
mismo backend Docker (`sinkia-erp` en `:3003`). No hay ya un proceso
`sinkia-api` nativo separado en `:3001` — cualquier documentación previa
que lo mencione (incluido `CLOUDFLARE-FIX-COMPLETE.md` de 2026-08-06) está
desactualizada respecto a la arquitectura actual.

---

## Comandos de monitorización

### Verificar estado del túnel
```bash
launchctl print gui/$(id -u)/com.synkia.cloudflared | grep -E "pid|state"
```

### Verificar puertos locales activos
```bash
for port in 3003 18791 9600 7777 5173 3120 3000 3030 4400 6335 8888 7080 5678 8787; do
  nc -z -w1 localhost $port && echo "$port UP" || echo "$port DOWN"
done
```

### Verificar todas las URLs públicas de una vez
```bash
for h in sinkialabs.com api.sinkialabs.com hub.sinkialabs.com mc.sinkialabs.com; do
  echo "$h -> $(curl -s -o /dev/null -w '%{http_code}' --max-time 6 https://$h/)"
done
```

### Recargar el ingress tras editar config.yml
```bash
cloudflared --config ~/.cloudflared/config.yml tunnel ingress validate
launchctl kickstart -k gui/$(id -u)/com.synkia.cloudflared
```

---

## Lección aprendida / prevención

**Causa de fondo**: al dockerizar un servicio y remapear su puerto (`3001`
interno → `3003` en el host), nadie actualizó la entrada correspondiente
del ingress de Cloudflare para ese subdominio específico (`api.*`), aunque
sí se actualizó para el dominio raíz.

**Recomendación**: cuando se migra un servicio de proceso nativo a
contenedor Docker con remapeo de puerto, revisar **todas** las entradas de
`~/.cloudflared/config.yml` que apunten a ese servicio, no sólo la
principal. Un `grep -n "3001\|3003" ~/.cloudflared/config.yml` tras cada
migración de puerto habría detectado esta discrepancia antes de que
llegara a producción.

---

## Nota sobre el archivo de configuración

`.cloudflared/config.yml` está deliberadamente excluido del repositorio
por `.gitignore` (línea 94: `.cloudflared/config.yml`), junto con los
credenciales del túnel (`.cloudflared/*.json`, línea 95). Esta es una
decisión de seguridad ya existente en el repo y se ha respetado: **no se
ha forzado su inclusión**. El backup local del config aplicado queda en
`~/.cloudflared/config.yml.bak-20260906-024506` para referencia y rollback
si hiciera falta.

---

## Cierre de la incidencia

- [x] Causa raíz identificada (ingress desactualizado tras migración a Docker)
- [x] Fix aplicado con backup previo del config
- [x] Validación de sintaxis (`ingress validate` → OK)
- [x] Túnel recargado sin downtime largo (`launchctl kickstart -k`)
- [x] 21/21 URLs públicas verificadas por curl
- [x] Verificación funcional en navegador (Playwright headless, 0 page errors, 0 failed requests)
- [x] Mapa de servicios actualizado y documentado
- [x] Lección aprendida registrada para prevenir recurrencia

**Estado final**: ✅ Incidencia cerrada. Todos los subdominios de
`sinkialabs.com` responden correctamente y la aplicación renderiza sin
errores en el navegador.
