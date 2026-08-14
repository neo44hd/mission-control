#!/usr/bin/env node
/**
 * synkia-health-probe v1.0
 * ═══════════════════════════════════════════════════════════════════════════════
 * Refreshes ~/.openclaw/model-health.json every PROBE_INTERVAL_MS (default 6h).
 * Probes EACH provider under openclaw.models.providers:
 *
 *   ollama         → GET http://127.0.0.1:11434/api/tags
 *   mlx-local      → GET http://127.0.0.1:4001/v1/models
 *   gateway        → GET http://127.0.0.1:3020/health
 *   gemini         → GET api_key ? models?key= : baseUrl (5s timeout)
 *   nvidia         → GET v1/models with Bearer auth
 *   inferx         → GET v1/models with Bearer auth
 *   openai_compatible (openrouter) → GET /api/v1/models with Bearer auth
 *   groq           → GET openai/v1/models with Bearer auth
 *
 * Writes per-model entries to ~/.openclaw/model-health.json with:
 *   tests_passed / tests_failed / last_error / status / health_score / last_updated
 *
 * If any LOCAL provider is degraded → alert immediately (regardless of interval).
 * Remote providers that fail are tolerated (may be rate-limited in fly).
 * ═══════════════════════════════════════════════════════════════════════════════
 */
'use strict';

const fs = require('fs');
const path = require('path');
const http = require('http');
const https = require('https');
const { exec } = require('child_process');

const HOME = '/Users/davidnows';
const OPENCLAW_JSON = path.join(HOME, '.openclaw/openclaw.json');
const MODEL_HEALTH_JSON = path.join(HOME, '.openclaw/model-health.json');
const INCIDENT_DIR = path.join(HOME, '.synkia/incidents');
const INTERVAL_MS = parseInt(process.env.PROBE_INTERVAL_MS || String(6 * 60 * 60 * 1000), 10);

function readJsonSafe(p) {
  try { return JSON.parse(fs.readFileSync(p, 'utf8')); }
  catch (e) { return { __error: e.message }; }
}
function writeJsonSafe(p, obj) {
  fs.mkdirSync(path.dirname(p), { recursive: true });
  fs.writeFileSync(p, JSON.stringify(obj, null, 2));
}

// Tiny completion poke used as fallback when /v1/models is gated.
// POSTs a single-token request. 200 → healthy. 429 → key valid, throttled.
async function probeCompletion(name, baseUrl, key, sampleModel) {
  if (!baseUrl || !key || !sampleModel || !sampleModel.id) {
    return { ok: false, status: 0, body: '', error: 'no completion params' };
  }
  const url = `${baseUrl.replace(/\/$/, '')}/chat/completions`;
  let payload;
  if (name === 'gemini') {
    // Gemini uses X-goog-api-key + different path; skip from this fallback (already special-cased).
    return { ok: false, status: 0, body: '', error: 'gemini uses different endpoint' };
  } else {
    payload = JSON.stringify({
      model: sampleModel.id,
      messages: [{ role: 'user', content: 'ping' }],
      max_tokens: 1,
      stream: false,
    });
  }
  return new Promise((resolve) => {
    const lib = url.startsWith('https') ? https : http;
    const u = new URL(url);
    const data = payload;
    const req = lib.request({
      method: 'POST',
      hostname: u.hostname,
      path: u.pathname,
      port: u.port || (url.startsWith('https') ? 443 : 80),
      headers: {
        'Authorization': `Bearer ${key}`,
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(data),
      },
      timeout: 6000,
    }, (res) => {
      let body = '';
      res.on('data', (c) => (body += c));
      res.on('end', () => resolve({
        ok: res.statusCode >= 200 && res.statusCode < 300,
        status: res.statusCode,
        body: body.slice(0, 256),
      }));
    });
    req.on('timeout', () => req.destroy(new Error('timeout')));
    req.on('error', (e) => resolve({ ok: false, status: 0, body: '', error: e.message }));
    req.write(data);
    req.end();
  });
}

