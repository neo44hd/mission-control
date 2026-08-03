# 🧪 LM Studio Model Testing Guide

He creado **3 herramientas de testing** para que pruebes todos tus modelos, especialmente los experimentales (merges no oficiales).

---

## 📁 Scripts Disponibles

### 1. `test-experimental-models.sh` ⭐ RECOMENDADO PARA TI
**Prueba específicamente los modelos no oficiales/experimentales**

```bash
chmod +x ~/test-experimental-models.sh
~/test-experimental-models.sh
```

**Qué prueba:**
- ✓ Qwythos 9B Claude Mythos 5
- ✓ Qwen 3.6 27B Claude Mythos Distilled
- ✓ Ternary Bonsai 27B (2-bit)
- ✓ GPT-OSS-20B

**Cada modelo se prueba con 6 prompts diferentes:**
1. English technical (quantum computing)
2. Spanish technical (machine learning)
3. Code generation (Python function)
4. Spanish creative (joke)
5. Simple factual (capital)
6. Spanish creative (poem)

**Qué esperar:**
- Cada test: ~1-3 minutos por modelo
- Tiempo total: ~30-60 minutos (depende del tamaño)
- Resultado: Score 0-100, conteo de caracteres corruptos, velocidad

---

### 2. `interactive-test-models.sh`
**Interfaz interactiva para testing manual y comparación**

```bash
chmod +x ~/interactive-test-models.sh
~/interactive-test-models.sh
```

**Comandos disponibles:**
```
list      - Listar todos los modelos disponibles
test <model> - Probar un modelo específico (ej: test nemotron)
compare   - Comparar múltiples modelos con el mismo prompt
quick     - Test rápido en todos los modelos
prompt    - Establecer prompt personalizado
help      - Mostrar menu
exit      - Salir
```

**Ejemplo de uso interactivo:**
```
lm-test> list
lm-test> test qwythos
lm-test> compare
Enter test prompt: Hola, explica el machine learning en español
lm-test> exit
```

---

### 3. `test-lm-studio-models.sh`
**Test automático de todos los modelos disponibles**

```bash
chmod +x ~/test-lm-studio-models.sh
~/test-lm-studio-models.sh
```

**Qué hace:**
- Detecta automáticamente todos los modelos en LM Studio
- Prueba cada uno con el mismo prompt
- Genera reporte de resultados

---

## 🚀 Cómo Empezar

### Prerequisito
**LM Studio debe estar corriendo:**
```bash
open /Applications/LM\ Studio.app
```

Espera a que aparezca "Server running on localhost:1234" antes de correr los tests.

### Opción 1: Testing Experimentales (RECOMENDADO PARA TI)

```bash
# Paso 1: Asegúrate que LM Studio está corriendo
open /Applications/LM\ Studio.app

# Paso 2: Espera ~30-60 segundos (a que cargue completamente)

# Paso 3: En otra terminal, corre el testing
~/test-experimental-models.sh
```

**El script te mostrará:**
- Cada test con estado (CLEAN, OK, CORRUPTED, TIMEOUT)
- Muestra de la respuesta (primeros 100 caracteres)
- Score final: 0-100
- Recomendación

### Opción 2: Testing Manual Interactivo

```bash
~/interactive-test-models.sh

# Dentro de la interfaz:
lm-test> list              # Ver modelos
lm-test> test qwythos      # Probar uno específico
lm-test> compare           # Comparar varios
lm-test> exit
```

### Opción 3: Testing Todos los Modelos

```bash
~/test-lm-studio-models.sh
```

---

## 📊 Interpretando Resultados

### Score/Quality
- **80-100**: ✅ EXCELLENT - Usa sin problemas
- **60-79**: ⚠️ GOOD - Funciona pero con algunas limitaciones
- **40-59**: ❌ POOR - Funciona pero con muchos errores
- **0-39**: ❌ BAD - No recomendado

### Caracteres Corruptos
- **0**: ✅ Perfecto, salida limpia
- **1-5**: ⚠️ Menor, generalmente aceptable
- **6-10**: ⚠️ Moderado, considera alternativas
- **11+**: ❌ Severo, no usar

### Response Time
- **< 2000ms**: ⚡ Muy rápido
- **2000-5000ms**: ✅ Rápido
- **5000-10000ms**: ⚠️ Aceptable
- **> 10000ms**: ❌ Lento

---

## 🎯 Qué Esperar de Cada Modelo

### Qwythos 9B Claude Mythos 5
**Histórico:**
- Fue el que causó tu mensaje garbled inicial
- Merge no oficial (Claude + Qwen)
- Cuantización agresiva (oQ6)

**En testing:**
- Probablemente: Score bajo (< 40%)
- Corrupted outputs esperados
- Tiempo variable

**Veredicto esperado:** ❌ No recomendado

---

### Qwen 3.6 27B Claude Mythos Distilled
**Histórico:**
- Similar al Qwythos
- Merge experimental
- 27B muy grande

**En testing:**
- Probablemente: Score bajo-medio (20-50%)
- Pueden haber caracteres corruptos
- Tiempo lento (requiere 16 GB)

**Veredicto esperado:** ⚠️ Marginal

---

### Ternary Bonsai 27B (2-bit)
**Características:**
- Cuantización extrema (2-bit ternary)
- Muy agresiva
- Solo para research

**En testing:**
- Probablemente: Score muy bajo (< 30%)
- Alta probabilidad de garbage
- Hallucinations posibles

**Veredicto esperado:** ❌ No recomendado

---

