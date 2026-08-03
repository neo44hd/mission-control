# Informe de Auditoría — Mac mini de David
**Generado:** 4 de julio de 2026  
**Hostname:** Davids-Mac-mini-2.local  
**Usuario:** davidnows

---

## Hardware y Sistema Operativo

| Elemento | Valor |
|---|---|
| Modelo | Mac mini — Apple M4 Pro (Mac16,11) |
| CPU | 12 núcleos (8 rendimiento + 4 eficiencia) |
| RAM | 24 GB LPDDR5 (Micron) |
| SSD interno | 500 GB (APPLE SSD AP0512Z) — S.M.A.R.T: Verificado |
| Disco externo | 1 TB CT1000P2 SSD8 (ExFAT, USB) — "Disco local" |
| Sistema Operativo | macOS 26.6 (25G5043d) — Darwin 25.6.0 |
| Tiempo encendido | 6 días, 17h 46m |
| SIP | Habilitado ✅ |
| Memoria Virtual Segura | Habilitada ✅ |
| FileVault | **Deshabilitado** ⚠️ |
| Número de serie | DHCF1W6PMQ |

---

## Almacenamiento

| Volumen | Capacidad | Usado | Libre | % |
|---|---|---|---|---|
| Macintosh HD (interno) | 494 GB | 407 GB | 87 GB | 82% ⚠️ |
| Disco local (externo USB) | 1 TB | 441 GB | 491 GB | 48% |
| VM (swap) | 460 GB virt. | 11 GB | — | — |

**Nota:** El volumen del sistema APFS aparece con sello "Broken" (común tras actualizaciones, no crítico).

---

## Red

| Interfaz | IP | Estado |
|---|---|---|
| en0 (Ethernet) | 192.168.3.32 | Activo |
| en1 (Wi-Fi) | 192.168.3.88 | Activo |
| utun4 (Tailscale) | 100.78.4.14 | Activo |
| bridge100–105 | 192.168.139/194/147/107/155/97 | OrbStack (Docker) |

**DNS:** Tailscale (100.100.100.100) + Cloudflare/Quad9 (1.1.1.1, 9.9.9.9)  
**Red Tailscale:** `tail126c66.ts.net`  
**IP pública:** 137.101.167.41 (España)  
**DERP más cercano:** Madrid (24.3ms)

---

## Puertos TCP Abiertos

| Puerto | Proceso | Bind | Descripción |
|---|---|---|---|
| 1234 | LM Studio | 127.0.0.1 | API local LM Studio |
| 3030 | OrbStack | 0.0.0.0 ⚠️ | Open WebUI |
| 3283 | ARDAgent | 0.0.0.0 ⚠️ | Remote Desktop Apple |
| 4000 | LiteLLM (Python) | 127.0.0.1 | Gateway LLM |
| 5000 | ControlCenter | 0.0.0.0 ⚠️ | — |
| 5190 | sinkia-next/server.py | 0.0.0.0 ⚠️ | Frontend Python |
| 5432 | PostgreSQL@15 | 127.0.0.1 | Base de datos |
| 5678 | OrbStack (n8n) | 0.0.0.0 ⚠️ | n8n workflows |
| 6333/6334 | OrbStack (Qdrant) | 0.0.0.0 ⚠️ | Vector DB |
| 7000 | ControlCenter | 0.0.0.0 ⚠️ | — |
| 7999 | openclaw-synkia | 0.0.0.0 ⚠️ | OpenClaw |
| 8080 | node | 0.0.0.0 ⚠️ | — |
| 8888 | SearXNG (OrbStack) | 0.0.0.0 ⚠️ | Motor de búsqueda |
| 8889 | hub-access.js (PM2) | 0.0.0.0 ⚠️ | Hub de acceso |
| 11434 | Ollama + OrbStack | 127.0.0.1 + 0.0.0.0 ⚠️ | API Ollama |
| 18790 | OpenClaw gateway | 127.0.0.1 | — |
| 20241 | cloudflared | 127.0.0.1 | Túnel Cloudflare |
| 40249 | lmlink-connector | 0.0.0.0 ⚠️ | LM Studio link |
| 49152 | rapportd | 0.0.0.0 | — |

---

## Servicios y Daemons Clave

| Servicio | PID | Estado | Descripción |
|---|---|---|---|
| Ollama | 520 | Online | Servidor LLM local (homebrew) |
| OpenClaw gateway | 58765 | Online | Gateway Node.js puerto 18790 |
| LiteLLM (llm-gateway) | 2093 | Online | Proxy LLM puerto 4000 |
| PostgreSQL@15 | 41470 | Online | Base de datos |
| LM Studio | 43584 | Online | Puertos 1234 + 41343 |
| cloudflared | 528 | Online | Túnel Cloudflare 53h activo |
| PM2 (God Daemon) | 1075 | Online | Gestor de procesos |
| Tailscale | 566 | Online | VPN mesh |
| OrbStack | 92379 | Online | 11.2% RAM (2.8 GB) |
| sinkia-next/server.py | 6914 | Online | Frontend Python puerto 5190 |
| ARDAgent (Remote Desktop) | 682 | Online | Puerto 3283 en todas interfaces |
| Warp | 12446 | Online | — |
| Comet (Perplexity) | 78941 | Online | ~310 MB RAM |

