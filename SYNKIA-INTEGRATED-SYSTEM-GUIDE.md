# 🦇 SYNK-IA Integrated System - Complete Guide

**Status**: ✅ **FULLY INTEGRATED & READY**  
**Date**: July 9, 2026  
**Architecture**: Ecosystem Agent + Search & Discovery Platform  

---

## 🚀 Quick Start (30 seconds)

### Start Everything
```bash
/Users/davidnows/Agentes-Pro/start-integrated-system.sh
```

You'll see both services start:
- 🦇 Ecosystem Agent (port 8009)
- 🔍 Search & Discovery Platform (port 8012)
- 📊 Master Dashboard (port 8010)

---

## 📡 System Architecture

```
┌─────────────────────────────────────────────────┐
│        Master Dashboard (Port 8010)             │
│    http://localhost:8010/master-panel-v2.html   │
└──────────────────┬──────────────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
   ┌────▼─────┐        ┌─────▼────┐
   │Ecosystem │        │  Search  │
   │ Agent    │        │Discovery │
   │ :8009    │        │  :8012   │
   └────┬─────┘        └─────┬────┘
        │                    │
     ┌──▼────────────────────▼──┐
     │   Providers (11 Free)     │
     │   Models (100+)           │
     │   Health Monitoring       │
     │   Analytics               │
     └───────────────────────────┘
```

---

## 🎯 System Components

### 1. **Ecosystem Agent** (Port 8009)
**Purpose**: Monitor and manage the entire ecosystem

**Key Endpoints**:
- `GET /health` - Agent health check
- `GET /ecosystem/status` - Complete ecosystem status
- `GET /ecosystem/providers` - All 11 providers health
- `GET /ecosystem/metrics` - System CPU/RAM/Disk metrics
- `GET /recommendations` - Auto-discovery recommendations
- `POST /ecosystem/update` - Trigger manual update

**Features**:
- ✅ Real-time provider health checks
- ✅ System resource monitoring (CPU, RAM, disk)
- ✅ Automatic discovery of new models/tools
- ✅ Uptime tracking and statistics
- ✅ Background task scheduling

**Example Usage**:
```bash
# Check ecosystem status
curl http://localhost:8009/ecosystem/status | jq

# Check providers
curl http://localhost:8009/ecosystem/providers | jq

# View metrics
curl http://localhost:8009/ecosystem/metrics | jq
```

---

### 2. **Search & Discovery Platform** (Port 8012)
**Purpose**: Advanced search, discovery, and analytics

**Key Endpoints**:

#### Search
- `GET /api/search?q=llama` - Unified search
- `GET /api/search/models` - List all models
- `GET /api/search/providers` - List all providers  
- `GET /api/search/tools` - List all tools

#### Monitoring
- `GET /api/monitor/health` - Ecosystem health
- `GET /api/monitor/providers` - Provider status
- `GET /api/monitor/metrics` - System metrics
- `GET /api/monitor/history/{provider}` - Health history

#### Analytics
- `GET /api/analytics` - Complete analytics
- `GET /api/analytics/usage` - Usage statistics
- `GET /api/analytics/trends` - Performance trends
- `GET /api/analytics/costs` - Cost analysis

#### Recommendations
- `GET /api/recommendations` - Smart recommendations
- `GET /api/recommendations/providers` - Provider suggestions
- `GET /api/recommendations/models` - Model alternatives

#### Installation
- `POST /api/install/tool` - Install tools automatically

#### WebSocket (Real-time)
- `ws://localhost:8012/ws/monitor` - Live health updates
- `ws://localhost:8012/ws/discover` - Discovery feed

**API Documentation**:
- Auto-generated Swagger UI: http://localhost:8012/api/docs
- ReDoc: http://localhost:8012/api/redoc
- OpenAPI JSON: http://localhost:8012/api/openapi.json

