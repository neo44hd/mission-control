import express from 'express';
import { createServer } from 'http';
import { WebSocketServer } from 'ws';
import { exec, spawn } from 'child_process';
import { promisify } from 'util';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';

const execAsync = promisify(exec);
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PORT = parseInt(process.env.APP_PORT || '9302', 10);
const HOST = process.env.APP_HOST || '0.0.0.0';

const app = express();
const server = createServer(app);
const wss = new WebSocketServer({ server, path: '/ws/terminal' });

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// ═══════════════════════════════════════════════════════════════
// AUTH MIDDLEWARE — Tailscale Device Authentication
// Only allow connections from localhost or Tailscale network
// ═══════════════════════════════════════════════════════════════
app.use((req, res, next) => {
  const ip = req.ip || req.socket.remoteAddress || '';
  const isLocalhost = ip === '127.0.0.1' || ip === '::1' || ip === 'localhost';
  const isTailscale = ip.startsWith('100.') || ip.startsWith('fd7a:');
  
  if (isLocalhost || isTailscale) {
    return next();
  }
  
  // Reject connections from outside Tailscale network
  res.status(401).json({ 
    error: 'Unauthorized',
    message: 'Solo dispositivos en la red Tailscale pueden acceder',
    your_ip: ip
  });
});

// ═══════════════════════════════════════════════════════════════
// SYSTEM METRICS
// ═══════════════════════════════════════════════════════════════

async function getSystemMetrics() {
  try {
    const { stdout: df } = await execAsync('df -h / | tail -1');
    const parts = df.trim().split(/\s+/);
    const { stdout: vm } = await execAsync('vm_stat');
    const { stdout: memsize } = await execAsync('sysctl -n hw.memsize');
    const { stdout: uptime } = await execAsync('uptime');
    const { stdout: load } = await execAsync("sysctl -n vm.loadavg");
    const { stdout: cpu } = await execAsync("sysctl -n machdep.cpu.brand_string 2>/dev/null || echo 'Apple Silicon'");
    const vmLines = vm.split('\n');
    let pageSize = 4096, freePages = 0, activePages = 0, inactivePages = 0, wiredPages = 0, speculativePages = 0, compressedPages = 0;
    for (const line of vmLines) {
      if (line.includes('page size of')) { const m = line.match(/(\d+)/); if (m) pageSize = parseInt(m[1]); }
      if (line.includes('Pages free:')) freePages = parseInt(line.match(/(\d+)/)?.[1] || '0');
      if (line.includes('Pages active:')) activePages = parseInt(line.match(/(\d+)/)?.[1] || '0');
      if (line.includes('Pages inactive:')) inactivePages = parseInt(line.match(/(\d+)/)?.[1] || '0');
      if (line.includes('Pages wired down:')) wiredPages = parseInt(line.match(/(\d+)/)?.[1] || '0');
      if (line.includes('Pages speculative:')) speculativePages = parseInt(line.match(/(\d+)/)?.[1] || '0');
      if (line.includes('Pages occupied by compressor:')) compressedPages = parseInt(line.match(/(\d+)/)?.[1] || '0');
    }
    const totalBytes = parseInt(memsize.trim(), 10);
    const availableBytes = (freePages + speculativePages + inactivePages) * pageSize;
    const usedBytes = Math.max(0, totalBytes - availableBytes);
    const totalGB = (totalBytes / (1024**3)).toFixed(1);
    const usedGB = (usedBytes / (1024**3)).toFixed(1);
    const freeGB = (availableBytes / (1024**3)).toFixed(1);
    const load1m = parseFloat(load.trim().split(' ')[1] || '0').toFixed(2);
    return { disk: { total: parts[1], used: parts[2], free: parts[3], pct: parts[4] }, ram: { totalGB, usedGB, freeGB, compressedGB: (compressedPages * pageSize / (1024**3)).toFixed(1) }, load: { '1m': load1m }, uptime: uptime.trim(), cpu: cpu.trim() };
  } catch (e) { return { error: e.message }; }
}

// ═══════════════════════════════════════════════════════════════
// DOCKER
// ═══════════════════════════════════════════════════════════════

