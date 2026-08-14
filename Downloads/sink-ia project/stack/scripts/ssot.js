#!/usr/bin/env node
/**
 * synkia/ssot.js v2.0
 * ═══════════════════════════════════════════════════════════════════════════════
 * Walks EVERY provider under openclaw.models.providers (ollama, gateway, gemini,
 * nvidia, inferx, mlx-local, openai_compatible, groq, + future) and emits a flat
 * SSOT snapshot. Secrets (apiKey, token, password) are ALWAYS redacted before
 * writing — consumers should use the openclaw.json directly only for token
 * resolution at use-time, never for store-and-forward.
 * ═══════════════════════════════════════════════════════════════════════════════
 */
'use strict';

const fs = require('fs');
const path = require('path');

const OPENCLAW_JSON = '/Users/davidnows/.openclaw/openclaw.json';
const MODEL_HEALTH_JSON = '/Users/davidnows/.openclaw/model-health.json';
const SSOT_OUTPUT = process.env.SSOT_OUTPUT || '/Users/davidnows/.synkia-ai-hub/openclaw-ssot.json';

function readJsonSafe(p) {
  try {
    return JSON.parse(fs.readFileSync(p, 'utf8'));
  } catch (err) {
    return { __error: err.message, __path: p };
  }
}

function rankHealthScore(h) {
  if (!h) return 0;
  if (h.status === 'healthy') return h.health_score ?? 100;
  if (h.status === 'degraded') return h.health_score ?? 70;
  return 0;
}

function shortId(id) {
  if (!id) return '';
  return String(id).replace(/:free$/, '').replace(/:[\d.]+(b|B)?$/, '');
}

function redactSecrets(p) {
  if (!p || typeof p !== 'object') return p;
  const out = Array.isArray(p) ? [] : {};
  for (const [k, v] of Object.entries(p)) {
    if (/apikey|api_key|secret|^token$|password/i.test(k)) {
      out[k] = v === null || v === undefined ? v : '<redacted>';
    } else if (v && typeof v === 'object') {
      out[k] = redactSecrets(v);
    } else {
      out[k] = v;
    }
  }
  return out;
}

function buildHealthIndex(healthObj) {
  const idx = Object.create(null);
  if (!healthObj || !healthObj.models || typeof healthObj.models !== 'object') return idx;
  for (const [k, v] of Object.entries(healthObj.models)) {
    const s = shortId(k);
    idx[s] = { ...v, __id: k };
    idx[k] = { ...v, __id: k };
  }
  return idx;
}

function matchHealth(modelId, healthIdx) {
  if (!modelId || !healthIdx) return null;
  if (healthIdx[modelId]) return healthIdx[modelId];
  const s = shortId(modelId);
  if (healthIdx[s]) return healthIdx[s];
  const last = modelId.includes('/') ? modelId.split('/').pop() : modelId;
  if (healthIdx[shortId(last)]) return healthIdx[shortId(last)];
  for (const k of Object.keys(healthIdx)) {
    if (k === '__id' || k.startsWith('__')) continue;
    if (k.includes(s) || s.includes(k)) return healthIdx[k];
  }
  return null;
}

function walkProviders(openclaw) {
  const providers = (openclaw.models && openclaw.models.providers) || {};
  const out = [];
  for (const [provName, p] of Object.entries(providers)) {
    if (!p || typeof p !== 'object') continue;
    const modelsArr = Array.isArray(p.models) ? p.models : [];
    const baseUrl = p.baseUrl || null;
    const api = p.api || null;
    const providerContextTokens = p.contextTokens || null;
    for (const m of modelsArr) {
      if (!m || typeof m !== 'object') continue;
      const id = m.id;
      if (!id) continue;
      out.push({
        provider: provName,
        id,
        full_id: `${provName}/${id}`,
        name: m.name || id,
        api: m.api || api,
        context_window: m.contextWindow || providerContextTokens || null,
        max_tokens: m.maxTokens || null,
        reasoning: !!m.reasoning,
        cost: m.cost || null,
        base_url: baseUrl,
        input: Array.isArray(m.input) ? m.input : null,
        params: m.params || null,
        local: provName === 'ollama' || provName === 'gateway' || provName === 'mlx-local',
        api_key_configured: !!p.apiKey,
      });
    }
  }
  return out;
}

