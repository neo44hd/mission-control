#!/usr/bin/env node

/**
 * 🎯 MODELS API CENTRALIZER v1.0
 * ═══════════════════════════════════════════════════════════════════════════
 * Central hub para descubrimiento dinámico de modelos de:
 * - OpenClaw Gateway (18790)
 * - Ollama (11434)
 * - LM Studio (1234)
 * - Cloud providers (via OpenClaw)
 *
 * Usado por todos los bots Telegram para:
 * ✅ Listar modelos disponibles en tiempo real
 * ✅ Validar IDs de modelo antes de usar
 * ✅ Mantener cache con TTL de 30s
 * ✅ Proporcionar aliases legibles
 * ═══════════════════════════════════════════════════════════════════════════
 */

const http = require('http');
const axios = require('axios');
const fs = require('fs');
const path = require('path');
const os = require('os');

const PORT = process.env.MODELS_API_PORT || 9502;
const CACHE_TTL = 30000; // 30 segundos
const COST_CHECK_INTERVAL = 3600000; // 1 hora para verificar cambios de precios

// Configuración: TODO pasa por OpenClaw Gateway como proveedor Único centralizado
const PROVIDERS = {
  openclaw: { 
    url: 'http://127.0.0.1:18790',
    name: 'OpenClaw Gateway (Central Hub)',
    endpoint: '/v1/models',
    description: 'Hub centralizado que gestiona Ollama, LM Studio, MLX Local, Cloud Providers'
  }
};

// Cache global con TTL
let modelCache = {
  data: [],
  timestamp: 0,
  valid: false,
  includeCloud: false
};

// Cache de información de costos (verificada directamente con proveedores)
let costCache = {
  data: {},
  timestamp: 0,
  verified: false
};

// Historial de cambios para notificaciones
let changeLog = {
  lastCheck: Date.now(),
  changes: [],
  subscribers: [] // Endpoints que quieren ser notificados
};

// Clasificación: OpenClaw determina qué es local vs cloud
// La API aplica la regla: modelos de pago ocultos por defecto
const COST_CLASSIFICATION = {
  // Criterios para detectar si un modelo es PAGO
  // OpenClaw marca en la respuesta de /v1/models
  'local': { free: true, verified: true, description: 'Local/Free models' },
  'cloud': { free: false, verified: false, description: 'Cloud/Paid models' }
};

// Palabras clave para clasificar modelos de OpenClaw
// IMPORTANTE: Usar :free como marcador para OpenRouter FREE, no substring matching
const MODEL_CLASSIFICATION_RULES = {
  // Solo modelos con ':free' explícito son gratuitos en OpenRouter
  free: [':free'],
  // Cloud providers sin :free son PAGOS
  paid: ['cloud', 'gemini', 'nvidia', 'anthropic', 'gpt', 'openai', 'inferx']
};

// Alias amigables para modelos
const MODEL_ALIASES = {
  // Locales - SIEMPRE visibles
  'coder': 'qwen2.5-coder:7b',
  'fast': 'llama3.2:3b',
  'reasoning': 'qwen3.5:latest',
  'vision': 'llama3.2-vision:11b',
  
  // Cloud - SOLO si includeCloud=true
  'glm': 'cloud/nvidia/glm-5.2',
  'gemini': 'cloud/google/gemini',
  'nemotron': 'cloud/nvidia/nemotron-3-ultra',
  'reasoning-cloud': 'cloud/google/gemini',
  'auto': 'cloud/auto',
  'claude': 'cloud/anthropic/claude'
};

