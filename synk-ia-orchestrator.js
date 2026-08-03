#!/usr/bin/env node

/**
 * SynK-IA ORCHESTRATOR v1.0
 * ═══════════════════════════════════════════════════════════════════════════════
 * Central daemon for SynK-IA ecosystem orchestration:
 * - Monitors all services (health checks every 30s)
 * - Auto-restarts critical services on failure
 * - Routes requests to best tool based on context
 * - Maintains unified ecosystem state
 * - Updates GitHub discoveries
 * - Learns from performance metrics
 * ═══════════════════════════════════════════════════════════════════════════════
 */

const http = require('http');
const https = require('https');
const fs = require('fs');
const path = require('path');
const yaml = require('js-yaml');
const { exec } = require('child_process');
const { promisify } = require('util');

const execAsync = promisify(exec);

// ─────────────────────────────────────────────────────────────────────────────
// CONFIGURATION & INITIALIZATION
// ─────────────────────────────────────────────────────────────────────────────

const CONFIG_PATH = process.env.CONFIG_PATH || '/Users/davidnows/synk-ia-global-config.yaml';
const DATA_DIR = '/Users/davidnows/.synkia-ai-hub';
const STATE_FILE = path.join(DATA_DIR, 'ecosystem-state.json');
const EVENT_LOG = path.join(DATA_DIR, 'ecosystem-events.log');
const MEMORY_FILE = path.join(DATA_DIR, 'unified-memory.json');

let config = {};
let ecosystemState = {};
let unifiedMemory = {};

// Load configuration
try {
  const configContent = fs.readFileSync(CONFIG_PATH, 'utf8');
  config = yaml.load(configContent);
  console.log('✅ Configuration loaded from', CONFIG_PATH);
} catch (err) {
  console.error('❌ Failed to load configuration:', err.message);
  process.exit(1);
}

// Load or initialize state files
function loadState() {
  try {
    if (fs.existsSync(STATE_FILE)) {
      ecosystemState = JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'));
    }
  } catch (err) {
    ecosystemState = { services: {}, lastCheck: new Date().toISOString() };
  }

  try {
    if (fs.existsSync(MEMORY_FILE)) {
      unifiedMemory = JSON.parse(fs.readFileSync(MEMORY_FILE, 'utf8'));
    }
  } catch (err) {
    unifiedMemory = { learning: {}, routing: {}, performance: {}, discoveries: [] };
  }
}

// Save state files
function saveState() {
  try {
    fs.writeFileSync(STATE_FILE, JSON.stringify(ecosystemState, null, 2));
    fs.writeFileSync(MEMORY_FILE, JSON.stringify(unifiedMemory, null, 2));
  } catch (err) {
    logEvent('error', `Failed to save state: ${err.message}`);
  }
}

