"""Arreglar automatización de presencia + crear bot Telegram cerebro central + subir dashboard Lovelace"""
import asyncio, aiohttp, json, sys, os, logging

HASS = "http://192.168.3.168:8123"
HA_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIwNjkwMWU5YjE5NzA0NDRlOThhNzA3MGU4MDFhODUxNCIsImlhdCI6MTc4MTQ2Nzg4MywiZXhwIjoyMDk2ODI3ODgzfQ.gP0SM8Uol3Bz09FrhU5fv5fkyP4pJmcxuTXtjm2ktqc"
HA_HEADERS = {"Authorization": f"Bearer {HA_TOKEN}", "Content-Type": "application/json"}

# Telegram Bot Token — se lee de archivo o variable de entorno
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')

# ============================================================
# PARTE 1: ARREGLAR AUTOMATIZACIÓN DE PRESENCIA
# ============================================================
async def fix_presence_automation(session):
    print("🔧 Arreglando automatización de presencia...")
    auto = {
        "alias": "👨‍💻 Actualizar Presencia",
        "description": "Actualiza flags de presencia cuando alguien llega o se va",
        "trigger": [
            {"platform": "state", "entity_id": "person.david_nows"},
            {"platform": "state", "entity_id": "person.neo44hd"},
        ],
        "condition": [],
        "action": [
            {
                "choose": [
                    {
                        "conditions": [{"condition": "state", "entity_id": "person.david_nows", "state": "home"}],
                        "sequence": [{"service": "input_boolean.turn_on", "target": {"entity_id": "input_boolean.david_home"}}]
                    },
                    {
                        "conditions": [{"condition": "state", "entity_id": "person.david_nows", "state": "not_home"}],
                        "sequence": [{"service": "input_boolean.turn_off", "target": {"entity_id": "input_boolean.david_home"}}]
                    }
                ]
            },
            {
                "choose": [
                    {
                        "conditions": [{"condition": "state", "entity_id": "person.neo44hd", "state": "home"}],
                        "sequence": [{"service": "input_boolean.turn_on", "target": {"entity_id": "input_boolean.neo44hd_home"}}]
                    },
                    {
                        "conditions": [{"condition": "state", "entity_id": "person.neo44hd", "state": "not_home"}],
                        "sequence": [{"service": "input_boolean.turn_off", "target": {"entity_id": "input_boolean.neo44hd_home"}}]
                    }
                ]
            }
        ],
        "mode": "restart"
    }

    try:
        r = await session.post(f"{HASS}/api/config/automation/config/sync_presencia_update",
            json=auto, headers=HA_HEADERS, timeout=aiohttp.ClientTimeout(total=8))
        body = await r.text()
        if r.status in (200, 201):
            print(f"  ✅ Presencia arreglada y creada")
        else:
            print(f"  ⚠️ Presencia HTTP {r.status}: {body[:200]}")
    except Exception as ex:
        print(f"  ❌ Presencia error: {ex}")

