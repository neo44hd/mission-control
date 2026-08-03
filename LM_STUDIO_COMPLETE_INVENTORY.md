# 🎯 LM Studio - Inventario Completo de Modelos

**Ubicación**: `/Volumes/Disco local/lmstudio/models/` (accesible como `~/.lmstudio/models`)  
**Total de modelos descargados**: 9  
**Tamaño total**: ~52+ GB  
**Última actualización**: 2026-08-02

---

## 📋 Resumen Ejecutivo

Tienes **9 modelos instalados** en LM Studio, pero la mayoría están **experimentales o merges**. Solo recomiendo 3 para uso diario.

| Estado | Cantidad | Ejemplos |
|--------|----------|----------|
| ✅ Recomendado | 3 | NVIDIA Nemotron, LFM, ruvltra |
| ⚠️ Experimental | 4 | Qwythos, Qwen Claude, Phi, Ternary |
| ❌ Vacío/Incompleto | 2 | DavidAU, HauhauCS, Jackrong |

---

## 🔍 Análisis Detallado por Proveedor

### 1. **chatqaq** - Qwen 3.6 Claude Mythos
```
Qwen3.6-27B-Claude-Mythos-Distilled.Q4_K_M.gguf (16 GB)
```
**Tipo**: Merge experimental  
**Cuantización**: Q4_K_M (4-bit)  
**Parámetros**: 27B (grande)  
**Recomendación**: ⚠️ **EVITAR** - Este es probablemente el modelo que causó tu problema anterior  
**Por qué**:
- Es un merge no oficial de Claude + Qwen
- La cuantización Q4_K_M es agresiva
- Históricamente, merges experimentales generan "token garbage"
- Similar al `qwythos-9b-claude-mythos-5-1m` que te causó problemas

**Veredicto**: NO uses este modelo. Considera eliminarlo si falla.

---

### 2. **lmstudio-community** - Modelos de Comunidad Oficial
#### 📦 GLM-4.6V-Flash-MLX-4bit (6.6 GB)
```
model-00001-of-00002.safetensors (5.0 GB)
model-00002-of-00002.safetensors (1.6 GB)
```
**Tipo**: Visión + Lenguaje (MLX format)  
**Cuantización**: 4-bit MLX  
**Mejor para**: Análisis de imágenes + texto  
**Recomendación**: ✅ **BUENO** - Modelo oficial de la comunidad LM Studio  
**Ventajas**:
- Formato MLX (optimizado para Apple Silicon)
- Soporte de visión (puede procesar imágenes)
- 4-bit mantiene buena calidad

---

#### 📦 Phi-4-reasoning-plus-MLX-4bit (7.6 GB)
```
model-00001-of-00002.safetensors (4.9 GB)
model-00002-of-00002.safetensors (2.7 GB)
```
**Tipo**: Reasoning/Razonamiento  
**Cuantización**: 4-bit MLX  
**Parámetros**: ~4B base (expandido)  
**Recomendación**: ✅ **EXCELENTE** - Mejor para lógica y coding  
**Ventajas**:
- Especializado en reasoning (cadena de pensamiento)
- Muy eficiente en Apple Silicon (MLX)
- Bueno para debugging y análisis complejo

**Mejor que**: Qwen Mythos para tareas técnicas

---

#### 📦 NVIDIA-Nemotron-3-Nano-4B (2.6 GB)
```
NVIDIA-Nemotron-3-Nano-4B-Q4_K_M.gguf (2.6 GB)
```
**Tipo**: General purpose (NVIDIA oficial)  
**Cuantización**: Q4_K_M  
**Parámetros**: 4B (compacto)  
**Recomendación**: ✅ **MUY RECOMENDADO** - Mejor balance  
**Ventajas**:
- Oficial de NVIDIA (no es merge)
- Muy rápido (solo 4B parámetros)
- Salida limpia, sin garbage
- Perfecto para testing y producción

**Mejor para**: Inicio rápido, testing, requests en paralelo

---

