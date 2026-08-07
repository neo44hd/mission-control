#!/usr/bin/env python3
"""
ha_deploy.py — Generador de deploy autocontenido para Terminal Addon de HA.
===============================================================
EJECUTAR EN TU MAC (no en la Terminal Addon).
Genera deploy_terminal.sh con brainbot.py embebido en base64.

Uso:
    python3 ha_deploy.py

Output: deploy_terminal.sh
Luego copia el contenido de deploy_terminal.sh en la Terminal Addon de HA.
"""

import base64
import textwrap
import os

BRAINBOT_SRC = "/Users/davidnows/scripts/bot/brainbot.py"
DASHBOARD_SRC = "/Users/davidnows/scripts/ui-lovelace.yaml"
OUTPUT = "/Users/davidnows/scripts/deploy_terminal.sh"

# ─── LEER FUENTES ─────────────────────────────────────────

with open(BRAINBOT_SRC, "r", encoding="utf-8") as f:
    brainbot_code = f.read()

with open(DASHBOARD_SRC, "r", encoding="utf-8") as f:
    dashboard_yaml = f.read()

brainbot_b64 = base64.b64encode(brainbot_code.encode("utf-8")).decode("ascii")
dashboard_b64 = base64.b64encode(dashboard_yaml.encode("utf-8")).decode("ascii")

# ─── GENERAR deploy_terminal.sh ──────────────────────────

deploy_script = textwrap.dedent("""\
#!/bin/bash
# ═══════════════════════════════════════════════════════════
#  Chicken Palace BrainBot v4.0 — Deploy desde Terminal Addon
#  EJECUTAR ESTE SCRIPT ENTERO EN LA TERMINAL ADDON DE HAOS
# ═══════════════════════════════════════════════════════════
set -e

echo "============================================================"
echo "  CHICKEN PALACE BRAINBOT v4.0 DEPLOY"
echo "============================================================"

# ─── TOKENS (se leen del environment de HAOS) ──────────────
TG_TOKEN="${TG_BOT_TOKEN:?ERROR: export TG_BOT_TOKEN=... antes de ejecutar}"
HASS_TOKEN="${HASS_TOKEN:?ERROR: export HASS_TOKEN=... antes de ejecutar}"

echo "[✓] Tokens detectados (longitud TG=${#TG_TOKEN}, HA=${#HASS_TOKEN})"

# ─── DIRECTORIOS ──────────────────────────────────────────
mkdir -p /config/bot
echo "[1/7] Directorio /config/bot creado"

# ─── ESCRIBIR brainbot.py (base64 → decode) ───────────────
echo "{BRAINBOT_B64}" | base64 -d > /config/bot/brainbot.py
chmod 755 /config/bot/brainbot.py
echo "[2/7] brainbot.py escrito ($(wc -c < /config/bot/brainbot.py) bytes)"

# ─── ESCRIBIR ui-lovelace.yaml (base64 → decode) ──────────
echo "{DASHBOARD_B64}" | base64 -d > /config/ui-lovelace.yaml
echo "[3/7] ui-lovelace.yaml escrito ($(wc -c < /config/ui-lovelace.yaml) bytes)"

# ─── INSTALAR aiohttp ─────────────────────────────────────
echo "[4/7] Instalando aiohttp..."
pip3 install aiohttp --quiet 2>&1 | tail -1 || echo "  (ya instalado o error menor)"

# ─── INICIAR BOT ──────────────────────────────────────────
echo "[5/7] Matando instancias previas..."
pkill -f "brainbot.py" 2>/dev/null || true
sleep 1

echo "[6/7] Lanzando brainbot..."
cd /config/bot
nohup python3 brainbot.py > /config/bot/brainbot.log 2>&1 &
BOT_PID=$!
echo "  PID: $BOT_PID"
sleep 3

# ─── VERIFICAR ────────────────────────────────────────────
if ps -p $BOT_PID > /dev/null 2>&1; then
    echo ""
    echo "============================================================"
    echo "  ✅ DEPLOY COMPLETADO — BrainBot v4.0 corriendo"
    echo "============================================================"
    echo ""
    echo "  Bot PID:    $BOT_PID"
    echo "  Log:        tail -f /config/bot/brainbot.log"
    echo ""
    echo "  Prueba: escribe /start a @Diosa44_bot"
    echo ""
    echo "  Comandos domóticos:"
    echo "    /home        Estado general"
    echo "    /luces on    Luces ON"
    echo "    /cine        Modo cine"
    echo "    /fiesta      Modo fiesta"
    echo "    /noche       Modo noche"
    echo "    /seguridad   Alarmas"
    echo "    /clima       Temperatura"
    echo ""
    echo "  Conversación libre: escríbele cualquier cosa!"
    echo "============================================================"
else
    echo "❌ BrainBot no pudo iniciar. Revisa el log:"
    cat /config/bot/brainbot.log
    exit 1
fi
""")

# Sustituir marcadores con base64 real
deploy_script = deploy_script.replace("{BRAINBOT_B64}", brainbot_b64)
deploy_script = deploy_script.replace("{DASHBOARD_B64}", dashboard_b64)

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write(deploy_script)
os.chmod(OUTPUT, 0o755)

print(f"✅ Generado: {OUTPUT}")
print(f"   brainbot.py:  {len(brainbot_code):,} chars → {len(brainbot_b64):,} base64")
print(f"   ui-lovelace:  {len(dashboard_yaml):,} chars → {len(dashboard_b64):,} base64")
print(f"   deploy total: {os.path.getsize(OUTPUT):,} bytes")
print()
print("Pasos:")
print("  1. Abre la Terminal Addon de Home Assistant")
print("  2. Exporta los tokens:")
print('     export TG_BOT_TOKEN="8773207493:..."')
print('     export HASS_TOKEN="eyJhbGci..."')
print("  3. Copia TODO el contenido de deploy_terminal.sh y péga lo")
print("  4. Espera 5 segundos y prueba con /start a @Diosa44_bot")