// Mapeo de IDs canónicos a info detallada
const MODEL_INFO = {
  'qwen2.5-coder:7b': {
    name: 'Qwen 2.5 Coder 7B',
    provider: 'ollama',
    context: 32768,
    speed: 'fast',
    specialty: 'coding',
    recommended: true
  },
  'qwen3.5:latest': {
    name: 'Qwen 3.5',
    provider: 'ollama',
    context: 262144,
    speed: 'medium',
    specialty: 'reasoning',
    recommended: true
  },
  'llama3.2:3b': {
    name: 'Llama 3.2 3B',
    provider: 'ollama',
    context: 8192,
    speed: 'very-fast',
    specialty: 'lightweight',
    recommended: true
  },
  'llama3.2-vision:11b': {
    name: 'Llama 3.2 Vision 11B',
    provider: 'ollama',
    context: 8192,
    speed: 'slow',
    specialty: 'vision',
    recommended: false
  },
  'gateway/nvidia-direct-glm-5.2': {
    name: 'GLM-5.2 (NVIDIA)',
    provider: 'cloud',
    context: 200000,
    speed: 'medium',
    specialty: 'general',
    recommended: true
  },
  'gateway/cloud-gemini': {
    name: 'Google Gemini',
    provider: 'cloud',
    context: 1000000,
    speed: 'medium',
    specialty: 'long-context',
    recommended: true
  },
  'gateway/nvidia-direct-nemotron-3-ultra': {
    name: 'Nemotron 3 Ultra (NVIDIA)',
    provider: 'cloud',
    context: 1000000,
    speed: 'medium',
    specialty: 'reasoning',
    recommended: true
  }
};

/**
 * Registrar cambios en clasificación de costos
 */
function recordChange(provider, oldStatus, newStatus, reason) {
  const change = {
    timestamp: new Date().toISOString(),
    provider,
    change: `${oldStatus} → ${newStatus}`,
    reason,
    severity: oldStatus === 'free' && newStatus === 'paid' ? 'CRITICAL' : 'INFO'
  };
  
  changeLog.changes.push(change);
  
  // Mantener solo últimos 100 cambios
  if (changeLog.changes.length > 100) {
    changeLog.changes.shift();
  }
  
  // Notificar a subscribers
  notifySubscribers(change);
  
  console.log(`\n📢 [CHANGE] ${change.severity}: ${provider} - ${change.change}`);
  console.log(`   Razón: ${change.reason}`);
}

/**
 * Notificar a todos los suscriptores de cambios
 */
function notifySubscribers(change) {
  changeLog.subscribers.forEach(subscriber => {
    try {
      // Log en archivo de cambios
      const changeLogPath = path.join(os.homedir(), '.synkia-ai-hub', 'cost-changes.log');
      const dir = path.dirname(changeLogPath);
      
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
      
      const logEntry = `[${change.timestamp}] ${change.severity} - ${change.provider}: ${change.change} (${change.reason})\n`;
      fs.appendFileSync(changeLogPath, logEntry, 'utf8');
      
      // Si es crítico (pago ahora), también notificar a stderr
      if (change.severity === 'CRITICAL') {
        console.error(`\n⚠️  CRITICAL: ${change.provider} is now PAID. Update your bot commands!`);
      }
    } catch (err) {
      console.warn('Could not log change:', err.message);
    }
  });
}

/**
 * Verificar estado de costos de un proveedor (consulta directa)
 */
async function verifyCostStatus(provider) {
  const classification = PROVIDER_CLASSIFICATION[provider];
  
  // Si es local verificado, es gratis
  if (classification?.type === 'local' && classification?.verified) {
    return { isFree: true, verified: true, reason: 'Local provider - always free' };
  }
  
  // Para cloud providers, consultar fuente de verdad
  try {
    if (provider === 'openclaw_cloud') {
      // Consultar OpenClaw: si tiene credenciales configuradas en openclaw.json, es pago
      const ocPath = path.join(os.homedir(), '.openclaw', 'openclaw.json');
      if (fs.existsSync(ocPath)) {
        const config = JSON.parse(fs.readFileSync(ocPath, 'utf8'));
        const hasCloudProviders = config.models?.providers?.gemini || 
                                  config.models?.providers?.nvidia ||
                                  config.models?.providers?.inferx;
        return { 
          isFree: false, 
          verified: true, 
          reason: hasCloudProviders ? 'OpenClaw Cloud (requiere credenciales)' : 'OpenClaw sin cloud configurado'
        };
      }
    }
    
    // Por defecto, asumir que cloud providers no son gratis
    return { isFree: false, verified: false, reason: 'Cloud provider - assume paid unless verified' };
  } catch (err) {
    console.warn(`⚠️  Could not verify cost for ${provider}:`, err.message);
    // En caso de error, asumir que es pago (seguridad)
    return { isFree: false, verified: false, reason: 'Unable to verify - assume paid' };
  }
}