**Example Usage**:
```bash
# Search for models
curl http://localhost:8012/api/search?q=llama&type=model | jq

# Get ecosystem health
curl http://localhost:8012/api/monitor/health | jq

# Get recommendations
curl http://localhost:8012/api/recommendations | jq

# Get analytics
curl http://localhost:8012/api/analytics | jq
```

---

## 📁 Project Structure

```
/Users/davidnows/Agentes-Pro/
├── start-integrated-system.sh         ← Main startup script
├── test-integration.sh                ← Test both services
│
├── ecosystem-agent/
│   ├── main.py                        ← FastAPI server (8009)
│   ├── health_checker.py              ← Provider health checks
│   ├── metrics.py                     ← System metrics collection
│   ├── scheduler.py                   ← Background task manager
│   ├── config.yaml                    ← Configuration
│   └── requirements.txt               ← Dependencies
│
├── search-discovery-platform/
│   ├── backend/
│   │   ├── main.py                    ← FastAPI server (8012)
│   │   ├── database.py                ← SQLite models
│   │   ├── schemas.py                 ← Pydantic schemas
│   │   ├── routers/
│   │   │   ├── search.py              ← Unified search
│   │   │   ├── recommendations.py     ← Recommendations
│   │   │   ├── monitoring.py          ← Health monitoring
│   │   │   ├── installation.py        ← Tool installation
│   │   │   ├── analytics.py           ← Analytics
│   │   │   └── websocket.py           ← Real-time updates
│   │   ├── services/
│   │   │   ├── provider_monitor.py    ← Provider health checks
│   │   │   └── github_crawler.py      ← GitHub discovery
│   │   ├── tasks/
│   │   │   └── scheduled_tasks.py     ← Background jobs
│   │   └── utils/
│   │       └── logger.py              ← Logging setup
│   └── README.md
│
├── venv/                              ← Python environment
├── litellm/                           ← LiteLLM configuration
├── .env                               ← Environment variables
│
└── master-panel-v2.html               ← Web dashboard
```

---

## 🔄 Integration Flow

```
User Request
    ↓
Dashboard (Port 8010)
    ↓
├─→ Search & Discovery Platform (8012)
│   ├─→ Search API
│   ├─→ Analytics API
│   ├─→ Monitoring API
│   └─→ WebSocket (real-time)
│
└─→ Ecosystem Agent (8009)
    ├─→ Provider Health Checks
    ├─→ System Metrics
    ├─→ Discovery Engine
    └─→ Recommendations

Database (SQLite)
├─→ Models, Providers, Tools
├─→ Health History
├─→ Recommendations
└─→ Analytics
```

---

## 📊 Monitoring Dashboard Ports

| Port | Service | URL | Purpose |
|------|---------|-----|---------|
| 8009 | Ecosystem Agent | http://localhost:8009/health | Ecosystem monitoring |
| 8010 | Master Dashboard | http://localhost:8010/master-panel-v2.html | Web UI |
| 8012 | Search & Discovery | http://localhost:8012/api/docs | API server |

---

## 🧪 Testing the Integration

### Quick Test
```bash
/Users/davidnows/Agentes-Pro/test-integration.sh
```

### Manual Tests

**Test Ecosystem Agent:**
```bash
# Health check
curl http://localhost:8009/health

# Get all providers
curl http://localhost:8009/ecosystem/providers

# Get metrics
curl http://localhost:8009/ecosystem/metrics
```

**Test Search & Discovery:**
```bash
# Search for models
curl "http://localhost:8012/api/search?q=llama&type=model"

# Get ecosystem health
curl http://localhost:8012/api/monitor/health

# Get analytics
curl http://localhost:8012/api/analytics

# Access documentation
open http://localhost:8012/api/docs
```

---

## 📈 Available Data

### Models (100+)
- Groq, Completions.me, Together.ai, ZeroLimitAI, BazaarLink
- Free.ai, LLM.kiwi, Requesty, AINative, ZeroCost, HuggingFace
- NVIDIA NIM (18 models)
- Local: Ollama, LM Studio

