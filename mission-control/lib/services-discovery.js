import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const exec = promisify(execFile);
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const SERVICES_JSON = path.join(__dirname, '..', 'services.json');

// ── Docker discovery ──
async function discoverDocker() {
  try {
    const { stdout } = await exec('docker', [
      'ps', '-a', '--format',
      '{{.ID}}\t{{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}\t{{.State}}'
    ], { timeout: 10000 });

    return stdout.trim().split('\n').filter(Boolean).map(line => {
      const [id, name, image, status, ports, state] = line.split('\t');
      const isHealthy = status.includes('healthy');
      const isUnhealthy = status.includes('unhealthy');
      const health = isUnhealthy ? 'unhealthy' : isHealthy ? 'healthy' : state === 'running' ? 'running' : 'stopped';
      // Extract host ports
      const portList = (ports || '').match(/\d+\.\d+\.\d+\.\d+:(\d+)/g)?.map(p => p.split(':')[1]) || [];

      return {
        id: `docker:${name}`,
        name,
        type: 'docker',
        image,
        status,
        state,
        health,
        ports: portList,
        containerId: id.slice(0, 12),
      };
    });
  } catch {
    return [];
  }
}

// ── PM2 discovery ──
async function discoverPM2() {
  try {
    const { stdout } = await exec('pm2', ['jlist'], { timeout: 10000 });
    const procs = JSON.parse(stdout);
    return procs.map(p => ({
      id: `pm2:${p.name}`,
      name: p.name,
      type: 'pm2',
      status: p.pm2_env?.status || 'unknown',
      health: p.pm2_env?.status === 'online' ? 'healthy' : 'stopped',
      pid: p.pid,
      memory: p.monit?.memory || 0,
      cpu: p.monit?.cpu || 0,
      uptime: p.pm2_env?.pm_uptime || 0,
      restarts: p.pm2_env?.restart_time || 0,
    }));
  } catch {
    return [];
  }
}

// ── Custom services from services.json ──
async function discoverCustom() {
  try {
    const raw = await readFile(SERVICES_JSON, 'utf8');
    const services = JSON.parse(raw);

    const results = await Promise.all(services.map(async (svc) => {
      let health = 'unknown';

      if (svc.healthUrl) {
        try {
          const controller = new AbortController();
          const timer = setTimeout(() => controller.abort(), 3000);
          const resp = await fetch(svc.healthUrl, { signal: controller.signal });
          clearTimeout(timer);
          health = resp.ok ? 'healthy' : 'unhealthy';
        } catch {
          health = 'offline';
        }
      } else if (svc.checkCmd) {
        try {
          const parts = svc.checkCmd.split(' ');
          await exec(parts[0], parts.slice(1), { timeout: 5000 });
          health = 'healthy';
        } catch {
          health = 'offline';
        }
      }

      return { ...svc, type: 'custom', health };
    }));

    return results;
  } catch {
    return [];
  }
}

// ── Discover ALL services ──
export async function discoverAll() {
  const [docker, pm2, custom] = await Promise.all([
    discoverDocker(),
    discoverPM2(),
    discoverCustom(),
  ]);

  const alerts = [...docker, ...pm2, ...custom].filter(
    s => s.health === 'unhealthy' || s.health === 'offline' || s.health === 'stopped'
  );

  return {
    docker,
    pm2,
    custom,
    alerts,
    total: docker.length + pm2.length + custom.length,
    timestamp: new Date().toISOString(),
  };
}

// ── Service logs ──
export async function getServiceLogs(serviceId, lines = 50) {
  const [type, name] = serviceId.split(':');

  if (type === 'docker') {
    try {
      const { stdout, stderr } = await exec('docker', ['logs', '--tail', String(lines), name], {
        timeout: 10000,
        maxBuffer: 2 * 1024 * 1024,
      });
      return (stdout || '') + (stderr || '');
    } catch (e) {
      return `Error: ${e.message}`;
    }
  }

  if (type === 'pm2') {
    try {
      const { stdout } = await exec('pm2', ['logs', name, '--nostream', '--lines', String(lines)], {
        timeout: 10000,
        maxBuffer: 2 * 1024 * 1024,
      });
      return stdout;
    } catch (e) {
      return `Error: ${e.message}`;
    }
  }

  return 'Log retrieval not supported for this service type.';
}

// ── Restart service ──
export async function restartService(serviceId) {
  const [type, name] = serviceId.split(':');

  if (type === 'docker') {
    const { stdout } = await exec('docker', ['restart', name], { timeout: 30000 });
    return { ok: true, output: stdout.trim() };
  }

  if (type === 'pm2') {
    const { stdout } = await exec('pm2', ['restart', name], { timeout: 15000 });
    return { ok: true, output: stdout.trim() };
  }

  throw new Error(`Restart not supported for type: ${type}`);
}

// ── System metrics ──
export async function getSystemMetrics() {
  const metrics = {};

  try {
    // macOS specific
    const { stdout: dfOut } = await exec('df', ['-h', '/'], { timeout: 5000 });
    const dfLine = dfOut.trim().split('\n')[1];
    const dfParts = dfLine.split(/\s+/);
    metrics.disk = { total: dfParts[1], used: dfParts[2], free: dfParts[3], percent: dfParts[4] };
  } catch { metrics.disk = null; }

  try {
    const { stdout: memOut } = await exec('sysctl', ['-n', 'hw.memsize'], { timeout: 5000 });
    const totalBytes = parseInt(memOut.trim(), 10);
    metrics.ram = { totalGB: (totalBytes / 1073741824).toFixed(1) };
  } catch { metrics.ram = null; }

  try {
    const { stdout: loadOut } = await exec('sysctl', ['-n', 'vm.loadavg'], { timeout: 5000 });
    const loads = loadOut.trim().replace(/[{}]/g, '').trim().split(/\s+/);
    metrics.load = { '1m': loads[0], '5m': loads[1], '15m': loads[2] };
  } catch { metrics.load = null; }

  try {
    const { stdout: portsOut } = await exec('lsof', ['-i', '-P', '-n'], { timeout: 10000, maxBuffer: 1024 * 1024 });
    const listening = portsOut.split('\n')
      .filter(l => l.includes('LISTEN'))
      .map(l => {
        const parts = l.split(/\s+/);
        return { process: parts[0], pid: parts[1], address: parts[8] };
      });
    metrics.ports = listening;
  } catch { metrics.ports = []; }

  try {
    const { stdout: uptimeOut } = await exec('uptime', [], { timeout: 5000 });
    metrics.uptime = uptimeOut.trim();
  } catch { metrics.uptime = null; }

  metrics.timestamp = new Date().toISOString();
  return metrics;
}

// ── OpenClaw agents ──
export async function getOpenClawAgents() {
  try {
    const raw = await readFile(path.join(process.env.HOME, '.openclaw', 'openclaw.json'), 'utf8');
    const config = JSON.parse(raw);
    const agents = (config.agents?.list || []).map(a => ({
      id: a.id,
      name: a.name || a.id,
      model: a.model || config.agents?.defaults?.model || 'unknown',
      workspace: a.workspace || config.agents?.defaults?.workspace,
      sandbox: a.sandbox?.mode || config.agents?.defaults?.sandbox?.mode || 'none',
    }));
    return {
      agents,
      gateway: {
        port: config.gateway?.port,
        mode: config.gateway?.mode,
        auth: config.gateway?.auth?.mode,
      },
      defaultModel: config.agents?.defaults?.model,
    };
  } catch (e) {
    return { agents: [], error: e.message };
  }
}
