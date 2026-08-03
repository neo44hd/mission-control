# LM Studio Repair & Model Configuration Guide

## ✅ Current Status

- **LM Studio Version**: 0.4.20+1 (Latest)
- **API Server**: ✓ Running on http://localhost:1234
- **Total Models Registered**: 8
- **Environment**: Correctly configured (UTF-8, OLLAMA_NUM_PARALLEL=1)

## ⚠️ Issue Found

Two GGUF files are **corrupted**:
- `qwen2.5-14b-instruct-q4_k_m-00001-of-00003.gguf` (3.7 GB)
- `qwen2.5-14b-instruct-q4_k_m-00002-of-00003.gguf` (2.8 GB)

### Cause
Likely incomplete download or partial file transfer. The files exist but lack valid GGUF magic bytes.

## 🔧 Solution: Delete Corrupted Files

```bash
# Backup first (optional)
mkdir -p ~/.ollama/corrupted-backup
mv ~/.ollama/models/qwen2.5-14b-instruct-q4_k_m-*.gguf ~/.ollama/corrupted-backup/

# Verify deletion
ls -lh ~/.ollama/models/*.gguf
```

## ✨ Recommended Models to Download

These are well-tested models that work perfectly with your setup:

### 1. **Llama 3.1 8B** (Best for coding)
- **Tier**: Fast & reliable
- **Download in LM Studio**:
  1. Click "Search" → Models
  2. Search: `llama2` or `meta-llama`
  3. Download: "Llama 3.1 8B" (Q4_K_M recommended)
- **Size**: ~4.7 GB
- **Speed**: Fast on Apple Silicon
- **Best for**: Code generation, general tasks

### 2. **Qwen 2.5 7B Coder** (Already registered!)
- **Tier**: Balanced coding
- **Status**: ✓ Already in your manifest (qwen2.5-coder/7b)
- **Action needed**: Download the Q4_K_M GGUF version
- **Size**: ~3.8 GB
- **Best for**: Code completion, technical explanations

### 3. **Mistral 7B** (Lightweight)
- **Tier**: Fast, English-focused
- **Download in LM Studio**:
  1. Search: `mistral`
  2. Download: "Mistral 7B" (Q4_K_M)
- **Size**: ~4.4 GB
- **Best for**: Quick responses, JSON generation

### 4. **Phi 3.5 Mini** (Ultra-lightweight)
- **Tier**: Minimal (~2 GB)
- **Best for**: Mobile testing, low-resource scenarios

### 5. **Qwen 3.5** (New & powerful)
- **Status**: ✓ Already in your manifest (qwen3.5/latest)
- **Action needed**: Download when ready
- **Best for**: Recent knowledge, multi-language

## 🚀 Quick Start After Fixing

### Step 1: Delete Corrupted Files
```bash
rm -f ~/.ollama/models/qwen2.5-14b-instruct-q4_k_m-*.gguf
```

### Step 2: Restart LM Studio
```bash
# Kill any existing instance
killall -9 "LM Studio" 2>/dev/null

# Reopen from Applications
open /Applications/LM\ Studio.app
```

### Step 3: Download a Test Model
In LM Studio → Search → "Llama 3.1 8B" → Download (Q4_K_M)

### Step 4: Test the API
```bash
# Once model is loaded:
curl -X POST http://localhost:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.1",
    "messages": [{"role": "user", "content": "Hello, how are you?"}],
    "temperature": 0.7
  }'
```

## 📊 All Your Current Models (Status)

| Model | Status | Action |
|-------|--------|--------|
| Llama 3.2 3B | ✓ Registered | Try downloading |
| Llama 3.2 Vision 11B | ✓ Registered | Try downloading |
| Qwen 2.5 7B | ✓ Registered | Try downloading |
| Qwen 2.5 Coder 7B | ✓ Registered | Try downloading |
| Qwen 3.5 | ✓ Registered | Try downloading |
| Qwen 2.5 14B | ✗ **CORRUPTED** | **DELETE** |
| Pixtral 12B | ✓ Registered | Try downloading |
| GLM OCR | ✓ Registered | (Vision model) |
| Nomic Embed Text | ✓ Registered | (Embedding only) |

## 🛠️ Environment Configuration

Your environment is **correctly set**:
```bash
export OLLAMA_NUM_PARALLEL=1          # ✓ Correct (your rule)
export OLLAMA_MAX_LOADED_MODELS=1     # ✓ Correct (your rule)
export LANG=en_US.UTF-8               # ✓ Just added
export LC_ALL=en_US.UTF-8             # ✓ Just added
```

Source your updated config:
```bash
source ~/.zshrc
```

## 🆘 If Problems Persist

### Test without LM Studio API
Use Ollama directly (if installed):
```bash
ollama run llama2
```

### Check LM Studio Logs
```bash
tail -f ~/Library/Application\ Support/LM\ Studio/Session\ Storage/*/log
```

### Full Reset (Nuclear Option)
```bash
# 1. Backup current config
cp -r ~/.ollama ~/.ollama.backup.$(date +%Y%m%d)

# 2. Clear everything except manifests
rm -rf ~/.ollama/cache/*
rm -rf ~/.ollama/models/blobs/*

# 3. Reinstall LM Studio
# Download from: https://lmstudio.ai

# 4. Start fresh with one model
```

## 🎯 Recommended Download Order

For your setup (MacOS, llama3.2 3B local model, OpenClaw/LiteLLM gateway):

1. **First**: Llama 3.1 8B (test core functionality)
2. **Second**: Qwen 2.5 7B Coder (for coding tasks)
3. **Third**: Add others as needed

Total recommended initial download: ~8-10 GB (manageable on macOS)

## 📝 Character Encoding Fix

The original message with garbled characters was likely from the corrupted Qwen model trying to generate. Once you:
1. Delete the corrupted files
2. Download a clean, official model (Llama, Mistral, Qwen official)
3. Restart LM Studio

You should see **clean, proper UTF-8 output**.

---

**Need help?** Check this guide's **"If Problems Persist"** section.
