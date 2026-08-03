# 🎯 SYNKIA - UNIFIED INFRASTRUCTURE ORCHESTRATION

**Versión**: 1.0.0 | **Status**: ✅ PRODUCCIÓN | **Actualizado**: 2026-03-26

Un sistema profesional, escalable y completamente integrado para orquestar y gestionar infraestructura, skills IA, modelos locales y servicios en tiempo real.

## 🚀 INICIO RÁPIDO

```bash
# 1. Asegúrate de estar en el directorio correcto
cd /Users/davidnows

# 2. Inicia todo con el script automático
./start-synkia-unified.sh

# 3. Accede al panel
open http://localhost:8004
```

**Tiempo de deploy**: ~2 minutos | **Status**: Verás health checks en tiempo real

## 🏗️ ARQUITECTURA

```
┌─────────────────────────────────────────────┐
│          NGINX (80/443)                     │
│  Reverse Proxy + Load Balancer              │
└────────────┬────────────────────────────────┘
             │
    ┌────────┼────────┬─────────┬───────────┐
    │        │        │         │           │
┌───▼──┐ ┌──▼───┐ ┌──▼──┐ ┌────▼──┐  ┌───▼──┐
│Admin │ │OpenClaw   │LM  │Legacy │  │API   │
│Panel │ │(7999)     │Bridge  │Dash  │      │
│8004  │ │           │8001  │18789 │8002  │
└──────┘ └────────┘ └─────┘ └──────┘  └──────┘
   │        │         │        │         │
React    Skills    Models   Python   Database
+Node    Orch.     Local    Compat.  Services
```

## 📦 SERVICIOS INTEGRADOS

| Servicio | Puerto | Descripción | Status |
|----------|--------|-------------|--------|
| **Admin Panel** | 8004 | Dashboard React + Node.js | ✅ |
| **OpenClaw** | 7999 | Orquestador de skills | ✅ |
| **LM Studio Bridge** | 8001 | Proxy a modelos locales | ✅ |
| **Backend API** | 8002 | Express.js (Docker, SSH, Monitoring) | ✅ |
| **Legacy Dashboard** | 18789 | Dashboard Python | ✅ |
| **Nginx** | 80/443 | Proxy reverso | ✅ |

## 🎨 FUNCIONALIDADES PRINCIPALES

### Admin Panel
- **Dashboard**: Estadísticas en tiempo real, gráficos CPU/memoria
- **Docker**: Gestión de contenedores, imágenes, logs en vivo
- **Monitoreo**: CPU, memoria, disco, procesos, red con gráficos
- **Servidores**: SSH a máquinas locales y remota (100.91.86.75)
- **OpenClaw**: Editar IDENTITY, USER, SOUL; gestionar skills
- **Tailscale**: Control de Serve/Funnel para acceso remoto

### OpenClaw
- Orquestación central de skills
- IDENTITY, USER, SOUL configuration
- API RESTful para automations
- Integración con LM Studio para modelos

### LM Studio Bridge
- Proxy transparente a LM Studio local (192.168.0.32:1234)
- Fallback automático a LM Link Cloud
- Manejo de timeout para requests largos

## 📂 ESTRUCTURA DE ARCHIVOS

```
/Users/davidnows/
├── docker-compose-unified.yml         # Orquestación de servicios
├── nginx/
│   ├── nginx.conf                     # Routing inteligente
│   └── ssl/                           # (Certificados)
├── synkia-admin-panel/
│   ├── Dockerfile                     # Build multi-stage
│   ├── server/                        # Node.js backend
│   ├── client/                        # React frontend
│   └── package.json
├── openclaw-docker/                   # OpenClaw container
├── logs/                              # Logs centralizados
│   ├── nginx/
│   ├── openclaw/
│   └── lmstudio-bridge/
├── start-synkia-unified.sh            # Script de arranque
├── README.md                          # Este archivo
├── DEPLOYMENT_GUIDE.md                # Guía detallada
└── .env.example                       # Template variables

```

## 🔧 CONFIGURACIÓN

### Variables de Entorno

Copia `.env.example` a `.env` y personaliza:

```bash
cp .env.example .env
```

Variables principales:
```bash
# Docker
DOCKER_HOST=unix:///var/run/docker.sock

# OpenClaw
OPENCLAW_API=http://openclaw-service:7999
OPENCLAW_PORT=7999

# LM Studio
LM_STUDIO_HOST=192.168.0.32
LM_STUDIO_PORT=1234
LM_FALLBACK_API_KEY=1b4b7d8187286903881e7a9edafd2545b

# Servidores
REMOTE_SERVER_IP=100.91.86.75
SSH_KEY_PATH=~/.ssh/id_rsa

# Admin Panel
ADMIN_PORT=8004
ADMIN_SECRET=your-secret-key

# Nginx
NGINX_PORT=80
NGINX_SSL_PORT=443
```

## 📊 RUTAS DE ROUTING