**LaunchAgents personalizados:**
- `com.cloudflare.cloudflared.plist`
- `ai.openclaw.gateway.plist`
- `ai.openclaw.model-health.plist`
- `ai.openclaw.model-sync.plist`
- `ai.openclaw.llm-gateway-watchdog.plist`
- `homebrew.mxcl.ollama.plist`
- `homebrew.mxcl.postgresql@15.plist`
- `pm2.davidnows.plist`

---

## Variables de Entorno

⚠️ **Las siguientes claves están expuestas en texto plano en el entorno del proceso:**

| Variable | Valor (parcial) |
|---|---|
| OPENAI_API_KEY | sk-or-v1-a24bfc0e... (OpenRouter) |
| OPENROUTER_API_KEY | sk-or-v1-a24bfc0e... |
| GATEWAY_AUTH_TOKEN | aca30e113a9d... |
| ANTHROPIC_AUTH_TOKEN | "ollama" (override) |
| ANTHROPIC_API_KEY | (vacío) |
| OLLAMA_HOST | 0.0.0.0:11434 ⚠️ |
| OLLAMA_ORIGINS | * ⚠️ |
| HERMES_YOLO_MODE | 1 |
| IS_SANDBOX | 1 |

---

## Docker / OrbStack

**Docker versión:** 29.4.0 (contexto: orbstack)  
**Servidor:** OrbStack Linux (kernel 7.0.11-orbstack, aarch64)  
**Contenedores:** 17 total — **16 en ejecución**, 1 parado

| Nombre | Imagen | Puerto | Estado |
|---|---|---|---|
| sinkia-n8n | n8nio/n8n:latest | 5678→5678 | Up 4 días |
| sinkia-api | sinkia-next-sinkia | 3001→3001 | Up 4 días (healthy) |
| sinkia-openwebui | open-webui:main | 3030→8080 | Up 4 días (healthy) |
| sinkia-searxng | searxng:latest | 8888→8080 | Up 4 días (healthy) |
| sinkia-qdrant | qdrant:latest | 6333-6334 | Up 4 días (healthy) |
| sinkia-ollama | ollama:latest | 11434→11434 | Up 4 días (healthy) |
| openclaw-synkia | davidnows-openclaw-synkia | 7999→7999 | Up 4 días (healthy) |
| sinkia-ollama-gateway | busybox:1.35 | — | Up 4 días |
| k8s_coredns (x2) | rancher/coredns | — | Up / Exited |
| k8s_local-path-prov. (x2) | rancher/local-path | — | Up / Exited |

**Redes:** `sinkia-net`, `sinkia-next_sinkia-net`, `davidnows_synkia-network`  
**Volúmenes notables:** `docker_pgdata`, `docker_redisdata`, `open-webui`, `qdrant_data`, `sinkia-next_n8n_data`

**Imágenes más pesadas:**
- open-webui: 4.25 GB
- ollama/ollama: 5.69 GB
- n8nio/n8n: 1.2 GB
- sinkia-next-sinkia: 1.52 GB

---

## Ollama

**Versión:** 0.30.10 (cliente 0.30.8 — desactualizado)  
**Estado:** Activo, escuchando en `127.0.0.1:11434`  
**GPU detectada:** Apple M4 Pro Metal (MTL0) — 17.8 GiB VRAM disponible  
**Ningún modelo cargado actualmente**

**Modelos instalados localmente:**

| Modelo | Tamaño | Última modificación |
|---|---|---|
| nomic-embed-text:latest | 274 MB | hace 2 días |
| qwen2.5-coder:7b | 4.7 GB | hace 12 días |
| llama3.2:3b | 2.0 GB | hace 12 días |

**Error recurrente en logs:** El modelo `hf.co/EnlistedGhost/Pixtral-12B-Ollama-GGUF:Q3_K_M` tiene blobs corruptos/eliminados. Se recomienda limpiar la referencia.

**LM Studio también activo** con modelo:
- `Negentropy-claude-opus-4.7-9B-Q4_K_S.gguf` — **20.7% RAM (5.2 GB)** — 2 instancias de llama-server

---

## Tailscale

**Versión:** 1.100.0  
**IP local:** `100.78.4.14` (sinkpro)  
**Cuenta:** neo44hd@

**Dispositivos en la red:**

| Hostname | IP | OS | Estado |
|---|---|---|---|
| sinkpro (este equipo) | 100.78.4.14 | macOS | — |
| imac-de-chicken | 100.116.49.37 | macOS | **Activo** (iMac conectado) |
| sinkia | 100.91.86.75 | Linux | — |
| sinkialabs | 100.103.194.10 | Linux | — |
| iphone-15-pro-max | 100.108.23.34 | iOS | — |
| ipadscren | 100.79.186.69 | iOS | offline 22m |
| iphone-11-pro-max | 100.68.160.50 | iOS | offline 44m |
| 7seve-n | 100.103.20.92 | Android | offline 19d |
| mmacbook-pro-dave0ne | 100.91.96.114 | macOS | offline 10d |
| imac-de-grout | 100.108.17.119 | macOS | offline 121d |