async function getDockerContainers() {
  try {
    const { stdout } = await execAsync('docker ps -a --format "{{.ID}}|{{.Names}}|{{.Image}}|{{.Status}}|{{.Ports}}" 2>/dev/null');
    const containers = [];
    for (const line of stdout.trim().split('\n')) {
      if (!line) continue;
      const [id, name, image, status, ports] = line.split('|');
      let health = 'unknown';
      if (status.includes('unhealthy')) health = 'unhealthy';
      else if (status.includes('healthy')) health = 'healthy';
      else if (status.includes('Up')) health = 'running';
      else if (status.includes('Exited') || status.includes('Created')) health = 'stopped';
      containers.push({ id: id.slice(0, 12), name, image, status, ports, health, type: 'docker' });
    }
    return containers;
  } catch { return []; }
}

async function dockerAction(id, action) {
  try { const { stdout, stderr } = await execAsync(`docker ${action} ${id} 2>&1`); return { ok: true, output: stdout || stderr }; }
  catch (e) { return { ok: false, error: e.message }; }
}

async function getDockerLogs(id, lines = 80) {
  try { const { stdout } = await execAsync(`docker logs --tail ${lines} ${id} 2>&1`); return stdout; }
  catch (e) { return e.message; }
}

// ═══════════════════════════════════════════════════════════════
// PM2
// ═══════════════════════════════════════════════════════════════

async function getPM2Processes() {
  try {
    const { stdout } = await execAsync('pm2 jlist 2>/dev/null');
    return JSON.parse(stdout).map(p => ({
      id: p.pm_id, name: p.name, pid: p.pid, status: p.pm2_env.status,
      health: p.pm2_env.status === 'online' ? 'healthy' : 'unhealthy',
      memory: p.monit?.memory, cpu: p.monit?.cpu, restarts: p.pm2_env.restart_time, type: 'pm2'
    }));
  } catch { return []; }
}

async function pm2Action(name, action) {
  try { const { stdout } = await execAsync(`pm2 ${action} ${name} 2>&1`); return { ok: true, output: stdout }; }
  catch (e) { return { ok: false, error: e.message }; }
}

async function getPM2Logs(name, lines = 80) {
  try {
    const logDir = path.join(process.env.HOME, '.pm2', 'logs');
    const files = fs.readdirSync(logDir).filter(f => f.startsWith(name) && f.endsWith('.out.log'));
    if (!files.length) return 'Sin logs';
    const { stdout } = await execAsync(`tail -${lines} "${path.join(logDir, files.sort().reverse()[0])}"`);
    return stdout;
  } catch (e) { return e.message; }
}

// ═══════════════════════════════════════════════════════════════
// OPENCLAW
// ═══════════════════════════════════════════════════════════════

async function getOpenClawAgents() {
  try {
    const cfg = JSON.parse(fs.readFileSync(path.join(process.env.HOME, '.openclaw', 'openclaw.json'), 'utf8'));
    return (cfg.agents?.list || []).map(a => ({
      id: a.id, name: a.name || a.id, model: a.model || cfg.agents.defaults?.model || 'default',
      workspace: a.workspace || cfg.agents.defaults?.workspace || 'default', type: 'openclaw-agent'
    }));
  } catch { return []; }
}

// ═══════════════════════════════════════════════════════════════
// OLLAMA
// ═══════════════════════════════════════════════════════════════

async function getOllamaModels() {
  try {
    const { stdout } = await execAsync('ollama list 2>/dev/null');
    return stdout.trim().split('\n').slice(1).map(l => {
      const p = l.split(/\s{2,}/);
      return { name: p[0], id: p[1], size: p[2], modified: p[3] };
    }).filter(m => m.name);
  } catch { return []; }
}

// ═══════════════════════════════════════════════════════════════
// SERVICES DISCOVERY
// ═══════════════════════════════════════════════════════════════

