# 📊 Estado de Instalación — AI Stack macOS

## ✅ COMPLETADO

### Fase 1: Herramientas Base
- ✅ Homebrew
- ✅ Node.js 25.8.0
- ✅ Python 3.14.3
- ✅ Git 2.53.0
- ✅ UV (gestor de paquetes Python)

### Fase 2: Ollama + Modelos
- ✅ Ollama instalado
- ✅ Variables de entorno configuradas (OLLAMA_HOST=0.0.0.0, OLLAMA_ORIGINS="*")
- ✅ Modelos descargados:
  - mistral-small:latest (14 GB)
  - qwen3:32b (20 GB)
  - gemma3:27b (17 GB)

### Fase 4: Node.js Tools
- ✅ Webclaw instalado globalmente

## ⏳ PENDIENTE (Requiere Autenticación)

### Fase 5: Seguridad
- ⏳ Tailscale (requiere sudo)
- ⏳ Caddy (requiere sudo)
- ⏳ Docker (requiere sudo)

### Fase 3: Open WebUI
- ⏳ Open WebUI (vía Docker — requiere Docker instalado)

---

## 🚀 PRÓXIMOS PASOS

### Paso 1: Instalar Herramientas Seguras
Ejecuta el script con autenticación:
```bash
chmod +x ~/install-secure.sh
~/install-secure.sh
```

Este script instala:
- Tailscale
- Caddy
- Docker (opcional pero recomendado)

### Paso 2: Verificar que Ollama está Funcionando
```bash
ollama list  # Debe mostrar los 3 modelos
curl http://localhost:11434/api/tags  # Alternativa
```

### Paso 3: Iniciar Open WebUI (una vez Docker esté instalado)
```bash
chmod +x ~/start-openwebui.sh
~/start-openwebui.sh
```

Luego accede a: **http://localhost:3000**

### Paso 4: Configurar Tailscale (Acceso Remoto)
```bash
# Abre la app y inicia sesión
open -a Tailscale

# En terminal, habilita acceso remoto:
tailscale serve 3000  # Open WebUI
```

---

## 📍 Puertos Activos

| Servicio | Puerto | Estado | URL |
|----------|--------|--------|-----|
| Ollama | 11434 | ✅ Activo | http://localhost:11434 |
| Open WebUI | 3000 | ⏳ (requiere Docker) | http://localhost:3000 |
| OpenClaw | 4000 | ⏳ (no instalado) | http://localhost:4000 |
| Webclaw | 5000 | ⏳ (no instalado) | http://localhost:5000 |

---

## 🔧 Configuración

### Caddyfile
Ubicado en: `~/Caddyfile`
- Proxy inverso para puertos 3000, 4000, 5000, 11434

### LaunchAgents
Para servicios automáticos (si lo necesitas después):
- `~/Library/LaunchAgents/com.openwebui.plist`
- `~/Library/LaunchAgents/com.ollama.plist`

---

## ⚠️ Notas

1. **Ollama**: Ya está corriendo. Puedes verificar con `ollama list`
2. **Open WebUI**: Necesita Docker instalado. PyPI no tenía el paquete disponible.
3. **Modelos**: Son bastante grandes (~50GB total). Verifica tu espacio en disco.
4. **Ollama config**: Se configuró para escuchar en `0.0.0.0` (todos los interfaces)

---

## 🆘 Troubleshooting

### Si Ollama no se inicia:
```bash
open -a Ollama
# O mediante launchctl:
launchctl list | grep ollama
```

### Si quieres detener Ollama:
```bash
pkill -f ollama
```

### Verificar que todo está escuchando:
```bash
netstat -an | grep LISTEN | grep -E "11434|3000|4000|5000"
```
