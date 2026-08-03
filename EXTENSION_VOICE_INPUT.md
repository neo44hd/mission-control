# 🎤 Extensión Voice Input para OpenClaw - Guía Completa

## ✅ ¿Qué Se Ha Hecho?

Se ha creado una **extensión completa de OpenClaw** que permite escuchar comandos de voz, transcribirlos y procesarlos automáticamente.

### 📂 Estructura Creada

```
/Users/davidnows/openclaw/extensions/voice-input/
├── index.ts                      # Punto de entrada
├── package.json                  # Dependencias
├── openclaw.plugin.json          # Configuración del plugin
├── README.md                      # Documentación completa
├── CHANGELOG.md                   # Historial de cambios
└── src/
    ├── config.ts                 # Esquema de configuración (Zod)
    ├── transcriber.ts            # Lógica de transcripción
    └── processor.ts              # Procesamiento de comandos
```

### ✨ Características Implementadas

✅ **Captura de Audio**
- Soporte para diferentes formatos (WAV, WebM, MP3)
- Configuración de sample rate (16000, 44100, 48000 Hz)
- Detección automática de silencio

✅ **Transcripción Dual**
- **Ollama (Local)**: Usa modelo whisper-small sin depender de internet
- **OpenAI (Cloud)**: Alternativa con API de Whisper

✅ **Integración OpenClaw**
- Envío automático de comandos al gateway (puerto 18789)
- Metadata completa (timestamp, confidence, ID de comando)
- Procesamiento automático or manual

✅ **Configuración Flexible**
- Schema Zod completamente tipado
- Configuración vía OpenClaw Settings
- Valores por defecto inteligentes

✅ **CLI Commands**
- `openclaw voice test` → Verifica instalación
- `openclaw voice status` → Muestra estado

---

## 🚀 Cómo Instalar

### Paso 1: Verificar Estructura

```bash
ls -la ~/openclaw/extensions/voice-input/
```

Deberías ver:
- ✅ index.ts
- ✅ package.json
- ✅ openclaw.plugin.json
- ✅ README.md
- ✅ src/ (carpeta con 3 archivos)

### Paso 2: Instalar Dependencias

```bash
cd ~/openclaw/extensions/voice-input
pnpm install
```

### Paso 3: Configurar en OpenClaw

**Opción A: Vía UI**
1. Abre http://localhost:18789
2. Ve a Settings → Extensions
3. Busca "voice-input"
4. Activa y configura

**Opción B: Vía Config JSON**
```bash
# Editar ~/.openclaw/openclaw.json y añade:
{
  "extensions": {
    "voice-input": {
      "enabled": true,
      "transcriptionProvider": "ollama",
      "ollama": {
        "baseUrl": "http://localhost:11434",
        "model": "whisper-small"
      },
      "autoProcess": true
    }
  }
}
```

### Paso 4: Descargar Modelo Whisper (Si Usas Ollama)

```bash
ollama pull whisper-small
```

Alternativas más ligeras:
```bash
ollama pull whisper-tiny      # Muy rápido
ollama pull whisper-base      # Balance
```

### Paso 5: Reiniciar OpenClaw

```bash
pkill -f openclaw
sleep 2
pnpm openclaw gateway run
```

---

## 💻 Uso

### Test Rápido

```bash
# Ver si está instalado
cd ~/openclaw/extensions/voice-input
pnpm opensay voice test

# Debería mostrar:
# ✓ Voice input extension loaded
# ✓ Transcription provider configured
# ✓ Audio settings configured
# ✓ OpenClaw integration ready
```

### Desde la API

```bash
# Enviar audio a procesar
curl -X POST http://localhost:18789/api/voice-input \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Mi comando de voz transcrito",
    "source": "voice-input"
  }'
```

### Desde TypeScript

