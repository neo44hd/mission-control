# Proyecto: SynK-IA Memory — Base de Datos de Memoria Retroactiva

## Contexto
Tengo un ecosistema llamado SynK-IA que incluye servicios gestionados con PM2, contenedores Docker, OpenClaw como API local de IA, y uso Claude Code como asistente de desarrollo. Genero constantemente chats, logs, informes, archivos de configuración y procesos que quiero poder buscar y consultar como una "memoria" del sistema.

## Objetivo
Construir una base de datos inteligente con búsqueda semántica y textual que actúe como memoria retroactiva del sistema. Debe indexar automáticamente todas las fuentes de datos y permitir buscar cualquier cosa: un chat antiguo, un log de error, un informe, un proceso que se ejecutó, etc.

## Requisitos Funcionales

### 1. Fuentes de datos a indexar

#### A. Logs y servicios del sistema
- **Logs de PM2**: `~/.pm2/logs/` — todos los archivos `.log`
- **Logs de Docker**: salida de `docker logs` de cada contenedor activo
- **Logs del sistema macOS**: `/var/log/` — `system.log`, `install.log`, etc.
- **Logs de Homebrew**: `$(brew --prefix)/var/log/` — logs de servicios instalados con brew
- **Historial de shell**: `~/.zsh_history`
- **Crontab del usuario**: salida de `crontab -l`

#### B. Conversaciones e historial de IA
- **Conversaciones de Claude Code**: `~/.claude/` — historial, proyectos, CLAUDE.md, configs
- **Conversaciones de Warp/Oz**: `~/.warp/` — historial de chats con Oz, sesiones de agente
- **Logs de Warp**: `~/Library/Logs/Warp/` o `~/Library/Application Support/dev.warp.Warp-Stable/` — logs internos de la app
- **Historial de OpenClaw**: logs y conversaciones del servicio OpenClaw local

#### C. Aplicaciones instaladas en el Mac mini
- **Lista de apps**: indexar salida de `ls /Applications/` + `brew list` + `brew list --cask` + `system_profiler SPApplicationsDataType`
- **Configs de apps**: `~/Library/Preferences/` — plists de configuración de apps
- **Application Support**: `~/Library/Application Support/` — datos de apps relevantes (Warp, Docker, VS Code, etc.)
- **LaunchAgents/Daemons**: `~/Library/LaunchAgents/` y `/Library/LaunchDaemons/` — servicios registrados

#### D. Proyecto SynK-IA y código
- **Archivos del proyecto SynK-IA**: `~/sinkia/` — código, configs, docs, READMEs
- **Otros proyectos**: `~/hermetic-mobile/`, `~/local-claude-code/` y cualquier repo en `~/`
- **Archivos de configuración**: `.env`, `docker-compose.yml`, `ecosystem.config.js`, `package.json`, etc.

#### E. Informes, documentos y archivos
- **Documentos**: cualquier `.md`, `.txt`, `.pdf`, `.docx`, `.xlsx` en `~/`, `~/Documents/`, `~/Desktop/`, `~/Downloads/`
- **Informes generados**: reportes, exports, summaries creados por cualquier herramienta
- **Notas y READMEs**: todos los `README.md`, `CHANGELOG.md`, `TODO.md` encontrados en proyectos
- **Skills de Claude**: `~/.claude/skills/` — definiciones de skills y sus configs

#### F. Red y servicios
- **Estado de red**: interfaces, túneles Cloudflare, puertos en escucha
- **Servicios activos**: snapshot periódico de `pm2 list`, `docker ps`, `brew services list`, `launchctl list`
- **Túnel Cloudflare**: logs y estado del túnel

### 2. Motor de búsqueda
- **Búsqueda textual** (full-text search) para coincidencias exactas
- **Búsqueda semántica** usando embeddings locales (Ollama con modelo de embeddings como `nomic-embed-text` o `all-minilm`)
- **Búsqueda combinada**: textual + semántica con ranking fusionado para mejores resultados

### 3. Sistema de filtros avanzados
Cada documento indexado debe tener metadata rica para permitir filtros combinables:

- **Por fecha**: `--since`, `--until`, `--date` (exacta), `--today`, `--this-week`, `--this-month`
- **Por app/servicio**: `--app docker`, `--app pm2`, `--app warp`, `--app claude`, `--app nginx`, etc.
- **Por tipo de fuente**: `--type log`, `--type chat`, `--type doc`, `--type config`, `--type code`, `--type report`
- **Por palabra clave**: búsqueda libre, soporta AND/OR/NOT (ej: `"error AND nginx NOT timeout"`)
- **Por categoría**: `--cat system`, `--cat ai`, `--cat network`, `--cat project`, `--cat docs`
- **Por severidad** (para logs): `--level error`, `--level warn`, `--level info`, `--level debug`
- **Por ruta/archivo**: `--path "sinkia/"`, `--file "docker-compose.yml"`
- **Por tag**: tags automáticos y manuales, ej: `--tag deployment`, `--tag bugfix`
- **Ordenamiento**: `--sort date`, `--sort relevance`, `--sort source` (default: relevance)
- **Límite de resultados**: `--limit N` (default: 20)
- **Formato de salida**: `--format table`, `--format json`, `--format detail`, `--format brief`

