import { execFile } from 'node:child_process';
import { promisify } from 'node:util';

const execAsync = promisify(execFile);

const MEMORY_CLI = process.env.MEMORY_CLI || '/Users/davidnows/sinkia-memory/memory';

function runMemory(...args) {
  return execAsync(MEMORY_CLI, args, { timeout: 60000, maxBuffer: 5 * 1024 * 1024 })
    .then(({ stdout }) => stdout)
    .catch(err => {
      throw new Error(err.stderr || err.message);
    });
}

export function registerMemoryRoutes(app) {
  // Serve the memory dashboard page
  app.get('/memory', (_req, res) => {
    res.sendFile(new URL('../public/memory.html', import.meta.url).pathname);
  });

  // Search
  app.get('/api/memory/search', async (req, res) => {
    try {
      const q = req.query.query || '';
      const args = ['search'];

      if (req.query.semantic === '1') args.push('--semantic');
      if (req.query.hybrid === '1') args.push('--hybrid');
      if (q) args.push(q);
      if (req.query.app) args.push('--app', req.query.app);
      if (req.query.type) args.push('--type', req.query.type);
      if (req.query.level) args.push('--level', req.query.level);
      if (req.query.since) args.push('--since', req.query.since);
      if (req.query.until) args.push('--until', req.query.until);
      if (req.query.limit) args.push('--limit', req.query.limit);
      args.push('--format', 'json');

      const raw = await runMemory(...args);
      const results = JSON.parse(raw);
      res.json({ ok: true, results });
    } catch (err) {
      res.status(500).json({ ok: false, error: err.message });
    }
  });

  // Stats
  app.get('/api/memory/stats', async (req, res) => {
    try {
      const args = ['stats'];
      const by = req.query.by;
      if (by === 'app') args.push('--by-app');
      else if (by === 'type' || by === 'doc_type') args.push('--by-type');
      else if (by === 'source') args.push('--by-source');

      const raw = await runMemory(...args);

      // Parse rich output into structured data
      if (by) {
        // Parse table output: lines like "│ app_name │ 123 │"
        const lines = raw.split('\n').filter(l => l.includes('│'));
        const data = [];
        for (const line of lines) {
          const cells = line.split('│').map(c => c.trim()).filter(Boolean);
          if (cells.length >= 2 && !cells[0].startsWith('─') && !cells[0].startsWith('Count') && !cells[0].startsWith(by.charAt(0).toUpperCase())) {
            const count = parseInt(cells[1], 10);
            if (!isNaN(count)) data.push({ key: cells[0], count });
          }
        }
        res.json(data);
      } else {
        // Parse "Total documentos: 91468"
        const match = raw.match(/(\d[\d,]*)/);
        const total = match ? parseInt(match[1].replace(/,/g, ''), 10) : 0;
        res.json([{ total }]);
      }
    } catch (err) {
      res.status(500).json({ ok: false, error: err.message });
    }
  });

  // Apps
  app.get('/api/memory/apps', async (_req, res) => {
    try {
      const raw = await runMemory('apps');
      // Parse panel output: lines with "• app_name"
      const apps = [...raw.matchAll(/•\s+(.+)/g)].map(m => m[1].trim().replace(/\s*│\s*$/, ''));
      res.json(apps);
    } catch (err) {
      res.status(500).json({ ok: false, error: err.message });
    }
  });

  // Sources
  app.get('/api/memory/sources', async (_req, res) => {
    try {
      const raw = await runMemory('sources');
      const sources = [...raw.matchAll(/•\s+(.+)/g)].map(m => m[1].trim().replace(/\s*│\s*$/, ''));
      res.json(sources);
    } catch (err) {
      res.status(500).json({ ok: false, error: err.message });
    }
  });

  // Index (POST)
  app.post('/api/memory/index', async (_req, res) => {
    try {
      const raw = await runMemory('index', '--all');
      res.json({ ok: true, output: raw });
    } catch (err) {
      res.status(500).json({ ok: false, error: err.message });
    }
  });
}
