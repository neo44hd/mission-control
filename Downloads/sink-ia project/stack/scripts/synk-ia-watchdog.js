#!/usr/bin/env node
/**
 * synkia-watchdog v1.0
 * ═══════════════════════════════════════════════════════════════════════════════
 * Supervises PM2-managed services in the SynK-IA stack.
 *
 * Every WATCHDOG_INTERVAL_MS (default 60s):
 *   1. Reads pm2 jlist for active processes under our supervision.
 *   2. For each one with a known /health port, runs a 5s timeout GET /health.
 *      - HTTP 200 with body.healthy==true OR 2xx → OK
 *      - Anything else (timeout, 5xx, 4xx, connection refused) → RESTART via pm2.
 *   3. For velin-dabot, additionally pings Telegram /getMe to verify the bot
 *      is registered and the token is still valid.
 *   4. Logs incidents to ~/.synkia/incidents/YYYY-MM-DD.jsonl (one line per event).
 *   5. If ALERTS_TO_TELEGRAM=true and incidents > 0 since last cycle, sends
 *      a Telegram alert via the existing velin-dabot channel.
 *
 * Self-loop is NORMALLY the supervisor under PM2 (max_restarts:5) — but if
 * we crash, PM2 restarts us, so this is safe to run unattended.
 * ═══════════════════════════════════════════════════════════════════════════════
 */
'use strict';

const fs = require('fs');
const path = require('path');
const http = require('http');
const https = require('https');
const { exec } = require('child_process');

const HOME = '/Users/davidnows';
const INCIDENT_DIR = path.join(HOME, '.synkia/incidents');
const INTERVAL_MS = parseInt(process.env.WATCHDOG_INTERVAL_MS || '60000', 10);
const ALERTS_TO_TELEGRAM = (process.env.ALERTS_TO_TELEGRAM || 'false') === 'true';

// ── Service catalog (PM2 name → health endpoint + restart cooldown) ──
// Skip self to avoid restart loop; skip cloudflared-tunnel (no HTTP /health).
const TARGETS = [
  { name: 'synkia-hub',           url: 'http://127.0.0.1:3020/health',     kind: 'http' },
  { name: 'synkia-orchestrator',  url: 'http://127.0.0.1:9500/health',     kind: 'http' },
  { name: 'synkia-model-selector',url: 'http://127.0.0.1:9501/health',     kind: 'http' },
  { name: 'ruflo-orchestrator',   url: 'http://127.0.0.1:8081/health',     kind: 'http' },
  { name: 'mission-control',      url: 'http://127.0.0.1:9302/',           kind: 'http' },
  { name: 'synos-panel',          url: 'http://127.0.0.1:3333/health',     kind: 'http' },
  { name: 'synkia-trends',        url: 'http://127.0.0.1:9700/health',     kind: 'http' },
  { name: 'velin-dabot',          url: null,                                kind: 'telegram' },
];

// Per-service restart throttle (only restart if lastRestart < minIntervalMs ago)
const lastRestart = new Map();
const RESTART_BACKOFF_MS = 5 * 60 * 1000; // 5 min

// ── Utilities ────────────────────────────────────────────────────────────────
function ensureDir(p) {
  fs.mkdirSync(p, { recursive: true });
}
function logLine(s) {
  process.stdout.write(`[${new Date().toISOString()}] ${s}\n`);
}
function todayFile() {
  const d = new Date();
  const stamp = d.toISOString().slice(0, 10);
  return path.join(INCIDENT_DIR, `${stamp}.jsonl`);
}
function appendIncident(evt) {
  ensureDir(INCIDENT_DIR);
  const line = JSON.stringify({ ts: new Date().toISOString(), ...evt }) + '\n';
  fs.appendFile(todayFile(), line, () => {});
}

function run(cmd) {
  return new Promise((resolve) => {
    exec(cmd, { timeout: 30000 }, (err, stdout, stderr) => {
      resolve({ err, stdout, stderr });
    });
  });
}

