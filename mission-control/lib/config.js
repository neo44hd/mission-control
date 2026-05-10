import 'dotenv/config';
import fs from 'node:fs';
import { execFileSync } from 'node:child_process';

function normalize(value) {
  const trimmed = value?.trim();
  return trimmed ? trimmed : undefined;
}

function readKeyFromFile(filePath) {
  if (!filePath || !fs.existsSync(filePath)) {
    return undefined;
  }

  const value = fs.readFileSync(filePath, 'utf8').trim();
  return value || undefined;
}

function readKeyFromKeychain(service, account) {
  if (!service) {
    return undefined;
  }

  const args = ['find-generic-password', '-s', service];
  if (account) {
    args.push('-a', account);
  }
  args.push('-w');

  try {
    const value = execFileSync('security', args, {
      encoding: 'utf8',
      stdio: ['ignore', 'pipe', 'ignore'],
    }).trim();
    return value || undefined;
  } catch {
    return undefined;
  }
}

function resolveAnthropicCredentials() {
  const envKey = normalize(process.env.ANTHROPIC_API_KEY);
  if (envKey) {
    return { apiKey: envKey, source: 'env' };
  }

  const fileKey = readKeyFromFile(normalize(process.env.ANTHROPIC_API_KEY_FILE));
  if (fileKey) {
    return { apiKey: fileKey, source: 'file' };
  }

  const keychainService = normalize(process.env.ANTHROPIC_API_KEY_KEYCHAIN_SERVICE);
  const keychainAccount = normalize(process.env.ANTHROPIC_API_KEY_KEYCHAIN_ACCOUNT);
  const keychainKey = readKeyFromKeychain(keychainService, keychainAccount);
  if (keychainKey) {
    return { apiKey: keychainKey, source: 'keychain' };
  }

  return { apiKey: undefined, source: 'none' };
}

export function getRuntimeConfig() {
  const anthropicCredentials = resolveAnthropicCredentials();

  return {
    provider: normalize(process.env.MODEL_PROVIDER) ?? 'auto',
    prompt:
      normalize(process.env.PROMPT) ??
      'Di hola y confirma qué proveedor y modelo estás usando.',
    systemPrompt:
      normalize(process.env.SYSTEM_PROMPT) ??
      'Responde como asistente conversacional en español. No uses tool calls, XML, etiquetas ni plantillas de funciones. Responde solo con texto natural claro y útil.',
    app: {
      host: normalize(process.env.APP_HOST) ?? '127.0.0.1',
      port: Number.parseInt(process.env.APP_PORT ?? '3030', 10),
    },
    lmstudio: {
      baseURL: normalize(process.env.LMSTUDIO_BASE_URL) ?? 'http://10.0.1.13:1234/v1',
      model: normalize(process.env.LMSTUDIO_MODEL) ?? 'medina-qwen3-14b-openclaw',
      apiKey: normalize(process.env.LMSTUDIO_API_KEY) ?? 'lm-studio',
    },
    anthropic: {
      apiKey: anthropicCredentials.apiKey,
      keySource: anthropicCredentials.source,
      baseURL: normalize(process.env.ANTHROPIC_BASE_URL),
      model: normalize(process.env.ANTHROPIC_MODEL) ?? 'claude-sonnet-4-6',
    },
  };
}

export function getPublicConfig() {
  const config = getRuntimeConfig();

  return {
    provider: config.provider,
    systemPrompt: config.systemPrompt,
    app: config.app,
    lmstudio: {
      baseURL: config.lmstudio.baseURL,
      model: config.lmstudio.model,
      configured: Boolean(config.lmstudio.baseURL && config.lmstudio.model),
    },
    anthropic: {
      baseURL: config.anthropic.baseURL ?? 'https://api.anthropic.com',
      model: config.anthropic.model,
      enabled: Boolean(config.anthropic.apiKey),
      keySource: config.anthropic.keySource,
    },
  };
}