### GPT-OSS-20B
**Características:**
- Open-source (no oficial)
- 20B parámetros
- Cuantización experimental (MXFP4-Q8)

**En testing:**
- Probabilidad: Score medio (40-70%)
- Menos garbage que Qwythos
- Tiempo moderado

**Veredicto esperado:** ⚠️ Depende de resultados

---

## 📝 Ejemplo de Salida

```
════════════════════════════════════════════════════════════════
Testing: Qwythos 9B Claude Mythos 5 MLX oQ6 (7.9 GB)
════════════════════════════════════════════════════════════════

  Test 1/6: CLEAN (245ms)
            Sample: "Quantum computing uses quantum bits (qubits) that can be both 0..."
  
  Test 2/6: ✓ CLEAN (312ms)
            Sample: "Machine learning es un subcampo de la inteligencia artificial..."
  
  Test 3/6: CORRUPTED (15 bad chars)
            Sample: "def factorial(n):␤␊    if n == 1: return 1␤␊    else:␤..."
  
  Test 4/6: OK (minor) (8 chars, 289ms)
            Sample: "Aquí va un chiste..."
  
  Test 5/6: ✓ CLEAN (156ms)
            Sample: "The capital of France is Paris..."
  
  Test 6/6: TIMEOUT
  
RESULTS FOR: Qwythos 9B Claude Mythos 5 MLX oQ6 (7.9 GB)
  Passed (clean):    4/6
  Corrupted:         1/6
  Failed/Timeout:    1/6
  Avg Response Time: 267ms
  Total Garbage:     23 chars
  Quality Score:     67/100 (GOOD)

═══════════════════════════════════════════════════════════════════
COMPARISON RESULTS
═══════════════════════════════════════════════════════════════════

Qwythos 9B Claude Mythos 5          Score: 67/100 | Pass: 4/6 | Corrupt: 1 | Time: 267ms
Ternary Bonsai 27B 2-bit             Score: 23/100 | Pass: 1/6 | Corrupt: 3 | Time: 1420ms
Qwen 3.6 27B Mythos Distilled Q4     Score: 42/100 | Pass: 2/6 | Corrupt: 2 | Time: 5230ms
GPT-OSS-20B MXFP4-Q8                 Score: 58/100 | Pass: 3/6 | Corrupt: 1 | Time: 3456ms

Recommendation:

⚠️  Qwythos 9B Claude Mythos 5 has acceptable performance (67/100)
    Works but consider official models for critical tasks
```

---

## 💡 Recomendaciones

### Si Testing muestra que Experimentales FUNCIONAN BIEN:
```
✅ Puedes mantenerlos y usarlos
⚠️  Pero considera que no tienen soporte oficial
❌ Evita para tareas críticas
```

### Si Testing muestra que Experimentales FALLAN:
```
❌ Elimina los que fallen
rm -rf /Volumes/Disco\ local/lmstudio/models/xunkutech-ai/
rm -f /Volumes/Disco\ local/lmstudio/models/chatqaq/*.gguf
rm -f /Volumes/Disco\ local/lmstudio/models/prism-ml/*.safetensors
```

### Luego:
```
✅ Usa modelos oficiales recomendados:
   - NVIDIA Nemotron-3-Nano-4B (mejor general)
   - Phi-4-reasoning-plus (mejor para código)
   - LFM2.5-1.2B (mejor para testing rápido)
```

---

## 🐛 Troubleshooting

### "API not responding"
```bash
# LM Studio no está corriendo
open /Applications/LM\ Studio.app

# Espera 30 segundos a que cargue
# Intenta de nuevo
```

### "No models found"
```bash
# LM Studio no tiene modelos cargados
# En LM Studio UI: Click en Search → Download un modelo

# O espera a que cargue automáticamente los existentes
```

### "Permission denied"
```bash
chmod +x ~/test-experimental-models.sh
chmod +x ~/test-lm-studio-models.sh
chmod +x ~/interactive-test-models.sh
```

### Script se cuelga
```bash
# Presiona Ctrl+C
# Probablemente un modelo se colgó
# Los resultados hasta ese punto se guardaron en /tmp/
```

---

## 📊 Resultados Guardados

Los resultados se guardan automáticamente en:
- `/tmp/experimental_test_results_*.txt` (experimental models)
- `/tmp/lm_studio_test_results.txt` (todos los modelos)
- `/tmp/lm_compare_results_*.txt` (comparación)

Puedes revisarlos después:
```bash
cat /tmp/experimental_test_results_*.txt
```

---

## ⏱️ Tiempo Estimado

- **test-experimental-models.sh**: 30-60 minutos (4 modelos × 6 tests cada uno)
- **interactive-test-models.sh**: Variable (depende de lo que pruebes)
- **test-lm-studio-models.sh**: 20-40 minutos (todos los modelos)

---

## 🎯 Tu Plan Recomendado

1. **Hoy**: Corre `test-experimental-models.sh`
   - Espera resultados
   - Ve qué modelos funcionan bien

2. **Basado en resultados**:
   - Si scores < 40%: Elimina esos modelos
   - Si scores 40-70%: Mantén pero usa como fallback
   - Si scores > 70%: Puedes usarlos con confianza

3. **Después**: Usa modelos oficiales para tareas importantes

---

## 📞 Preguntas?

Ver documentación completa:
- `~/LM_STUDIO_COMPLETE_INVENTORY.md` - Análisis detallado de todos los modelos
- `~/LM_STUDIO_REPAIR_GUIDE.md` - Guía de reparación
- `~/QUICK_ACTIONS.md` - Acciones rápidas

¡A testear! 🚀
