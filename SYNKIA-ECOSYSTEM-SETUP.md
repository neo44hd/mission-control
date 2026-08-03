# 🦇 SYNK-IA Ecosystem - Complete Setup & Configuration

## ✓ Estado del Ecosistema
**Última actualización:** 2026-07-09 10:31:55 GMT

### Servicios Operativos
- ✅ **Master Panel**: http://localhost:8010/master-panel.html (Dashboard Central)
- ✅ **Hub Control Center**: http://localhost:18791/ (Gestión de Agentes)
- ✅ **Memory Hub**: http://localhost:18792/ (Base de Datos de Memorias)
- ✅ **AI Provider Hub**: http://localhost:8010/ (Acceso a Modelos)
- ⚠️ **OpenClaw Gateway**: http://localhost:7999/ (Docker - Bajo demanda)

---

## 📊 Dashboard & Panel Maestro

### Panel Maestro Central
**URL:** http://localhost:8010/master-panel.html

Dashboard interactivo con:
- Estado en tiempo real de todos los servicios
- Información de los 4 agentes activos
- Accesos rápidos a cada servicio
- Handles de Telegram
- Auto-refresh cada 30 segundos

---

## 🤖 Agentes Activos y Bots de Telegram

### 1. **@Velin_dabot** (OpenClaw Main)
- **Rol:** Coordinador Principal
- **Modelo:** task-general
- **Superpoderes:** 
  - Acceso a sistemas
  - Memoria compartida
  - Auto-aprobación
- **URL:** Telegram Bot
- **Ubicación:** OpenClaw Main Agent

### 2. **@Diosa44_bot** (Hermes)
- **Rol:** Agente Multiusos
- **Modelo:** negentropy-claude-opus-4.7-9b
- **Superpoderes:**
  - Auto-aprobación
  - Memoria compartida
- **URL:** Telegram Bot
- **Ubicación:** Hermes Agent

### 3. **@rexiiiiiii_bot** (Claude Code)
- **Rol:** Programador Experto
- **Modelo:** local-claude-code
- **Superpoderes:**
  - Auto-aprobación
  - Memoria compartida
  - Sin restricciones de código
- **URL:** Telegram Bot
- **Ubicación:** Claude Code Agent

### 4. OpenClaw Coder
- **Rol:** Programador Especializado
- **Modelo:** local-claude-code
- **Superpoderes:**
  - Memoria compartida
  - Auto-aprobación
- **URL:** Shared Memory
- **Ubicación:** OpenClaw Coder Agent

---

## 🔗 Accesos Directos Actualizados

### En Escritorio (/Users/davidnows/Desktop/)

| Archivo | URL | Descripción |
|---------|-----|-------------|
| 🦇-BATCAVE-PANEL | http://localhost:8010/ | Panel BATCAVE Principal |
| 🌐-MASTER-GATEWAY | http://localhost:8010/api/master-gateway | API Gateway Maestro |
| 📈-MEJORAS | http://localhost:8010/api/improvements | Sistema de Mejoras |
| 🤖-DASHBOARD | http://localhost:8010/master-panel.html | Dashboard Master Control |
| 🤖-Hub-Control | http://localhost:18791/ | Hub Control Center |

**Formatos:**
- `.url` - Windows/Web shortcuts
- `.webloc` - macOS Safari shortcuts
- `.command` - Scripts ejecutables

---

## 📡 Servicios & Endpoints

### Hub Control Center (Puerto 18791)
```
URL: http://localhost:18791/
Tipo: Node.js Express
Función: Gestión y coordinación de agentes
Características:
  - Control de agentes
  - Gestión de tareas
  - Monitoreo de estado
```

### Memory Hub (Puerto 18792)
```
URL: http://localhost:18792/
Tipo: Python FastAPI
Función: Base de datos de memorias distribuida
Características:
  - 4,492 memorias indexadas
  - Búsqueda semántica
  - Integración embeddings
  - Acceso compartido entre agentes
```

### AI Provider Hub (Puerto 8010)
```
URL: http://localhost:8010/
Tipo: Node.js Express
Función: Acceso centralizado a modelos de IA

Endpoints principales:
  - GET  /health - Health check
  - GET  / - Dashboard
  - GET  /master-panel.html - Panel Maestro
  - POST /api/ai-hub/invoke - Invocación de modelos
  - GET  /api/agents/* - Gestión de agentes
  - GET  /api/registry/* - Catálogo de modelos
  - POST /api/discovery/* - Scan de repositorios
  - GET  /api/improvements/* - Sistema de mejoras
  - GET  /api/master-gateway/* - Gateway maestro

Modelos disponibles: 34 (11 locales + 5 cloud + 18 especializados)
  - Locales: Ollama models (llama3.2, llama2, etc.)
  - Cloud: OpenAI, Anthropic, Google, Replicate
  - Especializados: task-general, local-claude-code, etc.
```

