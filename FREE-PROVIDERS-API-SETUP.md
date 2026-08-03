# 🦇 SYNK-IA FREE PROVIDERS - API KEY SETUP GUIDE

**Status**: Ready for Integration  
**Total Providers**: 11 Free LLM APIs  
**Total Models**: 30+ (+ access to 400+ more)  
**Date**: 2026-07-09

---

## ⚡ QUICK START - API KEYS NEEDED (10 min signup)

```bash
# Copy these into your .env or export them in terminal:

export GROQ_API_KEY="your_key_here"
export TOGETHER_API_KEY="your_key_here"
export HUGGINGFACE_API_KEY="your_key_here"
export BAZAARLINK_API_KEY="your_key_here"
export ZEROLIMIT_API_KEY="your_key_here"
export FREEAI_API_KEY="your_key_here"
export COMPLETIONS_API_KEY="your_key_here"
export LLMKIWI_API_KEY="your_key_here"
export REQUESTY_API_KEY="your_key_here"
export AINATIVE_API_KEY="your_key_here"
export ZEROCOST_API_KEY="your_key_here"
```

---

## 1️⃣ GROQ (Ultra Fast - 100k tokens/month)

**Speed**: ⚡⚡⚡ (<1ms latency)  
**Models**: Llama 70B, Llama 8B, Mixtral 8x7B  
**Cost**: FREE (100k tokens/month)

### Signup Steps:
1. Go to: https://console.groq.com
2. Click "Sign up" → Use email or Google/GitHub
3. Verify email (instant)
4. Dashboard → API Keys → Create API Key
5. Copy the key to `GROQ_API_KEY`

**Rate Limits**: 
- 30k tokens/min (during burst)
- 100k tokens/month total

**API Endpoint** (auto in litellm):
```
https://api.groq.com/openai/v1
```

---

## 2️⃣ TOGETHER.AI (Fast + Multiple Models)

**Speed**: ⚡⚡⚡ (Very fast)  
**Models**: Llama 70B, Qwen 72B, Mistral 7B  
**Cost**: FREE (generous limits)

### Signup Steps:
1. Go to: https://www.together.ai
2. Click "Get Started" → Sign up with email/Google
3. Verify email
4. Settings → API Keys → Create new key
5. Copy to `TOGETHER_API_KEY`

**Rate Limits**: Generous (no official limits published)

**API Endpoint**:
```
https://api.together.xyz/v1
```

---

## 3️⃣ HUGGING FACE (Flexible Inference)

**Speed**: ⚡⚡ (Good)  
**Models**: Llama 70B, Mistral 7B  
**Cost**: FREE (limited but available)

### Signup Steps:
1. Go to: https://huggingface.co/settings/tokens
2. Click "New token" → Sign up if needed
3. Name: "synkia-api"
4. Type: "Read" (sufficient)
5. Copy token to `HUGGINGFACE_API_KEY`

**Rate Limits**: Limited (free tier)

**API Endpoint**:
```
https://api-inference.huggingface.co/v1
```

---

## 4️⃣ BAZAARLINK (Auto Router - Unlimited FREE)

**Speed**: ⚡⚡ (Depends on routed model)  
**Models**: auto:free (intelligent routing)  
**Cost**: FREE UNLIMITED

### Signup Steps:
1. Go to: https://bazaarlink.ai/keys
2. Click "Sign up" (instant, no email required)
3. Auto-generates API key immediately
4. Copy to `BAZAARLINK_API_KEY`

**Key Features**:
- ✅ Auto-selects best free model
- ✅ Intelligent fallback
- ✅ No credit card ever
- ✅ Unlimited requests

**API Endpoint**:
```
https://api.bazaarlink.ai/v1
```

---

## 5️⃣ ZEROLIMIT AI (Smart Routing with ELO Scores)

**Speed**: ⚡⚡⚡ (Top models daily)  
**Models**: ZeroOptimize™ (changes every 24h)  
**Cost**: FREE (2,000 calls/day)

### Current Top Models (24h):
1. Qwen 3-235B (1342 ELO) ⭐
2. Llama 4 Scout (1298 ELO)
3. DeepSeek R1 (1287 ELO)
4. GPT-OSS 120B (1271 ELO)

### Signup Steps:
1. Go to: https://www.zerolimitai.com
2. Click "Get Started"
3. Sign up with email (2 min)
4. API Keys → Create new key
5. Copy to `ZEROLIMIT_API_KEY`

**Rate Limits**: 2,000 calls/day (resets daily)

**API Endpoint**:
```
https://api.zerolimitai.com/v1
```

