# 🎯 Dashboard Rápido - Acceso Inmediato

## ✅ Status Verificado (Ahora Mismo)

```
✅ OLLAMA          → 3 modelos activos
✅ OPEN WEBUI      → http://localhost:3000
✅ OPENCLAW        → http://localhost:18789  
✅ WARP + OZ       → /Applications/Warp.app
```

---

## 🚀 Abre Ahora (Copy & Paste)

### Opción 1: Terminal Rápido (Warp + Oz)
```bash
open -a Warp
# Luego presiona / en la terminal
```

### Opción 2: Chat Web (Open WebUI)
```bash
open http://localhost:3000
```

### Opción 3: Acceso Remoto (Tailscale)
```bash
# Tu IP: 100.75.95.93
open http://100.75.95.93:3000     # Open WebUI
open http://100.75.95.93:18789    # OpenClaw
```

---

## 📋 Atajos Principales

| Herramienta | Comando/URL | Caso de Uso |
|------------|-----------|-----------|
| **Warp Oz** | `open -a Warp` + presiona `/` | ⚡ Rápido |
| **Open WebUI** | `open http://localhost:3000` | 📚 Análisis profundo |
| **OpenClaw** | `open http://localhost:18789` | 🤖 Automatización |
| **Ollama** | `curl http://localhost:11434/api/tags` | 🔧 Verificar |

---

## 💬 Ejemplos Rápidos (Copy & Paste)

### En Warp (presiona / y escribe):
```
/explain this error
/refactor this function  
/generate documentation
/optimize this code
/find bugs in this
```

### En Open WebUI:
```
Pega código → Pregunta → Enter
```

---

## 🔧 Comandos Útiles (Una Línea)

```bash
# Verificar Ollama
curl http://localhost:11434/api/tags | jq '.models[].name'

# Listar modelos
ollama list

# Reiniciar Ollama
brew services restart ollama

# Ver puertos activos
lsof -i :11434 -i :3000 -i :18789

# Abrir todo de una vez
open -a Warp & open http://localhost:3000
```

---

## 📍 Direcciones Clave

```
Localhost:
- Open WebUI        → http://localhost:3000
- OpenClaw          → http://localhost:18789
- Ollama API        → http://localhost:11434

Remoto (Tailscale):
- IP: 100.75.95.93
- Open WebUI        → http://100.75.95.93:3000
- OpenClaw          → http://100.75.95.93:18789
- Ollama API        → http://100.75.95.93:11434
```

---

## 🎓 Decisión Rápida: ¿Qué Usar?

| Necesitas... | Usa |
|-----------|-----|
| Respuesta en <5 segundos | **Warp Oz** (/) |
| Análisis profundo | **Open WebUI** |
| Automatizar tareas | **OpenClaw** |
| Mientras trabajas en terminal | **Warp Oz** (/) |
| Ver historial | **Open WebUI** |
| Acceso remoto | **Tailscale** + Open WebUI |

---

## 🆘 Si Algo Falla

```bash
# Oz no responde
pkill -f Warp; sleep 2; open -a Warp

# No hay modelos en Open WebUI
docker restart open-webui

# Ollama no responde
brew services restart ollama

# Verificar todo
curl http://localhost:11434/api/tags
curl http://localhost:3000 -I
curl http://localhost:18789 -I
```

---

## 📚 Documentación Disponible

| Archivo | Propósito |
|---------|-----------|
| **GUIA_WARP_OZ.md** | Cómo usar Warp y Oz |
| **STACK_INTEGRACION_COMPLETA.md** | Guía completa de todo |
| **CREDENCIALES_Y_REFERENCIAS.md** | Tokens, URLs, puertos |
| **openclaw-services.html** | Panel HTML interactivo |

---

## 🚀 Primeros 5 Minutos

1. **Abre Warp:**
   ```bash
   open -a Warp
   ```

