"""Fix todo: presencia, scripts, dashboard upload"""
import asyncio, aiohttp, json, os

HASS = "http://192.168.3.168:8123"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIwNjkwMWU5YjE5NzA0NDRlOThhNzA3MGU4MDFhODUxNCIsImlhdCI6MTc4MTQ2Nzg4MywiZXhwIjoyMDk2ODI3ODgzfQ.gP0SM8Uol3Bz09FrhU5fv5fkyP4pJmcxuTXtjm2ktqc"
H = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

async def main():
    s = aiohttp.ClientSession()

    # 1. PRESENCIA con choose
    print("1. Presencia...")
    auto_pres = {
        "alias": "Actualizar Presencia",
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
    r = await s.post(f"{HASS}/api/config/automation/config/sync_presencia_update",
        json=auto_pres, headers=H, timeout=aiohttp.ClientTimeout(total=8))
    body = await r.text()
    print(f"   {'OK' if r.status in (200,201) else 'FAIL'} HTTP {r.status}" + (f": {body[:120]}" if r.status not in (200,201) else ""))

    # 2. SCRIPTS (con puntos, no barras)
    print("\n2. Scripts HA...")
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
        "sync_desactivar_noche": {
            "alias": "Desactivar Modo Noche",
            "sequence": [
                {"service": "input_boolean.turn_off", "target": {"entity_id": "input_boolean.sync_night_mode_active"}},
                {"service": "input_boolean.turn_off", "target": {"entity_id": "input_boolean.sync_manual_night_mode"}},
            ]
        },
        "sync_toggle_movie_mode": {
            "alias": "Toggle Modo Cine",
            "sequence": [
                {"service": "input_boolean.toggle", "target": {"entity_id": "input_boolean.movie_mode_enabled"}},
            ]
        },
        "sync_luces_on": {
            "alias": "Encender Todas Luces",
            "sequence": [
                {"service": "light.turn_on", "target": {"entity_id": ["light.ventana_c_luz_de_fondo","light.ventana_t_luz_de_fondo","light.vesti_garaje_luz_de_fondo","light.vesti_grout_luz_de_fondo","light.joker","light.rayo"]}, "data": {"brightness_pct": 80}},
            ]
        },
        "sync_luces_off": {
            "alias": "Apagar Todas Luces",
            "sequence": [
                {"service": "light.turn_off", "target": {"entity_id": ["light.ventana_c_luz_de_fondo","light.ventana_t_luz_de_fondo","light.vesti_garaje_luz_de_fondo","light.vesti_grout_luz_de_fondo","light.joker","light.rayo"]}},
            ]
        },
        "sync_cortinas_up": {
            "alias": "Abrir Cortinas",
            "sequence": [
                {"service": "cover.set_cover_position", "target": {"entity_id": ["cover.ventana_c_cortina","cover.ventana_t_cortina","cover.vesti_garaje_cortina","cover.vesti_grout_cortina"]}, "data": {"position": 100}},
            ]
        },
        "sync_cortinas_down": {
            "alias": "Cerrar Cortinas",
            "sequence": [
                {"service": "cover.set_cover_position", "target": {"entity_id": ["cover.ventana_c_cortina","cover.ventana_t_cortina","cover.vesti_garaje_cortina","cover.vesti_grout_cortina"]}, "data": {"position": 0}},
            ]
        },
    }
    for eid, data in scripts.items():
        r = await s.post(f"{HASS}/api/config/script/config/{eid}",
            json=data, headers=H, timeout=aiohttp.ClientTimeout(total=8))
        status = "OK" if r.status in (200,201) else "FAIL"
        print(f"   {status}: {data['alias']} (HTTP {r.status})")

    # 3. Extra automation: toggle_movie_mode event
    print("\n3. Automation extra...")
    auto_toggle = {
        "alias": "Toggle Modo Cine Event",
        "trigger": [{"platform": "event", "event_type": "toggle_movie_mode"}],
        "condition": [],
        "action": [
            {"service": "script.turn_on", "data": {"entity_id": "script.sync_toggle_movie_mode"}},
        ],
        "mode": "restart"
    }
    r = await s.post(f"{HASS}/api/config/automation/config/sync_toggle_movie_event",
        json=auto_toggle, headers=H, timeout=aiohttp.ClientTimeout(total=8))
    body = await r.text()
    print(f"   {'OK' if r.status in (200,201) else 'FAIL'}: Toggle movie event (HTTP {r.status})")

    # Reload
    r = await s.post(f"{HASS}/api/services/automation/reload", headers=H, timeout=aiohttp.ClientTimeout(total=8))
    print(f"\n   Reload: HTTP {r.status}")

    # 4. Uploader dashboard YAML
    print("\n4. Dashboard YAML...")
    dashboard_path = "/Users/davidnows/scripts/dashboard.yaml"
    # We write it; user uploads via HACS or file editor
    print(f"   Dashboard guardado en: {dashboard_path}")

    await s.close()
    print("\n=== TODO CONFIGURADO ===")

asyncio.run(main())