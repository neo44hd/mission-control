# 🔧 Configuración de APIs y Modelos para SynK-IA

## Estado Actual

```
✅ OpenClaw: http://localhost:18789 (activo)
✅ Ollama: http://localhost:11434 (activo)
   - qwen3.5:latest (modelo principal)
   - qwen2.5-coder:14b (coding)
   - codegemma:7b (clasificación)
   - +8 modelos adicionales disponibles

❌ APIs Externas: No configuradas
❌ Modelos Cloud: No configuradas
```

---

## 1. OpenClaw - Gateway de IA

### ¿Qué es?
OpenClaw es un gateway HTTP que proxea requests a diferentes modelos y APIs. Se ejecuta en `localhost:18789`.

### Token Configurado
```
OPENCLAW_TOKEN=10bd712faff32d870d73a1bcd6c47a18ce563bfa63b01f43
```

### Endpoints Disponibles
- `GET /health` → Estado del gateway
- WebSocket `/ws/openclaw` → Chat interactivo (usa Ollama qwen3.5)

---

## 2. Modelos Disponibles Locales (Ollama)

Tu servidor Ollama tiene estos modelos:
```
✅ phi4-mini:latest (2.5B - ultraligero)
✅ gemma4:e4b
✅ llama3.2-vision:11b (visión)
✅ glm-ocr:latest (OCR)
✅ phi4:14b
✅ deepseek-r1:14b (razonamiento)
✅ qwen2.5-coder:14b (programación)
✅ gemma4:26b
✅ codegemma:7b
✅ functiongemma:latest
✅ qwen3.5:latest (ACTUAL - general)
```

---

## 3. APIs Externas Necesarias

Para ampliar capacidades, necesitas configurar APIs de estos proveedores:

### A. Claude (Anthropic)
**Para**: Análisis avanzado, reasoning, documentos complejos

```bash
# 1. Obtener API key en https://console.anthropic.com
# 2. Agregar al .env:
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
CLAUDE_MODEL=claude-opus-4-1  # o claude-sonnet-4-20250514

# 3. Usar en código:
const { Anthropic } = require("@anthropic-ai/sdk");
const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });
```

### B. OpenAI (GPT-4 / GPT-4o)
**Para**: Modelos más potentes, vision, embeddings

```bash
# 1. Obtener API key en https://platform.openai.com/api-keys
# 2. Agregar al .env:
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
OPENAI_MODEL=gpt-4o  # o gpt-4-turbo

# 3. Usar en código:
const OpenAI = require("openai");
const client = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
```

### C. Otros Proveedores
- **Groq** (modelo Mixtral rápido): https://console.groq.com
- **Together AI**: https://www.together.ai/
- **Replicate**: https://replicate.com/ (para modelos especializados)

---

## 4. Configuración Recomendada

### Para Clasificación de Documentos
```env
# Local (rápido, sin costo):
CLASSIFY_MODEL=ollama/codegemma:7b

# Cloud (más preciso):
CLASSIFY_MODEL=openai/gpt-4o-mini
```

### Para Chat General
```env
# Local:
CHAT_MODEL=ollama/qwen3.5:latest

# Cloud (mejor):
CHAT_MODEL=anthropic/claude-opus-4-1
```

### Para Coding
```env
# Local:
CODE_MODEL=ollama/qwen2.5-coder:14b

# Cloud:
CODE_MODEL=openai/gpt-4-turbo
```

### Para Visión/OCR
```env
# Local:
VISION_MODEL=ollama/llama3.2-vision:11b

# Cloud:
VISION_MODEL=openai/gpt-4o
```

---

## 5. Implementación en Código

### Ejemplo: Fallback Chain (Local → Cloud)

```javascript
async function classifyDocument(text) {
  try {
    // Intenta local primero (rápido, gratis)
    return await ollama.generate({
      model: 'codegemma:7b',
      prompt: `Clasifica: ${text}`
    });
  } catch (err) {
    console.warn('Ollama fallió, usando Claude...');
    // Fallback a cloud si falla
    const message = await anthropic.messages.create({
      model: 'claude-opus-4-1',
      max_tokens: 512,
      messages: [{ role: 'user', content: `Clasifica: ${text}` }]
    });
    return message.content[0].text;
  }
}
```

---

## 6. Próximos Pasos

### 1. Obtener API Keys
- [ ] Crear cuenta en https://console.anthropic.com (Claude)
- [ ] Crear cuenta en https://platform.openai.com (GPT-4)
- [ ] (Opcional) https://console.groq.com (Mixtral)

### 2. Agregar al `.env`
```bash
# server/.env
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-proj-...
GROQ_API_KEY=gsk-...
```

### 3. Implementar en Servicios
- [ ] `server/routes/ai.js` - Agregar soporte para APIs externas
- [ ] `server/routes/claude-proxy.js` - Actualizar para múltiples backends
- [ ] `server/agents/` - Usar mejor modelo según tarea

### 4. Configurar Fallbacks
- [ ] Prioridad: Local Ollama → OpenAI → Anthropic
- [ ] Timeouts y reintentos automáticos
- [ ] Logging de qué modelo se usó

---

## 7. Testing

```bash
# Verificar Ollama
curl http://localhost:11434/api/tags | python3 -m json.tool

# Verificar OpenClaw
curl http://localhost:18789/health

# Test con Claude (una vez configurado)
curl -X POST https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "content-type: application/json" \
  -d '{"model":"claude-opus-4-1","max_tokens":100,"messages":[{"role":"user","content":"Hola"}]}'
```

---

## 📊 Matriz de Capacidades

| Tarea | Local (Ollama) | OpenAI | Anthropic | Groq |
|-------|---|---|---|---|
| Chat General | qwen3.5 ✅ | GPT-4o | Opus ✅✅ | Mixtral |
| Coding | qwen2.5-coder ✅ | GPT-4 | Sonnet | Mixtral |
| Clasificación | codegemma ✅ | GPT-4o-mini | Haiku | Mixtral |
| Visión | llama3.2-vision ✅ | GPT-4o ✅✅ | N/A | N/A |
| Reasoning | deepseek-r1 ⚡ | o1 | Opus ✅✅ | N/A |
| Velocidad | ⚡⚡ (10-100ms) | ⚡ (500ms) | 🔄 (1s) | ⚡⚡⚡ |
| Costo | 💰 Gratis | 💵 | 💵 | 💵 |

---

## 🚀 Recomendación Inmediata

1. **Para testing rápido**: Usa modelos locales (Ollama)
2. **Para producción**: Configura Claude + OpenAI como fallback
3. **Para velocidad**: Agrega Groq para tareas sencillas

¿Quieres que configure alguna API específica?
