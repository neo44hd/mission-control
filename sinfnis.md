# SINFNIS — Informe del proceso y configuraciones

Fecha: 2026-06-17 · Máquina: Davids-Mac-mini-2 (macOS) · Autor: Oz

Documento de síntesis de todo el trabajo realizado para unificar los LLMs (locales + nube) tras un único gateway, cablear todos los agentes a él, dar resiliencia/autorreparación y mover los modelos a disco externo.

---

## 1. Resumen ejecutivo

Se ha construido un **gateway maestro de LLMs (LiteLLM)** que expone un único endpoint OpenAI‑compatible en `http://127.0.0.1:4000` y agrega todos los proveedores (LM Studio, Ollama y nube: OpenRouter, Gemini, NVIDIA, Anthropic) bajo **alias estables**. Todos los agentes de la máquina (OpenClaw, sinkia, local‑claude‑code) apuntan a ese gateway. Se añadió autorreparación, se corrigieron configuraciones rotas y se movieron los modelos (~84 GB) al disco externo, liberando el disco principal de 28 GB → 105 GB libres.

---

## 2. Arquitectura final

```
  Agentes                         Gateway (LiteLLM :4000)            Backends
  ───────                         ───────────────────────            ────────
  OpenClaw (main/brain/coder/  ┐                                  ┌ LM Studio :1234  (modelos en disco externo)
            docs/monitor)      │                                  │ Ollama   :11434  (modelos en disco externo)
  sinkia-api (classify/extract ├──►  alias → modelo real  ────────┤ OpenRouter (nube)
            /deep/analyzer/... )│     + fallbacks + retries        │ Gemini    (nube)
  local-claude-code (Devstral) ┘     + context-window fallbacks    │ NVIDIA    (nube)
                                                                   └ Anthropic (nube)
```

Punto único de fallo mitigado con: auto‑reinicio PM2 + watchdog + fallbacks internos del gateway + providers nativos de OpenClaw como respaldo.

---

## 3. Gateway LiteLLM (núcleo)

- Servicio PM2: **`llm-gateway`** (escucha solo en loopback `127.0.0.1:4000`, sin master key — prototipo local).
- Ficheros (en `~/.openclaw/litellm/`):
  - `config.yaml` — `model_list` con los alias + `litellm_settings` (drop_params, num_retries=2, request_timeout=600, fallbacks y context_window_fallbacks).
  - `.env` (chmod 600) — claves de nube: `OPENROUTER_API_KEY`, `GEMINI_API_KEY`, `NVIDIA_API_KEY`, `ANTHROPIC_API_KEY` (inyectadas desde el vault `~/.openclaw/credentials/providers.json` y `~/.claude/settings.json`).
  - `run-gateway.sh` — lanzador (carga `.env` y ejecuta `litellm --config ... --host 127.0.0.1 --port 4000`).
- Arranque/persistencia: `pm2 start ~/.openclaw/litellm/run-gateway.sh --name llm-gateway --interpreter bash --max-restarts 15 --exp-backoff-restart-delay=200` + `pm2 save`.

### Alias de modelos (nombre estable → backend real)
- `local-fast` → Ollama `llama3.2:3b`
- `local-coder` → LM Studio `mistralai/devstral-small-2-2512` (coding)
- `local-coder-ollama` → Ollama `qwen2.5-coder:7b`
- `local-reason` → LM Studio `deepseek-r1-0528-qwen3-8b` (razonamiento)
- `local-oss` → LM Studio `openai/gpt-oss-20b`
- `local-big` → LM Studio `qwen3.6-40b-…-code` (potente)
- `local-vision` → LM Studio `glm-4.6v-flash` (visión)
- `cloud-auto` → OpenRouter `auto`
- `cloud-gemini` → `gemini-flash-latest`
- `cloud-nvidia` → `meta/llama-3.3-70b-instruct`
- `cloud-claude` → `claude-sonnet-4-6`

### Fallbacks
- Por caída de backend: cada `local-*` cae a un equivalente y, en último término, a `cloud-auto`.
- Por desbordamiento de contexto (`context_window_fallbacks`): los locales saltan a `cloud-auto` / `cloud-gemini` (gran contexto).

---

## 4. Autorreparación / fiabilidad

- PM2 con límite de reinicios + backoff exponencial (`pm2 save`).
- Watchdog: `~/.openclaw/litellm/watchdog.sh` ejecutado por el LaunchAgent `~/Library/LaunchAgents/ai.openclaw.llm-gateway-watchdog.plist` cada 120 s; si `GET /health/liveliness` falla 3 veces seguidas, hace `pm2 restart llm-gateway`.
- Verificado: matando el proceso del gateway, PM2 lo revivió automáticamente.

---

## 5. OpenClaw (`~/.openclaw/openclaw.json`)

- Nuevo provider **`gateway`**: `baseUrl http://127.0.0.1:4000/v1`, `api openai-completions`, `apiKey "gateway-local"` (dummy), con los 11 alias y su `contextWindow` realista.
- Modelo por agente:
  - `main` → `gateway/cloud-auto`
  - `brain` → `gateway/local-reason`
  - `coder` → `gateway/local-coder`
  - `docs` → `gateway/local-fast`
  - `monitor` → `gateway/local-fast`
  - `agents.defaults.model` → `gateway/local-fast`
- Providers nativos (ollama/gemini/nvidia/openrouter) se conservan como **respaldo**.
- Buffer de compactación: `agents.defaults.compaction.reserveTokensFloor = 24000` (evita el error "Auto-compaction could not recover"; se capa por modelo).
- Se respetaron canales/Telegram/skills (no modificados).