---

## Cloudflare / Túneles

**cloudflared versión:** 2026.5.0 *(actualización disponible: 2026.6.1)* ⚠️  
**Túnel activo:** `sinkia` (ID: `4298eb1a-c6f0-42d7-aa57-f7987ff43787`)  
**Creado:** 8 de abril de 2026  
**Conectores:** 2xmad05, 2xmad06 (Madrid)  
**IP de origen:** 137.101.167.41  
**Tiempo activo del proceso:** 53h 08m

**Archivos de configuración en `~/.cloudflared/`:**
- `config.yml` (activo)
- `cert.pem` + `cert.key` (credenciales del túnel)
- `4298eb1a-...json` (secreto del túnel)

---

## PM2

**Versión:** 6.0.14 | **Node.js:** 26.3.0

**Procesos activos:**

| ID | Nombre | PID | Uptime | Reinicios | RAM | Script |
|---|---|---|---|---|---|---|
| 0 | dump | 1398 | 22h | 0 | 49 MB | `.pm2/dump.pm2` |
| 1 | hub-access | 1587 | 22h | 0 | 50 MB | `~/hub-access.js` |
| 2 | frontend-prod | 6914 | 22h | 3 ⚠️ | 10 MB | `~/sinkia-next/server.py` |
| 3 | llm-gateway | 2093 | 22h | 0 | 66 MB | `~/.openclaw/litellm/run-gateway.sh` |

**Logs de llm-gateway:** Errores recurrentes de compatibilidad entre **Python 3.9** y LiteLLM (sintaxis `dict | None` no soportada en Python <3.10). Afecta a los módulos guardrail `javelin` y `aim`.

---

## Alertas y Recomendaciones

### 🔴 Crítico
- **FileVault desactivado** — el disco no está cifrado en reposo. Con tantos servicios y datos sensibles, se recomienda activarlo urgentemente.
- **Claves API en texto plano** en variables de entorno (`OPENAI_API_KEY`, `OPENROUTER_API_KEY`, `GATEWAY_AUTH_TOKEN`) — visibles a cualquier proceso hijo. Mover a un gestor de secretos o ficheros `.env` con permisos restringidos.
- **`OLLAMA_HOST=0.0.0.0`** — Ollama escucha en todas las interfaces de red. Si no es necesario acceso externo, cambiar a `127.0.0.1`.

### 🟠 Importante
- **Puertos expuestos en `0.0.0.0`** — los puertos 3030, 5190, 5678, 6333, 6334, 7999, 8080, 8888, 8889, 40249 son accesibles desde la LAN local y desde la red Tailscale. Revisar cuáles deben limitarse a `localhost`.
- **ARDAgent (Remote Desktop)** activo en puerto 3283 en todas las interfaces — verificar que está protegido o desactivar si no se usa.
- **`frontend-prod`** ha reiniciado 3 veces — revisar logs en `~/.pm2/logs/frontend-prod-error.log`.
- **cloudflared desactualizado** (2026.5.0 → 2026.6.1 disponible).

### 🟡 Menor
- **LM Studio tiene 2 instancias de llama-server** ejecutando el mismo modelo GGUF — consumiendo 5.2 GB de RAM c/u (10.4 GB total). Verificar si ambas son necesarias.
- **`appstoreagent`** al 49.7% CPU desde el domingo — posible proceso colgado, considerar reiniciarlo.
- **Python 3.9** usado para LiteLLM causa errores de compatibilidad de tipos — actualizar a Python 3.10+ o usar `python@3.12` (ya instalado).
- **Ollama tiene blob huérfano** del modelo Pixtral — limpiar con `ollama rm hf.co/EnlistedGhost/Pixtral-12B-Ollama-GGUF:Q3_K_M`.
- **Volumen APFS del sistema con sello "Broken"** — no crítico pero monitorizar.
- **Disco interno al 82%** (407/494 GB) — revisar y limpiar si es necesario.

---

## Resumen del Ecosistema SynK-IA

El Mac mini actúa como servidor central del ecosistema SynK-IA con los siguientes componentes activos:

- **Stack Docker:** sinkia-api, sinkia-openwebui, sinkia-n8n, sinkia-qdrant, sinkia-searxng, sinkia-ollama, openclaw-synkia
- **Gateway de IA:** LiteLLM (puerto 4000) + OpenClaw (puerto 18790) + Ollama (puerto 11434)
- **Frontend:** sinkia-next (Python/server.py, puerto 5190)
- **Acceso externo:** Cloudflare Tunnel "sinkia" → servicios internos
- **VPN mesh:** Tailscale conectando múltiples dispositivos

---

*Generado automáticamente a partir de `~/audit-report.txt`*
