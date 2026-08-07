"""Conexion OAuth2 a Home Assistant - con form-urlencoded"""
import asyncio, aiohttp, json, re, sys

HASS = "http://192.168.3.168:8123"
USER = "davidnows"
PASS = "251101"
CLIENT_ID = "http://home-assistant.io/clients/android_app"

async def main():
    s = aiohttp.ClientSession()

    # ============================================================
    # PASO 1: GET /auth/authorize - obtener cookies y flow_id
    # ============================================================
    print("[1/4] GET /auth/authorize → obtener cookies y flow_id ...")

    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": "http://home-assistant.io/auth-callback/",
        "response_type": "code",
        "scope": "local",
        "state": "cli_state_001"
    }

    async with s.get(f"{HASS}/auth/authorize", params=params, allow_redirects=False) as r1:
        html = await r1.text()
        print(f"  HTTP {r1.status}")

        cookies = s.cookie_jar
        print(f"  Cookies: {len(cookies)}")
        for c in cookies:
            print(f"    - {c.key}={c.value[:40]}")

        # Extraer flow_id del HTML
        fm = re.findall(r'["\']flow_id["\']\s*[:=]\s*["\']([a-f0-9-]+)["\']', html)
        if fm:
            print(f"  ✅ flow_id encontrado: {fm}")

        # Extraer todos los scripts inline
        scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
        for i, sc in enumerate(scripts):
            if 'fetch(' in sc or 'window.location' in sc or 'oauth' in sc.lower() or 'login' in sc.lower():
                print(f"  Script {i} ({len(sc)} bytes): {sc[:200]}...")

        # Buscar cualquier URL POST en el HTML
        post_urls = re.findall(r'action="([^"]*)"', html)
        if post_urls:
            print(f"  Form actions: {post_urls}")

    # ============================================================
    # PASO 2: POST /auth/authorize con form-urlencoded
    # ============================================================
    print("\n[2/4] POST /auth/authorize → enviar credenciales (form-urlencoded) ...")

    form_data = aiohttp.FormData()
    form_data.add_field("username", USER)
    form_data.add_field("password", PASS)

    try:
        async with s.post(f"{HASS}/auth/authorize", data=form_data, allow_redirects=False, timeout=aiohttp.ClientTimeout(total=10)) as r2:
            loc2 = r2.headers.get("Location", "")
            body2 = await r2.text()
            print(f"  HTTP {r2.status}")
            print(f"  Location: {loc2[:300] if loc2 else '(none)'}")
            if body2:
                print(f"  Body: {body2[:300]}")
            if "code=" in loc2:
                code_match = re.findall(r"code=([^&]+)", loc2)
                if code_match:
                    code = code_match[0]
                    print(f"\n  🎯 AUTH CODE: {code}")

                    # Intercambiar por token
                    print("\n[3/4] POST /auth/token → intercambiar code por token ...")
                    token_data = {
                        "grant_type": "authorization_code",
                        "code": code,
                        "redirect_uri": "http://home-assistant.io/auth-callback/",
                        "client_id": CLIENT_ID
                    }
                    async with s.post(f"{HASS}/auth/token", json=token_data, timeout=aiohttp.ClientTimeout(total=8)) as rt:
                        tbody = await rt.text()
                        print(f"  HTTP {rt.status}: {tbody[:500]}")
                        if rt.status == 200:
                            td = json.loads(tbody)
                            access_token = td.get("access_token", "")
                            print(f"\n{'='*60}")
                            print(f"✅ ACCESS TOKEN: {access_token}")
                            print(f"{'='*60}")
                            await s.close()
                            return access_token
    except Exception as e:
        import traceback
        traceback.print_exc()

    # Si falla, intentar con el flow login_flow
    print("\n[2b/4] Alternativa: POST /auth/login_flow (JSON) ...")
    payload = {
        "client_id": CLIENT_ID,
        "handler": ["homeassistant", "null"],
        "username": USER,
        "password": PASS
    }
    try:
        async with s.post(f"{HASS}/auth/login_flow", json=payload, timeout=aiohttp.ClientTimeout(total=8)) as r3:
            body3 = await r3.text()
            print(f"  HTTP {r3.status}: {body3[:500]}")
    except Exception as e:
        print(f"  Error: {e}")

    # ============================================================
    # PASO 4: intentar con password legacy
    # ============================================================
    print("\n[4/4] Intentando /auth/token con password grant ...")
    pw_payload = {
        "grant_type": "password",
        "username": USER,
        "password": PASS,
        "client_type": "app",
        "client_id": CLIENT_ID
    }
    try:
        async with s.post(f"{HASS}/auth/token", json=pw_payload, timeout=aiohttp.ClientTimeout(total=8)) as rp:
            pbody = await rp.text()
            print(f"  HTTP {rp.status}: {pbody[:300]}")
            if rp.status == 200:
                pdata = json.loads(pbody)
                print(f"\n✅ ACCESS TOKEN: {pdata.get('access_token')}")
                await s.close()
                return pdata.get("access_token")
    except Exception as e:
        print(f"  Error: {e}")

    await s.close()
    print("\n❌ No se pudo autenticar automáticamente.")
    print("""
Soluciones manuales:
1. Entra a http://192.168.3.168:8123 desde un navegador
2. Logueate con user: davidnows / pass: 251101
3. Ve a Configuración → Cuenta → Tokens de acceso de larga duración
4. Crea uno y compártemelo aquí
""")

try:
    asyncio.run(main())
except Exception as e:
    import traceback
    traceback.print_exc()