async function discoverServices() {
  const [docker, pm2, agents, ollama, metrics] = await Promise.all([
    getDockerContainers(), getPM2Processes(), getOpenClawAgents(), getOllamaModels(), getSystemMetrics()
  ]);
  const custom = [];
  const portMap = {
    '3000': { name: 'SynK-IA Backend', icon: '🔧', url: 'http://localhost:3000' },
    '59401': { name: 'SynK-IA API', icon: '🔧', url: 'http://localhost:59401' },
    '9302': { name: 'Mission Control', icon: '⚡', url: 'http://localhost:9302' },
    '3030': { name: 'Open WebUI', icon: '💬', url: 'http://localhost:3030' },
    '4400': { name: 'Commerce TPV', icon: '🛒', url: 'http://localhost:4400' },
    '5678': { name: 'n8n', icon: '🔄', url: 'http://localhost:5678' },
    '6333': { name: 'Qdrant', icon: '🧠', url: 'http://localhost:6333' },
    // '7999': { name: 'OpenClaw Gateway (deprecated)', icon: '🦞', url: 'http://localhost:7999/dashboard' },
    '8888': { name: 'SearXNG', icon: '🔍', url: 'http://localhost:8888' },
    '11434': { name: 'Ollama', icon: '🦙', url: 'http://localhost:11434' },
  };
  try {
    const { stdout } = await execAsync('lsof -i -P -n 2>/dev/null | grep LISTEN');
    const ports = new Set(stdout.split('\n').map(l => l.match(/:(\d+)\s/)?.[1]).filter(Boolean));
    for (const [port, info] of Object.entries(portMap)) {
      if (ports.has(port)) custom.push({ id: `port-${port}`, ...info, port, health: 'healthy', type: 'service' });
    }
  } catch {}
  const alerts = [
    ...docker.filter(c => c.health === 'unhealthy' || c.health === 'stopped').map(c => ({ name: c.name, health: c.health, type: 'docker' })),
    ...pm2.filter(p => p.health !== 'healthy').map(p => ({ name: p.name, health: p.status, type: 'pm2' }))
  ];
  return { docker, pm2, agents, ollama, custom, metrics, alerts, total: docker.length + pm2.length + agents.length + custom.length };
}

// ═══════════════════════════════════════════════════════════════
// REPAIR KIT
// ═══════════════════════════════════════════════════════════════

async function runRepair(action) {
  const repairs = {
    'restart-all-docker': 'docker restart $(docker ps -q)',
    'restart-all-pm2': 'pm2 restart all',
    'stop-all-docker': 'docker stop $(docker ps -q)',
    'docker-prune': 'docker system prune -f',
    'pm2-save': 'pm2 save',
    'flush-dns': 'dscacheutil -flushcache && killall -HUP mDNSResponder',
    'restart-ollama': 'brew services restart ollama',
    'restart-openclaw': 'openclaw gateway restart',
    'reindex-memory': 'cd ~/sinkia-memory && /usr/bin/python3 src/cli.py index --all',
    'docker-compose-up': 'cd ~/synkia-app/docker && docker compose up -d',
    'docker-compose-down': 'cd ~/synkia-app/docker && docker compose down',
    'release-ram': 'sudo purge && echo "RAM cache liberada"',
  };
  const cmd = repairs[action];
  if (!cmd) return { ok: false, error: `Acción desconocida: ${action}` };
  try { const { stdout, stderr } = await execAsync(cmd); return { ok: true, output: stdout || stderr || 'Completado' }; }
  catch (e) { return { ok: false, error: e.message }; }
}

// ═══════════════════════════════════════════════════════════════
// TAILSCALE & CLOUDFLARE
// ═══════════════════════════════════════════════════════════════

async function getTailscaleStatus() {
  try { const { stdout } = await execAsync('tailscale status 2>/dev/null'); return stdout; }
  catch (e) { return 'Tailscale no disponible'; }
}

async function getTunnelStatus() {
  try { const { stdout } = await execAsync('cloudflared tunnel info 4298eb1a-c6f0-42d7-aa57-f7987ff43787 2>&1'); return stdout; }
  catch (e) { return e.message; }
}

// ═══════════════════════════════════════════════════════════════
// API ROUTES
// ═══════════════════════════════════════════════════════════════

