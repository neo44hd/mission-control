const providerMode = document.querySelector('#providerMode');
const lmstudioStatus = document.querySelector('#lmstudioStatus');
const lmstudioMeta = document.querySelector('#lmstudioMeta');
const anthropicStatus = document.querySelector('#anthropicStatus');
const anthropicMeta = document.querySelector('#anthropicMeta');
const responseOutput = document.querySelector('#responseOutput');
const responseProvider = document.querySelector('#responseProvider');
const responseModel = document.querySelector('#responseModel');
const responseFallback = document.querySelector('#responseFallback');
const providerSelect = document.querySelector('#providerSelect');
const systemPromptInput = document.querySelector('#systemPromptInput');
const promptInput = document.querySelector('#promptInput');
const sendBtn = document.querySelector('#sendBtn');
const refreshBtn = document.querySelector('#refreshBtn');

async function loadStatus() {
  const [healthResponse, configResponse] = await Promise.all([
    fetch('/api/health'),
    fetch('/api/config'),
  ]);

  const health = await healthResponse.json();
  const config = await configResponse.json();

  providerMode.textContent = config.provider;
  providerSelect.value = config.provider;
  systemPromptInput.value = config.systemPrompt ?? '';

  lmstudioStatus.textContent = health.lmstudio.reachable ? 'Conectado' : 'No disponible';
  lmstudioMeta.textContent = health.lmstudio.reachable
    ? `${config.lmstudio.model} · ${health.lmstudio.modelCount ?? 0} modelos visibles`
    : health.lmstudio.error ?? config.lmstudio.baseURL;

  anthropicStatus.textContent = config.anthropic.enabled ? 'Configurado' : 'Desactivado';
  anthropicMeta.textContent = `Modelo: ${config.anthropic.model} · clave: ${config.anthropic.keySource}`;
}

async function sendPrompt() {
  sendBtn.disabled = true;
  responseOutput.textContent = 'Consultando...';

  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        provider: providerSelect.value,
        systemPrompt: systemPromptInput.value,
        prompt: promptInput.value,
      }),
    });

    const data = await response.json();

    if (!response.ok || !data.ok) {
      throw new Error(data.error ?? 'La petición falló.');
    }

    responseProvider.textContent = `Proveedor: ${data.provider}`;
    responseModel.textContent = `Modelo: ${data.model}`;
    responseFallback.textContent = `Fallback: ${data.fallbackUsed ? 'sí' : 'no'}`;
    responseOutput.textContent = data.text || '(sin texto)';
  } catch (error) {
    responseProvider.textContent = 'Proveedor: error';
    responseModel.textContent = 'Modelo: -';
    responseFallback.textContent = 'Fallback: -';
    responseOutput.textContent = error.message;
  } finally {
    sendBtn.disabled = false;
  }
}

async function loadMemoryStats() {
  try {
    const [totalRes, typeRes] = await Promise.all([
      fetch('/api/memory/stats'),
      fetch('/api/memory/stats?by=doc_type'),
    ]);
    const total = totalRes[0]?.total ?? 0;
    document.querySelector('#memoryStatus').textContent = total.toLocaleString('es') + ' docs';
    document.querySelector('#memoryMeta').textContent = 'Memoria retroactiva — 100% embeddings';

    const types = {};
    (typeRes || []).forEach(r => { types[r.key] = r.count; });
    const bar = document.querySelector('#memoryBar');
    const topTypes = Object.entries(types).sort((a,b) => b[1] - a[1]).slice(0, 5);
    bar.innerHTML = topTypes.map(([k,v]) => `<span class="memory-tag">${k}: ${v.toLocaleString('es')}</span>`).join('');
  } catch (e) {
    document.querySelector('#memoryStatus').textContent = 'Offline';
    document.querySelector('#memoryMeta').textContent = 'sinkMAIND no disponible';
  }
}

refreshBtn.addEventListener('click', () => { loadStatus(); loadMemoryStats(); });
sendBtn.addEventListener('click', sendPrompt);

loadStatus().catch((error) => {
  responseOutput.textContent = `No se pudo cargar el estado inicial: ${error.message}`;
});

loadMemoryStats();