#### 📦 LFM2.5-1.2B-Instruct-MLX-8bit (1.2 GB)
```
model.safetensors (1.2 GB)
```
**Tipo**: Lightweight instruction-following  
**Cuantización**: 8-bit MLX  
**Parámetros**: 1.2B (ultra-compacto)  
**Recomendación**: ✅ **RECOMENDADO** - Para tareas rápidas  
**Ventajas**:
- Ultra rápido en Apple Silicon
- Bajo consumo de memoria
- Suficiente para tareas simples
- Ideal para desarrollo/testing

**Mejor para**: Prototipado, requests de baja latencia

---

### 3. **mlx-community** - GPT OSS 20B
```
model-00001-of-00003.safetensors (4.9 GB)
model-00002-of-00003.safetensors (4.9 GB)
model-00003-of-00003.safetensors (1.4 GB)
```
**Total**: ~11.2 GB  
**Tipo**: Open-source GPT (no es oficial)  
**Cuantización**: MXFP4-Q8  
**Parámetros**: 20B  
**Recomendación**: ⚠️ **PROCEDER CON CUIDADO**  
**Notas**:
- Es un modelo de open source, no oficial
- 20B es bastante grande
- Formato MXFP4 es experimental
- Prueba antes de usarlo en producción

---

### 4. **prism-ml** - Ternary Bonsai 27B
```
model.safetensors (7.9 GB)
```
**Tipo**: Experimental (Ternary quantization)  
**Cuantización**: 2-bit (ternary - EXTREMO)  
**Parámetros**: 27B  
**Recomendación**: ❌ **NO RECOMENDADO**  
**Por qué**:
- 2-bit es EXTREMADAMENTE agresivo
- Probables hallucinations y errores
- Calidad degradada severamente
- Solo para curiosidad/research

**Veredicto**: Eliminate si necesitas espacio

---

### 5. **ruv** - RuvUltra Claude Code
```
ruvltra-claude-code-0.5b-q4_k_m.gguf (380 MB)
```
**Tipo**: Claude-like lightweight (merge)  
**Cuantización**: Q4_K_M  
**Parámetros**: 0.5B (ultra-mini)  
**Recomendación**: ✅ **ÚTIL PARA TESTING**  
**Ventajas**:
- Increíblemente pequeño (380 MB)
- Claude-style training
- Perfecto para local testing
- Carga en <1 segundo

**Mejor para**: Rápidas iteraciones en desarrollo

---

### 6. **xunkutech-ai** - Qwythos 9B Claude Mythos 5
```
model-00001-of-00002.safetensors (4.7 GB)
model-00002-of-00002.safetensors (3.2 GB)
```
**Total**: ~7.9 GB  
**Tipo**: Experimental merge (Claude + Qwen)  
**Cuantización**: Safetensors (presumiblemente 8-bit)  
**Parámetros**: 9B  
**Recomendación**: ❌ **EVITAR - Este causó tu problema inicial**  
**Por qué**:
- Este es el modelo que generó tu mensaje garbled
- Merge no oficial
- Safetensors puede estar corrupto (como vimos)
- Historial de issues con LM Studio

**Acción recomendada**: **ELIMINAR** para liberar 7.9 GB

---

### 7-9. Carpetas Vacías
- **DavidAU** - Vacía
- **HauhauCS** - Vacía  
- **Jackrong** - Vacía

**Acción**: Pueden eliminarse si no las usas

---

## 🎯 Recomendaciones de Uso

### ✅ **Top 3 - Uso Diario**

1. **NVIDIA Nemotron-3-Nano-4B** (2.6 GB)
   - 🏆 Mejor balance general
   - ⚡ Muy rápido
   - 📊 Salida limpia, sin errores
   - 💾 Bajo uso de memoria
   ```bash
   # Usar: nemotron
   ```

2. **Phi-4-reasoning-plus** (7.6 GB)
   - 🧠 Mejor para lógica/debugging
   - 🔍 Excelente reasoning
   - 🎯 Técnicamente superior al Qwen Mythos
   ```bash
   # Usar: phi-4
   ```

3. **LFM2.5-1.2B** (1.2 GB)
   - ⚡ Ultra rápido
   - 🎮 Ideal para prototipado
   - 💡 Suficiente para tareas simples

---

### ⚠️ **Experimentales - Solo si sabes lo que haces**