/**
 * Obtener TODOS los modelos desde openclaw.json (fuente de verdad Única)
 * OpenClaw Gateway es el hub central que lee esta configuración
 */
async function getAllModelsFromOpenClawConfig() {
  try {
    const configPath = path.join(os.homedir(), '.openclaw', 'openclaw.json');
    if (!fs.existsSync(configPath)) {
      console.warn('⚠️  openclaw.json not found at', configPath);
      return [];
    }
    
    const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
    const allModels = [];
    
    // Extraer modelos de cada proveedor en openclaw.json
    if (config.models?.providers) {
      for (const [providerName, provider] of Object.entries(config.models.providers)) {
        if (!provider.models || !Array.isArray(provider.models)) continue;
        
        const models = provider.models.map(m => {
          const isFree = MODEL_CLASSIFICATION_RULES.free.some(keyword => m.id.toLowerCase().includes(keyword));
          const isPaid = !isFree && MODEL_CLASSIFICATION_RULES.paid.some(keyword => m.id.toLowerCase().includes(keyword));
          
          // Clasificación por provider
          const isOllama = providerName === 'ollama';
          const isLMStudio = providerName === 'lmstudio';
          const isMLXLocal = providerName === 'mlx-local';
          const isGateway = providerName === 'gateway';
          const isOpenRouter = providerName === 'openai_compatible';
          const isGroq = providerName === 'groq';
          const isCloudProvider = ['gemini', 'nvidia', 'inferx', 'openai', 'anthropic'].includes(providerName);
          
          // Modelos gratuitos definidos explícitamente
          const isLocalModel = isOllama || isLMStudio || isMLXLocal || 
                               (isGateway && m.id.toLowerCase().includes('local-')) ||
                               (isOpenRouter && m.id.includes(':free')) ||
                               (isGroq && m.id.includes(':free'));
          
          // Determinar si es realmente gratuito
          const reallyFree = isLocalModel;
          
          return {
            id: m.id,
            name: m.name || m.id,
            provider: providerName,
            context: m.contextWindow || m.context_window || 32768,
            available: true,
            isFree: reallyFree,
            costVerified: reallyFree,
            costReason: isOllama || isLMStudio || isMLXLocal ?
              `${providerName} - local/open-source, always free` :
              (isGateway && m.id.toLowerCase().includes('local-')) ?
                `gateway - local/open-source, always free` :
              (isOpenRouter && m.id.includes(':free')) ?
                `OpenRouter - free tier model (no API key cost)` :
              (isGroq && m.id.includes(':free')) ?
                `Groq - free tier model (rate-limited but free)` :
              isCloudProvider ?
                `${providerName} - cloud provider, requires paid API key` :
                'Unknown provider type',
            raw: m
          };
        });
        
        allModels.push(...models);
      }
    }
    
    console.log(`🎯 Loaded ${allModels.length} models from openclaw.json`);
    return allModels;
    
  } catch (err) {
    console.warn('❌ Failed to load models from openclaw.json:', err.message);
  }
  return [];
}

// NO se consultan directamente Ollama, LM Studio, etc.
// OpenClaw es el proveedor Único que agrupa todo
// Esta sección se mantiene para referencia histórica pero NO se usa

/**
 * Obtener todos los modelos con cache
 * ÚNICO PROVEEDOR: OpenClaw Gateway
 */
async function getAllModels(forceRefresh = false, includeCloud = false) {
  const now = Date.now();
  
  // Retornar cache si es válido
  if (!forceRefresh && modelCache.valid && (now - modelCache.timestamp) < CACHE_TTL && modelCache.includeCloud === includeCloud) {
    return modelCache.data;
  }
  
  console.log(`🔄 Refreshing models from OpenClaw config (${includeCloud ? 'all' : 'local only'})...`);
  
  // FUENTE Única: openclaw.json (OpenClaw Gateway lo usa para gestionar todo)
  const allModels = await getAllModelsFromOpenClawConfig().catch(() => []);
  
  // APLICAR REGLA DE PRIVACIDAD: filtrar modelos de pago si no se piden
  let filtered = allModels;
  if (!includeCloud) {
    filtered = allModels.filter(m => m.isFree !== false);
    console.log(`📋 Aplicando regla de privacidad: ${allModels.length} total → ${filtered.length} locales`);
  }
  
  // Enriquecer con info
  const enriched = filtered.map(m => {
    const info = MODEL_INFO[m.id];
    return {
      ...m,
      ...(info && { info }),
      isFree: m.isFree !== undefined ? m.isFree : true,
      costVerified: m.costVerified || false,
      costReason: m.costReason || 'Unknown'
    };
  });
  
  // Actualizar cache
  modelCache = {
    data: enriched,
    timestamp: now,
    valid: true,
    includeCloud: includeCloud,
    privacyRuleApplied: !includeCloud
  };
  
  console.log(`✅ Cached ${enriched.length} models${!includeCloud ? ' (PRIVACY RULE APPLIED)' : ' (INCLUDING CLOUD)'}`);
  return enriched;
}

