# 📋 Guía de Despliegue — SINKIA-OS

**Última actualización:** Agosto 16, 2026  
**Estado:** ✅ Operativo (5 servicios principales + infraestructura)

---

## 📊 Tabla de Puertos Completa

| Layer | Servicio | Puerto Host | Puerto Contenedor | Protocolo | Nota |
|-------|----------|------------|------------------|-----------|------|
| **Frontend** | GUI (Sinkia) | 3000 | 3000 | HTTP | Next.js dashboard |
| **API/Orquestación** | JARVIS Core | 8080 | 8080 | HTTP/REST | Healthcheck: `/api/health` |
| **IA Platform** | HEAVEN Agent | 8009 | 8009 | HTTP/REST | Healthcheck: `/health` |
|  | HEAVEN Hub | 8010 | 8010 | HTTP | Dashboard de hub |
|  | HEAVEN Search | 8012 | 8012 | HTTP | Búsqueda y descubrimiento |
|  | HEAVEN Memory | 8013 | 8013 | HTTP | (Opcional, sin chromadb) |
| **ERP/Negocio** | SYNK-IA TPV | 3003 | 3001 | HTTP | Healthcheck: `/api/health` |
| **Modelos** | Models Centralizer | 9502 | 9502 | HTTP | Proxy Ollama/OpenRouter |
| **Remote** | Remote Machine | 3334 | 3333 | HTTP | Acceso remoto (sin health real) |
| **Memory** | sinkMAIND | 8020 | 8020 | HTTP | (No implementado) |
| **BD Principal** | PostgreSQL | 5432 | 5432 | TCP | Usuario: `sinkia`, BD: `sinkia_os` |
| **Cache** | Redis | 6379 | 6379 | TCP | Sin autenticación |
| **Vector DB (Legacy)** | Qdrant Legacy | 6333 | 6333 | HTTP | Stack `davidnows` (no SINKIA-OS) |
| **Vector DB (SINKIA-OS)** | Qdrant SINKIA | 6335 | 6333 | HTTP | Contenedor: `sinkia-os-qdrant` |
| **LLM Local** | Ollama | 11434 | 11434 | HTTP | API: `/api/tags`, `/api/generate` |

---

## 🚀 Inicio Rápido

### Prerrequisitos
```bash
# Verificar Docker
docker --version  # ≥ 20.10
docker compose --version  # ≥ 2.0

# Verificar espacio en disco (mínimo 50GB)
df -h
```

### Desplegar (3 pasos)

#### 1. Navegar al directorio
```bash
cd "/Users/davidnows/Downloads/sink-ia project/SINKIA-OS"
```

#### 2. Iniciar todos los servicios
```bash
# Opción A: Script integrado (RECOMENDADO)
./start-all.sh
# → Infraestructura ✅
# → Servicios principales ✅
# → Import datos CSV ✅
# → Health checks ✅

# Opción B: Manual (paso a paso)
docker compose build heaven-platform synkia-erp remote-machine sinkmaind-memory
docker compose up -d postgres redis ollama qdrant
sleep 10
docker compose up -d heaven-platform jarvis sinkia-gui synkia-erp models-centralizer remote-machine
```

#### 3. Verificar estado
```bash
./status.sh

# Expected output:
# ✅ JARVIS Core (http://localhost:8080/api/health)
# ✅ GUI (http://localhost:3000)
# ✅ ERP (http://localhost:3003/api/health)
# ✅ Ollama (http://localhost:11434/api/tags)
# ✅ HEAVEN (http://localhost:8009/health)
```

#### 4. Abrir en navegador
```bash
open http://localhost:3000
```

---

## 📍 URLs de Acceso Directo

```bash
# Frontend
open http://localhost:3000          # GUI principal

# Backend APIs
curl http://localhost:8080/api/health     # JARVIS
curl http://localhost:8009/health         # HEAVEN Agent
curl http://localhost:3003/api/health     # ERP
curl http://localhost:11434/api/tags      # Ollama

# Dashboards & Admin
open http://localhost:8010         # HEAVEN Hub
open http://localhost:8012         # HEAVEN Search

# Bases de datos (CLI)
psql -h localhost -U sinkia -d sinkia_os    # PostgreSQL
redis-cli -h localhost                      # Redis
curl http://localhost:6335/healthz          # Qdrant SINKIA-OS
```

---

## 🔧 Problemas Comunes & Soluciones

### Error: "Port 3000 already in use"
```bash
# Identifica el proceso
lsof -nP -iTCP:3000 -sTCP:LISTEN

# Opción 1: Cambiar puerto en docker-compose.yml
sed -i 's/"3000:3000"/"3001:3000"/' docker-compose.yml
./start-all.sh

# Opción 2: Matar el proceso existente
kill -9 <PID>
./start-all.sh
```

### HEAVEN no responde desde el host
```bash
# Verificar que escucha en 0.0.0.0
docker exec sinkia-heaven netstat -tlnp | grep 8009
# Expected: 0.0.0.0:8009

# Si no: actualizar y rebuildar
docker compose down sinkia-heaven
docker compose build --no-cache heaven-platform
docker compose up -d heaven-platform
```

### PostgreSQL: base de datos vacía
```bash
# Reimportar esquema
docker exec -i sinkia-postgres psql -U sinkia -d sinkia_os < scripts/seed-database.sql

# Reimportar ventas
python3 scripts/seed-from-csv.py
docker exec -i sinkia-postgres psql -U sinkia -d sinkia_os < data/real/datos/ventas-reales_import.sql

# Verificar
docker exec sinkia-postgres psql -U sinkia -d sinkia_os -c "SELECT COUNT(*) FROM sales_daily;"
# Expected: 170
```