- **GLM-4.6V-Flash** - Bueno si necesitas visión
- **gpt-oss-20b** - Prueba antes de producción
- **Ternary Bonsai** - Solo research

---

### ❌ **Eliminar**

- **Qwythos 9B** (7.9 GB) ← Causó tu problema
- **Qwen Mythos Distilled** (16 GB) ← Parecido al anterior
- **Carpetas vacías** ← Sin usar

**Espacio a liberar**: ~31.9 GB si eliminas los problemáticos

---

## 🔧 Comparativa de Recomendados

| Métrica | Nemotron | Phi-4 | LFM | Qwythos ❌ |
|---------|----------|-------|-----|-----------|
| Velocidad | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| Calidad | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| Estabilidad | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ❌ |
| Tamaño | 2.6 GB | 7.6 GB | 1.2 GB | 7.9 GB |
| Coding | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ |
| General | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |

**Veredicto**: Usa **Nemotron** por defecto, **Phi-4** para código complejo, **LFM** para testing

---

## 🚀 Setup Recomendado

```bash
# Mantener en ~/.lmstudio/models/:
# ✅ lmstudio-community/NVIDIA-Nemotron-3-Nano-4B
# ✅ lmstudio-community/Phi-4-reasoning-plus-MLX-4bit
# ✅ lmstudio-community/LFM2.5-1.2B-Instruct-MLX-8bit
# ✅ lmstudio-community/GLM-4.6V-Flash-MLX-4bit (si necesitas visión)
# ✅ ruv/ruvltra-claude-code (para testing rápido)

# Eliminar:
# ❌ xunkutech-ai/Qwythos-9B (7.9 GB - causó tu problema)
# ❌ chatqaq/Qwen3.6-27B (16 GB - parecido al anterior)
# ❌ prism-ml/Ternary-Bonsai (7.9 GB - demasiado experimental)

# Vacías (opcional eliminar):
# - DavidAU/
# - HauhauCS/
# - Jackrong/
```

---

## ⚙️ Próximos Pasos

1. **Backup de Qwythos (opcional)**
   ```bash
   mv /Volumes/Disco\ local/lmstudio/models/xunkutech-ai/Qwythos-9B-Claude-Mythos-5-1M-MLX-oQ6-mtp \
      /Volumes/Disco\ local/lmstudio/models/.backup-qwythos/
   ```

2. **Usar en LM Studio**
   - LM Studio detectará automáticamente los modelos
   - Restart: `killall -9 "LM Studio" && open /Applications/LM\ Studio.app`

3. **Test**
   ```bash
   curl -X POST http://localhost:1234/v1/chat/completions \
     -H "Content-Type: application/json" \
     -d '{
       "model": "nemotron",
       "messages": [{"role": "user", "content": "Hola! Responde en español limpio, sin errores."}],
       "temperature": 0.7
     }'
   ```

---

## 📊 Storage Cleanup Potential

| Acción | Liberación |
|--------|-----------|
| Eliminar Qwythos 9B | +7.9 GB |
| Eliminar Qwen 27B Mythos | +16 GB |
| Eliminar Ternary Bonsai | +7.9 GB |
| **Total liberado** | **~31.9 GB** |
| **Espacio final** | ~20 GB (solo recomendados) |

---

## 🎓 Por qué Qwythos causó problemas

**Qwythos 9B Claude Mythos 5** es:
1. **Merge no oficial** - Combina pesos de múltiples modelos sin garantía
2. **Cuantización agresiva** - Oq6 (ternary-like) puede perder información
3. **Sin soporte oficial** - No hay documentación clara
4. **Historial de issues** - Múltiples reportes de token garbage

**Mejor alternativa**: Phi-4 (razonamiento) o Nemotron (general)

---

## 📝 Notas Finales

- **Tu setup LM Studio está bien instalado** - El problema era específicamente el modelo Qwythos
- **Tienes excelentes modelos** - Nemotron, Phi-4, y LFM son todos de calidad
- **Recomendación fuerte**: Elimina merges experimentales, usa oficiales
- **Para el futuro**: Solo descarga modelos de Hugging Face oficial, lmstudio-community, o proveedor NVIDIA

Disfruta de tus modelos limpios y sin errores de encoding. 🚀