app.get('/api/services', async (req, res) => { try { res.json(await discoverServices()); } catch (e) { res.status(500).json({ error: e.message }); } });
app.get('/api/system', async (req, res) => { try { res.json(await getSystemMetrics()); } catch (e) { res.status(500).json({ error: e.message }); } });
app.post('/api/docker/:id/:action', async (req, res) => res.json(await dockerAction(req.params.id, req.params.action)));
app.get('/api/docker/:id/logs', async (req, res) => res.json({ ok: true, logs: await getDockerLogs(req.params.id, parseInt(req.query.lines || '80')) }));
app.post('/api/pm2/:name/:action', async (req, res) => res.json(await pm2Action(req.params.name, req.params.action)));
app.get('/api/pm2/:name/logs', async (req, res) => res.json({ ok: true, logs: await getPM2Logs(req.params.name, parseInt(req.query.lines || '80')) }));
app.get('/api/openclaw/agents', async (req, res) => res.json({ agents: await getOpenClawAgents() }));
app.get('/api/ollama/models', async (req, res) => res.json({ models: await getOllamaModels() }));
app.post('/api/ollama/:action/:model', async (req, res) => {
  try { const { stdout } = await execAsync(`ollama ${req.params.action} ${req.params.model} 2>&1`); res.json({ ok: true, output: stdout }); }
  catch (e) { res.json({ ok: false, error: e.message }); }
});
app.post('/api/repair/:action', async (req, res) => res.json(await runRepair(req.params.action)));
app.get('/api/repair/actions', (req, res) => res.json({ actions: [
  { id: 'restart-all-docker', name: 'Reiniciar todos los contenedores', icon: '🐳', category: 'docker' },
  { id: 'restart-all-pm2', name: 'Reiniciar todos los procesos PM2', icon: '💚', category: 'pm2' },
  { id: 'stop-all-docker', name: 'Parar todos los contenedores', icon: '🛑', category: 'docker' },
  { id: 'docker-prune', name: 'Limpiar Docker (prune)', icon: '🧹', category: 'docker' },
  { id: 'docker-compose-up', name: 'Docker Compose Up', icon: '⬆️', category: 'docker' },
  { id: 'docker-compose-down', name: 'Docker Compose Down', icon: '⬇️', category: 'docker' },
  { id: 'release-ram', name: 'Liberar caché de RAM', icon: '⚡', category: 'system' },
  { id: 'restart-ollama', name: 'Reiniciar Ollama', icon: '🦙', category: 'services' },
  { id: 'restart-openclaw', name: 'Reiniciar OpenClaw Gateway', icon: '🦞', category: 'services' },
  { id: 'flush-dns', name: 'Limpiar caché DNS', icon: '🌐', category: 'network' },
  { id: 'pm2-save', name: 'Guardar estado PM2', icon: '💾', category: 'pm2' },
  { id: 'reindex-memory', name: 'Re-indexar sinkMAIND', icon: '🧠', category: 'services' },
  { id: 'update-system', name: 'Actualizar brew', icon: '⬆️', category: 'system' },
]}));
app.get('/api/tailscale/status', async (req, res) => res.json({ status: await getTailscaleStatus() }));
app.get('/api/cloudflare/status', async (req, res) => res.json({ status: await getTunnelStatus() }));

// ═══════════════════════════════════════════════════════════════
// WEBSOCKET TERMINAL
// ═══════════════════════════════════════════════════════════════

wss.on('connection', (ws) => {
  const shell = spawn('/bin/zsh', ['-i'], { cwd: process.env.HOME, env: { ...process.env, TERM: 'xterm-256color' }, pty: true });
  shell.stdout.on('data', d => ws.send(JSON.stringify({ type: 'output', data: d.toString() })));
  shell.stderr.on('data', d => ws.send(JSON.stringify({ type: 'output', data: d.toString() })));
  shell.on('close', () => { ws.send(JSON.stringify({ type: 'exit' })); ws.close(); });
  ws.on('message', msg => { try { const { type, data } = JSON.parse(msg.toString()); if (type === 'input') shell.stdin.write(data); } catch {} });
  ws.on('close', () => shell.kill());
});

// ═══════════════════════════════════════════════════════════════
// SPA FALLBACK (must be last)
// ═══════════════════════════════════════════════════════════════

app.use((req, res) => res.sendFile(path.join(__dirname, 'public', 'index.html')));

// ═══════════════════════════════════════════════════════════════
// START
// ═══════════════════════════════════════════════════════════════

server.listen(PORT, HOST, () => {
  console.log(`\n⚡ Mission Control v2 → http://${HOST}:${PORT}`);
  console.log(`   WebSocket terminal → ws://${HOST}:${PORT}/ws/terminal\n`);
});
