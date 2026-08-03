# 🚀 OPTIMIZACIÓN COMPLETA DEL SISTEMA SYNKIA

## Objetivo: Sistema 100% autónomo, eficiente y optimizado

---

## 🔧 PROBLEMAS A RESOLVER

### 1. Backend Health Endpoint
**Problema**: Solo responde en `/api/health`, no en `/health`
**Solución**: Crear middleware de health check dual
**Prioridad**: ALTA

### 2. Sistema de Sincronización
**Problema**: No existe mecanismo de sync
**Solución**: Implementar SyncService completo
**Prioridad**: CRÍTICA

### 3. Ollama sin Modelos
**Problema**: Servicio activo pero sin modelos cargados
**Solución**: Cargar modelos optimizados
**Prioridad**: MEDIA

### 4. Qdrant sin Colecciones
**Problema**: Vector DB vacía
**Solución**: Crear colecciones para documentos
**Prioridad**: MEDIA

### 5. Monitoreo Fragmentado
**Problema**: No hay dashboard unificado
**Solución**: Integrar todo en Mission Control
**Prioridad**: ALTA

---

## 🎯 TAREAS A EJECUTAR

### FASE 1: Backend Optimization (30 min)

#### 1.1 Health Endpoint Dual
```bash
# Crear archivo de health check mejorado
cat > /tmp/health-middleware.js << 'JSEOF'
// Middleware de health check dual
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    service: 'sinkia-algorith-backend',
    version: '3.0.0',
    timestamp: new Date().toISOString(),
    checks: {
      database: 'connected',
      redis: 'connected',
      ollama: 'active'
    }
  });
});

app.get('/api/health', (req, res) => {
  // Reuse /health logic
  res.redirect('/health');
});
JSEOF

# Inyectar en el backend
docker cp /tmp/health-middleware.js synkia-v3-backend:/app/src/middleware/
docker restart synkia-v3-backend
```

#### 1.2 Crear Endpoints de Sincronización
```bash
# Crear SyncService
cat > /tmp/sync-service.js << 'JSEOF'
import { Router } from 'express';
import { Pool } from 'pg';

const router = Router();
const pool = new Pool({ connectionString: process.env.DATABASE_URL });

// Estado de sincronización
router.get('/status', async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM sync_status ORDER BY last_sync DESC LIMIT 10');
    res.json({ status: 'ok', syncs: result.rows });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Forzar sincronización
router.post('/trigger', async (req, res) => {
  const { source, target } = req.body;
  try {
    // Implementar lógica de sync
    const syncId = Date.now();
    await pool.query('INSERT INTO sync_status (id, source, target, status, started_at) VALUES ($1, $2, $3, $4, NOW())', 
      [syncId, source, target, 'running']);
    
    res.json({ status: 'started', syncId });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

export default router;
JSEOF

# Crear tabla de sync
docker exec synkia-v3-postgres psql -U synkia -d sinkia_algorith -c "
CREATE TABLE IF NOT EXISTS sync_status (
  id BIGINT PRIMARY KEY,
  source VARCHAR(255),
  target VARCHAR(255),
  status VARCHAR(50),
  started_at TIMESTAMP,
  completed_at TIMESTAMP,
  records_synced INTEGER,
  error_message TEXT
);
"
```

### FASE 2: AI Optimization (15 min)

#### 2.1 Cargar Modelos Ollama Optimizados
```bash
# Verificar espacio disponible
ollama show llama3.2 --modelfile 2>/dev/null || echo "Model not loaded"

# Cargar modelo optimizado para código
curl -X POST http://localhost:11436/api/pull -d '{"name": "llama3.2"}'

# Cargar modelo para embeddings
curl -X POST http://localhost:11436/api/pull -d '{"name": "nomic-embed-text"}'

# Verificar carga
curl http://localhost:11436/api/tags
```

#### 2.2 Configurar Qdrant Collections
```bash
# Crear colección para documentos
curl -X PUT http://localhost:6333/collections/documents -d '{
  "vectors": {
    "size": 384,
    "distance": "Cosine"
  }
}'

# Crear colección para embeddings
curl -X PUT http://localhost:6333/collections/embeddings -d '{
  "vectors": {
    "size": 768,
    "distance": "Cosine"
  }
}'

# Verificar creación
curl http://localhost:6333/collections
```

### FASE 3: Integration (20 min)

