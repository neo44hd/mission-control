"""Deep exploration + control test"""
import asyncio, aiohttp, json, re

HASS = "http://192.168.3.168:8123"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIwNjkwMWU5YjE5NzA0NDRlOThhNzA3MGU4MDFhODUxNCIsImlhdCI6MTc4MTQ2Nzg4MywiZXhwIjoyMDk2ODI3ODgzfQ.gP0SM8Uol3Bz09FrhU5fv5fkyP4pJmcxuTXtjm2ktqc"
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

def jprint(label, obj, limit=600):
    text = json.dumps(obj, indent=2, ensure_ascii=False)
    if len(text) > limit:
        text = text[:limit] + f"\n  ... ({len(text)} total)"
    print(f"  {label}: {text}")

async def main():
    s = aiohttp.ClientSession()

    # ============================================================
    # 1. INTENTAR CONTROL REAL - encender/apagar una luz
    # ============================================================
    print("=" * 60)
    print("TEST 1: Control real - encender luz_rayo")
    print("=" * 60)
    try:
        # Turn ON
        r = await s.post(f"{HASS}/api/services/light/turn_on", json={"entity_id": "light.rayo"}, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=8))
        body = await r.text()
        print(f"  Turn ON → HTTP {r.status}: {body[:200]}")
    except Exception as e:
        print(f"  Error: {e}")

    # ============================================================
    # 2. DEVICES - /api/device_registry
    # ============================================================
    print("\n" + "=" * 60)
    print("2. DEVICE REGISTRY")
    print("=" * 60)
    for endpoint in [
        "/device_registry",
        "/device_registry/registry",
        "/devices",
    ]:
        try:
            r = await s.get(f"{HASS}/api{endpoint}", headers=HEADERS, timeout=aiohttp.ClientTimeout(total=8))
            body = await r.text()
            if r.status == 200:
                data = json.loads(body)
                if isinstance(data, list):
                    print(f"  GET /api{endpoint}: HTTP 200 - {len(data)} devices")
                    for d in data[:15]:
                        name = d.get("name") or d.get("name_by_user") or "?"
                        mfr = d.get("manufacturer", "?")
                        model = d.get("model", "?")
                        did = d.get("id", d.get("device_id", "?"))
                        print(f"    📱 {name:30s} | {mfr:15s} | {model:20s}")
                    break
                elif isinstance(data, dict):
                    print(f"  GET /api{endpoint}: HTTP 200 - dict with keys: {list(data.keys())[:10]}")
                    jprint("data", data, limit=400)
                    break
            else:
                print(f"  GET /api{endpoint}: HTTP {r.status}")
        except Exception as e:
            print(f"  GET /api{endpoint}: Error: {e}")

    # ============================================================
    # 3. AREAS
    # ============================================================
    print("\n" + "=" * 60)
    print("3. AREAS")
    print("=" * 60)
    for endpoint in ["/areas", "/zone_registry"]:
        try:
            r = await s.get(f"{HASS}/api{endpoint}", headers=HEADERS, timeout=aiohttp.ClientTimeout(total=8))
            body = await r.text()
            print(f"  GET /api{endpoint}: HTTP {r.status}")
            if r.status == 200:
                data = json.loads(body)
                if isinstance(data, list):
                    for a in data[:10]:
                        print(f"    📍 {a.get('name', '?')} (id: {a.get('area_id', a.get('id', '?'))})")
                break
        except Exception as e:
            print(f"  Error: {e}")

    # ============================================================
    # 4. AUTOMATIZACIONES
    # ============================================================
    print("\n" + "=" * 60)
    print("4. AUTOMATIZACIONES")
    print("=" * 60)
    for ep in [
        "/config/automation/config",
        "/config/automation/raw",
        "/config/automation/config/list",
        "/automation/config",
        "/events/automation",
    ]:
        try:
            r = await s.get(f"{HASS}/api{ep}", headers=HEADERS, timeout=aiohttp.ClientTimeout(total=8))
            body = await r.text()
            if r.status == 200:
                data = json.loads(body)
                if isinstance(data, dict) and data:
                    first_key = list(data.keys())[0]
                    if "alias" in str(data.get(first_key, "")):
                        print(f"  GET /api{ep}: HTTP 200 - {len(data)} automations")
                        for aid, aconf in list(data.items())[:10]:
                            alias = aconf.get("alias", "Sin alias") if isinstance(aconf, dict) else str(aconf)[:50]
                            en = aconf.get("id", "") if isinstance(aconf, dict) else ""
                            print(f"    🤖 {alias:35s} id={en}")
                        break
                    else:
                        print(f"  GET /api{ep}: HTTP 200 - keys: {list(data.keys())[:5]}")
                elif isinstance(data, list):
                    print(f"  GET /api{ep}: HTTP 200 - list of {len(data)}")
                    if data and isinstance(data[0], dict) and "alias" in data[0]:
                        for a in data[:10]:
                            print(f"    🤖 {a.get('alias', '?')}")
                        break
        except Exception as e:
            print(f"  Error en {ep}: {e}")

    # ============================================================
    # 5. SERVICIOS
    # ============================================================
    print("\n" + "=" * 60)
    print("5. SERVICIOS")
    print("=" * 60)
    try:
        r = await s.get(f"{HASS}/api/services", headers=HEADERS, timeout=aiohttp.ClientTimeout(total=8))
        body = await r.text()
        print(f"  HTTP {r.status}")
        if r.status == 200:
            data = json.loads(body)
            if isinstance(data, dict):
                for domain, svcs in sorted(data.items()):
                    if isinstance(svcs, dict):
                        svcs_list = list(svcs.keys())
                        print(f"    {domain}: {', '.join(svcs_list[:6])}{'...' if len(svcs_list) > 6 else ''}")
            elif isinstance(data, list):
                print(f"  Got list: {json.dumps(data[:10], indent=2)[:300]}")
    except Exception as e:
        print(f"  Error: {e}")

    # ============================================================
    # 6. ENTITIES BY DOMAIN SIMMARIZED
    # ============================================================
    print("\n" + "=" * 60)
    print("6. RESUMEN DE DOMINIOS ACTIVOS")
    print("=" * 60)
    try:
        r = await s.get(f"{HASS}/api/states", headers=HEADERS, timeout=aiohttp.ClientTimeout(total=10))
        entities = json.loads(await r.text()) if r.status == 200 else []
        by_domain = {}
        for e in entities:
            dom = e["entity_id"].split(".")[0]
            if dom not in by_domain:
                by_domain[dom] = []
            fname = e.get("attributes", {}).get("friendly_name", e["entity_id"])
            state = e.get("state", "?")
            by_domain[dom].append((fname, state))

        for dom, items in sorted(by_domain.items(), key=lambda x: -len(x[1])):
            on_count = sum(1 for _, s in items if s == "on")
            off_count = sum(1 for _, s in items if s == "off")
            unavail = sum(1 for _, s in items if s in ("unavailable", "unknown"))
            print(f"  📦 {dom:20s}: total={len(items):3d}  on={on_count:2d}  off={off_count:2d}  unavailable={unavail:2d}")
    except Exception as e:
        print(f"  Error: {e}")

    # ============================================================
    # 7. INTENTAR CAMBIAR ESTADO - control real
    # ============================================================
    print("\n" + "=" * 60)
    print("7. TEST DE CONTROL - Light toggle")
    print("=" * 60)
    test_entities = [
        "light.rayo",
        "light.led_bulb_w509z2",
        "light.led_bulb_w509z2_2",
        "light.ventana_c_luz_de_fondo",
    ]
    for entity in test_entities:
        try:
            # Get current state
            r = await s.get(f"{HASS}/api/states/{entity}", headers=HEADERS, timeout=aiohttp.ClientTimeout(total=5))
            if r.status == 200:
                current = (await r.json()).get("state", "?")
                action = "turn_on" if current == "off" else "turn_off"
                # Toggle
                r2 = await s.post(f"{HASS}/api/services/light/{action}",
                    json={"entity_id": entity},
                    headers=HEADERS, timeout=aiohttp.ClientTimeout(total=5))
                if r2.status == 200:
                    print(f"  ✅ {entity}: {current} → {'on' if action == 'turn_on' else 'off'}")
                else:
                    print(f"  ❌ {entity}: failed ({r2.status})")
            else:
                print(f"  ⚠️ {entity}: HTTP {r.status}")
        except Exception as e:
            print(f"  ❌ {entity}: Error: {e}")

    # ============================================================
    # 8. COMPONENTES INSTALADOS
    # ============================================================
    print("\n" + "=" * 60)
    print("8. COMPONENTES INTEGRADOS")
    print("=" * 60)
    try:
        r = await s.get(f"{HASS}/api/config", headers=HEADERS, timeout=aiohttp.ClientTimeout(total=8))
        if r.status == 200:
            d = await r.json()
            components = d.get("components", [])
            print(f"  Total: {len(components)} componentes")
            key_components = [c for c in components if c not in [
                "config", "persistent_notification", "logbook", "history",
                "shopping_list", "sun", "zone", "group", "input_boolean", "scene",
                "script", "websocket_api", "automation", "conversation", "update",
                "event", "homeassistant_alerts", "assist_pipeline", "tts"
            ]]
            print(f"\n  🔧 Componentes principales:")
            for c in sorted(key_components):
                print(f"    - {c}")
    except Exception as e:
        print(f"  Error: {e}")

    await s.close()
    print("\n✅ Exploración completa!")

try:
    asyncio.run(main())
except Exception as e:
    import traceback
    traceback.print_exc()