function getJson(url, timeoutMs = 5000) {
  return new Promise((resolve) => {
    const lib = url.startsWith('https') ? https : http;
    const req = lib.get(url, { timeout: timeoutMs }, (res) => {
      let body = '';
      res.on('data', (c) => (body += c));
      res.on('end', () => {
        let parsed = null;
        try { parsed = JSON.parse(body); } catch (_) {}
        resolve({ ok: res.statusCode >= 200 && res.statusCode < 300, status: res.statusCode, body, parsed });
      });
    });
    req.on('timeout', () => { req.destroy(new Error('timeout')); });
    req.on('error', (err) => resolve({ ok: false, status: 0, body: '', parsed: null, error: err.message }));
  });
}

// ── Telegram credentials ──────────────────────────────────────────────────────
// All three (token, chat_id, alert_chat_id) follow the same precedence:
//   1. process.env (PM2 or shell)
//   2. /Users/davidnows/synkia/bots/velin-dabot/.env  (read .kv)
//   3. /Users/davidnows/.openclaw/openclaw.json      (channels.telegram)
function readEnvKv(path, keys) {
  try {
    const text = fs.readFileSync(path, 'utf8');
    const out = {};
    for (const k of keys) {
      const m = text.match(new RegExp('^\\s*' + k + '\\s*=\\s*(.+)$', 'm'));
      if (m) out[k] = m[1].trim().replace(/^['"]|['"]$/g, '');
    }
    return out;
  } catch (_) { return {}; }
}
function resolveBotToken() {
  if (process.env.TELEGRAM_BOT_TOKEN) return process.env.TELEGRAM_BOT_TOKEN;
  const envK = readEnvKv('/Users/davidnows/synkia/bots/velin-dabot/.env', ['TELEGRAM_BOT_TOKEN']);
  if (envK.TELEGRAM_BOT_TOKEN) return envK.TELEGRAM_BOT_TOKEN;
  try {
    const oc = JSON.parse(fs.readFileSync('/Users/davidnows/.openclaw/openclaw.json', 'utf8'));
    return oc.channels?.telegram?.botToken || null;
  } catch (_) {}
  return null;
}
function resolveChatId() {
  if (process.env.TELEGRAM_CHAT_ID) return process.env.TELEGRAM_CHAT_ID;
  if (process.env.ALERT_CHAT_ID) return process.env.ALERT_CHAT_ID;
  const envK = readEnvKv('/Users/davidnows/synkia/bots/velin-dabot/.env', ['TELEGRAM_CHAT_ID', 'ALERT_CHAT_ID']);
  if (envK.TELEGRAM_CHAT_ID) return envK.TELEGRAM_CHAT_ID;
  if (envK.ALERT_CHAT_ID) return envK.ALERT_CHAT_ID;
  return null;
}

async function alertTelegram(text) {
  if (!ALERTS_TO_TELEGRAM) return;
  const token = resolveBotToken();
  const chatId = resolveChatId();
  if (!token || !chatId) {
    logLine(`[alert-skip] no TELEGRAM credentials (token=${!!token} chat=${!!chatId})`);
    return;
  }
  const url = `https://api.telegram.org/bot${token}/sendMessage`;
  try {
    const resp = await new Promise((resolve) => {
      const data = JSON.stringify({ chat_id: chatId, text, parse_mode: 'Markdown', disable_web_page_preview: true });
      const u = new URL(url);
      const req = https.request({
        method: 'POST',
        hostname: u.hostname,
        path: u.pathname,
        headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(data) },
        timeout: 5000,
      }, (res) => {
        let body = '';
        res.on('data', (c) => (body += c));
        res.on('end', () => resolve({ status: res.statusCode, body }));
      });
      req.on('error', (e) => resolve({ status: 0, body: e.message }));
      req.write(data);
      req.end();
    });
    logLine(`[alert-tg] ${resp.status}: ${String(resp.body).slice(0, 120)}`);
  } catch (err) {
    logLine(`[alert-tg-err] ${err.message}`);
  }
}

// ── Health probes ─────────────────────────────────────────────────────────────
// Accept any of the conventional success markers in JSON health bodies.
function isHealthyBody(parsed) {
  if (!parsed || typeof parsed !== 'object') return true; // 2xx with no body → ok
  if (parsed.healthy === true) return true;
  if (parsed.ok === true) return true;
  if (parsed.success === true) return true;
  if (parsed.status === true) return true;
  if (typeof parsed.status === 'string' && parsed.status.toLowerCase() === 'healthy') return true;
  if (parsed.service && parsed.uptime != null && !parsed.error) return true; // BATCAVE-style {service,uptime}
  return false;
}

async function checkHttp(t) {
  const r = await getJson(t.url, 5000);
  const healthy = r.ok && isHealthyBody(r.parsed);
  return { ...t, healthy, status: r.status, error: r.error || null, body: r.parsed };
}

async function checkTelegram(t) {
  const token = resolveBotToken();
  if (!token) return { ...t, healthy: false, error: 'no-bot-token', status: 0 };
  const r = await getJson(`https://api.telegram.org/bot${token}/getMe`, 6000);
  const healthy = !!r.parsed && r.parsed.ok === true;
  return { ...t, healthy, status: r.status, error: r.error || null, body: r.parsed };
}

async function isProcessOnline(pmName) {
  const r = await run(`pm2 jlist 2>/dev/null`);
  if (r.err) return false;
  try {
    const list = JSON.parse(r.stdout);
    return list.some((p) => p.name === pmName && p.pm2_env && p.pm2_env.status === 'online');
  } catch (_) {
    return false;
  }
}

async function restartWithBackoff(pmName) {
  const last = lastRestart.get(pmName) || 0;
  const now = Date.now();
  if (now - last < RESTART_BACKOFF_MS) {
    logLine(`[throttle] ${pmName} not restarted (last=${last} now=${now} diff=${now - last}ms)`);
    return false;
  }
  logLine(`[restart] ${pmName}`);
  const r = await run(`pm2 restart ${pmName}`);
  if (r.err) {
    logLine(`[restart-err] ${pmName}: ${r.stderr || r.err.message}`);
    return false;
  }
  lastRestart.set(pmName, now);
  return true;
}

// ── Main cycle ────────────────────────────────────────────────────────────────
async function cycle() {
  logLine('cycle start');
  const issues = [];
  for (const t of TARGETS) {
    const online = await isProcessOnline(t.name);
    if (!online) {
      // PM2 will autorestart by itself; we just note it once.
      issues.push({ name: t.name, kind: t.kind, problem: 'pm2-status-not-online' });
      appendIncident({ kind: 'pm2-offline', process: t.name });
      continue;
    }
    const check = t.kind === 'telegram' ? await checkTelegram(t) : await checkHttp(t);
    if (!check.healthy) {
      logLine(`[unhealthy] ${t.name} status=${check.status} err=${check.error}`);
      appendIncident({
        kind: 'health-fail',
        process: t.name,
        status: check.status,
        error: check.error,
        body: check.body ? Object.keys(check.body).slice(0, 6) : null,
      });
      const did = await restartWithBackoff(t.name);
      issues.push({ name: t.name, restart_attempted: did });
    } else {
      logLine(`[ok] ${t.name}`);
    }
  }
  if (issues.length > 0) {
    const msg = issues.map(i => `• ${i.name} → ${i.problem || i.kind} (restart: ${i.restart_attempted ? 'YES' : 'no'})`).join('\n');
    await alertTelegram(`🐺 *synkia-watchdog* — issues detected:\n${msg}`);
  }
  logLine('cycle done');
}

function start() {
  ensureDir(INCIDENT_DIR);
  logLine(`watchdog alive (interval=${INTERVAL_MS}ms alerts=${ALERTS_TO_TELEGRAM})`);
  cycle().catch((e) => logLine(`[cycle-err] ${e.message}`));
  setInterval(() => {
    cycle().catch((e) => logLine(`[cycle-err] ${e.message}`));
  }, INTERVAL_MS);
}

process.on('SIGINT',  () => { logLine('SIGINT, exit'); process.exit(0); });
process.on('SIGTERM', () => { logLine('SIGTERM, exit'); process.exit(0); });

if (require.main === module) start();