/**
 * Validar si un model ID existe
 * IMPORTANTE: Los alias de modelos pagos también deben estar ocultos
 */
async function validateModel(modelId, includeCloud = false) {
  const models = await getAllModels(false, includeCloud);
  const found = models.find(m => m.id === modelId || m.id.endsWith(modelId));
  
  if (found) {
    return {
      valid: true,
      model: found,
      aliases: Object.entries(MODEL_ALIASES)
        .filter(([_, v]) => v === modelId)
        .map(([k, _]) => k),
      costWarning: !found.isFree ? '⚠️  This is a PAID model' : null
    };
  }
  
  // Intentar por alias - pero SOLO si el modelo objetivo está disponible
  const aliasTarget = MODEL_ALIASES[modelId];
  if (aliasTarget) {
    const resolved = models.find(m => m.id === aliasTarget);
    
    if (resolved) {
      // El modelo existe en los modelos filtrados (respeta privacidad)
      return {
        valid: true,
        model: resolved,
        alias: modelId,
        resolvedTo: aliasTarget,
        costWarning: resolved && !resolved.isFree ? '⚠️  This is a PAID model' : null
      };
    } else {
      // El alias apunta a un modelo OCULTO (no disponible sin ?includeCloud=true)
      return {
        valid: false,
        model: null,
        alias: modelId,
        reason: 'This alias points to a paid model. Use ?includeCloud=true to access it.',
        suggestion: models.slice(0, 5),
        note: 'Use includeCloud=true to search paid models'
      };
    }
  }
  
  return {
    valid: false,
    model: null,
    suggestion: models.slice(0, 5), // Sugerir los primeros 5
    note: 'Use includeCloud=true to search paid models'
  };
}

/**
 * Obtener info detallada de un modelo
 */
async function getModelInfo(modelId, includeCloud = false) {
  const validation = await validateModel(modelId, includeCloud);
  
  if (validation.valid) {
    const model = validation.model;
    return {
      success: true,
      id: model.id,
      name: model.name,
      provider: model.provider,
      context: model.context,
      speed: model.speed || 'unknown',
      specialty: model.specialty || 'general',
      recommended: MODEL_INFO[model.id]?.recommended || false,
      isFree: model.isFree,
      costWarning: validation.costWarning,
      alias: validation.alias,
      resolvedTo: validation.resolvedTo
    };
  }
  
  return {
    success: false,
    error: `Model '${modelId}' not found`,
    suggestions: validation.suggestion,
    note: validation.note
  };
}

/**
 * REST API Server
 */