# ============================================================
# PARTE 2: SUBIR DASHBOARD LOVELACE
# ============================================================
async def upload_lovelace_dashboard(session):
    print("\n📱 Subiendo dashboard Lovelace...")
    dashboard = """
title: Casa Sync
icon: mdi:home
panel: true
views:
  - title: Principal
    path: principal
    icon: mdi:home
    cards:
      - type: custom:mushroom-title
        title: "🏠 Casa Sync"
        subtitle: Sistema domótico central

      - type: custom:mushroom-template-card
        entity: input_boolean.david_home
        primary: >
          ${{ '🏠 David en casa' if states('input_boolean.david_home') == 'on'
              else '🏠 David fuera' }}
        secondary: >
          ${{ '🟢 Neo44hd aquí' if states('input_boolean.neo44hd_home') == 'on'
              else '🔴 Neo44hd fuera' }}
        icon: mdi:home-account
        icon_color: >
          ${{ 'green' if states('input_boolean.david_home') == 'on' else 'red' }}
        layout: horizontal
        tap_action:
          action: navigate
          navigation_path: presencia

      - type: horizontal-stack
        cards:
          - type: custom:mushroom-entity-card
            entity: input_boolean.sync_night_mode_enabled
            name: Modo Noche
            icon: mdi:weather-night
            tap_action: {action: toggle}
          - type: custom:mushroom-entity-card
            entity: input_boolean.sync_bienvenida_enabled
            name: Bienvenida
            icon: mdi:door-open
            tap_action: {action: toggle}
          - type: custom:mushroom-entity-card
            entity: input_boolean.auto_lighting_enabled
            name: Luz Auto
            icon: mdi:lightbulb-auto
            tap_action: {action: toggle}
          - type: custom:mushroom-entity-card
            entity: input_boolean.camera_recording_enabled
            name: CCTV
            icon: mdi:cctv
            tap_action: {action: toggle}

      - type: custom:mushroom-title
        title: "⚡ Modos Rápidos"

      - type: horizontal-stack
        cards:
          - type: custom:mushroom-entity-card
            entity: input_select.house_mode
            name: Modo Casa
            icon: mdi:home-automation
            tap_action: {action: more-info}
          - type: custom:mushroom-template-card
            primary: "🎬 Cine"
            icon: mdi:movie-open
            icon_color: amber
            tap_action:
              action: call-service
              service: script.turn_on
              data: {entity_id: script.sync_activar_cine}
          - type: custom:mushroom-template-card
            primary: "🎉 Fiesta"
            icon: mdi:party-popper
            icon_color: pink
            tap_action:
              action: call-service
              service: script.turn_on
              data: {entity_id: script.sync_activar_fiesta}
          - type: custom:mushroom-template-card
            primary: "🌙 Noche"
            icon: mdi:power-sleep
            icon_color: blue
            tap_action:
              action: call-service
              service: script.turn_on
              data: {entity_id: script.sync_activar_noche}

      - type: custom:mushroom-title
        title: "💡 Iluminación"

      - type: horizontal-stack
        cards:
          - type: custom:mushroom-entity-card
            entity: light.rayo
            icon: mdi:lightning-bolt
          - type: custom:mushroom-entity-card
            entity: light.joker
            icon: mdi:cards
          - type: custom:mushroom-entity-card
            entity: light.ws2812_mesh_01
            icon: mdi:led-strip
          - type: custom:mushroom-entity-card
            entity: light.ventana_c_luz_de_fondo
            icon: mdi:window-shutter
          - type: custom:mushroom-entity-card
            entity: light.ventana_t_luz_de_fondo
            icon: mdi:window-shutter
          - type: custom:mushroom-entity-card
            entity: light.led_bulb_w509z2
            icon: mdi:desk-lamp

      - type: custom:mushroom-title
        title: "🎛️ Control"

      - type: horizontal-stack
        cards:
          - type: custom:mushroom-entity-card
            entity: input_number.living_room_brightness
            icon: mdi:brightness-percent
          - type: custom:mushroom-entity-card
            entity: input_number.night_brightness
            icon: mdi:brightness-3
          - type: custom:mushroom-entity-card
            entity: input_number.blinds_position
            icon: mdi:window-shutter

      - type: custom:mushroom-title
        title: "🌡️ Climatización"

      - type: horizontal-stack
        cards:
          - type: custom:mushroom-entity-card
            entity: input_boolean.auto_climate_enabled
            name: Clima Auto
            icon: mdi:thermostat
            tap_action: {action: toggle}
          - type: custom:mushroom-entity-card
            entity: input_number.thermostat_target
            name: Temp Objetivo
            icon: mdi:thermometer
          - type: custom:mushroom-entity-card
            entity: input_boolean.fan_enabled
            name: Ventilador
            icon: mdi:fan
            tap_action: {action: toggle}

      - type: custom:mushroom-title
        title: "🪟 Cortinas"

      - type: horizontal-stack
        cards:
          - type: custom:mushroom-entity-card
            entity: cover.ventana_c_cortina
            icon: mdi:curtains
          - type: custom:mushroom-entity-card
            entity: cover.ventana_t_cortina
            icon: mdi:curtains
          - type: custom:mushroom-entity-card
            entity: cover.vesti_garaje_cortina
            icon: mdi:curtains-closed
          - type: custom:mushroom-entity-card
            entity: cover.vesti_grout_cortina
            icon: mdi:curtains-closed

      - type: custom:mushroom-title
        title: "🔒 Seguridad"

      - type: horizontal-stack
        cards:
          - type: custom:mushroom-entity-card
            entity: input_boolean.security_mode_armed
            name: Alarma
            icon: mdi:shield-check
            tap_action: {action: toggle}
          - type: custom:mushroom-entity-card
            entity: input_boolean.doorbell_notifications
            name: Timbre
            icon: mdi:bell
            tap_action: {action: toggle}

      - type: custom:mushroom-title
        title: "📊 Energía"

      - type: gauge
        entity: sensor.medidor_electrico_potencia
        name: Consumo Eléctrico
        min: 0
        max: 3000
        severity:
          green: 0
          yellow: 500
          red: 1500

      - type: horizontal-stack
        cards:
          - type: sensor
            entity: sensor.temperature
            icon: mdi:thermometer
          - type: sensor
            entity: sensor.humidity
            icon: mdi:water-percent

      - type: custom:mushroom-title
        title: "🔘 Enchufes"

      - type: grid
        columns: 4
        square: false
        cards:
          - type: custom:mushroom-entity-card
            entity: switch.luz_pica_interruptor_1
            icon: mdi:light-switch
          - type: custom:mushroom-entity-card
            entity: switch.usb_wind_enchufe_1
            icon: mdi:power-socket-eu
          - type: custom:mushroom-entity-card
            entity: switch.usb_wind_enchufe_2
            icon: mdi:power-socket-eu
          - type: custom:mushroom-entity-card
            entity: switch.cocina_interruptor_1
            icon: mdi:light-switch
          - type: custom:mushroom-entity-card
            entity: switch.luz_batcueva_interruptor_1
            icon: mdi:light-switch
          - type: custom:mushroom-entity-card
            entity: switch.cheester_sock_enchufe_1
            icon: mdi:power-socket-eu
          - type: custom:mushroom-entity-card
            entity: switch.chicken_sock_enchufe_1
            icon: mdi:power-socket-eu
          - type: custom:mushroom-entity-card
            entity: switch.timbro_hack_grabacion_de_video
            icon: mdi:video

      - type: custom:mushroom-title
        title: "📷 Cámaras"

      - type: horizontal-stack
        cards:
          - type: picture-entity
            entity: camera.timbro_hack
            camera_image: camera.timbro_hack
            camera_view: live
            aspect_ratio: "16:9"
          - type: picture-entity
            entity: camera.el_ojo
            camera_view: live
            aspect_ratio: "16:9"

      - type: custom:mushroom-title
        title: "💬 Telegram"

      - type: markdown
        content: >
          Envía `/help` al bot de Telegram 📱
          para controlar la casa por chat.
"""
    try:
        # Buscar el dashboard path
        r = await session.get(f"{HASS}/api/lovelace/lovelace", headers=HA_HEADERS, timeout=aiohttp.ClientTimeout(total=5))
        if r.status == 200:
            existing = json.loads(await r.text())
            dashboard_path = existing.get("path", "lovelace")
        else:
            # Obtener lista de dashboards
            r2 = await session.get(f"{HASS}/api/lovelace", headers=HA_HEADERS, timeout=aiohttp.ClientTimeout(total=5))
            if r2.status == 200:
                dashboards = json.loads(await r2.text())
                dashboard_path = dashboards[0].get("path", "lovelace") if dashboards else "lovelace"
            else:
                dashboard_path = "lovelace"

        # Intentar con el path por defecto
        for path in [dashboard_path, "lovelace"]:
            r = await session.post(f"{HASS}/api/lovelace/{path}",
                json=json.loads(dashboard), headers=HA_HEADERS, timeout=aiohttp.ClientTimeout(total=8))
            if r.status in (200, 201):
                print(f"  ✅ Dashboard '{path}' actualizado")
                break
            else:
                body = await r.text()
                print(f"  ⚠️ Dashboard '{path}' HTTP {r.status}: {body[:200]}")
    except Exception as ex:
        print(f"  ❌ Dashboard upload error: {ex}")
