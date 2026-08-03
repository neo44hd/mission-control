# 📋 SynK-IA Unified Ecosystem — Deployment Guide

**Last Updated**: 2026-08-03  
**Status**: Phase 2 Complete — Ready for Production  
**Version**: 1.0

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation Steps](#installation-steps)
3. [Configuration](#configuration)
4. [Startup Procedures](#startup-procedures)
5. [Verification](#verification)
6. [Persistence with PM2](#persistence-with-pm2)
7. [Troubleshooting](#troubleshooting)
8. [Maintenance](#maintenance)

---

## Prerequisites

### System Requirements
- macOS (tested on macOS with zsh 5.9)
- Node.js v26.4.0 or higher
- npm with js-yaml package
- Docker & Docker Compose (for container services)
- PM2 (for process management - optional but recommended)

### Check Prerequisites
```bash
# Node.js
node -v  # Should be v26.4.0+

# npm
npm -v

# Docker
docker --version
docker-compose --version

# PM2 (if using)
pm2 -v
```

### Install Missing Dependencies
```bash
# Install js-yaml (if not present)
npm install js-yaml --save

# Install PM2 globally (optional)
npm install -g pm2
```

---

## Installation Steps

### Step 1: Clone/Download Configuration Files

All necessary files are already in place:

```bash
cd /Users/davidnows

# Verify files exist
ls -la synk-ia-*.js
ls -la synk-ia-global-config.yaml
ls -la SYNK-IA-*.md
ls -la .synkia-ai-hub/unified-memory.json
```

### Step 2: Make Scripts Executable

```bash
chmod +x /Users/davidnows/synk-ia-orchestrator.js
chmod +x /Users/davidnows/synk-ia-model-selector.js
chmod +x /Users/davidnows/hub-access-v2.js
```

### Step 3: Validate Configuration

```bash
# Test YAML syntax
node -e "const yaml = require('js-yaml'); const fs = require('fs'); \
  const config = yaml.load(fs.readFileSync('/Users/davidnows/synk-ia-global-config.yaml', 'utf8')); \
  console.log('✅ Config valid'); \
  console.log('Services:', Object.keys(config.services).length); \
  console.log('Task profiles:', Object.keys(config.modelSelection.taskProfiles).length);"
```

Expected output:
```
✅ Config valid
Services: 13
Task profiles: 5
```

### Step 4: Create Data Directories

```bash
# Ensure data directories exist
mkdir -p ~/.synkia-ai-hub/logs
mkdir -p ~/.synkia-ai-hub/metrics

# Check existing files
ls -la ~/.synkia-ai-hub/
```

---

## Configuration

### Global Configuration File

**Location**: `/Users/davidnows/synk-ia-global-config.yaml`

**Key Sections**:

#### Services (Lines 15-241)
Define all 13 services with:
- Port mappings
- Health check endpoints
- Critical/autoRestart flags
- Docker network assignments

Edit to add/remove services or change ports.

#### Model Selection (Lines 243-298)
Define task-specific model selections:
- **coding**: primary=local-claude-code, secondary=local-coder-ollama, fallback=qwen:7b
- **research**: primary=local-reason, secondary=local-big, fallback=llama:3b
- **creative**: primary=local-big, secondary=llama:3b, fallback=local-fast
- **fast**: primary=llama:3b, secondary=local-fast, fallback=qwen:3b
- **jobMatching**: primary=ruflow-semantic-scorer, secondary=local-reason, fallback=llama:3b

Edit to adjust model preferences or add new task types.

#### Orchestration Rules (Lines 300-370)
Define intelligent routing patterns:
- Context keywords → target tool
- Health check intervals (default: 30s)
- Auto-restart policies

#### Memory & Learning (Lines 372-400)
Configure:
- GitHub discovery interval (default: 3600s = 1 hour)
- Learning thresholds
- Trending keywords

#### Network Configuration (Lines 402-441)
Docker networks and Cloudflare tunnel routes.

#### PM2 Configuration (Lines 443-465)
Process management settings.

---

## Startup Procedures

### Option 1: Manual Start (Development)

#### Start Orchestrator
```bash
node /Users/davidnows/synk-ia-orchestrator.js
```

Output should show:
```
═══════════════════════════════════════════════════════════════════════════════
🚀 SynK-IA ORCHESTRATOR v1.0 — Starting...
═══════════════════════════════════════════════════════════════════════════════
✅ Configuration loaded from /Users/davidnows/synk-ia-global-config.yaml
✅ Orchestrator API listening on port 9500
✅ Health check cycle complete
✅ SynK-IA Orchestrator fully operational
```

In a new terminal, start Model Selector:
```bash
node /Users/davidnows/synk-ia-model-selector.js
```

Output should show:
```
✅ Configuration loaded
🚀 Model Selector API listening on port 9501
  - Select model: http://localhost:9501/api/model-selector/select?taskType=coding
  - Compare models: http://localhost:9501/api/model-selector/compare?models=...
  - All models: http://localhost:9501/api/model-selector/models
```

### Option 2: PM2 Start (Production) ⭐ RECOMMENDED

#### Install PM2 (if not already)
```bash
npm install -g pm2
```

#### Create PM2 Ecosystem File

Create `/Users/davidnows/ecosystem.config.js`:
```javascript
module.exports = {
  apps: [
    {
      name: 'synk-orchestrator',
      script: '/Users/davidnows/synk-ia-orchestrator.js',
      instances: 1,
      exec_mode: 'fork',
      env: {
        NODE_ENV: 'production',
        CONFIG_PATH: '/Users/davidnows/synk-ia-global-config.yaml'
      },
      max_memory_restart: '500M',
      error_file: '/Users/davidnows/.synkia-ai-hub/logs/orchestrator-error.log',
      out_file: '/Users/davidnows/.synkia-ai-hub/logs/orchestrator-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      autorestart: true,
      watch: false,
      ignore_watch: ['node_modules', '.git', 'logs']
    },
    {
      name: 'synk-model-selector',
      script: '/Users/davidnows/synk-ia-model-selector.js',
      instances: 1,
      exec_mode: 'fork',
      env: {
        NODE_ENV: 'production',
        CONFIG_PATH: '/Users/davidnows/synk-ia-global-config.yaml',
        MODEL_SELECTOR_PORT: 9501
      },
      max_memory_restart: '500M',
      error_file: '/Users/davidnows/.synkia-ai-hub/logs/model-selector-error.log',
      out_file: '/Users/davidnows/.synkia-ai-hub/logs/model-selector-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      autorestart: true,
      watch: false,
      ignore_watch: ['node_modules', '.git', 'logs']
    }
  ]
};
```

#### Start with PM2
```bash
pm2 start /Users/davidnows/ecosystem.config.js

# Save PM2 config so it restarts on reboot
pm2 save

# Create startup hook (macOS)
pm2 startup launchd -u davidnows --hp /Users/davidnows
```

#### PM2 Commands
```bash
# Check status
pm2 list

# View logs
pm2 logs synk-orchestrator
pm2 logs synk-model-selector

# Stop all
pm2 stop all

# Restart all
pm2 restart all

# Monitor
pm2 monit

# Remove
pm2 delete synk-orchestrator synk-model-selector
```

---

## Verification

### Test Orchestrator

```bash
# Get orchestrator status
curl -s http://localhost:9500/api/orchestrator/status | jq '.services | keys'

# Expected: list of all services
```

### Test Routing

```bash
# Test coding context
curl -s "http://localhost:9500/api/orchestrator/model-select?context=refactor&taskType=coding" | jq '.'

# Expected output:
# {
#   "status": "routed",
#   "tool": "...",
#   "model": "...",
#   "confidence": 0.9
# }
```

### Test Model Selector

```bash
# Get all models
curl -s http://localhost:9501/api/model-selector/models | jq '.total'

# Expected: 7

# Select best coding model
curl -s "http://localhost:9501/api/model-selector/select?taskType=coding" | jq '.recommendation'

# Expected: "local-claude-code"
```

### Test Hub (if updated)

```bash
# Hub v2.0 with proxies
curl -s http://localhost:8889/health | jq '.'

# Or visit in browser:
# http://localhost:8889/hub
```

---

## Persistence with PM2

### Enable Startup Hook

```bash
# Generate startup script
pm2 startup launchd -u davidnows --hp /Users/davidnows

# This creates: ~/.pm2/startup/launchd/pm2-davidnows-LaunchDaemons/
# Add to launch agents

# Verify
pm2 list
pm2 logs
```

### Automatic Restart on Crash

PM2 automatically restarts crashed processes. View in config:
```javascript
autorestart: true,  // Enabled in ecosystem.config.js
max_memory_restart: '500M'  // Restart if exceeds 500MB
```

### Manual Persistence Check

```bash
# Test: Kill a process
pm2 delete synk-orchestrator

# PM2 should auto-restart if enabled
# Verify:
ps aux | grep synk-ia-orchestrator
pm2 list
```

---

## Troubleshooting

### Orchestrator Won't Start

```bash
# Check if port 9500 is in use
lsof -i :9500

# Kill existing process if needed
pkill -f synk-ia-orchestrator

# Check Node.js version
node -v  # Should be v26.4.0+

# Run with verbose output
node /Users/davidnows/synk-ia-orchestrator.js 2>&1 | tee debug.log
```

### Model Selector Won't Start

```bash
# Check if port 9501 is in use
lsof -i :9501

# Verify js-yaml is installed
npm list js-yaml

# If missing:
npm install js-yaml
```

### Configuration Load Errors

```bash
# Validate YAML syntax
node -e "const yaml = require('js-yaml'); const fs = require('fs'); \
  try { yaml.load(fs.readFileSync('/Users/davidnows/synk-ia-global-config.yaml', 'utf8')); \
    console.log('✅ YAML valid'); } \
  catch(e) { console.error('❌', e.message); }"
```

### Services Showing as Offline

```bash
# Check if services are actually running
# SynK-IA-Ops (3001)
curl -s http://localhost:3001/health | jq '.status'

# Ollama (11434)
curl -s http://localhost:11434/api/version | jq '.version'

# OpenWebUI (3030)
curl -s http://localhost:3030/health

# If offline, restart via docker or pm2:
docker-compose -f docker-compose.synkia-os.yml restart sinkia-api
```

### High Memory Usage

```bash
# Check memory usage
pm2 monit

# If exceeding 500MB, process auto-restarts
# View logs for errors:
pm2 logs synk-orchestrator | tail -100
```

---

## Maintenance

### Daily Checks

```bash
# Check all services
curl -s http://localhost:9500/api/orchestrator/status | jq '.services | .[] | select(.status == "offline")'

# Check learning stats
curl -s http://localhost:9500/api/orchestrator/learning | jq '.recommendations'

# Verify memory growth
pm2 monit
```

### Weekly Tasks

```bash
# Update GitHub discoveries manually
curl -s http://localhost:9500/api/orchestrator/status | jq '.lastCheck'

# Check cost tracking
curl -s http://localhost:9501/api/model-selector/costs | jq '.' > /tmp/costs-$(date +%Y%m%d).json

# Backup unified memory
cp ~/.synkia-ai-hub/unified-memory.json ~/.synkia-ai-hub/unified-memory.backup.$(date +%Y%m%d).json
```

### Monthly Tasks

```bash
# Backup logs
tar -czf /tmp/synk-logs-$(date +%Y%m).tar.gz ~/.synkia-ai-hub/logs/

# Review performance metrics
cat ~/.synkia-ai-hub/unified-memory.json | jq '.performance'

# Cleanup old logs (keep last 30 days)
find ~/.synkia-ai-hub/logs -type f -mtime +30 -delete
```

### Configuration Updates

When changing `synk-ia-global-config.yaml`:

```bash
# 1. Validate new config
node -e "const yaml = require('js-yaml'); const fs = require('fs'); \
  yaml.load(fs.readFileSync('/Users/davidnows/synk-ia-global-config.yaml', 'utf8')); \
  console.log('✅ Config valid');"

# 2. Backup current config
cp synk-ia-global-config.yaml synk-ia-global-config.backup.$(date +%Y%m%d).yaml

# 3. Restart orchestrators
pm2 restart synk-orchestrator synk-model-selector

# 4. Verify new config loaded
curl -s http://localhost:9500/api/orchestrator/status | jq '.services | length'
```

---

## Production Checklist

- [ ] Node.js v26.4.0+ installed
- [ ] js-yaml npm package installed
- [ ] All scripts have execute permissions (chmod +x)
- [ ] Config YAML validated
- [ ] Data directories created (~/.synkia-ai-hub/)
- [ ] PM2 ecosystem config created
- [ ] Startup hook configured (pm2 startup)
- [ ] All services pass health checks
- [ ] Orchestrator responds on port 9500
- [ ] Model Selector responds on port 9501
- [ ] Intelligent routing verified with test queries
- [ ] PM2 persistence tested (restart machine, check pm2 list)
- [ ] Logs monitored for errors
- [ ] Backup schedule established

---

## Rollback Procedures

### If Something Goes Wrong

```bash
# 1. Stop all processes
pm2 stop all

# 2. Restore previous config
cp synk-ia-global-config.backup.YYYYMMDD.yaml synk-ia-global-config.yaml

# 3. Restore previous memory (if corrupted)
cp ~/.synkia-ai-hub/unified-memory.backup.YYYYMMDD.json ~/.synkia-ai-hub/unified-memory.json

# 4. Restart
pm2 restart all

# 5. Verify
curl http://localhost:9500/api/orchestrator/status
```

### Full Reset

```bash
# WARNING: This resets the entire system

# 1. Stop all processes
pm2 delete all

# 2. Clear memory (backup first!)
rm ~/.synkia-ai-hub/unified-memory.json
rm ~/.synkia-ai-hub/ecosystem-state.json

# 3. Restart orchestrators
pm2 start ecosystem.config.js

# 4. System will reinitialize with clean state
```

---

## Support & Documentation

- **Quick Reference**: `SYNK-IA-QUICK-REFERENCE.md`
- **Ecosystem Guide**: `SYNK-IA-ECOSYSTEM-GUIDE.md`
- **API Documentation**: See endpoints in quick reference
- **Logs**: `~/.synkia-ai-hub/ecosystem-events.log`

---

## Summary

| Component | Port | Status | Auto-restart |
|-----------|------|--------|--------------|
| Orchestrator | 9500 | ✅ Deployed | ✅ Yes (PM2) |
| Model Selector | 9501 | ✅ Deployed | ✅ Yes (PM2) |
| Hub v2.0 | 8889 | ✅ Ready | ✅ Yes (PM2) |
| SynK-IA-Ops | 3001 | ✅ Running | ✅ Yes (Docker) |
| Ollama | 11434 | ✅ Running | ✅ Yes (Docker) |

**Deployment Status**: ✅ COMPLETE  
**Production Ready**: ✅ YES  
**Next Step**: Monitor and optimize based on usage patterns

---

**Document Version**: 1.0  
**Last Updated**: 2026-08-03  
**Maintained By**: SynK-IA Ecosystem Team