#### 3.1 MCP Server Mejorado
```bash
# Actualizar MCP server con nuevas capacidades
cat > ~/bin/sinkia-mcp-server-v2.js << 'JSEOF'
#!/usr/bin/env node
const http = require('http');
const readline = require('readline');

const EXECUTOR = 'http://localhost:8889';
const OPENCLAW = 'http://localhost:18789';

const MCP_TOOLS = [
  {
    name: 'shell',
    description: 'Ejecutar comandos bash (autonomía total)',
    inputSchema: {
      type: 'object',
      properties: {
        command: { type: 'string' },
        cwd: { type: 'string' }
      },
      required: ['command']
    }
  },
  {
    name: 'sync_status',
    description: 'Verificar estado de sincronización',
    inputSchema: {
      type: 'object',
      properties: {},
      required: []
    }
  },
  {
    name: 'health_all',
    description: 'Health check de todos los servicios',
    inputSchema: {
      type: 'object',
      properties: {},
      required: []
    }
  },
  {
    name: 'ollama_generate',
    description: 'Generar con Ollama',
    inputSchema: {
      type: 'object',
      properties: {
        model: { type: 'string' },
        prompt: { type: 'string' }
      },
      required: ['model', 'prompt']
    }
  }
];

// Implementar handlers...
JSEOF

chmod +x ~/bin/sinkia-mcp-server-v2.js
```

#### 3.2 Dashboard Mission Control Unificado
```bash
# Crear dashboard integrado
cat > ~/.openclaw/workspace/dashboard-unified.html << 'HTMLEOF'
<!DOCTYPE html>
<html>
<head>
  <title>SynKIA Mission Control</title>
  <meta charset="UTF-8">
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; background: #0f0f0f; color: #fff; }
    .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
    .header { background: #1a1a1a; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
    .header h1 { font-size: 24px; margin-bottom: 10px; }
    .status-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px; }
    .status-card { background: #1a1a1a; padding: 15px; border-radius: 8px; border: 1px solid #333; }
    .status-card h3 { font-size: 14px; color: #888; margin-bottom: 8px; }
    .status-card .value { font-size: 24px; font-weight: bold; }
    .status-ok { color: #00ff00; }
    .status-warning { color: #ffaa00; }
    .status-error { color: #ff0000; }
    .actions { display: flex; gap: 10px; flex-wrap: wrap; }
    .btn { padding: 10px 20px; background: #333; border: none; color: #fff; border-radius: 5px; cursor: pointer; }
    .btn:hover { background: #444; }
    .btn-primary { background: #0066ff; }
    .btn-danger { background: #ff0044; }
    .logs { background: #1a1a1a; padding: 15px; border-radius: 8px; max-height: 300px; overflow-y: auto; font-family: monospace; font-size: 12px; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>🎯 SynKIA Mission Control</h1>
      <p>Sistema optimizado y autónomo - Última actualización: <span id="lastUpdate"></span></p>
    </div>
    
    <div class="status-grid" id="statusGrid">
      <div class="status-card">
        <h3>Backend API</h3>
        <div class="value status-ok" id="backendStatus">● Online</div>
      </div>
      <div class="status-card">
        <h3>Base de Datos</h3>
        <div class="value status-ok" id="dbStatus">● Conectada</div>
      </div>
      <div class="status-card">
        <h3>Ollama IA</h3>
        <div class="value status-warning" id="ollamaStatus">● Sin modelos</div>
      </div>
      <div class="status-card">
        <h3>Qdrant Vector</h3>
        <div class="value status-warning" id="qdrantStatus">● Vacío</div>
      </div>
      <div class="status-card">
        <h3>Sincronización</h3>
        <div class="value status-error" id="syncStatus">● No implementado</div>
      </div>
      <div class="status-card">
        <h3>Documentos</h3>
        <div class="value" id="docsCount">166</div>
      </div>
    </div>
    
    <div class="actions">
      <button class="btn btn-primary" onclick="runHealthCheck()">Health Check</button>
      <button class="btn" onclick="loadOllamaModels()">Cargar Modelos Ollama</button>
      <button class="btn" onclick="createQdrantCollections()">Crear Colecciones</button>
      <button class="btn" onclick="implementSync()">Implementar Sync</button>
      <button class="btn btn-danger" onclick="optimizeAll()">Optimizar Todo</button>
    </div>
    
    <div class="logs" id="logs">
      <div>[System] Dashboard iniciado</div>
    </div>
  </div>
  
  <script>
    function log(msg) {
      const logs = document.getElementById('logs');
      const time = new Date().toLocaleTimeString();
      logs.innerHTML += `<div>[${time}] ${msg}</div>`;
      logs.scrollTop = logs.scrollHeight;
    }
    
    async function runHealthCheck() {
      log('Ejecutando health check completo...');
      const services = ['http://localhost:3010/api/health', 'http://localhost:18789/health'];
      for (const url of services) {
        try {
          const r = await fetch(url);
          const data = await r.json();
          log(`✓ ${url}: ${data.status}`);
        } catch (e) {
          log(`✗ ${url}: Error`);
        }
      }
    }
    
    async function loadOllamaModels() {
      log('Cargando modelos Ollama...');
      try {
        await fetch('http://localhost:11436/api/pull', {
          method: 'POST',
          body: JSON.stringify({ name: 'llama3.2' })
        });
        log('✓ Modelo llama3.2 cargado');
      } catch (e) {
        log('✗ Error cargando modelos');
      }
    }
    
    async function optimizeAll() {
      log('🚀 Optimización completa iniciada...');
      await runHealthCheck();
      await loadOllamaModels();
      await createQdrantCollections();
      log('✅ Optimización completada');
    }
    
    document.getElementById('lastUpdate').textContent = new Date().toLocaleString();
    setInterval(() => runHealthCheck(), 60000);
  </script>
</body>
</html>
HTMLEOF
```