---

## 6. local-claude-code (tu Claude Code con fuente) → Devstral

- Cliente reescrito a **OpenAI‑compatible** en `src/ollama-client.ts` (`/v1/chat/completions`, `/v1/models`), conservando la API de la clase.
- Defaults en `src/cli.ts`: endpoint → `http://127.0.0.1:4000` (gateway), modelo → `local-coder` (Devstral). Recompilado (`npm run build`).
- Uso: `node /Users/davidnows/local-claude-code/dist/cli.js "<tarea>"` · override con `OLLAMA_MODEL=local-reason|local-big|cloud-auto`.
- Verificado: `healthy: true`, responde, y Devstral carga desde el disco externo.

---

## 7. Modelos en disco externo (liberar disco principal)

- **LM Studio** (~78 GB): `~/.lmstudio/models` → copiado a `"/Volumes/Disco local/lmstudio/models"`; original sustituido por **symlink**. Verificado: LM Studio sirve y carga modelos desde el disco externo.
- **Ollama** (~6.3 GB): `docker cp` fuera del contenedor → recreado `sinkia-ollama` con **bind‑mount** `-v "/Volumes/Disco local/ollama-data:/root/.ollama"` (env `OLLAMA_NUM_PARALLEL=1`, `OLLAMA_MAX_LOADED_MODELS=1`, healthcheck `ollama ps`). Volumen Docker antiguo eliminado.
- Resultado: disco `/` de **28 GB → 105 GB libres** (11% usado). `Disco local`: 501 GB libres.

---

## 8. sinkia (`/Users/davidnows/sinkia-next/server/.env`)

- Cada agente con `<AGENTE>_PROVIDER = lmstudio` y `LMSTUDIO_URL = http://127.0.0.1:4000/v1` (gateway). Modelos por alias:
  - `CLASSIFY_MODEL`, `EXTRACT_MODEL`, `HR_MODEL` → `local-fast`
  - `DEEP_MODEL`, `ANALYZER_MODEL`, `DOC_AGENT_MODEL`, `ACCOUNTING_MODEL`, `LEGAL_MODEL` → `local-reason`
- Sustituye los modelos rotos previos (`harmonic-hermes-9b`, `qwen36-tools`, inexistentes).
- Backup: `server/.env.bak-gateway`. NO se tocaron `TELEGRAM_BOT_TOKEN` ni la config de bots. `sinkia-api` reiniciado.

---

## 9. Saneamiento previo realizado (contexto)

- Gateway de OpenClaw: token reconciliado (launchd/.zshrc/env del servicio) → `health ok`.
- Ollama: se resolvió el conflicto de puerto 11434 (se paró el Ollama nativo; el contenedor Docker quedó como único), healthcheck corregido (usaba `curl` inexistente → `ollama ps`), env a 1/1.
- Docker: arreglado healthcheck de `sinkia-qdrant` (bash/`/dev/tcp`); levantado `n8n`; eliminados huérfanos de `commerce` (contenedores + volúmenes) y el `sinkia-api` `Created`.
- Modelos Ollama: sustituidos los borrados por `llama3.2:3b` + `qwen2.5-coder:7b`.

---

## 10. Cómo usar / operar

- Probar el gateway: `curl http://127.0.0.1:4000/v1/models` · chat: `POST /v1/chat/completions` con `"model":"<alias>"`.
- Estado del gateway: `pm2 status llm-gateway` · logs: `pm2 logs llm-gateway`.
- Cambiar el modelo de un agente OpenClaw: editar su `model` en `~/.openclaw/openclaw.json` (alias `gateway/<alias>`) y `openclaw gateway restart`.
- Cambiar modelo de un agente sinkia: editar `*_MODEL` en `server/.env` y `pm2 restart sinkia-api`.

---

## 11. Pendientes y notas

- **Cerebro (entorno gráfico)**: `local-claude-code` ya está listo (Devstral vía gateway) para construirlo. Lanzamiento sugerido:
  `node /Users/davidnows/local-claude-code/dist/cli.js "Construye una app web de centro de control que muestre en tiempo real providers, modelos, qué modelo/skills usa cada agente, salud de servicios y un playground; backend Node que lee openclaw.json, pm2 jlist, docker ps y el gateway :4000"`. Pendiente de ejecutar (build largo con modelo local).
- **Ruta `ai.js` (`/api/ai/classify`)** de sinkia aún llama a Ollama con un modelo inexistente (404): conviene apuntarla también al gateway (no usa el patrón `*_PROVIDER`).
- **Seguridad**: el gateway no tiene master key (solo loopback); añadir auth para hardening/SaaS. La API key de Anthropic está en texto plano en `~/.claude/settings.json`.
- **Git sin commitear**: cambios en `sinkia-next/docker-compose.yml` (healthcheck qdrant + commerce eliminado) y en `local-claude-code/src` (cliente OpenAI‑compat).
- **Token del gateway de OpenClaw**: estable en sesión vía launchctl; el `env file` se regenera en cada `gateway restart` (alineado a mano). Fijarlo en el vault para robustez total.

---

## 12. Validaciones realizadas

- Gateway: `/health/liveliness` OK; lista los 11 alias; chat local (`local-fast` → "Hola") y nube (`cloud-auto` → "hello"); Devstral (`local-coder`) responde.
- Autorreparación: kill del proceso → PM2 lo revive.
- LM Studio/Ollama: cargan modelos desde el disco externo.
- OpenClaw: `health ok`, sin warnings, agentes con alias válidos.
- sinkia: `sinkia-api` reiniciado; `/api/classify` (reglas) responde; agentes LLM cableados por env al gateway.
