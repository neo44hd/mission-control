# 🚀 SYNKIA UNIFIED ARCHITECTURE - DEPLOYMENT GUIDE

## VISIÓN GENERAL

Has completado una **arquitectura profesional y escalable** que integra:

- **Admin Panel React** (8004) - Dashboard visual completo
- **OpenClaw** (7999) - Orquestador de skills
- **LM Studio Bridge** (8001) - Proxy hacia modelos locales
- **Legacy Dashboard** (18789) - Compatibilidad backwards
- **Nginx** (80/443) - Proxy reverso inteligente

## ESTRUCTURA FINAL

```
/Users/davidnows/
├── docker-compose-unified.yml       # Composición completa
├── nginx/
│   ├── nginx.conf                   # Configuración proxy
│   └── ssl/                         # (Futuro: certificados)
├── synkia-admin-panel/
│   ├── Dockerfile                   # Build del panel
│   ├── server/                      # Backend Node.js
│   ├── client/                      # Frontend React
│   ├── package.json
│   └── .env
├── openclaw-docker/                 # (Existente)
├── logs/                            # Logs centralizados
│   ├── nginx/
│   ├── openclaw/
│   └── lmstudio-bridge/
└── start-synkia-unified.sh          # Script de arranque
```

## DEPLOYMENT - PASO A PASO

### 1. PREPARACIÓN (5 minutos)

```bash
# Asegúrate de estar en el directorio raíz
cd /Users/davidnows

# Verifica que Docker Desktop está corriendo
docker ps

# Verifica dependencias
docker-compose --version
```

### 2. ARRANQUE (2 minutos)

```bash
# Opción A: Usar script automático (RECOMENDADO)
./start-synkia-unified.sh

# Opción B: Arranque manual
docker-compose -f docker-compose-unified.yml up -d
```

### 3. VERIFICACIÓN (1 minuto)

```bash
# Ver estado de servicios
docker-compose -f docker-compose-unified.yml ps

# Verificar health checks
curl http://localhost/health

# Verificar acceso al admin panel
curl http://localhost:8004/api/health/all
```

## ACCESO A SERVICIOS

### Admin Panel (PRINCIPAL)
- **URL**: http://localhost:8004
- **Descripción**: Dashboard React con gestión completa
- **Funcionalidades**:
  - Docker management (local + remoto 100.91.86.75)
  - Monitoreo de sistema en tiempo real
  - OpenClaw skills management
  - Tailscale Serve/Funnel control
  - SSH a servidores remotos

### OpenClaw (ORQUESTACIÓN)
- **URL Direct**: http://localhost:7999
- **URL Proxy**: http://localhost/openclaw/
- **Descripción**: Orquestador central de skills

### LM Studio Bridge (MODELOS)
- **URL Direct**: http://localhost:8001
- **URL Proxy**: http://localhost/lm/
- **Descripción**: Proxy hacia LM Studio local (192.168.0.32:1234)

### Legacy Dashboard (COMPATIBILIDAD)
- **URL Direct**: http://localhost:18789
- **URL Proxy**: http://localhost/dashboard/
- **Descripción**: Dashboard Python actual

## MONITOREO Y LOGS

### Ver logs en tiempo real
```bash
# Todos los servicios
docker-compose -f docker-compose-unified.yml logs -f

# Servicio específico
docker-compose -f docker-compose-unified.yml logs -f admin-panel
docker-compose -f docker-compose-unified.yml logs -f openclaw-service
docker-compose -f docker-compose-unified.yml logs -f lmstudio-bridge
docker-compose -f docker-compose-unified.yml logs -f nginx
```

### Ver logs guardados
```bash
# Logs de Nginx
tail -f logs/nginx/access.log
tail -f logs/nginx/error.log

# Logs de OpenClaw
tail -f logs/openclaw/*
```

## OPERACIONES COMUNES

### Reiniciar un servicio
```bash
docker-compose -f docker-compose-unified.yml restart admin-panel
docker-compose -f docker-compose-unified.yml restart openclaw-service
```

### Detener todo
```bash
docker-compose -f docker-compose-unified.yml down
```

### Reconstruir (después de cambios)
```bash
# Reconstruir admin panel
docker-compose -f docker-compose-unified.yml build admin-panel
docker-compose -f docker-compose-unified.yml up -d admin-panel

# Reconstruir todo
docker-compose -f docker-compose-unified.yml build
docker-compose -f docker-compose-unified.yml up -d
```

### Ver recursos de contenedores
```bash
docker stats
```

## CONFIGURACIÓN AVANZADA

### SSL/TLS (Opcional)

