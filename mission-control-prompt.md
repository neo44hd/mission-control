# MISSION CONTROL - PANEL DE ADMINISTRACIÓN INTEGRAL
## Prompt para OpenClaw/Claude Code

### OBJETIVO
Construir un panel de control web tipo "god mode" con autenticación segura, métricas en tiempo real, gestor de archivos, terminal web, logs centralizados e integración con modelos locales (Ollama/LM Studio).

### STACK TECNOLÓGICO REQUERIDO

#### 1. BACKEND - Python FastAPI
```python
# Estructura del servidor
backend/
├── main.py              # FastAPI app principal
├── routers/
│   ├── auth.py          # JWT + PAM authentication macOS
│   ├── metrics.py       # Sistema: CPU, RAM, disco, red, procesos
│   ├── files.py         # Gestor de archivos (listar, leer, escribir, mover, copiar)
│   ├── logs.py          # Logs del sistema (syslog, console)
│   ├── terminal.py      # WebSocket para terminal interactiva
│   ├── ai_analysis.py       # Integración Ollama/LM Studio
│   ├── processes.py           # Control de procesos del sistema
│   ├── docker_control.py      # Control completo Docker Desktop/containers
│   ├── ollama_control.py      # Gestión de modelos Ollama
│   ├── lmstudio_control.py    # Control servidor LM Studio
│   ├── openclaw_terminal.py   # Terminal dedicado OpenClaw/Claude Code
│   └── services_control.py    # brew services, launchctl
├── services/
│   ├── system_monitor.py    # Monitor de recursos
│   ├── ai_engine.py         # Cliente Ollama/LM Studio
│   ├── file_manager.py      # Operaciones seguras de archivos
│   ├── docker_client.py     # Cliente Docker API
│   ├── ollama_manager.py    # Gestión modelos Ollama
│   └── service_controller.py  # Control servicios macOS
├── models/
│   ├── schemas.py       # Pydantic models
│   └── database.py      # SQLite para sesiones/caché
└── config.py            # Configuración Tailscale ACLs, auth
```

#### 2. FRONTEND - React + TypeScript
```typescript
// Estructura frontend
frontend/
├── src/
│   ├── components/
│   │   ├── Dashboard.tsx        # Panel principal con métricas
│   │   ├── FileManager.tsx      # Explorador de archivos drag-drop
│   │   ├── Terminal.tsx         # Terminal web (xterm.js)
│   │   ├── LogViewer.tsx        # Visualizador de logs + AI insights
│   │   ├── ProcessManager.tsx   # Lista de procesos + control
│   │   ├── AIModule.tsx         # Chat con modelo local para troubleshooting
│   │   ├── AuthGate.tsx         # Login con Tailscale awareness
│   │   ├── ServiceHub.tsx       # Centro de control Docker/Ollama/LMStudio/OpenClaw
│   │   ├── DockerPanel.tsx      # Control containers, imágenes, redes, volúmenes
│   │   ├── OllamaManager.tsx    # Gestión modelos Ollama (listar, pull, eliminar)
│   │   ├── LMStudioPanel.tsx    # Control servidor LM Studio
│   │   └── OpenClawConsole.tsx  # Terminal dedicado para Claude Code
│   ├── hooks/
│   │   ├── useMetrics.ts        # WebSocket realtime metrics
│   │   ├── useAI.ts             # Comunicación con Ollama
│   │   └── useTailscale.ts      # Detección red Tailscale
│   ├── services/
│   │   ├── api.ts               # Cliente API
│   │   └── websocket.ts         # Conexiones WS
│   └── App.tsx
└── package.json
```

#### 3. INTEGRACIÓN IA LOCAL
```python
# Configuración AI Engine
AI_ENGINE = {
    "primary": "ollama",  # o "lmstudio" según disponibilidad
    "ollama": {
        "base_url": "http://localhost:11434",
        "model": "llama3.2:latest",  # o el modelo que tenga disponible
        "timeout": 30
    },
    "lmstudio": {
        "base_url": "http://localhost:1234/v1",
        "model": "local-model"
    }
}

# Capacidades IA integradas:
# 1. Análisis de logs: Detectar patrones de error, sugerir fixes
# 2. Diagnóstico sistema: Analizar métricas y proponer optimizaciones
# 3. Terminal inteligente: Sugerir comandos según contexto
# 4. File assistant: Buscar archivos, analizar contenido
```

