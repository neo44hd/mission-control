#!/bin/bash

# 🎛️ SYNK-OPS - COMANDOS ÚTILES EN ESPAÑOL
# ==========================================

# 📊 VER ESTADO
echo "📊 VER ESTADO"
echo "synk-dashboard          # Ver estado bonito de todos"
echo "synk-status             # Ver estado en JSON"
echo "synk-health             # Ver salud del sistema"
echo ""

# 🚀 CONTROLAR SERVICIOS
echo "🚀 CONTROLAR SERVICIOS"
echo "synk-start              # Iniciar todos"
echo "synk-stop               # Parar todos"
echo "synk-restart            # Reiniciar todos"
echo ""

# 📋 VER LOGS
echo "📋 VER LOGS"
echo "synk-logs               # Ver todos los logs en tiempo real"
echo "tail -f ~/.synkia-ai-hub/main-server.log     # Log del servidor"
echo "tail -f ~/.synkia-ai-hub/hermes.log          # Log de Hermes"
echo "tail -f ~/.synkia-ai-hub/openclaw.log        # Log de OpenClaw"
echo "tail -f ~/.synkia-ai-hub/monitor.log         # Log del monitor"
echo ""

# 🎯 SERVICIOS INDIVIDUALES
echo "🎯 SERVICIOS INDIVIDUALES"
echo "launchctl start com.synkia.main-server       # Iniciar servidor"
echo "launchctl stop com.synkia.main-server        # Parar servidor"
echo "launchctl start com.synkia.hermes            # Iniciar Hermes"
echo "launchctl stop com.synkia.hermes             # Parar Hermes"
echo "launchctl list | grep com.synkia             # Ver todos"
echo ""

# 🌐 APIS
echo "🌐 LLAMAR APIS"
echo "curl http://localhost:3001/api/health                   # Test servidor"
echo "curl http://localhost:3001/api/agents/status            # Estado agentes"
echo ""

# 🔧 SOLUCIONAR PROBLEMAS
echo "🔧 SOLUCIONAR PROBLEMAS"
echo "lsof -i :3001                                # Ver qué usa puerto"
echo "kill -9 <PID>                                # Matar proceso"
echo "tail -f ~/.synkia-ai-hub/*-error.log         # Ver errores"
echo ""

# 💾 AUTO-ARRANQUE
echo "💾 AUTO-ARRANQUE"
echo "launchctl load ~/Library/LaunchAgents/com.synkia.*.plist     # Activar"
echo "launchctl unload ~/Library/LaunchAgents/com.synkia.*.plist   # Desactivar"
echo ""

# 📝 EJEMPLO: CHAT SIMPLE
echo "📝 EJEMPLO: CHAT SIMPLE"
cat << 'EOF'
curl -X POST http://localhost:3001/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "¿Cuánto es 2+2?"}
    ],
    "stream": false
  }' | jq .
EOF
echo ""

# 📚 DOCUMENTACIÓN
echo "📚 DOCUMENTACIÓN"
echo "Consulta estos archivos para más info:"
echo "  - INTEGRACION-MACOS-RESUMEN.md (en español)"
echo "  - MACOS-INTEGRATION-GUIDE.md (completo en inglés)"
echo "  - SYNK-OPS-QUICK-REF.md (referencia rápida)"
echo ""

echo "🎉 ¡Sistema listo! Todo está configurado con auto-arranque y auto-reinicio."
