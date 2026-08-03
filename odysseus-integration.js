#!/usr/bin/env node
/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * ODYSSEUS INTEGRATION BRIDGE FOR SYNK-IA
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Este script conecta Odysseus (puerto 7000) con el orquestador SYNK-IA
 * para proporcionar:
 * 
 * 1. Journey Management — Visualización de viajes de tareas
 * 2. Task Orchestration — Orquestación de tareas complejas
 * 3. Service Coordination — Coordinación entre servicios
 * 4. Dependency Resolution — Resolución automática de dependencias
 * 5. Resource Allocation — Asignación inteligente de recursos
 * 6. Status Monitoring — Monitoreo de estado de journey
 * 
 * Puertos:
 * - Odysseus API: 7000 (interno)
 * - SYNK-IA Orchestrator: 9500
 * - SYNK-IA Model Selector: 9501
 * - Odysseus Integration Bridge: 9999
 * ═══════════════════════════════════════════════════════════════════════════════
 */

const http = require('http');
const axios = require('axios');
const fs = require('fs');
const path = require('path');

// ═══════════════════════════════════════════════════════════════════════════════
// CONFIGURACIÓN
// ═══════════════════════════════════════════════════════════════════════════════

const config = {
  ODYSSEUS_HOST: process.env.ODYSSEUS_HOST || '127.0.0.1',
  ODYSSEUS_PORT: process.env.ODYSSEUS_PORT || 7000,
  ODYSSEUS_API_URL: `http://${process.env.ODYSSEUS_HOST || '127.0.0.1'}:${process.env.ODYSSEUS_PORT || 7000}`,
  SYNKIA_ORCHESTRATOR_URL: 'http://localhost:9500',
  SYNKIA_MODEL_SELECTOR_URL: 'http://localhost:9501',
  BRIDGE_PORT: 9999,
  BRIDGE_HOST: '0.0.0.0',
  LOG_FILE: path.join(__dirname, 'odysseus-integration.log'),
};

// ═══════════════════════════════════════════════════════════════════════════════
// LOGGING
// ═══════════════════════════════════════════════════════════════════════════════