**Special**: Models rotate daily based on ELO benchmarks!

---

## 6️⃣ FREE.AI (Multimodal - 400+ models)

**Speed**: ⚡⚡ (Good)  
**Models**: Qwen 7B (+ access to 400+ total)  
**Cost**: FREE (30k tokens/day)

### Features:
- 📝 Text: Qwen, Llama, Mistral
- 🖼️ Image: FLUX, SDXL
- 🎬 Video: CogVideoX
- 🎵 Audio: Kokoro TTS, Whisper STT
- 🌐 Translation: 450+ languages

### Signup Steps:
1. Go to: https://free.ai
2. Click "Sign up" → Email + password (2 min)
3. Dashboard → API Keys → Generate
4. Copy to `FREEAI_API_KEY`

**Rate Limits**: 30,000 tokens/day

**API Endpoint**:
```
https://api.free.ai/v1
```

---

## 7️⃣ COMPLETIONS.ME (Premium Models FREE! ⭐)

**Speed**: ⚡⚡⚡ (Very fast)  
**Models**: Claude Opus 4.6, GPT-5.2, Gemini 3.1 Pro  
**Cost**: COMPLETELY FREE - UNLIMITED!

### ⚠️ SPECIAL: NO RATE LIMITS - COMPLETELY UNRESTRICTED

### Signup Steps:
1. Go to: https://completions.me
2. Click "Get Started" → Instant signup (NO EMAIL REQUIRED!)
3. Auto-generates API key immediately
4. Copy to `COMPLETIONS_API_KEY`
5. Start using Claude/GPT-5/Gemini instantly

**Supported Models**:
- `claude-opus-4.6` (FREE)
- `gpt-5.2` (FREE)
- `gemini-3.1-pro` (FREE)

**Rate Limits**: NONE - Completely unlimited

**API Endpoint**:
```
https://api.completions.me/v1
```

**Why This Works**: Community-funded model proxy

---

## 8️⃣ LLM.KIWI (Edge-Delivered)

**Speed**: ⚡⚡⚡ (<2ms latency)  
**Models**: auto (intelligent routing)  
**Cost**: FREE (generous)

### Signup Steps:
1. Go to: https://llm.kiwi/login
2. Sign up with email (instant)
3. Dashboard → API Keys
4. Create new key
5. Copy to `LLMKIWI_API_KEY`

**Key Features**:
- 300+ edge locations worldwide
- Sub-50ms routing overhead
- Zero cold starts
- Smart auto-routing

**Rate Limits**: Generous (free tier)

**API Endpoint**:
```
https://api.llm.kiwi/v1
```

---

## 9️⃣ REQUESTY (Coding-Optimized)

**Speed**: ⚡⚡⚡ (Optimized for code)  
**Models**: auto (routing)  
**Cost**: FREE (200 requests/day)

### Perfect for:
- Claude Code integration
- Cursor AI integration
- Cline integration
- Roo Code integration

### Signup Steps:
1. Go to: https://www.requesty.ai
2. Click "Sign up" (email + password, 2 min)
3. Settings → API Keys
4. Create new API key
5. Copy to `REQUESTY_API_KEY`

**Rate Limits**: 200 requests/day (plenty for development)

**API Endpoint**:
```
https://api.requesty.ai/v1
```

**Features**:
- ✅ Built-in routing
- ✅ Caching included
- ✅ EU data residency
- ✅ Real-time analytics

---

## 🔟 AINATIVE STUDIO (Academic-Friendly)

**Speed**: ⚡⚡⚡ (Very fast)  
**Models**: 147+ models available, all free tier  
**Cost**: FREE (10M tokens/month, 60 RPM)

### Featured Models:
- Llama 3.3 70B (Instruct)
- DeepSeek R1 (Best reasoning)
- Qwen 72B
- Mistral 8x22B

### Signup Steps:
1. Go to: https://api.ainative.studio
2. Click "Get Started"
3. Sign up (email, 2 min)
4. API Dashboard → Generate API Key
5. Copy to `AINATIVE_API_KEY`

**Rate Limits**: 
- 10M tokens/month
- 60 requests/min

**API Endpoint**:
```
https://api.ainative.studio/v1
```

**Special**: Best for research/education with 147+ models

---

## 1️⃣1️⃣ ZEROCOST ROUTER (Smart Failover)

**Speed**: ⚡⚡⚡ (With failover)  
**Models**: Llama 70B (with auto-failover)  
**Cost**: FREE (1,000 requests/month)