### OpenClaw Gateway (Puerto 7999)
```
URL: http://localhost:7999/
Tipo: Docker Container
Función: Gateway de comunicación y routing
Características:
  - Orquestación de agentes
  - Integración Telegram
  - Enrutamiento inteligente
  - Almacenamiento de memoria compartida
```

---

## 📁 Estructura de Proyectos

### /Users/davidnows/Agentes-Pro/
```
├── hub/ (Node.js Express - Puerto 18791)
│   ├── server.js
│   └── package.json
├── memory-hub/ (Python FastAPI - Puerto 18792)
│   ├── server.py
│   └── indexer.py
├── openclaw/ (Docker - Puerto 7999)
├── litellm/ (Gateway de modelos)
├── hermes/ (Agente especial)
└── openclaw.json (Configuración)
```

### /Users/davidnows/synkia/ai-provider-hub/ (Puerto 8010)
```
├── server/
│   ├── index.js
│   └── routes/
│       ├── ai-hub.js
│       ├── agents.js
│       ├── dashboard.js
│       ├── master-gateway.js
│       └── improvements.js
├── public/
│   ├── dashboard.html
│   └── master-panel.html
└── package.json
```

---

## 💾 Configuración de Memoria Compartida

### Ruta: `/Users/davidnows/.openclaw/shared-memory/`

La memoria compartida permite que todos los agentes se comuniquen:
- **Formato:** JSON files en directorio `messages/`
- **Acceso:** Lectura/Escritura entre agentes
- **Sincronización:** Automática entre Memory Hub

### Ejemplo de Comunicación:
```json
{
  "timestamp": "2026-07-09T10:31:55Z",
  "agent": "@Velin_dabot",
  "message": "Actualizando estado del sistema",
  "data": { "status": "operational" }
}
```

---

## 🔧 Comandos Útiles

### Iniciar Ecosistema Completo
```bash
/Users/davidnows/Desktop/🦇-SYNKIA-MASTER-V3.command
```

### Verificar Estado de Servicios
```bash
lsof -i -P -n | grep LISTEN | grep -E ":8010|:18791|:18792|:7999"
```

### Ver Logs
```bash
# Hub Control Center
tail -f /tmp/hub.log

# Memory Hub
tail -f /tmp/memory-hub.log

# AI Provider Hub
tail -f /tmp/ai-hub.log

# Master Panel
tail -f /tmp/master-panel.log
```

### Reiniciar Servicios Individuales
```bash
# Matar Hub
lsof -i :18791 | grep LISTEN | awk '{print $2}' | xargs kill -9

# Matar Memory Hub
lsof -i :18792 | grep LISTEN | awk '{print $2}' | xargs kill -9

# Matar AI Provider
lsof -i :8010 | grep LISTEN | awk '{print $2}' | xargs kill -9
```

---

## 📋 Características del Sistema

### Superpoderes de Agentes
- ✅ Acceso a archivos (lectura/escritura)
- ✅ Navegación web
- ✅ Ejecución de habilidades (skills)
- ✅ Memoria compartida
- ✅ Auto-aprobación
- ✅ Integración con Telegram

### Acciones Críticas Protegidas
- ❌ delete_system
- ❌ format_disk
- ❌ send_money
- ❌ shutdown

(Requieren confirmación manual)

### Modelos de IA Disponibles
**11 Locales (Ollama):**
- llama3.2, llama2, mistral, neural-chat, etc.

**5 Cloud:**
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- Google (Gemini)
- Replicate

**18 Especializados:**
- task-general
- local-claude-code
- negentropy-claude-opus-4.7-9b
- Y más...

---

## 🚀 Uso Rápido

### Acceder al Panel Maestro
1. Abre tu navegador
2. Ve a: **http://localhost:8010/master-panel.html**
3. Verás estado de todos los servicios
4. Haz clic en cualquier servicio para abrir

### Hablar con Agentes por Telegram
1. Busca los bots:
   - **@Velin_dabot** - Coordinador
   - **@Diosa44_bot** - Hermes (Multiusos)
   - **@rexiiiiiii_bot** - Claude Code (Experto)
2. Envía comandos/preguntas
3. El agente responderá usando memoria compartida

### Acceder a Hub Control Center
1. Navegador: **http://localhost:18791/**
2. Gestiona y monitorea agentes
3. Coordina tareas entre sistemas

---

## 📞 Contacto & Soporte

**Configuración actualizada:** 2026-07-09
**Eco-sistema:** Completamente funcional
**Próximas mejoras:** Auto-escalado, dashboard avanzado

---

## ✅ Checklist Final

- ✅ Todos los servicios iniciados
- ✅ Accesos directos actualizados
- ✅ Bots de Telegram configurados
- ✅ Panel Maestro funcional
- ✅ Memoria compartida activa
- ✅ 34 modelos de IA disponibles
- ✅ 4 agentes operativos
- ✅ Gateway OpenClaw listo

**Estado:** 🟢 TODOS LOS SISTEMAS OPERATIVOS