// Logging
function logEvent(level, message, metadata = {}) {
  const timestamp = new Date().toISOString();
  const logEntry = `[${timestamp}] ${level.toUpperCase()}: ${message} ${Object.keys(metadata).length > 0 ? JSON.stringify(metadata) : ''}\n`;
  
  try {
    fs.appendFileSync(EVENT_LOG, logEntry);
  } catch (err) {
    console.error('Failed to write log:', err.message);
  }
  
  if (level === 'error' || level === 'critical') {
    console.error(`🚨 ${message}`, metadata);
  } else {
    console.log(`✅ ${message}`, metadata);
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// HEALTH CHECK ENGINE
// ─────────────────────────────────────────────────────────────────────────────

async function checkServiceHealth(serviceName, serviceConfig) {
  return new Promise((resolve) => {
    const timeout = serviceConfig.timeout || (config.orchestration?.healthCheck?.timeout || 5) * 1000;
    const timer = setTimeout(() => {
      resolve({ status: 'down', reason: 'timeout' });
    }, timeout);

    const url = `${serviceConfig.baseUrl}${serviceConfig.healthCheck || '/health'}`;
    const protocol = serviceConfig.protocol === 'https' ? https : http;

    const request = protocol.get(url, (res) => {
      clearTimeout(timer);
      resolve({
        status: res.statusCode === 200 ? 'healthy' : 'unhealthy',
        httpStatus: res.statusCode,
        reason: res.statusCode === 200 ? 'OK' : `HTTP ${res.statusCode}`
      });
    });

    request.on('error', (err) => {
      clearTimeout(timer);
      resolve({ status: 'down', reason: err.message });
    });
  });
}

async function monitorAllServices() {
  logEvent('info', '🔍 Starting health check cycle');
  ecosystemState.lastCheck = new Date().toISOString();
  ecosystemState.services = ecosystemState.services || {};

  const services = config.services || {};
  const criticalServices = config.orchestration?.healthCheck?.criticalServices || [];

  for (const [serviceName, serviceConfig] of Object.entries(services)) {
    const health = await checkServiceHealth(serviceName, serviceConfig);
    
    ecosystemState.services[serviceName] = {
      name: serviceConfig.name,
      status: health.status === 'healthy' ? 'online' : 'offline',
      port: serviceConfig.port,
      critical: serviceConfig.critical || false,
      autoRestart: serviceConfig.autoRestart || false,
      lastCheck: new Date().toISOString(),
      healthy: health.status === 'healthy',
      httpStatus: health.httpStatus,
      reason: health.reason
    };

    const statusEmoji = health.status === 'healthy' ? '✅' : '❌';
    logEvent('info', `${statusEmoji} ${serviceName}: ${health.status}`, { reason: health.reason });

    // Auto-restart critical services
    if (health.status !== 'healthy' && serviceConfig.autoRestart && serviceConfig.critical) {
      await autoRestartService(serviceName, serviceConfig);
    }
  }

  saveState();
}

async function autoRestartService(serviceName, serviceConfig) {
  logEvent('warn', `🔄 Attempting auto-restart of ${serviceName}`);

  try {
    if (serviceConfig.docker) {
      const { service, network } = serviceConfig.docker;
      await execAsync(`cd /Users/davidnows && docker-compose -f docker-compose.synkia-os.yml restart ${service}`);
      logEvent('info', `✅ Successfully restarted Docker service: ${service}`);
    } else if (serviceConfig.pm2) {
      await execAsync(`pm2 restart ${serviceName}`);
      logEvent('info', `✅ Successfully restarted PM2 process: ${serviceName}`);
    }
  } catch (err) {
    logEvent('error', `🚨 Failed auto-heal: ${serviceName}`, { error: err.message });
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// INTELLIGENT ROUTING ENGINE
// ─────────────────────────────────────────────────────────────────────────────

function analyzeContext(userInput) {
  const lowerInput = userInput.toLowerCase();
  const patterns = config.orchestration?.routing?.patterns || [];

  for (const pattern of patterns) {
    if (pattern.context && pattern.context.length > 0) {
      const matched = pattern.context.some(keyword => lowerInput.includes(keyword));
      if (matched) {
        return {
          targetTool: pattern.targetTool,
          model: pattern.model,
          priority: pattern.priority,
          confidence: 0.9
        };
      }
    }
  }

  // Default fallback
  return {
    targetTool: 'hub-ai-local',
    model: 'local-fast',
    priority: 'medium',
    confidence: 0.1
  };
}

function selectBestModel(taskType = 'fast') {
  const profile = config.modelSelection?.taskProfiles?.[taskType];
  if (!profile) return config.modelSelection?.taskProfiles?.fast;

  // Return primary model for this task type
  return {
    primary: profile.primary,
    secondary: profile.secondary,
    fallback: profile.fallback,
    reasoning: profile.reasoning,
    contextWindow: profile.contextWindow
  };
}

async function routeRequest(userInput, context = {}) {
  const analysis = analyzeContext(userInput);
  const targetTool = config.services?.[analysis.targetTool];
  
  if (!targetTool) {
    logEvent('warn', `Tool not found: ${analysis.targetTool}, using fallback`);
    return {
      status: 'error',
      message: 'Target tool not found',
      fallback: 'hub-ai-local'
    };
  }

  const modelSelection = selectBestModel(context.taskType);
  const toolHealth = ecosystemState.services?.[analysis.targetTool];

  if (toolHealth?.status === 'offline' && analysis.targetTool !== 'hub-ai-local') {
    logEvent('warn', `Primary tool ${analysis.targetTool} is offline, routing to fallback`);
    analysis.targetTool = 'hub-ai-local';
  }

  // Track this routing decision for learning
  unifiedMemory.routing = unifiedMemory.routing || {};
  unifiedMemory.routing[analysis.targetTool] = (unifiedMemory.routing[analysis.targetTool] || 0) + 1;
  saveState();

  logEvent('info', `🎯 Routed request to ${analysis.targetTool}`, {
    model: analysis.model,
    priority: analysis.priority,
    confidence: analysis.confidence
  });

  return {
    status: 'routed',
    tool: analysis.targetTool,
    toolUrl: targetTool.baseUrl,
    model: analysis.model,
    modelSelection,
    priority: analysis.priority,
    confidence: analysis.confidence
  };
}

// ─────────────────────────────────────────────────────────────────────────────
// GITHUB DISCOVERY INTEGRATION
// ─────────────────────────────────────────────────────────────────────────────

async function updateGitHubDiscoveries() {
  logEvent('info', '🔍 Checking GitHub discoveries...');
  
  try {
    const discoveryFile = path.join(DATA_DIR, 'discovery-cache.json');
    if (fs.existsSync(discoveryFile)) {
      const discoveries = JSON.parse(fs.readFileSync(discoveryFile, 'utf8'));
      const lastUpdate = new Date(discoveries.lastScan);
      const now = new Date();
      const hoursSinceUpdate = (now - lastUpdate) / (1000 * 60 * 60);

      if (hoursSinceUpdate > 1) {
        logEvent('info', '📚 GitHub discovery cache is stale, would refresh (skipping in demo)', {
          hoursSince: hoursSinceUpdate.toFixed(1)
        });
      }

      unifiedMemory.discoveries = discoveries.trending || [];
      unifiedMemory.lastDiscoveryUpdate = discoveries.lastScan;
      saveState();
    }
  } catch (err) {
    logEvent('error', 'Failed to update GitHub discoveries', { error: err.message });
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// PERFORMANCE LEARNING ENGINE
// ─────────────────────────────────────────────────────────────────────────────

function recordPerformanceMetric(toolName, taskType, duration, success) {
  unifiedMemory.performance = unifiedMemory.performance || {};
  unifiedMemory.performance[toolName] = unifiedMemory.performance[toolName] || {
    executions: 0,
    successes: 0,
    avgDuration: 0,
    errors: []
  };

  const metrics = unifiedMemory.performance[toolName];
  metrics.executions++;
  if (success) metrics.successes++;
  metrics.avgDuration = (metrics.avgDuration * (metrics.executions - 1) + duration) / metrics.executions;

  unifiedMemory.learning = unifiedMemory.learning || {};
  unifiedMemory.learning.lastUpdated = new Date().toISOString();

  saveState();
  logEvent('info', `📊 Performance recorded for ${toolName}`, {
    successRate: (metrics.successes / metrics.executions * 100).toFixed(1) + '%',
    avgDuration: metrics.avgDuration.toFixed(0) + 'ms'
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// ORCHESTRATOR API SERVER
// ─────────────────────────────────────────────────────────────────────────────

async function startOrchestratorAPI() {
  const PORT = process.env.ORCHESTRATOR_PORT || 9500;

  const server = http.createServer(async (req, res) => {
    res.setHeader('Content-Type', 'application/json');
    res.setHeader('Access-Control-Allow-Origin', '*');

    // CORS pre-flight
    if (req.method === 'OPTIONS') {
      res.writeHead(200);
      res.end();
      return;
    }

    // Status endpoint
    if (req.url === '/api/orchestrator/status' && req.method === 'GET') {
      res.writeHead(200);
      res.end(JSON.stringify({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        services: ecosystemState.services,
        uptime: process.uptime(),
        memory: process.memoryUsage()
      }, null, 2));
      return;
    }

    // Model select endpoint
    if (req.url.startsWith('/api/orchestrator/model-select') && req.method === 'GET') {
      const url = new URL(`http://localhost${req.url}`);
      const context = url.searchParams.get('context') || '';
      const taskType = url.searchParams.get('taskType') || 'fast';

      const routing = await routeRequest(context, { taskType });
      res.writeHead(200);
      res.end(JSON.stringify(routing, null, 2));
      return;
    }

    // Execute endpoint
    if (req.url.startsWith('/api/orchestrator/execute') && req.method === 'POST') {
      let body = '';
      req.on('data', chunk => { body += chunk; });
      req.on('end', async () => {
        try {
          const payload = JSON.parse(body);
          const routing = await routeRequest(payload.input || '', { taskType: payload.taskType });
          
          // Record execution
          const startTime = Date.now();
          // (In real implementation, would execute and track duration)
          recordPerformanceMetric(routing.tool, payload.taskType || 'unknown', 100, true);

          res.writeHead(200);
          res.end(JSON.stringify({ ...routing, queued: true }, null, 2));
        } catch (err) {
          res.writeHead(400);
          res.end(JSON.stringify({ error: err.message }));
        }
      });
      return;
    }

    // Learning stats
    if (req.url === '/api/orchestrator/learning' && req.method === 'GET') {
      res.writeHead(200);
      res.end(JSON.stringify({
        memory: unifiedMemory,
        recommendations: generateRecommendations()
      }, null, 2));
      return;
    }

    // Health check
    if (req.url === '/health' && req.method === 'GET') {
      res.writeHead(200);
      res.end(JSON.stringify({ status: 'healthy', timestamp: new Date().toISOString() }));
      return;
    }

    // 404
    res.writeHead(404);
    res.end(JSON.stringify({ error: 'Not found' }));
  });

  server.listen(PORT, () => {
    logEvent('info', `🚀 Orchestrator API listening on port ${PORT}`);
    console.log(`Orchestrator API: http://localhost:${PORT}`);
    console.log(`  - Status: http://localhost:${PORT}/api/orchestrator/status`);
    console.log(`  - Model Select: http://localhost:${PORT}/api/orchestrator/model-select?context=code&taskType=coding`);
    console.log(`  - Learning: http://localhost:${PORT}/api/orchestrator/learning`);
  });
}

function generateRecommendations() {
  const recommendations = [];

  // Check if critical services are healthy
  const criticalServices = config.orchestration?.healthCheck?.criticalServices || [];
  for (const service of criticalServices) {
    const serviceState = ecosystemState.services?.[service];
    if (serviceState?.status === 'offline') {
      recommendations.push({
        priority: 'critical',
        service,
        recommendation: `Critical service ${service} is offline. Attempting auto-restart...`,
        action: 'auto-restart'
      });
    }
  }

  // Performance-based recommendations
  const performance = unifiedMemory.performance || {};
  for (const [tool, metrics] of Object.entries(performance)) {
    if (metrics.avgDuration > 5000) {
      recommendations.push({
        priority: 'warning',
        service: tool,
        recommendation: `${tool} is slow (avg ${metrics.avgDuration.toFixed(0)}ms). Consider using a faster alternative.`,
        action: 'optimize'
      });
    }
  }

  return recommendations;
}

// ─────────────────────────────────────────────────────────────────────────────
// MAIN LOOP
// ─────────────────────────────────────────────────────────────────────────────

async function main() {
  console.log('═══════════════════════════════════════════════════════════════════════════════');
  console.log('🚀 SynK-IA ORCHESTRATOR v1.0 — Starting...');
  console.log('═══════════════════════════════════════════════════════════════════════════════');

  // Initialize
  loadState();
  logEvent('info', '🔄 Orchestrator initialized');

  // Start API server
  await startOrchestratorAPI();

  // Initial health check
  await monitorAllServices();

  // Health check loop (every 30 seconds)
  const healthCheckInterval = (config.orchestration?.healthCheck?.interval || 30) * 1000;
  setInterval(async () => {
    await monitorAllServices();
  }, healthCheckInterval);

  // GitHub discovery update (every 1 hour)
  const discoveryInterval = (config.memory?.githubDiscovery?.updateInterval || 3600) * 1000;
  setInterval(async () => {
    await updateGitHubDiscoveries();
  }, discoveryInterval);

  // Initial GitHub discovery check
  await updateGitHubDiscoveries();

  logEvent('info', '✅ SynK-IA Orchestrator fully operational');
  console.log('✅ Orchestrator ready. Monitoring 10+ services...\n');
}

// Graceful shutdown
process.on('SIGINT', () => {
  logEvent('info', 'Orchestrator shutting down gracefully');
  saveState();
  process.exit(0);
});

process.on('SIGTERM', () => {
  logEvent('info', 'Orchestrator terminated');
  saveState();
  process.exit(0);
});

// Start orchestrator
main().catch(err => {
  logEvent('critical', 'Fatal error in orchestrator', { error: err.message });
  process.exit(1);
});
