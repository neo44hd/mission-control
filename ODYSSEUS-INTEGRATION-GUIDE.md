# Odysseus Integration Guide — Journey Management for SYNK-OPS

## Overview

**Odysseus** es un maestro orquestador integrado en SYNK-OPS que proporciona:

- 🗺️ **Journey Management** — Visualización y ejecución de viajes de tareas
- 📋 **Task Orchestration** — Coordinación automática de tareas complejas
- 🔄 **Dependency Resolution** — Resolución inteligente de dependencias
- 🎯 **Intelligent Routing** — Enrutamiento automático al servicio correcto
- 🧠 **Model Selection** — Selección de modelo óptimo por tarea
- 📊 **Status Monitoring** — Monitoreo de estado de journeys en tiempo real

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                   TU APLICACIÓN                               │
│           (Define journeys y tasks)                           │
└──────────────────┬───────────────────────────────────────────┘
                   │
                   │ HTTP Request
                   ▼
┌──────────────────────────────────────────────────────────────┐
│    ODYSSEUS INTEGRATION BRIDGE (Puerto 9999)                 │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Journey API:                                           │  │
│  │ - POST   /api/journeys                (Create journey) │  │
│  │ - GET    /api/journeys/{id}           (Get journey)    │  │
│  │ - POST   /api/journeys/{id}/tasks     (Add task)       │  │
│  │ - POST   /api/journeys/{id}/execute   (Execute all)    │  │
│  │ - GET    /api/odysseus/status         (Status)         │  │
│  │ - GET    /health                      (Health check)   │  │
│  └────────────────────────────────────────────────────────┘  │
└──────┬──────────────────────────┬──────────────────────┬─────┘
       │                          │                      │
       ▼                          ▼                      ▼
┌─────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ ODYSSEUS        │  │ SYNK-IA          │  │ SYNK-IA          │
│ (7000 internal) │  │ Orchestrator     │  │ Model Selector   │
│                 │  │ (9500)           │  │ (9501)           │
│ - Sessions      │  │ - Route requests │  │ - Select models  │
│ - Tasks         │  │ - Execute tasks  │  │ - Fallback chains│
│ - Memory        │  │ - Health monitor │  │ - Cost tracking  │
│ - RAG           │  │                  │  │                  │
└─────────────────┘  └──────────────────┘  └──────────────────┘
       │                          │                      │
       └──────────────┬───────────┴──────────────────────┘
                      │
       ┌──────────────┼──────────────┐
       │              │              │
       ▼              ▼              ▼
    OpenClaw    SynK-IA-Ops    Hub AI Local
  (Agent MCP)  (API Gateway)   (Dashboard)
       │              │              │
       └──────────────┼──────────────┘
                      │
       ┌──────────────┼──────────────────┬──────────────┐
       │              │                  │              │
       ▼              ▼                  ▼              ▼
     n8n         Qdrant          OpenWebUI         RuFlow
  (Workflow)  (Vectors)      (Chat Interface)  (Job Matching)
```

---

## Quick Start

### 1. **Start Odysseus Container**

```bash
docker-compose -f docker-compose.synkia-os.yml up -d odysseus
```

Verify it's running:
```bash
docker ps | grep odysseus
curl http://localhost:9999/health
```

### 2. **Create a Journey**

```bash
curl -X POST http://localhost:9999/api/journeys \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Code Refactoring Journey",
    "description": "Refactor authentication module with testing",
    "steps": [
      "Review current implementation",
      "Identify improvements",
      "Implement changes",
      "Write unit tests",
      "Run tests"
    ]
  }'
```

Response:
```json
{
  "id": "journey-1722708180000",
  "name": "Code Refactoring Journey",
  "description": "Refactor authentication module with testing",
  "status": "planning",
  "tasks": [],
  "metrics": {
    "totalTasks": 0,
    "completedTasks": 0,
    "failedTasks": 0,
    "totalDuration": 0
  }
}
```

### 3. **Add Tasks to Journey**

```bash
# Task 1: Review implementation
curl -X POST http://localhost:9999/api/journeys/journey-1722708180000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Review the current authentication implementation and identify code quality issues",
    "dependencies": []
  }'

# Task 2: Refactor (depends on Task 1)
curl -X POST http://localhost:9999/api/journeys/journey-1722708180000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Refactor the authentication module to improve code quality and use async-await",
    "dependencies": ["task-1"]
  }'

# Task 3: Write tests (depends on Task 2)
curl -X POST http://localhost:9999/api/journeys/journey-1722708180000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Write comprehensive unit tests for the refactored authentication module",
    "dependencies": ["task-2"]
  }'
