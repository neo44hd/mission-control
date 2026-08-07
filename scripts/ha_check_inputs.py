"""Verificar estado actual de HA y crear lo que falta"""
import asyncio, aiohttp, json

HASS = "http://192.168.3.168:8123"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIwNjkwMWU5YjE5NzA0NDRlOThhNzA3MGU4MDFhODUxNCIsImlhdCI6MTc4MTQ2Nzg4MywiZXhwIjoyMDk2ODI3ODgzfQ.gP0SM8Uol3Bz09FrhU5fv5fkyP4pJmcxuTXtjm2ktqc"
H = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

async def main():
    s = aiohttp.ClientSession()

    # Obtener todas las entidades
    r = await s.get(f"{HASS}/api/states", headers=H, timeout=aiohttp.ClientTimeout(total=15))
    entities = json.loads(await r.text())
    entity_ids = [e["entity_id"] for e in entities]
    print(f"Total entidades: {len(entity_ids)}")

    # Verificar inputs boolean necesarios
    bool_inputs = [
        "input_boolean.sync_night_mode_enabled",
        "input_boolean.sync_bienvenida_enabled",
        "input_boolean.auto_lighting_enabled",
        "input_boolean.camera_recording_enabled",
        "input_boolean.david_home",
        "input_boolean.neo44hd_home",
        "input_boolean.doorbell_notifications",
        "input_boolean.security_mode_armed",
        "input_boolean.auto_climate_enabled",
        "input_boolean.fan_enabled",
        "input_boolean.party_mode_enabled",
        "input_boolean.movie_mode_enabled",
        "input_boolean.sync_night_mode_active",
        "input_boolean.sync_manual_night_mode",
    ]

    missing_bool = [e for e in bool_inputs if e not in entity_ids]
    print(f"\nFaltan {len(missing_bool)} inputs boolean: {missing_bool}")

    for eid in missing_bool:
        data = {"entity_id": eid}
        r2 = await s.post(f"{HASS}/api/states/{eid}",
            json={"state": "off", "attributes": {"friendly_name": eid.replace("input_boolean.", "").replace("_", " ").title()}},
            headers=H, timeout=aiohttp.ClientTimeout(total=5))
        result = "OK" if r2.status in (200, 201) else f"FAIL {r2.status}"
        print(f"  {result}: {eid}")

    # Verificar inputs numéricos
    num_inputs = [
        ("input_number.living_room_brightness", 80, 0, 100),
        ("input_number.night_brightness", 20, 0, 100),
        ("input_number.blinds_position", 50, 0, 100),
        ("input_number.thermostat_target", 22, 16, 30),
    ]
    missing_num = [(e, d, mn, mx) for e, d, mn, mx in num_inputs if e not in entity_ids]
    print(f"\nFaltan {len(missing_num)} inputs numericos: {[e[0] for e in missing_num]}")

    for eid, default, mn, mx in missing_num:
        r2 = await s.post(f"{HASS}/api/states/{eid}",
            json={"state": str(default), "attributes": {
                "friendly_name": eid.replace("input_number.", "").replace("_", " ").title(),
                "min": mn, "max": mx, "step": 1, "unit_of_measurement": "%"
            }},
            headers=H, timeout=aiohttp.ClientTimeout(total=5))
        result = "OK" if r2.status in (200, 201) else f"FAIL {r2.status}"
        print(f"  {result}: {eid}")

    # Verificar input select
    select_inputs = [
        ("input_select.house_mode", ["Auto", "Relax", "Trabajo", "Fiesta", "Cine", "Noche"]),
        ("input_select.music_source", ["Spotify", "Radio", "Local", "TV"]),
    ]
    missing_sel = [(e, opts) for e, opts in select_inputs if e not in entity_ids]
    print(f"\nFaltan {len(missing_sel)} inputs select: {[e[0] for e in missing_sel]}")

    for eid, options in missing_sel:
        r2 = await s.post(f"{HASS}/api/states/{eid}",
            json={"state": "Auto", "attributes": {
                "friendly_name": eid.replace("input_select.", "").replace("_", " ").title(),
                "options": options
            }},
            headers=H, timeout=aiohttp.ClientTimeout(total=5))
        result = "OK" if r2.status in (200, 201) else f"FAIL {r2.status}"
        print(f"  {result}: {eid}")

    await s.close()
    print("\n=== CHECK COMPLETADO ===")

asyncio.run(main())