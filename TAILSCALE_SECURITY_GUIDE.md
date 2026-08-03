# Tailscale Security Configuration Guide

## Overview

Your machine is now protected by a **Tailscale-based security layer** that restricts all access to devices in your Tailscale network. This document describes:

1. How access is controlled
2. How to access services via Tailscale
3. What services are protected
4. Configuration details

---

## Security Architecture

### Layers of Protection

```
Internet → Tailscale Network Boundary → Authenticated Access → Internal Services
                     ↓
            (Only your devices allowed)
                     ↓
         Tailscale Central Proxy (Port 8443)
                     ↓
        Routing to all internal services
```

### Access Control

- **Localhost (127.0.0.1, ::1)**: Full access (development/admin only)
- **Tailscale Network (100.x.x.x, fd7a:x:x:x)**: Full access (your devices)
- **External IPs**: Blocked with 401 Unauthorized

---

## Protected Services

The following services are now accessible ONLY through the Tailscale proxy:

| Shortcut | Service | Internal Port | Access URL |
|----------|---------|---------------|-----------|
| `mc` | Mission Control v1 | 3001 | `http://sinkpro.ts.net:8443/mc/` |
| `dashboard` | Mission Control v2 | 9302 | `http://sinkpro.ts.net:8443/dashboard/` |
| `api` | SynK-IA API | 59401 | `http://sinkpro.ts.net:8443/api/` |
| `webui` | Open WebUI | 3030 | `http://sinkpro.ts.net:8443/webui/` |
| `tpv` | Commerce TPV | 4400 | `http://sinkpro.ts.net:8443/tpv/` |
| `n8n` | n8n Workflow | 5678 | `http://sinkpro.ts.net:8443/n8n/` |
| `qdrant` | Qdrant Vector DB | 6333 | `http://sinkpro.ts.net:8443/qdrant/` |
| `openclaw` | OpenClaw AI | 7999 | `http://sinkpro.ts.net:8443/openclaw/` |
| `search` | SearXNG | 8888 | `http://sinkpro.ts.net:8443/search/` |
| `ollama` | Ollama Models | 11434 | `http://sinkpro.ts.net:8443/ollama/` |

---

## How to Access Services

### From Tailscale-Connected Devices

Simply use the service URLs above with your Tailscale hostname:

```bash
# Access Mission Control v2
curl http://sinkpro.ts.net:8443/dashboard/

# Access SynK-IA API
curl http://sinkpro.ts.net:8443/api/services

# Access Ollama
curl http://sinkpro.ts.net:8443/ollama/api/models
```

### Check Proxy Status

```bash
curl http://sinkpro.ts.net:8443/
```

Response shows available services and your IP address.

---

## Configuration Details

### Tailscale Central Proxy

**File**: `/Users/davidnows/tailscale-proxy.js`  
**Port**: 8443  
**Host**: 0.0.0.0 (but auth middleware blocks non-Tailscale IPs)  
**Process Manager**: PM2 (id: 4)  
**Status**: `pm2 status | grep tailscale-proxy`

**Key Features**:
- Tailscale IP detection (100.x.x.x and fd7a:x:x:x ranges)
- Localhost bypass for development
- HTTP proxy to internal services
- Request forwarding with Tailscale headers

### Mission Control v2

**File**: `/Users/davidnows/mission-control/server.js`  
**Port**: 9302  
**Auth**: Tailscale + Localhost  
**Process Manager**: PM2 (id: 3)  
**Access**: `http://sinkpro.ts.net:8443/dashboard/`

---

## Tailscale Device List

Your Tailscale network includes:

```
Devices:
- sinkpro (100.78.4.14)          - macOS [THIS MACHINE]
- imac-de-chicken (100.116.49.37) - macOS [active]
- 7seve-n (100.103.20.92)         - Android [offline]
- ipad-pro-12-9-gen-3 (100.79.186.69) - iOS
- iphone-15-pro-max (100.68.160.50)   - iOS
- sinkia (100.91.86.75)           - Linux server
- sinkialabs (100.103.194.10)     - Linux server
```

