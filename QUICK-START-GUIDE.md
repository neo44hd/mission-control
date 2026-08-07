# 🚀 Quick Start Guide - Claude Code Services

**Last Updated**: 7 de Agosto de 2026 - 18:16 UTC

---

## ⚡ One-Command Startup

```bash
~/startup-claude-services.sh
```

This single command starts **ALL** Claude Code services:
- ✅ Hermes Agent
- ✅ Ollama LLM Server
- ✅ Aider AI Pair Programmer
- ✅ OpenClaw API Server
- ✅ OpEncoder Code Optimizer
- ✅ LLM Selector Model Manager

---

## 📋 Individual Service Control

### Aider (AI Pair Programming)
```bash
~/scripts/aider.sh start              # Start Aider
~/scripts/aider.sh stop               # Stop Aider
~/scripts/aider.sh status             # Check status
~/scripts/aider.sh logs               # View logs
```

### OpenClaw (Local API)
```bash
~/scripts/openclaw_start.sh start     # Start OpenClaw
~/scripts/openclaw_start.sh stop      # Stop OpenClaw
~/scripts/openclaw_start.sh restart   # Restart
~/scripts/openclaw_start.sh status    # Check status
~/scripts/openclaw_start.sh logs      # View logs
```

### OpEncoder (Code Optimization)
```bash
~/scripts/opencoder.sh run            # Run optimization job
~/scripts/opencoder.sh background     # Run as daemon
~/scripts/opencoder.sh stop           # Stop job
~/scripts/opencoder.sh status         # Check status
~/scripts/opencoder.sh logs           # View logs
```

### LLM Selector (Model Manager)
```bash
~/scripts/lms-selector.sh start               # Start service
~/scripts/lms-selector.sh stop                # Stop service
~/scripts/lms-selector.sh status              # Check status
~/scripts/lms-selector.sh select <model>      # Select model
~/scripts/lms-selector.sh list                # List models
~/scripts/lms-selector.sh config              # Show config
~/scripts/lms-selector.sh logs                # View logs
```

---

## 🔍 Checking Service Status

### All Services at Once
```bash
echo "=== Aider ===" && ~/scripts/aider.sh status
echo "=== OpenClaw ===" && ~/scripts/openclaw_start.sh status
echo "=== LLM Selector ===" && ~/scripts/lms-selector.sh status
```

### Check Ollama Models
```bash
curl -s http://localhost:11434/api/tags | jq '.models[] | {name, size}'
```

---

## 📊 Viewing Logs

```bash
# Real-time logs (all services)
tail -f ~/.startup-logs/startup-*.log

# Individual service logs
tail -f ~/.aider/logs/aider.log
tail -f ~/.openclaw/logs/openclaw.log
tail -f ~/.opencoder/logs/opencoder.log
tail -f ~/.lms-selector/logs/selector.log
tail -f ~/.ollama/logs/ollama.log
```

---

## 🛠️ Configuration

### LLM Model Selection
```bash
# View current configuration
~/scripts/lms-selector.sh config

# Select a different model
~/scripts/lms-selector.sh select llama3

# List available models
~/scripts/lms-selector.sh list
```

### Hermes Configuration
```bash
# Show configuration
hermes config show

# Edit configuration
hermes config edit

# Check configuration validity
hermes config check

# Set specific values
hermes config set llm_provider "ollama"
hermes config set default_model "llama3"
```

---

## 🔧 Troubleshooting

### Service Won't Start

1. **Check if port is already in use**:
```bash
lsof -i :8000    # OpenClaw
lsof -i :9000    # Aider
```

2. **Kill existing process**:
```bash
pkill -f "openclaw"
pkill -f "aider"
```

3. **Check logs for errors**:
```bash
tail -100 ~/.openclaw/logs/openclaw.log
tail -100 ~/.aider/logs/aider.log
```

4. **Restart the service**:
```bash
~/scripts/openclaw_start.sh restart
```

### Ollama Not Responding

```bash
# Check if Ollama is running
ps aux | grep ollama

# Start Ollama manually
ollama serve

# Test Ollama connection
curl -s http://localhost:11434/api/tags
```

### All Services Down

```bash
# Full restart
~/startup-claude-services.sh

# Or individually restart critical services
~/scripts/openclaw_start.sh restart
ollama serve &
```

---

## 📁 File Locations

### Scripts
```
~/scripts/aider.sh
~/scripts/openclaw_start.sh
~/scripts/opencoder.sh
~/scripts/lms-selector.sh
~/startup-claude-services.sh          ← Master startup script
```

### Configuration
```
~/.lms-selector/config.json
~/.aider/logs/
~/.openclaw/logs/
~/.opencoder/logs/
~/.ollama/logs/
~/.startup-logs/                       ← Startup logs
```

---

## ⚙️ Advanced: Auto-Start on Boot

Create a launchd service to auto-start all services on system boot:

```bash
cat > ~/Library/LaunchAgents/com.claudecode.startup.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.claudecode.startup</string>
    <key>Program</key>
    <string>/Users/davidnows/startup-claude-services.sh</string>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/Users/davidnows/.startup-logs/launchd.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/davidnows/.startup-logs/launchd-error.log</string>
</dict>
</plist>
EOF

# Load it
launchctl load ~/Library/LaunchAgents/com.claudecode.startup.plist

# Verify
launchctl list | grep com.claudecode
```

---

## 📞 Common Use Cases

### I want to use Claude Code with Aider
```bash
~/scripts/aider.sh start
# Then use: aider .
```

### I need to optimize my codebase
```bash
~/scripts/opencoder.sh background
# Check logs: tail -f ~/.opencoder/logs/opencoder.log
```

### I want to switch to a different LLM model
```bash
~/scripts/lms-selector.sh list          # See available models
~/scripts/lms-selector.sh select llama3  # Select one
```

### Everything is broken, start fresh
```bash
# Stop all services
killall aider 2>/dev/null
pkill -f openclaw 2>/dev/null
pkill -f opencoder 2>/dev/null
pkill -f lms-selector 2>/dev/null

# Wait and restart
sleep 2
~/startup-claude-services.sh
```

---

## 📚 Related Documentation

- **STARTUP-SCRIPTS-FIX.md** - Detailed explanation of all fixes
- **README-INFRASTRUCTURE.md** - Full infrastructure guide
- **FINAL-STATUS-REPORT.md** - Complete infrastructure status

---

## ✅ Verification Checklist

After running `~/startup-claude-services.sh`, verify:

- [ ] All 6 services show "✅ STARTED"
- [ ] No critical errors in startup log
- [ ] Can access OpenClaw at `http://localhost:8000`
- [ ] Can access Ollama at `http://localhost:11434/api/tags`
- [ ] Aider is responding to commands
- [ ] LLM Selector has detected models

---

**Everything is set up and ready to use!**

Run `~/startup-claude-services.sh` to start all services, or use individual commands above.

*For detailed technical information, see STARTUP-SCRIPTS-FIX.md*
