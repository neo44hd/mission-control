"""DEEP SCAN: encontrar todos los dispositivos ocultos + probar creación de automatizaciones"""
import asyncio, aiohttp, json, sys

HASS = "http://192.168.3.168:8123"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIwNjkwMWU5YjE5NzA0NDRlOThhNzA3MGU4MDFhODUxNCIsImlhdCI6MTc4MTQ2Nzg4MywiZXhwIjoyMDk2ODI3ODgzfQ.gP0SM8Uol3Bz09FrhU5fv5fkyP4pJmcxuTXtjm2ktqc"
H = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

def jprint(label, obj, limit=600):
    text = json.dumps(obj, indent=2, ensure_ascii=False)
    if len(text) > limit:
        text = text[:limit] + f"\n  ... ({len(text)} total)"
    print(f"  {label}: {text}")

async def main():
    s = aiohttp.ClientSession()
    found_new = []
    entities = []
    by_domain = {}

    # ============================================================
    # FASE 1: BARRIDO TOTAL DE TODAS LAS ENTIDADES
    # ============================================================
    print("=" * 70)
    print("🚀 FASE 1: BARRIDO TOTAL DE ENTIDADES")
    print("=" * 70)

    try:
        r = await s.get(f"{HASS}/api/states", headers=H, timeout=aiohttp.ClientTimeout(total=15))
        entities = json.loads(await r.text())
        for e in entities:
            dom = e["entity_id"].split(".")[0]
            if dom not in by_domain:
                by_domain[dom] = []
            by_domain[dom].append(e)
    except Exception as ex:
        print(f"  ❌ Error obteniendo estados: {ex}")
        await s.close()
        return

    for dom in sorted(by_domain.keys()):
        items = by_domain[dom]
        print(f"\n  📦 [{dom}] ({len(items)} entidades)")
        for e in items:
            eid = e["entity_id"]
            fid = e.get("attributes", {}).get("friendly_name", eid)
            state = e.get("state", "?")
            if state != "unavailable":
                icon = "🟢" if state == "on" else "🔴" if state == "off" else "🟡"
                extra = ""
                attr = e.get("attributes", {})
                if "current_position" in attr:
                    extra = f" pos={attr['current_position']}%"
                if "brightness" in attr and attr["brightness"] != "?":
                    extra += f" bri={attr['brightness']}"
                if "volume_level" in attr:
                    extra += f" vol={attr['volume_level']}"
                if "temperature" in attr:
                    extra += f" temp={attr['temperature']}"
                if state == "?":
                    icon = "⚪"
                print(f"    {icon} {fid:45s} = {state:12s}{extra}")
                if dom in ("button","valve","humidifier","dehumidifier","fan",
                           "input_boolean","input_text","input_number","input_select",
                           "input_datetime","input_button","counter","timer",
                           "number","select","vacuum","cover","light",
                           "alarm_control_panel","siren","tag") and state in ("on","off"):
                    found_new.append((dom, fid, eid, state))

    # ============================================================
    # FASE 2: DISPOSITIVOS Y ÁREAS
    # ============================================================
    print("\n" + "=" * 70)
    print("🗺️ FASE 2: DISPOSITIVOS Y ÁREAS")
    print("=" * 70)

    try:
        r = await s.get(f"{HASS}/api/config/entries", headers=H, timeout=aiohttp.ClientTimeout(total=8))
        if r.status == 200:
            entries = json.loads(await r.text())
            print(f"\n  🔌 Config Entries ({len(entries)}):")
            for entry in entries:
                title = entry.get("title", "?")
                domain = entry.get("domain", "?")
                eid = entry.get("entry_id", "?")
                state = entry.get("state", "?")
                pref = entry.get("prefs", {})
                print(f"    [{domain:25s}] {title:30s} state={state:10s}")
                if pref:
                    for k, v in pref.items():
                        if "token" not in k.lower() and "password" not in k.lower() and "key" != k.lower():
                            print(f"      {k}: {v}")
    except Exception as ex:
        print(f"  Error config entries: {ex}")

    try:
        r = await s.get(f"{HASS}/api/events", headers=H, timeout=aiohttp.ClientTimeout(total=5))
        if r.status == 200:
            events = json.loads(await r.text())
            print(f"\n  📡 Eventos recientes ({len(events)}):")
            for ev in events[:20]:
                print(f"    - {ev.get('event_type', '?')}: data={ev.get('data', {})}")
    except Exception as ex:
        print(f"  Error events: {ex}")

    # ============================================================
    # FASE 3: HARDWARE / SISTEMA
    # ============================================================
    print("\n" + "=" * 70)
    print("🔩 FASE 3: HARDWARE")
    print("=" * 70)
    try:
        r = await s.get(f"{HASS}/api/hardware", headers=H, timeout=aiohttp.ClientTimeout(total=8))
        if r.status == 200:
            hw = json.loads(await r.text())
            print(f"  Hardware entries: {len(hw)}")
            for h in hw[:10]:
                print(f"    - {h.get('name','?')}: {h.get('board','?')} | {h.get('manufacturer','?')}")
    except Exception as ex:
        print(f"  Error hardware: {ex}")

    # ============================================================
    # FASE 4: CREAR INPUTS BOOLEANOS NECESARIOS
    # ============================================================
    print("\n" + "=" * 70)
    print("🔧 FASE 4: INPUTS BOOLEANOS PARA LAS AUTOMATIZACIONES")
    print("=" * 70)

    inputs_needed = [
        ("input_boolean.sync_manual_night_mode", "Modo noche manual (bloquea auto-luz)"),
        ("input_boolean.sync_night_mode_enabled", "Modo noche habilitado"),
        ("input_boolean.sync_night_mode_active", "Modo noche activo"),
        ("input_boolean.sync_bienvenida_enabled", "Bienvenida a casa habilitada"),
        ("input_boolean.sync_ahorro_enabled", "Ahorro energía habilitado"),
    ]

    for entity_id, name in inputs_needed:
        try:
            r = await s.post(f"{HASS}/api/states/{entity_id}",
                json={"state": "on", "attributes": {"friendly_name": name}},
                headers=H, timeout=aiohttp.ClientTimeout(total=5))
            if r.status in (200, 201):
                print(f"  ✅ {name}: creado/verificado ({entity_id})")
            else:
                body = await r.text()
                print(f"  ⚠️ {name}: HTTP {r.status} - {body[:100]}")
        except Exception as ex:
            print(f"  ❌ {name}: Error: {ex}")

    # ============================================================
    # FASE 5: CREAR LAS AUTOMATIZACIONES
    # ============================================================
    print("\n" + "=" * 70)
    print("🔧 FASE 5: CREANDO AUTOMATIZACIONES EN HOME ASSISTANT")
    print("=" * 70)

    # Primero verificar si automation.reload funciona
    try:
        r = await s.get(f"{HASS}/api/services/automation", headers=H, timeout=aiohttp.ClientTimeout(total=5))
        if r.status == 200:
            data = json.loads(await r.text())
            svcs = list(data.get("services", {}).keys())
            print(f"  ✅ Servicio 'automation' disponible: {svcs}")
    except Exception as ex:
        print(f"  ❌ Servicio automation no disponible: {ex}")

    automations = [
        {
            "id": "sync_luz_amanecer_atardecer",
            "alias": "🌅 Luz Amanecer/Atardecer",
            "description": "Auto enciende luces al atardecer, apaga al amanecer",
            "trigger": [
                {"platform": "state", "entity_id": "sun.sun", "to": "below_horizon", "for": "00:05:00"},
                {"platform": "state", "entity_id": "sun.sun", "to": "above_horizon", "for": "00:05:00"},
            ],
            "condition": [],
            "action": [
                {
                    "choose": [
                        {
                            "conditions": [{"condition": "state", "entity_id": "sun.sun", "state": "below_horizon"}],
                            "sequence": [
                                {"service": "light.turn_on", "target": {"entity_id": [
                                    "light.ventana_c_luz_de_fondo", "light.ventana_t_luz_de_fondo",
                                    "light.vesti_garaje_luz_de_fondo", "light.vesti_grout_luz_de_fondo"
                                ]}, "data": {"brightness_pct": 70, "transition": 30}},
                            ]
                        },
                        {
                            "conditions": [
                                {"condition": "state", "entity_id": "sun.sun", "state": "above_horizon"},
                                {"condition": "state", "entity_id": "input_boolean.sync_manual_night_mode", "state": "off"},
                            ],
                            "sequence": [
                                {"service": "light.turn_off", "target": {"entity_id": [
                                    "light.ventana_c_luz_de_fondo", "light.ventana_t_luz_de_fondo",
                                    "light.vesti_garaje_luz_de_fondo", "light.vesti_grout_luz_de_fondo"
                                ]}, "data": {"transition": 30}},
                            ]
                        }
                    ]
                }
            ],
            "mode": "single",
        },
        {
            "id": "sync_bienvenida_casa",
            "alias": "🏠 Bienvenida a Casa",
            "description": "Enciende luces y abre cortinas cuando David llega",
            "trigger": [{"platform": "state", "entity_id": "person.david_nows", "to": "home"}],
            "condition": [{"condition": "state", "entity_id": "input_boolean.sync_bienvenida_enabled", "state": "on"}],
            "action": [
                {
                    "parallel": [
                        {"service": "light.turn_on", "target": {"entity_id": [
                            "light.ventana_c_luz_de_fondo", "light.ventana_t_luz_de_fondo",
                            "light.vesti_garaje_luz_de_fondo"
                        ]}, "data": {"brightness_pct": 80, "transition": 15}},
                        {"service": "cover.set_cover_position", "target": {"entity_id": [
                            "cover.ventana_c_cortina", "cover.ventana_t_cortina",
                            "cover.vesti_garaje_cortina", "cover.vesti_grout_cortina"
                        ]}, "data": {"position": 80}},
                    ]
                },
                {"delay": "00:05:00"},
                {"service": "light.turn_on", "target": {"entity_id": [
                    "light.led_bulb_w509z2", "light.led_bulb_w509z2_2"
                ]}, "data": {"brightness_pct": 60, "transition": 10}},
            ],
            "mode": "restart",
        },
        {
            "id": "sync_modo_noche",
            "alias": "🌙 Modo Noche",
            "description": "A las 1:00 activa modo nocturno. Cortinas al 80%, luces apagadas, cámara activa",
            "trigger": [{"platform": "time", "at": "01:00:00"}],
            "condition": [{"condition": "state", "entity_id": "input_boolean.sync_night_mode_enabled", "state": "on"}],
            "action": [
                {
                    "parallel": [
                        {"service": "light.turn_off", "target": {"entity_id": [
                            "light.ventana_c_luz_de_fondo", "light.ventana_t_luz_de_fondo",
                            "light.vesti_garaje_luz_de_fondo", "light.vesti_grout_luz_de_fondo",
                            "light.rayo", "light.led_bulb_w509z2", "light.led_bulb_w509z2_2"
                        ]}, "data": {"transition": 30}},
                        {"service": "cover.set_cover_position", "target": {"entity_id": [
                            "cover.ventana_c_cortina", "cover.ventana_t_cortina",
                            "cover.vesti_garaje_cortina", "cover.vesti_grout_cortina"
                        ]}, "data": {"position": 80}},
                        {"service": "switch.turn_on", "target": {"entity_id": ["switch.timbro_hack_grabacion_de_video"]}},
                    ]
                },
                {"service": "input_boolean.turn_on", "target": {"entity_id": "input_boolean.sync_night_mode_active"}},
            ],
            "mode": "single",
        },
        {
            "id": "sync_desactivar_modo_noche",
            "alias": "☀️ Desactivar Modo Noche",
            "description": "A las 7:00 desactiva modo nocturno",
            "trigger": [
                {"platform": "time", "at": "07:00:00"},
                {"platform": "state", "entity_id": "input_boolean.sync_night_mode_enabled", "to": "off"},
            ],
            "condition": [],
            "action": [
                {"service": "input_boolean.turn_off", "target": {"entity_id": [
                    "input_boolean.sync_night_mode_active", "input_boolean.sync_manual_night_mode"
                ]}},
            ],
            "mode": "single",
        },
        {
            "id": "sync_ahorro_energia",
            "alias": "💰 Ahorro de Energía",
            "description": "Apaga enchufes si nadie está en casa y consumo > 500W",
            "trigger": [{"platform": "numeric_state", "entity_id": "sensor.medidor_electrico_potencia", "above": 500, "for": "00:10:00"}],
            "condition": [
                {"condition": "state", "entity_id": "person.david_nows", "state": "not_home"},
                {"condition": "state", "entity_id": "person.neo44hd", "state": "not_home"},
                {"condition": "state", "entity_id": "input_boolean.sync_ahorro_enabled", "state": "on"},
            ],
            "action": [
                {"service": "switch.turn_off", "target": {"entity_id": [
                    "switch.luz_pica_interruptor_1", "switch.usb_wind_enchufe_1",
                    "switch.usb_wind_enchufe_2", "switch.cocina_interruptor_1",
                    "switch.luz_batcueva_interruptor_1", "switch.cheester_sock_enchufe_1",
                    "switch.chicken_sock_enchufe_1"
                ]}},
                {"service": "persistent_notification.create", "data": {
                    "title": "💰 Ahorro activado",
                    "message": "Enchufes apagados por ahorro de energía. Consumo > 500W con nadie en casa."
                }},
            ],
            "mode": "single",
        },
        {
            "id": "sync_timbre_inteligente",
            "alias": "🔔 Timbre Inteligente",
            "description": "Notifica al teléfono cuando alguien toca el timbre",
            "trigger": [
                {"platform": "state", "entity_id": "binary_sensor.timbro_hack_imagen_del_timbre", "to": "on", "for": "00:00:10"},
                {"platform": "event", "event_type": "doorbell"},
            ],
            "condition": [],
            "action": [
                {
                    "parallel": [
                        {
                            "service": "notify.mobile_app_iphone_15_pro_max",
                            "data": {
                                "title": "🚪 ¡Timbre!",
                                "message": "Alguien ha tocado el timbre en casa",
                                "data": {"image": "/api/camera_proxy/camera.timbro_hack", "priority": "high", "ttl": 0}
                            }
                        },
                        {"service": "camera.snapshot", "target": {"entity_id": "camera.timbro_hack"}, "data": {"filename": "/config/www/timbre_snapshot.jpg"}},
                    ]
                },
                {"delay": "00:00:30"},
                {
                    "service": "notify.mobile_app_iphone_15_pro_max",
                    "data": {
                        "title": "🚪 Timbre - Foto adjunta",
                        "message": "Captura de quien tocó el timbre",
                        "data": {"image": "/config/www/timbre_snapshot.jpg", "priority": "high", "ttl": 0}
                    }
                },
            ],
            "mode": "restart",
        },
    ]

    created = 0
    errors = 0
    for auto in automations:
        try:
            r = await s.post(f"{HASS}/api/config/automation/config/{auto['id']}",
                json=auto, headers=H, timeout=aiohttp.ClientTimeout(total=8))
            body = await r.text()
            if r.status in (200, 201):
                print(f"  ✅ {auto['alias']}: creada")
                created += 1
            else:
                print(f"  ⚠️ {auto['alias']}: HTTP {r.status} — {body[:200]}")
                errors += 1
        except Exception as ex:
            print(f"  ❌ {auto['alias']}: Error: {ex}")
            errors += 1

    print(f"\n  Resultado: {created} creadas, {errors} errores")

    # ============================================================
    # FASE 6: RELOAD AUTOMATIZACIONES
    # ============================================================
    print("\n" + "=" * 70)
    print("🔄 FASE 6: RELOAD DE AUTOMATIZACIONES")
    print("=" * 70)
    try:
        r = await s.post(f"{HASS}/api/services/automation/reload", headers=H, timeout=aiohttp.ClientTimeout(total=8))
        print(f"  ✅ Reload: HTTP {r.status}")
    except Exception as ex:
        print(f"  ❌ Reload error: {ex}")

    # ============================================================
    # FASE 7: BUSCAR DISPOSITIVOS OCULTOS ADICIONALES
    # ============================================================
    print("\n" + "=" * 70)
    print("🔍 FASE 7: BUSQUEDA DE DISPOSITIVOS OCULTOS ADICIONALES")
    print("=" * 70)

    # Buscar dominios que podrían tener dispositivos no descubiertos
    hidden_checks = [
        "scene", "script", "tts", "media_player", "sensor",
        "binary_sensor", "device_tracker", "proximity", "zone",
        "sun", "weather", "calendar", "todo", "shopping_list"
    ]
    for dom in hidden_checks:
        try:
            r = await s.get(f"{HASS}/api/states?type={dom}", headers=H, timeout=aiohttp.ClientTimeout(total=5))
            if r.status == 200:
                items = json.loads(await r.text())
                if items:
                    print(f"  📦 {dom}: {len(items)} entidades")
                    for item in items[:5]:
                        fid = item.get("attributes", {}).get("friendly_name", item["entity_id"])
                        print(f"     - {fid} = {item.get('state', '?')}")
        except Exception:
            pass

    print(f"\n{'=' * 70}")
    print(f"📊 RESUMEN FINAL")
    print(f"{'=' * 70}")
    print(f"  Entidades totales: {len(entities)}")
    print(f"  Dominios activos: {len(by_domain)}")
    print(f"  Automatizaciones creadas: {created}/6")
    print(f"  Inputs booleanos configurados: {len(inputs_needed)}")

    await s.close()

asyncio.run(main())