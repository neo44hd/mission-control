# 🚀 Warp's Oz Platform - Agente IA en tu Terminal

## ✅ Status

**Warp:** Instalado en `/Applications/Warp.app`
**Oz:** Plataforma nativa para agentes IA en Warp

## 🎯 ¿Qué es Oz?

Oz es la plataforma de Warp para ejecutar agentes de IA directamente en tu terminal. Es como tener un asistente inteligente integrado en tu flujo de trabajo.

## 🚀 Cómo Empezar

### 1. Abre Warp
```bash
open -a Warp
```

### 2. Acceder a Oz
Dentro de Warp, tienes varias formas:

#### Opción A: Comando rápido (/)
- Presiona `/` en la terminal
- Escribe tu pregunta o comando
- Oz te responderá

#### Opción B: Comando explícito
```bash
# Ver versión de Oz
oz version

# Ejecutar una pregunta
oz run default --message "¿Cuál es la hora actual?"

# Ver agentes disponibles
oz agents list
```

#### Opción C: Interfaz de Warp
- Usa el menú de Warp
- Busca "Oz" o "Agent"
- Activa desde la interfaz

## 📋 Comandos Principales

```bash
# Ver status de Oz
oz status

# Listar agentes disponibles
oz agents list

# Crear un nuevo agente
oz agents create --name mi-agente

# Ejecutar agente
oz run mi-agente --message "tu pregunta"

# Ver logs
oz logs

# Ayuda
oz help
```

## 🧠 Usar Oz con tus Modelos Locales

Oz puede conectarse a tus modelos de Ollama. Ejemplos:

```bash
# Pregunta simple
oz run default --message "¿Cuáles son los 3 modelos disponibles?"

# Usar Ollama
oz run default --provider ollama --message "Explica qué es un LLM"

# Con más contexto
oz run default --message "Analiza el directorio actual y sugiere mejoras"
```

## 🎮 Casos de Uso Prácticos

### 1. Debugging Rápido
```bash
# En tu terminal de Warp
/explain this error message
# Oz te explicará el error
```

### 2. Refactoring de Código
```bash
# Selecciona código en Warp y pregunta:
/refactor this function to be more efficient
```

### 3. Documentación Auto
```bash
/generate documentation for this code
```

### 4. Ejecución de Comandos
```bash
/what command creates a new Docker container?
# Oz sugiere el comando y puedes ejecutarlo directamente
```

## ⚙️ Configuración

### Conectar a Ollama (Local)

Si quieres que Oz use tus modelos de Ollama:

1. Abre Warp Preferences (Cmd+,)
2. Busca "Oz" o "Agent"
3. Configura:
   ```
   Provider: Ollama
   URL: http://localhost:11434
   Model: mistral-small (o el que prefieras)
   ```

### Variables de Entorno
```bash
# En ~/.zprofile o ~/.bashrc
export OLLAMA_HOST=0.0.0.0:11434
export OZ_PROVIDER=ollama
export OZ_MODEL=mistral-small
```

## 🔄 Diferencias: Open WebUI vs Oz

| Aspecto | Open WebUI | Oz (Warp) |
|---------|-----------|-----------|
| Acceso | Navegador (http://localhost:3000) | Terminal integrada |
| Contexto | Sin contexto del terminal | Acceso completo al terminal |
| Integración | Separado | Nativo en Warp |
| Uso | Chat tradicional | Comandos rápidos (/) |
| Ejecución | Manual | Puede ejecutar comandos |

## 💡 Tips & Tricks

### Atajo Rápido
En Warp, presiona `/` en cualquier momento para activar Oz sin escribir comandos.

### Historial
Warp mantiene historial de todas tus interacciones con Oz.

### Compartir Respuestas
Las respuestas de Oz se pueden copiar y compartir directamente.

### Combinar con Herramientas
Oz puede ver el output de tus comandos y ayudarte:
```bash
ls -la
# Luego
/explain what these files are
```

## 🔗 Integración con tu Stack Actual

```
Terminal Warp
    ↓
    Oz (Agente IA) ←→ Ollama (Modelos locales)
    ↓
Resultado (explicaciones, comandos, código)
```

**Ya tienes configurado:**
- ✅ Ollama en 0.0.0.0:11434
- ✅ 3 Modelos listos
- ✅ Warp instalado
- ✅ Oz disponible

**Solo necesitas:** Abrirlo y usarlo

## 🚀 Primer Uso

1. Abre Warp:
   ```bash
   open -a Warp
   ```

2. Una vez dentro, presiona `/`

3. Escribe algo como:
   ```
   ¿Cuál es el mejor modelo para análisis de textos?
   ```

4. Oz te responderá

5. Presiona Enter para ejecutar sugerencias

## 📚 Documentación Oficial

- **Warp Docs:** https://docs.warp.dev
- **Oz Docs:** https://docs.warp.dev/features/ai

## 🆘 Troubleshooting

### Oz no responde
```bash
# Reiniciar Warp
pkill -f "Warp"
sleep 2
open -a Warp
```

### Quiero cambiar el modelo
```bash
# En Warp settings, busca Oz/Agent
# Cambia el modelo de Ollama
```

### Verificar que Ollama está activo
```bash
curl http://localhost:11434/api/tags | jq '.models[].name'
```

## ✨ Próximos Pasos

1. **Abre Warp**: `open -a Warp`
2. **Prueba Oz**: Presiona `/` y escribe una pregunta
3. **Explora**: Usa Oz para:
   - Preguntas sobre código
   - Debugging
   - Documentación
   - Ideas de comandos

## 📝 Notas

- Oz usa tus modelos de Ollama locales (no necesita internet)
- Las respuestas aparecen directamente en tu terminal
- Todo es privado (corre localmente)
- Puedes usar mientras trabajas sin cambiar de ventana

---

**Instalación:** Completa
**Configuración:** Lista
**Status:** ✅ Listo para usar

¡Abre Warp y presiona `/` para empezar! 🚀