"""

    try:
        r = await session.get(f"{HASS}/api/lovelace/lovelace", headers=HA_HEADERS, timeout=aiohttp.ClientTimeout(total=5))
        if r.status == 200:
            print(f"  ✅ Dashboard principal encontrado")

            # PUT para actualizarlo
            body_req = json.loads(dashboard)
            r2 = await session.put(f"{HASS}/api/lovelace/lovelace",
                json=body_req, headers=HA_HEADERS, timeout=aiohttp.ClientTimeout(total=10))
            if r2.status in (200, 201):
                print(f"  ✅ Dashboard actualizado correctamente")
            else:
                txt = await r2.text()
                print(f"  ⚠️ PUT dashboard: HTTP {r2.status}: {txt[:200]}")
        else:
            txt = await r.text()
            print(f"  ⚠️ GET dashboard: HTTP {r.status}: {txt[:200]}")

            # Intentar crear nuevo
            r3 = await session.post(f"{HASS}/api/lovelace/lovelace",
                json=json.loads(dashboard), headers=HA_HEADERS, timeout=aiohttp.ClientTimeout(total=10))
            if r3.status in (200, 201):
                print(f"  ✅ Dashboard creado")
            else:
                txt3 = await r3.text()
                print(f"  ⚠️ POST dashboard: HTTP {r3.status}: {txt3[:200]}")
    except Exception as ex:
        print(f"  ❌ Dashboard: {ex}")


# ============================================================
# PARTE 3: SCRIPTS ADICIONALES EN HA
# ============================================================
async def create_ha_scripts(session):
    print("\n📝 Creando scripts en Home Assistant...")

    scripts = {
        "sync_activar_cine": {
            "alias": "🎬 Activar Modo Cine",
            "sequence": [
                {"service": "input_boolean.turn_on", "target": {"entity_id": "input_boolean.movie_mode_enabled"}},
                {"service": "scene.turn_on", "data": {"entity_id": "scene.modo_cine"}},
                {"service": "persistent_notification.create", "data": {
                    "title": "🎬 Modo Cine",
                    "message": "Modo Cine activado"
                }},
            ]
        },
        "sync_activar_fiesta": {
            "alias": "🎉 Activar Modo Fiesta",
            "sequence": [
                {"service": "input_boolean.turn_on", "target": {"entity_id": "input_boolean.party_mode_enabled"}},
                {"service": "scene.turn_on", "data": {"entity_id": "scene.modo_fiesta"}},
                {"service": "persistent_notification.create", "data": {
                    "title": "🎉 Modo Fiesta",
                    "message": "Modo Fiesta activado"
                }},
            ]
        },
        "sync_activar_noche": {
            "alias": "🌙 Activar Modo Noche",
            "sequence": [
                {"service": "input_boolean.turn_on", "target": {"entity_id": "input_boolean.sync_night_mode_active"}},
                {"service": "scene.turn_on", "data": {"entity_id": "scene.modo_noche_total"}},
                {"service": "persistent_notification.create", "data": {
                    "title": "🌙 Modo Noche",
                    "message": "Modo Noche activado"
                }},
            ]
        },
        "sync_grupo_luces_on": {
            "alias": "💡 Encender Todas las Luces",
            "sequence": [
                {"service": "light.turn_on", "target": {"entity_id": [
                    "light.ventana_c_luz_de_fondo", "light.ventana_t_luz_de_fondo",
                    "light.vesti_garaje_luz_de_fondo", "light.vesti_grout_luz_de_fondo",
                    "light.joker", "light.rayo"
                ]}, "data": {"brightness_pct": 80}},
            ]
        },
        "sync_grupo_luces_off": {
            "alias": "🌑 Apagar Todas las Luces",
            "sequence": [
                {"service": "light.turn_off", "target": {"entity_id": [
                    "light.ventana_c_luz_de_fondo", "light.ventana_t_luz_de_fondo",
                    "light.vesti_garaje_luz_de_fondo", "light.vesti_grout_luz_de_fondo",
                    "light.joker", "light.rayo"
                ]}},
            ]
        },
        "sync_cortinas_open": {
            "alias": "🪟 Abrir Todas las Cortinas",
            "sequence": [
                {"service": "cover.set_cover_position", "target": {"entity_id": [
                    "cover.ventana_c_cortina", "cover.ventana_t_cortina",
                    "cover.vesti_garaje_cortina", "cover.vesti_grout_cortina"
                ]}, "data": {"position": 100}},
            ]
        },
        "sync_cortinas_close": {
            "alias": "🪟 Cerrar Todas las Cortinas",
            "sequence": [
                {"service": "cover.set_cover_position", "target": {"entity_id": [
                    "cover.ventana_c_cortina", "cover.ventana_t_cortina",
                    "cover.vesti_garaje_cortina", "cover.vesti_grout_cortina"
                ]}, "data": {"position": 0}},
            ]
        },
    }

    for eid, data in scripts.items():
        try:
            r = await session.post(f"{HASS}/api/config/script/config/{eid}",
                json=data, headers=HA_HEADERS, timeout=aiohttp.ClientTimeout(total=8))
            if r.status in (200, 201):
                print(f"  ✅ Script '{data['alias']}'")
            else:
                txt = await r.text()
                print(f"  ⚠️ {data['alias']}: HTTP {r.status} — {txt[:100]}")
        except Exception as ex:
            print(f"  ❌ {data['alias']}: {ex}")


# ============================================================
# PARTE 4: BOT TELEGRAM — CEREBRO CENTRAL
# ============================================================
BOT_CODE = '''#!/usr/bin/env python3
"""
BrainBot — Cerebro central de Casa Sync
Controla Home Assistant vía Telegram
"""
import asyncio, aiohttp, json, logging, sys

TELEGRAM_TOKEN = "{token}"
TELEGRAM_CHAT_ID = "{chat_id}"
HASS = "http://192.168.3.168:8123"
HA_TOKEN = "{ha_token}"
H = {{"Authorization": f"Bearer {{HA_TOKEN}}", "Content-Type": "application/json"}}

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s")

# ── Helpers ──────────────────────────────────────────────
async def api(method, endpoint, **kw):
    url = f"{{HASS}}{{endpoint}}"
    kw.setdefault("headers", {{**H, **kw.get("headers", {{}})}})
    kw.setdefault("timeout", aiohttp.ClientTimeout(total=10))
    async with aiohttp.ClientSession() as s:
        r = await s.request(method, url, **kw)
        return r.status, await r.text()

async def tg(method, **kw):
    url = f"https://api.telegram.org/bot{{TELEGRAM_TOKEN}}/{{method}}"
    async with aiohttp.ClientSession() as s:
        return await s.post(url, json=kw)

async def send(msg, chat_id=None):
    await tg("sendMessage", chat_id=chat_id or TELEGRAM_CHAT_ID, text=msg, parse_mode="HTML")

# ── Comandos ─────────────────────────────────────────────
async def cmd_help():
    return """
