# ✅ Solución: Modelos no visibles en Open WebUI

## ❌ Problema

Open WebUI no mostraba los modelos de Ollama aunque estaban descargados.

## 🔍 Causa Raíz

Open WebUI corre dentro de un contenedor Docker. Cuando usaba `localhost:11434`, en realidad estaba intentando conectar a `localhost` **dentro del contenedor**, no a tu Mac.

La solución fue usar la **IP local de tu máquina** en lugar de `localhost`.

## ✅ Solución Aplicada

Se reinició Open WebUI con la variable de entorno correcta:

```bash
docker run -d \
  --name open-webui \
  -p 3000:8080 \
  -e OLLAMA_BASE_URL="http://192.168.0.32:11434" \
  --restart unless-stopped \
  ghcr.io/open-webui/open-webui:latest
```

**Clave:** `OLLAMA_BASE_URL=http://192.168.0.32:11434` (IP local, no localhost)

## 📊 Configuración Final

```
🐳 Docker (Open WebUI en puerto 3000)
    ↓
    Conecta a → http://192.168.0.32:11434
    ↓
🦙 Ollama (en tu Mac, puerto 11434)
    ↓
📦 Modelos descargados (gemma3:27b, qwen3:32b, mistral-small)
```

## 🎯 Resultado

✅ Los modelos ahora son visibles en Open WebUI
✅ Puedes usar cualquier modelo para chatear
✅ Todo funciona en http://localhost:3000

## 🚀 Acceso

```bash
# Abrir Open WebUI
open http://localhost:3000

# Ver modelos disponibles
ollama list

# Verificar conectividad
curl http://192.168.0.32:11434/api/tags | jq '.models[].name'
```

## 🔧 Si necesitas cambiar la configuración

```bash
# Detener
docker stop open-webui
docker rm open-webui

# Obtener IP actual
ipconfig getifaddr en0

# Reiniciar con nueva IP
docker run -d \
  --name open-webui \
  -p 3000:8080 \
  -e OLLAMA_BASE_URL="http://TU_IP_AQUI:11434" \
  --restart unless-stopped \
  ghcr.io/open-webui/open-webui:latest
```

## 📝 Notas

- **IP local:** 192.168.0.32 (obtenida automáticamente)
- **Puerto Ollama:** 11434 (por defecto)
- **Puerto Open WebUI:** 3000 (mapeado a 8080 en Docker)
- **Modelos:** Los 3 modelos están disponibles (mistral-small, qwen3:32b, gemma3:27b)

## ✨ Ahora

Accede a **http://localhost:3000** y deberías ver todos los modelos listos para usar.

---

**Soluciona:** 2026-03-09T23:16
**Estado:** ✅ FUNCIONANDO