#### 4. SEGURIDAD Y ACCESO
```python
# Tailscale ACL Integration
# Detectar si la conexión viene de Tailscale (100.64.x.x/10.x en tailscale)
# Solo permitir acceso si:
# 1. Viene de red Tailscale (IP 100.64.x.x - 100.127.x.x)
# 2. Dispositivo está en lista authorized_machines
# 3. Autenticación local válida (usuario macOS)

AUTH_REQUIREMENTS = {
    "local_network": False,      # Requerir auth incluso en LAN
    "tailscale_required": True,  # Solo permitir desde Tailscale
    "mfa_optional": False,       # 2FA opcional
    "session_timeout": 3600,     # 1 hora
    "max_attempts": 3
}
```

### FUNCIONALIDADES REQUERIDAS

#### Dashboard Principal
- [ ] Métricas en tiempo real (WebSocket): CPU (por core), RAM (usada/libre/caché), Disco (por volumen), Red (up/down), Temperatura (si disponible)
- [ ] Gráficos históricos (últimas 24h, 7 días)
- [ ] Procesos activos con opción de kill/prioridad
- [ ] Alertas visuales para umbrales (CPU>80%, RAM>90%, disco<10%)

#### Gestor de Archivos
- [ ] Navegación completa del sistema (con límites de seguridad)
- [ ] Drag & drop para subir archivos
- [ ] Editor de texto integrado (código, logs, configs)
- [ ] Operaciones: copiar, pegar, mover, renombrar, eliminar, comprimir
- [ ] Búsqueda con indexado + IA (buscar contenido dentro de archivos)
- [ ] Preview de imágenes, PDFs, videos

#### Terminal Web
- [ ] Terminal interactiva vía WebSocket
- [ ] Múltiples tabs
- [ ] Soporte colores y comandos interactivos (htop, vim, etc.)
- [ ] Historial de comandos
- [ ] Autocompletado con IA (sugerir comandos basados en contexto)

#### Sistema de Logs
- [ ] Agregación de: system.log, kernel.log, Docker logs, app logs
- [ ] Búsqueda full-text con filtros (fecha, nivel, app)
- [ ] Análisis IA: "¿Qué errores hay?", "¿Qué pasó a las 3am?"
- [ ] Exportar logs

#### Módulo IA Integrado
- [ ] Chat panel lateral siempre disponible
- [ ] Contexto automático: "Analiza estos logs", "¿Por qué está lento el sistema?"
- [ ] Comandos sugeridos con botón "Ejecutar"
- [ ] Análisis de archivos: "Resume este log", "Encuentra errores"

#### Centro de Control de Servicios (Docker, Ollama, LM Studio, OpenClaw)
- [ ] **Docker**: Listar/start/stop containers, ver logs en tiempo real, ejecutar comandos en contenedores, gestionar imágenes, redes y volúmenes
- [ ] **Ollama Manager**: Ver modelos instalados, pull nuevos modelos, eliminar modelos, cambiar modelo activo, ver uso de VRAM/RAM por modelo, reiniciar servicio
- [ ] **LM Studio Integration**: Conectar a servidor local de LM Studio (puerto 1234), cambiar modelo cargado, verificar estado del servidor
- [ ] **OpenClaw Terminal**: Terminal dedicado para ejecutar OpenClaw/Claude Code con acceso al proyecto actual, historial de comandos claude, integración con el workspace
- [ ] **Process Control**: Start/stop/restart cualquier servicio (brew services, launchctl), ver logs de servicios del sistema
- [ ] **Resource Allocation**: Ver qué servicios consumen más recursos, alertas si Ollama/Docker usan demasiada RAM/VRAM

### ESTRUCTURA DE CARPETAS DEL PROYECTO
```
~/mission-control/
├── README.md
├── docker-compose.yml          # Opcional para deploy
├── requirements.txt            # Python deps
├── package.json               # Node deps
├── .env.example               # Variables de entorno
├── backend/
│   ├── main.py
│   ├── routers/
│   ├── services/
│   └── config.py
├── frontend/
│   ├── src/
│   ├── public/
│   └── vite.config.ts
└── scripts/
    ├── setup.sh              # Instalación automática
    └── tailscale-check.sh    # Verificación de ACLs
```

### REQUISITOS TÉCNICOS

#### Backend (Python)
```
fastapi
uvicorn[standard]
websockets
psutil          # Métricas del sistema
pytail          # Seguimiento de logs
python-pam      # Auth macOS
pyjwt
aiofiles        # Operaciones archivo async
httpx           # Cliente HTTP para Ollama
sqlite3         # Base datos local
```

