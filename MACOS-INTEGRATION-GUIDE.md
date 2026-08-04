# 🍎 macOS SYSTEM INTEGRATION - Complete Guide

**Status:** ✅ **FULLY INTEGRATED WITH LAUNCHD**  
**Auto-Startup:** ✅ **ENABLED**  
**System Monitoring:** ✅ **ACTIVE**  

---

## 📋 What Was Configured

Your entire SYNK-OPS system is now integrated into macOS LaunchD with:

- ✅ **Auto-launch on system startup** (all services)
- ✅ **Auto-restart on crash** (via KeepAlive)
- ✅ **System monitoring** (checks every 5 minutes)
- ✅ **Centralized logging** (all logs in ~/.synkia-ai-hub/)
- ✅ **Quick shell aliases** (for easy management)
- ✅ **Beautiful dashboard** (view all service status)

---

## 🚀 What Launches Automatically

When you restart your Mac, these services start **automatically**:

### Foundation Services
1. **Ollama** (:11434)
   - Local LLM with 7 models
   - Auto-restarts on crash
   - Configured for single model parallel

2. **LM Studio** (:1234)
   - Local LLM with 9 models
   - Must be started manually (macOS application)
   - Configured as primary provider

### Application Services
3. **Main Server** (:3001)
   - SYNK-OPS application
   - All APIs and routes
   - Auto-restarts on crash

### Agent Services
4. **Hermes Agent** (:5001)
   - Job orchestration
   - Auto-restarts on crash

5. **OpenClaw** (:7999)
   - Code generation
   - Auto-restarts on crash

6. **RuFlow** (:8001)
   - Workflow engine
   - Auto-restarts on crash

7. **Odysseus** (:8002)
   - Multi-agent orchestrator
   - Auto-restarts on crash

### Monitoring Service
8. **System Monitor**
   - Checks services every 5 minutes
   - Auto-restarts failed services
   - Logs activity to monitor.log

---

## 🎛️ LaunchD Configuration Files

All configuration files stored in:
```
~/Library/LaunchAgents/
├── com.ollama.service.plist
├── com.synkia.main-server.plist
├── com.synkia.hermes.plist
├── com.synkia.openclaw.plist
├── com.synkia.ruflow.plist
├── com.synkia.odysseus.plist
└── com.synkia.monitor.plist
```

Each plist includes:
- Auto-start configuration (`RunAtLoad: true`)
- Auto-restart on crash (`KeepAlive`)
- Environment variables (URLs, ports, keys)
- Logging (stdout/stderr)

---

## 📊 Quick Commands (Shell Aliases)

After sourcing `~/.zshrc`, you can use:

### View Dashboard
```bash
synk-dashboard          # See all service status
```

### Check Status
```bash
synk-status            # Get agent status (JSON)
synk-health            # Get system health
synk-logs              # Follow all logs in real-time
```

### Control Services
```bash
synk-start             # Start all services
synk-stop              # Stop all services
synk-restart           # Restart all services
```

### Manual LaunchD Control
```bash
# Start specific service
launchctl start com.synkia.main-server

# Stop specific service
launchctl stop com.synkia.main-server

# Enable/disable auto-launch
launchctl load ~/Library/LaunchAgents/com.synkia.main-server.plist
launchctl unload ~/Library/LaunchAgents/com.synkia.main-server.plist

# Check service status
launchctl list | grep com.synkia
```

---

## 🔍 Monitoring & Logging

### Log Files Location
```
/Users/davidnows/.synkia-ai-hub/
├── ollama.log
├── main-server.log
├── hermes.log
├── openclaw.log
├── ruflow.log
├── odysseus.log
├── monitor.log
└── *-error.log (error streams)
```

### View Logs
```bash
# View all logs in real-time
tail -f /Users/davidnows/.synkia-ai-hub/*.log

# View specific service
tail -f /Users/davidnows/.synkia-ai-hub/main-server.log

# View errors only
tail -f /Users/davidnows/.synkia-ai-hub/*-error.log
```

### System Monitor
- Runs automatically as LaunchAgent
- Checks all services every 5 minutes
- Auto-restarts services if they crash
- Logs all activity to `monitor.log`

---

## 🔄 System Lifecycle

### On System Startup
1. macOS LaunchD starts all `com.synkia.*` services
2. System monitor starts and begins checking every 5 minutes
3. Services initialize with configured environment variables
4. Logs created in `~/.synkia-ai-hub/`

### On Service Crash
1. System monitor detects port is not responding
2. Automatically restarts service via launchctl
3. Logs restart action to `monitor.log`
4. Service comes back online

### On System Shutdown
1. All LaunchAgents receive shutdown signal
2. Services gracefully terminate
3. Next startup automatically restarts them

---

