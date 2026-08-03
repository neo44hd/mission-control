# 🦞 Acceso al Control UI de OpenClaw

## ⚠️ PROBLEMA SOLUCIONADO

El Control UI requería autenticación. Se ha configurado correctamente con el token.

## 🔑 TOKEN DE AUTENTICACIÓN

```
aca30e113a9d745ec3458609c7a06b2261f49c0b91d0759428d4717c0cd7ff9c
```

**Ubicación:** `~/.openclaw/openclaw.json`

---

## 🌐 ACCESO AL CONTROL UI

### Opción 1: URL Directa (RECOMENDADO)
```
http://localhost:18789
```

1. Abre en tu navegador: **http://localhost:18789**
2. Verás: "Conexión a la puerta de enlace"
3. En el campo "Token de la puerta de enlace", pega:
   ```
   aca30e113a9d745ec3458609c7a06b2261f49c0b91d0759428d4717c0cd7ff9c
   ```
4. Haz clic en **"Conectar"**

### Opción 2: URL Tokenizada (Automática)
```bash
cd ~/openclaw
node dist/index.js dashboard --no-open
# Generará URL como: http://localhost:18789?token=...
```

---

## 📊 ESTADO ACTUAL

```
Sistema:        OpenClaw 2026.3.9
Puerto:         18789
Modo:           local
Autenticación:  Token-based (activada)
Estado:         ✅ Listo para conectar
```

---

## 🎯 PASOS RÁPIDOS

### 1. Asegúrate de que OpenClaw está corriendo
```bash
curl http://localhost:18789 | head -20
# Debe mostrar HTML del Control UI
```

### 2. Abre en tu navegador
```
http://localhost:18789
```

### 3. Introduce el token
**Campo:** "Token de la puerta de enlace"
**Valor:** `aca30e113a9d745ec3458609c7a06b2261f49c0b91d0759428d4717c0cd7ff9c`

### 4. Haz clic en "Conectar"

---

## ✅ VALIDACIÓN

Una vez conectado, verás:
- ✅ Estado: "Conectado"
- ✅ Tiempo de actividad (uptime)
- ✅ Intervalos de sincronización
- ✅ Estado de canales
- ✅ Sesiones activas

---

## 🆘 Troubleshooting

### "unauthorized: gateway token missing"
**Solución:**
1. Abre `http://localhost:18789` en tu navegador
2. Pega el token en **"Token de la puerta de enlace"**
3. Haz clic en **"Conectar"**

### Gateway no responde
```bash
# Verificar que OpenClaw está corriendo
ps aux | grep "node dist/index.js gateway"

# Si no está, reiniciar
cd ~/openclaw
node dist/index.js gateway --port 18789 --allow-unconfigured &
```

### Token incorrecto
**Token correcto:**
```
aca30e113a9d745ec3458609c7a06b2261f49c0b91d0759428d4717c0cd7ff9c
```

Verifica que es exactamente este, sin espacios adicionales.

---

## 🔐 SEGURIDAD

⚠️ **IMPORTANTE:**
- Este token está guardado en `~/.openclaw/openclaw.json`
- Nunca lo compartas públicamente
- Úsalo solo para Control UI local o acceso remoto vía Tailscale
- Para acceso remoto seguro, usa Tailscale Funnel con HTTPS

---

## 📱 Alternativas de Acceso

### WebChat (Chat Interface)
```
http://localhost:18789/web
```

### API WebSocket (Programático)
```
ws://localhost:18789
Headers: Authorization: Bearer aca30e113a9d745ec3458609c7a06b2261f49c0b91d0759428d4717c0cd7ff9c
```

### Comandos CLI
```bash
# Ver status del gateway
openclaw channels status

# Enviar mensaje
openclaw message send --to +1234567890 --message "Hello"

# Agent message
openclaw agent --message "Pregunta" --thinking high
```

---

## 🚀 Próximos Pasos

1. ✅ Acceder al Control UI
2. ✅ Verificar status del gateway
3. ✅ Configurar canales (opcional)
4. ✅ Crear sesiones
5. ✅ Integrar con Open WebUI

---

**Token guardado en:** `~/.openclaw/openclaw.json`
**Versión:** OpenClaw 2026.3.9
**Estado:** ✅ Listo
