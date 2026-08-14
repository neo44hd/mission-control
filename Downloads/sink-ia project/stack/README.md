# SynK-IA Stack — Cohesion 2026

> Single-source-of-truth wiring, auto-healing supervisor, and trends endpoints
> for the 9-provider LLM stack orchestrating Ollama, NVIDIA, NVIDIA-NIM, Gemini,
> OpenRouter, Groq, inferX, MLX-Local, and the local SynK-IA hub.

## Topología (puertos verificados escuchando)

| Servicio              | Puerto | Manejado por |
|-----------------------|--------|---------------|
| synkia-hub (BATCAVE)  | 3020   | PM2 |
| synos-panel (BrainCC) | 3333   | PM2 |
| ruflo-orchestrator    | 8081   | PM2 |
| hermes-bus (Python)   | 8082   | launchd `dev.synkia.os-orchestrator` |
| mission-control       | 9302   | PM2 |
| synkia-orchestrator   | 9500   | PM2 |
| synkia-model-selector | 9501   | PM2 |
| **synkia-trends**     | 9700   | PM2 (nuevo) |
| **synkia-watchdog**   | —      | PM2 (loop 60s) |
| **synkia-health-probe**| —     | PM2 (loop 6h) |
| ollama                | 11434  | launchd `com.brew.ollama` |
| openclaw gateway      | 18790  | launchd `ai.openclaw.gateway` |
| **velin-dabot**       | —      | PM2 (Telegram polling, antes huérfano) |
| **mlx-local-server**  | 4001   | PM2 (mlx_lm.server, Hermes-4-14B) |

(Total: 14 procesos bajo PM2.)

## Componentes nuevos (commit actual)

### `scripts/ssot.js`
SSOT (Single Source Of Truth). Walker de los 9 providers de `~/.openclaw/openclaw.json`:
caminata por todos los bloques, validación de `apiKey`, hash de health contra
`~/.openclaw/model-health.json`, secretos redactados en el cache.
Salida: `~/.synkia-ai-hub/openclaw-ssot.json`.

### `scripts/synk-ia-watchdog.js`
Cada 60s pinguea `/health` de los PM2-services. Matcher tolerante a
`{success:true}`, `{status:true}`, `{healthy:true}`, `{ok:true}`.
Restart con throttle 5 min. Telegram alerts con chat_id fallback
(env → velin-dabot .env → openclaw.json).

### `scripts/synk-ia-health-probe.js`
Cada 6h pings cada provider con su auth correcto:
- `AIza*`  → `X-goog-api-key` (Gemini AI Studio)
- `nvapi-*` → `Authorization: Bearer` (NVIDIA / NIM)
- `sk-/gsk_/ix_` → `Authorization: Bearer` (OpenAI-compat)
- Default → `Authorization: Bearer`
Fallback `chat/completions` cuando `/v1/models` retorna 404/5 (NIM).
429 con body JSON → throttling, no degradación.

### `scripts/synk-ia-trends.js`
HTTP `:9700`. Endpoints:
- `GET /health`
- `GET /api/trends/models`
- `GET /api/trends/services`
- `GET /api/alerts/recent`
- `GET /api/summary`
- `GET /` (dashboard HTML)

### `configs/ecosystem.config.js`
PM2 single-source-of-truth para los 14 servicios. Cada proceso declara
`autorestart`, `restart_delay`, `max_restarts`, `min_uptime`, `max_memory`,
`exp_backoff`. **Solo `openclaw` (launchd externo) lleva las claves de providers;
los demás consumen vía env o el SSOT cache.**

## Cambios en scripts pre-existentes (patches)

Estos edits viven fuera del repo (en `~/synk-ia-orchestrator.js`,
`~/synk-ia-model-selector.js`, `~/synkia/bots/velin-dabot/synkia-bot-es.js`).
Backups en `~/.stk/backups/<timestamp>/`.

### `synk-ia-orchestrator.js` (línea 50–63)
Bloque nuevo al arrancar: `ssot.refresh()` para popular cache, log con
`📡 OpenClaw SSOT synced: N models`. Antes: sin cache, cada consumer
leía openclaw.json por su cuenta.

