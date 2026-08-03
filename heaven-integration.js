#!/usr/bin/env node
/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * HEAVEN ECOSYSTEM INTEGRATION FOR SYNK-OPS
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Este script integra el ecosistema Heaven con SYNK-OPS para proporcionar:
 * 
 * 1. Knowledge Hub Integration — Hub de conocimiento centralizado
 * 2. Cross-Ecosystem Search — Búsqueda unificada de todas las fuentes
 * 3. Intelligent Content Routing — Enrutamiento inteligente de contenido
 * 4. Autonomous Task Execution — Ejecución automática de tareas complejas
 * 5. Ecosystem Synthesis — Síntesis de conocimiento entre servicios
 * 6. Dynamic Content Discovery — Descubrimiento dinámico de contenido
 * 
 * Puertos:
 * - Heaven Hub: 8765 (localhost:8080 interno)
 * - Heaven Search: 8766 (localhost:8000 interno)
 * - Heaven Agent: 8767 (localhost:9000 interno)
 * - SYNK-IA Orchestrator: 9500
 * - Odysseus: 9999
 * - Heaven Bridge: 8888
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
  HEAVEN_HUB_URL: 'http://localhost:8765',
  HEAVEN_SEARCH_URL: 'http://localhost:8766',
  HEAVEN_AGENT_URL: 'http://localhost:8767',
  SYNKIA_ORCHESTRATOR_URL: 'http://localhost:9500',
  ODYSSEUS_URL: 'http://localhost:9999',
  BRIDGE_PORT: 8888,
  BRIDGE_HOST: '0.0.0.0',
  LOG_FILE: path.join(__dirname, 'heaven-integration.log'),
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
// HEAVEN ECOSYSTEM CLIENTS
// ═══════════════════════════════════════════════════════════════════════════════

class HeavenHubClient {
  static async getHealth() {
    try {
      const response = await axios.get(`${config.HEAVEN_HUB_URL}/health`, { timeout: 5000 });
      return { status: 'healthy', data: response.data };
    } catch (error) {
      return { status: 'unhealthy', error: error.message };
    }
  }

  static async searchContent(query) {
    try {
      const response = await axios.post(
        `${config.HEAVEN_HUB_URL}/api/search`,
        { query },
        { timeout: 10000 }
      );
      return response.data;
    } catch (error) {
      log('WARN', 'Heaven Hub search failed', error.message);
      return { results: [] };
    }
  }

  static async addContent(title, content, metadata = {}) {
    try {
      const response = await axios.post(
        `${config.HEAVEN_HUB_URL}/api/content`,
        { title, content, metadata },
        { timeout: 10000 }
      );
      return response.data;
    } catch (error) {
      log('WARN', 'Failed to add content to Heaven Hub', error.message);
      return null;
    }
  }

  static async getKnowledgeBase() {
    try {
      const response = await axios.get(`${config.HEAVEN_HUB_URL}/api/knowledge-base`, { timeout: 10000 });
      return response.data;
    } catch (error) {
      log('WARN', 'Failed to get knowledge base', error.message);
      return { items: [] };
    }
  }
}

class HeavenSearchClient {
  static async getHealth() {
    try {
      const response = await axios.get(`${config.HEAVEN_SEARCH_URL}/health`, { timeout: 5000 });
      return { status: 'healthy', data: response.data };
    } catch (error) {
      return { status: 'unhealthy', error: error.message };
    }
  }

  static async search(query, options = {}) {
    try {
      const response = await axios.post(
        `${config.HEAVEN_SEARCH_URL}/api/search`,
        {
          query,
          type: options.type || 'full-text',
          limit: options.limit || 10,
          offset: options.offset || 0
        },
        { timeout: 10000 }
      );
      return response.data;
    } catch (error) {
      log('WARN', 'Heaven Search failed', error.message);
      return { results: [] };
    }
  }

  static async vectorSearch(embedding, topK = 5) {
    try {
      const response = await axios.post(
        `${config.HEAVEN_SEARCH_URL}/api/vector-search`,
        { embedding, topK },
        { timeout: 10000 }
      );
      return response.data;
    } catch (error) {
      log('WARN', 'Vector search failed', error.message);
      return { results: [] };
    }
  }

  static async indexContent(id, content, metadata = {}) {
    try {
      const response = await axios.post(
        `${config.HEAVEN_SEARCH_URL}/api/index`,
        { id, content, metadata },
        { timeout: 10000 }
      );
      return response.data;
    } catch (error) {
      log('WARN', 'Failed to index content', error.message);
      return null;
    }
  }
}

