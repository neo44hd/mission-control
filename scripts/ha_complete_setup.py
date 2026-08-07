"""Subir dashboard Lovelace (YAML directo) + crear bot Telegram + servicio systemd"""
import asyncio, aiohttp, json, os, platform

HASS = "http://192.168.3.168:8123"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIwNjkwMWU5YjE5NzA0NDRlOThhNzA3MGU4MDFhODUxNCIsImlhdCI6MTc4MTQ2Nzg4MywiZXhwIjoyMDk2ODI3ODgzfQ.gP0SM8Uol3Bz09FrhU5fv5fkyP4pJmcxuTXtjm2ktqc"
H = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

def find_ha_config_dir():
    """Buscar directorio de config de HA"""
    candidates = [
        "/root/.homeassistant",
        "/home/homeassistant/.homeassistant",
        "/home/david/.homeassistant",
        "/Users/davidnows/.homeassistant",
        "/srv/homeassistant",
        "/opt/homeassistant",
    ]
    for c in candidates:
        if os.path.isdir(c):
            return c
    # Buscar via red
    return None

async def query_ha_config():
    """Intentar obtener path de config via API"""
    s = aiohttp.ClientSession()
    try:
        r = await s.get(f"{HASS}/api/config", headers=H, timeout=aiohttp.ClientTimeout(total=8))
        if r.status == 200:
            data = json.loads(await r.text())
            return data
    except:
        pass
    try:
        r = await s.get(f"{HASS}/api/hassio/info/supervisor", headers=H, timeout=aiohttp.ClientTimeout(total=5))
        if r.status == 200:
            return json.loads(await r.text())
    except:
        pass
    return None