Los filtros deben ser combinables entre sí. Ejemplo: `memory search "error" --app docker --since 2025-03-01 --level error --sort date`

### 3. Ingesta automática
- Script/daemon que monitoree las fuentes y las indexe periódicamente (cron o watcher)
- Parseo inteligente: extraer metadata (timestamps, servicio origen, nivel de log, etc.)
- Deduplicación para no indexar lo mismo dos veces

### 4. Interfaz de consulta
- **CLI**: comando tipo `memory search "error en docker"` que devuelva resultados relevantes
- **API REST** (opcional): endpoint `/search?q=...` para integrarlo con otros servicios
- **Formato de salida**: mostrar fuente, fecha, fragmento relevante con contexto

## Requisitos Técnicos

### Stack sugerido (ajustar según convenga)
- **Base de datos**: SQLite con FTS5 para full-text + ChromaDB o similar para embeddings
- **Lenguaje**: Python 3 (compatible con el ecosistema existente)
- **Embeddings**: Ollama local (`nomic-embed-text`) via API en `http://localhost:11434`
- **Estructura del proyecto**: dentro de `~/sinkia/memory/` o `~/sinkia-memory/`

### Estructura esperada
```
sinkia-memory/
├── README.md
├── requirements.txt
├── config.yaml            # fuentes, rutas, intervalos de indexación
├── src/
│   ├── __init__.py
│   ├── indexer.py          # lógica de ingesta y parseo
│   ├── embeddings.py       # generación de embeddings via Ollama
│   ├── database.py         # SQLite FTS5 + vector store
│   ├── search.py           # motor de búsqueda combinado
│   └── cli.py              # interfaz de línea de comandos
├── scripts/
│   ├── index_now.sh        # indexar todo manualmente
│   └── setup_cron.sh       # configurar indexación periódica
└── tests/
    └── test_search.py
```

## Instrucciones para Claude Code

1. **Primero investiga** mi sistema: revisa qué hay en `~/sinkia/`, `~/.pm2/logs/`, `~/.claude/`, y `~/.zsh_history` para entender las fuentes reales disponibles.
2. **Crea el proyecto** en `~/sinkia-memory/` con la estructura propuesta.
3. **Implementa primero** el indexer + database + CLI básico con búsqueda textual (SQLite FTS5).
4. **Después añade** la búsqueda semántica con embeddings via Ollama.
5. **Prueba** que funciona: indexa algunas fuentes y haz búsquedas de prueba.
6. **Configura** un cron job para indexación automática cada 30 minutos.

## Ejemplo de uso esperado
```bash
# === INDEXACIÓN ===
memory index --all                          # Indexar todo ahora
memory index --source pm2-logs              # Indexar solo logs de PM2
memory index --source warp-chats            # Indexar chats de Warp/Oz
memory index --status                       # Ver progreso de indexación

# === BÚSQUEDA POR PALABRA ===
memory search "connection refused"           # Buscar texto exacto en todo
memory search "nginx error 502"              # Múltiples palabras
memory search "error AND docker NOT test"    # Operadores booleanos

# === BÚSQUEDA SEMÁNTICA ===
memory search --semantic "problemas de rendimiento en el servidor"
memory search --semantic "cómo configuré el túnel de cloudflare"
memory search --semantic "última vez que se cayó docker"

# === FILTROS POR FECHA ===
memory search "error" --today                # Solo hoy
memory search "deploy" --this-week           # Esta semana
memory search "nginx" --since 2025-03-01     # Desde una fecha
memory search "backup" --since 2025-01-01 --until 2025-06-30  # Rango

# === FILTROS POR APP/SERVICIO ===
memory search "timeout" --app docker         # Solo en Docker
memory search "crash" --app warp             # Solo en Warp
memory search "model" --app ollama           # Solo en Ollama
memory search "build" --app pm2              # Solo en PM2

# === FILTROS POR TIPO ===
memory search "error" --type log              # Solo en logs
memory search "openai" --type chat            # Solo en conversaciones
memory search "version" --type config         # Solo en configs
memory search "deploy" --type report          # Solo en informes

# === FILTROS COMBINADOS ===
memory search "error" --app docker --since 2025-03-01 --level error --sort date
memory search --semantic "problemas de memoria" --app pm2 --this-month --format detail
memory search "ssl" --type log --app nginx --limit 5 --format json

# === OTROS COMANDOS ===
memory stats                                 # Estadísticas generales
memory stats --by-app                        # Stats por aplicación
memory stats --by-type                       # Stats por tipo de fuente
memory recent                                # Últimos 10 documentos indexados
memory apps                                  # Listar apps/servicios detectados
memory sources                               # Listar fuentes configuradas
memory tag add "deployment" <doc_id>         # Añadir tag manual
memory export --query "docker" --format csv  # Exportar resultados
```

## Notas
- El servidor Ollama está en localhost:11434 con variables `OLLAMA_NUM_PARALLEL=1` y `OLLAMA_MAX_LOADED_MODELS=1`
- Priorizar que funcione ligero, ya que el servidor tiene recursos limitados
- Todo debe funcionar offline/local, sin dependencias de APIs externas