```

### 4. **Execute Journey**

```bash
curl -X POST http://localhost:9999/api/journeys/journey-1722708180000/execute
```

The journey will:
1. ✅ Detect context for each task (coding → sends to OpenClaw)
2. ✅ Select optimal model (local-claude-code for coding tasks)
3. ✅ Respect dependency order (Task 2 waits for Task 1 to complete)
4. ✅ Route to correct service automatically
5. ✅ Track execution metrics

### 5. **Monitor Journey Status**

```bash
curl http://localhost:9999/api/journeys/journey-1722708180000
```

Response:
```json
{
  "id": "journey-1722708180000",
  "name": "Code Refactoring Journey",
  "status": "completed",
  "tasks": [
    {
      "id": "task-1",
      "description": "Review the current authentication implementation...",
      "status": "completed",
      "assignedTool": "openclaw",
      "selectedModel": "local-claude-code",
      "result": "Found 3 issues: unsafe string concatenation, missing error handling, missing async/await"
    },
    {
      "id": "task-2",
      "description": "Refactor the authentication module...",
      "status": "completed",
      "dependencies": ["task-1"],
      "assignedTool": "openclaw",
      "selectedModel": "local-claude-code",
      "result": "Refactored authentication module with proper async-await and error handling"
    },
    {
      "id": "task-3",
      "description": "Write comprehensive unit tests...",
      "status": "completed",
      "dependencies": ["task-2"],
      "assignedTool": "openclaw",
      "selectedModel": "local-claude-code",
      "result": "Created 12 unit tests with 98% code coverage"
    }
  ],
  "metrics": {
    "totalTasks": 3,
    "completedTasks": 3,
    "failedTasks": 0,
    "totalDuration": 145.23
  }
}
```

---

## Journey API Reference

### **POST /api/journeys** — Create a Journey

Creates a new journey (sequence of coordinated tasks).

**Request:**
```bash
curl -X POST http://localhost:9999/api/journeys \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Journey Name",
    "description": "Journey description",
    "steps": ["step1", "step2", "step3"]
  }'
```

**Response:** `201 Created`
```json
{
  "id": "journey-1722708180000",
  "name": "Journey Name",
  "description": "Journey description",
  "status": "planning",
  "createdAt": "2026-08-03T23:30:00.000Z",
  "tasks": [],
  "metrics": { }
}
```

**Status codes:**
- `201` — Journey created successfully
- `400` — Invalid request body
- `500` — Server error

---

### **GET /api/journeys/{journeyId}** — Get Journey Status

Retrieves detailed status of a specific journey.

**Request:**
```bash
curl http://localhost:9999/api/journeys/journey-1722708180000
```

**Response:** `200 OK`
```json
{
  "id": "journey-1722708180000",
  "name": "Code Refactoring Journey",
  "status": "executing",
  "startedAt": "2026-08-03T23:31:00.000Z",
  "tasks": [ ... ],
  "metrics": {
    "totalTasks": 3,
    "completedTasks": 1,
    "failedTasks": 0,
    "totalDuration": 45.5
  }
}
```

**Status values:**
- `planning` — Journey created, awaiting tasks
- `executing` — Journey is running
- `completed` — All tasks finished
- `failed` — One or more tasks failed

---

### **POST /api/journeys/{journeyId}/tasks** — Add Task to Journey

Adds a new task to an existing journey.

**Request:**
```bash
curl -X POST http://localhost:9999/api/journeys/journey-1722708180000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "description": "What the task should do",
    "dependencies": []  # IDs of tasks this depends on
  }'
```

**Response:** `201 Created`
```json
{
  "id": "task-1",
  "description": "What the task should do",
  "dependencies": [],
  "status": "pending",
  "assignedTool": null,
  "selectedModel": null
}
```

**Dependency Resolution:**
- If task has dependencies, it won't execute until those tasks complete
- Dependencies are task IDs (e.g., "task-1", "task-2")

Example with dependencies:
```bash
curl -X POST http://localhost:9999/api/journeys/journey-1722708180000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Test the refactored code",
    "dependencies": ["task-2"]  # Won't run until task-2 completes
  }'