## 🎯 Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│            macOS System (LaunchD)                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌────────────────────────────────────────────────┐   │
│  │ Foundation Layer                               │   │
│  │ ├─ Ollama (:11434)                            │   │
│  │ └─ LM Studio (:1234) [manual start]           │   │
│  └────────────────────────────────────────────────┘   │
│           ↓                                             │
│  ┌────────────────────────────────────────────────┐   │
│  │ Application Layer                              │   │
│  │ └─ Main Server (:3001)                         │   │
│  │    ├─ API Routes                              │   │
│  │    └─ Chat Endpoint                           │   │
│  └────────────────────────────────────────────────┘   │
│           ↓                                             │
│  ┌────────────────────────────────────────────────┐   │
│  │ Agent Layer                                    │   │
│  │ ├─ Hermes (:5001)                             │   │
│  │ ├─ OpenClaw (:7999)                           │   │
│  │ ├─ RuFlow (:8001)                             │   │
│  │ └─ Odysseus (:8002)                           │   │
│  └────────────────────────────────────────────────┘   │
│           ↓                                             │
│  ┌────────────────────────────────────────────────┐   │
│  │ Monitoring Layer                               │   │
│  │ └─ System Monitor (checks every 5min)          │   │
│  │    ├─ Port health checks                      │   │
│  │    ├─ Auto-restart on crash                   │   │
│  │    └─ Activity logging                        │   │
│  └────────────────────────────────────────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## ⚙️ How to Manage Services

### Disable Auto-Launch
```bash
# Disable all SYNK-OPS services from auto-starting
launchctl unload ~/Library/LaunchAgents/com.synkia.*.plist
launchctl unload ~/Library/LaunchAgents/com.ollama.service.plist
```

### Enable Auto-Launch
```bash
# Re-enable all SYNK-OPS services to auto-start
launchctl load ~/Library/LaunchAgents/com.synkia.*.plist
launchctl load ~/Library/LaunchAgents/com.ollama.service.plist
```

### Remove Services
```bash
# Completely remove from system
launchctl unload ~/Library/LaunchAgents/com.synkia.*.plist
rm ~/Library/LaunchAgents/com.synkia.*.plist
rm ~/Library/LaunchAgents/com.ollama.service.plist
```

---

## 🚨 Troubleshooting

### Service Not Starting?
```bash
# Check if service is loaded
launchctl list | grep com.synkia.main-server

# Load the service manually
launchctl load ~/Library/LaunchAgents/com.synkia.main-server.plist

# Check for errors
tail -f /Users/davidnows/.synkia-ai-hub/main-server-error.log
```

### Port Already in Use?
```bash
# Find what's using the port
lsof -i :3001

# Kill the process
kill -9 <PID>

# Restart the service
launchctl stop com.synkia.main-server
sleep 2
launchctl start com.synkia.main-server
```

### Service Keeps Crashing?
```bash
# Check the error log
tail -50 /Users/davidnows/.synkia-ai-hub/main-server-error.log

# Check main log
tail -50 /Users/davidnows/.synkia-ai-hub/main-server.log

# Restart manually with debugging
cd /Users/davidnows/synkia/repos/synk-ia && npm start
```

---

## 📈 System Requirements

**Minimum:**
- macOS 10.13+
- 4GB RAM
- 2 CPU cores
- 10GB disk space

**Recommended:**
- macOS 11.0+ (Monterey)
- 16GB RAM
- 8+ CPU cores
- 50GB disk space

**Current System:**
- CPU: 12 cores
- Memory: 24 GB
- Available: ~1.2 GB (at last check)

---

## 🎓 What Happens on Restart

1. **System boots** → LaunchD loads all plist files
2. **Ollama starts** → LLM service initializes (7 models)
3. **Main server starts** → APIs and routes become available
4. **Agents start** → Hermes, OpenClaw, RuFlow, Odysseus initialize
5. **Monitor starts** → System health checks begin every 5 min
6. **System ready** → All services operational, zero manual intervention

---

## 💡 Best Practices

1. **Check dashboard regularly:**
   ```bash
   synk-dashboard
   ```

2. **Monitor logs for issues:**
   ```bash
   tail -f /Users/davidnows/.synkia-ai-hub/*.log
   ```

3. **Restart periodically:**
   ```bash
   synk-restart
   ```

4. **Keep LM Studio updated** (manual application)

5. **Monitor disk space** in `~/.synkia-ai-hub/`

---

## 🔗 Integration Points

### Browser Access
- Main API: http://localhost:3001
- Chat: POST http://localhost:3001/api/chat
- Agents: GET http://localhost:3001/api/agents/status

### Terminal Access
```bash
# Quick status check
synk-status

# Run chat query
curl -X POST http://localhost:3001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"test"}],"stream":false}'

# Check agent status
curl http://localhost:3001/api/agents/status | jq .
```

### System Monitoring
```bash
# Real-time system view
synk-dashboard

# Follow all logs
synk-logs
```

---

## ✨ Summary

Your SYNK-OPS system is now:
- ✅ Integrated with macOS LaunchD
- ✅ Auto-launching on system startup
- ✅ Auto-restarting on crashes
- ✅ Monitored every 5 minutes
- ✅ Fully manageable via command line
- ✅ Logged to centralized location
- ✅ Ready for production use

**Next:** Just restart your Mac and everything will be running automatically!

