"""Fix scenes (cover format correcto) + crear automatizaciones adicionales"""
import asyncio, aiohttp, json

HASS = "http://192.168.3.168:8123"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIwNjkwMWU5YjE5NzA0NDRlOThhNzA3MGU4MDFhODUxNCIsImlhdCI6MTc4MTQ2Nzg4MywiZXhwIjoyMDk2ODI3ODgzfQ.gP0SM8Uol3Bz09FrhU5fv5fkyP4pJmcxuTXtjm2ktqc"
H = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

async def main():
    s = aiohttp.ClientSession()

    # ============================================================
    # SCENES — Cover con state + attributes correctos
    # ============================================================
    print("🎬 SCENES (formato corregido):")

    scenes = [
        ("scene.modo_relax", "Modo Relax", {
            "light.ventana_c_luz_de_fondo": {"state": "on", "brightness_pct": 30},
            "light.ventana_t_luz_de_fondo": {"state": "on", "brightness_pct": 30},
            "light.vesti_garaje_luz_de_fondo": {"state": "on", "brightness_pct": 25},
            "light.vesti_grout_luz_de_fondo": {"state": "on", "brightness_pct": 25},
            "cover.ventana_c_cortina": {"state": "open", "current_position": 50},
            "cover.ventana_t_cortina": {"state": "open", "current_position": 50},
        }),
        ("scene.modo_trabajo", "Modo Trabajo", {
            "light.ventana_c_luz_de_fondo": {"state": "on", "brightness_pct": 90},
            "light.ventana_t_luz_de_fondo": {"state": "on", "brightness_pct": 90},
            "light.vesti_garaje_luz_de_fondo": {"state": "on", "brightness_pct": 80},
            "light.vesti_grout_luz_de_fondo": {"state": "on", "brightness_pct": 80},
            "cover.ventana_c_cortina": {"state": "open", "current_position": 100},
            "cover.ventana_t_cortina": {"state": "open", "current_position": 100},
        }),
        ("scene.modo_fiesta", "Modo Fiesta", {
            "light.ventana_c_luz_de_fondo": {"state": "on", "brightness_pct": 100},
            "light.ventana_t_luz_de_fondo": {"state": "on", "brightness_pct": 100},
            "light.vesti_garaje_luz_de_fondo": {"state": "on", "brightness_pct": 100},
            "light.vesti_grout_luz_de_fondo": {"state": "on", "brightness_pct": 100},
            "light.joker": {"state": "on", "brightness_pct": 80},
            "light.rayo": {"state": "on", "brightness_pct": 100},
            "cover.ventana_c_cortina": {"state": "closed", "current_position": 0},
            "cover.ventana_t_cortina": {"state": "closed", "current_position": 0},
        }),
        ("scene.modo_cine", "Modo Cine", {
            "light.ventana_c_luz_de_fondo": {"state": "off"},
            "light.ventana_t_luz_de_fondo": {"state": "off"},
            "light.vesti_garaje_luz_de_fondo": {"state": "off"},
            "light.vesti_grout_luz_de_fondo": {"state": "off"},
            "light.joker": {"state": "on", "brightness_pct": 15},
            "cover.ventana_c_cortina": {"state": "closed", "current_position": 0},
            "cover.ventana_t_cortina": {"state": "closed", "current_position": 0},
        }),
        ("scene.modo_noche_total", "Modo Noche Total", {
            "light.ventana_c_luz_de_fondo": {"state": "off"},
            "light.ventana_t_luz_de_fondo": {"state": "off"},
            "light.vesti_garaje_luz_de_fondo": {"state": "off"},
            "light.vesti_grout_luz_de_fondo": {"state": "off"},
            "light.rayo": {"state": "off"},
            "light.joker": {"state": "off"},
            "light.led_bulb_w509z2": {"state": "off"},
            "light.led_bulb_w509z2_2": {"state": "off"},
            "cover.ventana_c_cortina": {"state": "closed", "current_position": 80},
            "cover.ventana_t_cortina": {"state": "closed", "current_position": 80},
        }),
    ]

    for eid, name, entities in scenes:
        try:
            r = await s.post(f"{HASS}/api/config/scene/config/{eid}",
                json={"name": name, "entities": entities},
                headers=H, timeout=aiohttp.ClientTimeout(total=8))
            if r.status in (200, 201):
                print(f"  ✅ {name}")
            else:
                body = await r.text()
                print(f"  ⚠️ {name}: HTTP {r.status} — {body[:150]}")
        except Exception as ex:
            print(f"  ❌ {name}: {ex}")

    # ============================================================
    # AUTOMATIZACIONES ADICIONALES
    # ============================================================
    print("\n🔧 AUTOMATIZACIONES ADICIONALES:")

    extra_automations = [
        # Auto-movie mode: si es viernes/sábado noche + nadie en casa enciende cine
        {
            "id": "sync_auto_movie_friday",
            "alias": "🎬 Auto Cine Viernes",
            "description": "Viernes/sábado noche → Modo Cine automático",
            "trigger": [{"platform": "time", "at": "21:00:00"}],
            "condition": [
                {"condition": "state", "entity_id": "input_boolean.movie_mode_enabled", "state": "on"},
                {"condition": "or", "conditions": [
                    {"condition": "time", "weekday": ["fri"]},
                    {"condition": "time", "weekday": ["sat"]},
                ]},
                {"condition": "state", "entity_id": "person.david_nows", "state": "home"},
            ],
            "action": [
                {"service": "scene.turn_on", "data": {"entity_id": "scene.modo_cine"}},
                {"service": "persistent_notification.create", "data": {
                    "title": "🎬 Modo Cine",
                    "message": "Viernes noche → Modo Cine activado automáticamente"
                }},
            ],
            "mode": "single",
        },
        # Ventanas automáticas al amanecer
        {
            "id": "sync_ventanas_amanecer",
            "alias": "🌅 Abrir Ventanas Amanecer",
            "description": "Abre cortinas al amanecer si modo noche no activo",
            "trigger": [{"platform": "sun", "event": "sunrise", "offset": "-00:15:00"}],
            "condition": [
                {"condition": "state", "entity_id": "input_boolean.auto_blinds_enabled", "state": "on"},
                {"condition": "state", "entity_id": "input_boolean.sync_night_mode_active", "state": "off"},
            ],
            "action": [
                {"service": "cover.set_cover_position", "target": {"entity_id": [
                    "cover.ventana_c_cortina", "cover.ventana_t_cortina"
                ]}, "data": {"position": 100}},
                {"service": "persistent_notification.create", "data": {
                    "title": "🌅 Amanecer",
                    "message": "Cortinas abiertas al amanecer"
                }},
            ],
            "mode": "single",
        },
        # Cerrar cortinas al anochecer
        {
            "id": "sync_ventanas_anochecer",
            "alias": "🌇 Cerrar Ventanas Atardecer",
            "description": "Cierra cortinas al anochecer",
            "trigger": [{"platform": "sun", "event": "sunset", "offset": "00:10:00"}],
            "condition": [
                {"condition": "state", "entity_id": "input_boolean.auto_blinds_enabled", "state": "on"},
            ],
            "action": [
                {"service": "cover.set_cover_position", "target": {"entity_id": [
                    "cover.ventana_c_cortina", "cover.ventana_t_cortina"
                ]}, "data": {"position": 0}},
            ],
            "mode": "single",
        },
        # Toggle movie mode
        {
            "id": "sync_toggle_movie",
            "alias": "🎬 Toggle Modo Cine",
            "description": "Intercambia modo cine on/off",
            "trigger": [{"platform": "event", "event_type": "toggle_movie_mode"}],
            "condition": [],
            "action": [
                {"service": "input_boolean.toggle", "target": {"entity_id": "input_boolean.movie_mode_enabled"}},
                {"service": "input_boolean.toggle", "target": {"entity_id": "input_boolean.party_mode_enabled"}},
            ],
            "mode": "restart",
        },
        # Presencia: actualizar flags cuando cambian personas
        {
            "id": "sync_presencia_update",
            "alias": "👨‍💻 Actualizar Presencia",
            "description": "Actualiza flags de presencia cuando alguien llega o se va",
            "trigger": [
                {"platform": "state", "entity_id": "person.david_nows"},
                {"platform": "state", "entity_id": "person.neo44hd"},
            ],
            "condition": [],
            "action": [
                {"service": "input_boolean.turn_on", "target": {"entity_id": "input_boolean.david_home"},
                 "if": [{"condition": "state", "entity_id": "person.david_nows", "state": "home"}]},
                {"service": "input_boolean.turn_off", "target": {"entity_id": "input_boolean.david_home"},
                 "if": [{"condition": "state", "entity_id": "person.david_nows", "state": "not_home"}]},
            ],
            "mode": "restart",
        },
    ]

    created = 0
    errors = 0
    for auto in extra_automations:
        try:
            eid = auto.pop("id")
            name = auto.pop("alias")
            r = await s.post(f"{HASS}/api/config/automation/config/{eid}",
                json=auto, headers=H, timeout=aiohttp.ClientTimeout(total=8))
            if r.status in (200, 201):
                print(f"  ✅ {name}")
                created += 1
            else:
                body = await r.text()
                print(f"  ⚠️ {name}: HTTP {r.status} — {body[:120]}")
                errors += 1
        except Exception as ex:
            print(f"  ❌ {ex}")
            errors += 1

    print(f"\n  Resultado: {created} creadas, {errors} errores")

    # Reload
    try:
        r = await s.post(f"{HASS}/api/services/automation/reload", headers=H, timeout=aiohttp.ClientTimeout(total=8))
        print(f"  🔄 Reload automations: HTTP {r.status}")
    except Exception as ex:
        print(f"  ❌ Reload error: {ex}")

    await s.close()
    print("\n✅ Todo completado")

asyncio.run(main())