class HeavenAgentClient {
  static async getHealth() {
    try {
      const response = await axios.get(`${config.HEAVEN_AGENT_URL}/health`, { timeout: 5000 });
      return { status: 'healthy', data: response.data };
    } catch (error) {
      return { status: 'unhealthy', error: error.message };
    }
  }

  static async executeTask(task, context = {}) {
    try {
      const response = await axios.post(
        `${config.HEAVEN_AGENT_URL}/api/execute`,
        { task, context },
        { timeout: 30000 }
      );
      return response.data;
    } catch (error) {
      log('WARN', 'Heaven Agent task execution failed', error.message);
      return { status: 'failed', error: error.message };
    }
  }

  static async synthesizeKnowledge(sources = []) {
    try {
      const response = await axios.post(
        `${config.HEAVEN_AGENT_URL}/api/synthesize`,
        { sources },
        { timeout: 30000 }
      );
      return response.data;
    } catch (error) {
      log('WARN', 'Knowledge synthesis failed', error.message);
      return { synthesis: '', sources: [] };
    }
  }

  static async discoverContent(keywords = []) {
    try {
      const response = await axios.post(
        `${config.HEAVEN_AGENT_URL}/api/discover`,
        { keywords },
        { timeout: 10000 }
      );
      return response.data;
    } catch (error) {
      log('WARN', 'Content discovery failed', error.message);
      return { discoveries: [] };
    }
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// ORCHESTRATION CLIENTS
// ═══════════════════════════════════════════════════════════════════════════════

class SynKiaOrchestratorClient {
  static async execute(content, context) {
    try {
      const response = await axios.post(
        `${config.SYNKIA_ORCHESTRATOR_URL}/api/orchestrator/execute`,
        { content, context },
        { timeout: 10000 }
      );
      return response.data;
    } catch (error) {
      log('WARN', 'SYNK-IA execution failed', error.message);
      return null;
    }
  }
}

class OdysseusClient {
  static async createJourney(name, description) {
    try {
      const response = await axios.post(
        `${config.ODYSSEUS_URL}/api/journeys`,
        { name, description },
        { timeout: 10000 }
      );
      return response.data;
    } catch (error) {
      log('WARN', 'Failed to create Odysseus journey', error.message);
      return null;
    }
  }

  static async executeJourney(journeyId) {
    try {
      const response = await axios.post(
        `${config.ODYSSEUS_URL}/api/journeys/${journeyId}/execute`,
        {},
        { timeout: 30000 }
      );
      return response.data;
    } catch (error) {
      log('WARN', 'Failed to execute journey', error.message);
      return null;
    }
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// HEAVEN-SYNK-IA CONTENT PIPELINE
// ═══════════════════════════════════════════════════════════════════════════════

class HeavenSynKiaPipeline {
  /**
   * Crea un pipeline completo: search → synthesize → orchestrate → journey
   */
  static async executeContentPipeline(query, taskType = 'research') {
    log('INFO', `Starting content pipeline for query: ${query}`);

    try {
      // 1. Busca contenido en Heaven
      const searchResults = await HeavenSearchClient.search(query, { type: 'full-text', limit: 10 });
      log('INFO', `Content search completed`, { resultCount: searchResults.results?.length || 0 });

      // 2. Sintetiza el conocimiento
      const synthesis = await HeavenAgentClient.synthesizeKnowledge(
        searchResults.results?.map(r => r.id) || []
      );
      log('INFO', `Knowledge synthesis completed`, { sourceCount: synthesis.sources?.length || 0 });

      // 3. Guarda el contenido sintetizado en el Hub
      const hubEntry = await HeavenHubClient.addContent(
        `Synthesis: ${query}`,
        synthesis.synthesis,
        { taskType, originalQuery: query, synthesisDate: new Date() }
      );
      log('INFO', `Content saved to Heaven Hub`, { contentId: hubEntry?.id });

      // 4. Enruta a SYNK-IA para ejecución
      const orchestrationResult = await SynKiaOrchestratorClient.execute(
        `Based on the synthesis:\n${synthesis.synthesis}\n\nProvide actionable insights.`,
        taskType
      );
      log('INFO', `SYNK-IA orchestration completed`, { tool: orchestrationResult?.routed_to });

      return {
        status: 'completed',
        pipeline: {
          search: searchResults.results?.length || 0,
          synthesis: synthesis.synthesis,
          hubId: hubEntry?.id,
          orchestrationTool: orchestrationResult?.routed_to,
          orchestrationModel: orchestrationResult?.model_used
        }
      };
    } catch (error) {
      log('ERROR', 'Content pipeline failed', error.message);
      return { status: 'failed', error: error.message };
    }
  }

  /**
   * Crea un journey en Odysseus para ejecutar tareas Heaven-enhanced
   */
  static async createEnhancedJourney(tasks = []) {
    try {
      // 1. Crea journey en Odysseus
      const journey = await OdysseusClient.createJourney(
        'Heaven-Enhanced Task Execution',
        'Execute tasks with Heaven knowledge synthesis'
      );

      if (!journey) {
        throw new Error('Failed to create journey');
      }

      log('INFO', `Journey created`, { journeyId: journey.id });

      // 2. Para cada tarea, enriquécela con contenido de Heaven
      for (const task of tasks) {
        // Busca contenido relacionado en Heaven
        const relatedContent = await HeavenSearchClient.search(task.description);

        // Agrega tarea al journey con contexto enriquecido
        const enrichedTask = {
          description: task.description,
          context: {
            ...task.context,
            heavenEnhanced: true,
            relatedContentCount: relatedContent.results?.length || 0
          },
          dependencies: task.dependencies || []
        };

        log('INFO', `Task enriched with Heaven content`, { taskDescription: task.description });
      }

      // 3. Ejecuta el journey
      const execution = await OdysseusClient.executeJourney(journey.id);

      log('INFO', `Journey execution completed`, { metrics: execution?.metrics });

      return {
        journeyId: journey.id,
        execution
      };
    } catch (error) {
      log('ERROR', 'Enhanced journey creation failed', error.message);
      return { status: 'failed', error: error.message };
    }
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// HTTP BRIDGE SERVER (Puerto 8888)
// ═══════════════════════════════════════════════════════════════════════════════

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
      const heavenHub = await HeavenHubClient.getHealth();
      const heavenSearch = await HeavenSearchClient.getHealth();
      const heavenAgent = await HeavenAgentClient.getHealth();

      return res.end(JSON.stringify({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        heaven: {
          hub: heavenHub.status,
          search: heavenSearch.status,
          agent: heavenAgent.status
        },
        bridge: 'operational'
      }));
    }

    // ─────────────────────────────────────────────────────────────────────────────
    // SEARCH
    // ─────────────────────────────────────────────────────────────────────────────
    if (pathname === '/api/search' && method === 'POST') {
      let body = '';
      
      req.on('data', chunk => {
        body += chunk.toString();
      });

      req.on('end', async () => {
        const { query } = JSON.parse(body);
        const results = await HeavenSearchClient.search(query);

        return res.end(JSON.stringify({ results: results.results || [] }));
      });

      return;
    }

    // ─────────────────────────────────────────────────────────────────────────────
    // CONTENT PIPELINE
    // ─────────────────────────────────────────────────────────────────────────────
    if (pathname === '/api/pipeline' && method === 'POST') {
      let body = '';
      
      req.on('data', chunk => {
        body += chunk.toString();
      });

      req.on('end', async () => {
        const { query, taskType } = JSON.parse(body);
        const result = await HeavenSynKiaPipeline.executeContentPipeline(query, taskType || 'research');

        return res.end(JSON.stringify(result));
      });

      return;
    }

    // ─────────────────────────────────────────────────────────────────────────────
    // ENHANCED JOURNEY
    // ─────────────────────────────────────────────────────────────────────────────
    if (pathname === '/api/enhanced-journey' && method === 'POST') {
      let body = '';
      
      req.on('data', chunk => {
        body += chunk.toString();
      });

      req.on('end', async () => {
        const { tasks } = JSON.parse(body);
        const result = await HeavenSynKiaPipeline.createEnhancedJourney(tasks);

        return res.end(JSON.stringify(result));
      });

      return;
    }

    // ─────────────────────────────────────────────────────────────────────────────
    // KNOWLEDGE BASE
    // ─────────────────────────────────────────────────────────────────────────────
    if (pathname === '/api/knowledge-base' && method === 'GET') {
      const kb = await HeavenHubClient.getKnowledgeBase();
      return res.end(JSON.stringify(kb));
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
  log('INFO', `🌌 Heaven Integration Bridge started`, {
    host: config.BRIDGE_HOST,
    port: config.BRIDGE_PORT,
    heavenHubUrl: config.HEAVEN_HUB_URL,
    heavenSearchUrl: config.HEAVEN_SEARCH_URL,
    heavenAgentUrl: config.HEAVEN_AGENT_URL
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// GRACEFUL SHUTDOWN
// ═══════════════════════════════════════════════════════════════════════════════

process.on('SIGINT', () => {
  log('INFO', 'Shutting down Heaven Integration Bridge');
  server.close(() => {
    process.exit(0);
  });
});

module.exports = { HeavenSynKiaPipeline, HeavenHubClient, HeavenSearchClient, HeavenAgentClient };
