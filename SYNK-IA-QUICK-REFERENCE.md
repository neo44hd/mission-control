# 🚀 SynK-IA Unified Ecosystem — Quick Reference

## Current Status: ✅ OPERATIONAL

- **Orchestrator**: Port 9500 — Running ✅
- **Model Selector**: Port 9501 — Running ✅
- **Hub AI Local**: Port 8889 — Ready (hub-access.js or hub-access-v2.js)
- **SynK-IA-Ops**: Port 3001 — Healthy ✅
- **Ollama**: Port 11434 — Healthy ✅

---

## Quick Commands

### Check System Health
```bash
curl http://localhost:9500/api/orchestrator/status | jq '.services | keys'
```

### Route a Request Intelligently
```bash
# Coding task
curl "http://localhost:9500/api/orchestrator/model-select?context=refactor&taskType=coding"

# Research task
curl "http://localhost:9500/api/orchestrator/model-select?context=analyze&taskType=research"

# Job matching
curl "http://localhost:9500/api/orchestrator/model-select?context=match%20resume&taskType=jobMatching"
```

### Select Best Model
```bash
# For coding
curl "http://localhost:9501/api/model-selector/select?taskType=coding" | jq '.recommendation'

# For research
curl "http://localhost:9501/api/model-selector/select?taskType=research" | jq '.recommendation'

# All available models
curl "http://localhost:9501/api/model-selector/models" | jq '.models | length'
```

### Compare Models
```bash
curl "http://localhost:9501/api/model-selector/compare?models=local-claude-code,local-fast,local-reason" | jq '.'
```

### View Cost Tracking
```bash
curl "http://localhost:9501/api/model-selector/costs" | jq '.'
```

### Get Learning Stats
```bash
curl "http://localhost:9500/api/orchestrator/learning" | jq '.recommendations'
```

---

## Architecture Map

```
                    User Request
                         ↓
          Hub AI Local (8889) [Optional Entry Point]
                         ↓
    ╔═════════════════════════════════════════╗
    ║     Orchestrator (9500)                 ║
    ║  - Analyzes context                     ║
    ║  - Routes to best tool                  ║
    ║  - Monitors health                      ║
    ║  - Learns from performance              ║
    ╚═════════════════════════════════════════╝
             ↓           ↓           ↓
          Model        Tool      Execution
        Selector     Selection     Engine
        (9501)      [intelligent]
             ↓           ↓           ↓
    ┌─────────────────────────────────────────┐
    │  Core Services (Healthy & Monitored)    │
    ├─────────────────────────────────────────┤
    │ • SynK-IA-Ops (3001) — API Gateway      │
    │ • Ollama (11434) — Local Inference      │
    │ • OpenWebUI (3030) — Chat               │
    │ • n8n (5678) — Automation               │
    │ • SearXNG (8888) — Search               │
    │ • OpenClaw (7999) — Agents [offline]    │
    │ • RuFlow (8000/3000) — Jobs [offline]   │
    │ • Hermes (8787) — Desktop [offline]     │
    └─────────────────────────────────────────┘
             ↓
    ╔═════════════════════════════════════════╗
    ║   Unified Memory & Learning System      ║
    ║   ~/.synkia-ai-hub/unified-memory.json  ║
    ║  - Performance metrics                  ║
    ║  - Routing decisions                    ║
    ║  - Model preferences                    ║
    ║  - Discovery cache                      ║
    ╚═════════════════════════════════════════╝
```

---

## Configuration Files

### Global Config
**Location**: `/Users/davidnows/synk-ia-global-config.yaml`

Contains:
- All 13 services with endpoints and health checks
- Intelligent routing patterns (context → tool)
- 5 task profiles with model selection rules
- Docker network & Cloudflare tunnel config
- Auto-healing settings

Edit to:
- Add/remove services
- Change routing rules
- Adjust model fallback chains
- Update port mappings

---

## Daemons

### Start Orchestrator
```bash
node /Users/davidnows/synk-ia-orchestrator.js
```

### Start Model Selector
```bash
node /Users/davidnows/synk-ia-model-selector.js
```

### Make Persistent with PM2
```bash
pm2 start /Users/davidnows/synk-ia-orchestrator.js --name synk-orchestrator
pm2 start /Users/davidnows/synk-ia-model-selector.js --name synk-model-selector
pm2 save
```

### Check Status
```bash
pm2 list
pm2 logs synk-orchestrator
```

---

## Endpoints Reference

### Orchestrator (Port 9500)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/orchestrator/status` | GET | All services health + state |
| `/api/orchestrator/model-select` | GET | Route request, pick tool+model |
| `/api/orchestrator/execute` | POST | Execute with intelligent routing |
| `/api/orchestrator/learning` | GET | Learning stats + recommendations |
| `/health` | GET | Orchestrator health check |