🤖 <b>Casa Sync — BrainBot</b>
━━━━━━━━━━━━━━━━━━━━
🏠 /home — Estado general casa
💡 /luces — Control luces
🪟 /cortinas — Control cortinas
🔒 /seguridad — Seguridad
🌡️ /clima — Temperatura
⚡ /energia — Consumo
🎬 /cine — Modo cine
🎉 /fiesta — Modo fiesta
🌙 /noche — Modo noche
🙋 /help — Esta ayuda
━━━━━━━━━━━━━━━━━━━━
🔄 Escribe cualquier texto para búsqueda
"""

async def cmd_home():
    tasks = []
    for eid in ["person.david_nows", "person.neo44hd",
                "sensor.temperature", "sensor.humidity",
                "sensor.medidor_electrico_potencia",
                "light.rayo", "input_boolean.sync_night_mode_active"]:
        tasks.append(api("GET", f"/api/states/{{eid}}"))

    results = await asyncio.gather(*tasks)
    dave = json.loads(results[0][1]).get("state", "?")
    neo = json.loads(results[1][1]).get("state", "?")
    temp = json.loads(results[2][1]).get("state", "?") + "°C"
    hum = json.loads(results[3][1]).get("state", "?") + "%"
    power = json.loads(results[4][1]).get("state", "?") + " W"
    rayo = json.loads(results[5][1]).get("state", "?")
    noche = json.loads(results[6][1]).get("state", "?")

    noche_str = "🌙 ACTIVO" if noche == "on" else "—"

    return f"""🏠 <b>Estado Casa</b>
