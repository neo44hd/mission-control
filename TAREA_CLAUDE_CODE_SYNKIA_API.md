# 🎯 TAREA PARA CLAUDE CODE - AUTONOMÍA TOTAL

## Misión
Investigar por qué SynkIA API no sincroniza bien, clasificar todos los documentos y proporcionar soluciones concretas.

---

## 🔓 Permisos Totales Activados

**Tienes acceso completo a**:
- ✅ Shell completo (bash, zsh)
- ✅ Docker (todos los contenedores)
- ✅ Ollama (modelos locales)
- ✅ Base de datos (PostgreSQL, Redis, Qdrant)
- ✅ Aplicaciones (Frontend, Backend, Dashboard)
- ✅ Archivos (lectura, escritura, ejecución)
- ✅ Red (HTTP requests, APIs)
- ✅ OpenClaw (bridge, delegación)
- ✅ Misión Control (tarjetas, dashboard)

**REGLA**: Ejecutar sin preguntar. Si puedes hacerlo, hazlo.

---

## 📋 Pasos a Ejecutar

### 1. Health Check Completo
```bash
# Backend (puerto 3010)
curl http://localhost:3010/health
curl http://localhost:3010/api/health
docker logs synkia-v3-backend --tail 100

# Dashboard (puerto 18789)
curl http://localhost:18789/health

# Frontend (puerto 5183)
curl http://localhost:5183
```

### 2. Investigar Base de Datos
```bash
# PostgreSQL
docker exec synkia-v3-postgres psql -U [BUSCAR_USUARIO_CORRECTO] -l
docker exec synkia-v3-postgres psql -U [USUARIO] -d [DB] -c "SELECT * FROM users LIMIT 5;"

# Redis
docker exec synkia-v3-redis redis-cli ping
docker exec synkia-v3-redis redis-cli keys "*"

# Qdrant
curl http://localhost:6333/collections
```

### 3. Investigar Sincronización
```bash
# Buscar archivos de configuración
find /Users/davidnows/sinkia -name "*.config.*" -o -name "*sync*" -o -name "*.env*"

# Verificar variables de entorno
docker exec synkia-v3-backend env | grep -i sync
docker exec synkia-v3-backend env | grep -i db

# Revisar código del backend
docker exec synkia-v3-backend find /app -name "*.js" | head -20
docker exec synkia-v3-backend cat /app/src/index.js 2>/dev/null || echo "Buscar archivo principal"
```

### 4. Clasificar Documentación
```bash
# Listar todos los documentos
find /Users/davidnows/sinkia -type f \( -name "*.md" -o -name "*.txt" -o -name "*.pdf" \) -not -path "*/node_modules/*"

# Analizar cada uno
# - README.md: Propósito del proyecto
# - CLAUDE.md: Config Claude Code
# - SOUL.md: Filosofía
# - USER.md: Perfil usuario
# - API docs: Endpoints
# - Etc.
```

### 5. Usar Ollama para Análisis
```bash
# Listar modelos disponibles
ollama list

# Usar modelo para análisis (si necesario)
curl http://localhost:11436/api/generate -d '{
  "model": "llama3.2",
  "prompt": "Analiza estos logs de error: [PEGAR_LOGS]"
}'
```

### 6. Verificar Apps en Docker
```bash
# Todas las apps
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Stats de recursos
docker stats --no-stream

# Redes
docker network ls
docker network inspect bridge
```

### 7. Crear Health Endpoint (SI NO EXISTE)
```javascript
// Si el backend no tiene /health, crearlo
// Buscar el código del backend y añadir:
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});
```

---

## 🎯 Soluciones a Implementar

### A. Si backend no tiene /health
1. Buscar código fuente del backend
2. Añadir endpoint /health
3. Reiniciar contenedor
4. Verificar que funciona

### B. Si DB no conecta
1. Identificar usuario/DB correctos
2. Actualizar configuración
3. Crear DB si no existe
4. Verificar conexión

### C. Si no hay sincronización
1. Implementar SyncService básico
2. Crear endpoints /api/sync/*
3. Configurar cron job o worker
4. Documentar proceso

### D. Documentación
1. Crear API_DOCUMENTATION.md completo
2. Actualizar README con estado actual
3. Crear diagrama de arquitectura
4. Lista de endpoints funcionando

---

## 📊 Entregables Requeridos

1. **INFORME_COMPLETO.md** con:
   - Estado actual de todos los servicios
   - Problemas identificados
   - Soluciones propuestas
   - Código implementado
   - Métricas de rendimiento

2. **DOCUMENTOS_CLASIFICADOS.csv** con:
   - Nombre archivo
   - Tipo
   - Propósito
   - Ubicación
   - Última modificación

3. **SOLUCIONES_IMPLEMENTADAS.md** con:
   - Código añadido
   - Configuraciones cambiadas
   - Servicios reiniciados
   - Tests realizados

---

## 🔧 Herramientas Disponibles

### Shell Completo
```bash
# Puedes ejecutar CUALQUIER comando
rm -rf /path/to/delete
mkdir -p /new/directory
chmod 755 /file
chown user:group /file
```

### Docker Completo
```bash
# Puedes gestionar TODOS los contenedores
docker restart <container>
docker stop <container>
docker rm <container>
docker exec <container> <command>
```

### Ollama Completo
```bash
# Puedes usar modelos locales
ollama run llama3.2
ollama pull nuevo-modelo
ollama rm modelo-no-usado
```

### Archivos Completos
```bash
# Puedes crear, editar, eliminar archivos
echo "contenido" > /nuevo/archivo
sed -i 's/old/new/g' /archivo
rm /archivo/a/borrar
```

---

## ⚠️ Información Importante

### Estructura del Proyecto
- **Frontend**: /Users/davidnows/sinkia/frontend (React, puerto 5183)
- **Backend**: Contenedor Docker synkia-v3-backend (puerto 3010)
- **Dashboard**: Contenedor Docker synkia-dashboard (puerto 18789)
- **DB**: synkia-v3-postgres (puerto 5434)
- **Redis**: synkia-v3-redis (puerto 6381)
- **Qdrant**: sinkia-qdrant (puerto 6333)
- **Ollama**: synkia-v3-ollama (puerto 11436)

### Variables de Entorno Conocidas
```bash
OLLAMA_NUM_PARALLEL=1
OLLAMA_MAX_LOADED_MODELS=1
```

### Usuario
- **Nombre**: David Roldán Hueso
- **Empresa**: Chicken Palace Ibiza S.L.
- **Proyecto**: SynK-IA (sinkialabs.com)
- **Repo**: neo44hd/synk-ia (privado)
- **Idioma**: ESPAÑOL SIEMPRE

---

## 🚀 Ejecutar Ahora

**No esperes instrucciones adicionales.**

1. Lee este archivo
2. Ejecuta cada paso
3. Implementa soluciones
4. Crea los entregables
5. Reporta resultados

**Autonomía Total = Sin preguntar, solo hacer.**

---

## 📍 Ubicación de Resultados

Crear archivos en:
- `~/.openclaw/workspace/INFORME-SYNKIA-API-COMPLETO.md`
- `~/.openclaw/workspace/DOCUMENTOS_CLASIFICADOS.csv`
- `~/.openclaw/workspace/SOLUCIONES_IMPLEMENTADAS.md`
- `~/.claude/memory/TAREA_EJECUTADA.md`

---

**Fecha creación**: Mayo 2026
**Prioridad**: ALTA
**Estado**: LISTO PARA EJECUTAR
**Ejecutor**: Claude Code
**Permisos**: TOTAL ACCESS