def write_dashboard_yaml(config_dir):
    """Escribir dashboard YAML directamente en config de HA"""
    yaml_content = """title: Casa Sync
icon: mdi:home
panel: true
views:
  - title: Inicio
    path: inicio
    icon: mdi:home
    cards:
      - type: custom:mushroom-title
        title: "Casa Sync"
        subtitle: "Sistema domotico centralizado"

      - type: custom:mushroom-template-card
        entity: input_boolean.david_home
        primary: "David: ${{ states('input_boolean.david_home') }}"
        secondary: "Neo44hd: ${{ states('input_boolean.neo44hd_home') }}"
        icon: mdi:home-account
        layout: horizontal

      - type: horizontal-stack
        cards:
          - type: custom:mushroom-entity-card
            entity: input_boolean.sync_night_mode_enabled
          - type: custom:mushroom-entity-card
            entity: input_boolean.sync_bienvenida_enabled
          - type: custom:mushroom-entity-card
            entity: input_boolean.camera_recording_enabled
          - type: custom:mushroom-entity-card
            entity: input_boolean.auto_lighting_enabled

      - type: custom:mushroom-title
        title: "Modos"

      - type: horizontal-stack
        cards:
          - type: custom:mushroom-template-card
            primary: "Cine"
            icon: mdi:movie-open
            icon_color: amber
            tap_action:
              action: call-service
              service: script.sync_activar_cine
          - type: custom:mushroom-template-card
            primary: "Fiesta"
            icon: mdi:party-popper
            icon_color: pink
            tap_action:
              action: call-service
              service: script.sync_activar_fiesta
          - type: custom:mushroom-template-card
            primary: "Noche"
            icon: mdi:power-sleep
            icon_color: blue
            tap_action:
              action: call-service
              service: script.sync_activar_noche
          - type: custom:mushroom-template-card
            primary: "Despertar"
            icon: mdi:white-balance-sunny
            icon_color: orange
            tap_action:
              action: call-service
              service: script.sync_desactivar_noche

      - type: custom:mushroom-title
        title: "Luces"

      - type: horizontal-stack
        cards:
          - type: custom:mushroom-entity-card
            entity: light.rayo
          - type: custom:mushroom-entity-card
            entity: light.joker
          - type: custom:mushroom-entity-card
            entity: light.ventana_c_luz_de_fondo
          - type: custom:mushroom-entity-card
            entity: light.ventana_t_luz_de_fondo
          - type: custom:mushroom-entity-card
            entity: light.led_bulb_w509z2

      - type: custom:mushroom-title
        title: "Control"

      - type: horizontal-stack
        cards:
          - type: custom:mushroom-entity-card
            entity: input_number.thermostat_target
          - type: custom:mushroom-entity-card
            entity: input_number.living_room_brightness
          - type: custom:mushroom-entity-card
            entity: input_number.blinds_position

      - type: custom:mushroom-title
        title: "Cortinas"

      - type: horizontal-stack
        cards:
          - type: custom:mushroom-entity-card
            entity: cover.ventana_c_cortina
          - type: custom:mushroom-entity-card
            entity: cover.ventana_t_cortina
          - type: custom:mushroom-entity-card
            entity: cover.vesti_garaje_cortina
          - type: custom:mushroom-entity-card
            entity: cover.vesti_grout_cortina

      - type: custom:mushroom-title
        title: "Seguridad"

      - type: horizontal-stack
        cards:
          - type: custom:mushroom-entity-card
            entity: input_boolean.security_mode_armed
          - type: custom:mushroom-entity-card
            entity: input_boolean.doorbell_notifications

      - type: custom:mushroom-title
        title: "Energia"

      - type: gauge
        entity: sensor.medidor_electrico_potencia
        name: Consumo Electrico
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
          - type: sensor
            entity: sensor.humidity

      - type: custom:mushroom-title
        title: "Enchufes"

      - type: grid
        columns: 4
        square: false
        cards:
          - type: custom:mushroom-entity-card
            entity: switch.luz_pica_interruptor_1
          - type: custom:mushroom-entity-card
            entity: switch.usb_wind_enchufe_1
          - type: custom:mushroom-entity-card
            entity: switch.usb_wind_enchufe_2
          - type: custom:mushroom-entity-card
            entity: switch.cocina_interruptor_1
          - type: custom:mushroom-entity-card
            entity: switch.luz_batcueva_interruptor_1
          - type: custom:mushroom-entity-card
            entity: switch.cheester_sock_enchufe_1
          - type: custom:mushroom-entity-card
            entity: switch.chicken_sock_enchufe_1
          - type: custom:mushroom-entity-card
            entity: switch.timbro_hack_grabacion_de_video

      - type: custom:mushroom-title
        title: "Camara"

      - type: horizontal-stack
        cards:
          - type: picture-entity
            entity: camera.timbro_hack
            camera_image: camera.timbro_hack
            camera_view: live
          - type: picture-entity
            entity: camera.el_ojo
            camera_view: live

  - title: Presencia
    path: presencia
    icon: mdi:account-group
    cards:
      - type: custom:mushroom-title
        title: "Presencia"
      - type: entity
        entity: person.david_nows
      - type: entity
        entity: person.neo44hd

  - title: Telegram
    path: telegram
    icon: mdi:telegram
    cards:
      - type: custom:mushroom-title
        title: "Control por Telegram"
      - type: markdown
        content: |
          **Escribe al bot de Telegram para controlar la casa.**

          /cine - Modo cine
          /fiesta - Modo fiesta
          /noche - Modo noche
          /despertar - Desactivar noche
          /luzon - Luces on
          /luzoff - Luces off
          /cortinas - Abrir cortinas
          /cortinasc - Cerrar cortinas
          /home - Estado casa
          /seguridad - Toggle alarma
          /clima - Temperatura
          /energia - Consumo
"""
    if config_dir:
        path = os.path.join(config_dir, "ui-lovelace.yaml")
        with open(path, "w") as f:
            f.write(yaml_content)
        print(f"   Dashboard YAML: {path}")
    else:
        with open("/Users/davidnows/scripts/ui-lovelace.yaml", "w") as f:
            f.write(yaml_content)
        print("   Dashboard guardado en ui-lovelace.yaml (copialo a tu config HA)")

    # Also save JSON version
    with open("/Users/davidnows/scripts/dashboard.json", "w") as f:
        json.dump(json.loads(json.dumps(DASHBOARD_JSON())), f, indent=2, ensure_ascii=False)

