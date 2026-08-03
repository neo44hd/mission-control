# SYNK-OPS — Plataforma Unificada de Operaciones IA

## 📋 Tabla de Contenidos
1. [Descripción General](#descripción-general)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Componentes Principales](#componentes-principales)
4. [Funciones Detalladas](#funciones-detalladas)
5. [Ejemplos de Uso](#ejemplos-de-uso)
6. [Configuración Avanzada](#configuración-avanzada)
7. [API Reference Completa](#api-reference-completa)
8. [Troubleshooting](#troubleshooting)

---

## Descripción General

**SYNK-OPS** es una plataforma empresarial que unifica todos tus servicios y herramientas IA en un único ecosistema inteligente. Funciona como un **maestro orquestador** que:

- 🎯 **Enruta automáticamente** requests a la herramienta correcta basada en contexto
- 🧠 **Selecciona inteligentemente** el mejor modelo para cada tarea
- 💪 **Monitorea constantemente** la salud de todos los servicios
- 📊 **Aprende continuamente** de tus patrones de uso
- 🔄 **Auto-sanación**: Reinicia servicios caídos automáticamente

**Resultado**: Tus 13 servicios IA trabajan como **"una única pieza unificada"**.

---

## Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────┐
│                    TU APLICACIÓN                         │
│                  (Cliente HTTP/REST)                     │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ HTTP Request
                     ▼
┌──────────────────────────────────────────────────────────┐
│          SYNK-IA ORCHESTRATOR (Puerto 9500)              │
│  ┌────────────────────────────────────────────────────┐  │
│  │ 1. Analiza Contexto (keywords, task type)          │  │
│  │ 2. Enruta a Herramienta Óptima                     │  │
│  │ 3. Selecciona Modelo (via Model Selector)          │  │
│  │ 4. Monitorea Salud (30s intervals)                 │  │
│  │ 5. Registra Métricas (unified-memory.json)         │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────┬───────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────────┐
│ MODEL SELECTOR│ │HEALTH MONITOR│ │INTELLIGENT ROUTER│
│  (9501)      │ │              │ │                  │
│              │ │ Checks Health│ │ Context Keywords │
│ 7 Models     │ │ Auto-Restart │ │ Fallback Chains  │
│ + Fallbacks  │ │ Logs Stats   │ │ Performance Data │
└──────────────┘ └──────────────┘ └──────────────────┘
        │              │              │
        └──────────────┼──────────────┘
                       │
    ┌──────────────────┼──────────────────┐
    │                  │                  │
    ▼                  ▼                  ▼
┌─────────────┐  ┌──────────────┐  ┌──────────────┐
│ OpenClaw    │  │ SynK-IA-Ops  │  │ Hub AI Local │
│ (7999)      │  │ (3001)       │  │ (11435)      │
└─────────────┘  └──────────────┘  └──────────────┘
    │                  │                  │
    ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────┐
│           13 SERVICIOS ORQUESTADOS                  │
│  (Ollama, LiteLLM, OpenWebUI, n8n, etc.)           │
└─────────────────────────────────────────────────────┘
```

---

## Componentes Principales

### 1. **synk-ia-global-config.yaml** (597 líneas)
**Propósito**: Archivo de configuración centralizado que define TODO el ecosistema.

**¿Qué hace?**
- Define 13 servicios (puertos, health checks, flags críticos)
- Especifica patrones de enrutamiento (6 contextos → herramientas)
- Configura 5 perfiles de modelos por tarea
- Establece cadenas de fallback (plan B, plan C)
- Mantiene capabilidades del sistema

**Secciones principales:**

#### a) **Services (13 servicios)**
```yaml
services:
  hub-ai-local:
    port: 11435
    health_check: "http://localhost:11435/api/health"
    critical: true
    description: "Hub central para modelos locales"
```

**¿Por qué es importante?** Cada servicio tiene:
- **port**: Dónde escucha el servicio
- **health_check**: URL que verifica si está vivo
- **critical**: Si es true, el orchestrator lo reinicia automáticamente si cae
- **description**: Para documentación

#### b) **Routing Patterns (6 patrones inteligentes)**
```yaml
routing:
  - context: "coding"
    keywords: ["refactor", "debug", "function", "class", "optimize"]
    primary_tool: "openclaw"
    secondary_tool: "hub-ai-local"
    confidence: 0.95
```

**¿Por qué funciona?** El sistema detecta keywords en tu request y enruta automáticamente:
- Escribes: "refactor this function" → Detecta "refactor" + "function" → Enruta a **OpenClaw**
- Escribes: "analyze this data" → Detecta "analyze" + "data" → Enruta a **SynK-IA-Ops**

#### c) **Task Profiles (5 perfiles optimizados)**
```yaml
task_profiles:
  coding:
    primary_model: "local-claude-code"
    secondary_model: "local-coder-ollama"
    tertiary_model: "llama:3b"
    temperature: 0.3
    max_tokens: 4096
    purpose: "Código de producción, refactoring, debugging"
```

**¿Cuándo se usa cada perfil?**
- **coding**: Escribir/refactorizar código
- **creative**: Generar contenido, brainstorming
- **research**: Análisis, investigación, síntesis
- **fast**: Respuestas rápidas, low-latency
- **jobMatching**: Matching de empleos (especializado RuFlow)

---

### 2. **synk-ia-orchestrator.js** (511 líneas)
**Propósito**: Daemon inteligente que orquesta TODO en tiempo real.

**¿Qué hace?**
- ✅ Monitorea 13 servicios cada 30 segundos
- ✅ Auto-reinicia servicios críticos si caen
- ✅ Enruta requests inteligentemente
- ✅ Selecciona modelos dinámicamente
- ✅ Registra métricas de aprendizaje
- ✅ Descubre nuevos proyectos en GitHub

#### **Funciones Clave:**

**1. `checkServiceHealth()`**
```javascript
// Se ejecuta CADA 30 SEGUNDOS
async function checkServiceHealth() {
  for (let service in config.services) {
    const healthUrl = config.services[service].health_check;
    const response = await fetch(healthUrl);
    
    if (!response.ok && config.services[service].critical) {
      // AUTO-REINICIA el servicio
      restartService(service);
    }
  }
}
```

**¿Cuándo se activa?**
- Cada 30 segundos automáticamente
- Si un servicio crucial (critical: true) no responde, lo reinicia
- Ejemplo: Si Ollama cae, se reinicia solo automáticamente

**2. `intelligentRouter(request)`**
```javascript
// Analiza el request y enruta a la herramienta correcta
async function intelligentRouter(request) {
  // Extrae contexto del request
  const context = analyzeContext(request);
  // context = { type: "coding", confidence: 0.95 }
  
  // Busca la herramienta óptima
  const tool = getOptimalTool(context);
  // tool = { name: "openclaw", port: 7999 }
  
  // Obtiene el mejor modelo para esta tarea
  const model = selectModel(context.type);
  // model = { name: "local-claude-code", fallback: "qwen" }
  
  // Ejecuta la solicitud
  return executeRequest(tool, model, request);
}
```

**Ejemplo práctico:**
```
Tu solicitud: "Refactor this authentication function to use async-await"

┌─ Orchestrator recibe el request
├─ Analiza: keywords = ["refactor", "function", "authentication"]
├─ Detecta: context = "coding" (confidence 0.95)
├─ Enruta a: OpenClaw (herramienta de código)
├─ Selecciona modelo: local-claude-code (mejor para coding)
└─ Ejecuta: Envía request a OpenClaw con modelo seleccionado
```

**3. `selectModel(taskType)`**
```javascript
// Selecciona el mejor modelo según el tipo de tarea
function selectModel(taskType) {
  const profile = config.task_profiles[taskType];
  
  return {
    primary: profile.primary_model,
    secondary: profile.secondary_model,
    tertiary: profile.tertiary_model,
    // Intenta primary, si falla intenta secondary, etc.
  };
}
```

**4. `discoverGitHubTrends()`**
```javascript
// Se ejecuta cada 1 hora
async function discoverGitHubTrends() {
  // Busca proyectos IA trending en GitHub
  const trends = await searchGitHub({
    q: "topic:ai-ops stars:>1000",
    sort: "stars",
    per_page: 50
  });
  
  // Registra descubrimientos
  memory.discoveries.push({
    name: "new-ai-tool",
    url: "https://github.com/...",
    stars: 5000,
    description: "...",
    capabilities: ["orchestration", "routing"]
  });
  
  // Actualiza el ecosistema automáticamente
  updateCapabilities(trends);
}
```

**¿Por qué es poderoso?** Descubre nuevas herramientas IA trending y las integra automáticamente.

**5. `recordMetrics(request, response)`**
```javascript
// Registra cada operación para aprendizaje
function recordMetrics(request, response) {
  memory.metrics.push({
    timestamp: Date.now(),
    context: "coding",
    tool: "openclaw",
    model: "local-claude-code",
    latency: response.duration,
    success: response.status === 200,
    tokens_used: response.tokens,
    cost: response.cost
  });
  
  // Usa datos para optimizar decisiones futuras
  updateRoutingDecisions(memory.metrics);
}
```

---

### 3. **synk-ia-model-selector.js** (360 líneas)
**Propósito**: Motor inteligente que selecciona el mejor modelo para cada tarea.

**¿Qué hace?**
- 🎯 Selecciona el modelo óptimo por tipo de tarea
- 📊 Compara modelos (velocidad, costo, precisión)
- 💰 Rastrea costos de tokens y ejecución
- 🔄 Implementa fallback chains (plan B, plan C)
- 📈 Optimiza basado en historial

#### **7 Modelos Disponibles:**

```javascript
const models = {
  "local-claude-code": {
    name: "Claude Haiku para Coding",
    type: "local",
    best_for: ["coding", "refactoring", "debugging"],
    latency: "50ms",
    cost: "free", // Local
    capabilities: ["fast-coding", "debugging", "optimization"]
  },
  
  "local-coder-ollama": {
    name: "Ollama Coder (Qwen)",
    type: "local",
    best_for: ["coding", "documentation"],
    latency: "100ms",
    cost: "free",
    capabilities: ["coding", "docs"]
  },
  
  "local-reason": {
    name: "Reasoning Model (Ollama)",
    type: "local",
    best_for: ["research", "analysis", "complex-reasoning"],
    latency: "200ms",
    cost: "free",
    capabilities: ["reasoning", "analysis"]
  },
  
  "qwen-coder": {
    name: "Qwen Coder 32B (LiteLLM)",
    type: "remote",
    best_for: ["advanced-coding", "architecture"],
    latency: "300ms",
    cost: "$0.001/1K tokens",
    capabilities: ["advanced-coding", "architecture"]
  },
  
  "gpt-4o": {
    name: "GPT-4o (via LiteLLM)",
    type: "remote",
    best_for: ["complex-reasoning", "research"],
    latency: "400ms",
    cost: "$0.003/1K tokens",
    capabilities: ["reasoning", "research", "creativity"]
  },
  
  "claude-opus": {
    name: "Claude Opus (via LiteLLM)",
    type: "remote",
    best_for: ["strategic-reasoning", "complex-analysis"],
    latency: "500ms",
    cost: "$0.015/1K tokens",
    capabilities: ["strategic-thinking", "analysis"]
  },
  
  "llama:3b": {
    name: "Llama 3B (Ollama fallback)",
    type: "local",
    best_for: ["quick-responses", "fallback"],
    latency: "150ms",
    cost: "free",
    capabilities: ["general"]
  }
};
```

#### **Funciones Clave:**

**1. `selectBestModel(taskType)`**
```javascript
async function selectBestModel(taskType) {
  const profile = config.task_profiles[taskType];
  
  // Intenta models en orden de preferencia
  const models_to_try = [
    profile.primary_model,      // 1er intento
    profile.secondary_model,    // 2do intento
    profile.tertiary_model      // 3er intento (fallback final)
  ];
  
  for (let model of models_to_try) {
    const health = await checkModelHealth(model);
    if (health.available) {
      return {
        model: model,
        reason: `Optimal for ${taskType}`,
        fallback_chain: models_to_try
      };
    }
  }
  
  // Si todos fallan, usa el fallback final
  return { model: "llama:3b", reason: "All others unavailable" };
}
```

**Ejemplo práctico:**
```
Solicitud: "Refactor this code"
TaskType: "coding"

Búsqueda de modelo:
1. ¿Está local-claude-code disponible? ✅ SÍ → Usa ese
   (Razón: Es el más rápido y está local)

Si local-claude-code NO estuviera disponible:
2. ¿Está local-coder-ollama disponible? → Usa ese
3. Si tampoco → Usa llama:3b (fallback final)
```

**2. `compareModels(modelList)`**
```javascript
// Compara múltiples modelos
async function compareModels(modelList) {
  const comparison = {};
  
  for (let model of modelList) {
    const stats = memory.metrics.filter(m => m.model === model);
    
    comparison[model] = {
      avg_latency: calculateAverage(stats, 'latency'),
      success_rate: calculateSuccessRate(stats),
      total_tokens_used: sum(stats, 'tokens'),
      total_cost: sum(stats, 'cost'),
      avg_quality_score: calculateQuality(stats)
    };
  }
  
  return comparison;
}
```

**3. `trackModelCosts(modelUsage)`**
```javascript
// Rastrea costos de cada modelo
function trackModelCosts(modelUsage) {
  memory.costs[modelUsage.model] = {
    tokens_this_hour: modelUsage.tokens,
    tokens_today: getTodayTokens(modelUsage.model),
    tokens_this_month: getMonthTokens(modelUsage.model),
    cost_this_month: calculateMonthlyCost(modelUsage.model),
    estimated_monthly: extrapolateMonthly()
  };
}
```

---

### 4. **unified-memory.json** (140 líneas)
**Propósito**: Sistema centralizado de aprendizaje y memoria.

**¿Qué almacena?**

```json
{
  "routing_stats": {
    "total_requests": 1250,
    "context_distribution": {
      "coding": 450,      // 36% fueron solicitudes de coding
      "research": 300,    // 24% fueron de research
      "creative": 200,    // 16% fueron creativas
      "fast": 200,        // 16% fueron rápidas
      "jobMatching": 100  // 8% fueron de job matching
    },
    "tool_usage": {
      "openclaw": 450,
      "sinkia-ops": 300,
      "hub-ai-local": 250,
      "mission-control": 150,
      "ruflow": 100
    }
  },
  
  "performance_metrics": {
    "avg_latency_ms": 245,
    "success_rate": 0.98,
    "uptime_percentage": 99.7,
    "model_accuracy_scores": {
      "local-claude-code": 0.96,
      "local-coder-ollama": 0.92,
      "gpt-4o": 0.99
    }
  },
  
  "cost_tracking": {
    "tokens_this_month": 5000000,
    "cost_breakdown": {
      "local_models": 0,
      "remote_apis": 450.50
    },
    "projected_monthly_cost": 480.00
  },
  
  "discoveries": [
    {
      "name": "new-ai-orchestration-tool",
      "url": "https://github.com/...",
      "stars": 5000,
      "description": "New orchestration framework",
      "capabilities": ["routing", "health-monitoring"],
      "integration_status": "pending"
    }
  ],
  
  "learning_insights": [
    {
      "pattern": "coding tasks at 9-10am are 15% faster",
      "insight_type": "temporal",
      "recommendation": "Schedule heavy coding work for morning hours"
    }
  ]
}
```

**¿Cómo se usa?**
- El orchestrator actualiza estos datos constantemente
- Se usa para optimizar decisiones futuras
- Permite ver patrones de uso
- Rastrea costos y eficiencia

---

## Funciones Detalladas

### **Función: Intelligence Context Analysis**
**Ubicación**: `synk-ia-orchestrator.js`, línea 150

```javascript
function analyzeContext(request) {
  const text = request.body.content || request.query.q;
  const keywords = text.toLowerCase().split(/\s+/);
  
  // Busca en patrones de enrutamiento
  for (let pattern of config.routing) {
    const matches = keywords.filter(k => 
      pattern.keywords.includes(k)
    ).length;
    
    if (matches > 0) {
      return {
        type: pattern.context,
        confidence: matches / pattern.keywords.length,
        matched_keywords: keywords.filter(k => 
          pattern.keywords.includes(k)
        )
      };
    }
  }
  
  // Si no encuentra patrón, usa el contexto por defecto
  return { type: "general", confidence: 0.5 };
}
```

**¿Cuándo se usa?** Cada vez que llega un request HTTP.

**Ejemplo:**
```
Request: "Refactor the authentication function to be async"
Keywords: ["refactor", "authentication", "function", "be", "async"]

Análisis:
- Patrón "coding" tiene keywords: ["refactor", "debug", "function"]
- Coincidencias: "refactor", "function" = 2/3 = 0.67 confidence
- Resultado: { type: "coding", confidence: 0.67 }
```

---

### **Función: Automatic Health Monitoring**
**Ubicación**: `synk-ia-orchestrator.js`, línea 250

```javascript
async function monitorHealth() {
  setInterval(async () => {
    const healthReport = {};
    
    for (let [serviceName, config] of Object.entries(services)) {
      try {
        const response = await fetch(config.health_check, {
          timeout: 5000
        });
        
        healthReport[serviceName] = {
          status: response.ok ? 'healthy' : 'unhealthy',
          response_time: response.duration,
          last_check: new Date()
        };
        
        // Si está caído y es crítico, reinicia
        if (!response.ok && config.critical) {
          console.log(`🔧 Restarting critical service: ${serviceName}`);
          restartService(serviceName);
        }
      } catch (error) {
        healthReport[serviceName] = {
          status: 'error',
          error: error.message,
          last_check: new Date()
        };
        
        if (config.critical) {
          restartService(serviceName);
        }
      }
    }
    
    // Guarda reporte
    saveHealthReport(healthReport);
  }, 30000); // Cada 30 segundos
}
```

**¿Cómo funciona?**
1. Cada 30 segundos, envía un request a cada servicio
2. Si responde ✅ → status = "healthy"
3. Si no responde ❌ y es crítico → lo reinicia automáticamente
4. Registra todo en los logs

**Servicios críticos** (critical: true):
- hub-ai-local
- sinkia-ops
- openclaw
- ollama

---

### **Función: Dynamic Model Selection with Fallbacks**
**Ubicación**: `synk-ia-model-selector.js`, línea 120

```javascript
async function selectModelWithFallback(taskType) {
  const taskProfile = config.task_profiles[taskType];
  const fallbackChain = [
    taskProfile.primary_model,
    taskProfile.secondary_model,
    taskProfile.tertiary_model,
    "llama:3b" // Fallback final
  ];
  
  for (let i = 0; i < fallbackChain.length; i++) {
    const model = fallbackChain[i];
    
    try {
      // Intenta conectar al modelo
      const health = await checkModelAvailability(model);
      
      if (health.available) {
        return {
          selected_model: model,
          attempt: i + 1,
          reason: health.reason,
          fallback_chain: fallbackChain
        };
      }
    } catch (error) {
      console.log(`❌ ${model} unavailable, trying next...`);
      // Sigue al siguiente modelo
    }
  }
  
  // Si todo falla
  throw new Error(`All models in fallback chain unavailable`);
}
```

**Ejemplo práctico:**

```
Solicitud: "Solve this complex math problem"
TaskType: "research"

Perfil research tiene:
- primary_model: "local-reason"
- secondary_model: "gpt-4o"
- tertiary_model: "claude-opus"

Intento 1: ¿Está local-reason disponible?
- SÍ → Usa local-reason ✅

Si hubiera estado caído:
Intento 2: ¿Está gpt-4o disponible?
- SÍ → Usa gpt-4o ✅

Si ambos estuvieran caídos:
Intento 3: ¿Está claude-opus disponible?
- SÍ → Usa claude-opus ✅

Si TODO falla:
Intento 4: Usa llama:3b (fallback final) ✅
```

---

### **Función: Intelligent Routing with Context Keywords**
**Ubicación**: `synk-ia-orchestrator.js`, línea 320

```javascript
async function intelligentRoute(request) {
  // 1. Analiza el contexto
  const context = analyzeContext(request);
  console.log(`📍 Detected context: ${context.type}`);
  
  // 2. Obtiene la herramienta recomendada
  const routing = config.routing.find(r => r.context === context.type);
  
  if (!routing) {
    console.log(`⚠️ No routing pattern found, using default`);
    return forwardToDefault(request);
  }
  
  // 3. Verifica disponibilidad de herramienta primaria
  const primaryTool = services[routing.primary_tool];
  const primaryHealth = await checkServiceHealth(routing.primary_tool);
  
  if (primaryHealth.healthy) {
    console.log(`✅ Routing to primary: ${routing.primary_tool}`);
    return forwardRequest(request, primaryTool);
  }
  
  // 4. Usa herramienta secundaria si primaria está caída
  const secondaryTool = services[routing.secondary_tool];
  console.log(`⚠️ Primary unavailable, using secondary: ${routing.secondary_tool}`);
  return forwardRequest(request, secondaryTool);
}
```

**Flujo visual:**

```
Request recibido: "Can you help me debug this TypeScript error?"

┌─ analyzeContext()
├─ Detecta keywords: ["debug", "TypeScript", "error"]
├─ Busca en config.routing
├─ Encuentra patrón "coding"
└─ context = "coding" ✅

┌─ getRouting("coding")
├─ primary_tool: "openclaw"
├─ secondary_tool: "hub-ai-local"
└─ confidence: 0.95

┌─ checkServiceHealth("openclaw")
├─ GET http://localhost:7999/health
├─ Respuesta: ✅ 200 OK
└─ status: "healthy"

✅ ROUTE: openclaw (primario disponible)
└─ Forward request a: http://localhost:7999/api/execute
```

---

## Ejemplos de Uso

### **Ejemplo 1: Solicitud de Coding**

```bash
curl -X POST http://localhost:9500/api/orchestrator/execute \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Refactor this function to use async-await",
    "code": "function getData() { return fetch(url); }"
  }'
```

**Lo que ocurre internamente:**

1. **Orchestrator recibe** la solicitud
2. **analyzeContext()** detecta: `context = "coding", confidence = 0.95`
3. **intelligentRoute()** encuentra: `primary_tool = "openclaw"`
4. **selectModel()** elige: `model = "local-claude-code"`
5. **checkServiceHealth()** verifica: `openclaw = healthy ✅`
6. **executeRequest()** envía a: `http://localhost:7999/api/execute`
7. **recordMetrics()** guarda: latencia, tokens, costo, éxito

**Respuesta:**
```json
{
  "routed_to": "openclaw",
  "model": "local-claude-code",
  "context": "coding",
  "confidence": 0.95,
  "response": "async function getData() { return await fetch(url); }",
  "latency_ms": 145,
  "tokens_used": 250
}
```

---

### **Ejemplo 2: Solicitud de Research**

```bash
curl -X POST http://localhost:9500/api/orchestrator/execute \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Analyze the impact of quantum computing on cryptography"
  }'
```

**Lo que ocurre:**

1. **analyzeContext()**: `context = "research", confidence = 0.92`
2. **intelligentRoute()**: `primary_tool = "sinkia-ops"`
3. **selectModel()**: `model = "gpt-4o"` (research needs reasoning)
4. **executeRequest()**: Envía a SynK-IA-Ops

---

### **Ejemplo 3: Solicitud con Fallback**

```bash
curl -X POST http://localhost:9500/api/orchestrator/execute \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Create a machine learning pipeline for image classification"
  }'
```

**Escenario: OpenClaw está caído**

1. **analyzeContext()**: `context = "coding"`
2. **intelligentRoute()**: Intenta `openclaw` → ❌ No responde
3. **Fallback activado**: Usa `hub-ai-local` → ✅ Disponible
4. **Respuesta**: Completa desde herramienta secundaria

---

## Configuración Avanzada

### **Personalizar Patrones de Enrutamiento**

Edita `synk-ia-global-config.yaml`:

```yaml
routing:
  - context: "custom-context"
    keywords: ["word1", "word2", "word3"]
    primary_tool: "tool-name"
    secondary_tool: "backup-tool"
    confidence: 0.90
```

### **Agregar un Nuevo Modelo**

1. **Actualiza model-selector.js:**
```javascript
const models = {
  "mi-modelo-nuevo": {
    name: "Mi Modelo Nuevo",
    type: "local|remote",
    best_for: ["task1", "task2"],
    latency: "100ms",
    cost: "free|$0.001/1K tokens",
    capabilities: ["capability1", "capability2"]
  }
};
```

2. **Agrega al perfil en config.yaml:**
```yaml
task_profiles:
  coding:
    primary_model: "mi-modelo-nuevo"
    secondary_model: "local-claude-code"
    tertiary_model: "qwen-coder"
```

---

## API Reference Completa

### **Orchestrator (Puerto 9500)**

#### **GET /api/orchestrator/status**
```bash
curl http://localhost:9500/api/orchestrator/status
```

**Respuesta:**
```json
{
  "system_status": "operational",
  "timestamp": "2026-08-03T20:18:23Z",
  "services": {
    "openclaw": {
      "status": "healthy",
      "port": 7999,
      "response_time_ms": 45,
      "last_check": "2026-08-03T20:18:20Z"
    },
    "sinkia-ops": {
      "status": "healthy",
      "port": 3001,
      "response_time_ms": 120,
      "last_check": "2026-08-03T20:18:20Z"
    },
    // ... más servicios
  },
  "uptime_percentage": 99.7,
  "total_requests_today": 1250
}
```

---

#### **POST /api/orchestrator/execute**
```bash
curl -X POST http://localhost:9500/api/orchestrator/execute \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Your request here",
    "context": "optional-override",
    "model": "optional-model-override",
    "parameters": {
      "temperature": 0.3,
      "max_tokens": 2000
    }
  }'
```

**Respuesta:**
```json
{
  "request_id": "req-12345",
  "routed_to": "openclaw",
  "model_used": "local-claude-code",
  "context_detected": "coding",
  "confidence": 0.95,
  "response": "Result from the model",
  "execution_time_ms": 245,
  "tokens_used": 350,
  "cost": 0.00,
  "status": "success"
}
```

---

#### **GET /api/orchestrator/model-select?context=coding&taskType=coding**
```bash
curl "http://localhost:9500/api/orchestrator/model-select?context=coding&taskType=coding"
```

**Respuesta:**
```json
{
  "selected_model": "local-claude-code",
  "alternative_models": [
    "local-coder-ollama",
    "qwen-coder",
    "llama:3b"
  ],
  "reason": "Best performance for coding tasks",
  "fallback_chain": [
    "local-claude-code",
    "local-coder-ollama",
    "qwen-coder",
    "llama:3b"
  ]
}
```

---

### **Model Selector (Puerto 9501)**

#### **GET /api/model-selector/models**
```bash
curl http://localhost:9501/api/model-selector/models
```

**Respuesta:**
```json
{
  "available_models": 7,
  "models": [
    {
      "name": "local-claude-code",
      "type": "local",
      "latency": "50ms",
      "cost": "free",
      "best_for": ["coding", "refactoring", "debugging"]
    },
    // ... 6 modelos más
  ]
}
```

---

#### **GET /api/model-selector/select?taskType=coding**
```bash
curl "http://localhost:9501/api/model-selector/select?taskType=coding"
```

**Respuesta:**
```json
{
  "selected_model": "local-claude-code",
  "task_type": "coding",
  "reason": "Optimal for coding tasks",
  "primary_model": "local-claude-code",
  "secondary_model": "local-coder-ollama",
  "tertiary_model": "qwen-coder",
  "fallback_model": "llama:3b"
}
```

---

#### **GET /api/model-selector/compare?models=local-claude-code,gpt-4o**
```bash
curl "http://localhost:9501/api/model-selector/compare?models=local-claude-code,gpt-4o"
```

**Respuesta:**
```json
{
  "comparison": {
    "local-claude-code": {
      "avg_latency_ms": 50,
      "success_rate": 0.96,
      "total_tokens_used": 50000,
      "cost": 0,
      "quality_score": 0.94
    },
    "gpt-4o": {
      "avg_latency_ms": 400,
      "success_rate": 0.99,
      "total_tokens_used": 150000,
      "cost": 45.50,
      "quality_score": 0.98
    }
  }
}
```

---

#### **GET /api/model-selector/costs**
```bash
curl http://localhost:9501/api/model-selector/costs
```

**Respuesta:**
```json
{
  "cost_tracking": {
    "tokens_this_hour": 250000,
    "tokens_today": 1500000,
    "tokens_this_month": 5000000,
    "cost_this_month": 450.50,
    "projected_monthly": 480.00,
    "breakdown_by_model": {
      "local-claude-code": 0,
      "gpt-4o": 250.50,
      "claude-opus": 200.00
    }
  }
}
```

---

## Troubleshooting

### **Problema: Orchestrator no inicia**

```bash
# Verifica si el puerto 9500 está en uso
lsof -i :9500

# Si está en uso, mata el proceso
kill -9 <PID>

# Intenta reiniciar
node synk-ia-orchestrator.js
```

---

### **Problema: Servicios no responden a health checks**

```bash
# Verifica la configuración de health_check en la YAML
cat synk-ia-global-config.yaml | grep health_check

# Prueba manualmente la salud de un servicio
curl http://localhost:7999/health  # OpenClaw
curl http://localhost:3001/health  # SynK-IA-Ops
```

---

### **Problema: Enrutamiento incorrecto**

```bash
# Verifica qué contexto se detectó
curl -X POST http://localhost:9500/api/orchestrator/execute \
  -d '{"content": "Your request"}' | jq '.context_detected'

# Verifica patrones de enrutamiento
cat synk-ia-global-config.yaml | grep -A 5 "routing:"
```

---

### **Problema: Modelo no disponible**

```bash
# Verifica modelos disponibles
curl http://localhost:9501/api/model-selector/models

# Verifica salud de modelo específico
curl http://localhost:9501/api/model-selector/health?model=local-claude-code
```

---

## Conclusión

**SYNK-OPS** te proporciona una plataforma unificada donde:

- ✅ **Cada solicitud** es enrutada inteligentemente
- ✅ **El modelo correcto** se selecciona automáticamente
- ✅ **La salud del sistema** se monitorea constantemente
- ✅ **Los fallbacks** garantizan disponibilidad
- ✅ **Todo se optimiza** basado en aprendizaje
- ✅ **Trabaja como una única pieza** unificada

**Tu ecosistema IA funciona sin fricción. 🚀**
