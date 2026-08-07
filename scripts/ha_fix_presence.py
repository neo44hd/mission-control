"""Parte 1: Arreglar presencia + crear scripts HA"""
import asyncio, aiohttp, json

HASS = "http://192.168.3.168:8123"
HA_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIwNjkwMWU5YjE5NzA0NDRlOThhNzA3MGU4MDFhODUxNCIsImlhdCI6MTc4MTQ2Nzg4MywiZXhwIjoyMDk2ODI3ODgzfQ.gP0SM8Uol3Bz09FrhU5fv5fkyP4pJmcxuTXtjm2ktqc"
HA_HEADERS = {"Authorization": f"Bearer {HA_TOKEN}", "Content-Type": "application/json"}

async def main():
    s = aiohttp.ClientSession()

    # Arreglar presencia
    print("🔧 Presencia...")
    auto = {
        "alias": "Actualizar Presencia",
        "description": "Actualiza flags de presencia",
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
            {"service": "input_boolean.turn_on", "target": {"entity_id": "input_boolean.neo44hd_home"},
             "if": [{"condition": "state", "entity_id": "person.neo44hd", "state": "home"}]},
            {"service": "input_boolean.turn_off", "target": {"entity_id": "input_boolean.neo44hd_home"},
             "if": [{"condition": "state", "entity_id": "person.neo44hd", "state": "not_home"}]},
        ],
        "mode": "restart"
    }
    r = await s.post(f"{HASS}/api/config/automation/config/sync_presencia_update",
        json=auto, headers=HA_HEADERS, timeout=aiohttp.ClientTimeout(total=8))
    body = await r.text()
    print(f"  {'OK' if r.status in (200,201) else 'FAIL'}: HTTP {r.status}" + (f" - {body[:100]}" if r.status not in (200,201) else ""))

    # Crear scripts
    print("\n📝 Scripts HA...")
    scripts = {
        "sync_activar_cine": {
            "alias": "Activar Modo Cine",
            "sequence": [
                {"service": "input_boolean.turn_on", "target": {"entity_id": "input_boolean.movie_mode_enabled"}},
                {"service": "scene.turn_on", "data": {"entity_id": "scene.modo_cine"}},
            ]
        },
        "sync_activar_fiesta": {
            "alias": "Activar Modo Fiesta",
            "sequence": [
                {"service": "input_boolean.turn_on", "target": {"entity_id": "input_boolean.party_mode_enabled"}},
                {"service": "scene.turn_on", "data": {"entity_id": "scene.modo_fiesta"}},
            ]
        },
        "sync_activar_noche": {
            "alias": "Activar Modo Noche",
            "sequence": [
                {"service": "input_boolean.turn_on", "target": {"entity_id": "input_boolean.sync_night_mode_active"}},
                {"service": "scene.turn_on", "data": {"entity_id": "scene.modo_noche_total"}},
            ]
        },
        "sync_luces_on": {
            "alias": "Encender Todas Luces",
            "sequence": [
                {"service": "light/turn_on", "target": {"entity_id": ["light.ventana_c_luz_de_fondo","light.ventana_t_luz_de_fondo","light.vesti_garaje_luz_de_fondo","light.vesti_grout_luz_de_fondo","light.joker","light.rayo"]}, "data": {"brightness_pct": 80}},
            ]
        },
        "sync_luces_off": {
            "alias": "Apagar Todas Luces",
            "sequence": [
                {"service": "light/turn_off", "target": {"entity_id": ["light.ventana_c_luz_de_fondo","light.ventana_t_luz_de_fondo","light.vesti_garaje_luz_de_fondo","light.vesti_grout_luz_de_fondo","light.joker","light.rayo"]}},
            ]
        },
        "sync_desactivar_noche": {
            "alias": "Desactivar Modo Noche",
            "sequence": [
                {"service": "input_boolean/turn_off", "target": {"entity_id": "input_boolean.sync_night_mode_active"}},
                {"service": "input_boolean/turn_off", "target": {"entity_id": "input_boolean.sync_manual_night_mode"}},
                {"service": "light/turn_on", "target": {"entity_id": ["light.ventana_c_luz_de_fondo","light.ventana_t_luz_de_fondo"], "brightness_pct": 80}},
            ]
        },
    }
    for eid, data in scripts.items():
        r = await s.post(f"{HASS}/api/config/script/config/{eid}",
            json=data, headers=HA_HEADERS, timeout=aiohttp.ClientTimeout(total=8))
        status = "OK" if r.status in (200,201) else "FAIL"
        print(f"  {status}: {data['alias']} (HTTP {r.status})")

    # Reload
    r = await s.post(f"{HASS}/api/services/automation/reload", headers=HA_HEADERS, timeout=aiohttp.ClientTimeout(total=8))
    print(f"\n  Reload: HTTP {r.status}")

    await s.close()
    print("\nParte 1 completada")

asyncio.run(main())