function getUrl(url, headers = {}, timeoutMs = 5000) {
  return new Promise((resolve) => {
    const lib = url.startsWith('https') ? https : http;
    const u = new URL(url);
    const req = lib.request({
      method: 'GET',
      hostname: u.hostname,
      path: u.pathname + u.search,
      port: u.port || (url.startsWith('https') ? 443 : 80),
      headers: { 'User-Agent': 'synkia-health-probe/1.0', ...headers },
      timeout: timeoutMs,
    }, (res) => {
      let body = '';
      res.on('data', (c) => (body += c));
      res.on('end', () => resolve({
        ok: res.statusCode >= 200 && res.statusCode < 300,
        status: res.statusCode,
        body: body.slice(0, 256),
      }));
    });
    req.on('timeout', () => req.destroy(new Error('timeout')));
    req.on('error', (e) => resolve({ ok: false, status: 0, body: '', error: e.message }));
    req.end();
  });
}

function resolveApiKey(p) {
  if (!p || !p.apiKey) return null;
  const k = p.apiKey;
  if (typeof k === 'string') {
    if (k.startsWith('${') && k.endsWith('}')) {
      const envName = k.slice(2, -1).replace(/[^A-Z0-9_]/gi, '');
      return process.env[envName] || null;
    }
    return k; // literal key (e.g. "hub-local-gateway" or "sk-local")
  }
  if (typeof k === 'object' && k.source === 'file') {
    return { __vault_ref: k }; // signal vault reference, no usable key
  }
  return null;
}

// Per-provider probe URL strategy. Keeps gateway at the root /health
// (its baseUrl includes /v1), and routes remote providers to their /models endpoint.
function probeUrl(name, baseUrl, key) {
  if (!baseUrl) return null;
  const b = baseUrl.replace(/\/$/, '');
  switch (name) {
    case 'ollama':         return `${baseUrl}/api/tags`;
    case 'mlx-local':      return `${baseUrl}/v1/models`;
    case 'gateway':        return `${b.replace(/\/v1$/, '')}/health`;
    case 'gemini':         return `${baseUrl}/models`; // /models regardless of key header shape
    case 'nvidia':
    case 'inferx':
    case 'groq':
    case 'openai_compatible':
      return `${b}/models`;
    default:
      return baseUrl;
  }
}

