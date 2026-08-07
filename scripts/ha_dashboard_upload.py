"""Configurar HA storage mode + subir dashboard + crear servicio bot Telegram"""
import asyncio, aiohttp, json, subprocess

HASS = "http://192.168.3.168:8123"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIwNjkwMWU5YjE5NzA0NDRlOThhNzA3MGU4MDFhODUxNCIsImlhdCI6MTc4MTQ2Nzg4MywiZXhwIjoyMDk2ODI3ODgzfQ.gP0SM8Uol3Bz09FrhU5fv5fkyP4pJmcxuTXtjm2ktqc"
H = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

async def main():
    s = aiohttp.ClientSession()

    # 1. Verificar/configurar modo storage para Lovelace
    print("1. Checkeando modo Lovelace...")
    try:
        r = await s.get(f"{HASS}/api/config", headers=H, timeout=aiohttp.ClientTimeout(total=8))
        cfg = json.loads(await r.text())
        lovelace_mode = cfg.get("lovelace_mode", "yaml")
        print(f"   Modo actual: {lovelace_mode}")

        if lovelace_mode == "yaml":
            # Intentar cambiar a storage mode
            print("   Configurando storage mode...")
            r2 = await s.post(f"{HASS}/api/config",
                json={"lovelace_mode": "storage"},
                headers=H, timeout=aiohttp.ClientTimeout(total=8))
            if r2.status in (200, 201, 400):
                body2 = await r2.text()
                print(f"   Cambio storage: HTTP {r2.status} - {body2[:100]}")
                print("   Reinicia HA para aplicar cambio, o continuamos con YAML directo")
            else:
                print(f"   No se pudo cambiar: HTTP {r2.status}")
    except Exception as ex:
        print(f"   Error: {ex}")

    # 2. Intentar upload via API storage
    print("\n2. Subiendo dashboard via API...")
    dashboard = {
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
                        "layout": "horizontal"
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
                            {"type": "custom:mushroom-template-card", "primary": "Cine", "icon": "mdi:movie-open", "icon_color": "amber",
                             "tap_action": {"action": "call-service", "service": "script.sync_activar_cine"}},
                            {"type": "custom:mushroom-template-card", "primary": "Fiesta", "icon": "mdi:party-popper", "icon_color": "pink",
                             "tap_action": {"action": "call-service", "service": "script.sync_activar_fiesta"}},
                            {"type": "custom:mushroom-template-card", "primary": "Noche", "icon": "mdi:power-sleep", "icon_color": "blue",
                             "tap_action": {"action": "call-service", "service": "script.sync_activar_noche"}},
                            {"type": "custom:mushroom-template-card", "primary": "Despertar", "icon": "mdi:white-balance-sunny", "icon_color": "orange",
                             "tap_action": {"action": "call-service", "service": "script.sync_desactivar_noche"}},
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
                        "columns": 4, "square": False,
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
                ]
            },
            {
                "title": "Presencia",
                "path": "presencia",
                "icon": "mdi:account-group",
                "cards": [
                    {"type": "custom:mushroom-title", "title": "Presencia"},
                    {"type": "entity", "entity": "person.david_nows"},
                    {"type": "entity", "entity": "person.neo44hd"},
                    {"type": "custom:mushroom-template-card", "primary": "David", "secondary": "${states('input_boolean.david_home')}", "icon": "mdi:account"},
                    {"type": "custom:mushroom-template-card", "primary": "Neo44hd", "secondary": "${states('input_boolean.neo44hd_home')}", "icon": "mdi:account"},
                ]
            },
            {
                "title": "Telegram",
                "path": "telegram",
                "icon": "mdi:telegram",
                "cards": [
                    {"type": "custom:mushroom-title", "title": "Control por Telegram"},
                    {"type": "markdown", "content": "**Escribe al bot de Telegram** para controlar la casa.\n\n**Comandos:**\n/cine - Modo cine\n/fiesta - Modo fiesta\n/noche - Modo noche\n/despertar - Desactivar noche\n/luzon - Todas las luces on\n/luzoff - Todas las luces off\n/cortinas - Max abrir\n/cortinasc - Max cerrar\n/home - Estado casa\n/seguridad - Toggle alarma\n/clima - Temperatura\n/energia - Consumo\n/help - Ayuda"},
                ]
            },
        ]
    }

    # Intentar PUT primero, luego POST
    try:
        r = await s.put(f"{HASS}/api/lovelace/lovelace",
            json=dashboard, headers=H, timeout=aiohttp.ClientTimeout(total=10))
        if r.status in (200, 201):
            print("   OK: Dashboard subido via PUT")
        else:
            r2 = await s.post(f"{HASS}/api/lovelace/lovelace",
                json=dashboard, headers=H, timeout=aiohttp.ClientTimeout(total=10))
            if r2.status in (200, 201):
                print("   OK: Dashboard creado via POST")
            else:
                print(f"   PUT:{r.status} POST:{r2.status}")
                await save_yaml_fallback(dashboard)
    except Exception as ex:
        print(f"   Error API: {ex}")
        await save_yaml_fallback(dashboard)

    await s.close()

def save_yaml_fallback(dashboard):
    """Si la API falla, guardar YAML para File Editor"""
    lines = ["title: Casa Sync", "icon: mdi:home", "panel: true", "views:"]
    for idx, view in enumerate(dashboard["views"]):
        lines.append(f'  - title: "{view["title"]}"')
        lines.append(f'    path: "{view["path"]}"')
        lines.append(f'    icon: "{view["icon"]}"')
        lines.append("    cards:")
        # Simplified - cards need full YAML serialization
        lines.append("      # Dashboard generado automaticamente")
    with open("/Users/davidnows/scripts/ui-lovelace.yaml", "w") as f:
        f.write("\n".join(lines))
    print("   Dashboard guardado en ui-lovelace.yaml (usar File Editor)")

asyncio.run(main())