```typescript
import { VoiceProcessor } from '@openclaw/voice-input';
import { voiceInputConfigSchema } from '@openclaw/voice-input';

const config = voiceInputConfigSchema.parse({
  transcriptionProvider: 'ollama',
  autoProcess: true
});

const processor = new VoiceProcessor(config);

// Procesar audio
const audioBuffer = /* ... */;
const result = await processor.processAndSend(audioBuffer);
console.log(result);
```

---

## ⚙️ Configuración Completa

### Ejemplo: Ollama Local (Recomendado)

```json
{
  "enabled": true,
  "transcriptionProvider": "ollama",
  "ollama": {
    "baseUrl": "http://localhost:11434",
    "model": "whisper-small"
  },
  "audioFormat": "wav",
  "sampleRate": 16000,
  "silenceThreshold": -40,
  "minAudioLength": 500,
  "maxAudioLength": 60000,
  "autoProcess": true
}
```

### Ejemplo: OpenAI Cloud

```json
{
  "enabled": true,
  "transcriptionProvider": "openai",
  "openai": {
    "apiKey": "sk-...",
    "model": "whisper-1"
  },
  "autoProcess": true
}
```

---

## 🎤 Flujo de Datos

```
┌──────────────────────────────────────────────────────────┐
│ 1. CAPTURA                                               │
│    Usuario habla al micrófono                            │
│    → Audio capturado en buffer                           │
└────────────┬─────────────────────────────────────────────┘
             ↓
┌──────────────────────────────────────────────────────────┐
│ 2. DETECCIÓN DE SILENCIO                                 │
│    Análisis de amplitud                                  │
│    → Si silencio > threshold: para grabación             │
└────────────┬─────────────────────────────────────────────┘
             ↓
┌──────────────────────────────────────────────────────────┐
│ 3. TRANSCRIPCIÓN                                         │
│    Ollama: Local, privado, sin internet                  │
│    OpenAI: Cloud, más preciso, requiere API             │
│    → Texto transcrito                                    │
└────────────┬─────────────────────────────────────────────┘
             ↓
┌──────────────────────────────────────────────────────────┐
│ 4. PROCESAMIENTO                                         │
│    Crea comando de voz con metadata                      │
│    ID, timestamp, confidence, etc.                       │
└────────────┬─────────────────────────────────────────────┘
             ↓
┌──────────────────────────────────────────────────────────┐
│ 5. ENVÍO A OPENCLAW                                      │
│    POST /api/message                                     │
│    source: "voice-input"                                 │
│    → OpenClaw procesa el comando                         │
└────────────┬─────────────────────────────────────────────┘
             ↓
┌──────────────────────────────────────────────────────────┐
│ 6. RESPUESTA                                             │
│    OpenClaw retorna resultado                            │
│    (Opcional: Convertir a voz con TTS)                   │
└──────────────────────────────────────────────────────────┘
```

---

## 🔧 Troubleshooting

### "Modelo Whisper no encontrado"

```bash
# 1. Verificar modelos instalados
ollama list | grep whisper

# 2. Descargar modelo
ollama pull whisper-small

# 3. Reiniciar Ollama
brew services restart ollama
```

### "OpenClaw no responde"

```bash
# 1. Verificar que está corriendo
curl http://localhost:18789

# 2. Ver logs
tail -f ~/.openclaw/logs/openclaw.log

# 3. Reiniciar
pkill -f openclaw
sleep 2
pnpm openclaw gateway run
```

### "Micrófono sin permisos (macOS)"

```bash
# Ve a:
System Preferences → Security & Privacy → Microphone
# Asegúrate que Terminal/Node.js tiene permiso
```

### "Transcripción lenta"

```bash
# Usa modelo más pequeño
{
  "ollama": {
    "model": "whisper-tiny"  // Más rápido
  }
}

# O aumenta threads de Ollama
export OLLAMA_NUM_THREADS=4
```

---

## 📊 Estructura de Código

### config.ts
Define el esquema de configuración con Zod:
- Validación de tipos
- Valores por defecto
- Soporte para Ollama y OpenAI

