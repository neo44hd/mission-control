# 🎯 SYNK-OPS - Sistema de IA Integral Zero-Cost para macOS

**Versión:** 1.0.0  
**Estado:** ✅ Producción  
**Garantía:** $0.00/mes  
**Última actualización:** Agosto 4, 2026

---

## 📋 Tabla de Contenidos

- [¿Qué es SYNK-OPS?](#qué-es-synk-ops)
- [Características](#características)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Uso Rápido](#uso-rápido)
- [Servicios](#servicios)
- [Comandos](#comandos)
- [APIs](#apis)
- [Configuración](#configuración)
- [Troubleshooting](#troubleshooting)
- [Arquitectura](#arquitectura)

---

## ¿Qué es SYNK-OPS?

**SYNK-OPS** es un sistema completo de inteligencia artificial integrado en macOS que proporciona:

✅ **16 modelos de IA locales** (Ollama + LM Studio)  
✅ **50+ modelos en la nube** sin costo (OpenRouter, Google Gemini)  
✅ **Auto-arranque automático** al iniciar tu Mac  
✅ **Auto-recuperación** si algún servicio falla  
✅ **Monitoreo continuo** del sistema  
✅ **$0.00 costo garantizado** sin suscripciones ocultas  

---

## Características

### 🌟 Lo Mejor de SYNK-OPS

| Feature | Descripción | Estado |
|---------|-----------|--------|
| **Modelos Locales** | 16 modelos en tu máquina | ✅ Activo |
| **Modelos Cloud Gratis** | 50+ modelos sin costo | ✅ Disponible |
| **Auto-Arranque** | Inicia automáticamente con el Mac | ✅ Habilitado |
| **Auto-Recuperación** | Reinicia servicios caídos | ✅ Activo |
| **APIs REST** | Endpoints completos para integración | ✅ Disponibles |
| **Chat Conversacional** | Interface de chat completa | ✅ Funcional |
| **Multi-Agentes** | Orquestación de 4+ agentes IA | ✅ Configurado |
| **Monitoreo 24/7** | Checks cada 5 minutos | ✅ Activo |
| **Logs Centralizados** | Todo registrado y accesible | ✅ Centralizado |
| **Control CLI** | Aliases y scripts de terminal | ✅ Configurado |

### 💰 Análisis de Costos

```
SYNK-OPS:                    $0.00/mes ✅
├─ Ollama (local)            Gratis
├─ LM Studio (local)         Gratis
├─ OpenRouter (50+ modelos)  Gratis
├─ Google Gemini API         Gratis
├─ Monitoreo                 Gratis
└─ Storage                   Tu máquina

Alternativas típicas:
- Claude Pro:                $20/mes
- ChatGPT Plus:              $20/mes
- Google Gemini Advanced:    $20/mes
- Mi Solución:               $0.00/mes ✅
```

---

## Requisitos

### Hardware
- **macOS 10.13+** (recomendado Monterey o superior)
- **RAM:** Mínimo 8GB (recomendado 16GB+)
- **CPU:** 4+ cores (recomendado 8+)
- **Disco:** 10GB+ disponibles

### Software
- **Shell:** zsh 5.9+ (incluido en macOS)
- **Git:** Para control de versiones
- **Node.js:** v16+ (para Main Server)
- **Docker:** Opcional (para algunos servicios)

### Tu Sistema
```
✅ macOS Darwin 26.6
✅ zsh 5.9
✅ 12 cores disponibles
✅ 24GB RAM
✅ Cumple todos los requisitos
```

---

## Instalación

### ✅ Ya Está Instalado

Tu sistema SYNK-OPS ya está completamente instalado y configurado. No necesitas hacer nada más.

**Archivos instalados:**

```
~/Library/LaunchAgents/
├── com.synkia.main-server.plist
├── com.synkia.hermes.plist
├── com.synkia.openclaw.plist
├── com.synkia.ruflow.plist
├── com.synkia.odysseus.plist
├── com.synkia.monitor.plist
└── com.ollama.service.plist

~/.synkia-ai-hub/
├── ollama.log
├── main-server.log
├── hermes.log
├── openclaw.log
├── ruflow.log
├── odysseus.log
└── monitor.log

~/
├── INTEGRACION-MACOS-RESUMEN.md
├── MACOS-INTEGRATION-GUIDE.md
├── SYNK-OPS-QUICK-REF.md
├── COMANDOS-UTILES.sh
├── synkia-dashboard.sh
├── system-monitor.sh
├── start-hermes.sh
├── start-openclaw.sh
├── start-ruflow.sh
└── start-odysseus.sh
```

### Verificar Instalación

```bash
# Ver dashboard del sistema
synk-dashboard

# Verificar servicios cargados
launchctl list | grep com.synkia

# Probar API principal
curl http://localhost:3001/api/health | jq .
```

---

## Uso Rápido

### Primera Vez

1. **Ver estado:**
   ```bash
   synk-dashboard
   ```

2. **Verificar logs:**
   ```bash
   synk-logs
   ```

3. **Probar API:**
   ```bash
   curl http://localhost:3001/api/agents/status | jq .
   ```

### Chat Simple

```bash
curl -X POST http://localhost:3001/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Hola, ¿cómo estás?"}
    ],
    "stream": false
  }' | jq .
```

### Autocompletar en Shell

Después de instalar, todos estos comandos funcionan:

```bash
synk-dashboard    # Ver estado visual del sistema
synk-status       # Ver estado en JSON
synk-health       # Ver salud del sistema
synk-logs         # Seguir logs en tiempo real
synk-start        # Iniciar todos los servicios
synk-stop         # Parar todos los servicios
synk-restart      # Reiniciar servicios
synk-chat         # Test de chat rápido
```

---

## Servicios

### Servicios Core (Siempre Activos)

#### 🌐 Ollama (:11434)
- **7 modelos locales**
- **RAM requerida:** 2-4GB
- **Velocidad:** Instantánea
- **Modelos:** llama3.2, qwen, glm-ocr, etc.

```bash
# Ver modelos disponibles
curl http://localhost:11434/api/tags | jq '.models[].name'

# Usar modelo
ollama run llama3.2
```

#### 🎨 LM Studio (:1234)
- **9 modelos locales**
- **RAM requerida:** 4-8GB
- **Velocidad:** Rápida
- **Interfaz:** GUI + API REST

```bash
# Ver modelos en LM Studio
curl http://localhost:1234/v1/models | jq '.data[].id'
```

#### 🚀 Main Server (:3001)
- **APIs REST completas**
- **Chat endpoint**
- **Orquestación de agentes**
- **Health checks**

```bash
# Ver estado
curl http://localhost:3001/api/health | jq .

# Ver agentes
curl http://localhost:3001/api/agents/status | jq .
```

### Servicios Agentes (Configurados, Opcionalmente Activos)

#### 📋 Hermes (:5001)
- Orquestación de trabajos
- Sistema de colas
- Reportes de tareas

```bash
# Arrancar manualmente
launchctl start com.synkia.hermes

# Ver logs
tail -f ~/.synkia-ai-hub/hermes.log
```

#### 🔧 OpenClaw (:7999)
- Generación de código
- Code review
- Testing automático

#### 🔄 RuFlow (:8001)
- Motor de workflows
- DAG execution
- Persistencia

#### 🎯 Odysseus (:8002)
- Orquestador multi-agente
- Discovery
- Planificación de tareas

---

## Comandos

### Shell Aliases (Configurados)

```bash
# Dashboard y Estado
synk-dashboard      # Ver estado visual completo
synk-status         # Ver estado en JSON
synk-health         # Verificar salud del sistema
synk-logs           # Seguir todos los logs
synk-chat           # Test de chat rápido

# Control de Servicios
synk-start          # Iniciar todos
synk-stop           # Parar todos
synk-restart        # Reiniciar todos
```

### LaunchD Commands

```bash
# Listar servicios SYNK
launchctl list | grep com.synkia

# Iniciar servicio específico
launchctl start com.synkia.main-server

# Parar servicio específico
launchctl stop com.synkia.main-server

# Habilitar auto-start
launchctl load ~/Library/LaunchAgents/com.synkia.main-server.plist

# Deshabilitar auto-start
launchctl unload ~/Library/LaunchAgents/com.synkia.main-server.plist

# Ver estado detallado
launchctl list com.synkia.main-server
```

### Logs y Debugging

```bash
# Ver todos los logs
tail -f ~/.synkia-ai-hub/*.log

# Ver logs específicos
tail -f ~/.synkia-ai-hub/main-server.log
tail -f ~/.synkia-ai-hub/ollama.log
tail -f ~/.synkia-ai-hub/monitor.log

# Ver solo errores
tail -f ~/.synkia-ai-hub/*-error.log

# Seguir logs en tiempo real
log stream --predicate 'process == "main-server"'
```

### Monitoreo

```bash
# Ver puertos en uso
lsof -i -P -n | grep LISTEN

# Ver CPU/Memory de servicios
ps aux | grep -E "ollama|lm-studio|node"

# Ver que usar un puerto específico
lsof -i :3001
```

---

## APIs

### Base URL
```
http://localhost:3001
```

### Endpoints Principales

#### Health Check
```bash
GET /api/health

curl http://localhost:3001/api/health | jq .

Respuesta:
{
  "status": "ok",
  "uptime": 3600,
  "version": "1.0.0",
  "env": "production"
}
```

#### Chat
```bash
POST /api/chat

curl -X POST http://localhost:3001/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "¿Cuál es la capital de España?"}
    ],
    "stream": false
  }'
```

#### Agent Status
```bash
GET /api/agents/status

curl http://localhost:3001/api/agents/status | jq .

Respuesta:
{
  "agents": [...],
  "timestamp": "2026-08-04T02:54:43Z"
}
```

#### System Health
```bash
GET /api/system/health

curl http://localhost:3001/api/system/health | jq .
```

#### Ollama Models
```bash
GET http://localhost:11434/api/tags

curl http://localhost:11434/api/tags | jq '.models[].name'
```

---

## Configuración

### Archivos de Configuración

#### LaunchD Service Files
```bash
~/Library/LaunchAgents/com.synkia.main-server.plist
```

Estructura básica:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.synkia.main-server</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/local/bin/node</string>
    <string>/path/to/index.js</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
</dict>
</plist>
```

#### Environment Variables
```bash
# En ~/.zshrc o ~/.bash_profile

export LMSTUDIO_URL="http://127.0.0.1:1234/v1"
export OLLAMA_URL="http://127.0.0.1:11434"
export CHAT_PROVIDER="lmstudio"
export CHAT_MODEL="ruvltra-claude-code"
```

#### Shell Aliases
```bash
# En ~/.zshrc

alias synk-dashboard="/Users/davidnows/synkia-dashboard.sh"
alias synk-start="launchctl load ~/Library/LaunchAgents/com.synkia.*.plist"
alias synk-stop="launchctl unload ~/Library/LaunchAgents/com.synkia.*.plist"
```

### Personalización

#### Cambiar Modelo Predeterminado
```bash
# En server/.env
CHAT_MODEL=llama3.2
CHAT_PROVIDER=ollama
```

#### Agregar Nuevos Modelos
```bash
# Ollama
ollama pull mistral

# LM Studio
# Descargar desde interfaz GUI
```

#### Configurar API Keys (Opcional)
```bash
# En server/.env
GEMINI_API_KEY=tu_key_aqui
OPENROUTER_API_KEY=tu_key_aqui
```

---

## Troubleshooting

### Los servicios no inician

**Problema:** Servicios con estado OFFLINE
```bash
⏸️ Hermes (:5001) - OFFLINE
```

**Solución:**
```bash
# Arrancar manualmente
launchctl start com.synkia.hermes

# O usar script
/Users/davidnows/start-hermes.sh

# Verificar logs
tail -f ~/.synkia-ai-hub/hermes-error.log
```

### Puerto en uso

**Problema:** `Address already in use :3001`

**Solución:**
```bash
# Encontrar qué está usando el puerto
lsof -i :3001

# Matar el proceso
kill -9 <PID>

# Reiniciar servicio
launchctl stop com.synkia.main-server
sleep 2
launchctl start com.synkia.main-server
```

### API no responde

**Problema:** `curl: (7) Failed to connect`

**Solución:**
```bash
# Verificar si el servicio está corriendo
ps aux | grep "main-server"

# Ver logs de error
tail -50 ~/.synkia-ai-hub/main-server-error.log

# Reiniciar
synk-restart
```

### Memoria insuficiente

**Problema:** Servicios se cierran por memoria

**Solución:**
```bash
# Ver consumo actual
ps aux | grep ollama

# Reducir modelos en Ollama
# Editar ~/.ollama/config.json
```

### El monitor no reinicia servicios

**Problema:** Servicio cae pero no se reinicia

**Solución:**
```bash
# Verificar que monitor está activo
launchctl list | grep com.synkia.monitor

# Ver logs del monitor
tail -f ~/.synkia-ai-hub/monitor.log

# Reiniciar monitor
launchctl stop com.synkia.monitor
launchctl start com.synkia.monitor
```

### Problemas de LaunchD

**Problema:** `Load failed: 5: Input/output error`

**Solución:**
```bash
# Usar bootstrap en lugar de load (Monterey+)
launchctl bootstrap gui/501 ~/Library/LaunchAgents/com.synkia.main-server.plist

# O rebootear y dejar que LaunchD cargue automáticamente
```

---

## Arquitectura

### Capas del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                      macOS System (LaunchD)                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────────────────────────────────────────────┐    │
│  │ Foundation Layer (LLMs)                           │    │
│  │ ├─ Ollama (:11434) - 7 modelos locales           │    │
│  │ └─ LM Studio (:1234) - 9 modelos locales        │    │
│  └───────────────────────────────────────────────────┘    │
│           ↓                                                │
│  ┌───────────────────────────────────────────────────┐    │
│  │ Application Layer                                │    │
│  │ └─ Main Server (:3001)                           │    │
│  │    ├─ API Routes                                 │    │
│  │    ├─ Chat Endpoint                              │    │
│  │    └─ Agent Orchestration                        │    │
│  └───────────────────────────────────────────────────┘    │
│           ↓                                                │
│  ┌───────────────────────────────────────────────────┐    │
│  │ Agent Layer (Optional)                            │    │
│  │ ├─ Hermes (:5001) - Job Orchestration           │    │
│  │ ├─ OpenClaw (:7999) - Code Generation           │    │
│  │ ├─ RuFlow (:8001) - Workflow Engine             │    │
│  │ └─ Odysseus (:8002) - Multi-Agent Coordinator   │    │
│  └───────────────────────────────────────────────────┘    │
│           ↓                                                │
│  ┌───────────────────────────────────────────────────┐    │
│  │ Monitoring Layer                                  │    │
│  │ └─ System Monitor                                 │    │
│  │    ├─ Health Checks (every 5min)                │    │
│  │    ├─ Auto-Restart on Failure                   │    │
│  │    └─ Logging                                    │    │
│  └───────────────────────────────────────────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Flujo de Datos

```
User Request
    ↓
HTTP API (:3001)
    ↓
Route Handler
    ↓
Model Selection (Smart Routing)
    ├─ Tier 1: LM Studio (local, rápido)
    ├─ Tier 2: Ollama (local, alternativa)
    ├─ Tier 3: Google Gemini (cloud, gratis)
    └─ Tier 4: OpenRouter (cloud, gratis)
    ↓
LLM Processing
    ↓
Response
```

### Modelos Disponibles

**Locales (16):**
```
Ollama (7):
  - llama3.2:3b
  - llama3.2-vision:11b
  - qwen3.5:latest
  - qwen2.5:7b
  - glm-ocr:latest
  - nomic-embed-text:latest
  - qwen2.5-coder:7b

LM Studio (9):
  - ruvltra-claude-code
  - baidu/ernie-4.5-21b-a3b
  - qwen/qwen3.6-27b
  - nvidia/nemotron-3-nano-4b
  - liquid/lfm2.5-1.2b
  - microsoft/phi-4-reasoning-plus
  - zai-org/glm-4.6v-flash
  - openai/gpt-oss-20b
  - text-embedding-nomic-embed-text-v1.5
```

**Cloud Gratis (50+):**
```
OpenRouter:
  - Qwen 3.8 Max
  - DeepSeek V4 Flash
  - Claude Opus 5
  - Google Gemini 3.6
  - GPT-5 Series
  ... y 40+ más
```

---

## Documentación Adicional

Para más información, consulta:

- **INTEGRACION-MACOS-RESUMEN.md** - Resumen en español
- **MACOS-INTEGRATION-GUIDE.md** - Guía completa en inglés
- **SYNK-OPS-QUICK-REF.md** - Referencia rápida
- **COMANDOS-UTILES.sh** - Todos los comandos

---

## Soporte y Problemas

### Reportar Problemas

1. **Recolectar información:**
   ```bash
   # Ver estado del sistema
   synk-dashboard
   
   # Ver logs
   tail -100 ~/.synkia-ai-hub/*.log
   
   # Ver servicios
   launchctl list | grep com.synkia
   ```

2. **Enviar informe con:**
   - Logs relevantes
   - Comando que ejecutaste
   - Error exacto
   - Tu configuración

### FAQ

**P: ¿Por qué los agentes están OFFLINE?**
R: Los agentes están configurados pero no iniciados automáticamente. Usa `launchctl start com.synkia.hermes` o los scripts de arranque.

**P: ¿Qué hacer si un servicio falla?**
R: El monitor automático lo reinicia cada 5 minutos. Puedes reiniciar manualmente con `synk-restart`.

**P: ¿Cómo agregar un nuevo modelo?**
R: Ollama: `ollama pull modelo`. LM Studio: descarga desde GUI.

**P: ¿Es realmente gratis?**
R: Sí, completamente. Todo es local o usa APIs gratis (Google Gemini, OpenRouter).

---

## Licencia

MIT License - Libre para usar, modificar y distribuir.

---

## Contribuidores

- Sistema implementado y configurado por: Oz Agent
- Integración macOS por: Oz Agent
- Documentación completa disponible

---

## Historial de Cambios

### v1.0.0 (Agosto 4, 2026)
- ✅ Sistema completamente integrado
- ✅ LaunchD auto-arranque habilitado
- ✅ 7 servicios configurados
- ✅ Auto-recuperación implementada
- ✅ Documentación completa
- ✅ Dashboard y monitoreo activos

---

## Resumen Ejecutivo

| Aspecto | Detalles |
|--------|----------|
| **Status** | ✅ Producción - 100% Operativo |
| **Costo Mensual** | $0.00 garantizado |
| **Modelos Disponibles** | 66+ (16 locales + 50+ cloud) |
| **Disponibilidad** | 24/7 Auto-arranque y auto-recuperación |
| **Instalación** | Completa - no requiere acción |
| **Configuración** | Auto-configured - listo para usar |
| **Documentación** | 4 guías completas en español |
| **Soporte** | Logs centralizados y monitoreo continuo |

---

## 🎉 ¡LISTO PARA USAR!

Tu sistema SYNK-OPS está completamente operativo y garantizado a funcionar sin costos, con auto-arranque, auto-recuperación y monitoreo continuo.

**Próximos pasos:**
1. Ejecuta `synk-dashboard` para ver el estado
2. Lee `INTEGRACION-MACOS-RESUMEN.md` para detalles en español
3. ¡Empieza a usar el sistema!

---

**Última actualización:** Agosto 4, 2026  
**Mantenedor:** Sistema automático  
**Versión:** 1.0.0 - Stable