**Query Parameters** for `/model-select`:
- `context` — User input/context (e.g., "refactor code")
- `taskType` — Task category: `coding`, `creative`, `research`, `fast`, `jobMatching`

---

### Model Selector (Port 9501)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/model-selector/select` | GET | Select best model for task |
| `/api/model-selector/compare` | GET | Compare multiple models |
| `/api/model-selector/models` | GET | List all available models |
| `/api/model-selector/costs` | GET | Cost & token tracking |
| `/api/model-selector/profiles` | GET | All task profiles |
| `/api/model-selector/record-cost` | POST | Log token usage |
| `/health` | GET | Service health check |

**Query Parameters** for `/select`:
- `taskType` — `coding`, `creative`, `research`, `fast`, `jobMatching`
- `maxContextWindow` — Optional max context size

**Query Parameters** for `/compare`:
- `models` — Comma-separated model IDs (e.g., `local-claude-code,local-fast`)

---

### Hub AI Local (Port 8889)

| Path | Purpose |
|------|---------|
| `/hub` | Visual dashboard with all services |
| `/health` | Health status |
| `/api/orchestrator/*` | Proxy to orchestrator |
| `/api/model-selector/*` | Proxy to model selector |

---

## Models Available

### Local Models (Cost: $0)
- `local-claude-code` — Coding (reasoning, context: 32K)
- `local-coder-ollama` — Coding fast (qwen2.5-coder:7b)
- `local-llama:3b` — General lightweight
- `local-reason` — Research/analysis (reasoning, context: 32K)
- `local-big` — Creative writing (context: 16K)
- `local-fast` — Quick responses
- `ruflow-semantic-scorer` — Resume-job matching

### Task Profiles

| Task | Primary | Secondary | Fallback |
|------|---------|-----------|----------|
| **coding** | local-claude-code | local-coder-ollama | ollama-qwen:7b |
| **creative** | local-big | ollama-llama:3b | local-fast |
| **research** | local-reason | local-big | ollama-llama:3b |
| **fast** | ollama-llama:3b | local-fast | ollama-qwen:3b |
| **jobMatching** | ruflow-semantic-scorer | local-reason | ollama-llama:3b |

---

## Example Workflows

### Workflow 1: Code Refactoring
```bash
# User: "Refactor this function for performance"
curl "http://localhost:9500/api/orchestrator/model-select?context=refactor%20function&taskType=coding"

# Response:
# {
#   "tool": "openclaw",
#   "model": "local-claude-code",
#   "fallbackChain": ["local-claude-code", "local-coder-ollama", "qwen:7b"]
# }

# Execute through selected tool
curl -X POST "http://localhost:9500/api/orchestrator/execute" \
  -H "Content-Type: application/json" \
  -d '{"input": "Refactor this function", "taskType": "coding"}'
```

### Workflow 2: Data Analysis
```bash
curl "http://localhost:9500/api/orchestrator/model-select?context=analyze%20dataset&taskType=research"

# Response:
# {
#   "tool": "sinkia-ops",
#   "model": "local-reason",
#   "confidence": 0.9
# }
```

### Workflow 3: Get Model Recommendation
```bash
curl "http://localhost:9501/api/model-selector/select?taskType=coding"

# Response shows primary + fallback models
```

---

## Troubleshooting

### Orchestrator not responding
```bash
# Check if running
ps aux | grep synk-ia-orchestrator

# Check logs
curl http://localhost:9500/health

# Restart
pkill -f synk-ia-orchestrator
node /Users/davidnows/synk-ia-orchestrator.js &
```

### Model Selector not responding
```bash
ps aux | grep synk-ia-model-selector
curl http://localhost:9501/health
pkill -f synk-ia-model-selector
node /Users/davidnows/synk-ia-model-selector.js &
```

### Services showing offline
- OpenClaw: Not in docker-compose.synkia-os.yml (add to docker-compose)
- RuFlow: Not started (needs separate docker-compose.yml)
- Hermes: Not in Docker network (configure Docker bridge)

---

## Performance Metrics

Check unified memory for accumulated learning:
```bash
cat ~/.synkia-ai-hub/unified-memory.json | jq '.performance'
```

Shows:
- Executions per tool
- Success rates
- Average latency

---

## Next Improvements

- [ ] Deploy on PM2 for auto-restart
- [ ] Update Hub to v2.0
- [ ] Add OpenClaw to Docker network
- [ ] Integrate RuFlow job-matching
- [ ] Set up Hermes task queue
- [ ] Enable GitHub discovery auto-updates

---

**Last Updated**: 2026-08-03  
**Status**: ✅ Operational  
**Ecosystem**: 🎯 Unified