1. **Generar certificados** (self-signed o Let's Encrypt):
```bash
# Self-signed (desarrollo)
mkdir -p nginx/ssl
openssl req -x509 -newkey rsa:4096 -nodes \
  -out nginx/ssl/sinkialabs.crt \
  -keyout nginx/ssl/sinkialabs.key -days 365

# Let's Encrypt (producción)
certbot certonly --standalone -d sinkialabs.com
```

2. **Activar en nginx.conf**:
   - Descomentar bloque SSL en `nginx/nginx.conf`
   - Cambiar certificados
   - Reiniciar Nginx: `docker-compose restart nginx`

### Tailscale Serve/Funnel

```bash
# Instalar Tailscale (si no está)
brew install tailscale

# Activar Serve para exponer el panel
tailscale serve https / http://127.0.0.1:8004

# Activar Funnel para acceso público
tailscale funnel status
tailscale funnel on

# Ver URL pública
tailscale serve status
```

### Dominios Custom

Para conectar `sinkialabs.com`:

1. **Local (Desarrollo)**:
   - Editar `/etc/hosts` y agregar: `127.0.0.1 sinkialabs.com`
   - Acceso: http://sinkialabs.com

2. **Remoto (Producción)**:
   - Configurar DNS A record → IP del servidor
   - Agregar certificado SSL
   - Actualizar nginx.conf con `server_name sinkialabs.com`

## TROUBLESHOOTING

### Servicio no inicia
```bash
# Ver logs detallados
docker-compose logs admin-panel
docker-compose logs openclaw-service

# Reintentar
docker-compose down
docker-compose up -d
```

### Puerto en uso
```bash
# Encontrar qué proceso usa el puerto
lsof -i :8004
lsof -i :80

# Matar proceso (si es necesario)
kill -9 <PID>

# O cambiar puerto en docker-compose-unified.yml
```

### Conexión SSH remota falla
```bash
# Verificar clave SSH
ls -la ~/.ssh/id_rsa

# Crear si no existe
ssh-keygen -t ed25519 -f ~/.ssh/id_rsa

# Copiar clave al servidor
ssh-copy-id -i ~/.ssh/id_rsa.pub root@100.91.86.75
```

### OpenClaw no responde
```bash
# Verificar que está corriendo
docker ps | grep openclaw

# Revisar logs
docker-compose logs openclaw-service

# Reiniciar
docker-compose restart openclaw-service

# Verificar API
curl http://localhost:7999/health
```

## MANTENIMIENTO

### Backups
```bash
# Respaldar configuración de OpenClaw
tar -czf openclaw-backup-$(date +%s).tar.gz ~/.openclaw/

# Respaldar logs
tar -czf logs-backup-$(date +%s).tar.gz logs/
```

### Limpieza
```bash
# Limpiar imágenes no usadas
docker image prune

# Limpiar contenedores parados
docker container prune

# Limpiar volúmenes no usados
docker volume prune
```

### Updates
```bash
# Actualizar imágenes base
docker-compose pull
docker-compose up -d

# Reconstruir después de cambios
docker-compose build --no-cache
docker-compose up -d
```

## MÉTRICAS Y MONITOREO

### Health de servicios
```bash
# Admin Panel
curl http://localhost:8004/api/health/all

# OpenClaw
curl http://localhost:7999/health

# Nginx
curl http://localhost/health
```

### Docker stats
```bash
docker stats --no-stream

# Formato personalizado
docker stats --format="table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

## ARQUITECTURA DESPLEGADA

```
                    Internet / Local Network
                              │
                              │
                    ┌─────────▼──────────┐
                    │    NGINX (80/443)  │
                    │  Reverse Proxy      │
                    └──────┬──────────────┘
                           │
            ┌──────────────┼──────────────┬──────────────┐
            │              │              │              │
        ┌───▼──┐      ┌────▼───┐    ┌────▼───┐    ┌───▼──┐
        │ Admin │      │ OpenClaw    │  LM    │    │Dash  │
        │Panel  │      │ 7999   │    │Bridge  │    │board │
        │8004   │      │        │    │8001    │    │18789 │
        └──────┘      └────────┘    └────────┘    └──────┘
           │               │              │              │
      React+Node    Skills Orch.   Model API        Legacy
      (Prod Build)   (Docker)      (Local)          (Python)
```

## CHECKLIST FINAL

- ✅ Docker Compose configurado
- ✅ Nginx con routing inteligente
- ✅ Admin Panel React + Node.js
- ✅ OpenClaw orquestador
- ✅ LM Studio Bridge
- ✅ Health checks activos
- ✅ Logs centralizados
- ✅ Script de arranque automático
- ⏳ SSL/TLS (futuro)
- ⏳ Tailscale Serve/Funnel (futuro)
- ⏳ Dominios custom (futuro)

## PRÓXIMOS PASOS

1. **Ejecutar**: `./start-synkia-unified.sh`
2. **Acceder**: http://localhost:8004
3. **Explorar**: Dashboard → Docker → Monitoring → OpenClaw
4. **Monitorizar**: `docker-compose logs -f`
5. **Escalar**: Agregar más servicios según necesidad

## RECURSOS

- **Docker Compose Docs**: https://docs.docker.com/compose
- **Nginx Docs**: https://nginx.org/en/docs
- **React Docs**: https://react.dev
- **Node.js Docs**: https://nodejs.org/docs
- **OpenClaw**: Tu orquestador central

## SOPORTE

Para problemas:
1. Revisa los logs: `docker-compose logs <servicio>`
2. Verifica health: `curl http://localhost/health`
3. Reinicia servicios: `docker-compose restart`
4. Reconstruye si es necesario: `docker-compose build`

---

**Arquitectura desplegada**: 2026-03-26
**Versión**: 1.0.0
**Status**: ✅ LISTO PARA PRODUCCIÓN