2. **Prueba Oz:**
   - Presiona `/`
   - Escribe: `what is machine learning?`
   - Presiona Enter

3. **Abre Open WebUI:**
   ```bash
   open http://localhost:3000
   ```

4. **Selecciona un modelo y chatea**

5. **Done! ¡Tienes IA profesional funcionando!**

---

## ⚙️ Configuración Extra (Opcional)

### Cambiar Modelo en Oz
```bash
# En Warp Preferences (Cmd+,)
# Busca: Oz / Agent
# Cambia Model: mistral-small → gemma3:27b
```

### Descargar Más Modelos
```bash
ollama pull llama2
ollama pull neural-chat
ollama pull openchat
```

### Acceso Remoto Full (Caddy)
```bash
# Ya configurado con Tailscale
# Para HTTPS: espera a siguiente fase
```

---

## 💡 Pro Tips

1. **Combina herramientas:** Oz para pensar rápido, Open WebUI para profundizar
2. **Guarda en Open WebUI:** Mantiene historial y contexto
3. **Cambia modelos:** Cada uno excele en algo diferente
4. **Usa Oz en desarrollo:** Debugging sin dejar la terminal
5. **Comparte desde Open WebUI:** Export de conversaciones

---

## 📊 Stack Overview

```
┌────────────────────────────────────────┐
│  TÚ                                    │
├────────────────────────────────────────┤
│  Warp Terminal                         │
│  ├─ Oz (/command) ← Rápido             │
│  └─ Comandos normales                  │
│                                        │
│  Navegador Web                         │
│  ├─ Open WebUI ← Profundo              │
│  └─ OpenClaw ← Automatización          │
├────────────────────────────────────────┤
│  OLLAMA (3 Modelos)                    │
│  ├─ mistral-small (14GB)               │
│  ├─ gemma3:27b (17GB)                  │
│  └─ qwen3:32b (20GB)                   │
└────────────────────────────────────────┘
```

---

## 🎯 Misión: Entiende Cuál Usar

| Momento | Herramienta | Atajo |
|---------|-----------|-------|
| Debugging | Warp Oz | `/` |
| Análisis | Open WebUI | Cmd+L (abrir) |
| Cansado | OpenClaw | `http://localhost:18789` |
| Remoto | Tailscale | `100.75.95.93` |

---

## 🔐 Seguridad

- ✅ Todo corre **localmente** (tu máquina)
- ✅ **Sin Internet** requerido
- ✅ **Modelos privados** (no suben a la nube)
- ✅ **Tailscale encriptado** para acceso remoto
- ✅ Gateway token: `aca30e113a9d745ec...` (guardado localmente)

---

## 📞 Soporte Rápido

```bash
# Verificar todo funciona
curl http://localhost:11434/api/tags && \
curl http://localhost:3000 -I && \
curl http://localhost:18789 -I && \
echo "✅ TODO OK"

# Si falla algo
ps aux | grep -E "ollama|open-webui|openclaw"
```

---

## 🎬 Próximos Pasos (Orden Recomendado)

- [ ] **Hoy:** Abre Warp y prueba `/` (5 min)
- [ ] **Hoy:** Explora Open WebUI (10 min)
- [ ] **Mañana:** Crea tu primer script con Oz
- [ ] **Semana:** Configura OpenClaw para automatización
- [ ] **Mensual:** Experimenta con nuevos modelos

---

## 🌟 TL;DR (Demasiado Largo; No Leí)

```bash
# Rápido:
open -a Warp; # presiona / y pregunta

# Serio:
open http://localhost:3000

# Verificar:
curl http://localhost:11434/api/tags
```

**That's it. Tienes IA profesional funcionando en tu Mac. Usa Warp para rápido, Open WebUI para serio. Done.** 🚀

---

**Status:** ✅ 100% Funcional
**Modelos:** 3 activos
**Herramientas:** 4 integradas
**Tiempo total de aprendizaje:** <10 minutos

¡A trabajar! 💪
