/**
 * SynK-IA PM2 ecosystem.config.js v1.0
 * ═══════════════════════════════════════════════════════════════════════════════
 * Single source of truth for PM2-managed services in the SynK-IA stack.
 *
 * Launchd-managed services (out of PM2 scope):
 *   - ai.openclaw.gateway   (:18790)          brew/openclaw
 *   - com.synkia.openclaw, com.synkia.litellm, dev.synkia.os-orchestrator,
 *     dev.synkia.mission-control (alt PID), com.synkia.odysseus,
 *     com.synkia.ruflow, com.synkia.main-server, dev.synkia.commerce
 *
 * Apply NEW processes only (no `pm2 delete all` to avoid downtime):
 *   pm2 start ecosystem.config.js --only velin-dabot
 *   pm2 start ecosystem.config.js --only synkia-watchdog
 *   pm2 start ecosystem.config.js --only synkia-health-probe
 *   pm2 start ecosystem.config.js --only synkia-trends
 *   pm2 save
 * ═══════════════════════════════════════════════════════════════════════════════
 */

const path = require('path');
const HOME = '/Users/davidnows';

module.exports = {
  apps: [
    // ── Core AI / provider surface ────────────────────────────────────────
    {
      name: 'synkia-hub',
      cwd: path.join(HOME, 'synkia/ai-provider-hub'),
      script: 'server/index.js',
      args: '--port 3020',
      autorestart: true,
      restart_delay: 5000,
      max_restarts: 20,
      min_uptime: '30s',
      max_memory: '300M',
      exp_backoff: true,
      env: { PORT: '3020', NODE_ENV: 'production' },
    },

    // ── Orchestrator + model selector ─────────────────────────────────────
    {
      name: 'synkia-orchestrator',
      cwd: HOME,
      script: 'synk-ia-orchestrator.js',
      autorestart: true,
      restart_delay: 5000,
      max_restarts: 20,
      min_uptime: '30s',
      max_memory: '512M',
      exp_backoff: true,
      env: {
        ORCHESTRATOR_PORT: '9500',
        NODE_ENV: 'production',
        CONFIG_PATH: path.join(HOME, 'synk-ia-global-config.yaml'),
      },
    },
    {
      name: 'synkia-model-selector',
      cwd: HOME,
      script: 'synk-ia-model-selector.js',
      autorestart: true,
      restart_delay: 5000,
      max_restarts: 20,
      min_uptime: '30s',
      max_memory: '128M',
      exp_backoff: true,
      env: {
        MODEL_SELECTOR_PORT: '9501',
        NODE_ENV: 'production',
        CONFIG_PATH: path.join(HOME, 'synk-ia-global-config.yaml'),
      },
    },

    // ── Connectors / proxies ──────────────────────────────────────────────
    {
      name: 'ruflo-orchestrator',
      cwd: path.join(HOME, 'sinkia-connectors'),
      script: 'ruflo-proxy.js',
      autorestart: true,
      restart_delay: 5000,
      max_restarts: 20,
      min_uptime: '30s',
      max_memory: '128M',
      exp_backoff: true,
      env: { PORT: '8081', NODE_ENV: 'production' },
    },
    {
      name: 'hermes-bus',
      cwd: path.join(HOME, '.hermes/hermes-agent'),
      script: path.join(HOME, '.local/bin/hermes'),
      args: 'serve --port 8082 --host 127.0.0.1 --skip-build',
      interpreter: 'none',
      autorestart: true,
      restart_delay: 10000,
      max_restarts: 10,
      min_uptime: '60s',
      max_memory: '512M',
      exp_backoff: true,
      env: { NODE_ENV: 'production', HERMES_YOLO_MODE: 'false' },
    },
    // hermes-bus-proxy intentionally LEFT STOPPED. Restart only if needed.
    // {
    //   name: 'hermes-bus-proxy',
    //   cwd: path.join(HOME, 'sinkia-connectors'),
    //   script: 'hermes-proxy.js',
    //   autorestart: false,
    //   env: { PORT: '8083' },  // different port (8082 owned by Python)
    // },

    // ── Mission control / dashboard ───────────────────────────────────────
    {
      name: 'mission-control',
      cwd: HOME,
      script: 'mission-control/server.js',
      autorestart: true,
      restart_delay: 5000,
      max_restarts: 20,
      min_uptime: '30s',
      max_memory: '256M',
      exp_backoff: true,
      env: { APP_PORT: '9302', NODE_ENV: 'production' },
    },
    {
      name: 'synos-panel',
      cwd: path.join(HOME, 'remote-machine-server'),
      script: 'src/index.js',
      autorestart: true,
      restart_delay: 5000,
      max_restarts: 20,
      min_uptime: '30s',
      max_memory: '256M',
      exp_backoff: true,
      env: { NODE_ENV: 'production', PORT: '3333' },
    },

    // ── Tunnel (separate config; do NOT pass provider keys here) ──────────
    {
      name: 'cloudflared-tunnel',
      cwd: HOME,
      script: '/opt/homebrew/bin/cloudflared',
      args: 'tunnel --config /Users/davidnows/.cloudflared/config.yml run',
      interpreter: 'none',
      autorestart: true,
      restart_delay: 10000,
      max_restarts: 50,
      min_uptime: '30s',
      max_memory: '128M',
      exp_backoff: true,
    },

    // ── NEW: Telegram bot (was orphan before this plan) ───────────────────
    {
      name: 'velin-dabot',
      cwd: path.join(HOME, 'synkia/bots/velin-dabot'),
      script: 'synkia-bot-es.js',
      autorestart: true,
      restart_delay: 10000,
      max_restarts: 15,
      min_uptime: '60s',
      max_memory: '256M',
      exp_backoff: true,
      env: {
        NODE_ENV: 'production',
        TELEGRAM_BOT_TOKEN: process.env.TELEGRAM_BOT_TOKEN || '',
        TELEGRAM_CHAT_ID: process.env.TELEGRAM_CHAT_ID || '',
        FUNNEL_URL: process.env.FUNNEL_URL || '',
        TOKEN: process.env.TOKEN || '',
        MODEL_DEFAULT: process.env.MODEL_DEFAULT || '',
      },
    },

    // ── NEW: Watchdog (auto-restart supervisor) ───────────────────────────
    {
      name: 'synkia-watchdog',
      cwd: HOME,
      script: 'synk-ia-watchdog.js',
      autorestart: true,
      restart_delay: 30000,
      max_restarts: 5,
      min_uptime: '60s',
      max_memory: '128M',
      env: {
        NODE_ENV: 'production',
        WATCHDOG_INTERVAL_MS: '60000',
        ALERTS_TO_TELEGRAM: 'true',
      },
    },

    // ── NEW: Health-probe (refreshes ~/.openclaw/model-health.json) ───────
    {
      name: 'synkia-health-probe',
      cwd: HOME,
      script: 'synk-ia-health-probe.js',
      autorestart: true,
      restart_delay: 30000,
      max_restarts: 5,
      min_uptime: '60s',
      max_memory: '128M',
      env: {
        NODE_ENV: 'production',
        PROBE_INTERVAL_MS: String(6 * 60 * 60 * 1000), // 6h
        OPENCLAW_BASE_URL: 'http://127.0.0.1:18790',
      },
    },

    // ── NEW: Trends endpoint (read-only JSON API) ─────────────────────────
    {
      name: 'synkia-trends',
      cwd: HOME,
      script: 'synk-ia-trends.js',
      autorestart: true,
      restart_delay: 5000,
      max_restarts: 10,
      min_uptime: '30s',
      max_memory: '256M',
      env: {
        NODE_ENV: 'production',
        TRENDS_PORT: '9700',
      },
    },
  ],
};