// Probe a single provider.
// Returns { provider, base_ok, ts, sample_models: [{id, healthy, error?}] }
async function probeProvider(p, name) {
  if (!p) return { provider: name, base_ok: false, ts: new Date().toISOString(), error: 'no-provider' };
  const baseUrl = p.baseUrl;
  const result = { provider: name, base_url: baseUrl || null, ts: new Date().toISOString() };

  if (!baseUrl) {
    result.base_ok = false;
    result.error = 'no baseUrl';
    return result;
  }

  const key = resolveApiKey(p);
  let headers = {};
  let url;
  // Vault references can't be resolved here — note it and skip remote probe to avoid 401 storms.
  if (key && typeof key === 'object' && key.__vault_ref) {
    result.base_ok = false;
    result.status = 0;
    result.body_preview = '';
    result.error = `vault ref: ${key.__vault_ref.provider}:${key.__vault_ref.id}`;
    result.sample_models = (p.models || []).slice(0, 5).map((m) => ({
      id: m.id, full_id: `${name}/${m.id}`, healthy: false, error: result.error,
    }));
    return result;
  }
  // Per-provider auth strategy. Key prefix determines auth shape; baseUrl determines endpoint.
  //   AIza*    → Google AI Studio → X-goog-api-key header (NOT Bearer — Gemini rejects both)
  //   AQ.*     → Google Vertex ADCs → Authorization: Bearer (only valid for Vertex endpoints)
  //   nvapi-*  → NVIDIA build.nvidia.com / NIM → Authorization: Bearer
  //   sk-/gsk_/ix_/openai-* → OpenAI-compat → Authorization: Bearer
  //   others   → Authorization: Bearer (best-effort)
  if (typeof key === 'string' && key.length > 0) {
    if (key.startsWith('AIza')) {
      headers['X-goog-api-key'] = key;
      // When using X-goog-api-key, do NOT also send ?key= in the URL — keep URL clean.
      url = probeUrl(name, baseUrl, null);
    } else if (key.startsWith('AQ.')) {
      headers['Authorization'] = `Bearer ${key}`;
      url = probeUrl(name, baseUrl, key);
    } else {
      headers['Authorization'] = `Bearer ${key}`;
      url = probeUrl(name, baseUrl, key);
    }
  } else {
    url = probeUrl(name, baseUrl, null);
  }
  if (!url) {
    result.base_ok = false;
    result.error = 'no probe URL';
    return result;
  }
  const r = await getUrl(url, headers, 6000);
  result.base_ok = r.ok;
  result.status = r.status;
  result.body_preview = r.body;
  result.error = r.ok ? null : (r.error || `HTTP ${r.status}`);

  // Provider-specific fallbacks. Some APIs gate /v1/models behind auth scope;
  // we tolerate 404/405 on the listing endpoint if a tiny completion works.
  if (!result.base_ok && (result.status === 404 || result.status === 405) && typeof key === 'string') {
    const completion = await probeCompletion(name, baseUrl, key, p.models && p.models[0]);
    if (completion.ok) {
      result.base_ok = true;
      result.error = null;
      result.recovered_via = 'chat/completions';
      if (!result.body_preview || result.body_preview.length < 32) {
        result.body_preview = completion.body;
      }
    } else if (completion.status) {
      result.status = completion.status;
      result.error = completion.error || `HTTP ${completion.status}`;
    }
  }
  // 429 with a JSON body shaped like an API error means "key valid, throttled/billing".
  // Treat as healthy for credentials; record throttled flag.
  if (!result.base_ok && result.status === 429 && result.body_preview && result.body_preview[0] === '{') {
    result.base_ok = true;
    result.throttled = true;
    result.error = null;
  }

  // Per-model: assume all models in this provider inherit the provider status.
  if (!Array.isArray(p.models)) return result;
  result.sample_models = p.models.slice(0, 5).map((m) => ({
    id: m.id,
    full_id: `${name}/${m.id}`,
    healthy: r.ok,
    error: r.ok ? null : `${r.status} ${r.error || ''}`.trim(),
  }));
  return result;
}

function isLocalProvider(name) {
  return name === 'ollama' || name === 'mlx-local' || name === 'gateway';
}

// Update model-health.json merging in this run's probes.
// Preserves previous health stats, increments counters.
function mergeHealth(existing, probes) {
  const now = new Date().toISOString();
  const merged = (existing && typeof existing === 'object' && existing.models && typeof existing.models === 'object')
    ? structuredClone(existing)
    : { models: {}, last_updated: null };
  merged.last_updated = now;

  for (const probe of probes) {
    const allHealthy = probe.base_ok;
    const errMsg = allHealthy ? null : `${probe.status || 'ERR'} ${(probe.error || probe.body_preview || '').slice(0, 120)}`.trim();
    for (const m of (probe.sample_models || [])) {
      const key = m.full_id;
      const prev = merged.models[key] || { tests_passed: 0, tests_failed: 0, status: 'unknown', health_score: 0 };
      if (allHealthy) {
        prev.tests_passed = (prev.tests_passed || 0) + 1;
        prev.status = 'healthy';
        prev.health_score = Math.max(prev.health_score || 0, 100);
        prev.last_error = null;
      } else {
        prev.tests_failed = (prev.tests_failed || 0) + 1;
        if ((prev.tests_failed || 0) >= 2) {
          prev.status = 'degraded';
          prev.health_score = 70;
        }
        prev.last_error = errMsg;
      }
      prev.last_checked = now;
      merged.models[key] = prev;
    }
  }
  return merged;
}