def DASHBOARD_JSON():
    return {
        "title": "Casa Sync", "icon": "mdi:home", "panel": True,
        "views": [
            {"title": "Inicio", "path": "inicio", "icon": "mdi:home",
             "cards": [
                 {"type": "custom:mushroom-title", "title": "Casa Sync"},
                 {"type": "entity", "entity": "input_boolean.sync_night_mode_enabled"},
                 {"type": "entity", "entity": "input_boolean.sync_bienvenida_enabled"},
             ]}
        ]
    }

async def create_telegram_bot_script():
    """Crear script del bot de Telegram"""
    bot_code = '''#!/usr/bin/env python3
import asyncio, aiohttp, json, os, logging

TELEGRAM_TOKEN = os.environ.get("TG_BOT_TOKEN", "PON_TU_TOKEN_AQUI")
TELEGRAM_CHAT = os.environ.get("TG_CHAT_ID", "PON_TU_CHAT_ID_AQUI")
HASS = "http://192.168.3.168:8123"
HASS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIwNjkwMWU5YjE5NzA0NDRlOThhNzA3MGU4MDFhODUxNCIsImlhdCI6MTc4MTQ2Nzg4MywiZXhwIjoyMDk2ODI3ODgzfQ.gP0SM8Uol3Bz09FrhU5fv5fkyP4pJmcxuTXtjm2ktqc"
HEADERS = {"Authorization": f"Bearer {HASS_TOKEN}", "Content-Type": "application/json"}

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger("BrainBot")

async def api_call(method, endpoint, **kw):
    async with aiohttp.ClientSession() as s:
        url = HASS + endpoint
        kw["headers"] = {**HEADERS, **kw.get("headers", {})}
        kw["timeout"] = aiohttp.ClientTimeout(total=10)
        r = await s.request(method, url, **kw)
        return r.status, await r.text()

async def tg(method, **kw):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/{method}"
    async with aiohttp.ClientSession() as s:
        r = await s.post(url, json=kw)
        return json.loads(await r.text())

async def send(text, chat_id=None):
    await tg("sendMessage", chat_id=chat_id or TELEGRAM_CHAT, text=text, parse_mode="HTML")

async def cmd_help():
    return ("<b>BrainBot - Casa Sync</b>\\n"
            "━━━━━━━━━━━━━━━━━━\\n"
            "/home - Estado casa\\n"
            "/luzon - Encender luces\\n"
            "/luzoff - Apagar luces\\n"
            "/cortinas - Abrir cortinas\\n"
            "/cortinasc - Cerrar cortinas\\n"
            "/cine - Modo cine\\n"
            "/fiesta - Modo fiesta\\n"
            "/noche - Modo noche\\n"
            "/despertar - Despertar\\n"
            "/seguridad - Toggle alarma\\n"
            "/clima - Temperatura\\n"
            "/energia - Consumo\\n"
            "/david - Posicion David\\n"
            "/neo - Posicion Neo44hd\\n"
            "/luces - Estado luces\\n"
            "/camaras - Camaras\\n")

async def cmd_home():
    ents = ["person.david_nows","person.neo44hd","sensor.temperature","sensor.humidity"]
    vals = {}
    for e in ents:
        st, bd = await api_call("GET", f"/api/states/{e}")
        if st == 200:
            vals[e] = json.loads(bd).get("state","?")
    d = "en casa" if vals.get("person.david_nows")=="home" else "fuera"
    n = "aqui" if vals.get("person.neo44hd")=="home" else "fuera"
    t = vals.get("sensor.temperature","?")
    h = vals.get("sensor.humidity","?")
    return (f"<b>Estado Casa Sync</b>\\n"
            f"━━━━━━━━━━━━━━━━━━\\n"
            f"David: {d}\\n"
            f"Neo44hd: {n}\\n"
            f"Temp: {t}C / Humedad: {h}%")

async def cmd_luz_on():
    for e in ["light.ventana_c_luz_de_fondo","light.ventana_t_luz_de_fondo",
              "light.vesti_garaje_luz_de_fondo","light.vesti_grout_luz_de_fondo","light.rayo","light.joker"]:
        await api_call("POST", "/api/services/light/turn_on", json={"entity_id": e, "brightness_pct": 80})
    return "Luces ENCENDIDAS"

async def cmd_luz_off():
    for e in ["light.ventana_c_luz_de_fondo","light.ventana_t_luz_de_fondo",
              "light.vesti_garaje_luz_de_fondo","light.vesti_grout_luz_de_fondo","light.rayo","light.joker"]:
        await api_call("POST", "/api/services/light/turn_off", json={"entity_id": e})
    return "Luces APAGADAS"

async def cmd_cortinas(pos):
    p = int(pos) if pos.isdigit() else 100
    for e in ["cover.ventana_c_cortina","cover.ventana_t_cortina","cover.vesti_garaje_cortina","cover.vesti_grout_cortina"]:
        await api_call("POST", "/api/services/cover/set_cover_position", json={"entity_id": e, "position": p})
    return f"Cortinas al {p}%"

async def cmd_cine():
    await api_call("POST", "/api/services/script/turn_on", json={"entity_id": "script.sync_activar_cine"})
    return "🎬 Modo CINE activado"

async def cmd_fiesta():
    await api_call("POST", "/api/services/script/turn_on", json={"entity_id": "script.sync_activar_fiesta"})
    return "🎉 Modo FIESTA activado"

async def cmd_noche():
    await api_call("POST", "/api/services/script/turn_on", json={"entity_id": "script.sync_activar_noche"})
    return "🌙 Modo NOCHE activado"

async def cmd_despertar():
    await api_call("POST", "/api/services/script/turn_on", json={"entity_id": "script.sync_desactivar_noche"})
    return "☀️ Modo NOCHE desactivado"

async def cmd_seguridad():
    st, bd = await api_call("GET", "/api/states/input_boolean.security_mode_armed")
    armed = json.loads(bd).get("state")=="on"
    act = "off" if armed else "on"
    await api_call("POST", f"/api/services/input_boolean/turn_{act}", json={"entity_id": "input_boolean.security_mode_armed"})
    return f"Alarma {'DES' if armed else ''}ACTIVADA"

async def cmd_clima():
    for e in ["sensor.temperature","input_number.thermostat_target"]:
        st, bd = await api_call("GET", f"/api/states/{e}")
        if st==200: v = json.loads(bd).get("state","?")
        if "thermostat" in e: target=v
        else: temp=v
    return f"Temp: {temp}C / Objetivo: {target}C"

async def cmd_energia():
    st, bd = await api_call("GET", "/api/states/sensor.medidor_electrico_potencia")
    p = json.loads(bd).get("state","?") if st==200 else "?"
    return f"Consumo: {p} W"

async def cmd_position(who):
    entity = f"person.{who}"
    st, bd = await api_call("GET", f"/api/states/{entity}")
    if st==200:
        s = json.loads(bd).get("state","?")
        return f"{who}: {'en casa' if s=='home' else 'fuera'}"
    return f"{who}: desconocido"

async def cmd_luces():
    res = []
    for e in ["light.rayo","light.joker","light.ventana_c_luz_de_fondo","light.ventana_t_luz_de_fondo","light.led_bulb_w509z2"]:
        st, bd = await api_call("GET", f"/api/states/{e}")
        if st==200:
            s = json.loads(bd).get("state","?")
            res.append(f"{'🟢' if s=='on' else '🔴'} {e.split('.')[1]}")
    return "Luces:\\n" + "\\n".join(res)

async def cmd_camara():
    cams = ["camera.timbro_hack","camera.el_ojo"]
    res = []
    for e in cams:
        st, bd = await api_call("GET", f"/api/states/{e}")
        if st==200:
            s = json.loads(bd).get("state","?")
            res.append(f"{e.split('.')[1]}: {s}")
    return "Camaras:\\n" + "\\n".join(res)

ROUTES = {
    "/help": cmd_help, "/home": cmd_home, "/luzon": cmd_luz_on, "/luzoff": cmd_luz_off,
    "/cortinas": lambda: cmd_cortinas("100"), "/cortinasc": lambda: cmd_cortinas("0"),
    "/cine": cmd_cine, "/fiesta": cmd_fiesta, "/noche": cmd_noche, "/despertar": cmd_despertar,
    "/seguridad": cmd_seguridad, "/clima": cmd_clima, "/energia": cmd_energia,
    "/david": lambda: cmd_position("david_nows"), "/neo": lambda: cmd_position("neo44hd"),
    "/luces": cmd_luces, "/camaras": cmd_camara,
}

async def handle(msg):
    text = msg.get("text","")
    chat = msg.get("chat",{}).get("id")
    if not text or not chat: return
    parts = text.strip().split()
    cmd = parts[0].lower()
    arg = parts[1] if len(parts)>1 else ""

    if cmd == "/cortinas" and arg:
        resp = await cmd_cortinas(arg)
    elif cmd in ROUTES:
        f = ROUTES[cmd]
        if callable(f):
            resp = await f()
        else:
            resp = str(f)
    else:
        resp = await cmd_help()
    await send(resp, chat)

async def main():
    log.info(f"BrainBot started")
    offset = 0
    while True:
        try:
            r = await tg("getUpdates", offset=offset, timeout=30, allowed_updates=["message"])
            for u in r.get("result",[]):
                offset = u["update_id"]+1
                await handle(u.get("message",{}))
        except Exception as e:
            log.error(f"Error: {e}")
            await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(main())
'''
    os.makedirs("/Users/davidnows/scripts/bot", exist_ok=True)
    with open("/Users/davidnows/scripts/bot/brainbot.py", "w") as f:
        f.write(bot_code)
    os.chmod("/Users/davidnows/scripts/bot/brainbot.py", 0o755)
    print("   Bot: brainbot.py creado")