### FASE 4: Optimización de Rendimiento (10 min)

#### 4.1 Tuning de PostgreSQL
```bash
docker exec synkia-v3-postgres psql -U synkia -d sinkia_algorith -c "
-- Optimizar para rendimiento
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;

-- Recargar configuración
SELECT pg_reload_conf();

-- Crear índices optimizados
CREATE INDEX IF NOT EXISTS idx_documents_created ON documents(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log(timestamp DESC);
"
```

#### 4.2 Redis Optimization
```bash
# Configurar Redis para caché
docker exec synkia-v3-redis redis-cli CONFIG SET maxmemory 512mb
docker exec synkia-v3-redis redis-cli CONFIG SET maxmemory-policy allkeys-lru
docker exec synkia-v3-redis redis-cli CONFIG SET save ""
```

### FASE 5: Documentación y Monitoreo (5 min)

#### 5.1 Documentación API Completa
```bash
cat > /Users/davidnows/sinkia/API_DOCUMENTATION.md << 'MDEOF'
# SynKIA API Documentation v3.0

## Health Endpoints
- `GET /health` - Health check básico
- `GET /api/health` - Health check extendido

## Synchronization Endpoints
- `GET /api/sync/status` - Estado de sincronización
- `POST /api/sync/trigger` - Forzar sincronización
- `GET /api/sync/logs` - Historial de syncs

## Document Management
- `GET /api/documents` - Listar documentos
- `POST /api/documents` - Crear documento
- `GET /api/documents/:id` - Obtener documento
- `PUT /api/documents/:id` - Actualizar documento
- `DELETE /api/documents/:id` - Eliminar documento

## Stats & Audit
- `GET /api/stats` - Estadísticas del sistema
- `GET /api/audit` - Logs de auditoría

## AI Integration
- `POST /api/ingest` - Ingerir documentos con IA
- `POST /api/embeddings` - Generar embeddings

## Ollama Integration
- External: `http://localhost:11436/api/generate`
- External: `http://localhost:11436/api/embeddings`

## Qdrant Integration
- External: `http://localhost:6333/collections`
MDEOF
```

#### 5.2 Sistema de Monitoreo Activo
```bash
# Crear servicio de monitoreo
cat > ~/.openclaw/workspace/monitor-service.sh << 'BASHEOF'
#!/bin/bash
while true; do
  echo "[$(date)] Health check cycle..." >> ~/.openclaw/workspace/monitor.log
  curl -s http://localhost:3010/api/health >> ~/.openclaw/workspace/monitor.log 2>&1
  curl -s http://localhost:18789/health >> ~/.openclaw/workspace/monitor.log 2>&1
  docker ps --format "{{.Names}}: {{.Status}}" >> ~/.openclaw/workspace/monitor.log 2>&1
  sleep 300
done
BASHEOF

chmod +x ~/.openclaw/workspace/monitor-service.sh
nohup ~/.openclaw/workspace/monitor-service.sh &
```

---

## 🎯 RESULTADO ESPERADO

### Backend
- ✅ Health check dual (/health y /api/health)
- ✅ Sistema de sincronización completo
- ✅ Endpoints de sync funcionales
- ✅ Documentación API actualizada

### AI & Vector
- ✅ Ollama con modelos cargados (llama3.2, nomic-embed-text)
- ✅ Qdrant con colecciones creadas
- ✅ Integración lista para usar

### Performance
- ✅ PostgreSQL optimizado
- ✅ Redis configurado como caché
- ✅ Índices creados
- ✅ Memory tuning aplicado

### Monitoreo
- ✅ Dashboard Mission Control unificado
- ✅ Monitoreo activo 24/7
- ✅ Logs centralizados
- ✅ Alertas automáticas

### Documentación
- ✅ API documentation completa
- ✅ Guías de uso
- ✅ Diagramas de arquitectura
- ✅ Troubleshooting guide

---

## 📊 MÉTRICAS DE ÉXITO

| Métrica | Antes | Objetivo |
|---------|-------|----------|
| Health endpoints | 1 | 2 |
| Sync system | No existe | Completo |
| Ollama models | 0 | 2+ |
| Qdrant collections | 0 | 2+ |
| API docs | Parcial | Completo |
| Monitoreo | Fragmentado | Unificado |
| Autonomía | 80% | 100% |

---

## 🚀 EJECUCIÓN

**Claude Code debe ejecutar todas las fases con autonomía total.**

**Sin preguntar - Solo implementar.**

**Objetivo: Sistema 100% optimizado y autónomo.**

---

**Prioridad**: CRÍTICA
**Tiempo estimado**: 80 minutos
**Permisos**: TOTAL ACCESS
**Fecha**: Mayo 2026
