# Configuración de Puertos — SynK-IA

## Puertos Actuales

| Servicio | Puerto | URL | Descripción |
|----------|--------|-----|-------------|
| **sinkia-next** | 9002 | http://localhost:9002 | Panel administrativo + React SPA |
| **sinkia-commerce** | 4400 | http://localhost:4400 | Servidor POS/Commerce |
| Commerce Panel | 9002 | http://localhost:9002/commerce.html | Panel de control de commerce (proxied) |
| Ollama | 11434 | http://localhost:11434 | LLM local (llama3.2:3b) |
| LM Studio | 4000 | http://127.0.0.1:4000/v1 | Modelos locales avanzados |
| Open WebUI | 3030 | http://localhost:3030 | Interfaz Ollama |
| n8n | 5678 | http://localhost:5678 | Automatización (proxied en /n8n) |
| SearXNG | 8888 | http://localhost:8888 | Búsqueda web (proxied en /searxng) |

## Notas Importantes

### Puerto 3001
- **Ocupado por OrbStack** (contenedor/virtualizador de Docker)
- **NO usar** para sinkia-next
- sinkia-next ahora usa **puerto 9002** por defecto

### Configuración de Puertos

#### sinkia-next (.env)
```bash
BACKEND_URL=http://localhost:9002
PORT=9002  # default en server/index.js
```

#### sinkia-commerce (.env)
```bash
PORT=4400
```

### Inicio de Servicios

**sinkia-next** (puerto 9002):
```bash
cd /Users/davidnows/sinkia-next
npm start  # Usa PORT=9002 automáticamente
```

O explícitamente:
```bash
cd /Users/davidnows/sinkia-next
PORT=9002 npm start
```

**sinkia-commerce** (puerto 4400):
```bash
cd /Users/davidnows/sinkia-commerce-server
npm start
```

## Commerce Panel Integration

El panel de commerce en `http://localhost:9002/commerce.html` se comunica con sinkia-commerce (puerto 4400) a través de un **proxy de mismo origen** en sinkia-next:

- **Endpoint del proxy**: `/api/commerce-proxy/api/*`
- **Redirige a**: `http://localhost:4400/api/*`
- **Ventaja**: Evita CORS en el navegador

### Flujo:
```
Browser @ localhost:9002
    ↓
fetch('/api/commerce-proxy/api/health')
    ↓
sinkia-next proxy route
    ↓
curl http://localhost:4400/api/health
    ↓
sinkia-commerce
```

## Verificación

```bash
# sinkia-next
curl http://localhost:9002/api/health

# sinkia-commerce (directo)
curl http://localhost:4400/api/health

# sinkia-commerce (vía proxy en sinkia-next)
curl http://localhost:9002/api/commerce-proxy/api/health
```

## Historial de Cambios

- **2026-06-30**: 
  - Cambio de puerto 3001 → 9002 (OrbStack ocupa 3001)
  - Implementación de proxy `/api/commerce-proxy` en sinkia-next
  - Actualización de `.env` y `server/index.js` con PORT=9002 por defecto