```

---

### **POST /api/journeys/{journeyId}/execute** — Execute Journey

Starts execution of all tasks in the journey, respecting dependencies.

**Request:**
```bash
curl -X POST http://localhost:9999/api/journeys/journey-1722708180000/execute
```

**Response:** `200 OK`
```json
{
  "id": "journey-1722708180000",
  "status": "executing",
  "startedAt": "2026-08-03T23:32:00.000Z",
  "tasks": [
    {
      "id": "task-1",
      "status": "executing",
      "assignedTool": "openclaw",
      "selectedModel": "local-claude-code"
    }
  ]
}
```

**Execution flow:**
1. Journey status → `executing`
2. For each task (in dependency order):
   - Detect context (coding, research, creative, etc.)
   - Select optimal model via SYNK-IA Model Selector
   - Route to correct service (OpenClaw, SynK-IA-Ops, etc.)
   - Execute and record result
3. Task status → `completed` or `failed`
4. Journey status → `completed`

---

### **GET /api/journeys** — List All Journeys

Lists all journeys (active and completed).

**Request:**
```bash
curl http://localhost:9999/api/journeys
```

**Response:** `200 OK`
```json
{
  "journeys": [
    {
      "id": "journey-1722708180000",
      "name": "Code Refactoring Journey",
      "status": "completed",
      "tasks": [...],
      "metrics": { }
    },
    {
      "id": "journey-1722708190000",
      "name": "Research Investigation",
      "status": "executing",
      "tasks": [...],
      "metrics": { }
    }
  ]
}
```

---

### **GET /api/odysseus/status** — Odysseus Status

Detailed status of Odysseus integration.

**Request:**
```bash
curl http://localhost:9999/api/odysseus/status
```

**Response:** `200 OK`
```json
{
  "odysseus": {
    "status": "healthy",
    "data": { ... }
  },
  "journeys": {
    "total": 5,
    "active": 1,
    "completed": 4
  },
  "timestamp": "2026-08-03T23:35:00.000Z"
}
```

---

### **GET /health** — Health Check

Overall system health including Odysseus, SYNK-IA Orchestrator, and bridge.

**Request:**
```bash
curl http://localhost:9999/health
```

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "timestamp": "2026-08-03T23:35:00.000Z",
  "odysseus": {
    "status": "healthy",
    "data": { }
  },
  "synkia": "operational",
  "bridge": "operational"
}
```

---

## Task Context Detection

When a task is executed, Odysseus automatically detects the context and selects the best model:

### **Context Types:**

| Context | Keywords | Tool | Model |
|---------|----------|------|-------|
| **coding** | code, refactor, debug, function, class, optimize | OpenClaw | local-claude-code |
| **research** | research, analyze, investigate, deep-dive, search | SynK-IA-Ops | local-reason |
| **creative** | write, create, generate, brainstorm | OpenWebUI | local-big |
| **general** | other | Hub AI Local | local-fast |

### **Example: Automatic Model Selection**

```bash
# Task with "refactor" keyword
{
  "description": "Refactor this authentication function"
}
# → Detected: context = "coding"
# → Selected: model = "local-claude-code"
# → Routed: tool = "openclaw"

# Task with "analyze" keyword
{
  "description": "Analyze the impact of this change"
}
# → Detected: context = "research"
# → Selected: model = "local-reason"
# → Routed: tool = "sinkia-ops"
```

---

## Dependency Management

### **Linear Dependencies**

```
Task 1 → Task 2 → Task 3 → Task 4
```

```bash
# Task 1: No dependencies
{
  "description": "Step 1",
  "dependencies": []
}

# Task 2: Depends on Task 1
{
  "description": "Step 2",
  "dependencies": ["task-1"]
}

# Task 3: Depends on Task 2
{
  "description": "Step 3",
  "dependencies": ["task-2"]
}
```

### **Parallel Dependencies**

```
    Task 1
   /      \
Task 2    Task 3
   \      /
    Task 4
```

```bash
# Task 1: No dependencies
{ "description": "Setup", "dependencies": [] }

# Task 2: After Task 1
{ "description": "Part A", "dependencies": ["task-1"] }

# Task 3: After Task 1 (parallel to Task 2)
{ "description": "Part B", "dependencies": ["task-1"] }

# Task 4: After both Task 2 AND Task 3
{ "description": "Merge results", "dependencies": ["task-2", "task-3"] }
```

When task 4 executes, Odysseus waits until BOTH task-2 AND task-3 are completed.

---

## Execution Metrics

Each journey tracks detailed metrics:

```json
{
  "metrics": {
    "totalTasks": 5,           // Total tasks in journey
    "completedTasks": 4,       // Successfully completed
    "failedTasks": 1,          // Failed execution
    "totalDuration": 287.5     // Total time (seconds)
  }
}
```

Each task also tracks:

```json
{
  "id": "task-1",
  "description": "...",
  "status": "completed",
  "createdAt": "2026-08-03T23:31:00.000Z",
  "startedAt": "2026-08-03T23:31:05.000Z",
  "completedAt": "2026-08-03T23:31:42.000Z",
  "assignedTool": "openclaw",           // Which tool executed it
  "selectedModel": "local-claude-code", // Which model was used
  "result": "Task result/output"        // The actual result
}
```

---

## Real-World Example: Complex Project

### **Journey: Multi-Service API Development**

