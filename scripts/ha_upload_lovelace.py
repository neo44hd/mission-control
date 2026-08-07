"""Subir dashboard Lovelace JSON limpio + instalar bot Telegram como servicio"""
import asyncio, aiohttp, json

HASS = "http://192.168.3.168:8123"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIwNjkwMWU5YjE5NzA0NDRlOThhNzA3MGU4MDFhODUxNCIsImlhdCI6MTc4MTQ2Nzg4MywiZXhwIjoyMDk2ODI3ODgzfQ.gP0SM8Uol3Bz09FrhU5fv5fkyP4pJmcxuTXtjm2ktqc"
H = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

# Dashboard sin comentarios, puro JSON
DASHBOARD = {
    "title": "Casa Sync",
    "icon": "mdi:home",
    "panel": True,
    "views": [
        {
            "title": "Inicio",
            "path": "inicio",
            "icon": "mdi:home",
            "cards": [
                {"type": "custom:mushroom-title", "title": "Casa Sync", "subtitle": "Sistema domotico centralizado"},
                {
                    "type": "custom:mushroom-template-card",
                    "entity": "input_boolean.david_home",
                    "primary": "${states('input_boolean.david_home') == 'on'}",
                    "secondary": "${states('input_boolean.neo44hd_home') == 'on'}",
                    "icon": "mdi:home-account",
                    "layout": "horizontal",
                    "tap_action": {"action": "navigate", "navigation_path": "presencia"}
                },
                {
                    "type": "horizontal-stack",
                    "cards": [
                        {"type": "custom:mushroom-entity-card", "entity": "input_boolean.sync_night_mode_enabled", "name": "Modo Noche", "icon": "mdi:weather-night"},
                        {"type": "custom:mushroom-entity-card", "entity": "input_boolean.sync_bienvenida_enabled", "name": "Bienvenida", "icon": "mdi:door-open"},
                        {"type": "custom:mushroom-entity-card", "entity": "input_boolean.camera_recording_enabled", "name": "CCTV", "icon": "mdi:cctv"},
                        {"type": "custom:mushroom-entity-card", "entity": "input_boolean.auto_lighting_enabled", "name": "Luz Auto", "icon": "mdi:lightbulb-auto"},
                    ]
                },
                {"type": "custom:mushroom-title", "title": "Modos"},
                {
                    "type": "horizontal-stack",
                    "cards": [
                        {"type": "custom:mushroom-template-card", "primary": "Cine", "icon": "mdi:movie-open", "icon_color": "amber", "tap_action": {"action": "call-service", "service": "script.sync_activar_cine"}},
                        {"type": "custom:mushroom-template-card", "primary": "Fiesta", "icon": "mdi:party-popper", "icon_color": "pink", "tap_action": {"action": "call-service", "service": "script.sync_activar_fiesta"}},
                        {"type": "custom:mushroom-template-card", "primary": "Noche", "icon": "mdi:power-sleep", "icon_color": "blue", "tap_action": {"action": "call-service", "service": "script.sync_activar_noche"}},
                        {"type": "custom:mushroom-template-card", "primary": "Despertar", "icon": "mdi:white-balance-sunny", "icon_color": "orange", "tap_action": {"action": "call-service", "service": "script.sync_desactivar_noche"}},
                    ]
                },
                {"type": "custom:mushroom-title", "title": "Luces"},
                {
                    "type": "horizontal-stack",
                    "cards": [
                        {"type": "custom:mushroom-entity-card", "entity": "light.rayo", "icon": "mdi:lightning-bolt"},
                        {"type": "custom:mushroom-entity-card", "entity": "light.joker", "icon": "mdi:cards"},
                        {"type": "custom:mushroom-entity-card", "entity": "light.ventana_c_luz_de_fondo", "icon": "mdi:window-shutter"},
                        {"type": "custom:mushroom-entity-card", "entity": "light.ventana_t_luz_de_fondo", "icon": "mdi:window-shutter"},
                        {"type": "custom:mushroom-entity-card", "entity": "light.led_bulb_w509z2", "icon": "mdi:desk-lamp"},
                    ]
                },
                {"type": "custom:mushroom-title", "title": "Control"},
                {
                    "type": "horizontal-stack",
                    "cards": [
                        {"type": "custom:mushroom-entity-card", "entity": "input_number.thermostat_target", "icon": "mdi:thermometer"},
                        {"type": "custom:mushroom-entity-card", "entity": "input_number.living_room_brightness", "icon": "mdi:brightness-percent"},
                        {"type": "custom:mushroom-entity-card", "entity": "input_number.blinds_position", "icon": "mdi:window-shutter"},
                    ]
                },
                {"type": "custom:mushroom-title", "title": "Cortinas"},
                {
                    "type": "horizontal-stack",
                    "cards": [
                        {"type": "custom:mushroom-entity-card", "entity": "cover.ventana_c_cortina", "icon": "mdi:curtains"},
                        {"type": "custom:mushroom-entity-card", "entity": "cover.ventana_t_cortina", "icon": "mdi:curtains"},
                        {"type": "custom:mushroom-entity-card", "entity": "cover.vesti_garaje_cortina", "icon": "mdi:curtains-closed"},
                        {"type": "custom:mushroom-entity-card", "entity": "cover.vesti_grout_cortina", "icon": "mdi:curtains-closed"},
                    ]
                },
                {"type": "custom:mushroom-title", "title": "Seguridad"},
                {
                    "type": "horizontal-stack",
                    "cards": [
                        {"type": "custom:mushroom-entity-card", "entity": "input_boolean.security_mode_armed", "name": "Alarma", "icon": "mdi:shield-check"},
                        {"type": "custom:mushroom-entity-card", "entity": "input_boolean.doorbell_notifications", "name": "Timbre", "icon": "mdi:bell"},
                    ]
                },
                {"type": "custom:mushroom-title", "title": "Energia"},
                {
                    "type": "gauge",
                    "entity": "sensor.medidor_electrico_potencia",
                    "name": "Consumo",
                    "min": 0, "max": 3000,
                    "severity": {"green": 0, "yellow": 500, "red": 1500}
                },
                {
                    "type": "horizontal-stack",
                    "cards": [
                        {"type": "sensor", "entity": "sensor.temperature", "icon": "mdi:thermometer"},
                        {"type": "sensor", "entity": "sensor.humidity", "icon": "mdi:water-percent"},
                    ]
                },
                {"type": "custom:mushroom-title", "title": "Enchufes"},
                {
                    "type": "grid",
                    "columns": 4,
                    "square": False,
                    "cards": [
                        {"type": "custom:mushroom-entity-card", "entity": "switch.luz_pica_interruptor_1", "icon": "mdi:light-switch"},
                        {"type": "custom:mushroom-entity-card", "entity": "switch.usb_wind_enchufe_1", "icon": "mdi:power-socket-eu"},
                        {"type": "custom:mushroom-entity-card", "entity": "switch.usb_wind_enchufe_2", "icon": "mdi:power-socket-eu"},
                        {"type": "custom:mushroom-entity-card", "entity": "switch.cocina_interruptor_1", "icon": "mdi:light-switch"},
                        {"type": "custom:mushroom-entity-card", "entity": "switch.luz_batcueva_interruptor_1", "icon": "mdi:light-switch"},
                        {"type": "custom:mushroom-entity-card", "entity": "switch.cheester_sock_enchufe_1", "icon": "mdi:power-socket-eu"},
                        {"type": "custom:mushroom-entity-card", "entity": "switch.chicken_sock_enchufe_1", "icon": "mdi:power-socket-eu"},
                        {"type": "custom:mushroom-entity-card", "entity": "switch.timbro_hack_grabacion_de_video", "icon": "mdi:video"},
                    ]
                },
                {"type": "custom:mushroom-title", "title": "Camaras"},
                {
                    "type": "horizontal-stack",
                    "cards": [
                        {"type": "picture-entity", "entity": "camera.timbro_hack", "camera_image": "camera.timbro_hack", "camera_view": "live"},
                        {"type": "picture-entity", "entity": "camera.el_ojo", "camera_view": "live"},
                    ]
                },
                {"type": "custom:mushroom-title", "title": "Telegram"},
                {"type": "markdown", "content": "Escribe al bot de Telegram para controlar la casa. Usa /help para ver comandos."},
            ]
        }
    ]
}

async def main():
    s = aiohttp.ClientSession()

    # Intentar PUT (actualizar)
    print("Subiendo dashboard Lovelace...")
    for method_name, method in [("PUT", s.put), ("POST", s.post)]:
        try:
            r = await method(f"{HASS}/api/lovelace/lovelace",
                json=DASHBOARD, headers=H, timeout=aiohttp.ClientTimeout(total=10))
            if r.status in (200, 201):
                print(f"  OK via {method_name}: Dashboard actualizado")
                await s.close()
                return
            else:
                body = await r.text()
                print(f"  {method_name} HTTP {r.status}: {body[:200]}")
        except Exception as ex:
            print(f"  {method_name} error: {ex}")

    # Fallback: guardar local para File Editor
    with open("/Users/davidnows/scripts/dashboard.json", "w") as f:
        json.dump(DASHBOARD, f, indent=2, ensure_ascii=False)
    print("  Dashboard guardado localmente en dashboard.json")

    await s.close()

asyncio.run(main())