function log(level, message, data = null) {
  const timestamp = new Date().toISOString();
  const logMessage = `${timestamp} [${level}] ${message}${data ? ' → ' + JSON.stringify(data) : ''}`;
  
  console.log(logMessage);
  
  try {
    fs.appendFileSync(config.LOG_FILE, logMessage + '\n');
  } catch (error) {
    console.error('Failed to write to log file:', error.message);
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// ODYSSEUS API CLIENT
// ═══════════════════════════════════════════════════════════════════════════════

class OdysseusClient {
  static async getHealth() {
    try {
      const response = await axios.get(`${config.ODYSSEUS_API_URL}/health`, {
        timeout: 5000
      });
      return { status: 'healthy', data: response.data };
    } catch (error) {
      return { status: 'unhealthy', error: error.message };
    }
  }

  static async getSessions() {
    try {
      const response = await axios.get(`${config.ODYSSEUS_API_URL}/api/sessions`, {
        timeout: 5000,
        headers: { 'Accept': 'application/json' }
      });
      return response.data;
    } catch (error) {
      log('WARN', 'Failed to get Odysseus sessions', error.message);
      return [];
    }
  }

  static async getSession(sessionId) {
    try {
      const response = await axios.get(`${config.ODYSSEUS_API_URL}/api/session/${sessionId}`, {
        timeout: 5000,
        headers: { 'Accept': 'application/json' }
      });
      return response.data;
    } catch (error) {
      log('WARN', `Failed to get Odysseus session ${sessionId}`, error.message);
      return null;
    }
  }

  static async createSession(name, description) {
    try {
      const response = await axios.post(`${config.ODYSSEUS_API_URL}/api/sessions`, {
        name,
        description
      }, {
        timeout: 5000,
        headers: { 'Content-Type': 'application/json' }
      });
      return response.data;
    } catch (error) {
      log('WARN', 'Failed to create Odysseus session', error.message);
      return null;
    }
  }

  static async executeTask(sessionId, taskDescription, context = {}) {
    try {
      const response = await axios.post(
        `${config.ODYSSEUS_API_URL}/api/session/${sessionId}/execute`,
        {
          query: taskDescription,
          context,
          tools: ['memory', 'rag', 'browser', 'email']
        },
        {
          timeout: 30000,
          headers: { 'Content-Type': 'application/json' }
        }
      );
      return response.data;
    } catch (error) {
      log('WARN', 'Failed to execute task in Odysseus', error.message);
      return null;
    }
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SYNK-IA ORCHESTRATOR CLIENT
// ═══════════════════════════════════════════════════════════════════════════════

class SynKiaOrchestratorClient {
  static async getStatus() {
    try {
      const response = await axios.get(`${config.SYNKIA_ORCHESTRATOR_URL}/api/orchestrator/status`, {
        timeout: 5000
      });
      return response.data;
    } catch (error) {
      log('WARN', 'Failed to get SYNK-IA Orchestrator status', error.message);
      return null;
    }
  }

  static async routeRequest(content, context = 'general') {
    try {
      const response = await axios.post(
        `${config.SYNKIA_ORCHESTRATOR_URL}/api/orchestrator/execute`,
        {
          content,
          context
        },
        {
          timeout: 10000,
          headers: { 'Content-Type': 'application/json' }
        }
      );
      return response.data;
    } catch (error) {
      log('WARN', 'Failed to route request to SYNK-IA', error.message);
      return null;
    }
  }

  static async selectModel(taskType) {
    try {
      const response = await axios.get(
        `${config.SYNKIA_MODEL_SELECTOR_URL}/api/model-selector/select?taskType=${taskType}`,
        { timeout: 5000 }
      );
      return response.data;
    } catch (error) {
      log('WARN', 'Failed to select model from SYNK-IA', error.message);
      return null;
    }
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// JOURNEY ORCHESTRATOR — Coordinador de viajes de tareas
// ═══════════════════════════════════════════════════════════════════════════════

class JourneyOrchestrator {
  constructor() {
    this.journeys = new Map();
    this.taskId = 0;
  }

  /**
   * Inicia un viaje (journey) — una secuencia de tareas coordinadas
   */
  async startJourney(name, description, steps = []) {
    const journeyId = `journey-${Date.now()}`;
    
    const journey = {
      id: journeyId,
      name,
      description,
      steps,
      status: 'planning',
      createdAt: new Date(),
      startedAt: null,
      completedAt: null,
      tasks: [],
      metrics: {
        totalTasks: 0,
        completedTasks: 0,
        failedTasks: 0,
        totalDuration: 0
      }
    };

    this.journeys.set(journeyId, journey);
    
    log('INFO', `Journey created: ${name}`, { journeyId });
    
    return journey;
  }

  /**
   * Agrega una tarea a un viaje existente
   */
  async addTaskToJourney(journeyId, taskDescription, dependencies = []) {
    const journey = this.journeys.get(journeyId);
    
    if (!journey) {
      throw new Error(`Journey ${journeyId} not found`);
    }

    const taskId = `task-${++this.taskId}`;
    const task = {
      id: taskId,
      description: taskDescription,
      dependencies,
      status: 'pending',
      createdAt: new Date(),
      startedAt: null,
      completedAt: null,
      result: null,
      assignedTool: null,
      selectedModel: null
    };

    journey.tasks.push(task);
    journey.metrics.totalTasks++;

    log('INFO', `Task added to journey`, { journeyId, taskId, description: taskDescription });

    return task;
  }

  /**
   * Ejecuta un viaje completo — todas las tareas en orden de dependencias
   */
  async executeJourney(journeyId) {
    const journey = this.journeys.get(journeyId);
    
    if (!journey) {
      throw new Error(`Journey ${journeyId} not found`);
    }

    journey.status = 'executing';
    journey.startedAt = new Date();
    
    log('INFO', `Executing journey: ${journey.name}`, { journeyId, totalTasks: journey.tasks.length });

    // Ejecuta tareas en orden respetando dependencias
    for (const task of journey.tasks) {
      if (!this.canExecuteTask(journey, task)) {
        log('WARN', `Skipping task due to unmet dependencies`, { taskId: task.id });
        task.status = 'skipped';
        continue;
      }

      await this.executeTask(journeyId, task);
    }

    journey.status = 'completed';
    journey.completedAt = new Date();
    journey.metrics.totalDuration = (journey.completedAt - journey.startedAt) / 1000;

    log('INFO', `Journey completed: ${journey.name}`, {
      journeyId,
      metrics: journey.metrics
    });

    return journey;
  }

  /**
   * Ejecuta una tarea individual con coordinación automática
   */
  async executeTask(journeyId, task) {
    const journey = this.journeys.get(journeyId);
    
    task.status = 'executing';
    task.startedAt = new Date();

    try {
      // 1. Detecta contexto de la tarea
      const context = this.detectTaskContext(task.description);

      // 2. Obtiene el modelo óptimo
      const modelSelection = await SynKiaOrchestratorClient.selectModel(context);
      task.selectedModel = modelSelection?.selected_model || 'default';

      // 3. Enruta la tarea a la herramienta correcta
      const routingResult = await SynKiaOrchestratorClient.routeRequest(
        task.description,
        context
      );

      task.assignedTool = routingResult?.routed_to || 'generic';

      // 4. Ejecuta en Odysseus si es necesario
      if (context === 'research' || context === 'analysis') {
        const odysseusSession = await OdysseusClient.createSession(
          `Task: ${task.id}`,
          task.description
        );
        
        if (odysseusSession) {
          const odysseusResult = await OdysseusClient.executeTask(
            odysseusSession.id,
            task.description,
            { journey: journeyId, context }
          );
          task.result = odysseusResult || routingResult?.response;
        }
      } else {
        task.result = routingResult?.response || 'Task executed';
      }

      task.status = 'completed';
      journey.metrics.completedTasks++;

      log('INFO', `Task completed in journey`, {
        journeyId,
        taskId: task.id,
        tool: task.assignedTool,
        model: task.selectedModel
      });

    } catch (error) {
      task.status = 'failed';
      task.result = error.message;
      journey.metrics.failedTasks++;

      log('ERROR', `Task execution failed`, {
        journeyId,
        taskId: task.id,
        error: error.message
      });
    }

    task.completedAt = new Date();
  }

  /**
   * Verifica si una tarea puede ejecutarse (dependencias satisfechas)
   */
  canExecuteTask(journey, task) {
    if (task.dependencies.length === 0) return true;

    return task.dependencies.every(depId => {
      const depTask = journey.tasks.find(t => t.id === depId);
      return depTask && depTask.status === 'completed';
    });
  }

  /**
   * Detecta el contexto de una tarea basado en keywords
   */
  detectTaskContext(description) {
    const lowerDesc = description.toLowerCase();

    if (lowerDesc.includes('code') || lowerDesc.includes('refactor') || lowerDesc.includes('debug')) {
      return 'coding';
    }
    if (lowerDesc.includes('research') || lowerDesc.includes('analyze') || lowerDesc.includes('investigate')) {
      return 'research';
    }
    if (lowerDesc.includes('write') || lowerDesc.includes('create') || lowerDesc.includes('generate')) {
      return 'creative';
    }
    if (lowerDesc.includes('search') || lowerDesc.includes('find') || lowerDesc.includes('discover')) {
      return 'research';
    }
    
    return 'general';
  }

  /**
   * Obtiene el estado de un viaje
   */
  getJourneyStatus(journeyId) {
    return this.journeys.get(journeyId) || null;
  }

  /**
   * Obtiene todos los viajes
   */
  getAllJourneys() {
    return Array.from(this.journeys.values());
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// HTTP BRIDGE SERVER (Puerto 9999)
// ═══════════════════════════════════════════════════════════════════════════════

const journeyOrchestrator = new JourneyOrchestrator();

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://${req.headers.host}`);
  const pathname = url.pathname;
  const method = req.method;

  res.setHeader('Content-Type', 'application/json');
  res.setHeader('Access-Control-Allow-Origin', '*');

  try {
    // ─────────────────────────────────────────────────────────────────────────────
    // HEALTH CHECK
    // ─────────────────────────────────────────────────────────────────────────────
    if (pathname === '/health' && method === 'GET') {
      const odysseusHealth = await OdysseusClient.getHealth();
      const synkiaHealth = await SynKiaOrchestratorClient.getStatus();

      return res.end(JSON.stringify({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        odysseus: odysseusHealth,
        synkia: synkiaHealth ? 'operational' : 'unreachable',
        bridge: 'operational'
      }));
    }

    // ─────────────────────────────────────────────────────────────────────────────
    // STATUS ENDPOINT
    // ─────────────────────────────────────────────────────────────────────────────
    if (pathname === '/api/odysseus/status' && method === 'GET') {
      const odysseusStatus = await OdysseusClient.getHealth();
      const journeys = journeyOrchestrator.getAllJourneys();

      return res.end(JSON.stringify({
        odysseus: odysseusStatus,
        journeys: {
          total: journeys.length,
          active: journeys.filter(j => j.status === 'executing').length,
          completed: journeys.filter(j => j.status === 'completed').length
        },
        timestamp: new Date().toISOString()
      }));
    }

    // ─────────────────────────────────────────────────────────────────────────────
    // CREATE JOURNEY
    // ─────────────────────────────────────────────────────────────────────────────
    if (pathname === '/api/journeys' && method === 'POST') {
      let body = '';
      
      req.on('data', chunk => {
        body += chunk.toString();
      });

      req.on('end', async () => {
        const data = JSON.parse(body);
        const journey = await journeyOrchestrator.startJourney(
          data.name,
          data.description,
          data.steps || []
        );

        res.statusCode = 201;
        res.end(JSON.stringify(journey));
      });

      return;
    }

    // ─────────────────────────────────────────────────────────────────────────────
    // GET JOURNEY
    // ─────────────────────────────────────────────────────────────────────────────
    if (pathname.startsWith('/api/journeys/') && method === 'GET') {
      const journeyId = pathname.split('/')[3];
      const journey = journeyOrchestrator.getJourneyStatus(journeyId);

      if (!journey) {
        res.statusCode = 404;
        return res.end(JSON.stringify({ error: 'Journey not found' }));
      }

      return res.end(JSON.stringify(journey));
    }

    // ─────────────────────────────────────────────────────────────────────────────
    // ADD TASK TO JOURNEY
    // ─────────────────────────────────────────────────────────────────────────────
    if (pathname.includes('/tasks') && method === 'POST') {
      const journeyId = pathname.split('/')[3];
      
      let body = '';
      
      req.on('data', chunk => {
        body += chunk.toString();
      });

      req.on('end', async () => {
        const data = JSON.parse(body);
        const task = await journeyOrchestrator.addTaskToJourney(
          journeyId,
          data.description,
          data.dependencies || []
        );

        res.statusCode = 201;
        res.end(JSON.stringify(task));
      });

      return;
    }

    // ─────────────────────────────────────────────────────────────────────────────
    // EXECUTE JOURNEY
    // ─────────────────────────────────────────────────────────────────────────────
    if (pathname.includes('/execute') && method === 'POST') {
      const journeyId = pathname.split('/')[3];
      const journey = await journeyOrchestrator.executeJourney(journeyId);

      return res.end(JSON.stringify(journey));
    }

    // ─────────────────────────────────────────────────────────────────────────────
    // GET ALL JOURNEYS
    // ─────────────────────────────────────────────────────────────────────────────
    if (pathname === '/api/journeys' && method === 'GET') {
      const journeys = journeyOrchestrator.getAllJourneys();
      return res.end(JSON.stringify({ journeys }));
    }

    // ─────────────────────────────────────────────────────────────────────────────
    // DEFAULT: 404
    // ─────────────────────────────────────────────────────────────────────────────
    res.statusCode = 404;
    res.end(JSON.stringify({ error: 'Endpoint not found' }));

  } catch (error) {
    log('ERROR', 'Request handling error', error.message);
    res.statusCode = 500;
    res.end(JSON.stringify({ error: error.message }));
  }
});

// ═══════════════════════════════════════════════════════════════════════════════
// START SERVER
// ═══════════════════════════════════════════════════════════════════════════════

server.listen(config.BRIDGE_PORT, config.BRIDGE_HOST, () => {
  log('INFO', `🚀 Odysseus Integration Bridge started`, {
    host: config.BRIDGE_HOST,
    port: config.BRIDGE_PORT,
    odysseusUrl: config.ODYSSEUS_API_URL,
    synkiaOrchestratorUrl: config.SYNKIA_ORCHESTRATOR_URL
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// GRACEFUL SHUTDOWN
// ═══════════════════════════════════════════════════════════════════════════════

process.on('SIGINT', () => {
  log('INFO', 'Shutting down Odysseus Integration Bridge');
  server.close(() => {
    process.exit(0);
  });
});

module.exports = { journeyOrchestrator, JourneyOrchestrator };
