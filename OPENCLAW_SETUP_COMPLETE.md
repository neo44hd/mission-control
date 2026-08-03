# 🦞 OpenClaw Setup Completado

## ✅ ESTADO: TOTALMENTE OPERACIONAL

### 🚀 Servicios Activos

| Servicio | Puerto | Estado | URL |
|----------|--------|--------|-----|
| **Ollama** | 11434 | ✅ Activo | http://localhost:11434 |
| **Open WebUI** | 3000 | ✅ Corriendo en Docker | http://localhost:3000 |
| **OpenClaw Gateway** | 18789 | ✅ Activo | ws://localhost:18789 |
| **OpenClaw Control UI** | 18789 | ✅ Activo | http://localhost:18789 |
| **Tailscale** | - | ✅ Instalado y activo | - |

---

## 📊 ACCESO INMEDIATO

### 🏠 LOCAL (Dentro de la red)

```
🔹 Open WebUI (Chat con modelos Ollama)
   URL: http://localhost:3000
   Modelos: mistral-small, qwen3:32b, gemma3:27b

🔹 OpenClaw Control UI (Panel de administración)
   URL: http://localhost:18789
   
🔹 OpenClaw Gateway (API WebSocket)
   WS: ws://localhost:18789
   Autenticación: Token-based
```

### 🔒 RED PRIVADA VÍA TAILSCALE

Tu IP Tailscale (ejecuta en terminal):
```bash
tailscale ip -4
```

Luego accede desde cualquier dispositivo en tu Tailscale network:
```
🔹 OpenClaw: http://<tu-ip-tailscale>:18789
🔹 Open WebUI: http://<tu-ip-tailscale>:3000
🔹 Ollama API: http://<tu-ip-tailscale>:11434
```

### 🌍 INTERNET PÚBLICO VÍA TAILSCALE FUNNEL

Expone OpenClaw de forma segura al público:
```bash
chmod +x ~/expose-openclaw-tailscale.sh
~/expose-openclaw-tailscale.sh
```

Esto generará una URL HTTPS pública como:
```
https://mi-macmini.ts.net
```

---

## 🔧 CONFIGURACIÓN TECHNICAL

### Paths Importantes
```
Código: ~/openclaw
Configuración: ~/.openclaw/
Config JSON: ~/.openclaw/openclaw.json
Variables env: ~/.openclaw/.env
Logs: /tmp/openclaw/openclaw-2026-03-09.log
Gateway logs: tail -f /tmp/openclaw/openclaw-*.log
```

### Modelos Disponibles en Ollama
```
✅ mistral-small (14 GB) - Rápido, bajo consumo
✅ qwen3:32b (20 GB) - Muy capaz, buen balance
✅ gemma3:27b (17 GB) - Excelente razonamiento
```

### Configuración OpenClaw
```json
{
  "gateway": {
    "port": 18789,
    "bind": "loopback",
    "auth": { "mode": "token" }
  },
  "channels": {}
}
```

---

## 🎮 COMANDOS ÚTILES

### Arrancar/Detener OpenClaw

**Iniciar (en background):**
```bash
cd ~/openclaw
node dist/index.js gateway --port 18789 --allow-unconfigured &
```

**Ver logs en tiempo real:**
```bash
tail -f /tmp/openclaw/openclaw-*.log
```

**Detener todos los procesos de OpenClaw:**
```bash
pkill -f "node dist/index.js gateway"
```

### Verificar Status
```bash
# Verificar que todos los servicios están activos
ollama list                          # Modelos Ollama
curl http://localhost:3000          # Open WebUI
curl http://localhost:18789         # OpenClaw
```

### Integraciones
```bash
# Enviar mensaje a OpenClaw (una vez configurado)
curl -X POST http://localhost:18789/api/message \
  -H "Authorization: Bearer TOKEN" \
  -d '{"text":"Hello from OpenClaw"}'
```

---

## 🔐 SEGURIDAD & ACCESO REMOTO

### Tailscale Serve (VPN privada)
```bash
# Exponer en VPN privada (solo para máquinas en Tailscale)
tailscale serve localhost:18789
tailscale serve localhost:3000
```

### Tailscale Funnel (Internet público con HTTPS)
```bash
# Exponer al público con HTTPS automático
tailscale funnel 18789
```

### Ver estatus actual
```bash
tailscale status
tailscale serve status
tailscale funnel status
```

---

## 📋 PRÓXIMOS PASOS

### Opcional: Configurar Canales de Mensajería
OpenClaw puede conectarse a:
- WhatsApp, Telegram, Slack, Discord, Signal, etc.
- Configurable en `~/.openclaw/openclaw.json`

### Opcional: Instalar OpenClaw como Daemon Permanente
```bash
cd ~/openclaw
pnpm openclaw onboard --install-daemon
```

### Monitoreo
```bash
# Ver logs en tiempo real
tail -f /tmp/openclaw/openclaw-*.log | grep -E "ERROR|WARNING|INFO"

# Monitoreo de CPU/Memoria
watch 'ps aux | grep node'
```

---

## 🆘 TROUBLESHOOTING

### Si OpenClaw no inicia
```bash
# Ejecutar doctor para diagnóstico
cd ~/openclaw
node dist/index.js doctor --fix
```

### Si Open WebUI no ve Ollama
```bash
# Verificar conectividad a Ollama
curl http://192.168.0.32:11434/api/tags

# Reinicar Docker
docker restart open-webui
```

### Si Tailscale Funnel no funciona
```bash
# Verificar que Tailscale está activo
tailscale status

# Reiniciar Tailscale
tailscale down
tailscale up
```

---

## 📞 INFORMACIÓN DE CONTACTO & SOPORTE

- **OpenClaw Docs:** https://docs.openclaw.ai
- **Discord:** https://discord.gg/clawd
- **GitHub:** https://github.com/openclaw/openclaw

---

## 📝 RESUMEN RÁPIDO

Tu stack está completamente configurado:
✅ Ollama (motor IA local con 3 modelos)
✅ Open WebUI (interfaz gráfica para chat)
✅ OpenClaw (gestor inteligente de IA)
✅ Tailscale (acceso remoto seguro)
✅ Acceso público HTTPS vía Funnel

**Para acceder ahora:**
- Local: http://localhost:18789 (OpenClaw) y http://localhost:3000 (Open WebUI)
- Remoto: Ejecuta `~/expose-openclaw-tailscale.sh` para obtener URL pública

¡Listo para usar! 🎉