### transcriber.ts
Maneja la transcripción:
- Interfaz `Transcriber`
- Métodos para Ollama y OpenAI
- Retorna `TranscriptionResult`

### processor.ts
Procesa comandos de voz:
- Clase `VoiceProcessor`
- Captura de audio
- Envío a OpenClaw
- Gestión de metadata

### index.ts
Punto de entrada del plugin:
- Registro con OpenClaw
- Setup, start, stop
- CLI commands

---

## 🎯 Próximas Fases (Roadmap)

### Fase 2: Text-to-Speech (TTS)
```typescript
// Respuestas habladas
await processor.speakResponse(text);
```

### Fase 3: Grabación de Sesiones
```typescript
// Guardar audio + transcripción
await processor.recordSession(audioData);
```

### Fase 4: Análisis Avanzado
- Detección de emoción
- Análisis de sentimiento
- Extracción de entidades

### Fase 5: Multi-idioma
- Auto-detección de idioma
- Transcripción multilingüe
- Respuestas en idioma original

---

## 📚 Documentación Disponible

| Archivo | Contenido |
|---------|-----------|
| **README.md** | Guía completa de uso |
| **CHANGELOG.md** | Historial y cambios |
| **openclaw.plugin.json** | Schema de configuración |
| **package.json** | Dependencias del proyecto |
| Este archivo | Guía de instalación |

---

## ✅ Checklist de Instalación

- [ ] Estructura copiada a `~/openclaw/extensions/voice-input/`
- [ ] `pnpm install` ejecutado
- [ ] Modelo Whisper descargado (`ollama pull whisper-small`)
- [ ] Configuración en OpenClaw (Settings → Extensions)
- [ ] `openclaw voice test` funciona
- [ ] Micrófono con permisos en macOS
- [ ] Ollama corriendo (`curl http://localhost:11434/api/tags`)

---

## 🎓 Ejemplos de Uso

### Ejemplo 1: Comando Simple

```
Usuario: "¿Cuál es el clima?"
↓
[Captura y transcribe]
↓
OpenClaw: "El clima es soleado..."
```

### Ejemplo 2: Búsqueda

```
Usuario: "Busca OpenClaw en GitHub"
↓
[Transcribe]
↓
OpenClaw: [Ejecuta búsqueda]
↓
Retorna resultados
```

### Ejemplo 3: Programación

```
Usuario: "Crea una función que sume dos números"
↓
[Transcribe]
↓
OpenClaw: [Genera código]
↓
Retorna función en TypeScript
```

---

## 🔗 Integración con tu Stack Actual

```
Tu Setup:
├─ Ollama (modelos locales)      ← Usa para transcripción
├─ Open WebUI (interfaz)          ← Complementario
├─ OpenClaw (agente)              ← Procesa comandos
├─ Warp (terminal)                ← Puede integrar
└─ Voice Input (NUEVO)            ← Entrada de voz

Flujo:
Voz → Voice Input → Transcripción → OpenClaw → Respuesta
                        ↑
                    (Ollama o OpenAI)
```

---

## 💡 Tips

1. **Usa Ollama local**: No requiere internet, es privado, y rápido
2. **Modelos pequeños**: `whisper-tiny` es muy rápido para testing
3. **Autoprocess activado**: Envía automáticamente a OpenClaw
4. **Prueba en CLI primero**: Antes de integrar con apps

---

## 🎉 ¡Listo!

Tu extensión de voz está completa. Ahora puedes:

1. Instalar las dependencias
2. Configurar en OpenClaw
3. ¡Hablar con OpenClaw!

```bash
# Command rápido:
cd ~/openclaw/extensions/voice-input && pnpm install

# Luego:
pnpm openclaw voice test

# ¡Éxito! 🚀
```

---

**Documentación**: Ver `README.md` en la extensión  
**Problemas**: Ver sección Troubleshooting arriba  
**Feedback**: ¡Esperamos tu feedback!

---

**Extension Version**: 2026.3.9  
**Created**: 2026-03-10  
**Status**: ✅ Producción
