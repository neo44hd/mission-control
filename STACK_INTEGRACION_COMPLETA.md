# 🎯 Stack IA Integrado - Guía Completa de Uso

## 📊 Tu Setup Actual

```
┌─────────────────────────────────────────────────────────────┐
│                    TU ECOSISTEMA IA                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. OLLAMA (Motor de Modelos)                               │
│     └─ Localhost: 11434                                      │
│     └─ Modelos: gemma3:27b, qwen3:32b, mistral-small        │
│     └─ Escuchando en: 0.0.0.0 (red local + Docker)          │
│                                                              │
│  2. OPEN WEBUI (Interfaz Web)                               │
│     └─ Puerto: 3000 (Docker)                                 │
│     └─ URL: http://localhost:3000                           │
│     └─ Conectado a: Ollama 192.168.0.32:11434               │
│                                                              │
│  3. OPENCLAW (Agente Avanzado)                              │
│     └─ Puerto: 18789 (Gateway)                              │
│     └─ Control UI: http://localhost:8000 (opcional)         │
│     └─ Acceso Remoto: Tailscale                             │
│                                                              │
│  4. WARP + OZ (Terminal IA)                                 │
│     └─ Instalado: /Applications/Warp.app                    │
│     └─ Agente: Oz (presiona / para activar)                 │
│     └─ Integración: Con Ollama local                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 Flujos de Trabajo Recomendados

### Flujo 1: Chat Web (Rápido & Visual)
**Caso de uso:** Conversaciones largas, análisis de documentos

```
1. Abre navegador → http://localhost:3000
2. Carga un documento (si necesitas contexto)
3. Selecciona modelo (mistral-small, gemma3:27b, qwen3:32b)
4. Escribe tu pregunta
5. Lee respuesta
```

**Ventajas:**
- ✅ Interfaz visual limpia
- ✅ Historial de conversaciones
- ✅ Mejor para documentos largos
- ✅ Puedes cambiar modelos fácilmente

### Flujo 2: Terminal Rápida (Commandos & Debugging)
**Caso de uso:** Preguntas rápidas mientras trabajas en terminal

```
1. En Warp, presiona /
2. Escribe tu pregunta
3. Oz responde en 2-3 segundos
4. Vuelves al trabajo
```

**Ventajas:**
- ✅ Sin cambiar de ventana
- ✅ Contexto del terminal disponible
- ✅ Respuestas rápidas
- ✅ Ideal para debugging

### Flujo 3: Agente Automático (OpenClaw)
**Caso de uso:** Automatización de tareas complejas

```
1. OpenClaw ejecuta comandos automáticos
2. Integración con sistemas
3. Acceso remoto vía Tailscale
4. Gateway escucha en puerto 18789
```

**Ventajas:**
- ✅ Automatización completa
- ✅ Acceso remoto seguro
- ✅ Integración profunda
- ✅ Escalable a múltiples máquinas

---

## 🚀 Casos de Uso Prácticos

### Caso 1: Entender un Error de Código

```bash
# En terminal (ejecuta comando que falla)
python script.py
# Output: TypeError: unsupported operand type(s) for +: 'int' and 'str'

# Presiona / en Warp
/explain this error: TypeError: unsupported operand type(s)

# Oz responde inmediatamente:
# "Estás intentando sumar un número y un string. 
#  En Python necesitas convertir: str(numero) + string"

# Arreglas el código y listo
```

### Caso 2: Análisis de Documento Largo

```
1. Abre Open WebUI: http://localhost:3000
2. Carga tu documento (PDF, TXT, etc.)
3. Pregunta: "Resumen ejecutivo de este documento"
4. Selecciona gemma3:27b (mejor para análisis)
5. Recibe respuesta detallada
```

### Caso 3: Refactoring de Código

```bash
# Opción A: Desde terminal (Oz)
/refactor this function to be more efficient
# Oz sugiere cambios

