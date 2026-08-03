# Mission Control - SynK-IA Ecosystem Orchestrator

## 🎯 Acceso Rápido

### Desde la VPN (Tailscale)
```
https://sinkpro.tail126c66.ts.net
```

### Desde Internet (Cloudflare)
```
https://sinkialabs.com
```

### Local (Desarrollo)
```
http://127.0.0.1:3002
```

**Credenciales:** `admin` / `sinkia2026`

---

## 📊 Dashboard Principal

### 1. Health Dashboard (Estado)
Monitorea en **tiempo real** el estado de los 6 servicios principales:
- 🎛️ **Mission Control** (3002) - Este dashboard
- 🚀 **SynK-IA App** (3001) - Aplicación principal
- 📊 **Algorithm** (5183) - Procesamiento de datos
- 🛒 **Commerce** (4400) - Tienda e-commerce
- 🧠 **sinkMAIND** - Base de conocimiento
- 🔧 **OpenClaw** (7999) - Agente IA

**Indicadores:**
- 🟢 Verde = Online
- 🔴 Rojo = Offline
- Haz clic en "Actualizar Estado" para refresh manual

---

## 🚀 Servicios Principales

### SynK-IA App
**Aplicación principal de gestión**
- 🌐 Acceso Cloud: https://app.sinkialabs.com
- 🏠 Acceso Local: http://localhost:3001
- **Acciones:**
  - 🔄 **Reiniciar** - Reinicia la app si falla
  - 📋 **Logs** - Ver registro de errores

### sinkMAIND (Memoria)
**Sistema de memoria y contexto persistente**

**Características:**
- 📊 Estadísticas en vivo (documentos, embeddings)
- 🔍 Búsqueda avanzada de memoria
- 🔄 Sincronización manual
- 💾 Backup automático
- 🎯 Filtros: Conversaciones, Documentos, Agentes, Código

**Cómo usar:**
1. Escribe en el cuadro de búsqueda
2. Selecciona qué tipos buscar
3. Haz clic en "Buscar"
4. Los resultados aparecen con relevancia

### OpenClaw (Agente IA Multimodal)
**Asistente IA inteligente con terminal integrada**

**Modelos disponibles:**
- 🤖 Auto (Local - Recomendado)
- 🧠 Qwen 3.5
- ⚡ Phi-4 Mini
- 💎 Gemma 4
- 👁️ Llama 3.2 Vision
- ☁️ Claude Sonnet (Cloud)

**Modos:**
1. **💬 Chat** - Conversación normal
2. **🖥️ Terminal** - Ejecutar comandos
3. **💻 Código** - Análisis y edición de código

**Cómo usar:**
1. Selecciona el modelo que prefieres
2. Elige el modo (Chat/Terminal/Código)
3. Escribe tu pregunta o comando
4. Presiona Enter o haz clic en el botón

### OpenCloud (Búsqueda Web)
**Búsqueda integrada en internet**
1. Abre el panel
2. Escribe tu pregunta
3. Haz clic en "🔎 Buscar"
4. Ver resultados con enlaces

### Aider (Code Assistant)
**Asistente de programación inteligente**
1. Pega código en el editor
2. Describe los cambios que quieres
3. Haz clic en "✨ Aplicar Cambios"
4. El código se modifica automáticamente

**Modelos soportados:**
- 🤖 Auto (Local)
- 🔴 GPT-4o
- ☁️ Claude Sonnet
- 🧠 Qwen 3.5

### Claude Code
**Análisis avanzado de código**
1. Pega el código a analizar
2. Describe qué quieres analizar/refactorizar
3. Haz clic en "🔍 Analizar"
4. Recibe análisis detallado

**Modelos:**
- ☁️ Claude Sonnet 4.6 (Recomendado)
- 🎭 Claude Opus (Más potente)

### Commerce (Tienda)
**Sistema e-commerce TPV**
- 🌐 Cloud: https://commerce.sinkialabs.com
- 🏠 Local: http://localhost:4400
- Gestión de pedidos y productos

---

## 🚑 Botiquín de Emergencias

Scripts modulares para diagnosticar y reparar problemas. **Cada uno hace UNA sola cosa.**

### 01. Diagnóstico Completo 🏥
- **Qué hace:** Verifica todos los puertos y servicios
- **Tiempo:** ~5 segundos
- **No modifica:** Nada, solo comprueba
- **Cuándo usar:** Cuando algo "se siente raro"

### 02. Reiniciar Dashboard 🎛️
- **Qué hace:** Reinicia SOLO Mission Control (3002)
- **Tiempo:** ~5 segundos
- **No afecta:** SynK-IA App, Commerce, datos
- **Cuándo usar:** Mission Control no carga

### 03. Reiniciar SynK-IA 🚀
- **Qué hace:** Reinicia SynK-IA App y backend
- **Tiempo:** ~30-60 segundos (compila Docker)
- **No afecta:** Dashboard, Commerce, bases de datos
- **Cuándo usar:** La app no responde

### 04. Reiniciar Commerce 🛒
- **Qué hace:** Reinicia SOLO el TPV
- **Tiempo:** ~10-20 segundos
- **No afecta:** Dashboard, SynK-IA, datos
- **Cuándo usar:** La tienda no carga