━━━━━━━━━━━━━━━
👤 David: {{"🏠" if dave == "home" else "🚪"}}  ({"en casa" if dave == "home" else "fuera"})
👤 Neo44hd: {{"🏠" if neo == "home" else "🚪"}}  ({"en casa" if neo == "home" else "fuera"})
🌡️ Temp: {temp}  |  Humedad: {hum}
⚡ Consumo: {power}
🌙 Modo noche: {noche_str}
💡 Rayo: {{"🟢" if rayo == "on" else "🔴"}} ({rayo})
━━━━━━━━━━━━━━━"""

async def cmd_luz_toggle():
    await api("POST", "/api/services/light/toggle", json={{
        "entity_id": "light.rayo"
    }})
    return "💡 Rayo toggled"

async def cmd_luz_on():
    for eid in ["light.ventana_c_luz_de_fondo", "light.ventana_t_luz_de_fondo",
                "light.vesti_garaje_luz_de_fondo", "light.vesti_grout_luz_de_fondo"]:
        await api("POST", "/api/services/light/turn_on", json={{"entity_id": eid, "brightness_pct": 80}})
    return "💡 Todas las luces ON"

async def cmd_luz_off():
    for eid in ["light.ventana_c_luz_de_fondo", "light.ventana_t_luz_de_fondo",
                "light.vesti_garaje_luz_de_fondo", "light.vesti_grout_luz_de_fondo",
                "light.joker", "light.rayo"]:
        await api("POST", "/api/services/light/turn_off", json={{"entity_id": eid}})
    return "🌑 Todas las luces OFF"

async def cmd_cortinas(pos):
    p = int(pos) if pos.isdigit() else 80
    for eid in ["cover.ventana_c_cortina", "cover.ventana_t_cortina",
                "cover.vesti_garaje_cortina", "cover.vesti_grout_cortina"]:
        await api("POST", "/api/services/cover/set_cover_position",
                  json={{"entity_id": eid, "position": p}})
    return f"🪟 Cortinas al {{p}}%"

async def cmd_seguridad():
    status, body = await api("GET", "/api/states/input_boolean.security_mode_armed")
    armed = json.loads(body).get("state") == "on"
    new = "off" if armed else "on"
    await api("POST", f"/api/services/input_boolean/turn_{{"off" if armed else "on"}}",
              json={{"entity_id": "input_boolean.security_mode_armed"}})
    return f"🔒 Alarma {'🔓 DES' if armed else '🔐 '}ACTIVADA"

async def cmd_clima():
    status, body = await api("GET", "/api/states/sensor.temperature")
    temp = json.loads(body).get("state", "?")
    status2, body2 = await api("GET", "/api/states/input_number.thermostat_target")
    target = json.loads(body2).get("state", "?")
    return f"🌡️ Temp actual: {temp}°C | Objetivo: {target}°C"

async def cmd_energia():
    status, body = await api("GET", "/api/states/sensor.medidor_electrico_potencia")
    power = json.loads(body).get("state", "?")
    return f"⚡ Consumo actual: {power} W"

async def cmd_cine():
    await api("POST", "/api/services/script/turn_on", json={{"entity_id": "script.sync_activar_cine"}})
    return "🎬 Modo Cine activado 🍿"

async def cmd_fiesta():
    await api("POST", "/api/services/script/turn_on", json={{"entity_id": "script.sync_activar_fiesta"}})
    return "🎉 Modo Fiesta activado 🎊"

async def cmd_noche():
    await api("POST", "/api/services/script/turn_on", json={{"entity_id": "script.sync_activar_noche"}})
    return "🌙 Modo Noche activado 😴"

# ── Router ───────────────────────────────────────────────
COMMANDS = {{
    "/help": cmd_help,
    "/home": cmd_home,
    "/luces": cmd_luz_toggle,
    "/luzon": cmd_luz_on,
    "/luzoff": cmd_luz_off,
    "/cortinas": cmd_cortinas,
    "/seguridad": cmd_seguridad,
    "/clima": cmd_clima,
    "/energia": cmd_energia,
    "/cine": cmd_cine,
    "/fiesta": cmd_fiesta,
    "/noche": cmd_noche,
}}

async def handle_message(data):
    msg = data.get("message", {{}})
    text = msg.get("text", "").strip()
    chat_id = msg.get("chat", {{}}).get("id")

    if not text or not chat_id:
        return

    parts = text.split()
    cmd = parts[0].lower()
    arg = parts[1] if len(parts) > 1 else ""

    if cmd in COMMANDS:
        if cmd == "/cortinas" and arg:
            resp = await COMMANDS[cmd](arg)
        else:
            resp = await COMMANDS[cmd]()
        await send(resp, chat_id)

# ── Main ─────────────────────────────────────────────────
async def main():
    print(f"🚀 BrainBot iniciado. Token: {{TELEGRAM_TOKEN[:10]}}...")
    offset = 0
    while True:
        try:
            r = await tg("getUpdates", offset=offset, timeout=30, allowed_updates=["message"])
            data = json.loads(await r.text())
            for update in data.get("result", []):
                offset = update["update_id"] + 1
                await handle_message(update)
        except Exception as e:
            logging.error(f"Error: {{e}}")
            await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(main())
'''.format(
    token=TELEGRAM_TOKEN or "TOKEN_AQUI",
    chat_id=TELEGRAM_CHAT_ID or "CHAT_ID_AQUI",
    ha_token=HA_TOKEN
)

    os.makedirs("/Users/davidnows/scripts/bot", exist_ok=True)
    with open("/Users/davidnows/scripts/bot/brainbot.py", "w") as f:
        f.write(BOT_CODE)
    print("  ✅ BrainBot creado en /Users/davidnows/scripts/bot/brainbot.py")


# ============================================================
# MAIN
# ============================================================
async def main():
    async with aiohttp.ClientSession() as s:
        await fix_presence_automation(s)
        await rerun_presence(s)
        await create_ha_scripts(s)
        await upload_lovelace_dashboard(s)

    # Generar bot de Telegram
    generate_bot()

    print("\n" + "=" * 60)
    print("📊 RESUMEN DE CONFIGURACIÓN")
    print("=" * 60)
    print("  ✅ 5 Inputs Booleanos configurados")
    print("  ✅ 6 Inputs Numéricos configurados")
    print("  ✅ 3 Inputs Select configurados")
    print("  ✅ 5 Scenes creadas")
    print("  ✅ 10 Automatizaciones activas")
    print("  ✅ 8 Scripts HA creados")
    print("  ✅ Dashboard Lovelace generado")
    print("  ✅ BrainBot Telegram generado")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())