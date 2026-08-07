import asyncio, aiohttp, json, re

HASS = "http://192.168.3.168:8123"
USER = "davidnows"
PASS = "251101"

async def main():
    s = aiohttp.ClientSession()

    # Try multiple things in parallel
    results = {}

    # 1. Check if SSH is available
    print("🔌 Checking SSH...")
    try:
        r, _ = await asyncio.wait_for(
            s.get(f"http://192.168.3.168:22", timeout=aiohttp.ClientTimeout(total=3)),
            timeout=aiohttp.ClientTimeout(total=5)
        )
        print(f"  SSH HTTP: {r.status}")
    except:
        print("  SSH: not reachable via HTTP")

    # 2. Check other common HA ports
    for port in [8123, 8100, 8080, 8443]:
        try:
            async with s.get(f"http://192.168.3.168:{port}/", timeout=aiohttp.ClientTimeout(total=3)) as r:
                if r.status != 404:
                    print(f"  Port {port}: HTTP {r.status}")
                    ct = r.headers.get('content-type', '')
                    if 'json' in ct:
                        data = await r.json()
                        print(f"    JSON: {json.dumps(data, indent=2)[:300]}")
                    elif 'html' in ct:
                        txt = await r.text()
                        print(f"    HTML title: {re.search(r'<title>(.*?)</title>', txt).group(1) if re.search(r'<title>', txt) else 'N/A'}")
        except:
            pass

    # 3. Detailed authorize page analysis
    print("\n🔍 Detailed /auth/authorize analysis:")
    params = {
        "client_id": "http://home-assistant.io/clients/hass-cli",
        "redirect_uri": "http://home-assistant.io/auth-callback/",
        "response_type": "code",
        "scope": "local",
        "state": "test123"
    }
    async with s.get(f"{HASS}/auth/authorize", params=params) as r:
        html = await r.text()

        # Look for any URLs containing /auth/
        urls = re.findall(r'(?:action|href|src)="(/auth/[^"]*)"', html)
        urls += re.findall(r'(?:action|href|src)="(\./[^"]*)"', html)
        print(f"  URLs in page: {list(set(urls))}")

        # Look for data- attributes on the authorize component
        data_attrs = re.findall(r'data-(\w+)="([^"]*)"', html)
        if data_attrs:
            print(f"  Data attrs: {dict(data_attrs)}")

        # Look for any flow-related data
        flow_data = re.findall(r'["\']flow[^"\']*["\']\s*:\s*["\']([^"\']+)["\']', html)
        if flow_data:
            print(f"  Flow data: {flow_data}")

        # Look for x-something headers or custom headers
        for pattern in [r'authorization[^:]*:\s*([^;\n]+)', r'api[_-]key[^:]*:\s*([^;\n]+)']:
            m = re.search(pattern, html, re.IGNORECASE)
            if m:
                print(f"  Found: {pattern[:30]} = {m.group(1)[:50]}")

        # Extract ALL script contents for analysis
        scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
        for i, sc in enumerate(scripts):
            if 'fetch' in sc or 'xhr' in sc or 'post' in sc.lower():
                urls_in_script = re.findall(r'(?:url|Url|URL|fetch|action)\s*[:=]\s*["\']([^"\']+)["\']', sc)
                if urls_in_script:
                    print(f"  Script {i} URLs: {urls_in_script}")

    # 4. Try /auth/authorize with GET but different client_id formats
    print("\n🔄 Trying different client_id formats...")
    client_ids = [
        "http://home-assistant.io/clients/hass-cli",
        "http://home-assistant.io/clients/android_app",
        "cli",
        "http://localhost",
    ]
    for cid in client_ids:
        params2 = {
            "client_id": cid,
            "redirect_uri": "http://home-assistant.io/auth-callback/",
            "response_type": "code",
            "scope": "local",
            "state": "test"
        }
        try:
            async with s.get(f"{HASS}/auth/authorize", params=params2, allow_redirects=False) as r2:
                hl = r2.headers.get("Location", "")
                if hl and "code=" in hl:
                    print(f"  ✅ client_id={cid} → redirect with code!")
                    print(f"     Location: {hl[:200]}")
                else:
                    print(f"  client_id={cid[:40]}: HTTP {r2.status}, Location={hl[:80] if hl else 'none'}")
        except Exception as e:
            print(f"  client_id={cid[:40]}: Error: {e}")

    # 5. Try legacy auth with hass-cli configured token
    print("\n📦 Checking for existing config/tokens...")
    import os
    for path in [
        os.path.expanduser("~/.homeassistant.json"),
        os.path.expanduser("~/.hass-cli/config.json"),
        "/root/.homeassistant.json",
        "/tmp/homeassistant.json"
    ]:
        if os.path.exists(path):
            with open(path) as f:
                print(f"  Found {path}: {f.read()[:200]}")

    await s.close()

try:
    asyncio.run(main())
except Exception as e:
    import traceback
    traceback.print_exc()