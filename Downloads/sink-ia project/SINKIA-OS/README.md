# 🚀 SINKIA-OS — Ecosistema Unificado

**Single pane of glass** para orquestar todos los componentes de sink-ia en un ecosistema coherente.

## Arquitectura

```
┌──────────────────────────────────────────────────────────────┐
│        SINKIA-OS — DASHBOARD & SERVICIOS  (:3000)            │
│   Overview │ ERP/TPV │ HEAVEN │ Remote │ Memory │ Models     │
├───────────┬─────────┬────────┬────────┬────────┬─────────────┤
│ GUI (Next)│ ERP/TPV │HEAVEN  │ Remote │sinkMAID│ Stack Svcs  │
│ :3000     │ :3003   │:8009-13│ :3334  │ :8020  │ (PM2/legacy)│
├───────────┴─────────┴────────┴────────┴────────┴─────────────┤
│                  INFRAESTRUCTURA COMPARTIDA                  │
│ PostgreSQL:5432│ Redis:6379│ Qdrant:6335│ Ollama:11434      │
│ (healthcheck: :8080)                                         │
└──────────────────────────────────────────────────────────────┘
```

## Componentes & Puertos

### Servicios Principales (Docker Compose)

| # | Servicio | Puerto Host→Contenedor | Descripción | Estado |
|---|----------|----------------------|-------------|--------|
| 1 | **GUI (Sinkia)** | `3000→3000` | Next.js dashboard | ✅ Operativo |
| 2 | **JARVIS Core** | `8080→8080` | API de insights y orquestación | ✅ Operativo |
| 3 | **HEAVEN Platform** | `8009→8009`, `8010→8010`, `8012→8012`, `8013→8013` | Ecosystem Agent + Hub + Search | ✅ Operativo |
| 4 | **SYNK-IA ERP/TPV** | `3003→3001` | Gestión: TPV, pedidos, facturas | ✅ Operativo |
| 5 | **Models Centralizer** | `9502→9502` | Proxy unificado Ollama/APIs externas | ✅ Operativo |
| 6 | **sinkMAIND Memory** | `8020→8020` | Motor memoria: búsqueda + embeddings | ⚠️ No implementado |
| 7 | **Remote Machine** | `3334→3333` | Acceso remoto (archivos, terminal) | ⚠️ Sin endpoint health |

### Infraestructura (Base de Datos & Cache)

| # | Servicio | Puerto Host | Descripción | Estado |
|---|----------|-----------|-------------|--------|
| 8 | **PostgreSQL 16** | `5432` | BD principal (170 registros de ventas) | ✅ Healthy |
| 9 | **Redis 7** | `6379` | Cache y colas async | ✅ Healthy |
| 10 | **Qdrant (Legacy)** | `6333` | BD vectorial stack legacy | ✅ Healthy |
| 11 | **Qdrant (SINKIA-OS)** | `6335` | BD vectorial para este stack | ✅ Healthy |
| 12 | **Ollama** | `11434` | Modelos locales (llama3.2, etc.) | ✅ Operativo |

## Quick Start

```bash
cd "/Users/davidnows/Downloads/sink-ia project/SINKIA-OS"

# 1. Iniciar TODOS los servicios (con datos reales preimportados)
./start-all.sh

# 2. Ver estado
./status.sh

# 3. Abrir dashboard
open http://localhost:3000
```

## URLs de Acceso

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **Dashboard** | http://localhost:3000 | GUI principal (Next.js) |
| **JARVIS API** | http://localhost:8080/api/health | API de insights |
| **HEAVEN Agent** | http://localhost:8009/health | Ecosystem agent |
| **HEAVEN Dashboard** | http://localhost:8010 | Hub y visualización |
| **ERP/TPV** | http://localhost:3003 | Sistema de gestión |
| **Ollama** | http://localhost:11434/api/tags | Modelos disponibles |
| **PostgreSQL** | localhost:5432 | (usuario: sinkia, BD: sinkia_os) |
| **Redis** | localhost:6379 | (sin autenticación) |
| **Qdrant** | http://localhost:6335 | (BD vectorial SINKIA-OS) |

## Comandos Principales

| Comando | Descripción |
|---------|-------------|
| `./start-all.sh` | **[RECOMENDADO]** Levanta todo: infra → servicios → importa datos |
| `./stop.sh` | Para todos los servicios (datos persisten) |
| `./status.sh` | Diagnóstico: estado contenedores, HTTP health, BD, archivos |
| `docker compose logs -f [svc]` | Logs en vivo (ej: `docker compose logs -f sinkia-heaven`) |
| `docker compose restart [svc]` | Reiniciar un servicio (ej: `docker compose restart sinkia-erp`) |
| `docker compose ps` | Lista todos los contenedores y su estado |