Nginx enruta automáticamente:

```
GET  /                      → Admin Panel (/)
GET  /api/*                 → Backend API (:8002)
GET  /openclaw/*            → OpenClaw (:7999)
GET  /lm/*                  → LM Studio Bridge (:8001)
GET  /dashboard/*           → Legacy Dashboard (:18789)
POST /health                → Health check (Nginx)
```

## 🚨 HEALTH CHECKS

Todos los servicios implementan health checks:

```bash
# Admin Panel
curl http://localhost:8004/api/health/all

# OpenClaw
curl http://localhost:7999/health

# LM Bridge
curl http://localhost:8001/health

# Nginx
curl http://localhost/health
```

## 📝 LOGS

Ver logs en tiempo real:

```bash
# Todos los servicios
docker-compose -f docker-compose-unified.yml logs -f

# Servicio específico
docker-compose logs -f admin-panel
docker-compose logs -f openclaw-service
docker-compose logs -f lmstudio-bridge
docker-compose logs -f nginx
```

## 🔄 OPERACIONES COMUNES

```bash
# Ver estado de servicios
docker-compose -f docker-compose-unified.yml ps

# Reiniciar un servicio
docker-compose restart admin-panel

# Parar todo
docker-compose down

# Reconstruir después de cambios
docker-compose build
docker-compose up -d

# Ver recursos
docker stats
```

## 🛠️ DESARROLLO LOCAL

### Frontend (React)

```bash
cd synkia-admin-panel/client
npm install
npm run dev
```

### Backend (Node.js)

```bash
cd synkia-admin-panel/server
npm install
npm run dev
```

### Docker local

```bash
# Build
docker-compose build --no-cache

# Up con logs
docker-compose up --build

# Desarrollo interactivo
docker-compose up -d
docker-compose logs -f
```

## 🔐 SEGURIDAD

- ✅ SSH keys para acceso remoto
- ✅ Variables de entorno para secrets
- ✅ Health checks para validar servicios
- ⏳ SSL/TLS con Let's Encrypt (futuro)
- ⏳ API authentication (futuro)

## 📱 ACCESO REMOTO

### Via Tailscale (Recomendado)

```bash
# Instalar
brew install tailscale

# Activar Serve
tailscale serve https / http://127.0.0.1:8004

# Ver URL
tailscale serve status
```

### Via dominio custom

1. Editar `/etc/hosts`:
   ```
   127.0.0.1 sinkialabs.com
   ```

2. O configurar DNS A record y SSL

Ver `DEPLOYMENT_GUIDE.md` para detalles completos.

## 🐛 TROUBLESHOOTING

| Problema | Solución |
|----------|----------|
| Puerto en uso | `lsof -i :8004` → `kill -9 <PID>` |
| Servicio no inicia | `docker-compose logs <servicio>` |
| OpenClaw sin respuesta | `docker-compose restart openclaw-service` |
| SSH falla | Verificar `~/.ssh/id_rsa` y keys en servidor |
| LM Studio no responde | Verificar `192.168.0.32:1234` accesible |

Ver `DEPLOYMENT_GUIDE.md` para troubleshooting detallado.

## 📚 DOCUMENTACIÓN

- **DEPLOYMENT_GUIDE.md**: Guía completa de deployment, operación y troubleshooting
- **docker-compose-unified.yml**: Definición de servicios y networking
- **nginx/nginx.conf**: Configuración de proxy y routing
- **synkia-admin-panel/**: Frontend React y backend Node.js

## 🎯 CHECKLIST DE DEPLOYMENT

- ✅ Docker Compose configurado y testeado
- ✅ Nginx con routing inteligente a todos los servicios
- ✅ Admin Panel React con backend Node.js
- ✅ OpenClaw orquestador integrado
- ✅ LM Studio Bridge para modelos locales
- ✅ Health checks automáticos en todos los servicios
- ✅ Logs centralizados y monitoreo
- ✅ Script de arranque automático
- ✅ Documentación completa

## 🚀 PRÓXIMOS PASOS

1. **Ejecutar**: `./start-synkia-unified.sh`
2. **Acceder**: http://localhost:8004
3. **Explorar**: Dashboard → Docker → Monitoring → OpenClaw
4. **Monitorizar**: `docker-compose logs -f`
5. **Escalar**: Agregar servicios según necesidad

## 📞 SOPORTE

Para problemas:

1. Revisa los logs: `docker-compose logs -f`
2. Verifica health: `curl http://localhost/health`
3. Consulta `DEPLOYMENT_GUIDE.md` para troubleshooting
4. Reinicia servicios: `docker-compose restart`

## 📄 LICENCIA

SynkIA Infrastructure Management System - 2026

---

**Última actualización**: 2026-03-26 | **Versión**: 1.0.0 | **Status**: ✅ LISTO PARA PRODUCCIÓN

Para más detalles, ver `DEPLOYMENT_GUIDE.md`
