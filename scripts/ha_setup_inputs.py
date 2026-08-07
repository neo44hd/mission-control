"""Configurar todos los inputs booleanos del sistema con estados iniciales correctos"""
import asyncio, aiohttp, json

HASS = "http://192.168.3.168:8123"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIwNjkwMWU5YjE5NzA0NDRlOThhNzA3MGU4MDFhODUxNCIsImlhdCI6MTc4MTQ2Nzg4MywiZXhwIjoyMDk2ODI3ODgzfQ.gP0SM8Uol3Bz09FrhU5fv5fkyP4pJmcxuTXtjm2ktqc"
H = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

async def main():
    s = aiohttp.ClientSession()

    # ============================================================
    # INPUTS BOOLEANOS — VALORES INICIALES
    # ============================================================
    inputs = [
        # Sistema
        ("input_boolean.ha_startup_complete",       "Sistema HA arrancado",                    "on"),
        ("input_boolean.telegram_connected",         "Telegram conectado",                      "on"),
        ("input_boolean.alexa_connected",            "Alexa conectada",                         "on"),

        # Modo Noche
        ("input_boolean.sync_night_mode_enabled",    "Modo noche habilitado",                   "on"),
        ("input_boolean.sync_night_mode_active",     "Modo noche activo",                       "off"),
        ("input_boolean.sync_manual_night_mode",     "Modo noche manual",                       "off"),

        # Bienvenida
        ("input_boolean.sync_bienvenida_enabled",    "Bienvenida a casa habilitada",            "on"),

        # Ahorro
        ("input_boolean.sync_ahorro_enabled",        "Ahorro energía habilitado",               "on"),

        # Audio / Multiroom
        ("input_boolean.multiroom_enabled",          "Multiroom altavoces habilitado",          "on"),
        ("input_boolean.spotify_sync_enabled",       "Spotify sync habilitado",                 "on"),

        # Seguridad
        ("input_boolean.security_mode_enabled",      "Modo seguridad habilitado",               "on"),
        ("input_boolean.security_mode_armed",        "Modo seguridad armado",                   "off"),
        ("input_boolean.camera_recording_enabled",   "Grabación cámaras habilitada",            "on"),
        ("input_boolean.doorbell_notifications",     "Notificaciones timbre habilitadas",       "on"),

        # Iluminación
        ("input_boolean.auto_lighting_enabled",      "Iluminación automática habilitada",       "on"),
        ("input_boolean.movie_mode_enabled",         "Modo cine habilitado",                    "off"),
        ("input_boolean.party_mode_enabled",         "Modo fiesta habilitado",                  "off"),

        # Climatización
        ("input_boolean.auto_climate_enabled",       "Climatización automática habilitada",     "on"),
        ("input_boolean.fan_enabled",                "Ventilador habilitado",                   "on"),

        # Cortinas
        ("input_boolean.auto_blinds_enabled",        "Persianas automáticas habilitadas",       "on"),
        ("input_boolean.curtains_morning_enabled",   "Abrir cortinas mañana habilitado",        "on"),

        # Presencia
        ("input_boolean.david_home",                 "David en casa",                           "off"),
        ("input_boolean.neo44hd_home",               "Neo44hd en casa",                         "off"),

        # Notificaciones
        ("input_boolean.push_notifications_enabled", "Push notifications habilitadas",          "on"),
        ("input_boolean.telegram_alerts",            "Alertas Telegram habilitadas",            "on"),
    ]

    created = 0
    errors = 0
    for entity_id, name, default_state in inputs:
        try:
            r = await s.post(f"{HASS}/api/states/{entity_id}",
                json={"state": default_state, "attributes": {"friendly_name": name}},
                headers=H, timeout=aiohttp.ClientTimeout(total=5))
            if r.status in (200, 201):
                print(f"  ✅ {name}: {default_state} ({entity_id})")
                created += 1
            else:
                body = await r.text()
                print(f"  ⚠️ {name}: HTTP {r.status} — {body[:80]}")
                errors += 1
        except Exception as ex:
            print(f"  ❌ {name}: {ex}")
            errors += 1

    # ============================================================
    # INPUTS NUMÉRICOS
    # ============================================================
    print("\n📊 INPUTS NUMÉRICOS:")
    num_inputs = [
        ("input_number.living_room_brightness",   "Brillo salón",              70,  0, 100, 1),
        ("input_number.thermostat_target",        "Temperatura objetivo",      22,  16, 30, 0.5),
        ("input_number.volume_master",            "Volumen maestro",           25,  0, 100, 1),
        ("input_number.night_brightness",         "Brillo nocturno",           10,  0, 100, 1),
        ("input_number.blinds_position",          "Posición persianas",        80,  0, 100, 5),
        ("input_number.energy_threshold_watts",   "Umbral ahorro energía",     500, 0, 3000, 50),
    ]

    for entity_id, name, default, min_v, max_v, step in num_inputs:
        try:
            r = await s.post(f"{HASS}/api/states/{entity_id}",
                json={"state": str(default), "attributes": {
                    "friendly_name": name,
                    "min": min_v, "max": max_v, "step": step
                }},
                headers=H, timeout=aiohttp.ClientTimeout(total=5))
            if r.status in (200, 201):
                print(f"  ✅ {name}: {default} ({entity_id})")
                created += 1
            else:
                body = await r.text()
                print(f"  ⚠️ {name}: HTTP {r.status} — {body[:80]}")
                errors += 1
        except Exception as ex:
            print(f"  ❌ {name}: {ex}")
            errors += 1

    # ============================================================
    # INPUTS SELECT
    # ============================================================
    print("\n📋 INPUTS SELECT:")
    select_inputs = [
        ("input_select.house_mode", "Modo de casa", ["auto", "casa", "noche", "fiesta", "fuera", "cine"], "auto"),
        ("input_select.music_source", "Fuente música", ["spotify", "radio", "tts", "off"], "spotify"),
        ("input_select.lighting_scene", "Escena iluminación", ["relax", "trabajo", "fiesta", "noche", "amanecer"], "relax"),
    ]

    for entity_id, name, options, default in select_inputs:
        try:
            r = await s.post(f"{HASS}/api/states/{entity_id}",
                json={"state": default, "attributes": {
                    "friendly_name": name,
                    "options": options
                }},
                headers=H, timeout=aiohttp.ClientTimeout(total=5))
            if r.status in (200, 201):
                print(f"  ✅ {name}: {default} ({entity_id})")
                created += 1
            else:
                body = await r.text()
                print(f"  ⚠️ {name}: HTTP {r.status} — {body[:80]}")
                errors += 1
        except Exception as ex:
            print(f"  ❌ {name}: {ex}")
            errors += 1

    # ============================================================
    # SCENES PREDEFINIDAS
    # ============================================================
    print("\n🎬 SCENES PREDEFINIDAS:")
    scenes = [
        {
            "entity_id": "scene.modo_relax",
            "name": "Modo Relax",
            "data": {
                "entities": {
                    "light.ventana_c_luz_de_fondo": {"state": "on", "brightness_pct": 30},
                    "light.ventana_t_luz_de_fondo": {"state": "on", "brightness_pct": 30},
                    "light.vesti_garaje_luz_de_fondo": {"state": "on", "brightness_pct": 25},
                    "light.vesti_grout_luz_de_fondo": {"state": "on", "brightness_pct": 25},
                    "cover.ventana_c_cortina": {"position": 50},
                    "cover.ventana_t_cortina": {"position": 50},
                }
            }
        },
        {
            "entity_id": "scene.modo_trabajo",
            "name": "Modo Trabajo",
            "data": {
                "entities": {
                    "light.ventana_c_luz_de_fondo": {"state": "on", "brightness_pct": 90},
                    "light.ventana_t_luz_de_fondo": {"state": "on", "brightness_pct": 90},
                    "light.vesti_garaje_luz_de_fondo": {"state": "on", "brightness_pct": 80},
                    "light.vesti_grout_luz_de_fondo": {"state": "on", "brightness_pct": 80},
                    "cover.ventana_c_cortina": {"position": 100},
                    "cover.ventana_t_cortina": {"position": 100},
                }
            }
        },
        {
            "entity_id": "scene.modo_fiesta",
            "name": "Modo Fiesta",
            "data": {
                "entities": {
                    "light.ventana_c_luz_de_fondo": {"state": "on", "brightness_pct": 100},
                    "light.ventana_t_luz_de_fondo": {"state": "on", "brightness_pct": 100},
                    "light.vesti_garaje_luz_de_fondo": {"state": "on", "brightness_pct": 100},
                    "light.vesti_grout_luz_de_fondo": {"state": "on", "brightness_pct": 100},
                    "light.joker": {"state": "on", "brightness_pct": 80},
                    "light.rayo": {"state": "on", "brightness_pct": 100},
                    "cover.ventana_c_cortina": {"position": 0},
                    "cover.ventana_t_cortina": {"position": 0},
                }
            }
        },
        {
            "entity_id": "scene.modo_cine",
            "name": "Modo Cine",
            "data": {
                "entities": {
                    "light.ventana_c_luz_de_fondo": {"state": "off"},
                    "light.ventana_t_luz_de_fondo": {"state": "off"},
                    "light.vesti_garaje_luz_de_fondo": {"state": "off"},
                    "light.vesti_grout_luz_de_fondo": {"state": "off"},
                    "light.joker": {"state": "on", "brightness_pct": 15},
                    "cover.ventana_c_cortina": {"position": 0},
                    "cover.ventana_t_cortina": {"position": 0},
                }
            }
        },
        {
            "entity_id": "scene.modo_noche_total",
            "name": "Modo Noche Total",
            "data": {
                "entities": {
                    "light.ventana_c_luz_de_fondo": {"state": "off"},
                    "light.ventana_t_luz_de_fondo": {"state": "off"},
                    "light.vesti_garaje_luz_de_fondo": {"state": "off"},
                    "light.vesti_grout_luz_de_fondo": {"state": "off"},
                    "light.rayo": {"state": "off"},
                    "light.joker": {"state": "off"},
                    "light.led_bulb_w509z2": {"state": "off"},
                    "light.led_bulb_w509z2_2": {"state": "off"},
                    "cover.ventana_c_cortina": {"position": 80},
                    "cover.ventana_t_cortina": {"position": 80},
                }
            }
        },
    ]

    for scene in scenes:
        try:
            r = await s.post(f"{HASS}/api/config/scene/config/{scene['entity_id']}",
                json=scene, headers=H, timeout=aiohttp.ClientTimeout(total=8))
            if r.status in (200, 201):
                print(f"  ✅ {scene['name']}")
                created += 1
            else:
                body = await r.text()
                print(f"  ⚠️ {scene['name']}: HTTP {r.status} — {body[:80]}")
                errors += 1
        except Exception as ex:
            print(f"  ❌ {scene['name']}: {ex}")
            errors += 1

    await s.close()
    print(f"\n{'='*60}")
    print(f"  Total: {created} creados, {errors} errores")

asyncio.run(main())