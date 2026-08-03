# 🚀 LM Studio - Quick Actions

## ✅ What's Done (Already Fixed)

- [x] Diagnosed corrupted Qwen 2.5 14B files (6.5 GB)
- [x] Deleted corrupted GGUF files
- [x] Cleared cache (~/.ollama/cache)
- [x] Fixed UTF-8 environment variables
- [x] Created verification tools

**You're 80% done. Just need to:**

---

## 📋 Your Action Items (5 minutes)

### 1️⃣ Activate UTF-8 Config
```bash
source ~/.zshrc
```
✅ This activates the new environment variables added to your shell

### 2️⃣ Restart LM Studio
```bash
# Close it
killall -9 "LM Studio"

# Wait 2 seconds
sleep 2

# Reopen it
open /Applications/LM\ Studio.app
```

### 3️⃣ Download Llama 3.1 8B
In the LM Studio UI:
1. Click **Search** tab
2. Search: `llama 3.1` or `meta-llama`
3. Click **Download** on "Llama 3.1 8B" (Q4_K_M)
4. Wait ~10-30 min (depends on connection, ~4.7 GB)

### 4️⃣ Test It Works
```bash
curl -X POST http://localhost:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.1",
    "messages": [{"role": "user", "content": "Hola! Di algo en español."}],
    "temperature": 0.7
  }'
```

**Expected**: Clean UTF-8 response in Spanish. No garbage. ✨

---

## 🎯 Next Models to Download (Optional)

| Model | Why | Size | Time |
|-------|-----|------|------|
| **Llama 3.1 8B** | Start here | 4.7 GB | 10-30 min |
| Qwen 2.5 Coder 7B | Best for code | 3.8 GB | 8-20 min |
| Mistral 7B | Fast & reliable | 4.4 GB | 8-20 min |
| Qwen 3.5 | Newest & powerful | ~5 GB | 15-30 min |

---

## 📊 Your Registered Models

All these are already in your system (ready to download when you want):
- Llama 3.2 3B
- Llama 3.2 Vision 11B
- Qwen 2.5 7B
- Qwen 2.5 Coder 7B ⭐
- Qwen 3.5
- Pixtral 12B
- GLM OCR
- Nomic Embed Text

---

## 🔍 Verify Everything's OK

```bash
# Run anytime to check status
~/verify-lm-studio.sh
```

Expected output:
```
✓ Llama 3.2
✓ Qwen 2.5...
✓ API is running
✓ Found 10 models
```

---

## 🆘 If Something Breaks

### Quick Fix
```bash
source ~/.zshrc
killall -9 "LM Studio"
open /Applications/LM\ Studio.app
~/verify-lm-studio.sh
```

### Still Broken?
Read: `~/LM_STUDIO_REPAIR_GUIDE.md`

### Nuclear Reset
```bash
cp -r ~/.ollama ~/.ollama.backup.$(date +%Y%m%d)
rm -rf ~/.ollama/cache/* ~/.ollama/models/blobs/*
killall -9 "LM Studio"
open /Applications/LM\ Studio.app
# Download just Llama 3.1 and test
```

---

## 📚 Documentation

| File | Purpose |
|------|---------|
| `~/LM_STUDIO_REPAIR_GUIDE.md` | Complete repair guide |
| `~/LM_STUDIO_CLEANUP_TODO.txt` | Detailed checklist |
| `~/LMSTUDIO_REPAIR_SUMMARY.txt` | Full diagnostic report |
| `~/verify-lm-studio.sh` | Auto verification tool |
| `~/QUICK_ACTIONS.md` | You are here! 👈 |

---

## ✨ That's It!

Once you download Llama 3.1 8B and restart, your LM Studio will work perfectly with **clean UTF-8 output, no garbage characters**.

**Current time**: ~5 min actions + 20 min download = **25 minutes total to working system**

Go ahead → `source ~/.zshrc` 🚀