#### Frontend
```
react
typescript
@tanstack/react-query    # Queries
recharts                 # Gráficos
xterm                    # Terminal web
@xterm/addon-fit
@xterm/addon-web-links
socket.io-client         # WebSocket
axios
zustand                  # Estado global
tailwindcss             # UI
lucide-react            # Iconos
react-router-dom        # Routing
```

### IMPLEMENTACIÓN PASO A PASO

#### Fase 1: Backend Core (2-3 horas)
1. Configurar FastAPI con autenticación JWT + PAM
2. Implementar /metrics endpoint con WebSocket para realtime
3. Crear servicio de monitoreo con psutil (CPU, RAM, disco, red)
4. Endpoints de archivos seguros (validar paths, no permitir /etc/sudoers etc)
5. WebSocket para terminal (node-pty equivalent en Python: pty + asyncio)

#### Fase 2: Frontend Dashboard (2-3 horas)
1. Setup React + Vite + Tailwind
2. Componente Dashboard con gráficos Recharts
3. Conexión WebSocket a métricas
4. Panel de procesos con kill/prioridad
5. Layout responsive (sidebar + main content)

#### Fase 3: File Manager (2 horas)
1. Explorador de archivos tipo VS Code
2. Drag-drop upload
3. Editor Monaco o CodeMirror integrado
4. Operaciones CRUD archivo

#### Fase 4: Terminal Web (1-2 horas)
1. Integrar xterm.js
2. WebSocket bidireccional
3. Colores y terminal interactivo real

#### Fase 5: Logs + IA (2-3 horas)
1. Agregador de logs (tail -f vía WebSocket)
2. Panel IA con historial de chat
3. Integración Ollama API (chat completions)
4. Funciones tool-calling: "analizar_logs", "buscar_archivo", "ejecutar_comando"

#### Fase 6: Seguridad + Tailscale (1 hora)
1. Middleware para detectar IP Tailscale
2. Lista de dispositivos autorizados (chequear Tailscale API o hardcoded)
3. Auth gate en frontend
4. Session management

### VARIABLES DE ENTORNO (.env)
```
# Servidor
MC_HOST=0.0.0.0
MC_PORT=8080
MC_SECRET_KEY=generate-strong-secret-here

# Autenticación
MC_AUTH_REQUIRED=true
MC_TAILSCALE_ONLY=true
MC_ALLOWED_TAILSCALE_IPS=100.64.x.x,100.65.x.x  # IPs específicas
MC_SESSION_TIMEOUT=3600

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:latest
OLLAMA_ENABLED=true

# LM Studio (alternativa)
LMSTUDIO_BASE_URL=http://localhost:1234/v1
LMSTUDIO_ENABLED=false

# Paths (seguridad)
MC_ALLOWED_PATHS=/Users,/Applications,/opt,/tmp
MC_BLOCKED_PATHS=/etc/sudoers,/private/var/db,/System

# Tailscale
TAILSCALE_AUTH_KEY=tskey-auth-xxxx  # Para API Tailscale si se usa
```

### COMANDOS DE INICIO
```bash
# Después de instalar, iniciar el sistema:
cd ~/mission-control
source .env

# Terminal 1: Backend
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8080

# Terminal 2: Frontend
cd frontend
npm run dev

# Acceso: http://localhost:5173 (frontend) -> http://localhost:8080 (API)

# Para producción:
npm run build  # Frontend -> ../backend/static
python backend/main.py  # Sirve todo en :8080
```

### CONSIDERACIONES DE SEGURIDAD CRÍTICAS

1. **Validación de paths**: NUNCA permitir acceso a archivos fuera de allowed_paths
2. **Escape de comandos terminal**: Sanitizar todo input antes de exec
3. **Rate limiting**: Limitar requests a IA y operaciones de archivo
4. **Audit logging**: Registrar todo comando ejecutado, archivo accedido
5. **Tailscale verification**: Confirmar que el IP source está en 100.64.0.0/10

### CÓDIGO DE REFERENCIA - Endpoint IA
```python
# backend/routers/ai_analysis.py
from fastapi import APIRouter, Depends
from services.ai_engine import AIEngine
from models.schemas import AIQuery, AIResponse

router = APIRouter(prefix="/ai", tags=["AI"])
ai_engine = AIEngine()

@router.post("/chat")
async def ai_chat(query: AIQuery, user=Depends(get_current_user)):
    """
    Chat con contexto del sistema.
    Soporta tool-calling para:
    - analyze_logs(service, lines)
    - find_files(pattern, path)
    - system_status()
    - execute_command(cmd, safe_mode=True)
    """
    context = await build_context(query.context_type)
    response = await ai_engine.chat(
        message=query.message,
        context=context,
        model=query.model or "llama3.2:latest"
    )
    return AIResponse(response=response, actions=response.actions)

async def build_context(type: str):
    if type == "logs":
        return {"logs": await get_recent_logs(lines=100)}
    elif type == "system":
        return {"metrics": await get_current_metrics()}
    elif type == "files":
        return {"cwd": query.cwd, "files": await list_files(query.cwd)}
    return {}
```

