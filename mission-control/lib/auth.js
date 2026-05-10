import crypto from 'node:crypto';

/**
 * Basic Auth middleware for Express.
 * Credentials are read from env vars AUTH_USER and AUTH_PASS.
 * If AUTH_PASS is empty or missing, auth is disabled (local access only).
 * Supports session tokens via cookies for browser convenience.
 */

const AUTH_USER = process.env.AUTH_USER || 'admin';
const AUTH_PASS = process.env.AUTH_PASS || '';
const AUTH_ENABLED = AUTH_PASS.length > 0;
const SESSION_SECRET = process.env.AUTH_SECRET || crypto.randomBytes(32).toString('hex');
const SESSION_COOKIE = 'mc_session';
const SESSION_MAX_AGE = 24 * 60 * 60 * 1000; // 24h

// In-memory session store (resets on server restart)
const sessions = new Map();

function generateToken() {
  return crypto.randomBytes(32).toString('hex');
}

function isValidSession(token) {
  if (!token) return false;
  const entry = sessions.get(token);
  if (!entry) return false;
  if (Date.now() - entry.created > SESSION_MAX_AGE) {
    sessions.delete(token);
    return false;
  }
  return true;
}

function cleanExpiredSessions() {
  const now = Date.now();
  for (const [token, entry] of sessions) {
    if (now - entry.created > SESSION_MAX_AGE) sessions.delete(token);
  }
}

// Clean every hour
setInterval(cleanExpiredSessions, 60 * 60 * 1000);

/**
 * Express middleware that enforces Basic Auth or session cookie.
 */
export function requireAuth(req, res, next) {
  if (!AUTH_ENABLED) return next();

  // Allow localhost/127.0.0.1 without auth (local dev access)
  const remoteIp = req.ip || req.connection?.remoteAddress || '';
  if (remoteIp === '127.0.0.1' || remoteIp === '::1' || remoteIp === '::ffff:127.0.0.1') {
    return next();
  }

  // 1. Check session cookie
  const cookie = req.headers.cookie || '';
  const match = cookie.match(new RegExp(`${SESSION_COOKIE}=([^;]+)`));
  if (match && isValidSession(match[1])) {
    return next();
  }

  // 2. Check Basic Auth header
  const authHeader = req.headers.authorization;
  if (authHeader && authHeader.startsWith('Basic ')) {
    const decoded = Buffer.from(authHeader.slice(6), 'base64').toString();
    const colonIndex = decoded.indexOf(':');
    if (colonIndex > 0) {
      const user = decoded.slice(0, colonIndex);
      const pass = decoded.slice(colonIndex + 1);
      if (user === AUTH_USER && pass === AUTH_PASS) {
        // Create session
        const token = generateToken();
        sessions.set(token, { created: Date.now(), user });
        res.setHeader('Set-Cookie', `${SESSION_COOKIE}=${token}; Path=/; HttpOnly; SameSite=Strict; Max-Age=${SESSION_MAX_AGE / 1000}`);
        return next();
      }
    }
  }

  // 3. Reject
  // If browser (accepts HTML), show login page; otherwise send 401
  const accept = req.headers.accept || '';
  if (accept.includes('text/html')) {
    res.setHeader('WWW-Authenticate', 'Basic realm="Mission Control"');
    res.status(401).send(`<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Auth Required</title>
<style>body{font-family:system-ui;background:#0b1020;color:#ecf2ff;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0}
.card{background:#131a2d;border:1px solid #26314f;border-radius:18px;padding:40px;text-align:center;max-width:400px}
h1{font-size:20px;margin:0 0 8px}p{color:#a8b3cf;font-size:14px;margin:0 0 20px}
input{background:#1a233b;border:1px solid #26314f;border-radius:10px;padding:10px 14px;color:#ecf2ff;font:inherit;width:100%;margin-bottom:10px;box-sizing:border-box}
input:focus{outline:none;border-color:#6ea8fe}button{background:#6ea8fe;color:#081121;border:0;border-radius:10px;padding:10px 20px;font:inherit;font-weight:700;cursor:pointer;width:100%}
.err{color:#f87171;font-size:13px;margin-bottom:10px;display:none}</style></head>
<body><div class="card"><h1>Mission Control</h1><p>Introduce tus credenciales</p>
<div class="err" id="err">Credenciales incorrectas</div>
<form method="POST" action="/api/auth/login"><input type="text" id="u" name="username" placeholder="Usuario" autocomplete="username" required/>
<input type="password" id="p" name="password" placeholder="Contraseña" autocomplete="current-password" required/>
<button type="submit">Entrar</button></form></div></body></html>`);
    return;
  }

  // API clients get 401 JSON
  res.setHeader('WWW-Authenticate', 'Basic realm="Mission Control"');
  res.status(401).json({ ok: false, error: 'Authentication required', code: 'AUTH_REQUIRED' });
}

/**
 * Login endpoint for form-based auth (from the HTML login page).
 */
export function authLoginHandler(req, res) {
  const { username, password } = req.body || {};
  if (username === AUTH_USER && password === AUTH_PASS) {
    const token = generateToken();
    sessions.set(token, { created: Date.now(), user: username });
    res.setHeader('Set-Cookie', `${SESSION_COOKIE}=${token}; Path=/; HttpOnly; SameSite=Strict; Max-Age=${SESSION_MAX_AGE / 1000}`);
    // Redirect to the page they came from or root
    const redirect = req.query.redirect || '/';
    res.redirect(redirect);
  } else {
    res.redirect('/?auth=failed');
  }
}

/**
 * Logout endpoint.
 */
export function authLogoutHandler(_req, res) {
  const cookie = _req.headers.cookie || '';
  const match = cookie.match(new RegExp(`${SESSION_COOKIE}=([^;]+)`));
  if (match) sessions.delete(match[1]);
  res.setHeader('Set-Cookie', `${SESSION_COOKIE}=; Path=/; HttpOnly; SameSite=Strict; Max-Age=0`);
  res.redirect('/');
}