### Providers (11 Free)
- All monitored 24/7
- Uptime tracking
- Latency measurement
- Auto-failover support

### Capabilities
- ✅ Real-time health monitoring
- ✅ Performance analytics
- ✅ Cost analysis
- ✅ Discovery recommendations
- ✅ One-click installations
- ✅ WebSocket real-time updates

---

## 🔧 Configuration

### Environment Variables
```bash
# Optional GitHub token for discovery
export GITHUB_TOKEN="your_token_here"

# Optional API keys
export GROQ_API_KEY="..."
export TOGETHER_API_KEY="..."
# ... more keys in /Users/davidnows/FREE-PROVIDERS-API-SETUP.md
```

### Main Configuration
```bash
# Ecosystem Agent
/Users/davidnows/Agentes-Pro/ecosystem-agent/config.yaml

# LiteLLM
/Users/davidnows/Agentes-Pro/litellm/config.yaml
```

---

## 📊 Database Schema

### SQLite Database Location
```
/Users/davidnows/.synkia/data/synkia.db
```

### Main Tables
- **models** - LLM models (100+)
- **providers** - API providers (11)
- **tools** - Tools & frameworks
- **health_history** - Provider health time-series
- **recommendations** - Auto-generated recommendations
- **benchmarks** - Performance benchmarks

---

## 📋 API Response Examples

### Search Response
```json
{
  "models": [
    {
      "id": 1,
      "name": "groq-mixtral-8x7b",
      "provider": "groq",
      "type": "text",
      "latency_ms": 150,
      "rating": 4.8
    }
  ],
  "providers": [],
  "tools": [],
  "total": 1
}
```

### Ecosystem Health Response
```json
{
  "timestamp": "2026-07-09T12:39:10Z",
  "overall_status": "healthy",
  "providers": [
    {
      "provider_name": "groq",
      "status": "healthy",
      "latency_ms": 145,
      "uptime_percent": 99.8,
      "last_check": "2026-07-09T12:39:10Z"
    }
  ],
  "total_models": 100,
  "healthy_providers": 11,
  "uptime_percent": 99.8
}
```

### Analytics Response
```json
{
  "total_models": 100,
  "total_providers": 11,
  "total_tools": 30,
  "total_recommendations": 5,
  "provider_stats": {...},
  "model_stats": {...}
}
```

---

## 🚨 Logs & Monitoring

### Log Files
```bash
# Ecosystem Agent logs
tail -f /Users/davidnows/.synkia/logs/ecosystem-agent.log

# Search & Discovery logs
tail -f /Users/davidnows/.synkia/logs/search-discovery.log

# Combined logs
tail -f /Users/davidnows/.synkia/logs/synkia.log
```

### Process Management
```bash
# Check if services are running
ps aux | grep python

# Check open ports
lsof -i :8009  # Ecosystem Agent
lsof -i :8012  # Search & Discovery

# Kill services (if needed)
pkill -f "python.*main.py"
```

---

## 🔄 Workflow Examples

### Example 1: Find Best Model for Task
```bash
# Search for fast inference models
curl "http://localhost:8012/api/search?q=fast%20inference&type=model" | jq

# Get recommendations
curl http://localhost:8012/api/recommendations/models | jq

# Check health and latency
curl http://localhost:8012/api/monitor/providers | jq '.[] | {name, status, latency_ms}'
```

### Example 2: Monitor System Health
```bash
# Get complete ecosystem status
curl http://localhost:8009/ecosystem/status | jq

# Check system resources
curl http://localhost:8009/ecosystem/metrics | jq

# Get provider history
curl http://localhost:8012/api/monitor/history/groq | jq
```

