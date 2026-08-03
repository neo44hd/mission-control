#!/usr/bin/env node

/**
 * SynK-IA MODEL SELECTOR v1.0
 * ═══════════════════════════════════════════════════════════════════════════════
 * Intelligent model selection system:
 * - Selects best model per task type
 * - Implements fallback chains
 * - Tracks cost and token usage
 * - Auto-updates with GitHub discoveries
 * - Exposes REST API for all tools
 * ═══════════════════════════════════════════════════════════════════════════════
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const yaml = require('js-yaml');

const CONFIG_PATH = process.env.CONFIG_PATH || '/Users/davidnows/synk-ia-global-config.yaml';
const MEMORY_FILE = '/Users/davidnows/.synkia-ai-hub/unified-memory.json';

let config = {};
let memory = {};

// Load config
try {
  const content = fs.readFileSync(CONFIG_PATH, 'utf8');
  config = yaml.load(content);
  console.log('✅ Configuration loaded');
} catch (err) {
  console.error('❌ Failed to load config:', err.message);
  process.exit(1);
}

// Load memory
try {
  if (fs.existsSync(MEMORY_FILE)) {
    memory = JSON.parse(fs.readFileSync(MEMORY_FILE, 'utf8'));
  }
} catch (err) {
  memory = { models: {}, costs: {}, tokenUsage: {} };
}

// Model profiles database
const MODEL_DATABASE = {
  'local-claude-code': {
    provider: 'openclaw',
    type: 'coding',
    cost: 0,
    contextWindow: 32768,
    reasoning: true,
    speed: 'medium',
    quality: 'excellent',
    specialty: 'code-refactoring'
  },
  'local-coder-ollama': {
    provider: 'ollama',
    model: 'qwen2.5-coder:7b',
    type: 'coding',
    cost: 0,
    contextWindow: 32768,
    reasoning: false,
    speed: 'fast',
    quality: 'good',
    specialty: 'coding-tasks'
  },
  'local-llama:3b': {
    provider: 'ollama',
    model: 'llama3.2:3b',
    type: 'general',
    cost: 0,
    contextWindow: 8192,
    reasoning: false,
    speed: 'very-fast',
    quality: 'fair',
    specialty: 'lightweight-tasks'
  },
  'local-reason': {
    provider: 'litellm-gateway',
    type: 'reasoning',
    cost: 0,
    contextWindow: 32768,
    reasoning: true,
    speed: 'slow',
    quality: 'excellent',
    specialty: 'analysis-research'
  },
  'local-big': {
    provider: 'litellm-gateway',
    type: 'general',
    cost: 0,
    contextWindow: 16384,
    reasoning: false,
    speed: 'medium',
    quality: 'excellent',
    specialty: 'creative-writing'
  },
  'local-fast': {
    provider: 'ollama',
    type: 'general',
    cost: 0,
    contextWindow: 8192,
    reasoning: false,
    speed: 'very-fast',
    quality: 'fair',
    specialty: 'quick-responses'
  },
  'ruflow-semantic-scorer': {
    provider: 'ruflow',
    type: 'job-matching',
    cost: 0,
    contextWindow: 16384,
    reasoning: true,
    speed: 'medium',
    quality: 'excellent',
    specialty: 'resume-job-matching'
  }
};

// Cost tracking
function recordCost(modelId, inputTokens, outputTokens, success) {
  memory.costs = memory.costs || {};
  memory.costs[modelId] = memory.costs[modelId] || {
    totalInputTokens: 0,
    totalOutputTokens: 0,
    estimatedCost: 0,
    executions: 0,
    successes: 0
  };

  const costEntry = memory.costs[modelId];
  costEntry.totalInputTokens += inputTokens;
  costEntry.totalOutputTokens += outputTokens;
  costEntry.executions++;
  if (success) costEntry.successes++;

  // Estimate cost (local models are free, adjust for cloud models)
  const modelInfo = MODEL_DATABASE[modelId];
  if (modelInfo?.provider !== 'ollama' && modelInfo?.provider !== 'litellm-gateway') {
    costEntry.estimatedCost += (inputTokens * 0.001 + outputTokens * 0.002) / 1000; // Example pricing
  }

  fs.writeFileSync(MEMORY_FILE, JSON.stringify(memory, null, 2));
}

// Select model based on task
function selectModel(taskType, constraints = {}) {
  const profile = config.modelSelection?.taskProfiles?.[taskType] || config.modelSelection?.taskProfiles?.fast;
  const result = {
    taskType,
    suggestions: [],
    fallbackChain: [],
    recommendation: null
  };

  // Primary selection
  const primary = MODEL_DATABASE[profile.primary];
  if (primary) {
    // Check if meets constraints
    let viable = true;
    if (constraints.maxContextWindow && primary.contextWindow < constraints.maxContextWindow) {
      viable = false;
    }
    if (constraints.requireReasoning && !primary.reasoning) {
      viable = false;
    }
    if (constraints.maxLatency === 'fast' && primary.speed !== 'very-fast' && primary.speed !== 'fast') {
      viable = false;
    }

    result.suggestions.push({
      model: profile.primary,
      info: primary,
      viable,
      reason: viable ? 'Primary recommendation' : 'Does not meet constraints'
    });

    if (viable) {
      result.recommendation = profile.primary;
    }
  }

  // Secondary & Fallback
  [profile.secondary, profile.fallback].forEach((modelId, idx) => {
    if (modelId && MODEL_DATABASE[modelId]) {
      const model = MODEL_DATABASE[modelId];
      result.suggestions.push({
        model: modelId,
        info: model,
        viable: true,
        reason: idx === 0 ? 'Secondary option' : 'Fallback option'
      });
      if (!result.recommendation && idx === 0) {
        result.recommendation = modelId;
      }
    }
  });

  // Build fallback chain
  result.fallbackChain = [profile.primary, profile.secondary, profile.fallback].filter(m => m && MODEL_DATABASE[m]);

  return result;
}

// Compare models
function compareModels(modelIds) {
  const comparison = {
    models: [],
    bestFor: {}
  };

  modelIds.forEach(modelId => {
    const info = MODEL_DATABASE[modelId];
    if (info) {
      const costData = memory.costs?.[modelId] || {};
      comparison.models.push({
        id: modelId,
        provider: info.provider,
        contextWindow: info.contextWindow,
        reasoning: info.reasoning,
        speed: info.speed,
        quality: info.quality,
        specialty: info.specialty,
        avgCost: costData.executions > 0 ? (costData.estimatedCost / costData.executions).toFixed(4) : '0.0000',
        successRate: costData.executions > 0 ? ((costData.successes / costData.executions) * 100).toFixed(1) : 'N/A'
      });
    }
  });

  // Determine best for each category
  const models = comparison.models;
  if (models.length > 0) {
    comparison.bestFor.speed = models.reduce((prev, curr) => {
      const speedOrder = { 'very-fast': 1, 'fast': 2, 'medium': 3, 'slow': 4 };
      return speedOrder[prev.speed] < speedOrder[curr.speed] ? prev : curr;
    }).id;

    comparison.bestFor.quality = models.reduce((prev, curr) =>
      (prev.quality === 'excellent' ? prev : curr)
    ).id;

    comparison.bestFor.cost = models.reduce((prev, curr) =>
      parseFloat(prev.avgCost) < parseFloat(curr.avgCost) ? prev : curr
    ).id;

    comparison.bestFor.reasoning = models.find(m => m.reasoning)?.id || models[0].id;
  }

  return comparison;
}

// REST API Server
const PORT = process.env.MODEL_SELECTOR_PORT || 9501;

const server = http.createServer((req, res) => {
  res.setHeader('Content-Type', 'application/json');
  res.setHeader('Access-Control-Allow-Origin', '*');

  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }

  // GET /api/model-selector/select?taskType=coding&constraints=...
  if (req.url.startsWith('/api/model-selector/select') && req.method === 'GET') {
    const url = new URL(`http://localhost${req.url}`);
    const taskType = url.searchParams.get('taskType') || 'fast';
    const constraints = {};

    const maxCtx = url.searchParams.get('maxContextWindow');
    if (maxCtx) constraints.maxContextWindow = parseInt(maxCtx);

    const result = selectModel(taskType, constraints);
    res.writeHead(200);
    res.end(JSON.stringify(result, null, 2));
    return;
  }

  // GET /api/model-selector/compare?models=model1,model2,model3
  if (req.url.startsWith('/api/model-selector/compare') && req.method === 'GET') {
    const url = new URL(`http://localhost${req.url}`);
    const modelsStr = url.searchParams.get('models') || '';
    const modelIds = modelsStr.split(',').filter(m => m.trim());

    const comparison = compareModels(modelIds);
    res.writeHead(200);
    res.end(JSON.stringify(comparison, null, 2));
    return;
  }

  // POST /api/model-selector/record-cost
  if (req.url === '/api/model-selector/record-cost' && req.method === 'POST') {
    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', () => {
      try {
        const data = JSON.parse(body);
        recordCost(data.modelId, data.inputTokens || 0, data.outputTokens || 0, data.success !== false);
        res.writeHead(200);
        res.end(JSON.stringify({ recorded: true }));
      } catch (err) {
        res.writeHead(400);
        res.end(JSON.stringify({ error: err.message }));
      }
    });
    return;
  }

  // GET /api/model-selector/models
  if (req.url === '/api/model-selector/models' && req.method === 'GET') {
    const models = Object.entries(MODEL_DATABASE).map(([id, info]) => ({
      id,
      ...info
    }));
    res.writeHead(200);
    res.end(JSON.stringify({ models, total: models.length }, null, 2));
    return;
  }

  // GET /api/model-selector/costs
  if (req.url === '/api/model-selector/costs' && req.method === 'GET') {
    res.writeHead(200);
    res.end(JSON.stringify(memory.costs || {}, null, 2));
    return;
  }

  // GET /api/model-selector/profiles
  if (req.url === '/api/model-selector/profiles' && req.method === 'GET') {
    const profiles = config.modelSelection?.taskProfiles || {};
    res.writeHead(200);
    res.end(JSON.stringify(profiles, null, 2));
    return;
  }

  // Health check
  if (req.url === '/health' && req.method === 'GET') {
    res.writeHead(200);
    res.end(JSON.stringify({ status: 'healthy' }));
    return;
  }

  res.writeHead(404);
  res.end(JSON.stringify({ error: 'Not found' }));
});

server.listen(PORT, () => {
  console.log(`🚀 Model Selector API listening on port ${PORT}`);
  console.log(`  - Select model: http://localhost:${PORT}/api/model-selector/select?taskType=coding`);
  console.log(`  - Compare models: http://localhost:${PORT}/api/model-selector/compare?models=local-claude-code,local-fast`);
  console.log(`  - All models: http://localhost:${PORT}/api/model-selector/models`);
  console.log(`  - Cost tracking: http://localhost:${PORT}/api/model-selector/costs`);
  console.log(`  - Task profiles: http://localhost:${PORT}/api/model-selector/profiles`);
});

process.on('SIGINT', () => {
  fs.writeFileSync(MEMORY_FILE, JSON.stringify(memory, null, 2));
  process.exit(0);
});