## Configuración

Edita `.env` para personalizar:

```bash
# Base de datos
POSTGRES_PASSWORD=sinkia_secret_2026

# Modelos & APIs
AI_MODEL=llama3.2
OLLAMA_URL=http://localhost:11434
OLLAMA_NUM_PARALLEL=1
OLLAMA_MAX_LOADED_MODELS=1

# APIs externas (opcionales)
OPENROUTER_API_KEY=...
ANTHROPIC_API_KEY=...
GOOGLE_API_KEY=...

# Revo TPV (para ERP)
REVO_MERCHANT_ID=...
REVO_API_KEY=...

# Telegram Bot
TELEGRAM_BOT_TOKEN=...
```

## Servicios Legacy (Fuera de Docker — PM2/launchd)

El stack original tiene 14 servicios que siguen corriendo fuera de Docker:
- **ruflo-orchestrator** (:8081) — Orquestación de flujos
- **synkia-trends** (:9700) — Tendencias de mercado
- **mission-control** (:9302) — Centro de control
- **BATCAVE** (:3020) — Admin panel
- **BrainCC** (:3333) — ⚠️ Nota: SINKIA-OS usa :3334 para remote-machine
- **hermes-bus** (:8082) — Message bus
- **velin-dabot** — Bot Telegram
- **mlx-local-server** (:4001) — Modelos MLX
- **watchdog** + **health-probe** — Monitoreo

**Próximo paso:** Migración gradual de estos servicios a Docker Compose.

## Troubleshooting

### Un servicio no arranca
```bash
# Ver logs (últimas 50 líneas)
docker compose logs sinkia-heaven --tail=50

# Seguimiento en vivo
docker compose logs -f sinkia-heaven

# Entrar al contenedor para debuggear
docker exec -it sinkia-heaven bash

# Reiniciar solo ese servicio
docker compose restart sinkia-heaven
```

### Reconstruir una imagen (si tiene bugs o deps faltantes)
```bash
# Fuerza rebuild sin caché
docker compose build --no-cache heaven-platform

# Levanta nuevamente
docker compose up -d heaven-platform
```

### Conflictos de puerto
Si ves `Bind for 0.0.0.0:XXXX failed`, significa otro proceso usa ese puerto:

```bash
# Encuentra qué usa el puerto (ej: 3000)
lsof -nP -iTCP:3000 -sTCP:LISTEN

# Mata el proceso si es necesario
kill -9 <PID>
```

### Base de datos corrupta o desincronizada
```bash
# Ver estado de la DB
docker exec sinkia-postgres psql -U sinkia -d sinkia_os -c "SELECT COUNT(*) FROM sales_daily;"

# Reimportar CSV de ventas
python3 scripts/seed-from-csv.py
docker exec -i sinkia-postgres psql -U sinkia -d sinkia_os < data/real/datos/ventas-reales_import.sql
```

### Reset completo (⚠️ Pierde todos los datos)
```bash
./stop.sh
docker compose down -v  # Elimina contenedores Y volúmenes
./start-all.sh          # Reconstruye e importa datos de nuevo
```

## Conflictos Resueltos (Agosto 2026)

### Puertos y Contenedores
- ✅ **Qdrant:** Renombrado a `sinkia-os-qdrant` (puerto 6335) para coexistencia con stack legacy
- ✅ **ERP:** Movido a puerto 3003 (3001 ocupado por `sinkia-api` legacy)
- ✅ **Remote-Machine:** Movido a puerto 3334 (3333 ocupado localmente)
- ✅ **Unified Dashboard:** Movido a puerto 3004 (3000 para GUI)
- ✅ **HEAVEN:** Ahora escucha en `0.0.0.0` (accesible desde host)

### Dependencias
- ✅ **ERP:** Agregadas `axios`, `gray-matter`, `lru-cache`, `uuid`
- ✅ **HEAVEN:** Removido `airllm==0.2.1` y `ollama==0.1.15` (no existen en PyPI)
- ✅ **Dockerfiles:** Corregida sintaxis COPY y npm install
- ✅ **start-all.sh:** Ahora resiliente (no aborta en primer fallo)

### Datos
- ✅ **PostgreSQL:** 170 registros de ventas importados
- ✅ **Esquema:** Creado con 10 tablas principales

## Licencia

UNLICENSED — Uso interno Chicken Palace Ibiza / sink-ia labs