### Example 3: Discover New Tools
```bash
# Get current recommendations
curl http://localhost:8012/api/recommendations | jq '.[] | {type, title, impact}'

# Watch discovery feed (WebSocket)
# ws://localhost:8012/ws/discover
```

---

## 🎓 Next Steps

1. **Access Dashboard**
   - Open: http://localhost:8010/master-panel-v2.html
   - View all models and providers

2. **Configure API Keys**
   - Read: `/Users/davidnows/FREE-PROVIDERS-API-SETUP.md`
   - Export environment variables

3. **Explore APIs**
   - API Docs: http://localhost:8012/api/docs
   - Try endpoints in Swagger UI

4. **Monitor Health**
   - Check: http://localhost:8009/health
   - Monitor: http://localhost:8012/api/monitor/health

5. **Build Integrations**
   - Use search API for querying
   - Subscribe to WebSocket for real-time updates
   - Leverage analytics for insights

---

## 🆘 Troubleshooting

### Services Not Starting
```bash
# Check if ports are in use
lsof -i :8009
lsof -i :8012

# Kill existing processes
pkill -f "python.*main.py"

# Try again
/Users/davidnows/Agentes-Pro/start-integrated-system.sh
```

### Database Issues
```bash
# Reset database
rm /Users/davidnows/.synkia/data/synkia.db
# Database will be recreated on next startup
```

### Logs Show Errors
```bash
# Check ecosystem logs
tail -50 /Users/davidnows/.synkia/logs/ecosystem-agent.log

# Check discovery logs
tail -50 /Users/davidnows/.synkia/logs/search-discovery.log
```

### API Returns 500 Error
```bash
# Ensure database exists
ls -la /Users/davidnows/.synkia/data/

# Check logs for specific errors
grep ERROR /Users/davidnows/.synkia/logs/synkia.log
```

---

## 📞 Support & Documentation

| Resource | Location |
|----------|----------|
| Quick Start | This file |
| API Docs | http://localhost:8012/api/docs |
| Setup Guide | /Users/davidnows/FREE-PROVIDERS-API-SETUP.md |
| System Overview | /Users/davidnows/SYNKIA-COMPLETE-DELIVERABLES.md |
| GitHub Discoveries | /Users/davidnows/GITHUB-DISCOVERIES-SYNKIA.md |

---

## ✨ Key Features Deployed

### Real-time Monitoring
✅ Health checks every 5 minutes  
✅ Provider latency tracking  
✅ Uptime statistics  
✅ System metrics (CPU, RAM, disk)  

### Smart Discovery
✅ Auto-find new LLM models  
✅ Discover trending tools  
✅ Benchmark comparisons  
✅ Cost analysis  

### Powerful Search
✅ Full-text search  
✅ Multi-type filtering  
✅ Pagination support  
✅ Fast response (<100ms)  

### Analytics & Insights
✅ Usage statistics  
✅ Performance trends  
✅ Cost analysis  
✅ Provider reliability metrics  

### One-Click Operations
✅ Install tools  
✅ Update configurations  
✅ Auto-restart services  
✅ Verify installations  

---

## 🎉 Status

| Component | Status | Port |
|-----------|--------|------|
| Ecosystem Agent | ✅ Running | 8009 |
| Search & Discovery | ✅ Running | 8012 |
| Master Dashboard | ✅ Running | 8010 |
| Database | ✅ Initialized | Local SQLite |
| API Documentation | ✅ Available | /api/docs |
| WebSocket | ✅ Enabled | /ws/monitor |

---

## 🚀 Ready to Use!

Everything is configured and ready to go. Start the system with:

```bash
/Users/davidnows/Agentes-Pro/start-integrated-system.sh
```

Then access:
- **Dashboard**: http://localhost:8010/master-panel-v2.html
- **API Docs**: http://localhost:8012/api/docs
- **Agent Health**: http://localhost:8009/health

---

**Built with ❤️ for SYNK-IA Ecosystem**  
*Last Updated: July 9, 2026*
