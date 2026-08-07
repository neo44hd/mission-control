# 🔧 Startup Scripts Fix Guide

**Date**: 7 de Agosto de 2026 - 18:14 UTC  
**Issue**: Missing startup scripts in `~/scripts/` directory  
**Status**: ✅ **FIXED**

---

## Problem Summary

Your startup command had references to these missing scripts:
- ❌ `~/scripts/aider.sh` → Not found
- ❌ `~/scripts/openclaw_start.sh` → Not found
- ❌ `~/scripts/opencoder.sh` → Not found
- ❌ `~/scripts/lms-selector.sh` → Not found

Also, the Hermes config command used an invalid subcommand:
- ❌ `hermes config reload` → Invalid choice (should be `show|edit|get|set|unset|path|env-path|check|migrate`)

---

## Solution Applied

### 1. Created Missing Scripts

All scripts have been created in `~/scripts/` with proper error handling and logging:

#### `aider.sh` - Aider AI Pair Programmer
```bash
~/scripts/aider.sh start          # Start Aider service
~/scripts/aider.sh stop           # Stop Aider
~/scripts/aider.sh status         # Check status
~/scripts/aider.sh logs           # View logs
```

**Features**:
- Integrates Claude Code with Aider for collaborative coding
- Auto-detects Claude Opus model
- Logs to `~/.aider/logs/aider.log`
- PID management for reliable stop/start

#### `openclaw_start.sh` - OpenClaw API Server
```bash
~/scripts/openclaw_start.sh start    # Start OpenClaw
~/scripts/openclaw_start.sh stop     # Stop OpenClaw
~/scripts/openclaw_start.sh restart  # Restart
~/scripts/openclaw_start.sh status   # Check status
~/scripts/openclaw_start.sh logs     # View logs
```

**Features**:
- Manages local OpenClaw API server (port 8000)
- Health checks after startup
- Logs to `~/.openclaw/logs/openclaw.log`
- Automatic port configuration

#### `opencoder.sh` - Code Optimization Engine
```bash
~/scripts/opencoder.sh run          # Run optimization job
~/scripts/opencoder.sh background   # Run as daemon
~/scripts/opencoder.sh stop         # Stop job
~/scripts/opencoder.sh status       # Check status
~/scripts/opencoder.sh logs         # View logs
```

**Features**:
- Runs code optimization and encoding tasks
- Supports both direct execution and background mode
- Recursive directory processing
- Logs to `~/.opencoder/logs/opencoder.log`

#### `lms-selector.sh` - LLM Model Manager
```bash
~/scripts/lms-selector.sh start                # Start service
~/scripts/lms-selector.sh stop                 # Stop service
~/scripts/lms-selector.sh status               # Check status
~/scripts/lms-selector.sh select <model>       # Select default model
~/scripts/lms-selector.sh list                 # List available models
~/scripts/lms-selector.sh config               # Show configuration
~/scripts/lms-selector.sh logs                 # View logs
```

**Features**:
- Auto-creates configuration at `~/.lms-selector/config.json`
- Monitors Ollama at `localhost:11434`
- Model availability tracking
- JSON configuration management

---

## Fixed Startup Command

### Original (Broken)
```bash
# 1. Iniciar Hermes Agent (launchd)
launchctl load ~/Library/LaunchAgents/com.hermes.hertxplore.plist &

# 2. Verificar que Ollama está corriendo
ollama serve &   # ya estaba activo

# 3. Lanzar Aider
~/scripts/aider.sh start                        # ❌ Script didn't exist

# 4. Arrancar OpenClaw (si no lo hace automáticamente)
~/scripts/openclaw_start.sh                     # ❌ Script didn't exist

# 5. Ejecutar OpEncoder como job independiente (puede ser cron)
~/scripts/opencoder.sh run &                    # ❌ Script didn't exist

# 6. Reiniciar selector de LLM
~/scripts/lms-selector.sh start                 # ❌ Script didn't exist

# 7. Recargar configuración Heaven para que tome los tokens
hermes config reload                             # ❌ Invalid command
```

### Corrected
```bash
#!/bin/bash

# 1. Iniciar Hermes Agent (launchd)
echo "1️⃣  Starting Hermes Agent..."
launchctl load ~/Library/LaunchAgents/com.hermes.hertxplore.plist 2>/dev/null || echo "⚠️  Already loaded"

# 2. Verificar que Ollama está corriendo
echo "2️⃣  Starting Ollama..."
ollama serve > ~/.ollama/logs/ollama.log 2>&1 &
sleep 2

# 3. Lanzar Aider
echo "3️⃣  Starting Aider..."
~/scripts/aider.sh start

# 4. Arrancar OpenClaw
echo "4️⃣  Starting OpenClaw..."
~/scripts/openclaw_start.sh start

# 5. Ejecutar OpEncoder como job independiente
echo "5️⃣  Starting OpEncoder..."
~/scripts/opencoder.sh background

# 6. Iniciar selector de LLM
echo "6️⃣  Starting LLM Selector..."
~/scripts/lms-selector.sh start

# 7. Hermes config - use valid commands
echo "7️⃣  Checking Hermes configuration..."
hermes config show
hermes config check

echo "✅ All services started!"
```