function appendIncident(evt) {
  fs.mkdirSync(INCIDENT_DIR, { recursive: true });
  const stamp = new Date().toISOString().slice(0, 10);
  fs.appendFileSync(path.join(INCIDENT_DIR, `${stamp}.jsonl`), JSON.stringify({ ts: new Date().toISOString(), ...evt }) + '\n');
}

async function sendTelegramAlert(text) {
  if (process.env.ALERTS_TO_TELEGRAM !== 'true') return;
  const token = process.env.TELEGRAM_BOT_TOKEN;
  const chatId = process.env.TELEGRAM_CHAT_ID;
  if (!token || !chatId) return;
  try {
    const data = JSON.stringify({ chat_id: chatId, text, parse_mode: 'Markdown' });
    const u = new URL(`https://api.telegram.org/bot${token}/sendMessage`);
    await new Promise((resolve) => {
      const req = https.request({
        method: 'POST', hostname: u.hostname, path: u.pathname,
        headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(data) },
        timeout: 5000,
      }, () => resolve());
      req.on('error', () => resolve());
      req.write(data);
      req.end();
    });
  } catch (_) {}
}

async function runCycle() {
  const ts = new Date().toISOString();
  console.log(`[health-probe] cycle start at ${ts}`);
  const openclaw = readJsonSafe(OPENCLAW_JSON);
  const prevHealth = readJsonSafe(MODEL_HEALTH_JSON);
  if (openclaw.__error) {
    console.error('[health-probe] cannot read openclaw.json:', openclaw.__error);
    appendIncident({ kind: 'probe-error', message: openclaw.__error });
    return;
  }
  const providers = (openclaw.models && openclaw.models.providers) || {};
  const probes = [];
  for (const [name, p] of Object.entries(providers)) {
    const r = await probeProvider(p, name);
    probes.push(r);
    const tag = r.base_ok ? 'ok' : `FAIL(${r.status})`;
    console.log(`[probe] ${name}: ${tag} ${r.error ? '— ' + r.error : ''}`);
  }

  const merged = mergeHealth(prevHealth, probes);
  writeJsonSafe(MODEL_HEALTH_JSON, merged);

  // Refresh SSOT so other consumers see fresh data.
  try {
    const ssot = require(path.join(HOME, 'synkia/ssot.js'));
    ssot.refresh();
  } catch (e) {
    console.log('[health-probe] ssot refresh skipped:', e.message);
  }

  const failedLocals = probes.filter(p => isLocalProvider(p.provider) && !p.base_ok);
  if (failedLocals.length) {
    const msg = failedLocals.map(p => `🚨 ${p.provider}: ${p.status || 'err'} ${p.error || ''}`).join('\n');
    appendIncident({ kind: 'provider-degraded-snapshot', providers: failedLocals.map(p => p.provider) });
    await sendTelegramAlert(`🩺 *synkia-health-probe* — local provider degraded:\n${msg}`);
  }

  console.log(`[health-probe] done. ${probes.filter(p => p.base_ok).length}/${probes.length} providers ok. model-health.json updated.`);
}

function scheduleNext() {
  return setInterval(() => {
    runCycle().catch((e) => console.error('[health-probe] cycle-err:', e.message));
  }, INTERVAL_MS);
}

async function main() {
  console.log(`[health-probe] alive (interval=${INTERVAL_MS}ms)`);
  await runCycle().catch((e) => console.error('[health-probe] initial-err:', e.message));
  scheduleNext();
}
process.on('SIGINT',  () => { console.log('[health-probe] SIGINT, exit'); process.exit(0); });
process.on('SIGTERM', () => { console.log('[health-probe] SIGTERM, exit'); process.exit(0); });
if (require.main === module) main();