### INTEGRACIÓN ESPECÍFICA OLLAMA
```python
# backend/services/ai_engine.py
import httpx

class AIEngine:
    def __init__(self):
        self.ollama_url = "http://localhost:11434"
        self.default_model = "llama3.2:latest"
    
    async def chat(self, message: str, context: dict = None, model: str = None):
        system_prompt = self._build_system_prompt(context)
        
        payload = {
            "model": model or self.default_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            "stream": False,
            "tools": self._get_available_tools()
        }
        
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.ollama_url}/api/chat",
                json=payload,
                timeout=60.0
            )
            return resp.json()
    
    def _build_system_prompt(self, context):
        base = """Eres un asistente de administración de sistemas macOS.
        Tienes acceso a métricas, logs, archivos y terminal.
        Responde concisamente con comandos ejecutables cuando sea relevante."""
        
        if context.get("metrics"):
            base += f"\nEstado actual: {context['metrics']}"
        if context.get("logs"):
            base += f"\nLogs recientes disponibles para análisis."
        return base
```

### EXPECTATIVAS DE RESULTADO

Al ejecutar este prompt, OpenClaw debería producir:

1. **Backend funcional** en ~/mission-control/backend/
2. **Frontend funcional** en ~/mission-control/frontend/
3. **Script setup.sh** que instala dependencias automáticamente
4. **Sistema funcionando en** http://localhost:8080 tras ejecución
5. **Integración con Ollama** lista para usar (detectar modelo disponible)
6. **Tailscale verification** implementado

### CRITERIOS DE ÉXITO
- [ ] Puedo ver métricas en tiempo real en el dashboard
- [ ] Puedo navegar archivos y editar textos
- [ ] Puedo abrir terminal web y ejecutar comandos
- [ ] Puedo preguntar a la IA sobre logs del sistema
- [ ] Solo puedo acceder desde IP Tailscale autorizada
- [ ] Auth requiere usuario/contraseña macOS válida

---

## INSTRUCCIÓN FINAL PARA OPENCLAW

"Implementa el sistema Mission Control completo siguiendo estas especificaciones.

ESTE SISTEMA ES EL CENTRO DE MANDO ÚNICO: Debe poder controlar TODO desde una sola interfaz web:
- Docker Desktop: containers, imágenes, volúmenes, redes, logs en tiempo real
- Ollama: listar modelos, pull nuevos, eliminar, cambiar modelo activo, ver uso VRAM
- LM Studio: conectar al servidor local (puerto 1234), cambiar modelo cargado
- OpenClaw/Claude Code: terminal dedicado para ejecutar claude en el workspace actual
- Servicios del sistema: brew services, launchctl (start/stop/restart)
- Métricas: CPU, RAM, disco, red de TODO el sistema incluyendo estos servicios

Prioriza:
1. Control total de servicios (Docker, Ollama, LM Studio, OpenClaw)
2. Seguridad (validación inputs, paths restringidos, Tailscale ACLs)
3. Funcionalidad core (métricas en tiempo real, archivos, terminal general)
4. Integración IA (chat con contexto de todos los servicios)
5. UI/UX profesional (Tailwind, responsive, dark mode)

REQUISITOS ESPECÍFICOS SERVICIOS:
- Docker: Usar docker CLI vía subprocess o docker-py. Listar/start/stop containers. Ver logs con tail -f.
- Ollama: Usar API REST en localhost:11434. Endpoints: /api/tags (listar), /api/pull, /api/delete, /api/generate
- LM Studio: API OpenAI-compatible en localhost:1234/v1. GET /models para ver estado.
- OpenClaw: Terminal con workspace pre-configurado, historial de comandos claude persistente.

Detecta automáticamente qué modelo de Ollama está disponible y configúralo.
Verifica que estamos en macOS y adapta paths y comandos acorde.

Al terminar, proporciona:
- Resumen de archivos creados
- Comandos para iniciar el sistema
- URLs de acceso a cada servicio integrado
- Guía rápida de uso del ServiceHub"
