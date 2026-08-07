"""Exploración completa de Home Assistant con token"""
import asyncio, aiohttp, json, sys

HASS = "http://192.168.3.168:8123"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIwNjkwMWU5YjE5NzA0NDRlOThhNzA3MGU4MDFhODUxNCIsImlhdCI6MTc4MTQ2Nzg4MywiZXhwIjoyMDk2ODI3ODgzfQ.gP0SM8Uol3Bz09FrhU5fv5fkyP4pJmcxuTXtjm2ktqc"

HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

def jprint(label, obj, limit=800):
    text = json.dumps(obj, indent=2, ensure_ascii=False)
    if len(text) > limit:
        text = text[:limit] + f"\n  ... ({len(text)} bytes total)"
    print(f"  {label}: {text}")

async def main():
    s = aiohttp.ClientSession()

    # ============================================================
    # 1. CONFIGURACIÓN GENERAL
    # ============================================================
    print("=" * 60)
    print("1. CONFIGURACIÓN GENERAL")
    print("=" * 60)
    try:
        async with s.get(f"{HASS}/api/config", headers=HEADERS, timeout=aiohttp.ClientTimeout(total=8)) as r:
            body = await r.text()
            print(f"  HTTP {r.status}")
            if r.status == 200:
                d = json.loads(body)
                jprint("config", d)
            else:
                print(f"  Body: {body[:300]}")
    except Exception as e:
        print(f"  Error: {e}")

    # ============================================================
    # 2. ESTADO DE TODAS LAS ENTIDADES
    # ============================================================
    print("\n" + "=" * 60)
    print("2. ENTIDADES (states)")
    print("=" * 60)
    domains = {}
    entities_detail = []
    try:
        async with s.get(f"{HASS}/api/states", headers=HEADERS, timeout=aiohttp.ClientTimeout(total=10)) as r:
            body = await r.text()
            print(f"  HTTP {r.status}")
            if r.status == 200:
                entities = json.loads(body)
                print(f"  Total entidades: {len(entities)}")
                for e in entities:
                    domain = e["entity_id"].split(".")[0]
                    domains[domain] = domains.get(domain, 0) + 1
                    attrs = e.get("attributes", {})
                    friendly = attrs.get("friendly_name", e["entity_id"])
                    state = e.get("state", "?")
                    entities_detail.append((e["entity_id"], friendly, state, domain, attrs))

                print(f"\n  Entidades por dominio:")
                for d, c in sorted(domains.items(), key=lambda x: -x[1]):
                    print(f"    📌 {d}: {c}")

                print(f"\n  Detalle de entidades:")
                for eid, fname, st, dom, attrs in sorted(entities_detail):
                    unit = attrs.get("unit_of_measurement", "")
                    dev = attrs.get("device_class", "")
                    extra = f"[{unit}]" if unit else ""
                    extra += f" ({dev})" if dev else ""
                    icon = "🟢" if st == "on" else "🔴" if st == "off" else "🟡"
                    print(f"    {icon} {eid:50s} = {str(st):10s} {extra}  ({fname})")

    except Exception as e:
        print(f"  Error: {e}")
        import traceback
        traceback.print_exc()

    # ============================================================
    # 3. DISPOSITIVOS
    # ============================================================
    print("\n" + "=" * 60)
    print("3. DISPOSITIVOS (devices)")
    print("=" * 60)
    try:
        async with s.get(f"{HASS}/api/devices", headers=HEADERS, timeout=aiohttp.ClientTimeout(total=8)) as r:
            body = await r.text()
            print(f"  HTTP {r.status}")
            if r.status == 200:
                devices = json.loads(body)
                print(f"  Total dispositivos: {len(devices)}")
                for d in devices:
                    name = d.get("name", d.get("name_by_user", "?"))
                    model = d.get("model", "?")
                    mfr = d.get("manufacturer", "?")
                    did = d.get("id", "?")
                    via = d.get("via_device_id", None)
                    print(f"    📱 {name:30s} | {mfr:15s} | {model:20s} | id={did}")
                    if via:
                        print(f"       (via device: {via})")
    except Exception as e:
        print(f"  Error: {e}")

    # ============================================================
    # 4. ÁREAS
    # ============================================================
    print("\n" + "=" * 60)
    print("4. ÁREAS")
    print("=" * 60)
    try:
        async with s.get(f"{HASS}/api/areas", headers=HEADERS, timeout=aiohttp.ClientTimeout(total=8)) as r:
            body = await r.text()
            print(f"  HTTP {r.status}")
            if r.status == 200:
                areas = json.loads(body)
                print(f"  Total áreas: {len(areas)}")
                for a in areas:
                    name = a.get("name", "Sin nombre")
                    aid = a.get("area_id", "?")
                    print(f"    📍 {name:30s} (id: {aid})")
    except Exception as e:
        print(f"  Error: {e}")

    # ============================================================
    # 5. AUTOMATIZACIONES EXISTENTES
    # ============================================================
    print("\n" + "=" * 60)
    print("5. AUTOMATIZACIONES")
    print("=" * 60)
    try:
        async with s.get(f"{HASS}/api/config/automation/config", headers=HEADERS, timeout=aiohttp.ClientTimeout(total=8)) as r:
            body = await r.text()
            print(f"  HTTP {r.status}")
            if r.status == 200:
                automations = json.loads(body)
                print(f"  Total automatizaciones: {len(automations)}")
                for a in automations:
                    alias = a.get("alias", "Sin alias")
                    aid = a.get("id", "?")
                    enabled = a.get("enabled", "?")
                    print(f"    🤖 {alias:40s} (id: {aid}, enabled: {enabled})")
    except Exception as e:
        print(f"  Error: {e}")

    # ============================================================
    # 6. SCRIPTS EXISTENTES
    # ============================================================
    print("\n" + "=" * 60)
    print("6. SCRIPTS")
    print("=" * 60)
    try:
        async with s.get(f"{HASS}/api/services/script", headers=HEADERS, timeout=aiohttp.ClientTimeout(total=8)) as r:
            body = await r.text()
            print(f"  HTTP {r.status}")
            if r.status == 200:
                scripts = json.loads(body)
                for svc, info in scripts.items():
                    print(f"    📜 {svc}: {json.dumps(info, indent=4)[:200]}")
    except Exception as e:
        print(f"  Error: {e}")

    # ============================================================
    # 7. SERVICIOS DISPONIBLES
    # ============================================================
    print("\n" + "=" * 60)
    print("7. SERVICIOS")
    print("=" * 60)
    try:
        async with s.get(f"{HASS}/api/services", headers=HEADERS, timeout=aiohttp.ClientTimeout(total=8)) as r:
            body = await r.text()
            print(f"  HTTP {r.status}")
            if r.status == 200:
                services = json.loads(body)
                for domain, svc_list in sorted(services.items()):
                    svcs = list(svc_list.keys())
                    print(f"    📦 {domain}: {', '.join(svcs[:5])}{'...' if len(svcs) > 5 else ''}")
    except Exception as e:
        print(f"  Error: {e}")

    # ============================================================
    # 8. INFO DE HARDWARE
    # ============================================================
    print("\n" + "=" * 60)
    print("8. HARDWARE & INFO DEL SISTEMA")
    print("=" * 60)
    try:
        async with s.get(f"{HASS}/api/hardware", headers=HEADERS, timeout=aiohttp.ClientTimeout(total=8)) as r:
            body = await r.text()
            print(f"  HTTP {r.status}")
            if r.status == 200:
                hw = json.loads(body)
                for h in hw:
                    print(f"    🖥️ {h.get('board', '?')}: {h.get('name', '?')} ({h.get('uuid', '?')[:12]})")
                    for app in h.get("usb_by_port", {}) or {}:
                        print(f"       USB {app}")

        async with s.get(f"{HASS}/api/history/period?filter_entity_id=zone.home&significant_changes_only=1&minimal_response=1", headers=HEADERS, timeout=aiohttp.ClientTimeout(total=5)) as rz:
            pass

    except Exception as e:
        print(f"  Error: {e}")

    await s.close()
    print("\n✅ Exploración completa!")

try:
    asyncio.run(main())
except Exception as e:
    import traceback
    traceback.print_exc()