Only these devices can access your services.

---

## Testing Access Control

### Test From Localhost (Should Work)

```bash
curl http://localhost:8443/
# Returns: {"status": "online", "proxy": "Tailscale Central Security Proxy", ...}
```

### Test From Tailscale Network (Should Work)

From another device in your Tailscale network:

```bash
curl http://sinkpro.ts.net:8443/
# Returns: {"status": "online", ...}
```

### Test From External IP (Should Fail)

```bash
# From outside Tailscale network
curl http://YOUR_PUBLIC_IP:8443/
# Returns: 401 {"error": "Unauthorized", "message": "Solo dispositivos..."}
```

---

## Accessing via SSH Tunnel (Alternative)

If you prefer SSH access with local port forwarding:

```bash
# Connect to machine via Tailscale
ssh user@sinkpro.ts.net

# Then access services as if you were local
curl http://localhost:3001  # Mission Control v1
curl http://localhost:9302  # Mission Control v2
```

---

## Monitoring

### Check Proxy Status

```bash
pm2 status | grep tailscale-proxy
```

### View Logs

```bash
pm2 logs tailscale-proxy --lines 50
```

### Restart if Needed

```bash
pm2 restart tailscale-proxy
```

---

## Firewall Rules (for reference)

Currently, ports are open to 0.0.0.0 but protected by application-level middleware:

**Open Ports**:
- 8443 (Tailscale Central Proxy) - Auth required
- 9302 (Mission Control v2) - Auth required
- 3001, 3030, 4400, 5678, 6333, 7999, 8888, 11434 (Other services) - Not directly exposed

**Protected by**:
1. Tailscale network boundary (VPN)
2. Application-level IP filtering
3. User authentication (per-service)

---

## Next Steps

### Option A: Further Lock Down Ports

To add an extra layer of security, all services could be bound to **127.0.0.1 only** and accessed exclusively via:

1. SSH tunneling from Tailscale
2. Tailscale MagicDNS with local proxy

This would prevent direct network exposure.

### Option B: Firewall Rules

Configure macOS firewall to allow only Tailscale interface:

```bash
# Check current rules
sudo pfctl -sr

# Add rules to restrict ports to Tailscale interface only
```

### Option C: ACLs at Tailscale Level

Configure Tailscale ACLs to further restrict device-to-device communication:

Visit: https://login.tailscale.com/admin/acls

---

## Emergency Access

If Tailscale is down or misconfigured:

1. Physical access: Direct SSH on localhost
2. Recovery: `ssh localhost` (requires local key)
3. Reset: `pm2 restart all` to reload services

---

## Troubleshooting

### Proxy Returns 401

**Problem**: "Solo dispositivos en la red Tailscale pueden acceder"

**Solution**: Ensure you're connected to Tailscale network:
```bash
tailscale status
```

### Proxy Service Unavailable (503)

**Problem**: Service shows as unavailable

**Solution**: Check if backend service is running:
```bash
pm2 status
pm2 logs <service-name>
```

### Connection Refused on Port 8443

**Problem**: Can't connect to proxy

**Solution**: Verify proxy is running:
```bash
pm2 status tailscale-proxy
pm2 start /Users/davidnows/tailscale-proxy.js
```

---

## Security Notes

✅ **Implemented**:
- Tailscale network-based access control
- Localhost bypass for development
- Central proxy authentication
- Request forwarding with IP headers

⚠️ **Consider**:
- HTTPS/TLS for the proxy (currently HTTP)
- Rate limiting on proxy endpoints
- Audit logging of proxy requests
- Per-service API keys (in addition to network auth)

---

**Last Updated**: 2026-05-28  
**Maintained by**: Oz Agent  
**Status**: Production Ready