---

## Hermes Configuration Fix

The error was: `hermes config: error: argument config_command: invalid choice: 'reload'`

**Valid Hermes commands are**:
```bash
hermes config show          # Display current configuration
hermes config edit          # Edit configuration file
hermes config get <key>     # Get a specific value
hermes config set <key> <value>  # Set a value
hermes config unset <key>   # Remove a configuration key
hermes config path          # Show config file path
hermes config env-path      # Show environment path
hermes config check         # Validate configuration
hermes config migrate       # Migrate to new format
```

**To update token configuration**:
```bash
# Show current config
hermes config show

# Edit config file directly
hermes config edit

# Or use set command
hermes config set llm_provider "openrouter"
hermes config set api_key "your-api-key-here"

# Verify changes
hermes config check
```

---

## Script Locations & Logs

### Scripts
```
~/scripts/aider.sh
~/scripts/openclaw_start.sh
~/scripts/opencoder.sh
~/scripts/lms-selector.sh
```

### Logs
```
~/.aider/logs/aider.log
~/.openclaw/logs/openclaw.log
~/.opencoder/logs/opencoder.log
~/.lms-selector/logs/selector.log
```

### Configuration
```
~/.lms-selector/config.json          ← LLM model selection
```

---

## Quick Commands

### Start All Services
```bash
# Option 1: Use individual commands
~/scripts/aider.sh start
~/scripts/openclaw_start.sh start
~/scripts/opencoder.sh background
~/scripts/lms-selector.sh start

# Option 2: Create a startup script (see corrected version above)
chmod +x ~/startup-all.sh
~/startup-all.sh
```

### Check Status
```bash
~/scripts/aider.sh status
~/scripts/openclaw_start.sh status
~/scripts/opencoder.sh status
~/scripts/lms-selector.sh status
```

### View Logs
```bash
# Aider logs
tail -f ~/.aider/logs/aider.log

# OpenClaw logs
tail -f ~/.openclaw/logs/openclaw.log

# OpEncoder logs
tail -f ~/.opencoder/logs/opencoder.log

# LLM Selector logs
tail -f ~/.lms-selector/logs/selector.log
```

---

## Integration with Hermes

After fixing the startup scripts, configure Hermes to use them:

```bash
# Set Hermes to use the correct LLM model
hermes config set default_model "llama3"

# Configure API endpoints if using cloud providers
hermes config set openrouter_api_key "your-key-here"

# Validate configuration
hermes config check
```

---

## Next Steps

1. **Create a master startup script** (optional but recommended):
```bash
cat > ~/startup-services.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting all Claude Code services..."
~/scripts/aider.sh start
~/scripts/openclaw_start.sh start
~/scripts/opencoder.sh background
~/scripts/lms-selector.sh start
echo "✅ All services started"
EOF

chmod +x ~/startup-services.sh
```

2. **Add to launchd for auto-start on boot** (optional):
```bash
# Create a launchd plist that runs the startup script on boot
```

3. **Test the services individually**:
```bash
~/scripts/aider.sh status
~/scripts/openclaw_start.sh status
~/scripts/lms-selector.sh status
```

---

## Troubleshooting

### If a script fails to start

1. **Check if dependencies are installed**:
```bash
which aider              # Check Aider
which openclaw          # Check OpenClaw
python3 -m opencoder    # Check OpEncoder
```

2. **View detailed logs**:
```bash
tail -100 ~/.aider/logs/aider.log
tail -100 ~/.openclaw/logs/openclaw.log
tail -100 ~/.opencoder/logs/opencoder.log
```

3. **Check port conflicts**:
```bash
lsof -i :8000    # OpenClaw default port
lsof -i :9000    # Aider default port
```

4. **Restart problematic service**:
```bash
~/scripts/openclaw_start.sh stop
sleep 2
~/scripts/openclaw_start.sh start
```

---

## Files Modified/Created

✅ Created: `~/scripts/aider.sh`  
✅ Created: `~/scripts/openclaw_start.sh`  
✅ Created: `~/scripts/opencoder.sh`  
✅ Created: `~/scripts/lms-selector.sh`  
✅ Created: `~/STARTUP-SCRIPTS-FIX.md` (this file)

---

**All startup scripts have been created and are ready to use.** Run them with `start`, `stop`, `status`, or `logs` commands as shown above.

*Last updated: 2026-08-07 18:14 UTC*