def create_systemd_service():
    """Crear servicio systemd para el bot"""
    svc = """[Unit]
Description=BrainBot Telegram - Casa Sync
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /Users/davidnows/scripts/bot/brainbot.py
Restart=always
RestartSec=5
Environment=TG_BOT_TOKEN=PON_TOKEN_AQUI
Environment=TG_CHAT_ID=PON_CHAT_ID_AQUI
WorkingDirectory=/Users/davidnows/scripts/bot
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
"""
    svc_path = "/Users/davidnows/scripts/bot/brainbot.service"
    with open(svc_path, "w") as f:
        f.write(svc)
    print("   Service: brainbot.service creado")

    # Intentar instalar
    try:
        os.system("sudo cp /Users/davidnows/scripts/bot/brainbot.service /etc/systemd/system/brainbot.service")
        os.system("sudo systemctl daemon-reload")
        os.system("sudo systemctl enable brainbot")
        # No iniciar aun - necesita tokens
        print("   Service instalado (NO iniciado - necesita tokens)")
    except Exception as e:
        print(f"   Service no instalado: {e}")

async def main():
    print("=== CONFIGURACION COMPLETA ===")
    print("\n1. Dashboard Lovelace...")
    config_dir = find_ha_config_dir()
    print(f"   Config dir HA: {config_dir or 'No encontrado'}")
    write_dashboard_yaml(config_dir)

    print("\n2. Bot Telegram...")
    await create_telegram_bot_script()
    create_systemd_service()

    print("\n" + "="*50)
    print("INSTALACION COMPLETADA")
    print("="*50)
    print("""
  PASOS RESTANTES:
  1. Copia /Users/davidnows/scripts/ui-lovelace.yaml al config de HA
  2. Abre File Editor y verifica el dashboard
  3. Configura tokens del bot:
     nano /Users/davidnows/scripts/bot/brainbot.py
     - TG_BOT_TOKEN: token del bot de @BotFather
     - TG_CHAT_ID: tu chat ID
  4. Carga variables:
     export TG_BOT_TOKEN='tu_token'
     export TG_CHAT_ID='tu_chat_id'
     python3 /Users/davidnows/scripts/bot/brainbot.py
  5. Reinicia HA dashboard:
     Service -> Home Assistant -> Reload Lovelace
""")

asyncio.run(main())