# Opción B: Desde web (Open WebUI)
# 1. Copia tu función
# 2. Pega en Open WebUI
# 3. "Refactoriza este código"
# 4. Recibe versión mejorada
```

### Caso 4: Generar Documentación

```bash
# Terminal (rápido)
/generate documentation for this file

# O Web (más detallado)
# 1. http://localhost:3000
# 2. Pega código
# 3. "Genera documentación completa"
# 4. Copia resultado
```

### Caso 5: Análisis de Logs

```bash
# Terminal
tail -f app.log | head -20
# Luego
/analyze these logs and find issues

# Oz identifica problemas y sugiere soluciones
```

---

## 📊 Comparativa: Cuándo Usar Cada Herramienta

| Caso de Uso | Oz (Warp) | Open WebUI | OpenClaw |
|------------|-----------|-----------|----------|
| Pregunta rápida | ✅ Perfecto | ⭐ Bueno | ❌ Overkill |
| Chat largo | ❌ No ideal | ✅ Perfecto | ⭐ Bueno |
| Análisis de docs | ❌ Limitado | ✅ Perfecto | ⭐ Bueno |
| Debug inmediato | ✅ Perfecto | ⭐ Bueno | ❌ Lento |
| Automatización | ❌ Sólo sugerencias | ❌ Manual | ✅ Perfecto |
| Acceso remoto | ❌ Sólo local | ⭐ Con Tailscale | ✅ Integrado |
| Sin dejar terminal | ✅ Perfecto | ❌ Cambias ventana | ❌ Cambias ventana |

**Recomendación:** Empieza con **Oz (Warp)** para lo rápido, **Open WebUI** para lo serio.

---

## 🔧 Verificar que Todo Funciona

### 1. Verificar Ollama
```bash
# ¿Ollama está corriendo?
curl http://localhost:11434/api/tags

# Output esperado:
# {"models":[{"name":"gemma3:27b"...},{"name":"qwen3:32b"...}...]}
```

### 2. Verificar Open WebUI
```bash
# ¿Open WebUI está corriendo?
curl http://localhost:3000 -I

# Output esperado:
# HTTP/1.1 200 OK
```

### 3. Verificar OpenClaw
```bash
# ¿OpenClaw está corriendo?
curl http://localhost:18789 -I

# Output esperado:
# HTTP/1.1 200 OK o 401 Unauthorized (esperado sin token)
```

### 4. Verificar Warp + Oz
```bash
# ¿Warp está instalado?
ls /Applications/Warp.app

# ¿Oz está disponible?
open -a Warp
# (Dentro de Warp, presiona / - debería funcionar)
```

---

## ⚡ Comandos Rápidos

### Terminal (Warp)
```bash
# Estos funcionan dentro de Warp al presionar /

/what is Python?
/explain this error
/refactor this function
/generate documentation
/find bugs in this code
/optimize this query
/translate this to Spanish
/create a test for this
```

### Web (Open WebUI - http://localhost:3000)
```
1. Clic en chat nuevo
2. Selecciona modelo
3. Escribe pregunta
4. Enter para enviar
5. Puedes adjuntar archivos (documentos, imágenes)
```

### Terminal (Comandos CLI)
```bash
# Verificar modelos disponibles
ollama list

# Reiniciar Ollama
brew services restart ollama

# Ver logs
tail -f ~/.local/share/ollama/logs

# Verificar puerto
lsof -i :11434
lsof -i :3000
lsof -i :18789
```

---

## 🎓 Ejemplos Paso a Paso

### Ejemplo 1: Debuggear un Script Python

**Escenario:** Tu script falla con un error y quieres arreglarlo rápido.

```bash
# 1. Ejecuta el script en Warp
python analizar_datos.py
# Error: KeyError: 'nombre'

# 2. Presiona /
# 3. Escribe:
/why am I getting KeyError: 'nombre' in Python dict?

# 4. Oz explica en 10 segundos:
# "KeyError ocurre cuando accedes una clave que no existe.
#  Solución: usa dict.get('nombre') en lugar de dict['nombre']"

