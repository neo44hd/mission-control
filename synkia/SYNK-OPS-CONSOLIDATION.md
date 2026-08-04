# SYNK-OPS Consolidation Plan

## Status: CRITICAL - Secrets Exposed

### Issues Found
1. `.env.production` en SYNK-OPS contiene secrets:
   - JWT_SECRET hardcodeado
   - DATABASE_URL con password
   - API Keys (OpenRouter, OpenAI) con patrones visibles
   - GMAIL/SLACK tokens

2. Duplicación de código:
   - `server/index.js` — duplicado en synk-ia
   - `server/routes/*` — duplicado en synk-ia
   - `src/components/*` — duplicado en synk-ia
   - Modelos y configuración — duplicada

### Action Plan

**FASE 1: Secure SYNK-OPS Repo (Immediate)**
```bash
# 1. Remove .env.production y .env.bak-* del git history
git filter-branch --force --index-filter 'git rm --cached --ignore-unmatch .env.production .env.bak*' -- --all

# 2. Add to .gitignore
echo ".env.production" >> .gitignore
echo ".env.bak*" >> .gitignore
git add .gitignore
git commit -m "Add .env files to .gitignore"

# 3. Força push con credenciales limitadas
git push origin --force-with-lease
```

**FASE 2: Archive SYNK-OPS as Mirror**
```bash
# Renombrar branch
git branch -m main ops-archive-v1

# Marcar como archived
# En GitHub Settings: Archive this repository

# Crear notice en README
echo "Este repo fue archivado. El código activo está en synk-ia/." >> README.md
```

**FASE 3: Consolidate en synk-ia**
- synk-ia es la fuente de verdad
- Mantener SYNK-OPS solo para reference histórico
- No clonar secrets: usar .env.refs con Proton Pass

### Files to Keep (No duplicar)
- Documentation (DEPLOYMENT_SUMMARY.md, etc) — revisar antes
- Custom scripts (deploy.sh, start-dev.sh) — rescatar buenas prácticas
- Tests — migrar a synk-ia/tests si valen

### Files to Skip (Ya en synk-ia)
- server/index.js
- server/routes/*
- server/services/*
- src/components/*
- .env files (usar .env.refs + Proton Pass)

## DANGER: DO NOT PUSH SECRETS

Never push:
- .env.production
- .env.bak files
- JWT_SECRET, API_KEY, passwords
- Database credentials

Use only .env.example y .env.refs con referencias pass://