### Signup Steps:
1. Go to: https://zerocost-lp.vercel.app
2. Click "Get API Key"
3. Sign up with GitHub or email (instant)
4. Copy key to `ZEROCOST_API_KEY`

**Features**:
- AES-256-GCM encryption
- Auto-failover (Groq → Cerebras → HuggingFace)
- Edge-native (Cloudflare Workers)
- Zero startup time

**Rate Limits**: 1,000 requests/month

**API Endpoint**:
```
https://api.zerocost.ai/v1
```

---

## ✅ SETUP CHECKLIST

- [ ] Get GROQ_API_KEY from https://console.groq.com
- [ ] Get TOGETHER_API_KEY from https://www.together.ai
- [ ] Get HUGGINGFACE_API_KEY from https://huggingface.co/settings/tokens
- [ ] Get BAZAARLINK_API_KEY from https://bazaarlink.ai/keys
- [ ] Get ZEROLIMIT_API_KEY from https://www.zerolimitai.com
- [ ] Get FREEAI_API_KEY from https://free.ai
- [ ] Get COMPLETIONS_API_KEY from https://completions.me
- [ ] Get LLMKIWI_API_KEY from https://llm.kiwi/login
- [ ] Get REQUESTY_API_KEY from https://www.requesty.ai
- [ ] Get AINATIVE_API_KEY from https://api.ainative.studio
- [ ] Get ZEROCOST_API_KEY from https://zerocost-lp.vercel.app

**Total Time**: ~15 minutes for all 11 keys

---

## 🔧 ENVIRONMENT VARIABLES

Add to `~/.zshrc` or `~/.bashrc`:

```bash
# FREE PROVIDERS API KEYS
export GROQ_API_KEY="gsk_..."
export TOGETHER_API_KEY="..."
export HUGGINGFACE_API_KEY="hf_..."
export BAZAARLINK_API_KEY="..."
export ZEROLIMIT_API_KEY="..."
export FREEAI_API_KEY="..."
export COMPLETIONS_API_KEY="..."
export LLMKIWI_API_KEY="..."
export REQUESTY_API_KEY="..."
export AINATIVE_API_KEY="..."
export ZEROCOST_API_KEY="..."
```

Then reload:
```bash
source ~/.zshrc
```

---

## 📊 COMPARISON TABLE

| Provider | Speed | Models | Rate Limit | Signup |
|----------|-------|--------|-----------|--------|
| Groq | ⚡⚡⚡ | 3 | 100k tok/mo | 2 min |
| Together.ai | ⚡⚡⚡ | 3 | Generous | 2 min |
| HuggingFace | ⚡⚡ | 2 | Limited | 2 min |
| BazaarLink | ⚡⚡ | Auto | Unlimited | 1 min |
| ZeroLimit | ⚡⚡⚡ | Auto* | 2k calls/day | 2 min |
| Free.ai | ⚡⚡ | 400+ | 30k tok/day | 2 min |
| Completions.me | ⚡⚡⚡ | 3 | UNLIMITED | 1 min |
| LLM.Kiwi | ⚡⚡⚡ | Auto | Generous | 2 min |
| Requesty | ⚡⚡⚡ | Auto | 200 req/day | 2 min |
| AINative | ⚡⚡⚡ | 147+ | 10M tok/mo | 2 min |
| zerocost | ⚡⚡⚡ | 1 | 1k req/mo | 1 min |

*Changes daily based on ELO scores

---

## 🎯 BEST FOR...

**Ultra Speed**: Groq, Completions.me  
**Most Models**: AINative (147+), Free.ai (400+)  
**No Limits**: Completions.me (unlimited), BazaarLink (unlimited)  
**Coding**: Requesty, Completions.me  
**Research**: AINative Studio  
**Reasoning**: AINative (DeepSeek R1), ZeroLimit AI  
**Fallback**: ZeroCost Router  

---

## 🚀 NEXT STEPS

1. **Get all 11 API keys** (follow links above)
2. **Export environment variables** in your shell
3. **Test litellm** with each provider:
   ```bash
   litellm --model groq/llama-70b --prompt "Hello"
   litellm --model together_ai/llama-70b-instruct-turbo --prompt "Hello"
   ```
4. **Monitor usage** via each provider's dashboard
5. **Setup fallback chains** in litellm config (already configured)

---

## 📝 NOTES

- All providers are **100% FREE** in their tier
- No credit card required for any signup
- Most signups take <2 minutes
- All support OpenAI-compatible API format
- litellm config already has all models configured
- Just need to add the API keys!

---

**Status**: 🟢 Ready for Production  
**Last Updated**: 2026-07-09  
**Total Models Available**: 100+ (across all providers)