### `synk-ia-model-selector.js` (después de línea 336)
Nueva ruta `/api/model-selector/openclaw-models` que sirve el SSOT.
503 si el cache falta, con hint: `node ~/synkia/ssot.js --refresh`.

### `synkia/bots/velin-dabot/synkia-bot-es.js` (líneas 1–37)
- `require('dotenv').config()` + lectura de openclaw.json channels.telegram
  → token fallback chain.
- Resolución de modelo: lee SSOT, prefiere healthy local,
  fallback `qwen2.5:7b` legacy.
- Compatible con `node-telegram-bot-api@1.2.0` (exporta como objeto).

## Configuración de `~/.openclaw/openclaw.json` post-plan

9 providers × 65 modelos totales, todos con claves reales:

| Provider             | # Modelos | Auth | Notas |
|----------------------|-----------|------|-------|
| ollama               | 2         | n/a  | local |
| gateway (hub)        | 11        | n/a  | local (sin auth) |
| gemini               | 3         | `X-goog-api-key` | AI Studio |
| nvidia               | 7         | `Bearer nvapi-…` | build.nvidia.com |
| inferx               | 1         | `Bearer ix_…` | inferX endpoint |
| mlx-local            | 2         | `Bearer sk-local` | Hermes-4 + Gemma-4 |
| openai_compatible    | 26        | `Bearer ${OPENROUTER…}` | openrouter |
| groq                 | 4         | `Bearer gsk_…` | groq |
| nim                  | 7         | `Bearer nvapi-…` | NVIDIA NIM |

## Cómo operar

### Estado consolidado (visual)
```bash
curl -s http://127.0.0.1:9700/dashboard            # HTML
curl -s http://127.0.0.1:9700/api/summary | jq    # JSON
```

### Refresh SSOT manual
```bash
node ~/synkia/ssot.js --refresh
```

### Backup completo antes de editar
```bash
TS=$(date +%Y%m%d-%H%M%S); BAK=~/.stk/backups/$TS; mkdir -p $BAK; \
  cp ~/.openclaw/openclaw.json $BAK/ && \
  cp ~/.openclaw/model-health.json $BAK/ && \
  cp ~/.pm2/dump.pm2 $BAK/ && \
  cp -r ~/synkia/ssot.js $BAK/ && \
  cp ~/synk-ia-{watchdog,health-probe,trends,orchestrator,model-selector}.js $BAK/ && \
  echo "backup: $BAK"
```

### Resolver incidente (ej: conexión rechazada en :4001)
```bash
pm2 restart mlx-local-server
# Logs: ~/.pm2/logs/mlx-local-server-{out,error}.log
```

## Estado verificado en última ejecución

| Provider    | Tracked | OK | Degraded | Comentario |
|-------------|---------|----|---------|----------|
| ollama      | 2       | 2  | 0       | local |
| gateway     | 5       | 5  | 0       | subconjunto probeado |
| gemini      | 3       | 3  | 0       | throttled por billing, auth válida |
| nvidia      | 7       | 7  | 0       | build.nvidia.com |
| inferx      | 1       | 1  | 0       | |
| mlx-local   | 2       | 2  | 0       | Hermes-4-14B + Gemma-4-31B |
| openai_comp | 5       | 5  | 0       | subconjunto |
| groq        | 4       | 4  | 0       | |
| nim         | 7       | 5  | 0+2 unk | alcance via /chat/completions |
| **TOTAL**   | 36+     | 34 |       | 9/9 providers OK |

(Degradaciones restantes son modelos OpenRouter free con rate-limit histórico;
no son credential issues.)

## Changelog
- 2026-08-14: Initial stack cohesion. SSOT walker, watchdog, health-probe, trends endpoint, ecosystem.config.js, provider key wiring (NVIDIA, NIM, Gemini AI Studio). velin-dabot bajo PM2 con fallback chain de tokens. mlx-local-server arrancado en :4001.