### 05. Reparar Túneles 🌐
- **Qué hace:** Reconfigura Cloudflare + Tailscale
- **Tiempo:** ~5-10 segundos
- **No afecta:** Servicios locales
- **Cuándo usar:** No acceso desde móvil a sinkialabs.com

### 06. Backup Config 💾
- **Qué hace:** Copia de seguridad de configuraciones
- **Dónde:** ~/.config/synkia-backups/YYYYMMSS-HHMMSS/
- **Tiempo:** ~2 segundos
- **Cuándo usar:** Antes de cambios importantes

**Cómo usar cualquier script:**
1. Haz clic en la tarjeta del script
2. Lee la descripción detallada (hover)
3. Se abrirá un panel con la ejecución
4. Ver output en tiempo real
5. Cierra cuando termine

---

## 🔗 Infraestructura Completa

Acceso rápido a todos los servicios:

| Servicio | Puerto | Local | Cloud |
|----------|--------|-------|-------|
| Mission Control | 3002 | http://localhost:3002 | https://sinkialabs.com |
| SynK-IA App | 3001 | http://localhost:3001 | https://app.sinkialabs.com |
| SynK-IA Algorithm | 5183 | http://localhost:5183 | https://v3.sinkialabs.com |
| API Backend | 3000 | http://localhost:3000 | https://api-v3.sinkialabs.com |
| Commerce | 4400 | http://localhost:4400 | https://commerce.sinkialabs.com |
| n8n | 5678 | http://localhost:5678 | https://n8n.sinkialabs.com |
| OpenClaw | 7999 | http://localhost:7999 | https://claw.sinkialabs.com |
| SearXNG | 8888 | http://localhost:8888 | - |
| Qdrant | 6333 | http://localhost:6333 | - |
| Ollama | 11434 | http://localhost:11434 | - |

---

## ⚙️ Configuración

### Cambiar Modelos IA

Cada tarjeta expandible tiene un selector de modelos. Los cambios se guardan en el navegador.

**Modelos Locales (Gratis):**
- google/gemma-3-4b (Rápido, 4B parámetros)
- Qwen 3.5 (Potente, multilingüe)
- Phi-4 Mini (Eficiente)
- Llama 3.2 Vision (Con visión)

**Modelos Cloud (Pagos):**
- Claude Sonnet 4.6 (Recomendado)
- Claude Opus (Más potente)
- GPT-4o (OpenAI)

---

## 🎨 Características Avanzadas

### Paneles Expandibles
Haz clic en el título de cualquier tarjeta para expandir/contraer el panel.

### Terminal Integrada
En OpenClaw, modo Terminal:
- Ejecuta comandos del sistema
- Soporta bash, zsh, python, etc.
- Output en vivo

### Filtros de Búsqueda
En sinkMAIND:
- ☑️ Conversaciones
- ☑️ Documentos
- ☑️ Agentes
- ☐ Código

### Notificaciones
- Aparecen automáticamente en esquina inferior derecha
- Se cierran después de 3 segundos
- Verde = éxito, Rojo = error

---

## 🔐 Seguridad

### Autenticación
- Usuario: `admin`
- Contraseña: `sinkia2026` (cambiar en .env)
- Solo se requiere en acceso remoto

### Tailscale (VPN Privada)
- Acceso solo desde devices en la red Tailscale
- IP privada: 100.78.4.14
- Sin exposición a internet

### Cloudflare (Public con Auth)
- Dominio: sinkialabs.com
- Usa certificados SSL/TLS
- Tunnel autenticado

---

## 🚀 Gestión del Servicio

### Ver estado
```bash
pm2 list
pm2 status mission-control-dashboard
```

### Ver logs
```bash
pm2 logs mission-control-dashboard
```

### Reiniciar manualmente
```bash
pm2 restart mission-control-dashboard
```

### Detener
```bash
pm2 stop mission-control-dashboard
```

### Iniciar
```bash
pm2 start /Users/davidnows/mission-control/server.js --name mission-control-dashboard
```

---

## 📱 Acceso Móvil

**Desde iPhone/Android en Tailscale VPN:**
1. Abre Tailscale
2. Copia la IP de Mission Control
3. Accede a `http://IP:3002`
4. Introduce credenciales

**Desde internet público:**
1. Accede a https://sinkialabs.com
2. Introduce credenciales
3. Mismo dashboard funcional

---

## 🛠️ Troubleshooting

### "No se conecta a Mission Control"
1. Ejecuta: `curl http://127.0.0.1:3002`
2. Si no responde: `pm2 restart mission-control-dashboard`
3. Espera 5 segundos y reintenta

### "Tailscale no funciona"
1. Abre Tailscale en cliente
2. Verifica que esté conectado
3. Ejecuta script "05. Reparar Túneles"

### "Cloudflare no funciona"
```bash
pgrep cloudflared  # Ver si está corriendo
pm2 restart cloudflare-tunnel  # Si existe en PM2
```

### "Servicio X no responde"
1. Abre Botiquín → 01. Diagnóstico
2. Identifica el servicio problemático
3. Ejecuta el script de reinicio correspondiente

---

## 📞 Soporte

Para problemas específicos:
1. Ejecuta diagnóstico completo
2. Revisa logs del servicio
3. Consulta documentación del servicio específico

---

**Última actualización:** Mayo 2026  
**Versión:** 1.0  
**Estado:** ✅ Completo y Funcional