# 5. Arreglas tu código en el editor
python analizar_datos.py
# ✅ Funciona!
```

### Ejemplo 2: Entender un Concepto Nuevo

**Escenario:** Quieres aprender sobre async/await

```bash
# 1. En Warp, presiona /
# 2. Escribe:
/explain async and await in Python

# 3. Oz responde con:
# "async/await permite código no-bloqueante...
#  Ejemplo: async def fetch(url):"

# 4. Inmediatamente puedes ver ejemplos prácticos
# 5. Continúas con tu trabajo
```

### Ejemplo 3: Optimizar una Query SQL

**Escenario:** Tu query de base de datos es lenta

```bash
# 1. En Open WebUI (http://localhost:3000):

# 2. Pegas tu query:
SELECT * FROM usuarios 
WHERE ciudad = 'Madrid' 
AND edad > 25 
ORDER BY nombre

# 3. Pregunta:
# "¿Cómo optimizar esta query? ¿Qué índices necesito?"

# 4. Gemma3 responde:
# "Crea índice en (ciudad, edad)
#  Usa EXPLAIN ANALYZE
#  Considera particionamiento si dataset es grande"

# 5. Implementas las sugerencias
```

---

## 🌐 Acceso Remoto (Tailscale)

### Desde Otra Red / Otro Mac
```bash
# 1. Tu Tailscale IP: 100.75.95.93

# Desde otra máquina en tu Tailscale:
# Open WebUI:
http://100.75.95.93:3000

# OpenClaw:
http://100.75.95.93:18789
```

### Acceso Seguro con Caddy
```bash
# Si configuraste Caddy:
https://tu-dominio.com/openclaw
https://tu-dominio.com/webui
```

---

## 📋 Checklist de Verificación

- [ ] Ollama corriendo (`curl http://localhost:11434/api/tags`)
- [ ] Open WebUI accesible (`http://localhost:3000`)
- [ ] Modelos visibles en Open WebUI
- [ ] Warp instalado (`ls /Applications/Warp.app`)
- [ ] Warp abierto y Oz funciona (presiona `/`)
- [ ] OpenClaw corriendo (`curl http://localhost:18789`)
- [ ] Tailscale conectado (si necesitas acceso remoto)

---

## 🆘 Troubleshooting Rápido

### "Oz no responde en Warp"
```bash
# Reinicia Warp
pkill -f Warp
sleep 2
open -a Warp
```

### "No veo modelos en Open WebUI"
```bash
# Verifica conexión Ollama
curl http://localhost:11434/api/tags

# Reinicia Open WebUI
docker restart open-webui
```

### "Ollama no responde"
```bash
# Reinicia
brew services restart ollama

# Verifica puerto
lsof -i :11434
```

### "Warp no está en Aplicaciones"
```bash
# Busca en Spotlight: Cmd + Space, escribe "Warp"
# O instala desde: https://www.warp.dev/download
```

---

## 📈 Próximos Pasos

1. **Hoy:** Abre Warp y prueba Oz (presiona `/`)
2. **Mañana:** Explora Open WebUI con documentos
3. **Semana:** Automatiza tareas con OpenClaw
4. **Futuro:** Integra con tu flujo de trabajo diario

---

## 📚 Documentación Rápida

| Herramienta | URL |
|------------|-----|
| Warp Docs | https://docs.warp.dev |
| Ollama Docs | https://ollama.ai |
| Open WebUI | http://localhost:3000 |
| OpenClaw Docs | https://openclaw.ai |

---

## 💡 Tips Finales

1. **Usa el atajo correcto:** Oz para rápido, Open WebUI para serio
2. **Guarda respuestas útiles:** Open WebUI mantiene historial
3. **Prueba modelos diferentes:** Cada uno excele en algo
4. **Combina herramientas:** Oz → Open WebUI para profundizar
5. **Actualiza modelos:** `ollama pull nombre:latest`

---

**Status:** ✅ Stack completamente funcional
**Tiempo de aprendizaje:** 5-10 minutos para empezar
**Beneficio:** IA profesional sin límites de uso

¡Ahora sí, a trabajar! 🚀