### ERP/HEAVEN en bucle de reinicio
```bash
# Ver logs del último error
docker logs sinkia-erp --tail=50
docker logs sinkia-heaven --tail=50

# Si falta dependencia:
docker compose build --no-cache synkia-erp  # O heaven-platform
docker compose up -d synkia-erp

# Si corrupción: rebuild total
docker compose down synkia-erp
rm -rf ~/.docker/containers/*erp*  # ⚠️ Fuerte
docker compose up -d synkia-erp
```

### Qdrant unhealthy
```bash
# Verificar healthcheck
curl -v http://localhost:6335/healthz

# Recrear volumen
docker compose down sinkia-os-qdrant
docker volume rm sinkia-os_qdrant_data 2>/dev/null || true
docker compose up -d sinkia-os-qdrant
```

---

## 📦 Gestión de Datos

### Backup de PostgreSQL
```bash
# Full dump
docker exec sinkia-postgres pg_dump -U sinkia sinkia_os > backup_$(date +%s).sql

# Desde host
pg_dump -h localhost -U sinkia sinkia_os > backup.sql
```

### Restore desde backup
```bash
# Crear BD si no existe
docker exec sinkia-postgres createdb -U sinkia sinkia_os 2>/dev/null || true

# Restaurar
docker exec -i sinkia-postgres psql -U sinkia sinkia_os < backup.sql
```

### Exportar datos para análisis
```bash
# CSV de ventas
docker exec sinkia-postgres psql -U sinkia sinkia_os \
  -c "COPY sales_daily TO STDOUT WITH CSV HEADER;" > sales.csv

# JSON de insights
docker exec sinkia-postgres psql -U sinkia sinkia_os \
  -c "SELECT row_to_json(t) FROM jarvis_insights t;" > insights.json
```

---

## 🔄 Ciclo de Vida de Contenedores

### Start (primera vez)
```bash
./start-all.sh
# Tiempo esperado: ~2-5 min (primer build)
```

### Stop (sin perder datos)
```bash
./stop.sh
# O manualmente:
docker compose stop
```

### Restart (cuando fallan servicios)
```bash
# Un servicio
docker compose restart sinkia-heaven

# Todos
docker compose restart
```

### Remove (reset de datos)
```bash
# ⚠️ Destructivo — pierde TODO
./stop.sh
docker compose down -v
./start-all.sh
```

### Rebuild (si hay cambios en código/Dockerfile)
```bash
# Un servicio
docker compose build --no-cache heaven-platform
docker compose up -d heaven-platform

# Todos
docker compose build --no-cache
docker compose up -d
```

---

## 📊 Monitoreo en Tiempo Real

### Logs de un servicio
```bash
# Últimas 100 líneas
docker compose logs sinkia-heaven -n 100

# Seguimiento en vivo
docker compose logs -f sinkia-heaven

# Múltiples servicios
docker compose logs -f sinkia-heaven sinkia-erp sinkia-jarvis
```

### CPU & Memoria
```bash
# Stats de contenedores
docker stats

# Específico
docker stats sinkia-heaven sinkia-erp
```

### Health check status
```bash
docker compose ps

# Detallado
for svc in sinkia-heaven sinkia-erp sinkia-jarvis; do
  echo "=== $svc ==="
  docker inspect $svc --format='{{.State.Health.Status}}'
done
```

---

## 🔐 Seguridad & Credenciales

### Variables de entorno (.env)
```bash
# Ver configuración actual
cat .env

# Cambiar password PostgreSQL (⚠️ destructivo)
# 1. Parar servicios
./stop.sh

# 2. Editar .env
sed -i 's/POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=nuevo_secret/' .env

# 3. Eliminar volumen de datos
docker volume rm sinkia-os_postgres_data

# 4. Reiniciar
./start-all.sh
```

### Credenciales por defecto (DEV only)
```bash
# PostgreSQL
Usuario: sinkia
Contraseña: sinkia_secret_2026
BD: sinkia_os

# Redis
(sin autenticación)

# Ollama
(sin autenticación, acceso local)
```

---

## 📋 Checklist de Despliegue

- [ ] Docker instalado (`docker --version`)
- [ ] 50GB+ espacio libre (`df -h`)
- [ ] Puerto 3000 disponible (`lsof -nP -iTCP:3000`)
- [ ] Ejecutar `./start-all.sh`
- [ ] Esperar ~2 min a que arraque
- [ ] Ejecutar `./status.sh` → todos ✅
- [ ] Abrir `http://localhost:3000`
- [ ] Verificar datos en PostgreSQL
- [ ] Probar JARVIS API: `curl http://localhost:8080/api/health`

---

## 📞 Soporte & Roadmap

### Problemas conocidos
| Servicio | Issue | Workaround |
|----------|-------|-----------|
| sinkMAIND Memory | Módulo `src.api` no existe | No usar (fase futura) |
| Remote Machine | Sin endpoint `/api/machine/health` | Healthcheck falla |
| Unified Dashboard | No implementado | Usar GUI individual (:3000) |

### Próximas fases
- [ ] Migrar 14 servicios legacy (PM2 → Docker)
- [ ] Implementar sinkMAIND Memory (Chroma + embeddings)
- [ ] Unified Dashboard totalmente funcional
- [ ] Kubernetes deployment
- [ ] Multi-node replication

---

**Última revisión:** agosto 16, 2026  
**Autor:** Oz (Agent)  
**Estado:** Operativo ✅