```bash
# 1. Create journey
J_ID=$(curl -s -X POST http://localhost:9999/api/journeys \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Full-Stack API Development",
    "description": "Develop, test, and deploy new API"
  }' | jq -r '.id')

# 2. Add tasks with dependencies
# Task 1: Design API
curl -X POST http://localhost:9999/api/journeys/$J_ID/tasks \
  -d '{"description": "Design REST API endpoints and database schema", "dependencies": []}'
# → Routed to: sinkia-ops, Model: local-reason

# Task 2: Implement API (depends on design)
curl -X POST http://localhost:9999/api/journeys/$J_ID/tasks \
  -d '{"description": "Implement the API endpoints in Node.js", "dependencies": ["task-1"]}'
# → Routed to: openclaw, Model: local-claude-code

# Task 3: Write tests (depends on implementation)
curl -X POST http://localhost:9999/api/journeys/$J_ID/tasks \
  -d '{"description": "Write comprehensive unit tests for the API", "dependencies": ["task-2"]}'
# → Routed to: openclaw, Model: local-claude-code

# Task 4: Create documentation (can run in parallel)
curl -X POST http://localhost:9999/api/journeys/$J_ID/tasks \
  -d '{"description": "Generate API documentation and examples", "dependencies": ["task-2"]}'
# → Routed to: openclaw, Model: local-big

# Task 5: Deploy (depends on all)
curl -X POST http://localhost:9999/api/journeys/$J_ID/tasks \
  -d '{"description": "Deploy API to production", "dependencies": ["task-3", "task-4"]}'
# → Routed to: n8n, Model: local-fast

# 3. Execute journey
curl -X POST http://localhost:9999/api/journeys/$J_ID/execute

# 4. Monitor progress
watch -n 2 "curl -s http://localhost:9999/api/journeys/$J_ID | jq '.metrics'"
```

---

## Integration with SYNK-IA Components

### **OpenClaw (Agent MCP)**

When Odysseus routes to OpenClaw:
```json
{
  "routed_to": "openclaw",
  "endpoint": "http://localhost:7999/api/execute",
  "model": "local-claude-code",
  "context": "coding"
}
```

OpenClaw executes the task with MCP protocol, enabling autonomous agents.

### **SynK-IA-Ops (API Gateway)**

When Odysseus routes to SynK-IA-Ops:
```json
{
  "routed_to": "sinkia-ops",
  "endpoint": "http://localhost:3001/api/execute",
  "model": "local-reason",
  "context": "research"
}
```

SynK-IA-Ops handles complex analysis and research tasks with reasoning models.

### **Model Fallback Chains**

If the primary model isn't available:
```
local-claude-code (primary)
    ↓ (if unavailable)
local-coder-ollama (secondary)
    ↓ (if unavailable)
llama:3b (fallback)
```

---

## Troubleshooting

### **Journey not executing**

```bash
# Check if Odysseus is healthy
curl http://localhost:9999/health

# Check SYNK-IA Orchestrator
curl http://localhost:9500/api/orchestrator/status

# Check SYNK-IA Model Selector
curl http://localhost:9501/api/model-selector/models
```

### **Task staying in "pending"**

This usually means dependencies aren't satisfied:

```bash
# Check the journey status
curl http://localhost:9999/api/journeys/journey-id | jq '.tasks[] | {id, status, dependencies}'

# Make sure dependent tasks are completed
curl http://localhost:9999/api/journeys/journey-id | jq '.tasks[] | select(.id == "task-2") | .status'
```

### **Model not available**

```bash
# Check available models
curl http://localhost:9501/api/model-selector/models

# Check if local models are running
ollama ps
```

### **View execution logs**

```bash
tail -f odysseus-integration.log
```

---

## Advanced Usage

### **Programmatic Journey Creation**

```javascript
const axios = require('axios');

async function runJourney() {
  const baseURL = 'http://localhost:9999';
  
  // Create journey
  const journey = await axios.post(`${baseURL}/api/journeys`, {
    name: 'Automated Analysis',
    description: 'Run analysis and generate report'
  });
  
  const journeyId = journey.data.id;
  
  // Add tasks
  const task1 = await axios.post(
    `${baseURL}/api/journeys/${journeyId}/tasks`,
    { description: 'Collect data', dependencies: [] }
  );
  
  const task2 = await axios.post(
    `${baseURL}/api/journeys/${journeyId}/tasks`,
    {
      description: 'Analyze data',
      dependencies: [task1.data.id]
    }
  );
  
  // Execute
  const result = await axios.post(
    `${baseURL}/api/journeys/${journeyId}/execute`
  );
  
  console.log('Journey completed:', result.data.metrics);
}

runJourney().catch(console.error);
```

---

## Summary

**Odysseus** provides a unified journey management system that:

✅ Automatically detects task context
✅ Selects optimal models intelligently
✅ Routes to correct services (OpenClaw, SynK-IA-Ops, etc.)
✅ Respects task dependencies
✅ Tracks execution metrics
✅ Provides REST API for integration
✅ Monitors system health in real-time

**Use Odysseus when you need** coordinated execution of multiple complex tasks across your entire SYNK-IA ecosystem.
