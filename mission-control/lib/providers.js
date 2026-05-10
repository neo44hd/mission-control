import Anthropic from '@anthropic-ai/sdk';
import { getPublicConfig, getRuntimeConfig } from './config.js';

export { getRuntimeConfig, getPublicConfig } from './config.js';

function extractAnthropicText(message) {
  return (
    message.content
      ?.filter((block) => block.type === 'text')
      .map((block) => block.text)
      .join('\n')
      .trim() ?? ''
  );
}

function buildLmStudioUrl(baseURL, path) {
  return `${baseURL.replace(/\/$/, '')}${path}`;
}

export async function probeLmStudio() {
  const config = getRuntimeConfig();
  const response = await fetch(buildLmStudioUrl(config.lmstudio.baseURL, '/models'), {
    headers: {
      Authorization: `Bearer ${config.lmstudio.apiKey}`,
    },
  });

  if (!response.ok) {
    const details = await response.text();
    throw new Error(`LM Studio respondió ${response.status}: ${details}`);
  }

  const data = await response.json();
  return {
    reachable: true,
    modelCount: Array.isArray(data.data) ? data.data.length : 0,
  };
}

export async function callAnthropic(prompt, overrides = {}) {
  const config = getRuntimeConfig();
  const model = overrides.model ?? config.anthropic.model;
  const systemPrompt = overrides.systemPrompt ?? config.systemPrompt;

  if (!config.anthropic.apiKey) {
    const error = new Error(
      'Anthropic cloud está desactivado: no hay clave configurada en env, archivo o Keychain.',
    );
    error.code = 'ANTHROPIC_KEY_MISSING';
    throw error;
  }

  const client = new Anthropic({
    apiKey: config.anthropic.apiKey,
    baseURL: config.anthropic.baseURL,
  });

  const response = await client.messages.create({
    model,
    max_tokens: overrides.maxTokens ?? 1024,
    temperature: overrides.temperature ?? 0.2,
    system: systemPrompt,
    messages: [{ role: 'user', content: prompt }],
  });

  return {
    provider: 'anthropic',
    model: response.model ?? model,
    text: extractAnthropicText(response),
    usage: response.usage,
    fallbackUsed: false,
  };
}

export async function callLmStudio(prompt, overrides = {}) {
  const config = getRuntimeConfig();
  const model = overrides.model ?? config.lmstudio.model;
  const systemPrompt = overrides.systemPrompt ?? config.systemPrompt;
  const messages = [];
  if (systemPrompt) {
    messages.push({ role: 'system', content: systemPrompt });
  }
  messages.push({ role: 'user', content: prompt });
  const response = await fetch(
    buildLmStudioUrl(config.lmstudio.baseURL, '/chat/completions'),
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${config.lmstudio.apiKey}`,
      },
      body: JSON.stringify({
        model,
        messages,
        temperature: overrides.temperature ?? 0.2,
        max_tokens: overrides.maxTokens ?? 1024,
        stream: false,
      }),
    },
  );

  if (!response.ok) {
    const details = await response.text();
    const error = new Error(`LM Studio respondió ${response.status}: ${details}`);
    error.code = 'LMSTUDIO_REQUEST_FAILED';
    throw error;
  }

  const data = await response.json();
  return {
    provider: 'lmstudio',
    model: data.model ?? model,
    text: data.choices?.[0]?.message?.content?.trim() ?? '',
    usage: data.usage ?? null,
    fallbackUsed: false,
  };
}

export async function generateResponse({
  prompt,
  provider,
  model,
  systemPrompt,
  temperature,
  maxTokens,
} = {}) {
  const config = getRuntimeConfig();
  const effectiveProvider = provider ?? config.provider;
  const effectiveSystemPrompt = systemPrompt ?? config.systemPrompt;

  if (!prompt?.trim()) {
    const error = new Error('Debes enviar un prompt no vacío.');
    error.code = 'PROMPT_REQUIRED';
    throw error;
  }

  if (effectiveProvider === 'anthropic') {
    return callAnthropic(prompt, {
      model,
      systemPrompt: effectiveSystemPrompt,
      temperature,
      maxTokens,
    });
  }

  if (effectiveProvider === 'lmstudio') {
    return callLmStudio(prompt, {
      model,
      systemPrompt: effectiveSystemPrompt,
      temperature,
      maxTokens,
    });
  }

  try {
    return await callLmStudio(prompt, {
      model,
      systemPrompt: effectiveSystemPrompt,
      temperature,
      maxTokens,
    });
  } catch (localError) {
    if (!config.anthropic.apiKey) {
      localError.message = `${localError.message} | Anthropic cloud no está disponible porque falta la clave.`;
      throw localError;
    }

    const cloudResult = await callAnthropic(prompt, {
      model,
      systemPrompt: effectiveSystemPrompt,
      temperature,
      maxTokens,
    });

    return {
      ...cloudResult,
      fallbackUsed: true,
      fallbackReason: localError.message,
    };
  }
}

export async function getHealth() {
  const publicConfig = getPublicConfig();
  const health = {
    ok: true,
    providerMode: publicConfig.provider,
    lmstudio: {
      configured: publicConfig.lmstudio.configured,
      reachable: false,
      error: null,
    },
    anthropic: {
      enabled: publicConfig.anthropic.enabled,
      keySource: publicConfig.anthropic.keySource,
    },
  };

  try {
    const probe = await probeLmStudio();
    health.lmstudio = {
      ...health.lmstudio,
      reachable: true,
      modelCount: probe.modelCount,
    };
  } catch (error) {
    health.ok = false;
    health.lmstudio.error = error.message;
  }

  return health;
}
