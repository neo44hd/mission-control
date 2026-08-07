"""Exploración completa: automations, estados, endpoints disponibles"""
import asyncio, aiohttp, json

HASS = "http://192.168.3.168:8123"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIwNjkwMWU5YjE5NzA0NDRlOThhNzA3MGU4MDFhODUxNCIsImlhdCI6MTc4MTQ2Nzg4MywiZXhwIjoyMDk2ODI3ODgzfQ.gP0SM8Uol3Bz09FrhU5fv5fkyP4pJmcxuTXtjm2ktqc"
H = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

async def main():
    s = aiohttp.ClientSession()

    # 1. Listar todos los endpoints API disponibles
    print("=" * 60)
    print("1. ENDPOINTS API DISPONIBLES")
    print("=" * 60)
    endpoints = [
        "/", "/config", "/states", "/services",
        "/event/types", "/states/entity_id/sensor.temperature_temperatura",
        "/logbook/sensor.temperature_temperatura",
        "/history/period/sensor.temperature_temperatura",
        "/entity_id", "/events", "/areas",
        "/device_registry", "/devices",
        "/config/automation/config", "/config/automation/raw",
        "/config/scene", "/config/script",
        "/config/entry-registry", "/config/areas",
        "/hardware", "/person",
        "/frontend/panels", "/frontend/themes",
        "/stt/providers", "/intent",
        "/recorded_phrases", "/repairs",
        "/backups/info", "/backups/new",
        "/auth/mfa_modules", "/auth/current_user",
        "/system_health",
    ]
    for ep in endpoints:
        try:
            r = await s.get(f"{HASS}/api{ep}", headers=H, timeout=aiohttp.ClientTimeout(total=5))
            body = await r.text()
            try:
                data = json.loads(body)
                if isinstance(data, dict):
                    info = f"dict({len(data)} keys)"
                elif isinstance(data, list):
                    info = f"list({len(data)} items)"
                else:
                    info = f"str({len(data)} chars)"
            except:
                info = f"text({len(body)} chars)"
            print(f"  {'✅' if r.status == 200 else '❌'} GET /api{ep:45s} → HTTP {r.status} ({info})")
        except Exception as e:
            print(f"  ❌ GET /api{ep:45s} → Error: {e}")

    # 2. Automations - intentar múltiples formatos
    print("\n" + "=" * 60)
    print("2. AUTOMATIZACIONES (todos los formatos)")
    print("=" * 60)
    auto_endpoints = [
        "/config/automation/config",
        "/config/automation/raw",
        "/config/automation/raw/list",
    ]
    for ep in auto_endpoints:
        try:
            r = await s.get(f"{HASS}/api{ep}", headers=H, timeout=aiohttp.ClientTimeout(total=8))
            body = await r.text()
            print(f"\n  GET /api{ep}: HTTP {r.status} ({len(body)} bytes)")
            if r.status == 200:
                try:
                    data = json.loads(body)
                    if isinstance(data, dict):
                        for k, v in list(data.items())[:10]:
                            alias = v.get("alias", "n/a") if isinstance(v, dict) else str(v)[:60]
                            print(f"    id={k}: {alias}")
                    elif isinstance(data, list):
                        for item in data[:10]:
                            print(f"    - {json.dumps(item, indent=2)[:150]}")
                except:
                    print(f"    Raw: {body[:300]}")
        except Exception as e:
            print(f"    Error: {e}")

    # 3. YAML raw de automatizaciones
    try:
        r = await s.get(f"{HASS}/api/config/automation/raw", headers=H, timeout=aiohttp.ClientTimeout(total=8))
        if r.status == 200:
            print(f"\n  📜 RAW YAML AUTOMATIONS:\n")
            print(await r.text())
    except:
        pass

    # 4. Escenas
    print("\n" + "=" * 60)
    print("3. ESCENAS (scenes)")
    print("=" * 60)
    try:
        r = await s.get(f"{HASS}/api/config/scene/config", headers=H, timeout=aiohttp.ClientTimeout(total=8))
        body = await r.text()
        print(f"  HTTP {r.status} ({len(body)} bytes)")
        if r.status == 200:
            data = json.loads(body)
            if isinstance(data, dict):
                for k, v in list(data.items())[:15]:
                    alias = v.get("name", v.get("alias", k)) if isinstance(v, dict) else str(v)[:50]
                    print(f"    🎭 {alias}")
    except Exception as e:
        print(f"  Error: {e}")

    # 5. Scripts
    print("\n" + "=" * 60)
    print("4. SCRIPTS")
    print("=" * 60)
    try:
        r = await s.get(f"{HASS}/api/config/script/config", headers=H, timeout=aiohttp.ClientTimeout(total=8))
        body = await r.text()
        print(f"  HTTP {r.status} ({len(body)} bytes)")
        if r.status == 200:
            data = json.loads(body)
            if isinstance(data, dict):
                for k, v in list(data.items())[:15]:
                    alias = v.get("name", v.get("alias", k)) if isinstance(v, dict) else str(v)[:50]
                    print(f"    📜 {alias}")
    except Exception as e:
        print(f"  Error: {e}")

    # 6. Estados ON de interés (luces, switches, covers)
    print("\n" + "=" * 60)
    print("5. ESTADO ACTUAL - Dispositivos ON")
    print("=" * 60)
    try:
        r = await s.get(f"{HASS}/api/states", headers=H, timeout=aiohttp.ClientTimeout(total=10))
        entities = json.loads(await r.text())
        print(f"\n  💡 LUCES ON:")
        for e in entities:
            if e["entity_id"].startswith("light.") and e["state"] == "on":
                attr = e.get("attributes", {})
                fname = attr.get("friendly_name", e["entity_id"])
                bri = attr.get("brightness", "?")
                col = attr.get("rgb_color", attr.get("color_temp", "?"))
                print(f"    ✅ {fname:35s} br={bri} col={col}")

        print(f"\n  🔘 SWITCHES ON:")
        for e in entities:
            if e["entity_id"].startswith("switch.") and e["state"] == "on":
                attr = e.get("attributes", {})
                fname = attr.get("friendly_name", e["entity_id"])
                print(f"    ✅ {fname}")

        print(f"\n  🪟 COVERS:")
        for e in entities:
            if e["entity_id"].startswith("cover.") and e["state"] != "unavailable":
                attr = e.get("attributes", {})
                fname = attr.get("friendly_name", e["entity_id"])
                pos = attr.get("current_position", "?")
                print(f"    {e['state']:6s} {fname:30s} pos={pos}")

        print(f"\n  🌡️  CLIMATE:")
        for e in entities:
            if e["entity_id"].startswith("climate.") and e["state"] != "unavailable":
                attr = e.get("attributes", {})
                fname = attr.get("friendly_name", e["entity_id"])
                temp = attr.get("temperature", "?")
                mode = attr.get("hvac_mode", "?")
                print(f"    {e['state']:6s} {fname:30s} temp={temp} mode={mode}")

        print(f"\n  🔌 APARATOS (media_player):")
        for e in entities:
            if e["entity_id"].startswith("media_player.") and e["state"] != "unavailable":
                attr = e.get("attributes", {})
                fname = attr.get("friendly_name", e["entity_id"])
                vol = attr.get("volume_level", "?")
                src = attr.get("source", "?")
                print(f"    {e['state']:6s} {fname:25s} vol={vol} src={src}")

        print(f"\n  📷 CÁMARAS:")
        for e in entities:
            if e["entity_id"].startswith("camera.") and e["state"] != "unavailable":
                attr = e.get("attributes", {})
                fname = attr.get("friendly_name", e["entity_id"])
                print(f"    {e['state']:6s} {fname}")

        print(f"\n  🚪 SENSORES PUERTA/VENTANA:")
        for e in entities:
            fid = e.get("attributes", {}).get("friendly_name", "")
            if any(kw in fid.lower() for kw in ["puerta", "ventana", "door", "window"]):
                if e["state"] in ("on", "off", "open", "closed"):
                    print(f"    {e['state']:6s} {fid}")

    except Exception as e:
        print(f"  Error: {e}")
        import traceback
        traceback.print_exc()

    await s.close()

try:
    asyncio.run(main())
except Exception as e:
    import traceback
    traceback.print_exc()