function buildSnapshot() {
  const oc = readJsonSafe(OPENCLAW_JSON);
  const health = readJsonSafe(MODEL_HEALTH_JSON);
  const ts = new Date().toISOString();

  const healthIdx = buildHealthIndex(health);
  const providers = (oc.models && oc.models.providers) || {};
  const providerNames = Object.keys(providers);
  const providerSummary = {};
  for (const name of providerNames) {
    const p = providers[name] || {};
    providerSummary[name] = {
      base_url: p.baseUrl || null,
      api: p.api || null,
      model_count: Array.isArray(p.models) ? p.models.length : 0,
      api_key_configured: !!p.apiKey,
    };
  }
  const authProfiles = Object.keys((oc.auth && oc.auth.profiles) || {});
  const telegram = (oc.channels && oc.channels.telegram) || {};
  const agentDefaults = (oc.agents && oc.agents.defaults && oc.agents.defaults.model) || {};

  const models = walkProviders(oc).map((m) => {
    const h = matchHealth(m.id, healthIdx);
    return {
      ...m,
      health: h ? {
        status: h.status || 'unknown',
        score: rankHealthScore(h),
        tests_passed: h.tests_passed ?? 0,
        tests_failed: h.tests_failed ?? 0,
        last_error: h.last_error ?? null,
        last_updated: health.last_updated ?? null,
      } : null,
      healthy: !h || h.status !== 'degraded',
    };
  });

  const providerCounts = {};
  for (const m of models) {
    providerCounts[m.provider] = (providerCounts[m.provider] || 0) + 1;
  }

  return {
    __generated_at: ts,
    __source: 'openclaw',
    __openclaw_path: OPENCLAW_JSON,
    openclaw_last_touched: oc.meta ? oc.meta.lastTouchedAt : null,
    health_last_updated: health.last_updated ?? null,
    providers: providerNames,
    providers_detail: providerSummary,
    auth_profiles: authProfiles,
    agent_default_primary: agentDefaults.primary || null,
    agent_default_fallbacks: agentDefaults.fallbacks || [],
    telegram: telegram.enabled ? {
      enabled: true,
      bot_token_configured: !!telegram.botToken,
      dm_policy: telegram.dmPolicy || null,
      group_policy: telegram.groupPolicy || null,
    } : { enabled: false },
    models,
    model_count: models.length,
    healthy_model_count: models.filter(m => m.healthy).length,
    local_model_count: models.filter(m => m.local).length,
    remote_model_count: models.filter(m => !m.local).length,
    degraded_models: models.filter(m => m.health && m.health.status === 'degraded').map(m => m.full_id),
    provider_counts: providerCounts,
    warnings: [
      oc.__error ? `openclaw.json unreadable: ${oc.__error}` : null,
      health.__error ? `model-health.json unreadable: ${health.__error}` : null,
    ].filter(Boolean),
  };
}

function writeSnapshot(snap) {
  fs.mkdirSync(path.dirname(SSOT_OUTPUT), { recursive: true });
  fs.writeFileSync(SSOT_OUTPUT, JSON.stringify(snap, null, 2));
  return SSOT_OUTPUT;
}

function refresh() {
  const snap = buildSnapshot();
  const out = writeSnapshot(snap);
  return { path: out, snapshot: snap };
}

if (require.main === module) {
  const args = process.argv.slice(2);
  if (args.includes('--refresh') || args.length === 0) {
    const r = refresh();
    const s = r.snapshot;
    console.log(JSON.stringify({
      ok: true,
      path: r.path,
      providers: s.providers,
      provider_counts: s.provider_counts,
      model_count: s.model_count,
      healthy: s.healthy_model_count,
      local: s.local_model_count,
      remote: s.remote_model_count,
      degraded_count: s.degraded_models.length,
      warnings: s.warnings,
    }, null, 2));
  } else if (args.includes('--print')) {
    process.stdout.write(JSON.stringify(buildSnapshot(), null, 2));
  } else if (args.includes('--print-safe')) {
    const s = buildSnapshot();
    s.models = s.models.map(m => ({ ...m, base_url: m.base_url ? '<redacted>' : null }));
    process.stdout.write(JSON.stringify(s, null, 2));
  } else {
    process.stderr.write('Usage: node ssot.js [--refresh|--print|--print-safe]\n');
    process.exit(2);
  }
}

module.exports = {
  buildSnapshot,
  refresh,
  redactSecrets,
  matchHealth,
  OPENCLAW_JSON,
  MODEL_HEALTH_JSON,
  SSOT_OUTPUT,
};