const server = http.createServer(async (req, res) => {
  res.setHeader('Content-Type', 'application/json');
  res.setHeader('Access-Control-Allow-Origin', '*');
  
  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }

  // GET /api/models/list - Listar modelos (solo locales por defecto)
  if (req.url.startsWith('/api/models/list') && req.method === 'GET') {
    const url = new URL(`http://localhost${req.url}`);
    const includeCloud = url.searchParams.get('includeCloud') === 'true';
    const verbose = url.searchParams.get('verbose') === 'true';
    const models = await getAllModels(false, includeCloud);
    
    const filtered = includeCloud ? models : models.filter(m => m.isFree !== false);
    
    res.writeHead(200);
    res.end(JSON.stringify({
      total: filtered.length,
      showingCloud: includeCloud,
      notice: includeCloud ? 'Showing all models (local + cloud)' : 'Use ?includeCloud=true to see paid cloud models',
      models: filtered.map(m => {
        const obj = {
          id: m.id,
          name: m.name,
          provider: m.provider,
          context: m.context,
          available: m.available,
          isFree: m.isFree,
          costVerified: m.costVerified,
          recommended: MODEL_INFO[m.id]?.recommended || false
        };
        if (verbose) {
          obj.costReason = m.costReason;
        }
        return obj;
      })
    }, null, 2));
    return;
  }

  // GET /api/models/compact - Versión compacta para Telegram (solo locales por defecto)
  if (req.url.startsWith('/api/models/compact') && req.method === 'GET') {
    const url = new URL(`http://localhost${req.url}`);
    const includeCloud = url.searchParams.get('includeCloud') === 'true';
    const models = await getAllModels(false, includeCloud);
    
    const filtered = includeCloud ? models : models.filter(m => m.isFree !== false);
    const grouped = {
      local_ollama: filtered.filter(m => m.provider === 'ollama').map(m => m.id),
      local_lmstudio: filtered.filter(m => m.provider === 'lmstudio').map(m => m.id),
      local_other: filtered.filter(m => m.isFree && m.provider !== 'ollama' && m.provider !== 'lmstudio').map(m => m.id)
    };
    
    if (includeCloud) {
      grouped.cloud = filtered.filter(m => !m.isFree).map(m => m.id);
    }
    
    res.writeHead(200);
    res.end(JSON.stringify(grouped));
    return;
  }

  // GET /api/models/validate?id={modelId} - Validar un modelo
  if (req.url.startsWith('/api/models/validate') && req.method === 'GET') {
    const url = new URL(`http://localhost${req.url}`);
    const modelId = url.searchParams.get('id');
    const includeCloud = url.searchParams.get('includeCloud') === 'true';
    
    if (!modelId) {
      res.writeHead(400);
      res.end(JSON.stringify({ error: 'Missing id parameter' }));
      return;
    }
    
    const validation = await validateModel(modelId, includeCloud);
    res.writeHead(validation.valid ? 200 : 404);
    const response = JSON.parse(JSON.stringify(validation)); // Deep clone
    if (response.model) {
      response.model.costVerified = validation.model?.costVerified || false;
      response.model.costReason = validation.model?.costReason || 'Unknown';
    }
    res.end(JSON.stringify(response, null, 2));
    return;
  }

  // GET /api/models/{id}/info - Info detallada de modelo
  if (req.url.startsWith('/api/models/') && req.method === 'GET' && !req.url.startsWith('/api/models/list') && !req.url.startsWith('/api/models/validate') && !req.url.startsWith('/api/models/compact') && !req.url.startsWith('/api/models/aliases') && !req.url.startsWith('/api/models/refresh') && !req.url.startsWith('/api/models/changes') && !req.url.startsWith('/api/models/subscribe')) {
    const modelIdPart = req.url.replace('/api/models/', '');
    const url = new URL(`http://localhost${req.url}`);
    const modelId = modelIdPart.split('?')[0].replace('/info', '');
    const includeCloud = url.searchParams.get('includeCloud') === 'true';
    const info = await getModelInfo(modelId, includeCloud);
    
    res.writeHead(info.success ? 200 : 404);
    res.end(JSON.stringify(info, null, 2));
    return;
  }

  // GET /api/models/aliases - Obtener aliases disponibles
  if (req.url === '/api/models/aliases' && req.method === 'GET') {
    res.writeHead(200);
    res.end(JSON.stringify({
      aliases: MODEL_ALIASES,
      description: 'Alias cortos para usar en bots'
    }, null, 2));
    return;
  }

  // POST /api/models/refresh - Forzar refresh de cache
  if (req.url.startsWith('/api/models/refresh') && req.method === 'POST') {
    const url = new URL(`http://localhost${req.url}`);
    const includeCloud = url.searchParams.get('includeCloud') === 'true';
    const models = await getAllModels(true, includeCloud);
    res.writeHead(200);
    res.end(JSON.stringify({
      refreshed: true,
      total: models.length,
      includedCloud: includeCloud
    }));
    return;
  }

  // GET /api/models/changes - Obtener historial de cambios
  if (req.url === '/api/models/changes' && req.method === 'GET') {
    res.writeHead(200);
    res.end(JSON.stringify({
      lastCheck: changeLog.lastCheck,
      totalChanges: changeLog.changes.length,
      changes: changeLog.changes.slice(-20) // Últimos 20 cambios
    }, null, 2));
    return;
  }
  
  // POST /api/models/subscribe - Suscribirse a notificaciones de cambios
  if (req.url === '/api/models/subscribe' && req.method === 'POST') {
    const subscriberId = `subscriber_${Date.now()}`;
    changeLog.subscribers.push(subscriberId);
    
    res.writeHead(200);
    res.end(JSON.stringify({
      subscribed: true,
      id: subscriberId,
      message: 'Will be notified of cost classification changes',
      changeLogLocation: `${os.homedir()}/.synkia-ai-hub/cost-changes.log`
    }, null, 2));
    return;
  }

  // GET /health
  if (req.url === '/health' && req.method === 'GET') {
    res.writeHead(200);
    res.end(JSON.stringify({ status: 'healthy', uptime: process.uptime() }));
    return;
  }

  res.writeHead(404);
  res.end(JSON.stringify({ error: 'Not found' }));
});

