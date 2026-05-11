import express from 'express';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { getPublicConfig, getRuntimeConfig } from './lib/config.js';
import { generateResponse, getHealth } from './lib/providers.js';
import { registerMemoryRoutes } from './lib/memory-api.js';
import { requireAuth, authLoginHandler, authLogoutHandler } from './lib/auth.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const publicDir = path.join(__dirname, 'public');
const app = express();
const runtime = getRuntimeConfig();

app.use(express.json({ limit: '1mb' }));
app.use(express.urlencoded({ extended: true }));
app.use(express.static(publicDir));

// Auth login/logout (unauthenticated)
app.post('/api/auth/login', authLoginHandler);
app.get('/api/auth/logout', authLogoutHandler);

// All routes below require authentication (if AUTH_PASS is set in .env)
app.use(requireAuth);

// sinkMAIND memory API
registerMemoryRoutes(app);

app.get('/api/health', async (_req, res) => {
  const health = await getHealth();
  res.json(health);
});

app.get('/api/config', (_req, res) => {
  res.json(getPublicConfig());
});

app.post('/api/chat', async (req, res) => {
  try {
    const result = await generateResponse({
      prompt: req.body?.prompt,
      provider: req.body?.provider,
      model: req.body?.model,
      systemPrompt: req.body?.systemPrompt,
      temperature: req.body?.temperature,
      maxTokens: req.body?.maxTokens,
    });

    res.json({
      ok: true,
      ...result,
    });
  } catch (error) {
    const status =
      error.code === 'PROMPT_REQUIRED'
        ? 400
        : error.code === 'ANTHROPIC_KEY_MISSING'
          ? 503
          : 502;

    res.status(status).json({
      ok: false,
      error: error.message,
      code: error.code ?? 'REQUEST_FAILED',
    });
  }
});

app.get('/{*any}', (_req, res) => {
  res.sendFile(path.join(publicDir, 'index.html'));
});

app.listen(runtime.app.port, runtime.app.host, () => {
  console.log(
    `Mission Control API + panel en http://${runtime.app.host}:${runtime.app.port}`,
  );
});