server.listen(PORT, '127.0.0.1', () => {
  console.log(`\n🎯 Models API Centralizer v3.0 - OPENCLAW GATEWAY ONLY`);
  console.log(`📡 Listening on port ${PORT}`);
  console.log(`\n📋 ARQUITECTURA:`);
  console.log(`  ✓ Proveedor Único: OpenClaw Gateway (127.0.0.1:18790)`);
  console.log(`  ✓ Regla de privacidad: modelos de pago SIEMPRE ocultos por defecto`);
  console.log(`  ✓ Clasificación dinámica: detecta local vs cloud automáticamente`);
  console.log(`  ✓ Notificaciones automáticas de cambios`);
  console.log(`  ✓ Historial: ${os.homedir()}/.synkia-ai-hub/cost-changes.log`);
  console.log(`\n📋 Endpoints:`);
  console.log(`  • GET /api/models/list                             - Modelos locales (REGLA: pago oculto)`);
  console.log(`  • GET /api/models/list?includeCloud=true           - TODOS (local + cloud)`);
  console.log(`  • GET /api/models/list?verbose=true                - Con razón de clasificación`);
  console.log(`  • GET /api/models/compact                          - Compacto (local)`);
  console.log(`  • GET /api/models/compact?includeCloud=true        - Compacto (todos)`);
  console.log(`  • GET /api/models/aliases        - Alias disponibles`);
  console.log(`  • GET /api/models/validate?id=X  - Validar modelo`);
  console.log(`  • GET /api/models/{id}/info      - Info detallada`);
  console.log(`  • GET /api/models/changes        - Historial de cambios`);
  console.log(`  • POST /api/models/subscribe     - Suscribirse a notificaciones`);
  console.log(`  • GET /health                    - Health check\n`);
});

// Inicializar suscriptor automático
changeLog.subscribers.push('system');

// Verificar cambios de precios periódicamente (cada hora)
setInterval(async () => {
  console.log(`\n⏰ [Hourly Check @ ${new Date().toISOString()}] Verificando cambios en clasificación de costos...`);
  
  // Verificar cada proveedor
  for (const [provider, config] of Object.entries(PROVIDER_CLASSIFICATION)) {
    if (config.type === 'cloud') {
      const oldStatus = costCache.data[provider]?.isFree ? 'free' : 'paid';
      const newStatus = await verifyCostStatus(provider);
      const newStatusStr = newStatus.isFree ? 'free' : 'paid';
      
      if (oldStatus !== newStatusStr && oldStatus !== undefined) {
        recordChange(provider, oldStatus, newStatusStr, newStatus.reason);
      }
      
      costCache.data[provider] = newStatus;
    }
  }
  
  costCache.timestamp = Date.now();
  changeLog.lastCheck = Date.now();
  
  // Limpiar cache para forzar refresh en siguiente solicitud
  modelCache.valid = false;
}, COST_CHECK_INTERVAL);

process.on('SIGINT', () => {
  console.log('\n👋 Shutting down Models API Centralizer');
  console.log(`📊 Final stats: ${changeLog.changes.length} cost changes detected`);
  process.exit(0);
});
